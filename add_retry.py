#!/usr/bin/env python3
"""
add_retry.py — Adds retry configuration to failure-prone nodes in LexFlow n8n workflows.

Usage:
    python3 add_retry.py file1.json file2.json ...

Or to process ALL workflow JSONs in the current folder:
    python3 add_retry.py *.json

What it does:
    Opens each n8n workflow JSON and adds { retry: { enabled, maxTries, waitBetween } }
    to any node type that calls an external service (Supabase, Groq, HTTP, Ollama).
    Safe to run multiple times — will never double-stamp a node that already has retry.
"""

import json
import sys

# Retry configuration to inject
RETRY_CONFIG = {
    "enabled": True,
    "maxTries": 3,
    "waitBetween": 2000  # ms between retries
}

# Node types that should get automatic retry
# These are all the external-call node types in the LexFlow pipeline
RETRY_TYPES = {
    "n8n-nodes-base.httpRequest",        # Trigger Advocate / Devil / Analyst calls
    "n8n-nodes-base.supabase",           # All Supabase read/write nodes
    "@n8n/n8n-nodes-langchain.lmChatGroq",          # Groq LLM calls
    "@n8n/n8n-nodes-langchain.embeddingsOllama",    # Ollama embedding calls
    "@n8n/n8n-nodes-langchain.vectorStoreSupabase", # Supabase vector store
}

def add_retry_to_node(node):
    """Add retry config to a node if it's a retryable type and doesn't have it yet."""
    node_type = node.get("type", "")
    if node_type in RETRY_TYPES:
        if "retry" not in node:
            node["retry"] = RETRY_CONFIG
            return True
    return False

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed_nodes = []

    if "nodes" in data:
        for node in data["nodes"]:
            if add_retry_to_node(node):
                changed_nodes.append(node.get("name", node.get("id", "unknown")))

    if changed_nodes:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"✓ {path}")
        for name in changed_nodes:
            print(f"    + retry added → {name}")
    else:
        print(f"— {path} (no changes needed)")

if __name__ == "__main__":
    files = sys.argv[1:]
    if not files:
        print("Usage: python3 add_retry.py file1.json file2.json ...")
        print("       python3 add_retry.py *.json")
        sys.exit(1)

    print(f"\nProcessing {len(files)} file(s)...\n")
    for f in files:
        try:
            process_file(f)
        except FileNotFoundError:
            print(f"✗ {f} — file not found")
        except json.JSONDecodeError as e:
            print(f"✗ {f} — invalid JSON: {e}")
        except Exception as e:
            print(f"✗ {f} — error: {e}")

    print("\nDone.")
