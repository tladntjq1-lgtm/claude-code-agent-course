# AX Job Agent — 진행 상황 체크리스트

> **새 세션(Claude Web / Claude Code 어느 쪽이든)을 시작할 때 이 파일을 가장 먼저 읽는다.**
> "지금 어디까지 진행됐는지"와 "다음에 무엇을 해야 하는지"가 여기 다 있다.
> 전체 사양은 [SPEC.md](./SPEC.md) 참고.

---

## 지금 상태 요약 (마지막 업데이트: 2026-09-23)

- **현재 브랜치**: `ax-job-agent`
- **마지막으로 완료한 작업**: **STEP 16 완료 (사용자 본인 확인으로 검증됨)** — `python main.py` 실제 실행 성공 (약 20초), 수집 10건/신규 0건/보고서 생성/Slack 발송 True/Gmail 발송 True. Slack 채널과 Gmail 받은편지함 모두 실제 도착 확인됨
- **다음에 할 일**: STEP 17 — GitHub Actions 수동 실행 (`workflow_dispatch`만 있는 workflow 작성, GitHub Secrets 등록)
- **참고**: `src/` 모듈은 프로젝트 루트(`chapter11/ax-job-agent/`)에서 실행하는 것을 전제로 상대경로(`data/processed/...`, `.env`, `reports/`)를 사용함. 노트북(`notebooks/`)에서 그대로 가져다 쓰려면 경로 앞에 `../`가 필요함
- **주의사항 (.env 재로딩)**: 노트북 실행 중간에 `.env` 값을 새로 채워 넣은 경우, `load_dotenv()`를 다시 호출해도 **기본적으로 이미 로드된 값을 덮어쓰지 않음**. 반드시 `load_dotenv(path, override=True)`로 호출해야 새 값이 반영됨
- **주의사항 (Gemini 할당량)**: `gemini-3.6-flash`는 무료 티어 **하루 20회** 제한이 있어 실습 중 소진됨 (분당 제한과는 별개). `gemini-flash-lite-latest` 모델로 교체해서 해결 (별도 할당량, "lite" 계열 모델이 대체로 여유 있음). `summarize_job()`에 재시도 로직(APIError 전체 캐치, 25초 간격) + `job_url` 기준 캐싱(중복 호출 방지) 추가됨
- **최종 결정사항 (posted_date/closing_date)**: ~~날짜 없이 진행~~ → **날짜까지 포함해서 진행으로 변경**. 목록 페이지가 아닌 상세 페이지 요청(공고당 1회 추가)으로 정확한 날짜 확보 성공
- **보안 주의**: API 키를 절대 채팅에 붙여넣지 말 것. 한 번 사용자가 실수로 붙여넣어 즉시 폐기 후 재발급 처리함. `.env` 파일에 직접 입력하는 방식만 사용
- **중요 결정사항 (수정됨)**: ~~샘플 데이터 사용~~ → **실제 크롤링 데이터 사용**으로 변경. `data/raw/sample_jobs.csv`는 참고/백업용으로 남겨둠. posted_date/closing_date 두 컬럼은 당분간 비워둔 채 진행 (추후 별도 API 리버스엔지니어링으로 재도전 가능)
- **주의**: 노트북을 VS Code에 열어둔 상태에서 Claude Code가 파일을 직접 수정하면, VS Code 화면이 자동 갱신 안 될 수 있음 → 이런 경우 탭 닫고(Don't Save) 다시 열거나 "Revert File" 사용
- **막힌 것 / 주의할 점**:
  - PowerShell에서 venv 활성화 시 `.\` 접두사 필요 (`.\.venv\Scripts\Activate.ps1`)
  - 이 PC는 Windows 보안 정책 때문에 `pip.exe` 직접 실행이 차단됨 → 항상 `python -m pip ...` 사용
  - `gh pr create`는 Fork 저장소에서 기본 대상이 upstream(원본)으로 잡히는 사고가 있었음
    → PR 만들 때 반드시 `--repo tladntjq1-lgtm/claude-code-agent-course` 명시할 것
  - **Jupyter 커널 혼동 주의**: 이 PC에는 `C:\dev\python-study\.venv`처럼 이름이 같은(`.venv`) 다른 프로젝트 가상환경이 여러 개 있음. VS Code 커널 선택 시 이름만 보고 고르면 엉뚱한 환경이 선택될 수 있으니, 반드시 **`Workspace`라고 표시된 `.\.venv\Scripts\python.exe`**를 선택하고, 헷갈리면 `import sys; print(sys.executable)`로 실제 경로를 확인할 것. 커널을 바꾼 뒤에는 재선택뿐 아니라 **재시작(Restart)**까지 해야 반영됨

---

## STEP 체크리스트

### STEP 00. 환경 준비 ✅ 완료
- [x] GitHub 원본 저장소 Fork (`tladntjq1-lgtm/claude-code-agent-course`)
- [x] 로컬 Clone (`C:\dev\claude-code-agent-course`)
- [x] `origin`/`upstream` remote 구분 설정
- [x] 실습 브랜치 `ax-job-agent` 생성
- [x] `chapter11/ax-job-agent/` 폴더 구조 생성 (notebooks/src/data/reports)
- [x] Python 가상환경(`.venv`) 생성 및 활성화
- [x] 패키지 설치: pandas, requests, beautifulsoup4, jupyter, python-dotenv
- [x] `.gitignore`(루트 + 프로젝트), `.env.example` 작성
- [x] PR #1 생성 및 main 브랜치로 merge 완료

### STEP 01. Notebook 뼈대 만들기 ✅ 완료
- [x] `notebooks/ax-job-pipeline.ipynb` 생성
- [x] Markdown Cell + Code Cell 번갈아 사용하는 기본 패턴 적용
- [x] 환경 확인 코드 작성 (Python 버전, pandas/requests/beautifulsoup4 import 확인) — 크롤링 코드는 아직 X
- [x] VS Code에서 올바른 커널(`.venv` Workspace) 선택 후 셀 직접 실행, 에러 없이 출력 확인
- [x] 완료 조건 충족: 모든 셀이 에러 없이 실행되고, import 확인 메시지 출력됨 (pandas 3.0.6, requests 2.34.2, BeautifulSoup OK)

### STEP 02. 수집 데이터 명세 확정 ✅ 완료 (SPEC.md에 이미 명세됨, 별도 노트북 셀 생략하고 STEP 03/04로 통합)

### STEP 03. 채용공고 페이지 접근 테스트 ✅ 완료 (1차 결론 오류 → 정정 완료)
- [x] robots.txt 확인 (일반 크롤러는 공개 검색 페이지 접근 가능, 로그인/마이페이지 등만 차단)
- [x] 사용자가 브라우저에서 직접 검색해 복사한 실제 URL로 테스트, 상태 코드 200 확인
- [x] **1차 결론(SPA라 데이터 없음)이 틀렸음을 재확인**: `data-sentry-component="CardJob"`로 실제 공고 데이터가 원본 HTML에 있음을 확인, 노트북 해석 셀에 정정 기록
- [x] 완료 조건 충족: 실제 크롤링 가능 확정 (posted_date/closing_date 두 필드만 별도 API 필요해 제외)

### STEP 04. 소량 데이터 수집 (실제 크롤링) ✅ 완료
- [x] `collect_jobs(keyword, max_items)` 함수 작성 (requests + BeautifulSoup, "ax" 키워드로 최대 10건)
- [x] company_name/job_title/career/location/job_url 추출 로직을 Bash에서 직접 검증 완료 (정상 동작 확인)
- [x] 사용자가 VS Code 노트북에서 직접 셀 실행 → 실제 수집 결과(GS리테일 등) 확인, 해석 셀 작성 완료
- [x] `data/raw/sample_jobs.csv`(참고용 샘플)는 그대로 두고, 실제 파이프라인은 이 크롤러 결과 사용

### STEP 04-1. 상세 페이지에서 날짜 정보 보강 ✅ 완료
- [x] 공고 상세 페이지의 JSON-LD(`application/ld+json`, schema.org `JobPosting`)에서
      `datePosted`/`validThrough` 추출하는 `get_job_dates()` 함수 작성 (Bash에서 3건 사전 검증)
- [x] 사용자가 노트북에서 실행 → 10/10건 정상 반영 확인 (예: 2026-09-01 등록 / 2026-10-31 마감)

### STEP 05. DataFrame 생성/확정 ✅ 완료 (날짜 포함 재실행 완료)
- [x] `df.info()`/`df.dtypes`로 컬럼 타입 확인, SPEC.md 컬럼과 최종 대조 (일치 확인)
- [x] posted_date/closing_date 포함 결측치 현황 재확인 (모두 채워짐)

### STEP 06. 전처리 / 중복 제거 ✅ 완료 (날짜 포함 재실행 완료)
- [x] job_url 기준 중복 제거 확인 (0건)
- [x] career 결측치 "정보없음"으로 채움 (3건 → 0건)
- [x] `df_clean`에 날짜 포함하여 갱신 완료

### STEP 07. 신규 공고 판별 ✅ 완료
- [x] `data/processed/jobs_history.csv` 도입, 기존 URL과 비교 → 10건 중 9건 기존/1건 신규 정상 판별

### STEP 08. 기본 분석 / 관련 공고 필터링 ✅ 완료
- [x] 신규 건수(0건), 회사별(㈜NAVER 2건 최다)/지역별(경기 성남시 3건 최다) 분포, 경력 분포 계산 완료

### STEP 09. Gemini API 연동 ✅ 완료
- [x] Gemini API 키 발급 (한 번 유출되어 폐기 후 재발급), `.env`에 `GEMINI_API_KEY` 설정
- [x] `google-genai` SDK 설치 (`requirements.txt`에 추가)
- [x] 단일 공고 요약 테스트 성공 (모델: `gemini-3.6-flash`)

### STEP 10. Gemini 결과 검증 ✅ 완료
- [x] 3건 원문과 비교 (2건 정확히 일치/누락·과잉 없음, 1건은 API 일시 오류로 실패 처리)

### STEP 11. Markdown 보고서 생성 ✅ 완료
- [x] SPEC.md 보고서 템플릿대로 `reports/weekly_report_2026-09-23.md` 생성, 추천 공고 3건 Gemini 요약 포함

### STEP 12. Slack 발송 ✅ 완료
- [x] Slack 앱 생성 + Incoming Webhook 발급 (`.env`에 `SLACK_WEBHOOK_URL` 설정)
- [x] `send_slack()` 함수로 전체 보고서 발송, 채널에서 한글/길이 문제 없이 도착 확인
- [x] 보안 이슈 1건: 브라우저 화면에 Webhook URL이 노출되어 즉시 삭제 후 재발급 처리함

### STEP 13. Gmail 발송 ✅ 완료
- [x] Google 계정 2단계 인증 활성화 + 앱 비밀번호 발급
- [x] `.env`에 `GMAIL_USER`/`GMAIL_APP_PASSWORD` 설정, `send_email()` 함수로 발송 성공/수신 확인

### STEP 14. 함수화 ✅ 완료
- [x] `src/crawler.py`: `collect_jobs()`, `get_job_dates()`, `enrich_with_dates()`
- [x] `src/preprocess.py`: `clean_jobs()`, `find_new_jobs()`
- [x] `src/analyzer.py`: `analyze_jobs()`
- [x] `src/gemini_client.py`: `get_gemini_client()`, `summarize_job()` (캐싱 + 재시도 포함)
- [x] `src/reporter.py`: `create_report()`
- [x] `src/notifier.py`: `send_slack()`, `send_email()`
- [x] import 및 실제 데이터 기반 동작 검증 완료 (Bash)

### STEP 15. main.py 통합 ✅ 완료 (초안, 미실행)
- [x] `main.py` 작성 — src 함수들을 순서대로 호출 (collect → enrich → clean → find_new → analyze → report → slack → email)
- [x] 문법 검사(`py_compile`) 통과
- [ ] 실제 실행은 STEP 16에서 진행

### STEP 16. 로컬 전체 실행 검증 ✅ 완료
- [x] `python main.py` 끝까지 성공 (약 20초), 수집 10건/보고서 생성/Slack·Gmail 발송 True
- [x] 사용자가 Slack 채널/Gmail 받은편지함에서 실제 도착 확인

### STEP 17. GitHub Actions 수동 실행 ⬅️ **다음 작업**
- [ ] `workflow_dispatch`만 있는 workflow 작성, Secrets 등록, 수동 실행 성공

### STEP 18. GitHub Actions 주간 실행
- [ ] `schedule: cron` 추가 (주 1회), 정상 동작 확인

---

## 이 파일 사용법

1. **작업 시작 전**: "지금 상태 요약"과 현재 STEP의 미체크 항목을 확인한다.
2. **작업 완료 후**: 해당 항목에 `[x]` 표시하고, "지금 상태 요약"의 마지막 완료 작업/다음 작업/날짜를 갱신한다.
3. **막히거나 특이사항이 생기면**: "막힌 것 / 주의할 점"에 한 줄로 기록해 다음 세션이 같은 실수를 반복하지 않게 한다.
4. Claude Code/Claude Web 세션을 새로 열 때는 이 파일 내용을 붙여넣거나 "PROGRESS.md 확인해줘"라고 요청하면 된다.
