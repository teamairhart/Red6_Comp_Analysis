"""Sources API Router"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
from models.sources import (
    Source,
    SourceCategory,
    SourceLibrary,
    SourceCreateRequest,
    SourceUpdateRequest,
    SourceReliability,
)
import yaml
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sources", tags=["sources"])


def get_sources_file() -> Path:
    """Get the path to sources.yaml"""
    return Path(__file__).parent.parent.parent / "sources.yaml"


def load_sources() -> SourceLibrary:
    """Load sources from YAML file"""
    sources_file = get_sources_file()

    if not sources_file.exists():
        return SourceLibrary(categories=[], version="1.0", last_updated="")

    with open(sources_file, "r") as f:
        data = yaml.safe_load(f)

    categories = []
    for cat_data in data.get("categories", []):
        sources = []
        for src_data in cat_data.get("sources", []):
            sources.append(Source(
                id=src_data.get("id", str(uuid.uuid4())),
                name=src_data.get("name", ""),
                url=src_data.get("url", ""),
                description=src_data.get("description", ""),
                keywords=src_data.get("keywords", []),
                reliability=SourceReliability(src_data.get("reliability", "medium")),
                update_frequency=src_data.get("update_frequency", "varies"),
                hit_count=src_data.get("hit_count", 0),
            ))

        categories.append(SourceCategory(
            id=cat_data.get("id", str(uuid.uuid4())),
            name=cat_data.get("name", ""),
            icon=cat_data.get("icon", "folder"),
            description=cat_data.get("description", ""),
            sources=sources,
        ))

    return SourceLibrary(
        categories=categories,
        version=data.get("version", "1.0"),
        last_updated=data.get("last_updated", ""),
    )


def save_sources(library: SourceLibrary):
    """Save sources to YAML file"""
    sources_file = get_sources_file()

    data = {
        "categories": [],
        "version": library.version,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
    }

    for category in library.categories:
        cat_data = {
            "id": category.id,
            "name": category.name,
            "icon": category.icon,
            "description": category.description,
            "sources": [],
        }

        for source in category.sources:
            cat_data["sources"].append({
                "id": source.id,
                "name": source.name,
                "url": source.url,
                "description": source.description,
                "keywords": source.keywords,
                "reliability": source.reliability.value,
                "update_frequency": source.update_frequency,
                "hit_count": source.hit_count,
            })

        data["categories"].append(cat_data)

    with open(sources_file, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


@router.get("", response_model=SourceLibrary)
async def list_sources():
    """Get all sources organized by category"""
    return load_sources()


@router.get("/categories", response_model=list[SourceCategory])
async def list_categories():
    """Get all source categories"""
    library = load_sources()
    return library.categories


@router.get("/category/{category_id}", response_model=SourceCategory)
async def get_category(category_id: str):
    """Get a specific category with its sources"""
    library = load_sources()

    for category in library.categories:
        if category.id == category_id:
            return category

    raise HTTPException(status_code=404, detail=f"Category not found: {category_id}")


@router.get("/source/{source_id}", response_model=Source)
async def get_source(source_id: str):
    """Get a specific source by ID"""
    library = load_sources()

    for category in library.categories:
        for source in category.sources:
            if source.id == source_id:
                return source

    raise HTTPException(status_code=404, detail=f"Source not found: {source_id}")


@router.post("/source", response_model=Source)
async def create_source(request: SourceCreateRequest):
    """Create a new source in a category"""
    library = load_sources()

    # Find the category
    category_found = False
    for category in library.categories:
        if category.id == request.category_id:
            category_found = True

            # Create new source
            new_source = Source(
                id=str(uuid.uuid4())[:8],
                name=request.name,
                url=request.url,
                description=request.description,
                keywords=request.keywords,
                reliability=request.reliability,
                update_frequency=request.update_frequency,
            )

            category.sources.append(new_source)
            save_sources(library)
            return new_source

    if not category_found:
        raise HTTPException(status_code=404, detail=f"Category not found: {request.category_id}")


@router.put("/source/{source_id}", response_model=Source)
async def update_source(source_id: str, request: SourceUpdateRequest):
    """Update an existing source"""
    library = load_sources()

    for category in library.categories:
        for i, source in enumerate(category.sources):
            if source.id == source_id:
                # Update fields if provided
                if request.name is not None:
                    source.name = request.name
                if request.url is not None:
                    source.url = request.url
                if request.description is not None:
                    source.description = request.description
                if request.keywords is not None:
                    source.keywords = request.keywords
                if request.reliability is not None:
                    source.reliability = request.reliability
                if request.update_frequency is not None:
                    source.update_frequency = request.update_frequency

                category.sources[i] = source
                save_sources(library)
                return source

    raise HTTPException(status_code=404, detail=f"Source not found: {source_id}")


@router.delete("/source/{source_id}")
async def delete_source(source_id: str):
    """Delete a source"""
    library = load_sources()

    for category in library.categories:
        for i, source in enumerate(category.sources):
            if source.id == source_id:
                category.sources.pop(i)
                save_sources(library)
                return {"message": f"Source {source_id} deleted"}

    raise HTTPException(status_code=404, detail=f"Source not found: {source_id}")


@router.get("/search")
async def search_sources(q: str):
    """Search sources by keyword or name"""
    library = load_sources()
    results = []

    q_lower = q.lower()

    for category in library.categories:
        for source in category.sources:
            # Check name, description, and keywords
            if (q_lower in source.name.lower() or
                q_lower in source.description.lower() or
                any(q_lower in kw.lower() for kw in source.keywords)):
                results.append({
                    "source": source,
                    "category_id": category.id,
                    "category_name": category.name,
                })

    return {"query": q, "results": results, "count": len(results)}
