"""Prompts API Router"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
from models.prompts import Prompt, PromptCategory, PromptsResponse

router = APIRouter(prefix="/api/prompts", tags=["prompts"])

# Prompt configurations matching the Streamlit app
PROMPT_CONFIG = {
    "company_specific": {
        "name": "Company-Specific Research",
        "prompts": [
            ("org_structure_and_hiring", "Organization & Hiring", "Analyze organizational structure and hiring patterns"),
            ("executive_movements", "Executive Movements", "Track executive and leadership changes"),
            ("strategic_direction", "Strategic Direction", "Analyze company strategy and priorities"),
            ("products_and_pipeline", "Products & Pipeline", "Research product portfolio and development pipeline"),
            ("technology_roadmap", "Technology Roadmap", "Analyze technology investments and roadmap"),
            ("teaming_relationships", "Teaming & Partnerships", "Research partnerships and teaming arrangements"),
            ("ma_activity", "M&A Activity", "Track mergers, acquisitions, and divestitures"),
            ("rnd_investments", "R&D Investments", "Analyze R&D spending and focus areas"),
            ("program_execution", "Program Execution", "Assess program performance and delivery"),
            ("patents_and_ip", "Patents & IP", "Research patent portfolio and intellectual property"),
            ("contract_awards", "Contract Awards", "Track recent contract wins"),
            ("procurement_opportunities", "Procurement Opportunities", "Identify upcoming procurement opportunities"),
        ]
    },
    "multi_company": {
        "name": "Multi-Company Analysis",
        "prompts": [
            ("multi_primary_competitors_matrix", "Primary Competitors Matrix", "Compare primary competitors across key dimensions"),
            ("multi_cross_competitor_synthesis", "Cross-Competitor Synthesis", "Synthesize competitive landscape insights"),
        ]
    }
}


def get_prompts_dir() -> Path:
    """Get the prompts directory path"""
    # Navigate from backend/ to project root then to prompts/
    return Path(__file__).parent.parent.parent / "prompts"


@router.get("", response_model=PromptsResponse)
async def list_prompts():
    """List all available prompts organized by category"""
    prompts_dir = get_prompts_dir()
    categories = []

    for category_id, category_config in PROMPT_CONFIG.items():
        prompts = []
        for prompt_id, prompt_name, prompt_desc in category_config["prompts"]:
            filename = f"{prompt_id}.md"
            filepath = prompts_dir / filename

            prompts.append(Prompt(
                id=prompt_id,
                name=prompt_name,
                description=prompt_desc,
                category=category_id,
                filename=filename,
                requires_company=not prompt_id.startswith("multi_")
            ))

        categories.append(PromptCategory(
            id=category_id,
            name=category_config["name"],
            prompts=prompts
        ))

    return PromptsResponse(categories=categories)


@router.get("/{prompt_id}", response_model=Prompt)
async def get_prompt(prompt_id: str):
    """Get a specific prompt with its content"""
    prompts_dir = get_prompts_dir()

    # Find the prompt in config
    for category_id, category_config in PROMPT_CONFIG.items():
        for pid, pname, pdesc in category_config["prompts"]:
            if pid == prompt_id:
                filename = f"{prompt_id}.md"
                filepath = prompts_dir / filename

                if not filepath.exists():
                    raise HTTPException(status_code=404, detail=f"Prompt file not found: {filename}")

                content = filepath.read_text()

                return Prompt(
                    id=prompt_id,
                    name=pname,
                    description=pdesc,
                    category=category_id,
                    filename=filename,
                    content=content,
                    requires_company=not prompt_id.startswith("multi_")
                )

    raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}")
