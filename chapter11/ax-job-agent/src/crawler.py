import json
import re
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0"


def _get_with_retry(url, retries=3, timeout=15, wait_seconds=5, **kwargs):
    last_error = None
    for attempt in range(retries):
        try:
            res = requests.get(url, timeout=timeout, **kwargs)
            res.encoding = "utf-8"
            return res
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(wait_seconds)
    raise last_error


def collect_jobs(keyword, max_items=10):
    url = f"https://www.jobkorea.co.kr/Search/?stext={keyword}&tabType=recruit"
    res = _get_with_retry(url, headers={"User-Agent": USER_AGENT})
    soup = BeautifulSoup(res.text, "html.parser")
    cards = soup.find_all("div", attrs={"data-sentry-component": "CardJob"})

    rows = []
    for card in cards[:max_items]:
        title_a = card.find("a", attrs={"data-sentry-component": "Title"})
        if not title_a:
            continue
        job_title = title_a.get_text(strip=True)
        job_url = title_a.get("href", "").split("?")[0]

        company_name = None
        title_wrapper = title_a.find_parent("div")
        if title_wrapper:
            company_span_wrapper = title_wrapper.find_next_sibling("span")
            if company_span_wrapper:
                company_a = company_span_wrapper.find("a")
                if company_a:
                    company_span = company_a.find("span", class_="truncate")
                    company_name = company_span.get_text(strip=True) if company_span else None

        chips = card.find_all("div", attrs={"data-sentry-component": "GrayChip"})
        location = None
        if chips:
            loc_span = chips[0].find("span", class_="truncate")
            location = loc_span.get_text(strip=True) if loc_span else None

        full_text = card.get_text(" ", strip=True)
        career_match = re.search(r"(경력\s*\d+년\s*↑|경력무관|신입[·/]?경력?|신입)", full_text)
        career = career_match.group(1) if career_match else None

        rows.append({
            "company_name": company_name,
            "job_title": job_title,
            "career": career,
            "location": location,
            "posted_date": None,
            "closing_date": None,
            "job_url": job_url,
            "search_keyword": keyword,
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    return pd.DataFrame(rows)


def get_job_dates(job_url):
    try:
        res = _get_with_retry(job_url, headers={"User-Agent": USER_AGENT}, retries=2)
        soup = BeautifulSoup(res.text, "html.parser")
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                data = json.loads(script.string)
            except (TypeError, json.JSONDecodeError):
                continue
            if isinstance(data, dict) and data.get("@type") == "JobPosting":
                posted = data.get("datePosted")
                closing = data.get("validThrough")
                return (posted[:10] if posted else None, closing[:10] if closing else None)
    except requests.RequestException:
        pass
    return None, None


def enrich_with_dates(df, delay_seconds=0.3):
    posted_list, closing_list = [], []
    for url in df["job_url"]:
        posted, closing = get_job_dates(url)
        posted_list.append(posted)
        closing_list.append(closing)
        time.sleep(delay_seconds)

    df = df.copy()
    df["posted_date"] = posted_list
    df["closing_date"] = closing_list
    return df
