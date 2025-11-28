"""
Red 6 Competitive Intelligence Research Platform
Streamlit MVP Application
"""
import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from api import (
    ResearchEngine,
    SynthesisAgent,
    save_synthesis_report,
    ReportExporter,
    export_report
)
from api.cost_calculator import CostCalculator, calculate_query_cost, format_cost_table

# Page config
st.set_page_config(
    page_title="Red 6 Competitive Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }

    /* Card styling */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        height: 100%;
    }
    .metric-card h3 {
        color: #6b7280;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .value {
        color: #1f2937;
        font-size: 2rem;
        font-weight: 700;
    }

    /* Status badges */
    .status-success {
        background-color: #dcfce7;
        color: #166534;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .status-error {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .status-pending {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    /* Provider cards */
    .provider-card {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .provider-card.success {
        border-left-color: #22c55e;
    }
    .provider-card.error {
        border-left-color: #ef4444;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8fafc;
    }

    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Report viewer */
    .report-container {
        background: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'engine' not in st.session_state:
    st.session_state.engine = ResearchEngine()
    st.session_state.provider_status = st.session_state.engine.setup_researchers()

if 'research_results' not in st.session_state:
    st.session_state.research_results = None

if 'synthesis_result' not in st.session_state:
    st.session_state.synthesis_result = None

if 'cost_calculator' not in st.session_state:
    st.session_state.cost_calculator = CostCalculator()

if 'last_query_costs' not in st.session_state:
    st.session_state.last_query_costs = None


def get_report_history(company: str = None) -> list:
    """Get list of previous research runs."""
    reports_dir = Path(__file__).parent / "reports"
    history = []

    if not reports_dir.exists():
        return history

    companies = [company] if company else [d.name for d in reports_dir.iterdir() if d.is_dir()]

    for comp in companies:
        comp_dir = reports_dir / comp
        if not comp_dir.exists():
            continue

        for run_dir in comp_dir.iterdir():
            if run_dir.is_dir() and run_dir.name != "latest" and not run_dir.is_symlink():
                # Check for metadata
                metadata_file = run_dir / "metadata.txt"
                if metadata_file.exists():
                    history.append({
                        "company": comp,
                        "timestamp": run_dir.name,
                        "path": str(run_dir),
                        "files": [f.name for f in run_dir.glob("*.md")]
                    })

    # Sort by timestamp descending
    history.sort(key=lambda x: x["timestamp"], reverse=True)
    return history


def render_header():
    """Render the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Red 6 Competitive Intelligence</h1>
        <p>Multi-Provider AI Research Platform with Cross-Validation</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with research controls."""
    with st.sidebar:
        st.markdown("## 📊 Research Configuration")
        st.markdown("---")

        # Prompt selection FIRST (so we can determine if company is needed)
        prompts = st.session_state.engine.get_prompts()
        prompt_names = [p["name"] for p in prompts]

        # Display name overrides for cleaner UI
        display_name_overrides = {
            # Multi-company prompts
            "multi_cross_competitor_synthesis": "Cross-Competitor Synthesis",
            "multi_primary_competitors_matrix": "Primary Competitors Matrix",
            # Products & Technology
            "products_and_pipeline": "Products and Development Pipeline",
            "technology_roadmap": "Technology Roadmap and Evolution",
            "patents_and_ip": "Patents and Intellectual Property",
            # People & Organization
            "executive_movements": "Executive Movements and Talent Flow",
            "org_structure_and_hiring": "Org Structure and Hiring Trends",
            # Contracts & Programs
            "contract_awards": "Recent Contract Awards",
            "procurement_opportunities": "Government Procurement Opportunities",
            "program_execution": "Program Execution and Performance",
            # Strategy & Partnerships
            "strategic_direction": "Strategic Direction and Investments",
            "ma_activity": "M&A and Acquisition Activity",
            "teaming_relationships": "Teaming and Partner Relationships",
            "rnd_investments": "R&D and New Product Releases",
        }

        # Define category groupings for single-company prompts
        category_groups = {
            "── MULTI-COMPANY ANALYSIS ──": ["multi_cross_competitor_synthesis", "multi_primary_competitors_matrix"],
            "── PRODUCTS & TECHNOLOGY ──": ["products_and_pipeline", "technology_roadmap", "patents_and_ip"],
            "── PEOPLE & ORGANIZATION ──": ["executive_movements", "org_structure_and_hiring"],
            "── CONTRACTS & PROGRAMS ──": ["contract_awards", "procurement_opportunities", "program_execution"],
            "── STRATEGY & PARTNERSHIPS ──": ["strategic_direction", "ma_activity", "teaming_relationships", "rnd_investments"],
        }

        # Build ordered list with category headers
        ordered_prompts = []
        prompt_lookup = {p["name"]: p for p in prompts}

        for category, prompt_names_in_cat in category_groups.items():
            # Add category header (non-selectable visual separator)
            ordered_prompts.append({
                "name": f"__header__{category}",
                "display": category,
                "is_header": True,
                "is_multi": "MULTI" in category
            })

            # Add prompts in this category
            for pname in prompt_names_in_cat:
                if pname in prompt_lookup:
                    is_multi = pname.startswith("multi_")
                    prefix = "🔀 " if is_multi else "    "
                    ordered_prompts.append({
                        "name": pname,
                        "display": f"{prefix}{display_name_overrides.get(pname, pname.replace('_', ' ').title())}",
                        "is_header": False,
                        "is_multi": is_multi
                    })

        # Find first non-header index for default selection
        default_idx = next((i for i, p in enumerate(ordered_prompts) if not p.get("is_header")), 0)

        # Create selectbox
        selected_prompt_idx = st.selectbox(
            "📝 Select Research Prompt",
            options=range(len(ordered_prompts)),
            index=default_idx,
            format_func=lambda x: ordered_prompts[x]["display"],
            help="Select a research prompt from the categorized list"
        )

        selected_item = ordered_prompts[selected_prompt_idx]

        # If user selected a header, show warning
        if selected_item.get("is_header"):
            st.warning("⚠️ Please select a research prompt, not a category header.")
            selected_prompt = None
            is_cross_competitor = False
            is_primary_competitors = False
        else:
            selected_prompt = selected_item["name"]
            # Check if this is a multi-competitor analysis prompt
            is_cross_competitor = selected_prompt == "multi_cross_competitor_synthesis"
            is_primary_competitors = selected_prompt == "multi_primary_competitors_matrix"

        # Company selection with priority grouping
        companies = st.session_state.engine.get_companies()
        company_names = [c["name"] for c in companies]

        # Define priority companies (first 4 in CSV)
        priority_companies = company_names[:4] if len(company_names) >= 4 else company_names
        other_companies = company_names[4:] if len(company_names) > 4 else []

        # Build grouped options with labels
        company_options = []
        company_labels = {}

        # Add priority companies
        for comp in priority_companies:
            company_options.append(comp)
            company_labels[comp] = f"⭐ {comp}"

        # Add other companies
        for comp in other_companies:
            company_options.append(comp)
            company_labels[comp] = f"   {comp}"

        if is_cross_competitor:
            # Show disabled placeholder for cross-competitor synthesis
            st.selectbox(
                "🏢 Select Company",
                options=["All Competitors (Multi-Company Analysis)"],
                disabled=True,
                help="Cross-competitor synthesis analyzes all competitors - no single company selection needed"
            )
            st.info("📊 This prompt analyzes ALL competitors and synthesizes findings into a unified competitive landscape report.")
            selected_company = "Cross-Competitor-Synthesis"
        elif is_primary_competitors:
            # Show disabled placeholder for primary competitors analysis
            st.selectbox(
                "🏢 Select Company",
                options=["Primary Competitors (BAE, Elbit, Thales, Red 6)"],
                disabled=True,
                help="Primary competitors analysis compares BAE, Elbit, Thales, and Red 6"
            )
            st.info("📊 This prompt compares **BAE Systems**, **Elbit Systems**, **Thales Group**, and **Red 6** across all relevant dimensions including HMD, AR, simulation, and training technologies.")
            selected_company = "Primary-Competitors-Analysis"
        else:
            selected_company = st.selectbox(
                "🏢 Select Company",
                options=company_options,
                format_func=lambda x: company_labels.get(x, x),
                help="⭐ = Priority Companies | Others = Companies of Interest"
            )

        st.markdown("---")

        # Research mode
        st.markdown("### ⚡ Research Mode")
        research_mode = st.radio(
            "Select depth of research:",
            options=["basic", "deep"],
            format_func=lambda x: "Basic (Quick scan)" if x == "basic" else "Deep (Comprehensive analysis)",
            help="Basic is faster and cheaper. Deep uses agentic loops for thorough research."
        )

        st.markdown("---")

        # Provider selection
        st.markdown("### 🤖 AI Providers")

        # Header row for provider selection
        col_name, col_status = st.columns([3, 1])
        with col_name:
            st.caption("Provider")
        with col_status:
            st.caption("API Status")

        available_providers = []
        for provider, status in st.session_state.provider_status.items():
            col_name, col_status = st.columns([3, 1])
            with col_name:
                enabled = st.checkbox(
                    provider.upper(),
                    value=status,
                    disabled=not status,
                    key=f"provider_{provider}"
                )
                if enabled and status:
                    available_providers.append(provider)
            with col_status:
                if status:
                    st.markdown("✓")
                else:
                    st.markdown("✗")

        st.markdown("---")

        # Run synthesis option
        run_synthesis = st.checkbox(
            "🔄 Run Cross-Validation Synthesis",
            value=True,
            help="Synthesize results from multiple providers into one validated report"
        )

        st.markdown("---")

        # Run button
        run_disabled = len(available_providers) == 0 or selected_prompt is None

        if st.button(
            "🚀 Run Research",
            type="primary",
            disabled=run_disabled,
            use_container_width=True
        ):
            return {
                "run": True,
                "company": selected_company,
                "prompt": selected_prompt,
                "mode": research_mode,
                "providers": available_providers,
                "synthesize": run_synthesis
            }

        if run_disabled:
            st.warning("No providers available. Check API keys.")

        # Session cost tracking display
        st.markdown("---")
        st.markdown("### 💰 Session Costs")

        session_total = st.session_state.cost_calculator.get_session_total()
        query_count = len(st.session_state.cost_calculator.session_costs)

        # Display session total with color based on threshold
        if session_total >= 5.00:
            st.error(f"⚠️ Session Total: **${session_total:.4f}**")
            st.warning("Session cost has exceeded $5.00 threshold!")
        elif session_total >= 2.50:
            st.warning(f"Session Total: **${session_total:.4f}**")
        else:
            st.info(f"Session Total: **${session_total:.4f}**")

        st.caption(f"Queries this session: {query_count}")

        # Reset session button
        if query_count > 0:
            if st.button("🔄 Reset Session", use_container_width=True):
                st.session_state.cost_calculator.reset_session()
                st.session_state.last_query_costs = None
                st.rerun()

        return None


def render_dashboard():
    """Render the main dashboard."""
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    # Get stats
    companies = st.session_state.engine.get_companies()
    prompts = st.session_state.engine.get_prompts()
    history = get_report_history()
    active_providers = sum(1 for s in st.session_state.provider_status.values() if s)

    with col1:
        st.metric(
            label="Companies Tracked",
            value=len(companies),
            delta=None
        )

    with col2:
        st.metric(
            label="Research Prompts",
            value=len(prompts),
            delta=None
        )

    with col3:
        st.metric(
            label="Active Providers",
            value=f"{active_providers}/4",
            delta=None
        )

    with col4:
        st.metric(
            label="Reports Generated",
            value=len(history),
            delta=None
        )


def render_research_progress(config: dict):
    """Run research and display progress."""
    st.markdown("## 🔬 Research in Progress")

    progress_container = st.container()

    with progress_container:
        # Show configuration
        st.info(f"""
        **Company:** {config['company']}
        **Prompt:** {config['prompt'].replace('_', ' ').title()}
        **Mode:** {config['mode'].title()}
        **Providers:** {', '.join([p.upper() for p in config['providers']])}
        """)

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Run research
        status_text.text("Initializing research...")
        progress_bar.progress(10)
        time.sleep(0.5)

        status_text.text(f"Running parallel research across {len(config['providers'])} providers...")
        progress_bar.progress(20)

        # Execute research
        try:
            output = st.session_state.engine.run_and_save(
                company=config['company'],
                prompt_name=config['prompt'],
                mode=config['mode'],
                providers=config['providers']
            )

            st.session_state.research_results = output
            progress_bar.progress(60)

            # Calculate and track costs
            status_text.text("Calculating query costs...")
            query_costs = calculate_query_cost(output['results'])
            st.session_state.last_query_costs = query_costs

            # Add individual costs to session tracker
            for provider, result in output['results'].items():
                if result.usage:
                    # Handle both dict (OpenAI, Anthropic, xAI, Perplexity) and object (Google) usage formats
                    if isinstance(result.usage, dict):
                        input_tokens = result.usage.get("input_tokens", 0) or result.usage.get("prompt_tokens", 0) or 0
                        output_tokens = result.usage.get("output_tokens", 0) or result.usage.get("completion_tokens", 0) or 0
                    else:
                        # Google returns usage_metadata as an object with attributes
                        input_tokens = getattr(result.usage, 'prompt_token_count', 0) or getattr(result.usage, 'input_tokens', 0) or 0
                        output_tokens = getattr(result.usage, 'candidates_token_count', 0) or getattr(result.usage, 'output_tokens', 0) or 0
                    estimate = st.session_state.cost_calculator.calculate_cost(
                        provider=provider,
                        model=result.model or "unknown",
                        input_tokens=input_tokens,
                        output_tokens=output_tokens
                    )
                    st.session_state.cost_calculator.add_to_session(estimate)

            progress_bar.progress(70)

            # Run synthesis if requested
            if config['synthesize'] and len(output['results']) > 1:
                status_text.text("Running cross-validation synthesis...")

                synthesis_agent = SynthesisAgent(os.getenv('ANTHROPIC_API_KEY'))
                results_list = list(output['results'].values())

                synthesis_result = synthesis_agent.synthesize(
                    results_list,
                    config['company'],
                    config['prompt']
                )

                # Save synthesis
                synth_path = save_synthesis_report(
                    synthesis_result,
                    config['company'],
                    config['prompt'],
                    output['output_dir']
                )

                st.session_state.synthesis_result = synthesis_result
                output['synthesis_path'] = synth_path

            # Add company and prompt info to output for export buttons
            output['company'] = config['company']
            output['prompt_name'] = config['prompt']

            progress_bar.progress(100)
            status_text.text("Research complete!")

            st.success(f"✅ Research saved to: `{output['output_dir']}`")

            return output

        except Exception as e:
            st.error(f"❌ Research failed: {str(e)}")
            return None


def render_export_buttons(content: str, company: str, prompt_name: str, timestamp: str, prefix: str = ""):
    """Render export download buttons for a report."""
    st.markdown("#### 📥 Export Report")

    col1, col2, col3, col4 = st.columns(4)

    # Get safe filename base
    filename_base = f"{company}_{prompt_name}_{timestamp}".replace(" ", "_")

    with col1:
        # Markdown export
        try:
            md_bytes = export_report(content, 'md', company, prompt_name, timestamp)
            st.download_button(
                label="📝 Markdown",
                data=md_bytes,
                file_name=f"{filename_base}.md",
                mime="text/markdown",
                key=f"{prefix}_md_{timestamp}",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"MD export failed: {e}")

    with col2:
        # HTML export
        try:
            html_bytes = export_report(content, 'html', company, prompt_name, timestamp)
            st.download_button(
                label="🌐 HTML",
                data=html_bytes,
                file_name=f"{filename_base}.html",
                mime="text/html",
                key=f"{prefix}_html_{timestamp}",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"HTML export failed: {e}")

    with col3:
        # DOCX export
        try:
            docx_bytes = export_report(content, 'docx', company, prompt_name, timestamp)
            st.download_button(
                label="📄 Word",
                data=docx_bytes,
                file_name=f"{filename_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"{prefix}_docx_{timestamp}",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"DOCX export failed: {e}")

    with col4:
        # PDF export
        try:
            pdf_bytes = export_report(content, 'pdf', company, prompt_name, timestamp)
            st.download_button(
                label="📕 PDF",
                data=pdf_bytes,
                file_name=f"{filename_base}.pdf",
                mime="application/pdf",
                key=f"{prefix}_pdf_{timestamp}",
                use_container_width=True
            )
        except Exception as e:
            # PDF often fails without system dependencies
            st.download_button(
                label="📕 PDF",
                data=b"",
                file_name=f"{filename_base}.pdf",
                mime="application/pdf",
                key=f"{prefix}_pdf_{timestamp}",
                disabled=True,
                use_container_width=True,
                help="PDF export requires WeasyPrint system dependencies"
            )


def render_results(output: dict):
    """Render research results."""
    st.markdown("## 📋 Research Results")

    # Display query cost summary if available
    if st.session_state.last_query_costs:
        costs = st.session_state.last_query_costs
        with st.expander("💰 Query Cost Breakdown", expanded=True):
            # Cost table
            st.markdown(format_cost_table(costs))

            # Query total
            total_cost = costs['total']['cost']
            st.markdown(f"\n**Query Total: ${total_cost:.4f}**")

            # Check threshold warning
            warning = st.session_state.cost_calculator.check_threshold_warning()
            if warning:
                st.warning(warning)

    # Get company and prompt from output
    company = output.get('company', 'Unknown')
    prompt_name = output.get('prompt_name', 'research')
    timestamp = output.get('timestamp', datetime.utcnow().strftime("%Y-%m-%d_%H%M%S"))

    # Try to extract from first result if not in output
    if company == 'Unknown' and output['results']:
        first_result = list(output['results'].values())[0]
        # Parse from saved files path if available
        if output.get('output_dir'):
            parts = Path(output['output_dir']).parts
            if len(parts) >= 2:
                company = parts[-2]

    # Results tabs
    tab_names = list(output['results'].keys())
    if st.session_state.synthesis_result:
        tab_names.append("SYNTHESIS")

    tabs = st.tabs([name.upper() for name in tab_names])

    for i, tab in enumerate(tabs):
        with tab:
            if i < len(output['results']):
                # Individual provider result
                provider = list(output['results'].keys())[i]
                result = output['results'][provider]

                # Metrics row
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Characters", f"{len(result.text):,}")
                with col2:
                    st.metric("Citations", len(result.citations))
                with col3:
                    st.metric("Model", result.model)

                # Export buttons
                st.markdown("---")
                render_export_buttons(
                    content=result.text,
                    company=company,
                    prompt_name=f"{prompt_name}_{provider}",
                    timestamp=timestamp,
                    prefix=f"provider_{provider}"
                )

                st.markdown("---")

                # Report content
                st.markdown("### Report Content")
                with st.expander("View Full Report", expanded=True):
                    st.markdown(result.text)

                # Citations
                if result.citations:
                    st.markdown("### Sources")
                    with st.expander(f"View {len(result.citations)} Citations"):
                        for j, cite in enumerate(result.citations[:20], 1):
                            title = cite.get('title', 'No title')
                            url = cite.get('url', '#')
                            st.markdown(f"{j}. [{title}]({url})")

            else:
                # Synthesis result
                synth = st.session_state.synthesis_result

                # Metrics row
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Agreement Score", f"{synth.provider_agreement_score:.0%}")
                with col2:
                    st.metric("Key Findings", len(synth.key_findings))
                with col3:
                    st.metric("Discrepancies", len(synth.discrepancies))

                # Export buttons for synthesis
                st.markdown("---")
                render_export_buttons(
                    content=synth.synthesized_report,
                    company=company,
                    prompt_name=f"{prompt_name}_SYNTHESIZED",
                    timestamp=timestamp,
                    prefix="synthesis"
                )

                st.markdown("---")

                # Provider summary
                st.markdown("### Provider Summary")
                for provider, count in synth.source_summary.items():
                    st.markdown(f"- **{provider.upper()}**: {count} citations")

                # Synthesized report
                st.markdown("### Synthesized Report")
                with st.expander("View Full Synthesis", expanded=True):
                    st.markdown(synth.synthesized_report)


def render_history():
    """Render research history."""
    history = get_report_history()

    if not history:
        st.info("No research history yet. Run your first research above!")
        return

    # Filter by company
    all_companies = list(set(h["company"] for h in history))
    selected_company = st.selectbox(
        "Filter by Company",
        options=["All"] + all_companies
    )

    filtered = history if selected_company == "All" else [h for h in history if h["company"] == selected_company]

    # Display history
    for item in filtered[:10]:  # Show last 10
        with st.expander(f"{item['company']} - {item['timestamp']}"):
            st.markdown(f"**Files:** {', '.join(item['files'])}")

            # View reports
            for file in item['files']:
                filepath = Path(item['path']) / file
                if filepath.exists():
                    if st.button(f"View {file}", key=f"view_{item['timestamp']}_{file}"):
                        content = filepath.read_text()
                        st.markdown(content)


def get_prompts_list():
    """Get list of available prompts with their content."""
    prompts_dir = Path(__file__).parent / "prompts"
    prompts = []

    # Display name overrides for cleaner UI
    display_name_overrides = {
        # Multi-company prompts
        "multi_cross_competitor_synthesis": "Cross-Competitor Synthesis",
        "multi_primary_competitors_matrix": "Primary Competitors Matrix",
        # Products & Technology
        "products_and_pipeline": "Products and Development Pipeline",
        "technology_roadmap": "Technology Roadmap and Evolution",
        "patents_and_ip": "Patents and Intellectual Property",
        # People & Organization
        "executive_movements": "Executive Movements and Talent Flow",
        "org_structure_and_hiring": "Org Structure and Hiring Trends",
        # Contracts & Programs
        "contract_awards": "Recent Contract Awards",
        "procurement_opportunities": "Government Procurement Opportunities",
        "program_execution": "Program Execution and Performance",
        # Strategy & Partnerships
        "strategic_direction": "Strategic Direction and Investments",
        "ma_activity": "M&A and Acquisition Activity",
        "teaming_relationships": "Teaming and Partner Relationships",
        "rnd_investments": "R&D and New Product Releases",
    }

    if prompts_dir.exists():
        # Define category groupings
        category_groups = {
            "── MULTI-COMPANY ANALYSIS ──": ["multi_cross_competitor_synthesis", "multi_primary_competitors_matrix"],
            "── PRODUCTS & TECHNOLOGY ──": ["products_and_pipeline", "technology_roadmap", "patents_and_ip"],
            "── PEOPLE & ORGANIZATION ──": ["executive_movements", "org_structure_and_hiring"],
            "── CONTRACTS & PROGRAMS ──": ["contract_awards", "procurement_opportunities", "program_execution"],
            "── STRATEGY & PARTNERSHIPS ──": ["strategic_direction", "ma_activity", "teaming_relationships", "rnd_investments"],
        }

        # Build lookup from actual files
        all_prompts = {p.stem: p for p in prompts_dir.glob("*.md")}

        # Build ordered list with categories
        for category, prompt_names_in_cat in category_groups.items():
            # Add category header
            prompts.append({
                "name": f"__header__{category}",
                "display_name": category,
                "filename": None,
                "path": None,
                "is_header": True,
                "is_multi": "MULTI" in category
            })

            # Add prompts in this category
            for pname in prompt_names_in_cat:
                if pname in all_prompts:
                    prompt_file = all_prompts[pname]
                    is_multi = pname.startswith("multi_")
                    prefix = "🔀 " if is_multi else "    "
                    base_display = display_name_overrides.get(pname, pname.replace("_", " ").title())
                    prompts.append({
                        "name": pname,
                        "display_name": f"{prefix}{base_display}",
                        "filename": prompt_file.name,
                        "path": prompt_file,
                        "is_header": False,
                        "is_multi": is_multi
                    })

    return prompts


def render_prompt_library():
    """Render the prompt library viewer."""
    prompts = get_prompts_list()

    if not prompts:
        st.info("No prompts found. Add .md files to the prompts/ directory.")
        return

    # Find first non-header index for default selection
    default_idx = next((i for i, p in enumerate(prompts) if not p.get("is_header")), 0)

    # Prompt selector
    prompt_options = {p["display_name"]: p for p in prompts}
    selected_display_name = st.selectbox(
        "Select a Prompt to View",
        options=list(prompt_options.keys()),
        index=default_idx,
        key="prompt_library_selector"
    )

    if selected_display_name:
        selected_prompt = prompt_options[selected_display_name]

        # Check if header was selected
        if selected_prompt.get("is_header"):
            st.info("👆 Select a prompt from the list above to view its content.")
            return

        # Show prompt metadata
        st.markdown(f"**Filename:** `{selected_prompt['filename']}`")

        # Read and display prompt content
        try:
            content = selected_prompt["path"].read_text()

            # Display in a code block for better readability
            st.markdown("---")
            st.markdown("### Prompt Content")

            # Use expander for long prompts, direct display for shorter ones
            line_count = content.count('\n') + 1

            if line_count > 30:
                with st.expander("View Full Prompt", expanded=True):
                    st.markdown(content)
            else:
                st.markdown(content)

            # Show some stats
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Lines", line_count)
            with col2:
                st.metric("Characters", len(content))
            with col3:
                word_count = len(content.split())
                st.metric("Words", word_count)

        except Exception as e:
            st.error(f"Error reading prompt: {e}")


def main():
    """Main application entry point."""
    render_header()

    # Sidebar controls
    config = render_sidebar()

    # Main content area
    if config and config.get("run"):
        # Run research
        output = render_research_progress(config)

        if output:
            render_results(output)

    else:
        # Show dashboard
        render_dashboard()

        st.markdown("---")

        # Tabbed section for History and Prompt Library
        tab_history, tab_prompts = st.tabs(["Research History", "Prompt Library"])

        with tab_history:
            render_history()

        with tab_prompts:
            render_prompt_library()


if __name__ == "__main__":
    main()
