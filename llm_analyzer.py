
import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

from analyzer import analyze_log
from tools import search_error_guide


# Load the API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from your .env file."
    )

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.5-flash-lite"


# Declare the tool Gemini is allowed to call
search_guide_tool = {
    "name": "search_error_guide",
    "description": (
        "Search the troubleshooting knowledge base "
        "for a specific application error."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "error_message": {
                "type": "STRING",
                "description": "The application error to investigate."
            }
        },
        "required": ["error_message"]
    }
}


def create_incident_report(file_path):
    # Step 1: Analyze the log locally
    log_result = analyze_log(file_path)

    if log_result.get("status") != "success":
        return log_result

    errors = log_result.get("errors", [])

    if errors:
        primary_error = errors[0]
    else:
        primary_error = "Application incident"

    # Step 2: Ask Gemini to investigate the primary error
    prompt = f"""
You are an application support incident analyst.

Analyze these log findings:

{json.dumps(log_result, indent=2)}

Primary error:
{primary_error}

Use the search_error_guide tool to retrieve relevant
troubleshooting guidance before writing the report.

Your report must contain:
1. Incident summary
2. Exact errors found
3. Possible root causes, clearly marked as hypotheses
4. Recommended diagnostic checks
5. Evidence needed to confirm the root cause

Do not invent log entries.
Do not present an unconfirmed hypothesis as a proven cause.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        function_declarations=[search_guide_tool]
                    )
                ],
                temperature=0.2,
            ),
        )

        candidate = response.candidates[0]

        # Step 3: Find the tool calls requested by Gemini
        function_calls = [
            part.function_call
            for part in candidate.content.parts
            if part.function_call
        ]

        # The model may sometimes answer without requesting a tool
        if not function_calls:
            return response.text or "Gemini returned no report."

        print("Tool calls requested by Gemini:")

        function_responses = []

        # Step 4: Execute each supported tool call
        for call in function_calls:
            print(f"  Tool: {call.name}")
            print(f"  Arguments: {call.args}")

            if call.name != "search_error_guide":
                continue

            args = dict(call.args or {})
            error_message = args.get("error_message")

            if not isinstance(error_message, str):
                result = {
                    "error": "Missing or invalid error_message."
                }
            else:
                result = search_error_guide(error_message)

            function_responses.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={"result": result},
                )
            )

        if not function_responses:
            return "No supported troubleshooting tool was executed."

        # Step 5: Send the tool results back to Gemini
        follow_up_contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt)
                ],
            ),
            candidate.content,
            types.Content(
                role="user",
                parts=function_responses,
            ),
        ]

        follow_up = client.models.generate_content(
            model=MODEL_NAME,
            contents=follow_up_contents,
            config=types.GenerateContentConfig(
                temperature=0.2,
            ),
        )

        # Step 6: Return the final incident report
        return follow_up.text or "Gemini returned no final report."

    except Exception as exc:
        error_text = str(exc)

        if "503" in error_text or "UNAVAILABLE" in error_text:
            return (
                "Gemini is temporarily unavailable (503). "
                "Your local log analyzer and knowledge base "
                "can still be tested independently. "
                "Please retry later."
            )

        raise


if __name__ == "__main__":
    report = create_incident_report(
        "sample_logs/batch_failure.log"
    )

    print("\n===== AI INCIDENT REPORT =====\n")
    print(report)
