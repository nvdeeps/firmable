import pytest
import os
from httpx import AsyncClient, ASGITransport
from dotenv import load_dotenv
from asgi_lifespan import LifespanManager
from app.main import app

# Load environment variables
load_dotenv()

AUTH_HEADER = {"Authorization": f"Bearer {os.getenv('SECRET_KEY')}"}


@pytest.mark.asyncio
async def test_analyze_unauthorized():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.post("/analyze", json={"url": "https://www.apple.com"})
            assert res.status_code == 401


@pytest.mark.asyncio
async def test_analyze_authorized_minimal():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.post(
                "/analyze",
                json={"url": "https://www.apple.com"},
                headers=AUTH_HEADER
            )
            assert res.status_code in (200, 500)
            if res.status_code == 200:
                data = res.json()
                assert "company_info" in data



@pytest.mark.asyncio
async def test_analyze_and_converse_flow():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # First, analyze the page
            analyze_res = await client.post(
                "/analyze",
                json={"url": "https://www.apple.com"},
                headers=AUTH_HEADER
            )
            assert analyze_res.status_code == 200
            analyze_data = analyze_res.json()
            assert "session_id" in analyze_data
            session_id = analyze_data["session_id"]

            # Then, use session_id in /converse
            converse_payload = {
                "session_id": session_id,
                "query": "Give me their services list?",
                "conversation_history": [
                    {
                        "user": "Can you tell me launches of Apple?",
                        "agent": "Apple is Launching iPod"
                    }
                ]
            }

            converse_res = await client.post(
                "/converse",
                json=converse_payload,
                headers=AUTH_HEADER
            )
            assert converse_res.status_code in (200, 500)
            if converse_res.status_code == 200:
                data = converse_res.json()
                assert "agent_response" in data
                assert isinstance(data["agent_response"], str)
