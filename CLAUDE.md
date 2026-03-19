# LexFlow — JL Laniog Law Firm · Project Documentation
_Last updated: 2026-03-19_

---

## 🚀 SESSION TRIGGER

**When Luke types "lex":**
- Read this CLAUDE.md file only
- Do NOT explore any other files
- Do NOT run any commands
- Respond with exactly this:
  > "Oh great, you're back. ProjectLEX is ready — what do you want me to do next, master?"
- Then wait for instructions

---

## 🎭 HOW TO RESPOND

- Be sarcastically funny but always concise and precise
- Never over-explain — if it can be said in 2 lines, use 2 lines
- After every change, briefly state what you changed and why
- Use simple language — Luke is still learning, not a senior dev
- Never explore files unless Luke explicitly asks
- If something is obvious, say it once and move on
- When Luke makes a mistake, point it out — but make it funny or even insulting. It's ok with me.

---

## Project Overview

LEX is an AI-powered legal case processing pipeline that automates and standardizes client intake, legal analysis, and strategy formulation for the JL Laniog Law Firm.

### What It Does

1. **Client Intake** - Law firm clerks submit case details through a web dashboard
2. **Multi-Layer Analysis** - The case passes through three specialized AI lawyers:
   - **Advocate**: Builds the strongest possible case for the client
   - **Devil's Advocate**: Identifies weaknesses, risks, and counterarguments
   - **Senior Legal Analyst**: Synthesizes both analyses and issues final strategy
3. **Results Delivery** - Dashboard updates in real-time as each analysis completes, allowing the legal team to review and take action
4. **Legal Knowledge Base** - Integrated with Philippine legal documents (Constitution, statutes, jurisprudence) for grounded, relevant advice

The pipeline handles diverse case types (Labor, Criminal, Civil, Family, Property, Corporate, Tax, IP Law) with urgency-based prioritization and outputs concrete recommendations: Settle, Go to Trial, Demand Letter, Mediation, Administrative Complaint, Urgent Protection Order, or Drop Case.

### Technology Stack

- **Workflow Orchestration**: n8n - Visual workflow automation platform
- **Backend Database**: Supabase - PostgreSQL with real-time capabilities
  - `cases` table: Stores all case data and AI analyses
  - `documents` table: Vector embeddings for legal knowledge base (RAG)
  - Storage bucket: `case_files` for document uploads
- **LLM Provider**: Groq - High-speed inference API
  - Model: `llama-3.3-70b-versatile` for all three AI lawyers
- **Embeddings**: Ollama - Local embeddings server
  - Model: `nomic-embed-text:latest` for legal document vectorization
- **Frontend**: Custom HTML/JavaScript dashboard (`lexflow_dashboard.html`)
  - Polls workflow status every 5 seconds
  - Progressive rendering of lawyer analyses
  - Case search and detail modal

### Architecture Pattern

Sequential pipeline with trigger-based handoffs. Each stage writes its analysis to Supabase, and the dashboard polls for updates. Fail-safe design: if one lawyer fails, the pipeline can still proceed (with null fields), and the dashboard displays partial results gracefully.

---

## Architecture Overview

Sequential AI pipeline. Each workflow triggers the next via HTTP POST.

```
Dashboard (clerk submits)
    ↓
Case Intake Pipeline + Delete  ← also handles case deletion
    ↓
Advocate Workflow
    ↓
Devil's Advocate Workflow
    ↓
Legal Analyst Workflow
    ↓
Fetch Results Workflow  ← dashboard polls this every 5s
```

Data is written to Supabase `cases` table progressively — each lawyer UPDATEs the same row as it completes. The dashboard polls Fetch Results and renders each lawyer's analysis as soon as it arrives (6-minute max window, 72 poll attempts × 5s).

---

## Workflow Files (current, import-ready)

| File | Webhook Path | Status |
|------|-------------|--------|
| `Case Intake Pipeline.json` | `/intake` | ✓ Ready |
| `Delete Files From  Supabase.json` | `/delete-case` | ✓ Ready |
| `Advocate (Corrected).json` | `/advocate` | ✓ Ready |
| `Devil's Advocate (Corrected).json` | `/devil` | ✓ Ready |
| `Legal Analyst (Strategist).json` | `/analyst` | ✓ Ready |
| `Fetch Results.json` | `/fetch-results` | ✓ Ready |

**Note:** Intake and Delete are separate workflows (previously combined).

---

## Supabase Configuration

**Project URL:** `https://ncvlpqbevllqwrpdauxi.supabase.co`

Two credential types are required in n8n:

### 1. Native Supabase nodes (Supabase Get / Insert / Update / Delete)
- **Credential name:** `Supabase account 2`
- **Credential ID:** `YjOL2NYwLrO3tdr0`
- Used by: all `n8n-nodes-base.supabase` nodes across all workflows

### 2. Code nodes (Upload / Delete Storage files)
- Set as n8n environment variables:
  - `SUPABASE_URL` = `https://ncvlpqbevllqwrpdauxi.supabase.co`
  - `SUPABASE_SERVICE_KEY` = your service role key

### Storage
- **Bucket name:** `case_files` (underscore — not a dash)
- Path pattern: `{case_id}/{timestamp}_{random}_{filename}`
- Used by: Upload Files to Storage (Intake), Delete Storage Files (Intake)

### Tables
- `cases` — all case data + lawyer analyses (`lawyer_a`, `lawyer_b`, `senior_partner` columns)
- `documents` — vector embeddings for LEX legal database (separate ingestion pipeline)

---

## AI Models

| Workflow | LLM | Embeddings |
|----------|-----|-----------|
| Advocate | Groq `llama-3.3-70b-versatile` | Ollama `nomic-embed-text:latest` |
| Devil's Advocate | Groq `llama-3.3-70b-versatile` | Ollama `nomic-embed-text:latest` |
| Legal Analyst | Groq `llama-3.3-70b-versatile` | Ollama `nomic-embed-text:latest` |

---

## Fixes Applied (2026-03-13)

### Case Intake Pipeline
- Removed duplicate `lawyer_a / lawyer_b / senior_partner` lines in Normalize & Validate node
- Fixed bucket name `case-files` → `case_files` in Upload and Delete Storage nodes
- Updated all Supabase credentials to `Supabase account 2`
- **Critical fix:** Removed invalid `credentials` blocks from "Upload Files to Storage" and "Delete Storage Files" Code nodes (Code nodes don't support credentials)
- Replaced `$credentials.supabaseStorage.url` and `$credentials.supabaseStorage.key` template variables with `process.env.SUPABASE_URL` and `process.env.SUPABASE_SERVICE_KEY`
- **Required setup:** Configure n8n environment variables `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` for these Code nodes to work

### Advocate
- Added `filterMode: defineBelow` + `case_id eq` filter to "Save lawyer_a to Supabase" node (was updating wrong rows without this)
- Updated Supabase credentials to `Supabase account 2`

### Devil's Advocate
- Set Groq model to `llama-3.3-70b-versatile` (was missing)
- Removed stray `{% else %}` and `{% endif %}` Jinja2 tags from AI Agent prompt
- Updated Supabase credentials to `Supabase account 2`

### Legal Analyst
- Set Groq model to `llama-3.3-70b-versatile` (was missing)
- Updated Supabase credentials to `Supabase account 2`

### Fetch Results
- Updated Supabase credentials to `Supabase account 2`

---

## Dashboard Updates (2026-03-19)

**File:** `lexflow_dashboard.html`

### Sidebar Enhancements
- **Quick Actions** — Added "New Case" button (gold CTA) below logo. Opens template picker modal for direct intake access.
- **System Status Widget** — Real-time health indicators for n8n and Supabase (coupled via poll success). Shows `● online` / `● offline` / `—` (stale/no data). Groq API shown as static `—` (no direct health check from dashboard).

### Bug Fixes
- Fixed modal nesting bug: Template Picker modal was inside Webhook modal, making it invisible. Un-nested — now both modals are direct children of `<body>` and function correctly.

---

## Dashboard

**File:** `lexflow_dashboard.html`

- Submits to Intake webhook, then polls Fetch Results every 5s
- Poll window: 72 attempts × 5s = 6 minutes max
- Renders each lawyer's analysis progressively as it arrives
- Live pipeline stage indicator: INTAKE → ADVOCATE → DEVIL'S ADV. → STRATEGIST → COMPLETE
- Case detail modal: view, edit, and resubmit any case record
- Search: by name, case ID, legal topic, issue, opposing party, clerk notes

---

## Import Order in n8n

Import and activate in this order — each workflow must be active before the one before it can trigger it:

1. `Fetch Results.json`
2. `Legal Analyst (Strategist).json`
3. `Devil's Advocate (Corrected).json`
4. `Advocate (Corrected).json`
5. `Case Intake Pipeline.json`

Then activate the delete workflow (can be imported anytime):
6. `Delete Files From  Supabase.json`

Finally, point the dashboard webhook URL to `/intake`.

---

## LEX Ingestion Pipeline

**File:** `LEX Ingestion.json` (separate, run manually)

Downloads PDFs from Google Drive → extracts text → cleans + chunks → stores embeddings in Supabase `documents` table. Run once per legal document. Not part of the live case pipeline.

---

## ⚠️ EXIT RITUAL — MANDATORY BEFORE EVERY /exit

You are NOT allowed to exit without completing this sequence. No exceptions. Not even if Luke forgets to ask.

```
1. Update this CLAUDE.md — add today's changes to the Fixes/Changelog section
2. Stage all changes        → git add .
3. Commit with date         → git commit -m "session update YYYY-MM-DD"
4. Push to GitHub           → git push
5. Confirm to Luke          → "Done. ProjectLEX is saved, committed, and pushed. You may now leave."
```

If Luke tries to /exit without doing this, remind him — sarcastically.
