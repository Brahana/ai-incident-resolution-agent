

\# AI Incident Resolution Agent



An AI-assisted application support tool that analyzes application logs,

retrieves troubleshooting guidance, and generates incident reports.



\## Features



\- Parses application logs and identifies errors and warnings.

\- Searches a Python troubleshooting knowledge base.

\- Uses Gemini function calling to retrieve relevant guidance.

\- Generates incident summaries, root-cause hypotheses,

&#x20; diagnostic checks, and evidence requirements.

\- Exposes log analysis through a FastAPI REST API.

\- Includes automated API tests using pytest.



\## Architecture



Application Log

&#x20;   -> Python Log Analyzer

&#x20;   -> Troubleshooting Knowledge Base

&#x20;   -> Gemini AI with Function Calling

&#x20;   -> Incident Report

&#x20;   -> FastAPI JSON Response



\## Technology Stack



\- Python

\- Google Gemini API

\- FastAPI

\- Uvicorn

\- Pytest

\- Git



\## Setup



1\. Clone the repository.

2\. Create and activate a virtual environment.

3\. Install dependencies.

4\. Configure your Gemini API key in a local `.env` file.

5\. Start the API.



\### Install dependencies



&#x20;   python -m pip install fastapi uvicorn python-multipart python-dotenv google-genai pytest httpx



\### Configure the API key



Create a `.env` file:



&#x20;   GEMINI\_API\_KEY=your\_api\_key\_here



Never commit your actual API key.



\### Run the API



&#x20;   python -m uvicorn app:app --reload



Open http://127.0.0.1:8000/docs to explore the API.



\### Run tests



&#x20;   python -m pytest -v



\## API Endpoints



| Method | Endpoint | Purpose |

|---|---|---|

| GET | / | API information |

| GET | /health | Health check |

| POST | /analyze | Analyze an uploaded .log or .txt file |



\## Limitations



\- Root causes are hypotheses until supported by operational evidence.

\- AI report generation depends on external model availability.

\- The current project uses sample logs and is not yet production-hardened.



\## Security



Do not upload confidential production logs or credentials to an external

AI service without appropriate authorization and data-handling controls.



