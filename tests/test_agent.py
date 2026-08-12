import pytest
from unittest.mock import MagicMock, patch
import agent
from config import settings


def test_get_llm_openai(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", "openai-key")

    mock_llm = MagicMock()
    monkeypatch.setattr(agent, "ChatOpenAI", MagicMock(return_value=mock_llm))

    resume_agent = agent.ResumeTailorAgent()
    assert resume_agent.llm is mock_llm
    agent.ChatOpenAI.assert_called_once_with(
        model=settings.model_name or "gpt-4-turbo-preview",
        openai_api_key="openai-key",
        temperature=0.7
    )


@patch.object(agent.ResumeTailorAgent, "_setup_chains", lambda self: None)
def test_tailor_resume_returns_chain_output():
    with patch.object(agent.ResumeTailorAgent, "_get_llm", return_value=MagicMock()):
        resume_agent = agent.ResumeTailorAgent()

    resume_agent.resume_chain = MagicMock()
    resume_agent.resume_chain.invoke.return_value.content = "tailored text"

    output = resume_agent.tailor_resume("resume text", "job description")
    assert output == "tailored text"
    resume_agent.resume_chain.invoke.assert_called_once_with(
        {"resume": "resume text", "job_description": "job description"}
    )


@patch.object(agent.ResumeTailorAgent, "_setup_chains", lambda self: None)
def test_generate_cover_letter_returns_chain_output():
    with patch.object(agent.ResumeTailorAgent, "_get_llm", return_value=MagicMock()):
        resume_agent = agent.ResumeTailorAgent()

    resume_agent.cover_letter_chain = MagicMock()
    resume_agent.cover_letter_chain.invoke.return_value.content = "cover letter text"

    output = resume_agent.generate_cover_letter("resume text", "job description")
    assert output == "cover letter text"
    resume_agent.cover_letter_chain.invoke.assert_called_once_with(
        {"resume": "resume text", "job_description": "job description"}
    )


@patch.object(agent.ResumeTailorAgent, "_setup_chains", lambda self: None)
def test_analyze_skill_gaps_returns_chain_output():
    with patch.object(agent.ResumeTailorAgent, "_get_llm", return_value=MagicMock()):
        resume_agent = agent.ResumeTailorAgent()

    resume_agent.skill_gap_chain = MagicMock()
    resume_agent.skill_gap_chain.invoke.return_value.content = "analysis text"

    output = resume_agent.analyze_skill_gaps("resume text", "job description")
    assert output == "analysis text"
    resume_agent.skill_gap_chain.invoke.assert_called_once_with(
        {"resume": "resume text", "job_description": "job description"}
    )


@patch.object(agent.ResumeTailorAgent, "_setup_chains", lambda self: None)
def test_process_full_application_returns_all_outputs():
    with patch.object(agent.ResumeTailorAgent, "_get_llm", return_value=MagicMock()):
        resume_agent = agent.ResumeTailorAgent()

    resume_agent.tailor_resume = MagicMock(return_value="tailored")
    resume_agent.generate_cover_letter = MagicMock(return_value="cover")
    resume_agent.analyze_skill_gaps = MagicMock(return_value="analysis")

    result = resume_agent.process_full_application("resume text", "job description")
    assert result == {
        "tailored_resume": "tailored",
        "cover_letter": "cover",
        "skill_gap_analysis": "analysis"
    }
