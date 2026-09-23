import os
from datetime import date

from src.gemini_client import summarize_job


def create_report(df_clean, new_jobs, analysis, client, output_dir="reports"):
    report_date = date.today().isoformat()
    highlight_jobs = new_jobs if len(new_jobs) > 0 else df_clean.head(3)

    lines = []
    lines.append("# 주간 AX 채용 동향")
    lines.append(f"실행일: {report_date}")
    lines.append("")
    lines.append("## 1. 이번 주 요약")
    lines.append(f"- 이번 수집 공고 수: {analysis['total_count']}건")
    lines.append(f"- 신규 공고: {analysis['new_count']}건")
    lines.append(f"- 검색 키워드: {df_clean['search_keyword'].unique().tolist()}")
    lines.append("")
    lines.append("## 2. 주요 동향")
    lines.append("- 회사별 공고 수 Top 5:")
    for company, count in analysis["top_companies"].items():
        lines.append(f"  - {company}: {count}건")
    lines.append("- 지역별 공고 수 Top 5:")
    for loc, count in analysis["top_locations"].items():
        lines.append(f"  - {loc}: {count}건")
    lines.append("")
    lines.append("## 3. 추천 공고")
    for idx, (_, row) in enumerate(highlight_jobs.head(3).iterrows(), start=1):
        lines.append(f"### {idx}) {row['company_name']} / {row['job_title']}")
        lines.append(f"- 경력: {row['career']}")
        lines.append(f"- 지역: {row['location']}")
        lines.append(f"- 등록일/마감일: {row['posted_date']} ~ {row['closing_date']}")
        lines.append(f"- Gemini 요약: {summarize_job(client, row)}")
        lines.append(f"- 공고 링크: {row['job_url']}")
        lines.append("")
    lines.append("## 4. 데이터 기준")
    lines.append(f"- 검색어: {df_clean['search_keyword'].unique().tolist()}")
    lines.append(f"- 수집 시각: {df_clean['collected_at'].iloc[0]}")
    lines.append(f"- 분석 대상 건수: {analysis['total_count']}건")
    lines.append("")
    lines.append("## 5. 주의사항")
    lines.append("- 실제 지원 전 원문 공고를 다시 확인할 것")
    lines.append("- 이 보고서는 학습용 파이프라인 실습 결과이며, Gemini 요약은 참고용임")

    report_text = "\n".join(lines)

    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, f"weekly_report_{report_date}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return report_path, report_text
