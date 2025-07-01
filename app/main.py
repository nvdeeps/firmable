from fastapi import FastAPI, Request, Depends,HTTPException
from app.auth import verify_token
from app.server import init_redis,rate_limiter
from app.models import WebsiteRequest, AnalysisWithSession, CompanyInfo, ConversationalRequest, ConversationalResponse
from app.scrapper import scrape_homepage
from app.ai import analyze_content, followup_response,is_valid_url
from datetime import datetime
import uuid, json

app = FastAPI(title="AI Web Insights API")

@app.on_event("startup")
async def startup():
    print("Booting!")
    await init_redis(app)

@app.post("/analyze", response_model=AnalysisWithSession, tags=["Website Analysis"])
async def analyze_website(
    request: WebsiteRequest,
    fastapi_request: Request,
    _: None = Depends(verify_token),
    __: None = Depends(rate_limiter)
):
    try:
        # Validate URL from request
        if not is_valid_url(request.url):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        # Scrape and analyze
        content = await scrape_homepage(request.url)
        result = await analyze_content(content, request.url, request.questions)

        # Save session in Redis
        session_id = str(uuid.uuid4())
        redis = fastapi_request.app.state.redis

        await redis.set(session_id, json.dumps({
            "url": request.url,
            "analysis": result.model_dump()
        }))

        # Return result with session ID
        return {**result.model_dump(), "session_id": session_id}

    except Exception as e:
        print(f"Error: {e}")
        # Fallback dummy response
        dummy_result = AnalysisWithSession(
            url=request.url,
            analysis_timestamp=str(datetime.utcnow().isoformat()) + "Z",
            company_info=CompanyInfo(),
            extracted_answers=[],
            session_id="error-session"
        )
        return dummy_result


@app.post("/converse", response_model=ConversationalResponse, tags=["Conversational QA"])
async def converse(
    conv_request: ConversationalRequest,
    fastapi_request: Request,
   _: None = Depends(verify_token) ,
       __: None = Depends(rate_limiter)       # Rate limiter
):
    redis = fastapi_request.app.state.redis
    agent_response, sources, url = await followup_response(conv_request, redis)
    return ConversationalResponse(
        url=url,
        user_query=conv_request.query,
        agent_response=agent_response,
        context_sources=sources
    )
