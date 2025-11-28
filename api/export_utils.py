"""
Export Utilities - Convert research reports to various formats.
Supports: PDF, DOCX, Markdown, HTML
"""
import os
import io
import markdown
from pathlib import Path
from datetime import datetime
from typing import Optional

# DOCX support
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE


class ReportExporter:
    """Export research reports to various formats."""

    # Professional styling for exports
    BRAND_COLOR = "#1e3a5f"  # Red 6 navy blue
    ACCENT_COLOR = "#3b82f6"  # Accent blue

    def __init__(self):
        self.css_template = self._get_css_template()

    def _get_css_template(self) -> str:
        """CSS template for HTML/PDF exports."""
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                line-height: 1.6;
                color: #1f2937;
                max-width: 900px;
                margin: 0 auto;
                padding: 40px;
                background: #ffffff;
            }

            .report-header {
                background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
                color: white;
                padding: 30px 40px;
                margin: -40px -40px 40px -40px;
                border-radius: 0 0 10px 10px;
            }

            .report-header h1 {
                margin: 0 0 10px 0;
                font-size: 28px;
                font-weight: 700;
            }

            .report-header .meta {
                opacity: 0.9;
                font-size: 14px;
            }

            .report-header .meta span {
                margin-right: 20px;
            }

            .confidential-banner {
                background: #fef3c7;
                border: 1px solid #f59e0b;
                color: #92400e;
                padding: 10px 20px;
                border-radius: 6px;
                text-align: center;
                font-weight: 600;
                margin-bottom: 30px;
            }

            h1 { font-size: 24px; font-weight: 700; color: #1e3a5f; margin-top: 40px; }
            h2 { font-size: 20px; font-weight: 600; color: #1e3a5f; margin-top: 30px; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }
            h3 { font-size: 16px; font-weight: 600; color: #374151; margin-top: 25px; }

            p { margin: 15px 0; }

            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 14px;
            }

            th {
                background: #f3f4f6;
                color: #1e3a5f;
                font-weight: 600;
                text-align: left;
                padding: 12px 15px;
                border: 1px solid #e5e7eb;
            }

            td {
                padding: 12px 15px;
                border: 1px solid #e5e7eb;
                vertical-align: top;
            }

            tr:nth-child(even) {
                background: #f9fafb;
            }

            ul, ol {
                margin: 15px 0;
                padding-left: 25px;
            }

            li {
                margin: 8px 0;
            }

            blockquote {
                border-left: 4px solid #3b82f6;
                padding-left: 20px;
                margin: 20px 0;
                color: #4b5563;
                font-style: italic;
            }

            code {
                background: #f3f4f6;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 13px;
            }

            .highlight-box {
                background: #eff6ff;
                border: 1px solid #3b82f6;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }

            .warning-box {
                background: #fef3c7;
                border: 1px solid #f59e0b;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }

            .footer {
                margin-top: 50px;
                padding-top: 20px;
                border-top: 2px solid #e5e7eb;
                text-align: center;
                color: #6b7280;
                font-size: 12px;
            }

            @media print {
                body { padding: 20px; }
                .report-header { margin: -20px -20px 30px -20px; }
            }
        </style>
        """

    def markdown_to_html(
        self,
        md_content: str,
        title: str,
        company: str,
        prompt_name: str,
        timestamp: str
    ) -> str:
        """Convert markdown to styled HTML."""

        # Convert markdown to HTML
        html_body = markdown.markdown(
            md_content,
            extensions=['tables', 'fenced_code', 'toc']
        )

        # Format display values
        prompt_display = prompt_name.replace("_", " ").title()
        timestamp_display = timestamp.replace("_", " ").replace("-", "/", 2).replace("/", "-", 2)

        # Build full HTML document
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            {self.css_template}
        </head>
        <body>
            <div class="report-header">
                <h1>{title}</h1>
                <div class="meta">
                    <span><strong>Company:</strong> {company}</span>
                    <span><strong>Research:</strong> {prompt_display}</span>
                    <span><strong>Generated:</strong> {timestamp_display}</span>
                </div>
            </div>

            <div class="confidential-banner">
                CONFIDENTIAL - RED 6 COMPETITIVE INTELLIGENCE - DO NOT DISTRIBUTE
            </div>

            {html_body}

            <div class="footer">
                <p>Red 6 Competitive Intelligence Platform</p>
                <p>Generated {timestamp_display} | Confidential and Proprietary</p>
            </div>
        </body>
        </html>
        """

        return html

    def export_to_markdown(
        self,
        content: str,
        company: str,
        prompt_name: str,
        timestamp: str,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Export report as markdown file.

        Returns bytes if no output_path, otherwise saves to file.
        """
        # Add header
        prompt_display = prompt_name.replace("_", " ").title()

        header = f"""---
title: "{company} - {prompt_display}"
date: "{timestamp}"
classification: "CONFIDENTIAL"
---

# Red 6 Competitive Intelligence Report

**Company:** {company}
**Research:** {prompt_display}
**Generated:** {timestamp}

---

**CONFIDENTIAL - DO NOT DISTRIBUTE**

---

"""
        full_content = header + content

        if output_path:
            Path(output_path).write_text(full_content)
            return full_content.encode('utf-8')

        return full_content.encode('utf-8')

    def export_to_html(
        self,
        content: str,
        company: str,
        prompt_name: str,
        timestamp: str,
        output_path: Optional[str] = None
    ) -> bytes:
        """Export report as HTML file."""

        title = f"{company} - {prompt_name.replace('_', ' ').title()}"
        html = self.markdown_to_html(content, title, company, prompt_name, timestamp)

        if output_path:
            Path(output_path).write_text(html)
            return html.encode('utf-8')

        return html.encode('utf-8')

    def export_to_pdf(
        self,
        content: str,
        company: str,
        prompt_name: str,
        timestamp: str,
        output_path: Optional[str] = None
    ) -> bytes:
        """Export report as PDF file."""

        # First convert to HTML
        title = f"{company} - {prompt_name.replace('_', ' ').title()}"
        html = self.markdown_to_html(content, title, company, prompt_name, timestamp)

        try:
            from weasyprint import HTML, CSS

            # Generate PDF
            pdf_bytes = HTML(string=html).write_pdf()

            if output_path:
                Path(output_path).write_bytes(pdf_bytes)

            return pdf_bytes

        except Exception as e:
            # Fallback: return HTML with PDF instructions
            fallback_msg = f"PDF generation failed: {str(e)}. Please use HTML export and print to PDF."
            raise RuntimeError(fallback_msg)

    def export_to_docx(
        self,
        content: str,
        company: str,
        prompt_name: str,
        timestamp: str,
        output_path: Optional[str] = None
    ) -> bytes:
        """Export report as Word document."""

        doc = Document()

        # Set up styles
        style = doc.styles['Normal']
        style.font.name = 'Calibri'
        style.font.size = Pt(11)

        # Title
        title = doc.add_heading(f'{company}', level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Subtitle
        prompt_display = prompt_name.replace("_", " ").title()
        subtitle = doc.add_paragraph(prompt_display)
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Metadata
        doc.add_paragraph()
        meta = doc.add_paragraph()
        meta.add_run("CONFIDENTIAL - RED 6 COMPETITIVE INTELLIGENCE").bold = True
        meta.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph(f"Generated: {timestamp}")
        doc.add_paragraph()

        # Add horizontal line
        doc.add_paragraph("─" * 60)

        # Parse markdown content and add to document
        lines = content.split('\n')
        current_list = None

        for line in lines:
            line = line.strip()

            if not line:
                doc.add_paragraph()
                current_list = None
                continue

            # Headers
            if line.startswith('# '):
                doc.add_heading(line[2:], level=1)
            elif line.startswith('## '):
                doc.add_heading(line[3:], level=2)
            elif line.startswith('### '):
                doc.add_heading(line[4:], level=3)
            elif line.startswith('#### '):
                doc.add_heading(line[5:], level=4)

            # List items
            elif line.startswith('- ') or line.startswith('* '):
                doc.add_paragraph(line[2:], style='List Bullet')

            elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
                doc.add_paragraph(line[3:], style='List Number')

            # Tables (simplified - just add as text)
            elif line.startswith('|'):
                # Skip table separators
                if '---' in line:
                    continue
                # Clean up table row
                cells = [c.strip() for c in line.split('|')[1:-1]]
                doc.add_paragraph(' | '.join(cells))

            # Regular paragraph
            else:
                # Handle bold/italic
                para = doc.add_paragraph()
                self._add_formatted_text(para, line)

        # Footer
        doc.add_paragraph()
        doc.add_paragraph("─" * 60)
        footer = doc.add_paragraph()
        footer.add_run("Red 6 Competitive Intelligence Platform").italic = True
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Save to bytes
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        docx_bytes = buffer.read()

        if output_path:
            Path(output_path).write_bytes(docx_bytes)

        return docx_bytes

    def _add_formatted_text(self, paragraph, text: str):
        """Add text with basic markdown formatting (bold, italic)."""
        import re

        # Simple pattern matching for bold and italic
        # This is a simplified implementation
        parts = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', text)

        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                # Bold
                run = paragraph.add_run(part[2:-2])
                run.bold = True
            elif part.startswith('*') and part.endswith('*'):
                # Italic
                run = paragraph.add_run(part[1:-1])
                run.italic = True
            else:
                paragraph.add_run(part)

    def export(
        self,
        content: str,
        format: str,
        company: str,
        prompt_name: str,
        timestamp: str,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Export report to specified format.

        Args:
            content: Markdown content
            format: 'pdf', 'docx', 'md', 'html'
            company: Company name
            prompt_name: Research prompt name
            timestamp: Timestamp string
            output_path: Optional path to save file

        Returns:
            Bytes of the exported file
        """
        format = format.lower()

        if format == 'pdf':
            return self.export_to_pdf(content, company, prompt_name, timestamp, output_path)
        elif format == 'docx':
            return self.export_to_docx(content, company, prompt_name, timestamp, output_path)
        elif format == 'md' or format == 'markdown':
            return self.export_to_markdown(content, company, prompt_name, timestamp, output_path)
        elif format == 'html':
            return self.export_to_html(content, company, prompt_name, timestamp, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'pdf', 'docx', 'md', or 'html'.")


# Convenience function
def export_report(
    content: str,
    format: str,
    company: str,
    prompt_name: str,
    timestamp: str = None
) -> bytes:
    """
    Quick export function.

    Args:
        content: Markdown content
        format: 'pdf', 'docx', 'md', 'html'
        company: Company name
        prompt_name: Research prompt name
        timestamp: Optional timestamp (defaults to now)

    Returns:
        Bytes of the exported file
    """
    if timestamp is None:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")

    exporter = ReportExporter()
    return exporter.export(content, format, company, prompt_name, timestamp)
