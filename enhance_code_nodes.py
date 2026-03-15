#!/usr/bin/env python3
"""
enhance_code_nodes.py — Replaces JS code in the Upload and Delete Storage Code nodes
across ALL LexFlow workflow JSON files in the current folder.

Usage:
    python3 enhance_code_nodes.py

What it does:
    Finds Code nodes named "Upload Files to Storage" and "Delete Storage Files"
    (or variants like "Delete Storage Files1") and replaces their jsCode with
    improved versions that have:
    - Proper $env.SUPABASE_URL / $env.SUPABASE_SERVICE_KEY credential access
    - fetchWithRetry wrapper with exponential backoff
    - Correct MIME type detection
    - Timestamp + random suffix for filename collision prevention
    - Patches document_urls back to the cases table after upload

Fixes from original:
    1. Node matching changed from node.get("id") to node.get("name") — original
       never matched because IDs are UUIDs, not human-readable strings.
    2. Credential access changed from {{ $credentials.supabaseStorage.url }}
       (Jinja2 template syntax — does NOT work in Code nodes) to
       $env.SUPABASE_URL and $env.SUPABASE_SERVICE_KEY (correct n8n env var access).
"""

import json
import glob

# ─────────────────────────────────────────────────────────────
# UPLOAD FILES TO STORAGE — improved JS
# ─────────────────────────────────────────────────────────────
UPLOAD_CODE = r"""// Upload files to Supabase Storage
// Credentials read from n8n environment variables (Settings → Environment Variables)
// Required: SUPABASE_URL, SUPABASE_SERVICE_KEY

const item = $input.first().json;
const caseId = item.case_id;
const attachments = item._attachments_full || [];

if (!attachments || attachments.length === 0) {
  return [{ json: { ...item, document_urls: [], upload_errors: null, _attachments_full: undefined } }];
}

const supabaseUrl = $env.SUPABASE_URL || "https://ncvlpqbevllqwrpdauxi.supabase.co";
const supabaseKey = $env.SUPABASE_SERVICE_KEY || "";
const bucket = "case_files";

if (!supabaseKey) {
  throw new Error("SUPABASE_SERVICE_KEY environment variable is not set. Configure it in n8n Settings → Environment Variables.");
}

// Retry wrapper with exponential backoff
async function fetchWithRetry(url, options, maxRetries = 3, delayMs = 2000) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, options);
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errText}`);
      }
      return res;
    } catch (err) {
      if (attempt === maxRetries) throw err;
      await new Promise(r => setTimeout(r, delayMs * attempt)); // exponential: 2s, 4s, 6s
    }
  }
}

const MIME_TYPES = {
  "pdf":  "application/pdf",
  "jpg":  "image/jpeg",
  "jpeg": "image/jpeg",
  "png":  "image/png",
  "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "doc":  "application/msword",
  "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "xls":  "application/vnd.ms-excel",
  "txt":  "text/plain"
};

const uploadedUrls = [];
const errors = [];

for (const file of attachments) {
  const originalName = file.name || "document";
  const ext = originalName.split(".").pop().toLowerCase();
  const mimeType = MIME_TYPES[ext] || "application/octet-stream";

  // Prevent filename collisions: timestamp + random 6-char suffix
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  const fileName = `${timestamp}_${random}_${originalName}`;
  const filePath = `${caseId}/${fileName}`;

  try {
    // Decode base64 → binary
    const binaryStr = atob(file.data);
    const bytes = new Uint8Array(binaryStr.length);
    for (let i = 0; i < binaryStr.length; i++) {
      bytes[i] = binaryStr.charCodeAt(i);
    }

    await fetchWithRetry(
      `${supabaseUrl}/storage/v1/object/${bucket}/${filePath}`,
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${supabaseKey}`,
          "Content-Type": mimeType,
          "x-upsert": "true"
        },
        body: bytes
      }
    );

    const publicUrl = `${supabaseUrl}/storage/v1/object/public/${bucket}/${filePath}`;
    uploadedUrls.push({ name: originalName, url: publicUrl, type: mimeType });

  } catch (error) {
    console.error(`Upload failed for ${originalName}:`, error.message);
    errors.push({ name: originalName, error: error.message });
  }
}

// Patch the cases row with document_urls so the dashboard can display them
if (uploadedUrls.length > 0) {
  try {
    await fetchWithRetry(
      `${supabaseUrl}/rest/v1/cases?case_id=eq.${caseId}`,
      {
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${supabaseKey}`,
          "apikey": supabaseKey,
          "Content-Type": "application/json",
          "Prefer": "return=minimal"
        },
        body: JSON.stringify({ document_urls: uploadedUrls })
      }
    );
  } catch (patchError) {
    console.error("Failed to patch document_urls on case record:", patchError.message);
    errors.push({ name: "PATCH_CASE", error: patchError.message });
  }
}

return [{
  json: {
    ...item,
    document_urls: uploadedUrls,
    upload_errors: errors.length > 0 ? errors : null,
    _attachments_full: undefined  // strip large base64 payload before passing downstream
  }
}];
"""

# ─────────────────────────────────────────────────────────────
# DELETE STORAGE FILES — improved JS
# ─────────────────────────────────────────────────────────────
DELETE_CODE = r"""// Delete all files for a case from Supabase Storage
// Credentials read from n8n environment variables (Settings → Environment Variables)
// Required: SUPABASE_URL, SUPABASE_SERVICE_KEY

const item = $input.first().json;
const caseId = item.case_id;

const supabaseUrl = $env.SUPABASE_URL || "https://ncvlpqbevllqwrpdauxi.supabase.co";
const supabaseKey = $env.SUPABASE_SERVICE_KEY || "";
const BUCKET = "case_files";

if (!supabaseKey) {
  return [{ json: { ...item, storage_deleted: false, storage_error: "SUPABASE_SERVICE_KEY not set" } }];
}

// Retry wrapper with exponential backoff
async function fetchWithRetry(url, options, maxRetries = 3, delayMs = 2000) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, options);
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errText}`);
      }
      return res;
    } catch (err) {
      if (attempt === maxRetries) throw err;
      await new Promise(r => setTimeout(r, delayMs * attempt));
    }
  }
}

// List all files in this case's folder
let files;
try {
  const listRes = await fetchWithRetry(
    `${supabaseUrl}/storage/v1/object/list/${BUCKET}`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${supabaseKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ prefix: `${caseId}/`, limit: 1000 })
    }
  );
  files = await listRes.json();
} catch (listError) {
  return [{ json: { ...item, storage_deleted: false, storage_error: listError.message } }];
}

if (!files || files.length === 0) {
  return [{ json: { ...item, storage_deleted: true, files_deleted: 0 } }];
}

const paths = files.map(f => `${caseId}/${f.name}`);

// Delete all files in parallel, each with retry
const deleteResults = await Promise.all(
  paths.map(filePath =>
    fetchWithRetry(
      `${supabaseUrl}/storage/v1/object/${BUCKET}/${filePath}`,
      {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${supabaseKey}` }
      }
    )
    .then(() => true)
    .catch(() => false)
  )
);

const deletedCount = deleteResults.filter(r => r).length;

return [{
  json: {
    ...item,
    storage_deleted: true,
    files_deleted: deletedCount,
    files_found: paths.length,
    storage_error: deletedCount < paths.length
      ? `Partial delete: ${deletedCount}/${paths.length} files removed`
      : null
  }
}];
"""

# ─────────────────────────────────────────────────────────────
# Node name patterns to match (covers both workflow versions)
# Merged workflow uses "Upload Files to Storage" / "Delete Storage Files"
# Delete_2 workflow uses "Upload Files to Storage" / "Delete Storage Files1"
# ─────────────────────────────────────────────────────────────
UPLOAD_NAMES = {"Upload Files to Storage"}
DELETE_NAMES = {"Delete Storage Files", "Delete Storage Files1"}

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed_nodes = []

    if "nodes" in data:
        for node in data["nodes"]:
            if node.get("type") != "n8n-nodes-base.code":
                continue

            name = node.get("name", "")

            if name in UPLOAD_NAMES:
                current = node.get("parameters", {}).get("jsCode", "")
                if current != UPLOAD_CODE:
                    node.setdefault("parameters", {})["jsCode"] = UPLOAD_CODE
                    changed_nodes.append(f"{name} → upload code updated")

            elif name in DELETE_NAMES:
                current = node.get("parameters", {}).get("jsCode", "")
                if current != DELETE_CODE:
                    node.setdefault("parameters", {})["jsCode"] = DELETE_CODE
                    changed_nodes.append(f"{name} → delete code updated")

    if changed_nodes:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"✓ {path}")
        for msg in changed_nodes:
            print(f"    + {msg}")
    else:
        print(f"— {path} (no matching code nodes found or already up to date)")

if __name__ == "__main__":
    files = glob.glob("*.json")
    if not files:
        print("No JSON files found in current directory.")
        print("Make sure you run this script from the same folder as your workflow JSON files.")
        import sys; sys.exit(1)

    print(f"\nProcessing {len(files)} JSON file(s)...\n")
    for f in sorted(files):
        try:
            process_file(f)
        except json.JSONDecodeError as e:
            print(f"✗ {f} — invalid JSON: {e}")
        except Exception as e:
            print(f"✗ {f} — error: {e}")

    print("\nDone. Import the modified JSON files back into n8n.")
