import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://fr.indeed.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GenAI-Jobs/1.0)"
}


def fetch_indeed_jobs(query: str, location: str = "", limit: int = 10):
    jobs = []
    start = 0

    while len(jobs) < limit:
        params = {
            "q": query,
            "l": location,
            "start": start
        }

        r = requests.get(
            f"{BASE_URL}/jobs",
            params=params,
            headers=HEADERS,
            timeout=15
        )
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("a.tapItem")

        if not cards:
            break

        for card in cards:
            if len(jobs) >= limit:
                break

            title_el = card.select_one("h2.jobTitle")
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            href = card.get("href")
            url = urljoin(BASE_URL, href)

            jobs.append({
                "title": title,
                "url": url,
                "source": "Indeed"
            })

        start += 10

    return jobs


if __name__ == "__main__":
    results = fetch_indeed_jobs(
        query="ingénieur chimiste",
        location="Île-de-France",
        limit=10
    )

    for j in results:
        print("—")
        print(j["title"])
        print(j["url"])
