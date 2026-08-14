# JD To Resume Customiser

> Transform job descriptions into customised resumes using AI. Automatically customise your resume to match any job application with LLMs and LangChain.

---

## Overview

JD To Resume Customiser is an intelligent application that uses Large Language Models (LLMs) to automatically customize your resume based on job descriptions. Upload a job description, and the tool analyzes requirements, identifies key skills and keywords, then generates:

- **Customised Resume** - Restructured and reworded to match the job
- **Skill Gap Analysis** - Identifies missing skills with recommendations


## Features

- **ATS Optimization** - Incorporates relevant keywords for Applicant Tracking Systems
- **Time-Saving** - Generates customised resumes in minutes, not hours
- **Skill Gap Analysis** - Identifies missing skills and provides actionable recommendations
- **Multiple Outputs** - Generates professional PDFs for all outputs
- **User-Friendly Web UI** - Built with Streamlit for easy interaction
- **Secure Configuration** - Environment-based secrets management

---

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Palakjain890/jd-to-resume-customiser.git
   cd jd-to-resume-customiser
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration**
   ```bash
   cp .env.example .env
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The app will open at `http://localhost:8501`

---

## Configuration

### Environment Variables

Configure using `.env` file for local development or `.streamlit/secrets.toml` for Streamlit Cloud:

```env
OPENAI_API_KEY=your-api-key-here
OPENAI_URL=your-url-here
MODEL_NAME=your-model-name-here
MODEL_VERSION=your-model-version-here
```

### In-App Configuration

You don't need a `.env` file to get started. The sidebar lets you enter your own
`OPENAI_API_KEY`, `OPENAI_URL`, `MODEL_NAME`, and `MODEL_VERSION` directly in the app.
Click **Test Configuration** to verify the credentials work before they are used to
generate any documents. Once verified, that configuration is used for the rest of
the session.

See [CONFIGURATION.md](CONFIGURATION.md) for detailed setup instructions.

---

## Usage

### Web Interface (Recommended)

1. **Configure Credentials**
   - Enter your `OPENAI_API_KEY`, `OPENAI_URL`, `MODEL_NAME`, and `MODEL_VERSION` in the sidebar
   - Click "Test Configuration" and confirm the connection succeeds

2. **Upload Files**
   - Upload your resume (PDF)
   - Upload the job description (PDF)

3. **Choose Action**
   - Click "Customise My Resume" for full customization
   - Click "Analyze Skill Gaps Only" for analysis only

4. **Download Results**
   - Download customised resume PDF
   - Download skill gap analysis
---

## Architecture

### Application Flow

```
User Uploads PDFs → PDF Parser → AI Agent → LLM Processing
                                   ↓
                            Resume customising 
                                   ↓
                            Skill Gap Analysis
                                   ↓
                            PDF Generator
                                   ↓
                            Download Outputs
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **LLM Framework** | LangChain |
| **PDF Parsing** | pdfplumber |
| **PDF Generation** | ReportLab |
| **LLM Provider** | OpenAI |

---

## Project Structure

```
jd-to-resume-customiser/
├── app.py                 
├── agent.py             
├── config.py             
├── pdf_parser.py         
├── pdf_generator.py      
├── cli.py                
├── tests/                
│   ├── test_agent.py
│   ├── test_app.py
│   ├── test_config.py
│   ├── test_pdf_*.py
│   └── conftest.py
├── .streamlit/           # Streamlit configuration
│   └── secrets.toml      # Cloud secrets template
├── requirements.txt      # Python dependencies
├── CONFIGURATION.md      # Configuration guide
└── README.md            # This file
```

---

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agent.py -v

# Run with coverage
pytest tests/ --cov
```

All tests pass with proper configuration isolation.

---

## How It Works

1. **PDF Parsing** - Extracts text from uploaded resume and job description
2. **AI Analysis** - LangChain agent analyzes job requirements using GPT-4
3. **Content Generation** - Customises resume, analyzes skills
4. **PDF Creation** - Generates professional PDF outputs
5. **Download** - User downloads all generated documents

---
