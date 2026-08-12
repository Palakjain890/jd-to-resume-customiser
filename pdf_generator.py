"""PDF generation utilities for creating tailored resumes and cover letters."""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from datetime import datetime
import os


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

    def _parse_content_sections(self, content: str) -> list:
        """Parse content into sections based on markdown-style headers."""
        lines = content.split('\n')
        elements = []

        current_paragraph = []

        for line in lines:
            line = line.strip()

            # Check for headers (lines starting with # or ** or all caps)
            if line.startswith('#'):
                # Save previous paragraph
                if current_paragraph:
                    text = ' '.join(current_paragraph)
                    elements.append(Paragraph(self._clean_text(text), self.styles['CustomBody']))
                    elements.append(Spacer(1, 0.1 * inch))
                    current_paragraph = []

                # Add header
                header_text = line.lstrip('#').strip()
                elements.append(Paragraph(self._clean_text(header_text), self.styles['CustomHeading']))

            elif line.startswith('**') and line.endswith('**'):
                # Bold section header
                if current_paragraph:
                    text = ' '.join(current_paragraph)
                    elements.append(Paragraph(self._clean_text(text), self.styles['CustomBody']))
                    elements.append(Spacer(1, 0.1 * inch))
                    current_paragraph = []

                header_text = line.strip('*').strip()
                elements.append(Paragraph(f"<b>{self._clean_text(header_text)}</b>", self.styles['CustomBody']))

            elif line == '':
                # Empty line - paragraph break
                if current_paragraph:
                    text = ' '.join(current_paragraph)
                    elements.append(Paragraph(self._clean_text(text), self.styles['CustomBody']))
                    elements.append(Spacer(1, 0.15 * inch))
                    current_paragraph = []

            else:
                # Regular text line
                current_paragraph.append(line)

        # Add final paragraph
        if current_paragraph:
            text = ' '.join(current_paragraph)
            elements.append(Paragraph(self._clean_text(text), self.styles['CustomBody']))

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
