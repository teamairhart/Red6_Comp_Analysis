"""Source Service - handles source matching and tracking"""
from pathlib import Path
from typing import List, Dict, Optional
import yaml
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


def get_sources_file() -> Path:
    """Get the path to sources.yaml"""
    return Path(__file__).parent.parent.parent / "sources.yaml"


def load_all_sources() -> List[Dict]:
    """Load all sources from YAML file as flat list"""
    sources_file = get_sources_file()

    if not sources_file.exists():
        return []

    with open(sources_file, "r") as f:
        data = yaml.safe_load(f)

    sources = []
    for category in data.get("categories", []):
        for source in category.get("sources", []):
            source["category_id"] = category.get("id")
            source["category_name"] = category.get("name")
            sources.append(source)

    return sources


def find_relevant_sources(prompt_keywords: List[str], limit: int = 5) -> List[Dict]:
    """
    Find sources relevant to the given keywords.

    Args:
        prompt_keywords: List of keywords to match against source keywords
        limit: Maximum number of sources to return

    Returns:
        List of matching sources sorted by relevance score
    """
    all_sources = load_all_sources()
    scored_sources = []

    prompt_keywords_lower = [kw.lower() for kw in prompt_keywords]

    for source in all_sources:
        score = 0
        source_keywords = [kw.lower() for kw in source.get("keywords", [])]
        source_name = source.get("name", "").lower()
        source_desc = source.get("description", "").lower()

        # Score based on keyword matches
        for prompt_kw in prompt_keywords_lower:
            # Direct keyword match
            if prompt_kw in source_keywords:
                score += 3

            # Partial keyword match
            for src_kw in source_keywords:
                if prompt_kw in src_kw or src_kw in prompt_kw:
                    score += 1

            # Name or description match
            if prompt_kw in source_name:
                score += 2
            if prompt_kw in source_desc:
                score += 1

        # Boost high-reliability sources
        if source.get("reliability") == "high":
            score += 1

        if score > 0:
            scored_sources.append((score, source))

    # Sort by score descending
    scored_sources.sort(key=lambda x: x[0], reverse=True)

    return [s[1] for s in scored_sources[:limit]]


def format_sources_for_prompt(sources: List[Dict]) -> str:
    """
    Format sources as a hint section to append to research prompts.

    Args:
        sources: List of source dictionaries

    Returns:
        Formatted string to append to prompt
    """
    if not sources:
        return ""

    lines = [
        "\n\n---",
        "## Recommended Sources",
        "Consider checking these curated sources for authoritative information:",
        ""
    ]

    for source in sources:
        lines.append(f"- **{source['name']}** ({source['url']})")
        lines.append(f"  {source['description']}")

    return "\n".join(lines)


def extract_domains_from_citations(citations: List[Dict]) -> List[str]:
    """
    Extract unique domains from a list of citations.

    Args:
        citations: List of citation dicts with 'url' key

    Returns:
        List of unique domain names
    """
    domains = set()
    for citation in citations:
        url = citation.get("url", "")
        if url:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                # Remove www. prefix
                if domain.startswith("www."):
                    domain = domain[4:]
                domains.add(domain)
            except Exception:
                pass

    return list(domains)


def match_citations_to_sources(citations: List[Dict]) -> List[str]:
    """
    Match citations to curated sources and return matched source IDs.

    Args:
        citations: List of citation dicts with 'url' key

    Returns:
        List of source IDs that were cited
    """
    cited_domains = extract_domains_from_citations(citations)
    all_sources = load_all_sources()
    matched_ids = []

    for source in all_sources:
        source_url = source.get("url", "")
        if source_url:
            try:
                parsed = urlparse(source_url)
                source_domain = parsed.netloc.lower()
                if source_domain.startswith("www."):
                    source_domain = source_domain[4:]

                # Check if any cited domain matches this source
                for cited_domain in cited_domains:
                    if cited_domain == source_domain or cited_domain.endswith("." + source_domain):
                        matched_ids.append(source["id"])
                        break
            except Exception:
                pass

    return matched_ids


def update_source_hit_counts(source_ids: List[str]):
    """
    Increment hit_count for the given source IDs.

    Args:
        source_ids: List of source IDs to increment
    """
    if not source_ids:
        return

    sources_file = get_sources_file()

    if not sources_file.exists():
        return

    with open(sources_file, "r") as f:
        data = yaml.safe_load(f)

    updated = False
    for category in data.get("categories", []):
        for source in category.get("sources", []):
            if source.get("id") in source_ids:
                current_count = source.get("hit_count", 0)
                source["hit_count"] = current_count + 1
                updated = True
                logger.info(f"Incremented hit_count for source {source['id']} to {source['hit_count']}")

    if updated:
        with open(sources_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def get_prompt_keywords(prompt_id: str) -> List[str]:
    """
    Extract keywords from a prompt ID for source matching.

    Args:
        prompt_id: The prompt ID (e.g., "executive_movements", "contract_awards")

    Returns:
        List of keywords derived from the prompt
    """
    # Map prompt IDs to relevant keywords for source matching
    prompt_keyword_map = {
        "executive_movements": ["hiring", "executives", "leadership", "personnel"],
        "org_structure_and_hiring": ["organization", "hiring", "jobs", "employees"],
        "strategic_direction": ["strategy", "business", "markets", "analysis"],
        "products_and_pipeline": ["technology", "products", "research", "patents"],
        "technology_roadmap": ["technology", "research", "patents", "innovation"],
        "teaming_relationships": ["contracts", "partnerships", "business"],
        "ma_activity": ["business", "finance", "markets", "acquisitions"],
        "rnd_investments": ["research", "technology", "patents", "innovation"],
        "program_execution": ["contracts", "defense", "military", "programs"],
        "patents_and_ip": ["patents", "intellectual property", "technology"],
        "contract_awards": ["contracts", "federal", "procurement", "awards", "defense"],
        "procurement_opportunities": ["procurement", "contracts", "federal", "opportunities"],
    }

    # Get mapped keywords or derive from prompt_id
    keywords = prompt_keyword_map.get(prompt_id, [])

    # Also add words from the prompt_id itself
    words = prompt_id.replace("_", " ").split()
    keywords.extend(words)

    return list(set(keywords))
