import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse

async def scrape_homepage(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return text

def get_homepage_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, '/', '', '', ''))