# Red 6 Competitive Intelligence Platform

A multi-provider LLM research orchestration platform that runs competitive intelligence queries across 5 AI providers in parallel, cross-validates findings, synthesizes results into unified reports, and maintains a per-company knowledge base to track what's changed over time.

## Overview

This platform enables Red 6's competitive intelligence team to:

- **Run parallel research** across OpenAI, Anthropic, Google, xAI, and Perplexity simultaneously
- **Cross-validate findings** by comparing what multiple AI providers report
- **Synthesize results** into unified combined reports with confidence levels
- **Track changes over time** using a per-company Knowledge Base that detects NEW, UPDATED, and CONTRADICTED information
- **View Intelligence Briefings** summarizing what's changed across all companies
- **Export reports** in multiple formats (Markdown, HTML, DOCX, PDF)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Next.js Frontend (Port 3000)                         │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│   │  Dashboard  │ │   Reports   │ │  Briefing   │ │   Prompts   │           │
│   │ (New Research)│ │   Library   │ │ (Deltas)    │ │   Library   │           │
│   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘           │
└──────────┼───────────────┼───────────────┼───────────────┼──────────────────┘
           │               │               │               │
           └───────────────┴───────────────┴───────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (Port 8000)                             │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                         API Routers                                   │  │
│   │  /api/research  /api/prompts  /api/reports  /api/delta  /api/sources │  │
│   └─────────────────────────────┬────────────────────────────────────────┘  │
│                                 │                                            │
│   ┌─────────────────────────────┴────────────────────────────────────────┐  │
│   │                          Services                                     │  │
│   │                                                                       │  │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐   │  │
│   │  │ Research Engine │  │ Synthesis       │  │ Knowledge Base      │   │  │
│   │  │ (Multi-provider)│  │ Service         │  │ Service             │   │  │
│   │  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘   │  │
│   │           │                    │                      │               │  │
│   └───────────┼────────────────────┼──────────────────────┼───────────────┘  │
│               │                    │                      │                  │
│   ┌───────────┴────────────────────┴──────────────────────┴───────────────┐  │
│   │                      AI Provider Clients                              │  │
│   │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────────┐               │  │
│   │  │OpenAI │ │Anthro │ │Google │ │ xAI   │ │Perplexity │               │  │
│   │  │GPT-4  │ │Claude │ │Gemini │ │Grok   │ │  Sonar    │               │  │
│   │  └───────┘ └───────┘ └───────┘ └───────┘ └───────────┘               │  │
│   └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Data Storage                                      │
│                                                                              │
│   /reports/{company}/{date}/          - Generated research reports          │
│   /reports/.delta/{job_id}.json       - Delta analysis results              │
│   /knowledge_base/{company}.json      - Per-company entity knowledge base   │
│   /data/jobs/{job_id}.json            - Research job records                │
│   /data/prompts.json                  - Prompt library                       │
│   /data/sources.json                  - Curated intelligence sources        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the **project root** directory:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=your-gemini-key
XAI_API_KEY=xai-...
PERPLEXITY_API_KEY=pplx-...
```

> Note: At minimum, you need `ANTHROPIC_API_KEY` for entity extraction and at least one other provider key for research.

### 3. Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Project Structure

```
competitive_analysis_research/
├── api/                            # Core research engine
│   ├── __init__.py                 # Package exports
│   ├── base_researcher.py          # Abstract base class for providers
│   ├── research_engine.py          # Orchestration & parallel execution
│   ├── openai_research.py          # OpenAI GPT provider
│   ├── anthropic_research.py       # Anthropic Claude provider
│   ├── google_research.py          # Google Gemini provider
│   ├── xai_research.py             # xAI Grok provider
│   ├── perplexity_research.py      # Perplexity Sonar provider
│   ├── synthesis_agent.py          # Cross-model synthesis
│   ├── cost_calculator.py          # API cost tracking
│   └── export_utils.py             # Report export utilities
│
├── backend/
│   ├── main.py                     # FastAPI application entry
│   ├── routers/                    # API route handlers
│   │   ├── research.py             # Research job endpoints
│   │   ├── prompts.py              # Prompt library endpoints
│   │   ├── reports.py              # Report browsing endpoints
│   │   ├── delta.py                # Delta/briefing endpoints
│   │   ├── sources.py              # Intelligence sources endpoints
│   │   └── schedule.py             # Scheduled research endpoints
│   ├── services/                   # Business logic
│   │   ├── research_service.py     # Research orchestration
│   │   ├── synthesis_service.py    # Multi-model report synthesis
│   │   ├── knowledge_base_service.py # Entity extraction & change detection
│   │   ├── delta_service.py        # Delta analysis service
│   │   └── source_service.py       # Source management
│   ├── models/                     # Pydantic data models
│   │   ├── research.py             # Research job models
│   │   ├── knowledge_base.py       # Entity & KB models
│   │   └── delta.py                # Delta finding models
│   └── data/                       # Persistent job data
│
├── frontend/
│   ├── src/app/                    # Next.js pages (App Router)
│   │   ├── page.tsx                # Dashboard (New Research)
│   │   ├── reports/                # Reports library
│   │   ├── briefing/               # Intelligence Briefing
│   │   ├── prompts/                # Prompt library
│   │   └── research/[jobId]/       # Research progress & results
│   └── src/components/             # React components
│
├── prompts/                        # Research prompt templates (.md files)
├── reports/                        # Generated research reports
│   └── .delta/                     # Delta analysis results
├── docs/                           # API documentation
├── tests/                          # Unit tests for api/ module
├── companies.csv                   # Tracked companies list
├── sources.yaml                    # Curated intelligence sources
└── .env                            # API keys (not committed)
```

---

## Core Features

### 1. Multi-Provider Research

Run competitive intelligence queries across 5 AI providers simultaneously:

| Provider   | Model            | Web Search      | Best For                    |
|------------|------------------|-----------------|------------------------------|
| OpenAI     | GPT-4            | Responses API   | General analysis             |
| Anthropic  | Claude Sonnet    | MCP Tool        | Detailed, nuanced analysis   |
| Google     | Gemini           | Grounding       | Fast, current information    |
| xAI        | Grok             | Built-in        | Real-time data + X/Twitter   |
| Perplexity | Sonar Pro        | Native          | Best citations & current news|

### 2. Combined Report Synthesis

When multiple models are selected with "Generate Combined Report" enabled:

1. Each provider runs research independently
2. Claude synthesizes all outputs into ONE unified report
3. The combined report includes:
   - **Executive Summary** - Key findings across all models
   - **High-Confidence Findings** - Points where models AGREED
   - **Areas of Disagreement** - Where models conflicted
   - **Unique Insights by Model** - What each model uniquely found
   - **Methodology Note** - Which models contributed

### 3. Research Modes

| Mode     | Speed     | Depth          | Use Case                    |
|----------|-----------|----------------|-----------------------------|
| Basic    | ~30-60s   | Quick scan     | Initial reconnaissance      |
| Deep     | ~2-5 min  | Comprehensive  | Detailed competitive intel  |
| Combined | ~3-6 min  | Multi-model    | Highest confidence results  |

---

## Knowledge Base System

The Knowledge Base is a per-company database that tracks structured entities over time. This enables the system to detect what's genuinely NEW vs. what was already known.

### How It Works

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         KNOWLEDGE BASE FLOW                                 │
└────────────────────────────────────────────────────────────────────────────┘

1. Research Completes
   ┌──────────────────────────────────────────────────────────────┐
   │  Report: "Elbit M&A Activity"                                │
   │  Content: "Elbit acquired Sparton Corp for $380M..."         │
   └──────────────────────────────────┬───────────────────────────┘
                                      │
                                      ▼
2. Entity Extraction (Claude)
   ┌──────────────────────────────────────────────────────────────┐
   │  Extracted Entities:                                         │
   │  - ACQUISITION: Sparton Corp ($380M, 2021)                   │
   │  - EXECUTIVE: Bezhalel Machlis (CEO)                         │
   │  - TECHNOLOGY: Night vision systems                          │
   └──────────────────────────────────┬───────────────────────────┘
                                      │
                                      ▼
3. Load Existing Knowledge Base
   ┌──────────────────────────────────────────────────────────────┐
   │  /knowledge_base/elbit_systems.json                          │
   │  {                                                           │
   │    "company": "Elbit Systems",                               │
   │    "entities": [                                             │
   │      { "type": "EXECUTIVE", "name": "Bezhalel Machlis" },    │
   │      { "type": "CUSTOMER", "name": "IDF" }                   │
   │    ]                                                         │
   │  }                                                           │
   └──────────────────────────────────┬───────────────────────────┘
                                      │
                                      ▼
4. Change Detection (Claude)
   ┌──────────────────────────────────────────────────────────────┐
   │  Compare new entities vs existing KB:                        │
   │                                                              │
   │  - Sparton Corp acquisition → NEW (not in KB)                │
   │  - Bezhalel Machlis CEO → CONFIRMED (already known)          │
   │  - Night vision systems → NEW (not in KB)                    │
   └──────────────────────────────────┬───────────────────────────┘
                                      │
                                      ▼
5. Update KB + Generate Delta Report
   ┌──────────────────────────────────────────────────────────────┐
   │  - Add new entities to KB                                    │
   │  - Update timestamps on confirmed entities                   │
   │  - Save delta findings for Briefing page                     │
   └──────────────────────────────────────────────────────────────┘
```

### Entity Types Tracked

| Type          | Description                              | Example Details                          |
|---------------|------------------------------------------|------------------------------------------|
| EXECUTIVE     | Key personnel                            | title, since, previous_role              |
| CUSTOMER      | Organizations buying from company        | contract_value, region, product          |
| CONTRACT      | Specific contract awards                 | value, customer, award_date, duration    |
| TECHNOLOGY    | Key technologies & capabilities          | category, status, description            |
| PRODUCT       | Specific products or product lines       | category, status, customers              |
| PARTNER       | Strategic partners, JVs                  | partner_type, since, description         |
| COMPETITOR    | Direct competitors mentioned             | competitive_area                          |
| ACQUISITION   | M&A activity                             | target, value, date, status              |
| FINANCIAL     | Key financial metrics                    | metric_type, value, period, trend        |
| FACILITY      | Manufacturing sites, R&D centers         | location, type, size                     |
| CERTIFICATION | Certifications & clearances              | certifying_body, scope, expiration       |
| LAWSUIT       | Legal matters                            | opposing_party, type, status, value      |
| STRATEGY      | Strategic initiatives                    | category, timeline, description          |

### Change Types

| Type         | Description                                  | Typical Importance |
|--------------|----------------------------------------------|-------------------|
| NEW          | Entity not present in KB                     | NOTABLE           |
| UPDATED      | Entity exists but values changed             | NOTABLE-CRITICAL  |
| CONTRADICTED | New info contradicts existing KB             | CRITICAL          |
| CONFIRMED    | Entity matches existing KB (no change)       | MINOR             |

### Example: Cross-Report Intelligence

```
Research Run 1: "Elbit M&A Activity" (January)
  → Extracts: CEO: Bezhalel Machlis, Acquisition: Sparton Corp
  → KB Status: Empty
  → All entities marked as NEW

Research Run 2: "Elbit Executive Changes" (February)
  → Extracts: CEO: Bezhalel Machlis, CFO: Yossi Gaspar
  → KB Status: Has CEO from Run 1
  → Findings:
    - CEO: CONFIRMED (already knew this)
    - CFO: NEW (first time seeing CFO)

Research Run 3: "Elbit Tech Trends" (March)
  → Extracts: CEO: "New Person", Technology: ARCAS AI Sight
  → KB Status: Has CEO as Bezhalel Machlis
  → Findings:
    - CEO: CONTRADICTED (CRITICAL! CEO changed!)
    - ARCAS: NEW
```

This cross-report intelligence means:
- You can run ANY prompt type on a company
- The system remembers ALL entities from ALL previous reports
- If an M&A report mentions a new executive, it will be flagged
- If a Tech report shows a CEO change, it will be flagged as CRITICAL

---

## Intelligence Briefing

The Briefing page (`/briefing`) shows a summary of all detected changes across all companies over a selected time period.

### What's Displayed

1. **Summary Cards**
   - Total findings
   - Critical count (requiring attention)
   - Notable count
   - Companies tracked

2. **Type Breakdown**
   - NEW: Information not previously in KB
   - UPDATED: Changed values
   - CONTRADICTED: Conflicting information

3. **Critical Findings Section**
   - Red-highlighted urgent items
   - Executive changes, major contract losses, etc.

4. **Findings by Company**
   - Grouped view of all changes
   - Click "View Timeline" for full company history

### Data Source

The Briefing page pulls from `/api/delta/briefing?days=N` which:
1. Loads all delta reports from the specified period
2. Aggregates findings across all companies
3. Sorts by importance (CRITICAL first)

---

## API Endpoints

### Research

| Endpoint                          | Method | Description                     |
|-----------------------------------|--------|---------------------------------|
| `/api/research`                   | POST   | Start new research job          |
| `/api/research`                   | GET    | List recent jobs                |
| `/api/research/{job_id}`          | GET    | Get job status                  |
| `/api/research/{job_id}/export/{provider}` | GET | Export provider result |
| `/api/research/{job_id}/export/combined` | GET | Export combined report    |
| `/api/research/providers`         | GET    | Get provider availability       |

### Delta / Briefing

| Endpoint                          | Method | Description                     |
|-----------------------------------|--------|---------------------------------|
| `/api/delta/briefing?days=N`      | GET    | Get intelligence briefing       |
| `/api/delta/findings`             | GET    | Get all findings with filters   |
| `/api/delta/company/{company}/timeline` | GET | Company change timeline   |

### Prompts

| Endpoint                          | Method | Description                     |
|-----------------------------------|--------|---------------------------------|
| `/api/prompts`                    | GET    | List all prompts by category    |
| `/api/prompts/{prompt_id}`        | GET    | Get specific prompt             |

### Sources

| Endpoint                          | Method | Description                     |
|-----------------------------------|--------|---------------------------------|
| `/api/sources`                    | GET    | List curated intel sources      |
| `/api/sources/search?q=...`       | GET    | Search sources                  |

---

## Data Storage

### Knowledge Base Files

Location: `backend/knowledge_base/{company_name}.json`

```json
{
  "company": "Elbit Systems",
  "entities": [
    {
      "id": "uuid-...",
      "entity_type": "executive",
      "name": "Bezhalel Machlis",
      "details": {
        "title": "CEO",
        "since": "2021"
      },
      "source_report_id": "job-uuid",
      "source_date": "2025-01-15T...",
      "last_updated": "2025-02-20T...",
      "confidence": "HIGH"
    }
  ],
  "last_updated": "2025-02-20T...",
  "total_reports_processed": 5,
  "report_ids_processed": ["job-1", "job-2", ...]
}
```

### Delta Report Files

Location: `reports/.delta/{job_id}.json`

```json
{
  "id": "delta-uuid",
  "job_id": "research-job-uuid",
  "company": "Elbit Systems",
  "prompt_id": "executive_movements",
  "findings": [
    {
      "id": "finding-uuid",
      "finding_text": "Executive: Jane Doe - New CFO appointment",
      "finding_type": "NEW",
      "importance": "CRITICAL",
      "category": "Executive",
      "created_at": "2025-02-20T..."
    }
  ],
  "summary": "Found 3 delta findings. 1 CRITICAL items require attention.",
  "created_at": "2025-02-20T..."
}
```

---

## Research Prompts

Located in `prompts/` directory. Use `[COMPANY NAME]` as a placeholder.

| Prompt                              | Purpose                                |
|-------------------------------------|----------------------------------------|
| `executive_movements`               | Leadership changes, departures, hires  |
| `contract_awards`                   | Government contracts, military programs|
| `ma_activity`                       | Mergers, acquisitions, divestitures    |
| `technology_trends`                 | R&D, new products, capabilities        |
| `financial_performance`             | Revenue, margins, backlog              |
| `strategic_direction`               | Future plans, roadmaps, investments    |
| `org_structure_and_hiring`          | Org changes, key hires                 |
| `multi_primary_competitors_matrix`  | Cross-competitor comparison            |

### Adding New Prompts

Create a markdown file in `prompts/`:

```markdown
# Research Topic

Research [COMPANY NAME] for the following information:

1. First research area
2. Second research area
...

Focus on recent developments from the past 6 months.
Provide specific names, dates, and values where available.
```

---

## Troubleshooting

### Provider shows as "Unavailable"
- Check API key in `.env` file
- Ensure key doesn't start with placeholder text
- Verify API key is valid and has credits

### Briefing page is empty
- Run research jobs first - delta analysis runs automatically after each job
- Check that ANTHROPIC_API_KEY is set (required for entity extraction)
- Look at backend logs for errors during delta analysis

### Knowledge base not updating
- Ensure research jobs complete successfully
- Check `/backend/knowledge_base/` directory for JSON files
- Review backend logs for extraction errors

### High API costs
- Use Basic mode for initial research
- Select fewer providers
- Combined mode uses additional API calls for synthesis

---

## Development

### Running Tests
```bash
# From project root
python -m pytest tests/
```

### Backend Hot Reload
```bash
cd backend
source ../venv/bin/activate  # Activate venv from root
uvicorn main:app --reload --port 8000
```

### Frontend Hot Reload
```bash
cd frontend
npm run dev
```

### Viewing API Documentation
Open http://localhost:8000/docs for interactive Swagger UI

---

## License

Proprietary - Red 6 Internal Use Only
