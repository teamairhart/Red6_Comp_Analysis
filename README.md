# Red 6 Competitive Intelligence Research Platform

A multi-provider LLM research orchestration platform that runs competitive intelligence queries across 5 AI providers in parallel, cross-validates findings, and synthesizes results into unified reports with confidence scoring.

## Overview

This platform enables Red 6's competitive intelligence team to:

- **Run parallel research** across OpenAI, Anthropic, Google, xAI, and Perplexity simultaneously
- **Cross-validate findings** by comparing what multiple AI providers report
- **Synthesize results** into unified reports with confidence levels and discrepancy flagging
- **Track costs** per provider and session with budget warnings
- **Export reports** in multiple formats (Markdown, HTML, DOCX, PDF)

## Quick Start

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=your-gemini-key
XAI_API_KEY=xai-...
PERPLEXITY_API_KEY=pplx-...
```

### 3. Run the Application

**Web UI (Recommended):**
```bash
streamlit run app.py
```
Then open http://localhost:8501

**Command Line:**
```bash
python run_research.py "Elbit Systems" leadership_team_dynamics --mode basic
```

## Project Structure

```
competitive_analysis_research/
├── app.py                      # Streamlit web application
├── run_research.py             # CLI entry point
├── api/                        # Core research engine
│   ├── base_researcher.py      # Abstract base class for providers
│   ├── research_engine.py      # Orchestration & parallel execution
│   ├── openai_research.py      # OpenAI GPT-5.1 provider
│   ├── anthropic_research.py   # Anthropic Claude Opus 4.5 provider
│   ├── google_research.py      # Google Gemini 3 Pro provider
│   ├── xai_research.py         # xAI Grok 4 provider
│   ├── perplexity_research.py  # Perplexity Sonar provider
│   ├── synthesis_agent.py      # Cross-validation & synthesis
│   ├── cost_calculator.py      # Token cost tracking
│   └── export_utils.py         # Report export (MD/HTML/DOCX/PDF)
├── prompts/                    # Research prompt templates
├── reports/                    # Generated reports (timestamped)
├── companies.csv               # Target companies list
└── .env                        # API keys (not committed)
```

## Research Providers

| Provider | Model | Web Search | Notes |
|----------|-------|------------|-------|
| OpenAI | GPT-5.1 | Responses API | `web_search_preview` tool |
| Anthropic | Claude Opus 4.5 | MCP Tool | `web_search_20250305`, search costs extra |
| Google | Gemini 3 Pro | Grounding | Google Search grounding |
| xAI | Grok 4 | Built-in | Searches web + X (Twitter) |
| Perplexity | Sonar Pro/Deep | Native | Built into Sonar models |

## Research Modes

### Basic Mode
- Quick research scan (~30-60 seconds)
- 5-10 web searches per provider
- Lower cost (~$0.75-1.50 per run across all providers)
- Good for initial reconnaissance

### Deep Mode
- Comprehensive analysis (~2-5 minutes)
- 15-25+ web searches per provider
- Higher cost (~$2.25-4.50 per run)
- Exhaustive research with verification

## Research Prompts

Located in `prompts/` directory:

| Prompt | Purpose |
|--------|---------|
| `leadership_team_dynamics` | Executive movements, departures, board changes |
| `recent_contract_awards` | Government contracts, military programs |
| `partnerships_and_ma_activity` | Joint ventures, acquisitions |
| `program_performance` | Product performance, technical capabilities |
| `recent_investments_and_new_product_releases` | R&D, new products, funding |
| `future_investments_and_strategic_direction` | Strategic plans, roadmaps |
| `comprehensive_cross_competitor_synthesis` | Holistic competitive analysis |

### Adding New Prompts

Create a markdown file in `prompts/` using `[COMPANY NAME]` as a placeholder:

```markdown
# Research Topic

Research [COMPANY NAME] for the following information:

1. First research area
2. Second research area
...
```

## Cross-Validation Synthesis

When enabled, the synthesis agent (Claude Opus 4.5) analyzes all provider results and:

1. **Identifies agreements** - Facts confirmed by multiple providers (HIGH confidence)
2. **Flags single-source findings** - Information from only one provider (MEDIUM confidence)
3. **Highlights discrepancies** - Where providers contradict each other (CONFLICT)
4. **Calculates agreement score** - 0-100% measure of provider consensus

### Confidence Levels

- `[HIGH]` - 3+ providers agree with citations
- `[MEDIUM]` - 2 providers agree OR 1 provider with strong citations
- `[LOW]` - Single provider, no citations
- `[CONFLICT]` - Providers disagree

## Cost Tracking

The platform tracks API costs in real-time:

**Approximate Pricing (per 1M tokens):**

| Provider | Input | Output |
|----------|-------|--------|
| Anthropic Claude Opus 4.5 | $15.00 | $75.00 |
| OpenAI GPT-5.1 | $2.50 | $10.00 |
| Google Gemini 3 Pro | $1.25 | $5.00 |
| xAI Grok 4 | $3.00 | $15.00 |
| Perplexity Sonar | $3.00 | $15.00 |

Additional costs:
- Anthropic web search: $10 per 1,000 searches
- xAI search: $0.025 per source

Session warning threshold: $5.00

## Report Output

Reports are saved to `reports/{company}/{timestamp}/`:

```
reports/
└── Elbit Systems/
    └── 2025-11-28_143022/
        ├── leadership_team_dynamics-openai.md
        ├── leadership_team_dynamics-anthropic.md
        ├── leadership_team_dynamics-google.md
        ├── leadership_team_dynamics-xai.md
        ├── leadership_team_dynamics-SYNTHESIZED.md
        └── metadata.txt
```

### Export Formats

- **Markdown** - Raw with YAML frontmatter
- **HTML** - Styled with Red 6 branding
- **DOCX** - Microsoft Word document
- **PDF** - Professional PDF (requires WeasyPrint)

## CLI Usage

```bash
# List available companies and prompts
python run_research.py --list

# Basic research
python run_research.py "BAE Systems" recent_contract_awards

# Deep research with specific providers
python run_research.py "Thales" partnerships_and_ma_activity --mode deep --providers anthropic google

# All providers
python run_research.py "Lockheed Martin" leadership_team_dynamics --mode deep
```

## Configuration Files

### companies.csv

```csv
company,website
Elbit Systems,https://www.elbitsystems.com
BAE Systems,https://www.baesystems.com
Thales,https://www.thalesgroup.com
```

### .streamlit/config.toml

UI theme configuration (Red 6 branding colors).

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit UI / CLI                  │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                  Research Engine                     │
│         (Parallel execution via ThreadPool)          │
└───┬─────────┬─────────┬─────────┬─────────┬─────────┘
    │         │         │         │         │
    ▼         ▼         ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────────┐
│OpenAI │ │Anthro │ │Google │ │ xAI   │ │Perplexity │
│GPT5.1 │ │Claude │ │Gemini │ │Grok 4 │ │  Sonar    │
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └─────┬─────┘
    │         │         │         │           │
    └─────────┴─────────┴─────────┴───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Synthesis Agent     │
              │   (Cross-validation)  │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Report Generation   │
              │   (MD/HTML/DOCX/PDF)  │
              └───────────────────────┘
```

## Adding a New Provider

1. Create `api/{provider}_research.py`
2. Extend `BaseResearcher` class
3. Implement `basic_research()` and `deep_research()` methods
4. Return `ResearchResult` objects
5. Add to `ResearchEngine.setup_researchers()` in `research_engine.py`
6. Add pricing to `cost_calculator.py`

## Troubleshooting

### Provider shows as unavailable
- Check API key in `.env` file
- Ensure key doesn't start with placeholder text (e.g., `sk-your-...`)
- Verify API key is valid and has credits

### Google usage metadata error
- Fixed in recent update - usage objects are handled correctly

### PDF export fails
- WeasyPrint requires system dependencies
- Install via: `brew install weasyprint` (macOS) or system package manager

### High costs
- Use Basic mode for initial research
- Select fewer providers
- Monitor session cost in sidebar
- Reset session to clear cost tracking

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Structure
- `api/base_researcher.py` - Interface definition
- `api/research_engine.py` - Orchestration logic
- `api/*_research.py` - Provider implementations
- `api/synthesis_agent.py` - Cross-validation
- `app.py` - UI components and flow

## License

Proprietary - Red 6 Internal Use Only
