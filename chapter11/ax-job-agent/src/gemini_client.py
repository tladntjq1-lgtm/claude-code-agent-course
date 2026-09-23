import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

_summary_cache = {}


def get_gemini_client(env_path=".env"):
    load_dotenv(env_path, override=True)
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


def summarize_job(client, row, model="gemini-flash-lite-latest", retries=3, wait_seconds=25):
    if row["job_url"] in _summary_cache:
        return _summary_cache[row["job_url"]]

    prompt = f"""다음 채용공고를 3줄로 요약해줘.

회사명: {row['company_name']}
공고 제목: {row['job_title']}
경력: {row['career']}
지역: {row['location']}
"""
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            _summary_cache[row["job_url"]] = response.text
            return response.text
        except APIError as e:
            if attempt == retries - 1:
                return f"(Gemini 요약 실패: {e.code} {e.status})"
            time.sleep(wait_seconds)
