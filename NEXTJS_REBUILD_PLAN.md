# Red 6 Competitive Intelligence Platform - Next.js Rebuild Plan

> **Document Purpose**: This is our master planning document for the Next.js rebuild.
> All work should follow this plan sequentially. Do not deviate without updating this document first.

---

## Branch Strategy

| Branch | Purpose | Status |
|--------|---------|--------|
| `main` | Stable Streamlit version (fallback) | Protected |
| `nextjs-rebuild` | New Next.js + FastAPI implementation | Active Development |

**To return to stable version:** `git checkout main`

---

## Project Overview

### What We're Building
A modern, enterprise-grade Competitive Intelligence Platform with:
- Next.js 14 frontend (App Router, Tailwind CSS, shadcn/ui)
- FastAPI backend (async, WebSocket support)
- Intelligence Delta Engine (what's new detection)
- Custom Source Library (team-curated sources)
- Scheduled Research (automated weekly runs)
- Real-time progress updates

### Success Criteria
- [x] All current Streamlit functionality preserved
- [x] Research runs successfully through new UI
- [x] Real-time progress updates working (polling-based)
- [x] Delta detection operational
- [x] Source library integrated
- [x] Scheduled research functional
- [ ] Team can use without training

---

## Phase Overview

| Phase | Name | Duration Estimate | Status |
|-------|------|-------------------|--------|
| 0 | Foundation Setup | 1 session | **COMPLETED** |
| 1 | FastAPI Backend | 2-3 sessions | **COMPLETED** |
| 2 | Next.js Core UI | 2-3 sessions | **COMPLETED** |
| 3 | Research Workflow | 2 sessions | **COMPLETED** |
| 4 | Results & Export | 1-2 sessions | **COMPLETED** |
| 5 | Source Library | 1-2 sessions | **COMPLETED** |
| 6 | Delta Intelligence | 2-3 sessions | **COMPLETED** |
| 7 | Scheduled Research | 1-2 sessions | **COMPLETED** |
| 8 | Polish & Deploy | 1-2 sessions | **COMPLETED** |

---

## Phase 0: Foundation Setup

### 0.1 Project Structure
**Goal**: Set up the monorepo structure with frontend and backend directories

```
competitive_analysis_research/
├── frontend/                 # Next.js application
├── backend/                  # FastAPI application
├── api/                      # Existing research engine (keep as-is)
├── prompts/                  # Research prompts (keep as-is)
├── data/                     # CSV files (keep as-is)
├── reports/                  # Generated reports (keep as-is)
├── sources.yaml              # NEW: Custom source library
├── app.py                    # OLD: Streamlit (keep for fallback)
└── NEXTJS_REBUILD_PLAN.md    # This document
```

**Tasks**:
- [x] 0.1.1 Create `frontend/` directory
- [x] 0.1.2 Create `backend/` directory
- [x] 0.1.3 Initialize Next.js in frontend/
- [x] 0.1.4 Initialize FastAPI in backend/
- [x] 0.1.5 Verify both servers start independently

**Test Criteria**:
- Next.js dev server runs on port 3000
- FastAPI server runs on port 8000
- Both can be started simultaneously

---

### 0.2 Next.js Setup
**Goal**: Configure Next.js with all required dependencies

**Tasks**:
- [x] 0.2.1 Install Next.js 14 with App Router
- [x] 0.2.2 Install and configure Tailwind CSS
- [x] 0.2.3 Install shadcn/ui and configure components
- [x] 0.2.4 Install additional dependencies (see list below)
- [x] 0.2.5 Create basic layout with header/navigation
- [x] 0.2.6 Verify hot reload works

**Dependencies**:
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "various",
    "lucide-react": "^0.300.0",
    "framer-motion": "^10.0.0",
    "zustand": "^4.4.0",
    "@tanstack/react-query": "^5.0.0",
    "socket.io-client": "^4.6.0",
    "react-markdown": "^9.0.0",
    "date-fns": "^3.0.0"
  }
}
```

**Test Criteria**:
- Can import and use shadcn Button component
- Tailwind classes render correctly
- Page navigation works

---

### 0.3 FastAPI Setup
**Goal**: Configure FastAPI with proper project structure

**Tasks**:
- [x] 0.3.1 Create FastAPI application structure
- [x] 0.3.2 Configure CORS for frontend communication
- [x] 0.3.3 Set up WebSocket support
- [x] 0.3.4 Create health check endpoint
- [x] 0.3.5 Connect to existing research engine
- [x] 0.3.6 Verify API responds correctly

**Backend Structure**:
```
backend/
├── main.py                   # FastAPI app entry point
├── config.py                 # Configuration and env vars
├── routers/
│   ├── __init__.py
│   ├── research.py           # Research endpoints
│   ├── companies.py          # Company endpoints
│   ├── prompts.py            # Prompt endpoints
│   ├── history.py            # Report history endpoints
│   └── exports.py            # Export endpoints
├── services/
│   ├── __init__.py
│   ├── research_service.py   # Wraps existing engine
│   ├── delta_service.py      # Delta analysis
│   └── source_service.py     # Source library
├── models/
│   ├── __init__.py
│   └── schemas.py            # Pydantic models
└── websocket/
    ├── __init__.py
    └── progress.py           # WebSocket handlers
```

**Test Criteria**:
- GET /health returns {"status": "ok"}
- GET /api/companies returns company list
- GET /api/prompts returns prompt list
- CORS allows requests from localhost:3000

---

## Phase 1: FastAPI Backend Core

### 1.1 Company & Prompt Endpoints
**Goal**: Expose existing data through REST API

**Tasks**:
- [x] 1.1.1 Create GET /api/companies endpoint (via CSV loader)
- [x] 1.1.2 Create GET /api/prompts endpoint
- [x] 1.1.3 Create GET /api/providers endpoint (with status)
- [x] 1.1.4 Add proper error handling
- [ ] 1.1.5 Add request/response logging

**Test Criteria**:
- All endpoints return correct data shape
- Provider status accurately reflects API key availability
- Errors return proper HTTP codes

---

### 1.2 Research Execution Endpoint
**Goal**: Trigger research runs via API

**Tasks**:
- [x] 1.2.1 Create POST /api/research endpoint
- [x] 1.2.2 Integrate with existing ResearchEngine
- [x] 1.2.3 Return job ID for tracking
- [x] 1.2.4 Store results in session/cache
- [x] 1.2.5 Create GET /api/research/{job_id} endpoint

**Request Schema**:
```python
class ResearchRequest(BaseModel):
    company: str
    prompt: str
    mode: Literal["basic", "deep"]
    providers: List[str]
    run_synthesis: bool = True
```

**Test Criteria**:
- Can trigger research via curl/Postman
- Job ID returned immediately
- Results retrievable after completion

---

### 1.3 WebSocket Progress Updates
**Goal**: Real-time research progress

**Tasks**:
- [ ] 1.3.1 Create WebSocket endpoint /ws/research/{job_id}
- [ ] 1.3.2 Emit progress events during research
- [ ] 1.3.3 Send provider completion events
- [ ] 1.3.4 Send final completion event
- [ ] 1.3.5 Handle disconnection gracefully

**Progress Event Schema**:
```python
class ProgressEvent(BaseModel):
    job_id: str
    event_type: Literal["started", "provider_started", "provider_completed", "completed", "error"]
    provider: Optional[str]
    progress_percent: int
    message: str
    data: Optional[Dict]
```

**Test Criteria**:
- Can connect via WebSocket client
- Receives progress updates during research
- Connection closes cleanly on completion

---

### 1.4 Report History & Export
**Goal**: Access past reports and export functionality

**Tasks**:
- [x] 1.4.1 Create GET /api/reports endpoint (list reports)
- [x] 1.4.2 Create GET /api/reports/{id} endpoint (single report)
- [x] 1.4.3 Create GET /api/reports/{id}/download endpoint
- [ ] 1.4.4 Support all export formats (md, html, docx, pdf)
- [x] 1.4.5 Return downloadable file (md format)

**Test Criteria**:
- Can list all historical reports
- Can retrieve specific report content
- Export produces valid files

---

## Phase 2: Next.js Core UI

### 2.1 Layout & Navigation
**Goal**: Create the app shell and navigation structure

**Tasks**:
- [x] 2.1.1 Create root layout with header
- [x] 2.1.2 Add navigation (top header nav with links)
- [ ] 2.1.3 Add user menu (placeholder)
- [x] 2.1.4 Create API status indicator in header
- [x] 2.1.5 Implement dark mode toggle
- [x] 2.1.6 Add loading states and skeletons

**Pages to Create**:
```
app/
├── page.tsx                  # Dashboard
├── research/
│   ├── page.tsx              # Research list
│   └── new/page.tsx          # New research wizard
├── reports/
│   ├── page.tsx              # Report history
│   └── [id]/page.tsx         # Single report view
├── compare/page.tsx          # Competitor comparison
├── sources/page.tsx          # Source library
├── settings/page.tsx         # Configuration
└── briefing/page.tsx         # Intelligence briefing
```

**Test Criteria**:
- Navigation works between all pages
- Responsive on desktop/tablet
- Dark mode toggles correctly

---

### 2.2 Dashboard Page
**Goal**: Create the main dashboard with key metrics

**Tasks**:
- [x] 2.2.1 Create action cards with icons
- [x] 2.2.2 Add quick action buttons (New Research, View Reports, View Prompts)
- [x] 2.2.3 Create recent topics section
- [x] 2.2.4 Create tracked competitors list
- [x] 2.2.5 Add loading and error states

**Test Criteria**:
- Metrics display correct values from API
- Recent activity shows last 5 reports
- Quick actions navigate to correct pages

---

### 2.3 API Integration Layer
**Goal**: Set up frontend-backend communication

**Tasks**:
- [x] 2.3.1 Create API client (fetch calls in each page)
- [ ] 2.3.2 Set up React Query for data fetching
- [ ] 2.3.3 Create hooks for common queries
- [ ] 2.3.4 Set up WebSocket connection manager
- [x] 2.3.5 Create basic error handling (try/catch in fetches)

**Hooks to Create**:
```typescript
useCompanies()
usePrompts()
useProviders()
useHistory()
useResearch(jobId)
useWebSocket(jobId)
```

**Test Criteria**:
- Data fetches on page load
- Caching works correctly
- Errors display user-friendly messages

---

## Phase 3: Research Workflow

### 3.1 Research Wizard - Step 1: Company Selection
**Goal**: Beautiful company selection interface

**Tasks**:
- [x] 3.1.1 Create company card components (text input field)
- [ ] 3.1.2 Show priority companies prominently
- [ ] 3.1.3 Create searchable dropdown for others
- [ ] 3.1.4 Add multi-select for comparison mode
- [ ] 3.1.5 Style with animations

**Test Criteria**:
- Can select single company
- Can select multiple for comparison
- Selection persists to next step

---

### 3.2 Research Wizard - Step 2: Prompt Selection
**Goal**: Categorized prompt selection

**Tasks**:
- [x] 3.2.1 Display prompts by category (dropdown selector)
- [ ] 3.2.2 Show prompt previews on hover
- [ ] 3.2.3 Allow multi-select for batch runs
- [x] 3.2.4 Preserve category headers from Streamlit

**Test Criteria**:
- Prompts grouped correctly
- Can preview prompt content
- Selection carries forward

---

### 3.3 Research Wizard - Step 3: Provider & Mode
**Goal**: Configure research parameters

**Tasks**:
- [x] 3.3.1 Show provider cards with status (checkboxes)
- [x] 3.3.2 Allow provider selection (multi-select)
- [x] 3.3.3 Add mode toggle (basic/deep)
- [ ] 3.3.4 Show cost estimate
- [ ] 3.3.5 Add synthesis toggle

**Test Criteria**:
- Only active providers selectable
- Cost estimate updates dynamically
- Clear summary before submission

---

### 3.4 Research Progress Page
**Goal**: Real-time progress visualization

**Tasks**:
- [x] 3.4.1 Create progress bar component
- [x] 3.4.2 Show provider status cards
- [ ] 3.4.3 Connect to WebSocket for updates (using polling for now)
- [ ] 3.4.4 Add live log viewer
- [x] 3.4.5 Handle completion redirect

**Test Criteria**:
- Progress updates in real-time
- Each provider shows individual status
- Navigates to results on completion

---

## Phase 4: Results & Export

### 4.1 Results Viewer
**Goal**: Display research results beautifully

**Tasks**:
- [x] 4.1.1 Create tabbed interface for providers
- [x] 4.1.2 Render markdown content properly
- [ ] 4.1.3 Show synthesis tab prominently
- [x] 4.1.4 Display metrics (chars, citations, cost)
- [x] 4.1.5 Add citation viewer with links

**Test Criteria**:
- All provider results display
- Markdown renders correctly
- Citations are clickable

---

### 4.2 Export Functionality
**Goal**: One-click export to multiple formats

**Tasks**:
- [x] 4.2.1 Create export button group
- [x] 4.2.2 Implement download for each format (MD, HTML)
- [ ] 4.2.3 Show loading state during export
- [ ] 4.2.4 Add email option (future)

**Test Criteria**:
- Can download markdown
- Can download HTML
- Can download DOCX
- PDF works if dependencies installed

---

### 4.3 Report History Page
**Goal**: Browse and search past reports

**Tasks**:
- [x] 4.3.1 Create report list with filters
- [x] 4.3.2 Add company and date filters (search bar filters)
- [ ] 4.3.3 Show report previews
- [x] 4.3.4 Enable quick actions (view, download)

**Test Criteria**:
- Can filter by company
- Can filter by date range
- Can open any historical report

---

## Phase 5: Source Library

### 5.1 Source Data Structure
**Goal**: Create and load sources.yaml

**Tasks**:
- [x] 5.1.1 Create initial sources.yaml with examples
- [x] 5.1.2 Create source loader utility
- [x] 5.1.3 Validate source schema
- [x] 5.1.4 Create API endpoints for sources

**Test Criteria**:
- sources.yaml loads without errors
- GET /api/sources returns source list
- Sources grouped by category

---

### 5.2 Source Library UI
**Goal**: View and manage sources

**Tasks**:
- [x] 5.2.1 Create source list page
- [x] 5.2.2 Group by category with icons
- [x] 5.2.3 Show source effectiveness stats
- [x] 5.2.4 Create "Add Source" modal
- [ ] 5.2.5 Create "Edit Source" modal

**Test Criteria**:
- Can view all sources
- Can add new source
- Can edit existing source

---

### 5.3 Source Integration with Research
**Goal**: Use sources during research

**Tasks**:
- [x] 5.3.1 Filter relevant sources for query
- [x] 5.3.2 Inject source hints into prompts
- [x] 5.3.3 Track which sources were cited
- [x] 5.3.4 Update source hit rates

**Test Criteria**:
- Research prompts include source hints
- Source hits tracked after research
- Effectiveness stats update

---

## Phase 6: Delta Intelligence Engine

### 6.1 Delta Analysis Backend
**Goal**: Detect what's new in reports

**Tasks**:
- [x] 6.1.1 Create delta_service.py
- [x] 6.1.2 Load historical reports for company
- [x] 6.1.3 Create comparison prompt for Claude
- [x] 6.1.4 Parse delta findings from response
- [x] 6.1.5 Store findings in database/files

**Delta Finding Schema**:
```python
class DeltaFinding(BaseModel):
    id: str
    report_id: str
    company: str
    finding_text: str
    finding_type: Literal["NEW", "UPDATED", "CONTRADICTED"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    importance: Literal["CRITICAL", "NOTABLE", "MINOR"]
    event_date: Optional[date]
    previous_text: Optional[str]  # For updates/contradictions
```

**Test Criteria**:
- Delta analysis runs after research
- Findings correctly classified
- Stored for later retrieval

---

### 6.2 Intelligence Briefing Page
**Goal**: Show what's new across all research

**Tasks**:
- [x] 6.2.1 Create briefing page layout
- [x] 6.2.2 Show critical updates prominently
- [x] 6.2.3 Show recent findings by company
- [x] 6.2.4 Add configurable time filter
- [ ] 6.2.5 Create trend detection display

**Test Criteria**:
- Briefing shows new findings
- Can filter by time period
- Critical items highlighted

---

### 6.3 Company Timeline View
**Goal**: Chronological intelligence history

**Tasks**:
- [x] 6.3.1 Create timeline component
- [x] 6.3.2 Show findings on timeline
- [x] 6.3.3 Color code by finding type
- [x] 6.3.4 Allow filtering by topic

**Test Criteria**:
- Timeline displays correctly
- Findings in chronological order
- Can filter and search

---

## Phase 7: Scheduled Research

### 7.1 Schedule Configuration
**Goal**: Create and manage research schedules

**Tasks**:
- [x] 7.1.1 Create schedule data model
- [x] 7.1.2 Create schedule CRUD endpoints
- [x] 7.1.3 Create schedule configuration UI
- [x] 7.1.4 Validate schedule parameters

**Test Criteria**:
- Can create new schedule
- Can edit existing schedule
- Can pause/resume schedule

---

### 7.2 Background Job Runner
**Goal**: Execute scheduled research

**Tasks**:
- [x] 7.2.1 Set up APScheduler or Celery
- [x] 7.2.2 Create job execution wrapper
- [x] 7.2.3 Run delta analysis on completion
- [x] 7.2.4 Store execution history

**Test Criteria**:
- Job runs at scheduled time
- Research executes correctly
- Delta analysis runs automatically

---

### 7.3 Notifications
**Goal**: Notify users of scheduled results

**Tasks**:
- [ ] 7.3.1 Create email template
- [ ] 7.3.2 Configure email sending (optional)
- [x] 7.3.3 Show in-app notifications
- [ ] 7.3.4 Add Slack integration (optional)

**Test Criteria**:
- Notification appears in dashboard
- Email sends if configured

---

## Phase 8: Polish & Deploy

### 8.1 UI Polish
**Goal**: Refine all UI elements

**Tasks**:
- [x] 8.1.1 Review all pages for consistency
- [x] 8.1.2 Add loading skeletons everywhere
- [x] 8.1.3 Add micro-animations
- [x] 8.1.4 Ensure responsive design
- [x] 8.1.5 Test dark mode throughout

---

### 8.2 Error Handling
**Goal**: Graceful error handling

**Tasks**:
- [x] 8.2.1 Add error boundaries
- [x] 8.2.2 Create error pages (404, 500)
- [x] 8.2.3 Add retry mechanisms
- [x] 8.2.4 User-friendly error messages

---

### 8.3 Documentation
**Goal**: Prepare for team handoff

**Tasks**:
- [x] 8.3.1 Update README with new setup
- [ ] 8.3.2 Create user guide
- [x] 8.3.3 Document API endpoints
- [x] 8.3.4 Create troubleshooting guide

---

### 8.4 Deployment
**Goal**: Production-ready deployment

**Tasks**:
- [ ] 8.4.1 Configure production environment
- [ ] 8.4.2 Set up process manager (PM2)
- [ ] 8.4.3 Configure reverse proxy (optional)
- [ ] 8.4.4 Final testing
- [ ] 8.4.5 Merge to main branch

---

## Working Session Checklist

Before each work session:
1. [ ] Review this document for current phase
2. [ ] Check off completed tasks
3. [ ] Identify blockers
4. [ ] Set session goals

After each work session:
1. [ ] Update task checkboxes
2. [ ] Commit changes with clear message
3. [ ] Note any deviations or new requirements
4. [ ] Update phase status

---

## Current Status

**Phase**: 8 - Polish & Deploy (COMPLETED)
**Current Task**: All phases complete! Platform ready for use.
**Blockers**: None
**Last Updated**: 2025-11-28

### Session Progress (2025-11-28):
- Fixed backend research execution - jobs now run to completion
- Connected ResearchEngine to FastAPI via ThreadPoolExecutor background tasks
- Fixed frontend/backend field name mismatches (id vs job_id, failed vs error)
- Verified end-to-end flow works: POST research → background execution → results saved
- Built results viewer page with tabbed interface for multiple providers
- Added markdown rendering with react-markdown + remark-gfm
- Added citation viewer with clickable links
- Added export buttons (Markdown, HTML formats)
- Added model name and citation count to result metadata
- Created sources.yaml with 6 categories and 18 curated sources
- Built Sources API (CRUD + search)
- Built Sources UI page with category sidebar, search, and source cards
- Added "Add Source" dialog modal
- Created source_service.py with source matching and tracking functions
- Integrated source service into research router
- Added recommended_sources and cited_sources tracking to ResearchJob model
- Added curated sources display to results page with hit count tracking
- Created delta models (DeltaFinding, DeltaReport, DeltaSummary)
- Created delta_service.py with Claude-powered delta analysis
- Created delta API endpoints (/api/delta/*)
- Integrated delta analysis to run automatically after research
- Created Intelligence Briefing page (/briefing)
- Created Company Timeline view (/briefing/company/[company])
- Created schedule models (ResearchSchedule, ScheduleConfig, Notification)
- Installed and configured APScheduler for background job execution
- Created schedule_service.py with full scheduling logic
- Created schedule API endpoints (/api/schedules/*)
- Created Schedules UI page (/schedules) with create/pause/resume/delete
- Added notification bell to navigation header with real-time updates

### Phase 8 Completion:
- **Added loading skeletons** to all pages (dashboard, research, reports, prompts, sources, briefing, schedules)
- **Added error boundaries** with custom error pages (error.tsx, not-found.tsx, global-error.tsx)
- **Added micro-animations** using Framer Motion (FadeIn, SlideIn, StaggerChildren components)
- **Implemented dark mode** with next-themes (ThemeProvider, ThemeToggle)
- **Enhanced responsive design** with mobile navigation menu
- **Updated frontend README** with comprehensive documentation

### Completed Pages:
- Dashboard (/) - action cards, quick topics, competitors list
- Research Form (/research) - company input, prompt selector, provider checkboxes, mode toggle
- Research Progress (/research/[jobId]) - progress bar, provider status cards, job details, polling
- Results Viewer (/research/[jobId]/results) - tabbed provider results, markdown rendering, citations, export
- Reports List (/reports) - search filter, date grouping, view/download buttons
- Report Detail (/reports/[id]) - full report view with download button
- Prompts Library (/prompts) - two-panel view with category list and content viewer
- Source Library (/sources) - category sidebar, search, source cards, add source modal
- **Intelligence Briefing (/briefing)** - summary cards, critical findings, findings by company
- **Company Timeline (/briefing/company/[company])** - chronological findings timeline with filters
- **Schedules (/schedules)** - create/edit/pause/resume/delete scheduled research

### Backend Endpoints Working:
- GET /api/health
- GET /api/prompts, GET /api/prompts/{id}
- GET /api/reports, GET /api/reports/{id}, GET /api/reports/{id}/download
- POST /api/research - triggers background research
- GET /api/research/{job_id} - returns job status with progress, results, citations
- GET /api/research/{job_id}/export/{provider}?format=md|html - export results
- GET /api/sources - list all sources by category
- GET /api/sources/search?q= - search sources
- POST /api/sources/source - create new source
- PUT /api/sources/source/{id} - update source
- DELETE /api/sources/source/{id} - delete source
- **POST /api/delta/analyze** - run delta analysis on a job
- **GET /api/delta/report/{id}** - get delta report by ID
- **GET /api/delta/job/{job_id}** - get delta report for a job
- **GET /api/delta/reports** - list all delta reports
- **GET /api/delta/findings** - get findings with filters
- **GET /api/delta/briefing** - get intelligence briefing data
- **GET /api/delta/company/{company}/timeline** - get company timeline
- **GET /api/schedules** - list all schedules
- **POST /api/schedules** - create new schedule
- **GET /api/schedules/{id}** - get schedule by ID
- **PUT /api/schedules/{id}** - update schedule
- **DELETE /api/schedules/{id}** - delete schedule
- **POST /api/schedules/{id}/run** - trigger immediate run
- **POST /api/schedules/{id}/pause** - pause schedule
- **POST /api/schedules/{id}/resume** - resume schedule
- **GET /api/schedules/notifications/all** - get all notifications
- **GET /api/schedules/notifications/count** - get unread count
- **POST /api/schedules/notifications/read-all** - mark all as read

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-28 | Use Next.js 14 with App Router | Modern, best DX, server components |
| 2025-11-28 | Use FastAPI for backend | Async, WebSocket support, works with Python research engine |
| 2025-11-28 | Use YAML for sources | More readable than CSV, supports nested data |
| 2025-11-28 | Keep existing research engine | Proven, working, no need to rewrite |

---

## Notes

- **Always** run tests after completing a phase before moving on
- **Never** skip phases - dependencies exist between them
- **Update** this document if requirements change
- **Commit** after each completed task or related group of tasks
