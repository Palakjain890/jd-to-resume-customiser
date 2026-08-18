"""PDF generation utilities for creating tailored resumes and cover letters."""
import re
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from datetime import datetime
import os

# Matches list item markers at the start of a line: "- ", "* ", "• ", "1. ", "1) "
BULLET_PATTERN = re.compile(r'^(?:[-*\u2022]|\d+[.)])\s+')

# Common resume section titles - rendered as headings even without markdown
# markup, since the input resume (and LLM output) often uses plain section
# names like "Experience" or "EXPERIENCE" rather than "# Experience".
SECTION_HEADERS = {
    'experience', 'work experience', 'professional experience',
    'projects', 'personal projects',
    'education',
    'skills', 'technical skills', 'core skills',
    'summary', 'professional summary', 'objective',
    'certifications', 'achievements', 'awards',
    'contact', 'profile', 'about', 'about me',
    'publications', 'leadership', 'activities', 'interests',
}


def _looks_like_section_header(line: str) -> bool:
    """Return True if the line is a standalone resume section title."""
    candidate = line.rstrip(':').strip().lower()
    return candidate in SECTION_HEADERS


class PDFGenerator:
    """Generate professional PDF documents."""

    def __init__(self, page_size=letter):
        """Initialize PDF generator with page size."""
        self.page_size = page_size
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor='#2C3E50',
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor='#34495E',
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor='#2C3E50',
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14
        ))

        # Bullet/list item style
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['CustomBody'],
            leftIndent=0.2 * inch,
            bulletIndent=0,
            spaceAfter=4
        ))

    def _clean_text(self, text: str) -> str:
        """Clean text for PDF generation, handling special characters."""
        # Replace problematic characters
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def _convert_inline_markdown(self, text: str) -> str:
        """Convert simple markdown emphasis (bold/italic) to ReportLab markup.

        Must be called on already-HTML-escaped text so the inserted
        <b>/<i> tags survive and aren't re-escaped.
        """
        # Bold: **text** or __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        # Italic: *text* or _text_ (single markers, not already consumed above)
        text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', text)
        text = re.sub(r'(?<!_)_([^_]+)_(?!_)', r'<i>\1</i>', text)
        return text

    def _format_text(self, text: str) -> str:
        """Escape HTML-sensitive characters and render markdown emphasis."""
        return self._convert_inline_markdown(self._clean_text(text))

    def _parse_content_sections(self, content: str) -> list:
        """Parse content into sections based on markdown-style headers."""
        lines = content.split('\n')
        elements = []

        current_paragraph = []
        current_is_bullet = False

        def flush():
            if not current_paragraph:
                return
            text = ' '.join(current_paragraph)
            if current_is_bullet:
                text = f"\u2022 {self._format_text(text)}"
                elements.append(Paragraph(text, self.styles['CustomBullet']))
            else:
                elements.append(Paragraph(self._format_text(text), self.styles['CustomBody']))

        for line in lines:
            line = line.strip()

            # Check for headers (lines starting with # or ** or all caps)
            if line.startswith('#'):
                # Save previous paragraph
                had_content = bool(current_paragraph)
                flush()
                if had_content:
                    elements.append(Spacer(1, 0.1 * inch))
                current_paragraph = []
                current_is_bullet = False

                # Add header
                header_text = line.lstrip('#').strip()
                elements.append(Paragraph(self._format_text(header_text), self.styles['CustomHeading']))

            elif line.startswith('**') and line.endswith('**') and len(line) > 4:
                # Bold section header
                had_content = bool(current_paragraph)
                flush()
                if had_content:
                    elements.append(Spacer(1, 0.1 * inch))
                current_paragraph = []
                current_is_bullet = False

                header_text = line.strip('*').strip()
                elements.append(Paragraph(f"<b>{self._clean_text(header_text)}</b>", self.styles['CustomBody']))

            elif _looks_like_section_header(line):
                # Plain section title (e.g. "Experience", "PROJECTS") with no markdown
                had_content = bool(current_paragraph)
                flush()
                if had_content:
                    elements.append(Spacer(1, 0.1 * inch))
                current_paragraph = []
                current_is_bullet = False

                elements.append(Paragraph(self._format_text(line.rstrip(':')), self.styles['CustomHeading']))

            elif line == '':
                # Empty line - paragraph break
                flush()
                if current_paragraph:
                    elements.append(Spacer(1, 0.15 * inch))
                current_paragraph = []
                current_is_bullet = False

            elif BULLET_PATTERN.match(line):
                # Start of a new list item - flush whatever came before it
                flush()
                current_paragraph = [BULLET_PATTERN.sub('', line, count=1)]
                current_is_bullet = True

            else:
                # Regular text line (continuation of paragraph or current bullet)
                current_paragraph.append(line)

        # Add final paragraph
        flush()

        return elements

    def generate_resume_pdf(self, content: str, output_path: str, title: str = "Tailored Resume"):
        """
        Generate a PDF resume from text content.

        Args:
            content: Resume content text
            output_path: Path where PDF should be saved
            title: Document title
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=self.page_size,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        story = []

        # Add title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2 * inch))

        # Parse and add content
        elements = self._parse_content_sections(content)
        story.extend(elements)

        # Build PDF
        doc.build(story)

    def generate_cover_letter_pdf(self, content: str, output_path: str):
        """
        Generate a PDF cover letter.

        Args:
            content: Cover letter content
            output_path: Path where PDF should be saved
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=self.page_size,
            rightMargin=1 * inch,
            leftMargin=1 * inch,
            topMargin=1 * inch,
            bottomMargin=1 * inch
        )

        story = []

        # Add date
        date_str = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(date_str, self.styles['CustomBody']))
        story.append(Spacer(1, 0.3 * inch))

        # Parse and add content
        elements = self._parse_content_sections(content)
        story.extend(elements)

        # Add closing
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("Sincerely,", self.styles['CustomBody']))

        # Build PDF
        doc.build(story)

    def generate_analysis_pdf(self, content: str, output_path: str):
        """
        Generate a PDF skill gap analysis report.

        Args:
            content: Analysis content
            output_path: Path where PDF should be saved
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=self.page_size,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        story = []

        # Add title
        story.append(Paragraph("Skill Gap Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2 * inch))

        # Parse and add content
        elements = self._parse_content_sections(content)
        story.extend(elements)

        # Build PDF
        doc.build(story)

    def generate_complete_package(
        self,
        resume_content: str,
        cover_letter_content: str,
        analysis_content: str,
        output_dir: str,
        base_filename: str = "application"
    ):
        """
        Generate all three PDFs for a complete application package.

        Args:
            resume_content: Tailored resume content
            cover_letter_content: Cover letter content
            analysis_content: Skill gap analysis content
            output_dir: Directory to save PDFs
            base_filename: Base name for output files

        Returns:
            Dictionary with paths to generated files
        """
        os.makedirs(output_dir, exist_ok=True)

        resume_path = os.path.join(output_dir, f"{base_filename}_resume.pdf")
        cover_letter_path = os.path.join(output_dir, f"{base_filename}_cover_letter.pdf")
        analysis_path = os.path.join(output_dir, f"{base_filename}_analysis.pdf")

        self.generate_resume_pdf(resume_content, resume_path)
        self.generate_cover_letter_pdf(cover_letter_content, cover_letter_path)
        self.generate_analysis_pdf(analysis_content, analysis_path)

        return {
            "resume": resume_path,
            "cover_letter": cover_letter_path,
            "analysis": analysis_path
        }