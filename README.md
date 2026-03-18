# ⚖️ ProjectLEX
### AI-Powered Legal Case Management System
*JL Laniog Law Firm — Clerk Dashboard & AI Pipeline*

---

## What is ProjectLEX?

ProjectLEX is an AI-powered legal intake and case management system built for JL Laniog Law Firm. It automates the journey from client intake to legal analysis using a multi-agent AI pipeline — combining a clerk dashboard, n8n automation workflows, local AI models, and a vector-based legal knowledge base.

---

## How It Works

```
Client walks in
      ↓
Clerk fills out intake form (Dashboard)
      ↓
Case data fires to n8n via webhook
      ↓
AI Pipeline activates:
  ├── Document Processor   →  reads & chunks uploaded legal docs
  ├── LEX Researcher       →  searches legal knowledge base (Supabase)
  ├── Advocate Lawyer      →  builds argument for the client
  ├── Devil's Advocate     →  challenges the argument
  └── Judge / Strategist   →  evaluates both, recommends strategy
      ↓
Final Case Analysis Report generated
```

---

## Features

- **Clerk Dashboard** — intake forms for 6 legal categories with case ID generation
- **AI Legal Pipeline** — multi-agent system with advocate, counter-advocate, and judge roles
- **LEX Knowledge Base** — vector search over Philippine laws and jurisprudence
- **Real-time File Sync** — file watcher auto-syncs workflow changes to n8n
- **Case Records** — searchable intake history with urgency tracking
- **Webhook Integration** — direct pipeline trigger from dashboard to n8n

---

## Legal Categories Supported

| Category | Issues Covered |
|----------|---------------|
| 👷 Labor Law | Illegal dismissal, constructive dismissal, NLRC, wage disputes |
| ⚔️ Criminal Law | Estafa, theft, physical injuries, cybercrime, drug cases |
| 🏠 Family Law | Annulment, custody, support, VAWC, legal separation |
| 📜 Civil Law | Contract disputes, breach, damages, collection cases |
| 🏗️ Property Law | Land disputes, ejectment, titling, ownership conflicts |
| 🏢 Corporate Law | SEC complaints, shareholder disputes, governance |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Dashboard | HTML / CSS / JavaScript |
| Automation | n8n (self-hosted, localhost:5678) |
| Local AI | Ollama (localhost:11434) |
| Embeddings | nomic-embed-text via Ollama |
| Vector Store | Supabase (pgvector) |
| File Sync | Python watchdog (watch_and_sync.py) |
| Version Control | GitHub |

---

## Project Structure

```
ProjectLEX/
├── lexflow_dashboard.html      # Main clerk intake dashboard
├── watch_and_sync.py           # File watcher — syncs changes to n8n
├── START_PROJECTLEX.bat        # Launcher — starts n8n, Ollama, watcher
├── CLAUDE.md                   # AI context file for Claude Code sessions
├── README.md                   # This file
└── workflows/
    └── LEX_INGESTION.json      # n8n workflow — ingests legal PDFs to Supabase
```

---

## Getting Started

### Prerequisites
- [n8n](https://n8n.io) installed globally (`npm install -g n8n`)
- [Ollama](https://ollama.ai) installed with `nomic-embed-text` model
- Python 3.x with `watchdog` library (`pip install watchdog`)
- Supabase account with `documents` table and pgvector enabled

### Launch
Double-click `START_PROJECTLEX.bat` — this starts:
1. **n8n** at `http://localhost:5678`
2. **Ollama** at `http://localhost:11434`
3. **File Watcher** monitoring the ProjectLEX folder

### Configure Webhook
1. Open the dashboard → Settings
2. Paste your n8n webhook URL
3. Toggle between Test and Production mode

---

## AI Agent Roles

| Agent | Role |
|-------|------|
| 📥 Case Intake | Receives form data, creates Case ID, triggers pipeline |
| 📄 Document Processor | Extracts, chunks, and embeds uploaded legal documents |
| 🔍 LEX Researcher | Retrieves relevant laws, articles, and jurisprudence |
| ⚖️ Advocate Lawyer | Builds the strongest argument for the client |
| 🗡️ Devil's Advocate | Challenges the argument, finds weaknesses |
| 🏛️ Judge / Strategist | Evaluates both sides, recommends legal strategy |

---

## Development Workflow

```
Edit files in Cursor or Claude Code
          ↓
watch_and_sync.py detects changes
          ↓
Auto-syncs to n8n workflows
          ↓
git add . → git commit → git push
          ↓
GitHub updated
```

---

## End of Session Checklist

Before closing any session:
- [ ] Ask Claude Code to update `CLAUDE.md` with today's changes
- [ ] `git add .`
- [ ] `git commit -m "describe what changed"`
- [ ] `git push`

---

## Built By

**Luke** — JL Laniog Law Firm  
AI-assisted development using Claude Code + Cursor + n8n

---

*ProjectLEX — turning legal intake into intelligent case preparation.*
