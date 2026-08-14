"""LangChain agent for resume tailoring."""
from typing import Dict, Optional
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from config import settings


class ResumeTailorAgent:
    """Agent that tailors resumes based on job descriptions."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
    ):
        """
        Initialize the agent with configured LLM.

        Args:
            api_key: Optional OpenAI API key override (falls back to settings).
            base_url: Optional OpenAI API base URL override (falls back to settings).
            model_name: Optional model name override (falls back to settings).
            model_version: Optional model version override (falls back to settings).
        """
        self.api_key = api_key or settings.openai_api_key
        self.base_url = base_url or settings.openai_url
        self.model_name = model_name or settings.model_name
        self.model_version = model_version or settings.model_version
        self.llm = self._get_llm()
        self._setup_chains()

    def _get_llm(self):
        """Get the configured OpenAI LLM."""
        if self.base_url and "azure.com" in self.base_url:
            # Azure OpenAI requires a different client that builds the
            # /openai/deployments/{deployment}/chat/completions?api-version=...
            # URL shape instead of the plain OpenAI /chat/completions path.
            return AzureChatOpenAI(
                azure_endpoint=self.base_url,
                azure_deployment=self.model_name,
                api_version=self.model_version,
                api_key=self.api_key,
                temperature=0.7
            )
        return ChatOpenAI(
            model=self.model_name or "gpt-4-turbo-preview",
            openai_api_key=self.api_key,
            openai_api_base=self.base_url,
            temperature=0.7
        )

    def test_connection(self) -> bool:
        """
        Test that the configured LLM credentials work by making a minimal request.

        Returns:
            True if the connection succeeds.

        Raises:
            ConnectionError: If the request fails.
        """
        try:
            self.llm.invoke("Respond with the single word: OK")
            return True
        except Exception as error:
            raise ConnectionError(f"Failed to connect to OpenAI API: {str(error)}") from error

    def _setup_chains(self):
        """Setup LangChain chains for different tasks."""
        # Resume tailoring chain
        self.resume_template = PromptTemplate(
            input_variables=["resume", "job_description"],
            template="""You are an expert resume writer and career coach. Your task is to tailor the given resume to match the job description.

Original Resume:
{resume}

Job Description:
{job_description}

Instructions:
1. Analyze the job description and identify key requirements, skills, and keywords
2. Restructure and reword the resume to highlight relevant experience and skills
3. Use action verbs and quantifiable achievements where possible
4. Maintain truthfulness - do not add false information
5. Optimize for ATS (Applicant Tracking Systems) by incorporating relevant keywords naturally
6. Keep the same format structure but enhance the content

Provide the tailored resume in a clean, professional format:"""
        )
        self.resume_chain = self.resume_template | self.llm

        # Cover letter chain
        self.cover_letter_template = PromptTemplate(
            input_variables=["resume", "job_description"],
            template="""You are an expert cover letter writer. Create a compelling, personalized cover letter based on the resume and job description.

Resume:
{resume}

Job Description:
{job_description}

Instructions:
1. Write a professional, engaging cover letter (3-4 paragraphs)
2. Address specific requirements from the job description
3. Highlight relevant achievements from the resume
4. Show enthusiasm and cultural fit
5. Keep it concise (250-400 words)
6. Use a professional yet personable tone

Write the cover letter:"""
        )
        self.cover_letter_chain = self.cover_letter_template | self.llm

        # Skill gap analysis chain
        self.skill_gap_template = PromptTemplate(
            input_variables=["resume", "job_description"],
            template="""You are a career development analyst. Analyze the gap between the candidate's resume and the job requirements.

Resume:
{resume}

Job Description:
{job_description}

Provide a detailed skill gap analysis:
1. **Matching Skills**: List skills and qualifications the candidate already has
2. **Missing Skills**: Identify required skills not evident in the resume
3. **Recommendations**: Suggest how to acquire missing skills (courses, certifications, projects)
4. **Match Score**: Provide an overall match score (0-100%)
5. **Interview Preparation**: Key areas to emphasize in interviews

Format your response clearly with the sections above:"""
        )
        self.skill_gap_chain = self.skill_gap_template | self.llm

    def tailor_resume(self, resume_text: str, job_description: str) -> str:
        """
        Tailor resume to match job description.

        Args:
            resume_text: Original resume text
            job_description: Job description text

        Returns:
            Tailored resume text
        """
        result = self.resume_chain.invoke({
            "resume": resume_text,
            "job_description": job_description
        })
        return result.content

    def generate_cover_letter(self, resume_text: str, job_description: str) -> str:
        """
        Generate a cover letter based on resume and job description.

        Args:
            resume_text: Resume text
            job_description: Job description text

        Returns:
            Generated cover letter
        """
        result = self.cover_letter_chain.invoke({
            "resume": resume_text,
            "job_description": job_description
        })
        return result.content

    def analyze_skill_gaps(self, resume_text: str, job_description: str) -> str:
        """
        Analyze skill gaps between resume and job requirements.

        Args:
            resume_text: Resume text
            job_description: Job description text

        Returns:
            Skill gap analysis
        """
        result = self.skill_gap_chain.invoke({
            "resume": resume_text,
            "job_description": job_description
        })
        return result.content

    def process_full_application(
        self, resume_text: str, job_description: str
    ) -> Dict[str, str]:
        """
        Process complete application: tailored resume, cover letter, and skill gap analysis.

        Args:
            resume_text: Original resume text
            job_description: Job description text

        Returns:
            Dictionary with all generated content
        """
        return {
            "tailored_resume": self.tailor_resume(resume_text, job_description),
            "cover_letter": self.generate_cover_letter(resume_text, job_description),
            "skill_gap_analysis": self.analyze_skill_gaps(resume_text, job_description)
        }
