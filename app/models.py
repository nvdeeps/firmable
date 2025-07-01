from pydantic import BaseModel
from typing import Optional, List, Dict

class WebsiteRequest(BaseModel):
    url: str
    questions: Optional[List[str]] = None

class ContactInfo(BaseModel):
    email: Optional[str]
    phone: Optional[str]
    social_media: Optional[Dict[str, str]]


class ConversationalRequest(BaseModel):
    query: str
    session_id:str
    conversation_history: Optional[List[Dict[str, str]]]

class ConversationalResponse(BaseModel):
    url: str
    user_query: str
    agent_response: str
    context_sources: List[str]



class CompanyInfo(BaseModel):
    industry: Optional[str]
    company_size: Optional[str]
    location: Optional[str]
    core_products_services: Optional[List[str]]
    unique_selling_proposition: Optional[str]
    target_audience: Optional[str]
    contact_info: Optional[ContactInfo]


class ContactInfo(BaseModel):
    email: Optional[str]
    phone: Optional[str]
    social_media: Optional[Dict[str, str]]


class ExtractedAnswer(BaseModel):
    question: str
    answer: str

class AnalysisResult(BaseModel):
    url: str
    analysis_timestamp: str
    company_info: CompanyInfo
    extracted_answers: Optional[List[ExtractedAnswer]] = []

class AnalysisWithSession(AnalysisResult):
    session_id: str