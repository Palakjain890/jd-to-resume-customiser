import os
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
import cli
from config import settings


def test_config_command_displays_settings(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", "openai-key")
    monkeypatch.setattr(settings, "model_name", "gpt-4-turbo-preview")
    monkeypatch.setattr(type(settings), "validate_api_keys", lambda self: True)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["config"])

    assert result.exit_code == 0
    assert "Provider: OpenAI" in result.output
    assert "Model: gpt-4-turbo-preview" in result.output
    assert "Yes" in result.output


def test_tailor_command_success(tmp_path, monkeypatch):
    resume_file = tmp_path / "resume.pdf"
    jd_file = tmp_path / "job_description.pdf"
    resume_file.write_text("resume")
    jd_file.write_text("job desc")

    monkeypatch.setattr(type(settings), "validate_api_keys", lambda self: True)

    agent_mock = MagicMock()
    agent_mock.tailor_resume.return_value = "tailored resume"
    agent_mock.generate_cover_letter.return_value = "cover letter"
    agent_mock.analyze_skill_gaps.return_value = "analysis"
    pdf_result = {
        "resume": str(tmp_path / "resume.pdf"),
        "cover_letter": str(tmp_path / "cover_letter.pdf"),
        "analysis": str(tmp_path / "analysis.pdf"),
    }

    with patch("cli.ResumeTailorAgent", return_value=agent_mock):
        with patch("cli.ResumeParser.extract_text_from_pdf", side_effect=["resume", "job desc"]):
            with patch("cli.PDFGenerator.generate_complete_package", return_value=pdf_result):
                runner = CliRunner()
                result = runner.invoke(
                    cli.cli,
                    ["tailor", "-r", str(resume_file), "-j", str(jd_file), "-o", str(tmp_path)]
                )

    assert result.exit_code == 0
    assert "Success! Generated files:" in result.output
    assert "resume.pdf" in result.output


def test_analyze_command_success(tmp_path, monkeypatch):
    resume_file = tmp_path / "resume.pdf"
    jd_file = tmp_path / "job_description.pdf"
    resume_file.write_text("resume")
    jd_file.write_text("job desc")

    monkeypatch.setattr(type(settings), "validate_api_keys", lambda self: True)

    agent_mock = MagicMock()
    agent_mock.analyze_skill_gaps.return_value = "analysis text"

    with patch("cli.ResumeTailorAgent", return_value=agent_mock):
        with patch("cli.ResumeParser.extract_text_from_pdf", side_effect=["resume", "job desc"]):
            runner = CliRunner()
            result = runner.invoke(
                cli.cli,
                ["analyze", "-r", str(resume_file), "-j", str(jd_file)]
            )

    assert result.exit_code == 0
    assert "Skill Gap Analysis" in result.output


def test_tailor_command_fails_without_api_key(tmp_path, monkeypatch):
    resume_file = tmp_path / "resume.pdf"
    jd_file = tmp_path / "job_description.pdf"
    resume_file.write_text("resume")
    jd_file.write_text("job desc")

    monkeypatch.setattr(type(settings), "validate_api_keys", lambda self: False)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        ["tailor", "-r", str(resume_file), "-j", str(jd_file)]
    )

    assert result.exit_code == 0
    assert "Error: API key not configured!" in result.output
