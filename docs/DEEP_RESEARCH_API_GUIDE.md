# Research API Guide

This document outlines how web search is configured for each LLM provider.

## IMPORTANT: Web Search is ALWAYS Enabled

For competitive intelligence, **all queries use web search** to ensure current information.
The "Basic" vs "Deep" mode controls the **depth of research**, not whether web search is used.

| Mode | Web Search | Behavior |
|------|------------|----------|
| **Basic** | ✅ Always ON | Focused search (~5 queries) - faster, lower cost |
| **Deep** | ✅ Always ON | Exhaustive search (~15+ queries) - thorough, higher cost |

## Provider Summary

| Provider | Model | Web Search Method | Notes |
|----------|-------|-------------------|-------|
| **OpenAI** | `gpt-5-search-api` / `o3-deep-research` | Built-in web_search_preview | Responses API |
| **Anthropic** | `claude-opus-4.5` | `web_search_20250305` tool | $10/1K searches |
| **Google** | `gemini-3-pro-preview` | Google Search grounding | Built-in |
| **xAI** | `grok-4` | DeepSearch (web + X search) | Built-in |

---

## 1. OpenAI Deep Research API

### Models
- `o3-deep-research-2025-06-26` - Optimized for in-depth synthesis and higher-quality output
- `o4-mini-deep-research-2025-06-26` - Lightweight and faster, ideal for latency-sensitive use cases

### Python Implementation

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def openai_deep_research(prompt: str, system_message: str = "") -> dict:
    """
    Run OpenAI Deep Research query.
    Returns the response with citations.
    """
    response = client.responses.create(
        model="o3-deep-research-2025-06-26",
        input=[
            {
                "role": "developer",
                "content": [{"type": "input_text", "text": system_message}]
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}]
            }
        ],
        reasoning={"summary": "detailed"},  # "auto" or "detailed"
        tools=[
            {"type": "web_search_preview"},
            {
                "type": "code_interpreter",
                "container": {"type": "auto", "file_ids": []}
            }
        ]
    )

    # Extract final report and citations
    final_content = response.output[-1].content[0]
    return {
        "text": final_content.text,
        "citations": getattr(final_content, 'annotations', [])
    }
```

### Key Parameters
- `reasoning.summary`: "auto" or "detailed" for longer reports
- `tools`: Must include `web_search_preview` for deep research
- Uses the `responses` endpoint (not chat completions)

---

## 2. Anthropic (Claude) Deep Research API

### Models (with web search support)
- `claude-opus-4.5` (recommended for deep research)
- `claude-sonnet-4.5`
- `claude-opus-4.1`
- `claude-opus-4`
- `claude-sonnet-4`
- `claude-haiku-4.5`

### Python Implementation

```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def anthropic_deep_research(prompt: str, max_searches: int = 10) -> dict:
    """
    Run Anthropic Claude Deep Research query with web search.
    Returns the response with citations.
    """
    response = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=16384,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": max_searches  # Limit searches per request
        }]
    )

    # Extract text and any citations from response
    result_text = ""
    citations = []

    for block in response.content:
        if hasattr(block, 'text'):
            result_text += block.text
        if hasattr(block, 'citations'):
            citations.extend(block.citations)

    return {
        "text": result_text,
        "citations": citations,
        "stop_reason": response.stop_reason
    }
```

### Key Parameters
- `tools`: Must include `web_search_20250305` tool
- `max_uses`: Limits number of searches per request (cost control)
- `allowed_domains`: Optional - restrict to specific domains
- `blocked_domains`: Optional - exclude specific domains

### Pricing
- $10 per 1,000 searches + standard token costs

---

## 3. Google Gemini Deep Research API

### Status: Requires Allowlist Access

Google's Deep Research is available via the Discovery Engine API but requires:
1. Google Cloud Project
2. Allowlist approval from Google
3. Discovery Engine app configuration

### Alternative: Gemini with Grounding (Available Now)

For teams without allowlist access, use Gemini with Google Search grounding:

```python
from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def gemini_research_with_grounding(prompt: str) -> dict:
    """
    Run Gemini query with Google Search grounding.
    This is the available alternative to Deep Research.
    """
    response = client.models.generate_content(
        model="gemini-3-pro-preview",
        contents=prompt,
        config={
            "tools": [{"google_search": {}}],
            "thinking_config": {"thinking_budget": 10000}  # Enable deep thinking
        }
    )

    return {
        "text": response.text,
        "grounding_metadata": getattr(response, 'grounding_metadata', None)
    }
```

### Full Deep Research API (If Approved)

```python
# Requires Discovery Engine API access
# Endpoint: https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/collections/default_collection/engines/{APP_ID}/assistants/default_assistant:streamAssist

# This is a streaming endpoint that:
# 1. Assesses if the question is research-related
# 2. Generates a research plan
# 3. Streams questions/answers as it progresses
# 4. Generates a final report with citations and audio summary
```

---

## 4. xAI (Grok) DeepSearch API

### Models
- `grok-4-0709` or `grok-4` (latest stable)
- Context window: 256,000 tokens

### Python Implementation

```python
from openai import OpenAI  # xAI uses OpenAI-compatible API
import os

# xAI uses OpenAI SDK with different base URL
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

def xai_deep_research(prompt: str) -> dict:
    """
    Run xAI Grok DeepSearch query.
    Returns response with web-sourced information.
    """
    response = client.chat.completions.create(
        model="grok-4-0709",
        messages=[
            {
                "role": "system",
                "content": "You are a research assistant. Use DeepSearch to find comprehensive, current information from multiple web sources. Synthesize findings and cite sources."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        tools=["deepsearch"],  # Enable DeepSearch agent
        temperature=0.3  # Lower temperature for factual research
    )

    return {
        "text": response.choices[0].message.content,
        "model": response.model,
        "usage": response.usage
    }
```

### Alternative: Responses API with Server-Side Tools

```python
# For more control, use the Responses API with explicit tools:
# - web_search: Real-time web search and page browsing
# - x_search: Search X posts, users, and threads
# - code_execution: Execute Python code for analysis
```

---

## Mode Selection Logic

For our research app, implement mode selection as follows:

```python
def run_research(provider: str, prompt: str, mode: str = "basic") -> dict:
    """
    Run research with specified provider and mode.

    Args:
        provider: "openai", "anthropic", "google", "xai"
        prompt: The research prompt
        mode: "basic" (standard chat) or "deep" (deep research)

    Returns:
        dict with text, citations, and metadata
    """
    if mode == "basic":
        # Use standard chat completions (current llm CLI approach)
        return run_basic_query(provider, prompt)

    elif mode == "deep":
        # Use deep research APIs
        if provider == "openai":
            return openai_deep_research(prompt)
        elif provider == "anthropic":
            return anthropic_deep_research(prompt)
        elif provider == "google":
            return gemini_research_with_grounding(prompt)
        elif provider == "xai":
            return xai_deep_research(prompt)
```

---

## Cost Estimates (Deep Research Mode)

| Provider | Input Cost | Output Cost | Search Cost | Notes |
|----------|------------|-------------|-------------|-------|
| OpenAI (o3-deep) | ~$10/1M | ~$40/1M | Included | Higher quality, slower |
| Anthropic | $5/1M | $25/1M | $10/1K searches | Claude Opus 4.5 |
| Google | $2/1M | $12/1M | TBD | Requires allowlist |
| xAI | $3/1M | $15/1M | Included | DeepSearch included |

---

## Dependencies

```
# requirements.txt
openai>=1.0.0
anthropic>=0.75.0
google-genai>=0.5.0
python-dotenv>=1.0.0
```

---

## Sources

- [OpenAI Deep Research API Introduction](https://cookbook.openai.com/examples/deep_research_api/introduction_to_deep_research_api)
- [Anthropic Web Search Tool Documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)
- [Google Gemini Deep Research](https://docs.cloud.google.com/gemini/enterprise/docs/research-assistant)
- [xAI Grok 4 API Guide](https://walterpinem.com/grok-4-xai-api-python/)
- [xAI API Documentation](https://docs.x.ai/docs/overview)
