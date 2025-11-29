"""Knowledge Base Models - Structured entity storage per company"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, date
from enum import Enum


class EntityType(str, Enum):
    """Types of entities we track"""
    EXECUTIVE = "executive"
    CUSTOMER = "customer"
    CONTRACT = "contract"
    TECHNOLOGY = "technology"
    PRODUCT = "product"
    PARTNER = "partner"
    COMPETITOR = "competitor"
    ACQUISITION = "acquisition"
    FINANCIAL = "financial"
    FACILITY = "facility"
    CERTIFICATION = "certification"
    LAWSUIT = "lawsuit"
    STRATEGY = "strategy"


class Entity(BaseModel):
    """A single tracked entity/fact about a company"""
    id: str
    entity_type: EntityType
    name: str  # Primary identifier (e.g., person name, product name, customer name)
    details: Dict[str, str] = {}  # Flexible key-value for type-specific details
    # e.g., for EXECUTIVE: {"title": "CEO", "since": "2021"}
    # e.g., for CONTRACT: {"value": "$50M", "customer": "US Army", "description": "..."}
    # e.g., for TECHNOLOGY: {"category": "UAV", "status": "production"}
    source_report_id: str  # Which report this came from
    source_date: datetime  # When this was first recorded
    last_updated: datetime  # When this was last confirmed/updated
    confidence: str = "HIGH"  # HIGH, MEDIUM, LOW
    notes: Optional[str] = None  # Additional context


class EntityChange(BaseModel):
    """Represents a change detected in an entity"""
    entity_id: str
    entity_type: EntityType
    entity_name: str
    change_type: str  # "NEW", "UPDATED", "REMOVED", "CONTRADICTED"
    field_changed: Optional[str] = None  # Which field changed (for updates)
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    importance: str = "NOTABLE"  # CRITICAL, NOTABLE, MINOR
    explanation: str  # Human-readable explanation of the change
    source_report_id: str
    detected_at: datetime


class CompanyKnowledgeBase(BaseModel):
    """Complete knowledge base for a single company"""
    company: str
    entities: List[Entity] = []
    last_updated: datetime
    total_reports_processed: int = 0
    report_ids_processed: List[str] = []  # Track which reports contributed


class ExtractionResult(BaseModel):
    """Result of extracting entities from a report"""
    company: str
    report_id: str
    extracted_entities: List[Entity] = []
    changes_detected: List[EntityChange] = []
    extraction_timestamp: datetime
