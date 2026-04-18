import requests
from bs4 import BeautifulSoup

def get_html(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(url, headers=headers, timeout=10)
        return res.text
    except:
        return ""

def extract_image(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        img = soup.find("img")
        if img:
            return img.get("src") or img.get("data-src") or ""
        return ""
    except:
        return ""
