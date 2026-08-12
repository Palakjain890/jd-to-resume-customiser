import os
from pdf_generator import PDFGenerator


def test_clean_text_escapes_html_characters():
    generator = PDFGenerator()
    escaped = generator._clean_text('a & b < c > "d" \'e\'')
    assert escaped == 'a &amp; b &lt; c &gt; &quot;d&quot; &apos;e&apos;'


def test_parse_content_sections_handles_headers_and_paragraphs():
    generator = PDFGenerator()
    content = "# Header\n\n**Bold Section**\nLine one\nLine two\n\nFinal line"
    sections = generator._parse_content_sections(content)

    text_values = [getattr(element, "text", "") for element in sections]
    assert any("Header" in text for text in text_values)
    assert any("Bold Section" in text for text in text_values)
    assert any("Line one Line two" in text for text in text_values)
    assert any("Final line" in text for text in text_values)


def test_generate_resume_pdf_creates_file(tmp_path):
    output_path = tmp_path / "resume.pdf"
    PDFGenerator().generate_resume_pdf("Hello\n\nWorld", str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_generate_cover_letter_pdf_creates_file(tmp_path):
    output_path = tmp_path / "cover_letter.pdf"
    PDFGenerator().generate_cover_letter_pdf("Dear Hiring Manager,\n\nI am writing...", str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_generate_analysis_pdf_creates_file(tmp_path):
    output_path = tmp_path / "analysis.pdf"
    PDFGenerator().generate_analysis_pdf("Analysis\n\nThis candidate...", str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_generate_complete_package_creates_all_files(tmp_path):
    generator = PDFGenerator()
    result = generator.generate_complete_package(
        resume_content="Resume content",
        cover_letter_content="Cover letter content",
        analysis_content="Analysis content",
        output_dir=str(tmp_path),
        base_filename="application"
    )

    assert set(result.keys()) == {"resume", "cover_letter", "analysis"}
    assert all(os.path.exists(path) for path in result.values())
import os
from pdf_generator import PDFGenerator


def test_clean_text_escapes_html_characters():
    generator = PDFGenerator()
    escaped = generator._clean_text('a & b < c > "d" \'e\'')
    assert escaped == 'a &amp; b &lt; c &gt; &quot;d&quot; &apos;e&apos;'


def test_parse_content_sections_handles_headers_and_paragraphs():
    generator = PDFGenerator()
    content = "# Header\n\n**Bold Section**\nLine one\nLine two\n\nFinal line"
    sections = generator._parse_content_sections(content)

    text_values = [getattr(element, "text", "") for element in sections]
    assert any("Header" in text for text in text_values)
    assert any("Bold Section" in text for text in text_values)
    assert any("Line one Line two" in text for text in text_values)
    assert any("Final line" in text for text in text_values)


def test_generate_resume_pdf_creates_file(tmp_path):
    output_path = tmp_path / "resume.pdf"
    PDFGenerator().generate_resume_pdf("Hello\n\nWorld", str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_generate_cover_letter_pdf_creates_file(tmp_path):
    output_path = tmp_path / "cover_letter.pdf"
    PDFGenerator().generate_cover_letter_pdf("Dear Hiring Manager,\n\nI am writing...", str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_generate_analysis_pdf_creates_file(tmp_path):
    output_path = tmp_path / "analysis.pdf"
    PDFGenerator().generate_analysis_pdf("Analysis\n\nThis candidate...", str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_generate_complete_package_creates_all_files(tmp_path):
    generator = PDFGenerator()
    result = generator.generate_complete_package(
        resume_content="Resume content",
        cover_letter_content="Cover letter content",
        analysis_content="Analysis content",
        output_dir=str(tmp_path),
        base_filename="application"
    )

    assert set(result.keys()) == {"resume", "cover_letter", "analysis"}
    assert all(os.path.exists(path) for path in result.values())
    