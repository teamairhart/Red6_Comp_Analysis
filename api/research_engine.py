"""
Research Engine - Orchestrates parallel research across all LLM providers.
"""
import os
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from .base_researcher import ResearchResult
from .openai_research import OpenAIResearcher
from .anthropic_research import AnthropicResearcher
from .google_research import GoogleResearcher
from .xai_research import XAIResearcher
from .perplexity_research import PerplexityResearcher


@dataclass
class ResearchJob:
    """Represents a research job configuration."""
    company: str
    prompt_name: str
    prompt_content: str
    mode: str  # "basic" or "deep"
    output_format: str  # "markdown", "pdf", "docx"


class ResearchEngine:
    """
    Main orchestration engine for multi-provider research.

    Manages:
    - Loading companies and prompts
    - Running parallel research across providers
    - Collecting and saving results
    """

    PROVIDERS = ["openai", "anthropic", "google", "xai", "perplexity"]

    def __init__(self, project_root: str = None):
        """
        Initialize the research engine.

        Args:
            project_root: Path to project root (defaults to parent of api/)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent

        self.project_root = Path(project_root)
        self.prompts_dir = self.project_root / "prompts"
        self.reports_dir = self.project_root / "reports"
        self.companies_file = self.project_root / "companies.csv"

        # Initialize researchers (will be set up when keys are loaded)
        self.researchers: Dict[str, object] = {}

        # Load environment variables
        self._load_env()

    def _load_env(self):
        """Load API keys from .env file."""
        env_file = self.project_root / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

    def setup_researchers(self) -> Dict[str, bool]:
        """
        Initialize all research providers with API keys.

        Returns:
            Dict mapping provider name to success status
        """
        status = {}

        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and not openai_key.startswith("sk-your"):
            try:
                self.researchers["openai"] = OpenAIResearcher(openai_key)
                status["openai"] = True
            except Exception as e:
                status["openai"] = False
                print(f"OpenAI setup failed: {e}")
        else:
            status["openai"] = False

        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and not anthropic_key.startswith("sk-ant-your"):
            try:
                self.researchers["anthropic"] = AnthropicResearcher(anthropic_key)
                status["anthropic"] = True
            except Exception as e:
                status["anthropic"] = False
                print(f"Anthropic setup failed: {e}")
        else:
            status["anthropic"] = False

        # Google
        google_key = os.getenv("GEMINI_API_KEY")
        if google_key and not google_key.startswith("your-gemini"):
            try:
                self.researchers["google"] = GoogleResearcher(google_key)
                status["google"] = True
            except Exception as e:
                status["google"] = False
                print(f"Google setup failed: {e}")
        else:
            status["google"] = False

        # xAI
        xai_key = os.getenv("XAI_API_KEY")
        if xai_key and not xai_key.startswith("xai-your"):
            try:
                self.researchers["xai"] = XAIResearcher(xai_key)
                status["xai"] = True
            except Exception as e:
                status["xai"] = False
                print(f"xAI setup failed: {e}")
        else:
            status["xai"] = False

        # Perplexity
        perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        if perplexity_key and not perplexity_key.startswith("pplx-your"):
            try:
                self.researchers["perplexity"] = PerplexityResearcher(perplexity_key)
                status["perplexity"] = True
            except Exception as e:
                status["perplexity"] = False
                print(f"Perplexity setup failed: {e}")
        else:
            status["perplexity"] = False

        return status

    def get_companies(self) -> List[Dict[str, str]]:
        """Load companies from CSV file."""
        companies = []
        if self.companies_file.exists():
            with open(self.companies_file, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    companies.append({
                        "name": row.get("company", "").strip(),
                        "website": row.get("website", "").strip()
                    })
        return companies

    def get_prompts(self) -> List[Dict[str, str]]:
        """Load available prompts from prompts directory."""
        prompts = []
        if self.prompts_dir.exists():
            for prompt_file in self.prompts_dir.glob("*.md"):
                prompts.append({
                    "name": prompt_file.stem,
                    "filename": prompt_file.name,
                    "path": str(prompt_file)
                })
        return sorted(prompts, key=lambda x: x["name"])

    def load_prompt(self, prompt_name: str) -> str:
        """Load prompt content by name."""
        prompt_path = self.prompts_dir / f"{prompt_name}.md"
        if prompt_path.exists():
            return prompt_path.read_text()
        raise FileNotFoundError(f"Prompt not found: {prompt_name}")

    def run_research(
        self,
        company: str,
        prompt_name: str,
        mode: str = "basic",
        providers: List[str] = None
    ) -> Dict[str, ResearchResult]:
        """
        Run research across all (or specified) providers in parallel.

        Args:
            company: Company name to research
            prompt_name: Name of prompt file (without .md)
            mode: "basic" or "deep"
            providers: List of providers to use (default: all available)

        Returns:
            Dict mapping provider name to ResearchResult
        """
        # Load prompt
        prompt_content = self.load_prompt(prompt_name)

        return self.run_research_with_prompt(company, prompt_content, mode, providers)

    def run_research_with_prompt(
        self,
        company: str,
        prompt_content: str,
        mode: str = "basic",
        providers: List[str] = None
    ) -> Dict[str, ResearchResult]:
        """
        Run research with direct prompt content across all (or specified) providers in parallel.

        Args:
            company: Company name to research
            prompt_content: The actual prompt text to use
            mode: "basic" or "deep"
            providers: List of providers to use (default: all available)

        Returns:
            Dict mapping provider name to ResearchResult
        """
        # Determine which providers to use
        if providers is None:
            providers = list(self.researchers.keys())

        results = {}

        # Run research in parallel
        with ThreadPoolExecutor(max_workers=len(providers)) as executor:
            futures = {}

            for provider in providers:
                if provider in self.researchers:
                    future = executor.submit(
                        self.researchers[provider].research,
                        prompt_content,
                        company,
                        mode
                    )
                    futures[future] = provider

            for future in as_completed(futures):
                provider = futures[future]
                try:
                    results[provider] = future.result()
                except Exception as e:
                    results[provider] = ResearchResult(
                        provider=provider,
                        model="N/A",
                        mode=mode,
                        text="",
                        citations=[],
                        timestamp=datetime.utcnow(),
                        error=str(e)
                    )

        return results

    def save_results(
        self,
        results: Dict[str, ResearchResult],
        company: str,
        prompt_name: str,
        timestamp: datetime = None
    ) -> tuple[List[str], str]:
        """
        Save research results to files with timestamp in filename.

        Args:
            results: Dict of provider -> ResearchResult
            company: Company name
            prompt_name: Prompt name
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Tuple of (list of saved file paths, timestamp string used)
        """
        # Generate timestamp for filenames (format: YYYY-MM-DD_HHMMSS)
        if timestamp is None:
            timestamp = datetime.utcnow()
        timestamp_str = timestamp.strftime("%Y-%m-%d_%H%M%S")

        # Create output directory with timestamp subfolder
        output_dir = self.reports_dir / company / timestamp_str
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []

        for provider, result in results.items():
            # Generate filename with timestamp
            filename = f"{prompt_name}-{provider}.md"
            filepath = output_dir / filename

            # Convert to markdown and save
            content = result.to_markdown()
            filepath.write_text(content)
            saved_files.append(str(filepath))

        # Save metadata file
        metadata_file = output_dir / "metadata.txt"
        metadata_content = f"""Research Run Metadata
=====================
Company: {company}
Prompt: {prompt_name}
Timestamp: {timestamp.isoformat()}
Providers: {', '.join(results.keys())}
"""
        metadata_file.write_text(metadata_content)

        # Also create/update a "latest" symlink for easy access
        latest_link = self.reports_dir / company / "latest"
        if latest_link.is_symlink():
            latest_link.unlink()
        elif latest_link.exists():
            import shutil
            shutil.rmtree(latest_link)
        latest_link.symlink_to(timestamp_str)

        return saved_files, timestamp_str

    def run_and_save(
        self,
        company: str,
        prompt_name: str,
        mode: str = "basic",
        providers: List[str] = None
    ) -> Dict[str, any]:
        """
        Convenience method to run research and save results.

        Returns:
            Dict with results, saved file paths, and timestamp
        """
        timestamp = datetime.utcnow()
        timestamp_display = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

        print(f"\n{'='*60}")
        print(f"Research: {company} | Prompt: {prompt_name} | Mode: {mode}")
        print(f"Timestamp: {timestamp_display}")
        print(f"{'='*60}\n")

        # Run research
        results = self.run_research(company, prompt_name, mode, providers)

        # Report status
        for provider, result in results.items():
            if result.error:
                print(f"  ✗ {provider}: FAILED - {result.error}")
            else:
                print(f"  ✓ {provider}: {len(result.text)} chars, {len(result.citations)} citations")

        # Save results with timestamp
        saved_files, timestamp_str = self.save_results(results, company, prompt_name, timestamp)

        print(f"\nSaved {len(saved_files)} files to reports/{company}/{timestamp_str}/")

        return {
            "results": results,
            "saved_files": saved_files,
            "timestamp": timestamp_str,
            "output_dir": str(self.reports_dir / company / timestamp_str)
        }


def main():
    """CLI entry point for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Run competitive intelligence research")
    parser.add_argument("company", help="Company name to research")
    parser.add_argument("prompt", help="Prompt name (without .md)")
    parser.add_argument("--mode", choices=["basic", "deep"], default="basic",
                        help="Research mode (default: basic)")
    parser.add_argument("--providers", nargs="+", choices=["openai", "anthropic", "google", "xai", "perplexity"],
                        help="Specific providers to use (default: all)")

    args = parser.parse_args()

    # Initialize engine
    engine = ResearchEngine()

    # Setup researchers
    print("Setting up research providers...")
    status = engine.setup_researchers()
    for provider, ok in status.items():
        print(f"  {provider}: {'✓' if ok else '✗'}")

    if not any(status.values()):
        print("\nNo providers available. Check your API keys in .env")
        return

    # Run research
    engine.run_and_save(
        company=args.company,
        prompt_name=args.prompt,
        mode=args.mode,
        providers=args.providers
    )


if __name__ == "__main__":
    main()
