import pytest
from unittest.mock import MagicMock, patch
from pdf_parser import ResumeParser


class DummyPage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


def test_extract_text_from_pdf_returns_text():
    pages = [DummyPage("Hello"), DummyPage("World")]
    pdf_mock = MagicMock()
    pdf_mock.pages = pages

    cm = MagicMock()
    cm.__enter__.return_value = pdf_mock
    with patch("pdf_parser.pdfplumber.open", return_value=cm):
        text = ResumeParser.extract_text_from_pdf("dummy.pdf")

    assert text == "Hello\nWorld"


def test_extract_text_from_pdf_raises_when_no_text():
    pages = [DummyPage(None), DummyPage("")]
    pdf_mock = MagicMock()
    pdf_mock.pages = pages

    cm = MagicMock()
    cm.__enter__.return_value = pdf_mock
    with patch("pdf_parser.pdfplumber.open", return_value=cm):
        with pytest.raises(ValueError, match="No text content found in PDF"):
            ResumeParser.extract_text_from_pdf("dummy.pdf")


def test_parse_job_description_delegates_to_extract_text(monkeypatch):
    monkeypatch.setattr(ResumeParser, "extract_text_from_pdf", MagicMock(return_value="JD TEXT"))
    result = ResumeParser.parse_job_description("job_description.pdf")

    assert result == "JD TEXT"
    ResumeParser.extract_text_from_pdf.assert_called_once_with("job_description.pdf")


def test_parse_resume_returns_raw_text_and_path(monkeypatch):
    monkeypatch.setattr(ResumeParser, "extract_text_from_pdf", MagicMock(return_value="RESUME TEXT"))
    result = ResumeParser.parse_resume("resume.pdf")

    assert result == {"raw_text": "RESUME TEXT", "path": "resume.pdf"}
    ResumeParser.extract_text_from_pdf.assert_called_once_with("resume.pdf")
