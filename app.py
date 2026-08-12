"""Streamlit web interface for JD To Resume Customiser."""
import streamlit as st
import os
import tempfile
from agent import ResumeTailorAgent
from pdf_parser import ResumeParser
from pdf_generator import PDFGenerator
from config import settings

# Page configuration
st.set_page_config(
    page_title="JD To Resume Customiser",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7F8C8D;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📄 JD To Resume Customiser</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Driven Resume Customisation for Every Opportunity</div>', unsafe_allow_html=True)

# Validate configuration on app startup
if not settings.validate_api_keys():
    st.error("""
    ❌ OpenAI API Key not configured!
    
    Please configure your API key in `.streamlit/secrets.toml`:
    ```toml
    openai_api_key = "your-api-key-here"
    openai_url = "https://api.openai.com/v1"
    model_name = "gpt-4-turbo-preview"
    model_version = "2024-04-09"
    ```
    
    Or set environment variables in `.env`:
    ```
    OPENAI_API_KEY=your-api-key-here
    OPENAI_URL=https://api.openai.com/v1
    MODEL_NAME=gpt-4-turbo-preview
    MODEL_VERSION=2024-04-09
    ```
    """)
    st.stop()

# Sidebar for information
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Show loaded configuration (read-only)
    with st.expander("🔒 Loaded Configuration", expanded=False):
        st.write(f"**Model:** {settings.model_name}")
        st.write(f"**Version:** {settings.model_version}")
        st.write(f"**API URL:** {settings.openai_url}")
        st.write("✅ OpenAI API Key configured")

    st.markdown("""
    ### 📚 How to Use
    1. Upload your resume (PDF)
    2. Upload job description (PDF)
    3. Click "Customise My Resume"
    4. Download generated files
    """)

# Main interface
resume_column, job_description_column = st.columns(2)

with resume_column:
    st.subheader("📄 Your Resume")
    resume_file = st.file_uploader("Upload your resume (PDF)", type=['pdf'], key="resume")

    if resume_file:
        st.success(f"Uploaded: {resume_file.name}")

with job_description_column:
    st.subheader("📋 Job Description")
    job_description_file = st.file_uploader("Upload job description (PDF)", type=['pdf'], key="jd")

    if job_description_file:
        st.success(f"Uploaded: {job_description_file.name}")

st.divider()

# Action buttons
analyze_button_column, tailor_button_column, button_spacer_column = st.columns([1, 1, 2])

with analyze_button_column:
    analyze_only = st.button("🔍 Analyze Skill Gaps Only", use_container_width=True)

with tailor_button_column:
    tailor_button = st.button("✨ Customise My Resume", type="primary", use_container_width=True)

# Process files
if (tailor_button or analyze_only) and resume_file and job_description_file:
    if not settings.validate_api_keys():
        st.error("❌ Please configure your API key in the sidebar")
    else:
        try:
            with st.spinner("Processing your files..."):
                # Save uploaded files temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temporary_resume_file:
                    temporary_resume_file.write(resume_file.read())
                    resume_path = temporary_resume_file.name

                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temporary_job_description_file:
                    temporary_job_description_file.write(job_description_file.read())
                    job_description_path = temporary_job_description_file.name

                # Parse documents
                with st.status("Parsing documents...", expanded=True) as status:
                    st.write("📄 Reading resume...")
                    resume_text = ResumeParser.extract_text_from_pdf(resume_path)

                    st.write("📋 Reading job description...")
                    job_description_text = ResumeParser.extract_text_from_pdf(job_description_path)

                    st.write("🤖 Initializing AI agent...")
                    agent = ResumeTailorAgent()

                    if analyze_only:
                        st.write("🔍 Analyzing skill gaps...")
                        skill_gap_analysis = agent.analyze_skill_gaps(resume_text, job_description_text)
                        status.update(label="✅ Analysis complete!", state="complete")

                        # Display analysis
                        st.subheader("📊 Skill Gap Analysis")
                        st.markdown(skill_gap_analysis)

                    else:
                        st.write("✍️ Tailoring resume...")
                        tailored_resume = agent.tailor_resume(resume_text, job_description_text)

                        st.write("✉️ Generating cover letter...")
                        cover_letter = agent.generate_cover_letter(resume_text, job_description_text)

                        st.write("🔍 Analyzing skill gaps...")
                        skill_gap_analysis = agent.analyze_skill_gaps(resume_text, job_description_text)

                        st.write("📄 Creating PDF files...")
                        pdf_gen = PDFGenerator()
                        output_dir = tempfile.mkdtemp()
                        output_files = pdf_gen.generate_complete_package(
                            tailored_resume,
                            cover_letter,
                            skill_gap_analysis,
                            output_dir
                        )

                        status.update(label="✅ Complete!", state="complete")

                        # Display results in tabs
                        tab1, tab2, tab3 = st.tabs(["📄 Tailored Resume", "✉️ Cover Letter", "📊 Skill Gap Analysis"])

                        with tab1:
                            st.markdown(tailored_resume)
                            with open(output_files['resume'], 'rb') as f:
                                st.download_button(
                                    "⬇️ Download Resume PDF",
                                    f.read(),
                                    file_name="tailored_resume.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )

                        with tab2:
                            st.markdown(cover_letter)
                            with open(output_files['cover_letter'], 'rb') as f:
                                st.download_button(
                                    "⬇️ Download Cover Letter PDF",
                                    f.read(),
                                    file_name="cover_letter.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )

                        with tab3:
                            st.markdown(skill_gap_analysis)
                            with open(output_files['analysis'], 'rb') as f:
                                st.download_button(
                                    "⬇️ Download Analysis PDF",
                                    f.read(),
                                    file_name="skill_gap_analysis.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )

                # Cleanup temp files
                os.unlink(resume_path)
                os.unlink(jd_path)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

elif (tailor_button or analyze_only):
    st.warning("⚠️ Please upload both your resume and job description")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #7F8C8D; padding: 1rem;'>
    <p>Built with LangChain • Powered by Groq & OpenAI</p>
</div>
""", unsafe_allow_html=True)
