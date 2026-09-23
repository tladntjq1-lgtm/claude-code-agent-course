# AX Job Agent — 프로젝트 사양서

> 잡코리아의 AX/AI/데이터 관련 채용공고를 주기적으로 수집·분석·요약해서
> Slack/Gmail로 주간 보고서를 보내는 자동화 파이프라인.
> Chapter 11 실습 (Claude Web = Orchestrator, Claude Code = Coding Agent).

---

## 1. 목표

1. AX / AI / 데이터 관련 채용공고를 잡코리아에서 수집한다.
2. 필요한 컬럼만 정리한다.
3. 중복 공고와 기존 공고를 구분한다.
4. 신규 공고의 기본 통계를 계산한다.
5. 관련성이 높은 공고를 추린다.
6. Gemini API로 주요 내용을 요약한다.
7. 주간 Markdown 보고서를 만든다.
8. Slack과 Gmail로 결과를 전송한다.
9. GitHub Actions가 주 1회 자동 실행한다.

이 프로젝트의 핵심은 크롤링 기술이 아니라
**수집 → 정제 → 분석 → AI 해석 → 검증 → 보고 → 자동화**가
하나의 파이프라인으로 연결되는 과정을 경험하는 것이다.

---

## 2. 검색 키워드 (초기안)

`AX`, `AI`, `인공지능`, `데이터 분석`, `생성형 AI`, `LLM`,
`Machine Learning`, `Data Scientist`, `AI Engineer`

---

## 3. 협업 구조 (역할 분리)

| 역할 | 담당 | 하는 일 |
|---|---|---|
| Orchestrator | Claude Web (GPT/Gemini/Claude 웹 중 택1) | 전체 계획, STEP 분리, Claude Code용 프롬프트 작성, 결과 보고 후 다음 단계 결정 |
| Coding Agent | Claude Code (로컬, 토큰 소진 시 세션 교체 가능) | 실제 파일 읽기/쓰기, 코드 작성, 명령 실행, 오류 수정 |
| Human (사용자) | 본인 (Python/데이터분석 초보) | 실행 결과 확인, 데이터/해석 검증, 다음 단계 승인 |

개발 도구: **VS Code + Jupyter Notebook** (셀 단위 실행/검증 중심)

---

## 4. 원칙 (반드시 지킬 것)

1. 한 번에 전체 프로그램을 만들지 않는다. 현재 STEP 하나만 진행한다.
2. 코드가 생성되면 반드시 직접 실행하고 눈으로 결과를 확인한다.
3. 결과를 Markdown Cell에 해석/기록한다 (성공 여부, 다음 단계 진행 가능 여부).
4. 이상하면 다음 단계로 넘어가지 않는다.
5. **계산 가능한 사실은 pandas로 계산**하고, **Gemini는 요약·해석 전용**으로 쓴다.
   - 예: "이번 주 신규 공고 몇 건?" → pandas가 계산 (Gemini에게 시키지 않음)
   - 예: "이 공고의 핵심 요구 기술은?" → Gemini가 답변
6. API Key, 비밀번호는 절대 코드/Git에 올리지 않는다 (`.env` + `.gitignore` + GitHub Secrets).
7. 로컬에서 `python main.py`가 완전히 성공한 뒤에만 GitHub Actions를 추가한다.
8. 크롤링은 요청 전 robots.txt/이용약관을 확인하고, 소량(1검색어·1페이지)부터 검증 후 확장한다.
   자동 수집이 어려우면 저장된 샘플 HTML/CSV로 이후 파이프라인을 계속 진행한다.
   → **실제 적용 사례(STEP 03/04/04-1에서 검증)**: 잡코리아 검색 페이지는 겉보기엔 Next.js 기반
     SPA이지만, 실제로는 공고 목록이 원본 HTML(`data-sentry-component="CardJob"`)에
     서버 렌더링되어 있어 `requests + BeautifulSoup`로 회사명/제목/경력/지역/URL을
     정상 추출 가능함을 확인함. 등록일/마감일은 **목록 페이지에는 없지만, 각 공고의
     상세 페이지(`GI_Read/{id}`)에 있는 JSON-LD 구조화 데이터(`application/ld+json`,
     schema.org `JobPosting`)의 `datePosted`/`validThrough` 필드에서 정상적으로
     가져올 수 있음을 확인**함 (공고당 추가 요청 1회 필요). (참고용 가상 샘플 데이터는
     `data/raw/sample_jobs.csv`에 남겨둠)
9. Notebook의 모든 작업은 **[계획 → 코드 → 해석] 3단 블록**을 단위로 진행한다.
   구체적인 코딩/작업 규칙은 **[CONVENTIONS.md](./CONVENTIONS.md)** 에서 계속 관리한다.

---

## 5. 데이터 명세

**DataFrame의 한 행 = 채용공고 한 건**

| 컬럼명 | 설명 |
|---|---|
| company_name | 회사명 |
| job_title | 공고 제목 |
| career | 경력 조건 |
| location | 근무 지역 |
| posted_date | 등록일 |
| closing_date | 마감일 |
| job_url | 공고 URL (중복/신규 판별 기준 키) |
| search_keyword | 어떤 검색어로 발견했는지 |
| collected_at | 수집 시각 |

신규 공고 판별 기준: **`job_url`** (지난 실행 저장 URL + 이번 수집 URL → 새로 나타난 URL만 신규).
필요 시 보조 키: 회사명 + 공고 제목 + 마감일.
이력 저장 파일: `data/processed/jobs_history.csv` (SQLite 등 별도 DB는 초기에 사용하지 않음).

---

## 6. 최종 폴더 구조

```
chapter11/ax-job-agent/
├── docs/
│   ├── SPEC.md              # 이 문서 (전체 사양)
│   ├── PROGRESS.md          # 진행 상황 체크리스트 (세션 시작 시 항상 확인)
│   └── CONVENTIONS.md       # 코딩/작업 규칙 모음
├── notebooks/
│   └── ax-job-pipeline.ipynb   # 셀 단위 검증 기록 (버리지 않음)
├── src/
│   ├── crawler.py           # collect_jobs()
│   ├── preprocess.py        # clean_jobs(), find_new_jobs()
│   ├── analyzer.py          # analyze_jobs()
│   ├── gemini_client.py     # summarize_with_gemini()
│   ├── reporter.py          # create_report()
│   └── notifier.py          # send_slack(), send_email()
├── data/
│   ├── raw/                 # 원본 수집 데이터 (git 제외)
│   └── processed/           # 정제 데이터, jobs_history.csv (git 제외)
├── reports/                 # 생성된 주간 Markdown 보고서
├── .env.example             # API 키 템플릿 (실값 없음)
├── .gitignore
├── main.py                  # 전체 흐름만 호출 (로직 없음)
├── requirements.txt
└── README.md
```

---

## 7. 아키텍처 (운영 단계)

```
GitHub Actions (주 1회, cron)
        ↓
      main.py
        ↓
     Crawler (잡코리아 검색 결과 수집)
        ↓
     pandas
    ├─ 정제 / 중복 제거
    ├─ 신규 공고 판별 (job_url 기준)
    ├─ 관련 공고 필터링
    └─ 기본 통계 (신규 건수, 회사별/지역별 분포 등)
        ↓
     Gemini API
    ├─ 핵심 내용 요약
    ├─ 요구 기술 추출
    ├─ 직무 유형 분류
    └─ AX 관련성 / 추천 이유
        ↓
     Report (주간 Markdown)
        ↓
   ┌────┴────┐
   ▼         ▼
 Slack     Gmail
```

---

## 8. Git 브랜치 전략

- `origin` = 본인 Fork (`tladntjq1-lgtm/claude-code-agent-course`) — push하는 곳
- `upstream` = 원본 강의 저장소 (`GilbertMoon/claude-code-agent-course`) — 참고용, push 금지
- 작업 브랜치: `ax-job-agent` — 이 프로젝트의 모든 변경사항은 여기서 커밋 후 본인 Fork로 PR
- **주의**: PR을 열 때 반드시 `--repo <본인 Fork>`를 명시할 것. `gh pr create`는 Fork의 경우 기본값이 upstream(원본)으로 잡히는 사고가 발생한 적 있음.

---

## 9. 보안 규칙

- `.env`에는 `GEMINI_API_KEY`, `SLACK_WEBHOOK_URL`, `GMAIL_USER`, `GMAIL_APP_PASSWORD` 저장
- `.env`는 `.gitignore`에 포함되어 커밋되지 않음. 저장소에는 `.env.example`(빈 값)만 커밋
- 운영(GitHub Actions)에서는 동일한 키를 **GitHub Secrets**로 등록해서 환경변수로 전달
- 커밋 전 항상 `git status`/`git diff`로 민감정보 포함 여부 확인

---

## 10. 완료 정의 (Definition of Done)

- [x] `python main.py` 로컬 실행 시 끝까지 에러 없이 성공
- [x] 수집 건수 0건이 아님
- [x] 필수 컬럼 모두 존재, 날짜 변환 실패 없음
- [x] 중복 URL 제거 정상 동작
- [x] 신규 공고 판별 정상 동작
- [x] Gemini 응답이 원문과 크게 다르지 않음 (사람이 샘플 검증)
- [x] Markdown 보고서 생성됨
- [x] Slack 메시지 도착 확인
- [x] Gmail 메일 도착 확인
- [x] GitHub Actions 수동 실행(workflow_dispatch) 성공
- [ ] GitHub Actions 주 1회 schedule 등록 및 정상 실행 확인

세부 진행 상황과 "지금 어디까지 했고 다음에 뭘 해야 하는지"는
**[PROGRESS.md](./PROGRESS.md)** 에서 관리한다.
