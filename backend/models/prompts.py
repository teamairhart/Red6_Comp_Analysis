"""Prompt models"""
from pydantic import BaseModel
from typing import Optional


class Prompt(BaseModel):
    """A research prompt template"""
    id: str
    name: str
    description: str
    category: str
    filename: str
    content: Optional[str] = None
    requires_company: bool = True  # Some prompts like synthesis don't need company


class PromptCategory(BaseModel):
    """A category of prompts"""
    id: str
    name: str
    prompts: list[Prompt]


class PromptsResponse(BaseModel):
    """Response containing all prompts organized by category"""
    categories: list[PromptCategory]
