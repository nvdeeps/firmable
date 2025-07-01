import os
import google.generativeai as genai
from app.models import CompanyInfo,AnalysisResult,ConversationalRequest
from fastapi.exceptions import HTTPException

from datetime import datetime
import json
import re
from dotenv import load_dotenv
from urllib.parse import urlparse


load_dotenv()  # loads from .env file automatically

# Set Gemini API key
genai.configure(api_key=os.getenv("GENAI_APIKEY"))

# Shared model instance
model = genai.GenerativeModel(os.getenv("GENAI_MODEL"))


def extract_json_from_ai_text(ai_text: str) -> dict:
    # Remove ```python or ```json and ``` (if present)
    cleaned = re.sub(r"^```(?:json|python)?\s*|\s*```$", "", ai_text.strip())
    
    # Replace Python None with JSON null for compatibility
    cleaned = cleaned.replace("None", "null")

    # Now load using json
    return json.loads(cleaned)


def extract_json_from_ai_text(ai_text: str) -> dict:
    cleaned = re.sub(r"^```(?:json|python)?\s*|\s*```$", "", ai_text.strip())
    cleaned = cleaned.replace("None", "null")
    return json.loads(cleaned)

def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return all([parsed.scheme in ("http", "https"), parsed.netloc])


async def analyze_content(content: str, url: str, questions: list = None):

    prompt = (
        f"Analyze the following homepage content:\n\n{content}\n\n"
        "Return only a valid Python dictionary (no explanations, no extra text) "
        "matching this structure:\n\n"
    )

    if questions:
        prompt += (
            "{\n"
            "  \"url\": string,\n"
            "  \"analysis_timestamp\": ISO 8601 UTC timestamp,\n"
            "  \"company_info\": {\n"
            "    \"industry\": string or null,\n"
            "    \"company_size\": string or null,\n"
            "    \"location\": string or null,\n"
            "    \"core_products_services\": list of strings,\n"
            "    \"unique_selling_proposition\": string or null,\n"
            "    \"target_audience\": string or null,\n"
            "    \"contact_info\": {\n"
            "      \"email\": string or null,\n"
            "      \"phone\": string or null,\n"
            "      \"social_media\": dictionary of platform name to URL or null\n"
            "    }\n"
            "  },\n"
            "  \"extracted_answers\": [\n"
            "    { \"question\": string, \"answer\": string }, ...\n"
            "  ]\n"
            "}\n"
            "\nOnly include fields listed above. Do not include any explanation or comments."
        )
        prompt += "\n\nQuestions:\n" + "\n".join(questions)
    else:
        prompt += (
            "{\n"
            "  \"industry\": string or null,\n"
            "  \"company_size\": string or null,\n"
            "  \"location\": string or null,\n"
            "  \"core_products_services\": list of strings,\n"
            "  \"unique_selling_proposition\": string or null,\n"
            "  \"target_audience\": string or null,\n"
            "  \"contact_info\": {\n"
            "    \"email\": string or null,\n"
            "    \"phone\": string or null,\n"
            "    \"social_media\": dictionary of platform name to URL or null\n"
            "  }\n"
            "}"
        )

    try:
        response = model.generate_content(prompt)
        ai_text = response.text.strip()
        data = extract_json_from_ai_text(ai_text)
        data["url"] = url  # Enforce correct value

        if questions:
            return AnalysisResult(**data)
        else:
            company_info = CompanyInfo(**data)
            result = AnalysisResult(
                url=url,
                analysis_timestamp=datetime.utcnow().isoformat() + "Z",
                company_info=company_info,
                extracted_answers=[]
            )
            return result
    except Exception as e:
        raise RuntimeError(f"Gemini API failed: {str(e)}")

    

async def followup_response(convrequest, redis):
    session_id = convrequest.session_id

    if not session_id:
        raise HTTPException(status_code=400, detail="Invalid or missing session_id")

    analysis_raw = await redis.get(session_id)
    if not analysis_raw:
        raise HTTPException(status_code=404, detail="No analysis found for session_id")

    try:
        analysis_data = json.loads(analysis_raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Corrupted analysis data in Redis")

    prompt = (
        f"Website Analysis:\n{analysis_data['analysis']}\n\n"
        f"Conversation history: {convrequest.conversation_history or ''}\n"
        f"User: {convrequest.query}\n\n"
        f"Respond to the user query, and also list the specific parts of the analysis you used as 'context_sources'. "
        f"Format the output like this:\n"
        f"Answer: <your answer here>\nContext Sources: <bullet list or comma-separated>\n"
    )

    try:
        response = model.generate_content(prompt)
        full_text = response.text.strip()

        try:
            answer_part, context_part = full_text.split("Context Sources:", 1)
            reply = answer_part.replace("Answer:", "").strip()
            context_sources = [src.strip() for src in context_part.split(",") if src.strip()]
        except ValueError:
            reply = full_text
            context_sources = []

        return reply, context_sources, analysis_data["url"]

    except Exception as e:
        raise RuntimeError(f"Gemini API follow-up failed: {str(e)}")
