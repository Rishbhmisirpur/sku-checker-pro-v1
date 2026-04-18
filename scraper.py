import requests
import random

session = requests.Session()

def get_html(url):
    try:
        headers_list = [
            {"User-Agent": "Mozilla/5.0"},
            {"User-Agent": "Chrome/124"},
            {"User-Agent": "Safari/537"}
        ]

        for _ in range(3):
            headers = random.choice(headers_list)
            r = session.get(url, headers=headers, timeout=25)

            if r.status_code == 200 and len(r.text) > 200:
                return r.text

        return ""

    except:
        return ""
