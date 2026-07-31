# AIVOA — AI-Powered Customer Complaint Management System

AI-powered customer complaint management module for a pharmaceutical (API & FDF) manufacturer's Quality Management System (QMS). Features a chat-driven AI co-pilot that extracts complaint details, populates forms, and assesses risk — all through natural language.

![AIVOA QMS Copilot Demo](demo.png)

---

## Demo Flow

```
User types in chat ──► AI extracts fields ──► Form auto-fills + Risk assessed
User uploads PDF   ──► AI extracts fields ──► Form auto-fills + Risk assessed
User says "sorry, batch is X" ──► AI updates only that field
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Redux Toolkit + RTK Query + Tailwind CSS v4 |
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async) |
| AI Agent | LangGraph + LangChain tool calling |
| LLM | Groq API — `openai/gpt-oss-120b` |
| Database | PostgreSQL 15+ (via asyncpg) |
| Font | Google Inter |

> **Note on model:** The assignment specifies `gemma2-9b-it`, but Groq deprecated it on October 8, 2025. We are using `openai/gpt-oss-120b` to future-proof the demo against upcoming model deprecations. Model names are configured via `.env` — never hardcoded.

---

## Architecture

```
┌─────────────────────────────┐    ┌──────────────────────────────┐
│   LEFT PANEL                │    │   RIGHT PANEL                │
│   Log Customer Complaint    │    │   AIVOA Co-Pilot             │
│                             │    │                              │
│   ┌───────────────────────┐ │    │   ┌──────────────────────┐   │
│   │ Origin & Customer     │ │    │   │ Risk Assessment      │   │
│   │ Product & Batch       │ │    │   │ Severity | Priority  │   │
│   │ Complaint Details     │ │    │   │ Next Action          │   │
│   │ Severity & Priority   │ │    │   │ Justification        │   │
│   └───────────────────────┘ │    │   └──────────────────────┘   │
│                             │    │                              │
│   Fields filled BY the AI   │    │   ┌──────────────────────┐   │
│   (not manually)            │◄───│   │ Chat Messages        │   │
│                             │    │   │ 🤖 AI: Logged...     │   │
│   [Reset] [Save Complaint]  │    │   │ 👤 Sorry, batch...   │   │
│                             │    │   │ 🤖 AI: Updated...    │   │
│                             │    │   │                      │   │
│                             │    │   │ [📎] [Type here] [➤] │   │
└─────────────────────────────┘    │   └──────────────────────┘   │
                                   └──────────────────────────────┘
```

---

## Three Mandatory AI Tools

### 1. Log Complaint (Chat → Form)
Type a complaint description in the chat. The AI extracts all fields and populates the form + generates a risk assessment.

**Example prompt:**
> Apollo Pharmacy reported discolored capsules in Amoxicylin Capsules 500mg, batch BMX24601, mfg Jan 2024, exp Dec 2025, 50 affected capsules

**Result:** Product name, strength, batch number, dates, quantities, complaint type, description all populate automatically. Risk assessment shows severity, priority, next action.

### 2. Edit Complaint (Correction → Partial Update)
Send a correction in the chat. The AI updates only the specified fields, preserving everything else.

**Example prompt:**
> Sorry, the batch number is BMX24602 and the affected quantity is 48 capsules

**Result:** Only `batch_number` and `quantity_affected` change. All other fields remain as-is.

### 3. Document Extraction (File Upload → Form)
Click 📎 in the chat input, upload a PDF/DOCX/TXT/EML file. The AI extracts complaint details and populates the form + risk assessment.

After extraction, you can still use edit commands to correct specific fields.

---

## Bonus AI Features

Six additional AI analysis tools are available via shortcut buttons in the copilot panel. Each one sends a specialized prompt to the AI and returns structured analysis right in the chat.

| Button | What it does |
|--------|-------------|
| **Completeness** | Reviews every field in the form, reports which are filled vs missing, gives a completeness % |
| **Root Cause** | Ishikawa fishbone analysis across 6 categories: Man, Machine, Method, Material, Measurement, Environment |
| **Duplicates** | Analyzes the complaint pattern (product + batch + defect type) and flags likely duplicate reports |
| **CAPA** | Recommends Corrective Actions (fix this batch) and Preventive Actions (stop recurrence), referencing ICH Q10 / 21 CFR 211 |
| **Summary** | Generates a management-ready complaint summary for QA leadership review |
| **Risk Class.** | Multi-factor risk assessment: Patient Safety, Regulatory Impact, Business Impact, Supply Chain Impact |

These features work through the same copilot chat — no separate screens. Log a complaint first, then click any button to get instant AI analysis.

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ running locally
- Groq API key → [console.groq.com](https://console.groq.com)

### 1. Database
```bash
psql -U postgres -c "CREATE DATABASE pcms;"
```

### 2. Backend
```bash
cd backend

# Create & activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env → set GROQ_API_KEY and DATABASE_URL
# Example: DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/pcms

# Start backend (auto-creates tables on first run)
uvicorn app.main:app --reload --port 8000

# (Optional) Seed test data
python seed_data.py
```

### 3. Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 4. Open
- **App:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

---

## API Endpoints

### Core — AI Copilot
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/copilot/chat` | **Primary endpoint** — chat message + optional file upload |

### Complaint CRUD
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/complaints` | Create/save complaint |
| GET | `/api/complaints` | List (filter by status/severity/product) |
| GET | `/api/complaints/{id}` | Get complaint detail |
| PUT | `/api/complaints/{id}` | Update (per-field audit trail) |
| DELETE | `/api/complaints/{id}` | Soft-delete only |

### AI Features (per-complaint)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/complaints/{id}/chat` | Chat with complaint context |
| GET | `/api/complaints/{id}/chat` | Chat history |
| POST | `/api/complaints/{id}/check-duplicates` | Duplicate detection |
| POST | `/api/complaints/{id}/root-cause-suggestions` | Ishikawa root cause |
| POST | `/api/complaints/{id}/capa-recommendations` | CAPA suggestions |
| POST | `/api/complaints/{id}/completeness-check` | Field completeness |
| POST | `/api/complaints/{id}/risk-classification` | Severity classification |
| GET | `/api/complaints/{id}/audit-trail` | Audit history |

### Extraction (legacy)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/complaints/extract/upload` | File upload extraction |
| POST | `/api/complaints/extract/text` | Text extraction |
| WS | `/ws/extraction/{run_id}` | Real-time progress |

---

## Project Structure

```
Ai_voova/
├── .gitignore
├── README.md
│
├── backend/
│   ├── requirements.txt
│   ├── .env.example              # Template (no secrets)
│   ├── .env                      # Your secrets (gitignored)
│   ├── alembic.ini
│   ├── seed_data.py
│   │
│   ├── sample_complaints/        # Demo files for document extraction
│   │   ├── complaint_email_amoxicylin.txt
│   │   └── complaint_metformin_api.txt
│   │
│   ├── alembic/
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   └── app/
│       ├── main.py               # FastAPI app + router includes
│       │
│       ├── core/
│       │   ├── config.py          # Pydantic Settings (.env)
│       │   └── database.py        # Async SQLAlchemy engine
│       │
│       ├── models/                # SQLAlchemy ORM (7 tables)
│       │   ├── complaint.py
│       │   ├── complaint_attachment.py
│       │   ├── ai_extraction_run.py
│       │   ├── chat_message.py
│       │   ├── duplicate_match.py
│       │   ├── capa_recommendation.py
│       │   └── audit_trail.py
│       │
│       ├── schemas/               # Pydantic request/response
│       │   ├── complaint.py
│       │   ├── extraction.py
│       │   ├── chat.py
│       │   ├── ai_features.py
│       │   └── copilot.py         # ★ Copilot schemas + RiskAssessment
│       │
│       ├── api/routes/
│       │   ├── complaints.py      # CRUD + audit trail
│       │   ├── extraction.py      # File/text extraction
│       │   ├── ws.py              # WebSocket progress
│       │   ├── chat.py            # Per-complaint chat
│       │   ├── ai_features.py     # Duplicates, root cause, CAPA
│       │   └── copilot.py         # ★ POST /api/copilot/chat
│       │
│       ├── agents/
│       │   ├── state.py           # LangGraph TypedDict state
│       │   ├── graph.py           # Extraction pipeline (6 nodes)
│       │   ├── copilot_agent.py   # ★ Tool-calling copilot agent
│       │   │
│       │   ├── tools/
│       │   │   └── complaint_tools.py  # ★ log_complaint + edit_complaint
│       │   │
│       │   ├── nodes/             # Pipeline nodes (9 files)
│       │   │   ├── parse_document.py
│       │   │   ├── extract_fields.py
│       │   │   ├── check_completeness.py
│       │   │   ├── classify_severity.py
│       │   │   ├── detect_duplicates.py
│       │   │   ├── generate_summary.py
│       │   │   ├── chat_node.py
│       │   │   ├── root_cause_node.py
│       │   │   └── capa_node.py
│       │   │
│       │   └── prompts/           # One file per node's system prompt
│       │       ├── extract_fields_prompt.py
│       │       ├── classify_severity_prompt.py
│       │       ├── detect_duplicates_prompt.py
│       │       ├── generate_summary_prompt.py
│       │       ├── chat_prompt.py
│       │       ├── root_cause_prompt.py
│       │       └── capa_prompt.py
│       │
│       └── services/
│           ├── file_parser.py     # PDF/DOCX/TXT/EML → text
│           └── groq_client.py     # LLM factory + retry logic
│
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    │
    └── src/
        ├── main.tsx               # Redux Provider entry point
        ├── App.tsx                # Two-panel layout
        ├── index.css              # Tailwind v4 + Inter font
        │
        ├── store/
        │   ├── index.ts           # Redux store config
        │   ├── api.ts             # RTK Query (all endpoints)
        │   ├── complaintFormSlice.ts   # Form state (value+source+confidence)
        │   └── aiPanelSlice.ts    # AI panel + risk assessment state
        │
        ├── components/
        │   ├── Header.tsx
        │   ├── ComplaintForm.tsx       # Left panel — 4 form sections
        │   ├── FormSection.tsx         # Collapsible section container
        │   ├── AIFormField.tsx         # Smart field (AI badge + confidence)
        │   ├── FormActions.tsx         # Reset / Save buttons
        │   ├── AIAssistantPanel.tsx    # ★ Right panel (Risk + Features + Chat)
        │   ├── AIAssistantChat.tsx     # ★ Chat with 📎 file upload
        │   ├── RiskAssessment.tsx      # ★ Severity/priority/next action
        │   └── CopilotFeatureBar.tsx   # ★ 6 bonus AI analysis shortcuts
        │
        ├── hooks/
        │   ├── useWebSocket.ts
        │   └── useExtraction.ts
        │
        └── types/
            └── index.ts           # TypeScript interfaces
```

Files marked with ★ are the core copilot components.

---

## Key Design Decisions

| Decision | Why |
|----------|-----|
| Chat-first, not form-first | Assignment requirement: "you must not fill the left form manually" |
| LangChain tool calling | LLM decides whether to `log_complaint` or `edit_complaint` based on user intent |
| FormData for copilot endpoint | Supports both text messages and file uploads in a single request |
| Risk assessment in Redux | Separate slice allows the AI to update risk independently of form fields |
| Per-field `source` tracking | Every field knows if it was set by AI or user — drives the AI badge UI |
| Soft-delete only | Pharmaceutical records must never be hard-deleted (21 CFR 211.198) |
| Per-field audit trail | Every change is traceable to who/when/old/new |
| Exponential backoff on Groq | Free tier is rate-limited; `tenacity` retry handles 429s gracefully |

---

## Sample Complaint Documents

Two sample files in `backend/sample_complaints/` for demoing document extraction:

1. **`complaint_email_amoxicylin.txt`** — Email from Apollo Pharmacy about discolored Amoxicylin Capsules 500mg
2. **`complaint_metformin_api.txt`** — API complaint from MediCure Formulations about out-of-spec Metformin HCl

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | (required) | Your Groq API key |
| `GROQ_MODEL_FAST` | `openai/gpt-oss-120b` | Model for fast tasks |
| `GROQ_MODEL_REASONING` | `openai/gpt-oss-120b` | Model for reasoning tasks |
| `DATABASE_URL` | `postgresql+asyncpg://user:password@localhost:5432/pcms` | PostgreSQL connection string |
| `MAX_UPLOAD_MB` | `10` | Max file upload size |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins |

---

## Database

7 tables: `complaints`, `complaint_attachments`, `ai_extraction_runs`, `chat_messages`, `duplicate_matches`, `capa_recommendations`, `audit_trail`

Tables are auto-created on first startup via `init_db()`. For production, use Alembic:
```bash
cd backend
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

## Known Limitations

1. **No authentication** — MVP has no login. In production, integrate with enterprise SSO.
2. **Groq rate limits** — Free tier is 30 RPM / 12,000 RPD. Rapid interactions may see delays.
3. **No OCR** — File parser handles text-based PDFs only, not scanned images.
4. **Chat is the only input method** — Form fields can be manually edited after AI fills them, but the primary input is always through chat.
5. **Model deprecation** — `gemma2-9b-it` deprecated Oct 2025. Using `openai/gpt-oss-120b`. Model names are in `.env` for easy swapping.
