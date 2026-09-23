from datetime import datetime

from src.crawler import collect_jobs, enrich_with_dates
from src.preprocess import clean_jobs, find_new_jobs
from src.analyzer import analyze_jobs
from src.gemini_client import get_gemini_client
from src.reporter import create_report
from src.notifier import send_slack, send_email

SEARCH_KEYWORD = "ax"
MAX_ITEMS = 10


def main():
    start_time = datetime.now()
    print(f"[{start_time}] AX Job Agent 실행 시작 (키워드: {SEARCH_KEYWORD})")

    jobs = collect_jobs(SEARCH_KEYWORD, max_items=MAX_ITEMS)
    print(f"수집 건수: {len(jobs)}")

    jobs = enrich_with_dates(jobs)
    clean = clean_jobs(jobs)
    new_jobs = find_new_jobs(clean)
    print(f"신규 공고 수: {len(new_jobs)}")

    analysis = analyze_jobs(clean, new_jobs)

    client = get_gemini_client()
    report_path, report_text = create_report(clean, new_jobs, analysis, client)
    print(f"보고서 생성: {report_path}")

    slack_ok = send_slack(report_text)
    print(f"Slack 발송 성공 여부: {slack_ok}")

    email_ok = send_email(f"주간 AX 채용 동향 ({start_time.date()})", report_text)
    print(f"Gmail 발송 성공 여부: {email_ok}")

    end_time = datetime.now()
    print(f"[{end_time}] AX Job Agent 실행 종료 (소요 시간: {end_time - start_time})")


if __name__ == "__main__":
    main()
