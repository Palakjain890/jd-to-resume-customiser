"""PDF parsing utilities for resume extraction."""
import pdfplumber
from typing import Dict, Optional


class ResumeParser:
    """Parse resume from PDF format."""

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extract text content from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")

        if not text.strip():
            raise ValueError("No text content found in PDF")

        return text.strip()

    @staticmethod
    def parse_job_description(job_description_path: str) -> str:
        """
        Extract job description from a PDF file.

        Args:
            job_description_path: Path to the job description PDF file

        Returns:
            Extracted job description text
        """
        return ResumeParser.extract_text_from_pdf(job_description_path)

    @staticmethod
    def parse_resume(resume_path: str) -> Dict[str, str]:
        """
        Parse resume and return structured data.

        Args:
            resume_path: Path to the resume PDF file

        Returns:
            Dictionary with resume content
        """
        text = ResumeParser.extract_text_from_pdf(resume_path)
        return {
            "raw_text": text,
            "path": resume_path
        }
