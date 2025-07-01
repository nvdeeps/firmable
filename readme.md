# 🚀 AI Web Insights API

**AI Web Insights API** is an intelligent FastAPI-based service that **scrapes website homepages**, leverages **LLMs (like GPT-4 or Gemini)** to extract key business insights, and supports **conversational Q&A** based on the analysis.

---

## ✨ Features

- ✅ **Homepage Scraping**: Extracts textual content from a company's website.
- ✅ **AI-Powered Analysis**: Uses LLMs (e.g., GPT-4 or Gemini Pro) to structure and interpret website data.
- ✅ **Conversational Follow-ups**: Ask follow-up questions using stored session context.
- ✅ **Secure Access**: Token-based authentication.
- ✅ **Rate Limiting**: Prevents abuse by limiting request frequency.
- ✅ **Async Performance**: Fully async using FastAPI and HTTPX for non-blocking performance.

---

## ⚙️ Technologies Used

| Component       | Technology       |
|----------------|------------------|
| API Framework  | FastAPI          |
| Web Scraping   | BeautifulSoup / Playwright |
| AI Model       | Gemini |
| Cache/Storage  | Redis (Session storage) |
| Auth           | Bearer Token (JWT) |
| Rate Limiting  | Custom dependency |
| Testing        | Pytest + HTTPX    |

---

## 🧠 How It Works

1. You send a `POST /analyze` request with a website URL.
2. The backend:
   - Scrapes the homepage content.
   - Prompts an LLM to extract structured business insights.
   - Stores the results in Redis using a unique `session_id`.
3. You can send a `POST /converse` request with:
   - A `session_id`
   - A new user question
   - An optional conversation history
4. The API will reply using AI-generated answers contextualized to the analyzed website.

---

## ▶️ How to Run Locally

### 🔧 Prerequisites

- Python 3.10+
- Redis (local)
- `.env` file with your Gemini API keys

### 🛠 Installation

```bash
git clone https://github.com/nvdeeps/firmable
pip install -r requirements.txt
```

### 🧪 Start Redis (if not already running)

```bash
sudo systemctl start redis
```

### 🚀 Start the FastAPI App

```bash
uvicorn app.main:app --reload
```

### ✅ Test the API

```bash
PYTHONPATH=. pytest -s
```

---

## 📡 API Endpoints

### 🔍 `POST /analyze`

**Purpose**: Scrape and analyze a website.

#### Request Body
```json
{
  "url": "https://example.com",
  "questions": ["What are their main services?", "Where is the HQ located?"]
}
```

#### Response
```json
{
  "url": "https://example.com",
  "analysis_timestamp": "2025-07-01T12:00:00Z",
  "company_info": { ... },
  "extracted_answers": [ ... ],
  "session_id": "uuid-string"
}
```

---

### 💬 `POST /converse`

**Purpose**: Ask follow-up questions based on earlier analysis.

#### Request Body
```json
{
  "session_id": "uuid-from-analyze",
  "query": "What’s their unique selling point?",
  "conversation_history": [
    {"user": "What are their services?", "agent": "They offer cloud storage and analytics."}
  ]
}
```

#### Response
```json
{
  "url": "https://example.com",
  "user_query": "What’s their unique selling point?",
  "agent_response": "They offer seamless integration between hardware and software.",
  "context_sources": ["homepage", "previous Q&A"]
}
```

---

## 🔐 Authentication

All endpoints require an **Authorization header**:

```http
Authorization: Bearer <your-token>
```

---

## 📂 Project Structure

```bash
app/
├── main.py                # FastAPI app entry point
├── ai.py                  # LLM integration and prompt handling
├── auth.py                # Token verification logic
├── models.py              # Pydantic request/response models
├── scrapper.py            # Homepage scraping utility
├── server.py              # Redis init & rate limiter
tests/                     # Pytest test suite
```

---

