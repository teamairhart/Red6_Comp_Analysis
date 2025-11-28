#!/usr/bin/env python3
"""
CLI script to run competitive intelligence research.

Usage:
    python run_research.py <company> <prompt> [--mode basic|deep] [--providers ...]

Examples:
    python run_research.py Elbit leadership_team_dynamics --mode deep
    python run_research.py BAE recent_contract_awards --mode basic --providers anthropic
    python run_research.py "Lockheed Martin" partnerships_and_ma_activity --mode deep
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.research_engine import ResearchEngine


def list_available():
    """List available companies and prompts."""
    engine = ResearchEngine()

    print("\n" + "="*60)
    print("AVAILABLE COMPANIES")
    print("="*60)
    companies = engine.get_companies()
    for i, company in enumerate(companies, 1):
        print(f"  {i:2}. {company['name']}")

    print("\n" + "="*60)
    print("AVAILABLE PROMPTS")
    print("="*60)
    prompts = engine.get_prompts()
    for i, prompt in enumerate(prompts, 1):
        print(f"  {i:2}. {prompt['name']}")

    print("\n" + "="*60)
    print("RESEARCH MODES (Web search ALWAYS enabled)")
    print("="*60)
    print("  • basic - Web search with focused queries (faster, ~5 searches)")
    print("  • deep  - Exhaustive multi-round research (slower, ~15+ searches)")
    print("  NOTE: Both modes use real-time web search for current information")
    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run competitive intelligence research across multiple LLM providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_research.py Elbit leadership_team_dynamics --mode deep
  python run_research.py BAE recent_contract_awards --mode basic
  python run_research.py --list  # Show available companies and prompts
        """
    )

    parser.add_argument("company", nargs="?", help="Company name to research")
    parser.add_argument("prompt", nargs="?", help="Prompt name (without .md extension)")
    parser.add_argument("--mode", choices=["basic", "deep"], default="basic",
                        help="Research mode: basic (fewer searches) or deep (exhaustive research). Both use web search.")
    parser.add_argument("--providers", nargs="+",
                        choices=["openai", "anthropic", "google", "xai"],
                        help="Specific providers to use (default: all available)")
    parser.add_argument("--list", action="store_true",
                        help="List available companies and prompts")

    args = parser.parse_args()

    # Handle --list flag
    if args.list:
        list_available()
        return

    # Validate required arguments
    if not args.company or not args.prompt:
        parser.print_help()
        print("\nError: company and prompt are required (or use --list)")
        sys.exit(1)

    # Initialize engine
    engine = ResearchEngine()

    # Validate company exists
    companies = [c["name"].lower() for c in engine.get_companies()]
    if args.company.lower() not in companies:
        print(f"\nError: Company '{args.company}' not found in companies.csv")
        print("Use --list to see available companies")
        sys.exit(1)

    # Validate prompt exists
    prompts = [p["name"] for p in engine.get_prompts()]
    if args.prompt not in prompts:
        print(f"\nError: Prompt '{args.prompt}' not found in prompts/")
        print("Use --list to see available prompts")
        sys.exit(1)

    # Setup researchers
    print("\nInitializing research providers...")
    status = engine.setup_researchers()

    available_providers = [p for p, ok in status.items() if ok]
    unavailable_providers = [p for p, ok in status.items() if not ok]

    print(f"  Available: {', '.join(available_providers) if available_providers else 'None'}")
    if unavailable_providers:
        print(f"  Unavailable: {', '.join(unavailable_providers)} (check API keys)")

    if not available_providers:
        print("\nError: No providers available. Check your API keys in .env")
        sys.exit(1)

    # Filter to requested providers if specified
    providers_to_use = args.providers if args.providers else available_providers

    # Check if requested providers are available
    for p in providers_to_use:
        if p not in available_providers:
            print(f"\nError: Provider '{p}' not available (API key missing or invalid)")
            sys.exit(1)

    # Confirm before running (web search always incurs costs)
    print(f"\n⚠️  Web search is enabled (API costs will apply)")
    print(f"   Mode: {args.mode} ({'~5 searches' if args.mode == 'basic' else '~15+ searches'} per provider)")
    print(f"   Providers: {', '.join(providers_to_use)}")
    response = input("   Continue? [y/N]: ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    # Run research
    result = engine.run_and_save(
        company=args.company,
        prompt_name=args.prompt,
        mode=args.mode,
        providers=providers_to_use
    )

    # Summary
    print("\n" + "="*60)
    print("RESEARCH COMPLETE")
    print("="*60)
    print(f"Company: {args.company}")
    print(f"Prompt: {args.prompt}")
    print(f"Mode: {args.mode}")
    print(f"\nOutput files:")
    for filepath in result["saved_files"]:
        print(f"  • {filepath}")
    print()


if __name__ == "__main__":
    main()
