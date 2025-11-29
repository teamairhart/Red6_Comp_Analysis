"""Knowledge Base Service - Entity extraction and change detection"""
import os
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import anthropic

from models.knowledge_base import (
    Entity,
    EntityType,
    EntityChange,
    CompanyKnowledgeBase,
    ExtractionResult,
)

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent


def get_knowledge_base_dir() -> Path:
    """Get the knowledge base storage directory"""
    kb_dir = get_project_root() / "knowledge_base"
    kb_dir.mkdir(exist_ok=True)
    return kb_dir


def get_anthropic_client() -> Optional[anthropic.Anthropic]:
    """Get Anthropic client from environment"""
    env_file = get_project_root() / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key.strip() == "ANTHROPIC_API_KEY":
                        os.environ["ANTHROPIC_API_KEY"] = value.strip()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-your"):
        logger.warning("Anthropic API key not configured for knowledge base extraction")
        return None

    return anthropic.Anthropic(api_key=api_key)


# Prompt for entity extraction
ENTITY_EXTRACTION_PROMPT = """You are an intelligence analyst extracting structured facts from a competitive intelligence report about {company}.

## REPORT CONTENT
{report_content}

## YOUR TASK
Extract all significant entities and facts from this report into structured data. Focus on:

1. **EXECUTIVE** - Key personnel (CEO, CFO, CTO, Board members, etc.)
   - Details: title, since (start date if known), previous_role, notes

2. **CUSTOMER** - Organizations that buy from this company
   - Details: contract_value, contract_date, product_purchased, region, notes

3. **CONTRACT** - Specific contract awards or deals
   - Details: value, customer, description, award_date, duration, notes

4. **TECHNOLOGY** - Key technologies, platforms, or capabilities
   - Details: category, status (development/production/deployed), description, notes

5. **PRODUCT** - Specific products or product lines
   - Details: category, status, customers, description, notes

6. **PARTNER** - Strategic partners, joint ventures, teaming arrangements
   - Details: partner_type, description, since, notes

7. **COMPETITOR** - Direct competitors mentioned
   - Details: competitive_area, notes

8. **ACQUISITION** - M&A activity (acquisitions made or being acquired)
   - Details: target_or_acquirer, value, date, status, rationale, notes

9. **FINANCIAL** - Key financial metrics
   - Details: metric_type (revenue/profit/backlog/etc), value, period, trend, notes

10. **FACILITY** - Manufacturing sites, R&D centers, offices
    - Details: location, type, size, notes

11. **CERTIFICATION** - Certifications, clearances, qualifications
    - Details: certifying_body, scope, expiration, notes

12. **LAWSUIT** - Legal matters, disputes
    - Details: opposing_party, type, status, value, notes

13. **STRATEGY** - Strategic initiatives, announced plans
    - Details: category, timeline, description, notes

## OUTPUT FORMAT
Return a JSON array of entities. Each entity must have:
- entity_type: One of the types above (uppercase)
- name: Primary identifier (person name, product name, customer name, etc.)
- details: Object with type-specific key-value pairs
- confidence: HIGH, MEDIUM, or LOW
- notes: Optional additional context

Example:
```json
[
  {{
    "entity_type": "EXECUTIVE",
    "name": "John Smith",
    "details": {{
      "title": "CEO",
      "since": "January 2024",
      "previous_role": "COO"
    }},
    "confidence": "HIGH",
    "notes": "Promoted from COO role"
  }},
  {{
    "entity_type": "CONTRACT",
    "name": "US Army IVAS Phase 2",
    "details": {{
      "value": "$500M",
      "customer": "US Army",
      "description": "Next-generation augmented reality headsets",
      "award_date": "November 2024",
      "duration": "5 years"
    }},
    "confidence": "HIGH",
    "notes": null
  }},
  {{
    "entity_type": "TECHNOLOGY",
    "name": "ARCAS AI Rifle Sight",
    "details": {{
      "category": "Soldier Systems",
      "status": "production",
      "description": "AI-powered rifle sight with target identification"
    }},
    "confidence": "HIGH",
    "notes": "Being deployed to multiple NATO countries"
  }}
]
```

IMPORTANT:
- Extract ALL significant entities, not just a few examples
- Be specific with names - use full product names, full person names
- Include financial values with currency when mentioned
- If confidence is uncertain, mark as MEDIUM or LOW
- Return ONLY the JSON array, no other text
- If no entities found, return empty array: []
"""


CHANGE_DETECTION_PROMPT = """You are an intelligence analyst comparing newly extracted entities against an existing knowledge base for {company}.

## EXISTING KNOWLEDGE BASE
These are the currently known facts about {company}:
{existing_kb}

## NEWLY EXTRACTED ENTITIES
These entities were just extracted from a new report:
{new_entities}

## YOUR TASK
Compare the new entities against the existing knowledge base and identify:

1. **NEW** - Entities that don't exist in the knowledge base at all
2. **UPDATED** - Entities that exist but have changed values (e.g., new title, new contract value)
3. **CONTRADICTED** - Entities that directly contradict existing information
4. **CONFIRMED** - Entities that match existing data (no change needed)

For each change (NEW, UPDATED, CONTRADICTED), rate its importance:
- **CRITICAL** - Major change requiring immediate attention (new CEO, major acquisition, lost contract)
- **NOTABLE** - Significant change worth highlighting (new product, new customer, updated financials)
- **MINOR** - Small update or addition (minor detail change, confirmation of known info)

## OUTPUT FORMAT
Return a JSON array of changes. Each change must have:
- entity_name: Name of the entity
- entity_type: Type of entity
- change_type: NEW, UPDATED, CONTRADICTED, or CONFIRMED
- field_changed: Which field changed (for UPDATED/CONTRADICTED, null otherwise)
- old_value: Previous value (for UPDATED/CONTRADICTED)
- new_value: New value
- importance: CRITICAL, NOTABLE, or MINOR
- explanation: Brief explanation of why this matters

Example:
```json
[
  {{
    "entity_name": "Jane Doe",
    "entity_type": "EXECUTIVE",
    "change_type": "NEW",
    "field_changed": null,
    "old_value": null,
    "new_value": "CFO since October 2024",
    "importance": "CRITICAL",
    "explanation": "New CFO appointment - leadership change"
  }},
  {{
    "entity_name": "US Army IVAS Contract",
    "entity_type": "CONTRACT",
    "change_type": "UPDATED",
    "field_changed": "value",
    "old_value": "$400M",
    "new_value": "$500M",
    "importance": "NOTABLE",
    "explanation": "Contract value increased by $100M - indicates expanded scope"
  }},
  {{
    "entity_name": "ARCAS AI Rifle Sight",
    "entity_type": "TECHNOLOGY",
    "change_type": "CONFIRMED",
    "field_changed": null,
    "old_value": null,
    "new_value": null,
    "importance": "MINOR",
    "explanation": "Existing technology confirmed in new report"
  }}
]
```

IMPORTANT:
- Focus on meaningful changes, not minor wording differences
- CONFIRMED items should be MINOR importance
- NEW executives or major contracts should be CRITICAL
- Return ONLY the JSON array, no other text
"""


def load_knowledge_base(company: str) -> Optional[CompanyKnowledgeBase]:
    """Load the knowledge base for a company from disk"""
    kb_dir = get_knowledge_base_dir()
    # Sanitize company name for filename
    safe_name = company.lower().replace(" ", "_").replace("/", "_")
    kb_file = kb_dir / f"{safe_name}.json"

    if not kb_file.exists():
        return None

    try:
        with open(kb_file, "r") as f:
            data = json.load(f)
        return CompanyKnowledgeBase(**data)
    except Exception as e:
        logger.error(f"Failed to load knowledge base for {company}: {e}")
        return None


def save_knowledge_base(kb: CompanyKnowledgeBase) -> None:
    """Save the knowledge base for a company to disk"""
    kb_dir = get_knowledge_base_dir()
    safe_name = kb.company.lower().replace(" ", "_").replace("/", "_")
    kb_file = kb_dir / f"{safe_name}.json"

    try:
        with open(kb_file, "w") as f:
            json.dump(kb.model_dump(mode="json"), f, indent=2, default=str)
        logger.info(f"Saved knowledge base for {kb.company} with {len(kb.entities)} entities")
    except Exception as e:
        logger.error(f"Failed to save knowledge base for {kb.company}: {e}")


def extract_entities_from_report(
    company: str,
    report_content: str,
    report_id: str,
) -> List[Entity]:
    """
    Extract structured entities from a research report using Claude.

    Args:
        company: Company name
        report_content: Full text of the research report
        report_id: ID of the source report

    Returns:
        List of extracted Entity objects
    """
    client = get_anthropic_client()
    if not client:
        logger.error("Cannot extract entities - Anthropic client not available")
        return []

    prompt = ENTITY_EXTRACTION_PROMPT.format(
        company=company,
        report_content=report_content[:50000],  # Limit content size
    )

    try:
        logger.info(f"Extracting entities from report for {company}")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text
        entities = _parse_entities_response(response_text, report_id, company)

        logger.info(f"Extracted {len(entities)} entities for {company}")
        return entities

    except Exception as e:
        logger.error(f"Entity extraction failed for {company}: {e}")
        return []


def detect_changes(
    company: str,
    existing_kb: CompanyKnowledgeBase,
    new_entities: List[Entity],
    report_id: str,
) -> List[EntityChange]:
    """
    Compare new entities against existing knowledge base and detect changes.

    Args:
        company: Company name
        existing_kb: Current knowledge base
        new_entities: Newly extracted entities
        report_id: ID of the source report

    Returns:
        List of detected changes
    """
    client = get_anthropic_client()
    if not client:
        logger.error("Cannot detect changes - Anthropic client not available")
        return []

    # Format existing KB for the prompt
    existing_kb_text = _format_kb_for_prompt(existing_kb)
    new_entities_text = _format_entities_for_prompt(new_entities)

    prompt = CHANGE_DETECTION_PROMPT.format(
        company=company,
        existing_kb=existing_kb_text,
        new_entities=new_entities_text,
    )

    try:
        logger.info(f"Detecting changes for {company} ({len(new_entities)} new entities vs {len(existing_kb.entities)} existing)")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text
        changes = _parse_changes_response(response_text, report_id)

        # Filter out CONFIRMED items - we only care about actual changes
        significant_changes = [c for c in changes if c.change_type != "CONFIRMED"]

        logger.info(f"Detected {len(significant_changes)} significant changes for {company}")
        return significant_changes

    except Exception as e:
        logger.error(f"Change detection failed for {company}: {e}")
        return []


def process_report_for_knowledge_base(
    company: str,
    report_content: str,
    report_id: str,
) -> ExtractionResult:
    """
    Full pipeline: Extract entities, compare to KB, detect changes, update KB.

    Args:
        company: Company name
        report_content: Full text of the research report
        report_id: ID of the source report

    Returns:
        ExtractionResult with entities and changes
    """
    now = datetime.utcnow()

    # Step 1: Extract entities from the new report
    new_entities = extract_entities_from_report(company, report_content, report_id)

    if not new_entities:
        logger.warning(f"No entities extracted from report for {company}")
        return ExtractionResult(
            company=company,
            report_id=report_id,
            extracted_entities=[],
            changes_detected=[],
            extraction_timestamp=now,
        )

    # Step 2: Load existing knowledge base (or create empty one)
    existing_kb = load_knowledge_base(company)
    if not existing_kb:
        existing_kb = CompanyKnowledgeBase(
            company=company,
            entities=[],
            last_updated=now,
            total_reports_processed=0,
            report_ids_processed=[],
        )

    # Step 3: Detect changes if we have existing data
    changes = []
    if existing_kb.entities:
        changes = detect_changes(company, existing_kb, new_entities, report_id)
    else:
        # First report - all entities are NEW
        for entity in new_entities:
            changes.append(EntityChange(
                entity_id=entity.id,
                entity_type=entity.entity_type,
                entity_name=entity.name,
                change_type="NEW",
                new_value=f"{entity.entity_type.value}: {entity.name}",
                importance="NOTABLE",  # First-time entries are notable, not critical
                explanation=f"First recorded data for {company}",
                source_report_id=report_id,
                detected_at=now,
            ))

    # Step 4: Update the knowledge base
    _update_knowledge_base(existing_kb, new_entities, report_id, now)
    save_knowledge_base(existing_kb)

    return ExtractionResult(
        company=company,
        report_id=report_id,
        extracted_entities=new_entities,
        changes_detected=changes,
        extraction_timestamp=now,
    )


def _update_knowledge_base(
    kb: CompanyKnowledgeBase,
    new_entities: List[Entity],
    report_id: str,
    timestamp: datetime,
) -> None:
    """Update the knowledge base with new entities"""
    # Build a lookup of existing entities by type+name
    existing_lookup: Dict[str, Entity] = {}
    for entity in kb.entities:
        key = f"{entity.entity_type.value}:{entity.name.lower()}"
        existing_lookup[key] = entity

    # Process new entities
    for new_entity in new_entities:
        key = f"{new_entity.entity_type.value}:{new_entity.name.lower()}"

        if key in existing_lookup:
            # Update existing entity
            existing = existing_lookup[key]
            existing.details.update(new_entity.details)
            existing.last_updated = timestamp
            existing.source_report_id = report_id
            if new_entity.confidence == "HIGH":
                existing.confidence = "HIGH"
        else:
            # Add new entity
            kb.entities.append(new_entity)

    kb.last_updated = timestamp
    kb.total_reports_processed += 1
    if report_id not in kb.report_ids_processed:
        kb.report_ids_processed.append(report_id)


def _format_kb_for_prompt(kb: CompanyKnowledgeBase) -> str:
    """Format knowledge base for inclusion in prompt"""
    if not kb.entities:
        return "No existing data."

    sections = {}
    for entity in kb.entities:
        type_name = entity.entity_type.value
        if type_name not in sections:
            sections[type_name] = []

        details_str = ", ".join(f"{k}: {v}" for k, v in entity.details.items())
        sections[type_name].append(f"- {entity.name}: {details_str}")

    output = []
    for type_name, items in sorted(sections.items()):
        output.append(f"\n### {type_name.upper()}")
        output.extend(items)

    return "\n".join(output)


def _format_entities_for_prompt(entities: List[Entity]) -> str:
    """Format entities list for inclusion in prompt"""
    if not entities:
        return "No entities extracted."

    sections = {}
    for entity in entities:
        type_name = entity.entity_type.value
        if type_name not in sections:
            sections[type_name] = []

        details_str = ", ".join(f"{k}: {v}" for k, v in entity.details.items())
        sections[type_name].append(f"- {entity.name}: {details_str}")

    output = []
    for type_name, items in sorted(sections.items()):
        output.append(f"\n### {type_name.upper()}")
        output.extend(items)

    return "\n".join(output)


def _parse_entities_response(response_text: str, report_id: str, company: str) -> List[Entity]:
    """Parse Claude's JSON response into Entity objects"""
    entities = []
    now = datetime.utcnow()

    try:
        json_text = _extract_json(response_text)
        raw_entities = json.loads(json_text)

        for raw in raw_entities:
            try:
                entity_type = EntityType(raw.get("entity_type", "").lower())
            except ValueError:
                logger.warning(f"Unknown entity type: {raw.get('entity_type')}")
                continue

            entity = Entity(
                id=str(uuid.uuid4()),
                entity_type=entity_type,
                name=raw.get("name", "Unknown"),
                details=raw.get("details", {}),
                source_report_id=report_id,
                source_date=now,
                last_updated=now,
                confidence=raw.get("confidence", "MEDIUM"),
                notes=raw.get("notes"),
            )
            entities.append(entity)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse entities JSON: {e}")
        logger.debug(f"Response was: {response_text[:500]}")
    except Exception as e:
        logger.error(f"Error processing entities: {e}")

    return entities


def _parse_changes_response(response_text: str, report_id: str) -> List[EntityChange]:
    """Parse Claude's JSON response into EntityChange objects"""
    changes = []
    now = datetime.utcnow()

    try:
        json_text = _extract_json(response_text)
        raw_changes = json.loads(json_text)

        for raw in raw_changes:
            try:
                entity_type = EntityType(raw.get("entity_type", "").lower())
            except ValueError:
                logger.warning(f"Unknown entity type in change: {raw.get('entity_type')}")
                entity_type = EntityType.STRATEGY  # Fallback

            change = EntityChange(
                entity_id=str(uuid.uuid4()),
                entity_type=entity_type,
                entity_name=raw.get("entity_name", "Unknown"),
                change_type=raw.get("change_type", "NEW"),
                field_changed=raw.get("field_changed"),
                old_value=raw.get("old_value"),
                new_value=raw.get("new_value"),
                importance=raw.get("importance", "NOTABLE"),
                explanation=raw.get("explanation", ""),
                source_report_id=report_id,
                detected_at=now,
            )
            changes.append(change)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse changes JSON: {e}")
        logger.debug(f"Response was: {response_text[:500]}")
    except Exception as e:
        logger.error(f"Error processing changes: {e}")

    return changes


def _extract_json(text: str) -> str:
    """Extract JSON from response, handling markdown code blocks"""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        json_lines = []
        in_block = False
        for line in lines:
            if line.startswith("```") and not in_block:
                in_block = True
                continue
            elif line.startswith("```") and in_block:
                break
            elif in_block:
                json_lines.append(line)
        return "\n".join(json_lines)
    return text


def get_company_knowledge_base(company: str) -> Optional[CompanyKnowledgeBase]:
    """Public function to get a company's knowledge base"""
    return load_knowledge_base(company)


def list_all_knowledge_bases() -> List[str]:
    """List all companies with knowledge bases"""
    kb_dir = get_knowledge_base_dir()
    companies = []
    for f in kb_dir.glob("*.json"):
        # Convert filename back to company name
        name = f.stem.replace("_", " ").title()
        companies.append(name)
    return sorted(companies)
