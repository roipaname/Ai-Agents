import os, re, time, html
import requests
from bs4 import BeautifulSoup
from readability import Document

TIMEOUT = int(os.getenv("SCRAPE_TIMEOUT", "10"))

def ddg_search(query: str, max_results: int = 5):
    # DuckDuckGo lite HTML
    url = "https://duckduckgo.com/html/"
    r = requests.post(url, data={"q": query}, timeout=TIMEOUT, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for a in soup.select("a.result__a")[:max_results]:
        href = a.get("href")
        title = a.get_text(" ", strip=True)
        results.append({"title": title, "url": href})
    return results

def fetch_readable(url: str) -> str:
    r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent":"Mozilla/5.0"})
    doc = Document(r.text)
    summary_html = doc.summary()
    soup = BeautifulSoup(summary_html, "html.parser")
    text = soup.get_text("\n", strip=True)
    return text
