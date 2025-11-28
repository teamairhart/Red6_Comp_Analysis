"""Source Library models"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class SourceReliability(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Source(BaseModel):
    """A curated information source"""
    id: str
    name: str
    url: str
    description: str
    keywords: list[str] = []
    reliability: SourceReliability = SourceReliability.MEDIUM
    update_frequency: str = "varies"
    hit_count: int = 0  # Times this source was cited in research


class SourceCategory(BaseModel):
    """A category of sources"""
    id: str
    name: str
    icon: str
    description: str
    sources: list[Source] = []


class SourceLibrary(BaseModel):
    """The full source library"""
    categories: list[SourceCategory]
    version: str = "1.0"
    last_updated: str = ""


class SourceCreateRequest(BaseModel):
    """Request to create a new source"""
    category_id: str
    name: str
    url: str
    description: str
    keywords: list[str] = []
    reliability: SourceReliability = SourceReliability.MEDIUM
    update_frequency: str = "varies"


class SourceUpdateRequest(BaseModel):
    """Request to update an existing source"""
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[list[str]] = None
    reliability: Optional[SourceReliability] = None
    update_frequency: Optional[str] = None
