# ─────────────────────────────────────────────────────────────
# ProjectLEX — File Watcher & Auto Sync
# Watches the ProjectLEX folder for JSON changes and
# automatically pushes them to n8n via API
#
# Usage: python watch_and_sync.py
# Stop:  Ctrl+C
# ─────────────────────────────────────────────────────────────

import os
import sys
import time
import json
import urllib.request
import urllib.error
from datetime import datetime

# ── CONFIG ───────────────────────────────────────────────────
N8N_URL    = "http://localhost:5678"
API_KEY    = os.environ.get("N8N_API_KEY", "")
FOLDER     = os.path.dirname(os.path.abspath(__file__))
POLL_SEC   = 2       # check for changes every 2 seconds
DEBOUNCE   = 1.5     # wait 1.5s after a change before syncing
                     # (prevents syncing mid-save)

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

# Properties n8n API rejects on nodes
NODE_STRIP_KEYS = {
    "retry", "continueOnFail", "alwaysOutputData",
    "executeOnce", "notesInFlow", "notes"
}

# ── HELPERS ──────────────────────────────────────────────────
def ts():
    return datetime.now().strftime("%H:%M:%S")

def log(msg, symbol="•"):
    print(f"[{ts()}] {symbol} {msg}")

def api_call(method, path, data=None):
    url     = f"{N8N_URL}/api/v1{path}"
    headers = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}
    body    = json.dumps(data).encode("utf-8") if data else None
    req     = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"        HTTP {e.code}: {e.read().decode('utf-8')[:200]}")
        return None
    except Exception as e:
        print(f"        Error: {e}")
        return None

def clean_nodes(nodes):
    return [{k: v for k, v in n.items() if k not in NODE_STRIP_KEYS} for n in nodes]

def sync_file(filename, workflow_id):
    filepath = os.path.join(FOLDER, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            local = json.load(f)
    except json.JSONDecodeError as e:
        log(f"  ✗ Invalid JSON in {filename}: {e}", "✗")
        return False
    except Exception as e:
        log(f"  ✗ Could not read {filename}: {e}", "✗")
        return False

    current = api_call("GET", f"/workflows/{workflow_id}")
    if not current:
        log(f"  ✗ Could not fetch {filename} from n8n", "✗")
        return False

    payload = {
        "name":        local.get("name", current.get("name")),
        "nodes":       clean_nodes(local.get("nodes", [])),
        "connections": local.get("connections", {}),
        "settings":    local.get("settings", current.get("settings", {})),
        "staticData":  current.get("staticData"),
    }

    result = api_call("PUT", f"/workflows/{workflow_id}", payload)
    if result:
        log(f"✓ Synced → {filename}", "✓")
        return True
    return False

# ── FILE WATCHER ─────────────────────────────────────────────
def get_mtimes():
    """Get last modified times for all watched JSON files"""
    mtimes = {}
    for filename in WORKFLOWS:
        filepath = os.path.join(FOLDER, filename)
        if os.path.exists(filepath):
            mtimes[filename] = os.path.getmtime(filepath)
    return mtimes

def watch():
    if not API_KEY:
        print("✗ N8N_API_KEY not set in environment variables.")
        print("  Run: [System.Environment]::SetEnvironmentVariable('N8N_API_KEY', 'your-key', 'User')")
        print("  Then restart PowerShell and run this script again.")
        sys.exit(1)

    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║     ProjectLEX — Auto Sync Watcher              ║")
    print("║     Watching for JSON changes...                ║")
    print("║     Press Ctrl+C to stop                        ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"  Folder:  {FOLDER}")
    print(f"  n8n:     {N8N_URL}")
    print(f"  Watching {len(WORKFLOWS)} workflow files")
    print()

    # Initial snapshot of file modification times
    known_mtimes = get_mtimes()
    pending = {}  # filename → time change was detected

    log("Watcher started — ready", "▶")
    print()

    try:
        while True:
            time.sleep(POLL_SEC)
            current_mtimes = get_mtimes()

            for filename, mtime in current_mtimes.items():
                known = known_mtimes.get(filename, 0)
                if mtime != known:
                    if filename not in pending:
                        log(f"Change detected → {filename}", "~")
                    pending[filename] = time.time()
                    known_mtimes[filename] = mtime

            # Process pending files after debounce period
            now = time.time()
            synced = []
            for filename, detected_at in list(pending.items()):
                if now - detected_at >= DEBOUNCE:
                    workflow_id = WORKFLOWS[filename]
                    sync_file(filename, workflow_id)
                    synced.append(filename)

            for filename in synced:
                del pending[filename]

    except KeyboardInterrupt:
        print()
        log("Watcher stopped", "■")
        print()

# ── MAIN ─────────────────────────────────────────────────────
if __name__ == "__main__":
    watch()
