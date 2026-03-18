# ─────────────────────────────────────────────────────────────
# ProjectLEX — n8n Sync Script
# Pushes local JSON workflow files directly to n8n via API
# Usage: python sync_to_n8n.py                → sync all workflows
#        python sync_to_n8n.py advocate       → sync one workflow
# ─────────────────────────────────────────────────────────────

import json
import os
import sys
import urllib.request
import urllib.error

# ── CONFIG ───────────────────────────────────────────────────
N8N_URL  = "http://localhost:5678"
API_KEY  = os.environ.get("N8N_API_KEY", "")

# Map: local filename → n8n workflow ID
WORKFLOWS = {
    "Advocate (Corrected).json":         "bTIQsyS8e7SEIU9xQUMEP",
    "Case Intake Pipeline.json":         "2aiiL9TI5-p0v4qtJBYW_",
    "Delete Files From Supabase.json":   "0CfSj-Zs9oqvqJF4WY2Dq",
    "Devil's Advocate (Corrected).json": "9ay5wFdBCmAowe7DOj9sQ",
    "Fetch Results.json":                "GcjdXJgqgY2hu70FzCd9T",
    "Legal Analyst (Strategist).json":   "eqbXr-BFyRfS3CmQxt6em",
    "LEX Ingestion.json":                "F5SD7YqD73bjBqsxzIffN",
    "PARALEGAL.json":                    "T4nrC5enTkI5dIjoDuyY2",
}

# Properties n8n's API rejects on nodes
NODE_STRIP_KEYS = {"retry", "continueOnFail", "alwaysOutputData", "executeOnce", "notesInFlow", "notes"}

# ── HELPERS ──────────────────────────────────────────────────
def api_call(method, path, data=None):
    url = f"{N8N_URL}/api/v1{path}"
    headers = {
        "X-N8N-API-KEY": API_KEY,
        "Content-Type":  "application/json"
    }
    body = json.dumps(data).encode("utf-8") if data else None
    req  = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  ✗ HTTP {e.code}: {error_body[:300]}")
        return None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None

def clean_nodes(nodes):
    """Strip properties that n8n API rejects on node objects"""
    cleaned = []
    for node in nodes:
        clean = {k: v for k, v in node.items() if k not in NODE_STRIP_KEYS}
        cleaned.append(clean)
    return cleaned

def sync_workflow(filename, workflow_id):
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    if not os.path.exists(filepath):
        print(f"  ✗ File not found: {filename}")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        local = json.load(f)

    # Fetch current workflow from n8n to get internal fields
    current = api_call("GET", f"/workflows/{workflow_id}")
    if not current:
        print(f"  ✗ Could not fetch workflow from n8n")
        return False

    # Build clean update payload
    payload = {
        "name":        local.get("name", current.get("name")),
        "nodes":       clean_nodes(local.get("nodes", [])),
        "connections": local.get("connections", {}),
        "settings":    local.get("settings", current.get("settings", {})),
        "staticData":  current.get("staticData"),
    }

    result = api_call("PUT", f"/workflows/{workflow_id}", payload)
    if result:
        print(f"  ✓ Synced successfully")
        return True
    return False

# ── MAIN ─────────────────────────────────────────────────────
def main():
    if not API_KEY:
        print("✗ N8N_API_KEY not set.")
        print("  Run: $env:N8N_API_KEY = 'your-api-key'")
        print("  Then run this script again.")
        sys.exit(1)

    filter_arg = sys.argv[1].lower() if len(sys.argv) > 1 else None

    targets = {
        f: wid for f, wid in WORKFLOWS.items()
        if not filter_arg or filter_arg in f.lower()
    }

    if not targets:
        print(f"✗ No workflow matched '{filter_arg}'")
        print(f"  Available:")
        for f in WORKFLOWS.keys():
            print(f"    - {f}")
        sys.exit(1)

    print(f"\nProjectLEX → n8n Sync")
    print(f"{'─' * 50}")
    print(f"Syncing {len(targets)} workflow(s)...\n")

    success = 0
    for filename, workflow_id in targets.items():
        print(f"► {filename}")
        if sync_workflow(filename, workflow_id):
            success += 1

    print(f"\n{'─' * 50}")
    print(f"Done. {success}/{len(targets)} synced successfully.\n")

if __name__ == "__main__":
    main()
