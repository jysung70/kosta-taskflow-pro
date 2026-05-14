# 04 — Tasks

## 진행 규칙

- **순서대로만 진행** — 이전 단계 검증 통과 전 다음 단계 시작 금지
- **병렬 작업 금지** — Phase 2와 Phase 3은 동시 진행하지 않는다
- **단계별 검증 필수** — 검증 방법 항목을 실제로 실행해 확인 후 ✅ 표시
- **확장 단계 미포함** — JWT 로그인, 팀, Kanban 등은 별도 문서에서 다룬다

---

## Phase 1 — 설계 ✅ 완료

| # | 작업 | 상태 | 검증 방법 |
|---|---|---|---|
| 1 | GitHub 저장소 생성 및 로컬 연결 | ✅ | `git remote -v` 에서 origin URL 확인 |
| 2 | `CLAUDE.md` 작성 (역할·규칙·모호한 요청 처리) | ✅ | 파일 존재 및 5개 절대 규칙 항목 확인 |
| 3 | `docs/` 폴더 생성 및 6개 파일 초기화 | ✅ | `ls docs/` 에서 00~05 파일 6개 확인 |
| 4 | `docs/00-overview.md` 작성 | ✅ | 파일 매핑표·읽는 순서·관심사 분리 설명 포함 확인 |
| 5 | `docs/01-product.md` 작성 | ✅ | 목표·페르소나·MVP 범위·성공 기준 포함 확인 |
| 6 | `docs/02-specs.md` 작성 | ✅ | Task 모델 7필드·API 5개·화면 명세 포함 확인 |
| 7 | `docs/03-design.md` 작성 | ✅ | 설계 결정 8선 표·디자인 토큰·의존성 정책 포함 확인 |
| 8 | `docs/04-tasks.md` 작성 (현재 파일) | ✅ | Phase 1·2·3 체크리스트 및 검증 방법 포함 확인 |
| 9 | `docs/05-conventions.md` 작성 | ✅ | 네이밍·폴더 구조·커밋 메시지 규칙 포함 확인 |
| 10 | 전체 docs/ 일관성 검토 후 최종 push | ✅ | `git log --oneline` 에서 docs 커밋 6개 이상 확인 |

---

## Phase 2 — 백엔드 ✅ 완료

> **시작 조건**: Phase 1 전체 ✅ 완료 후 진행

| # | 작업 | 상태 | 검증 방법 |
|---|---|---|---|
| 1 | `backend/` 폴더 구조 생성 및 `venv` 환경 설정 | ✅ | `python -m venv venv` 실행 후 폴더 생성 확인 |
| 2 | FastAPI·Uvicorn·SQLAlchemy 설치 및 `requirements.txt` 작성 | ✅ | `pip install -r requirements.txt` 오류 없이 완료 확인 |
| 3 | `database.py` — SQLite 연결·세션·Base 설정 | ✅ | `python -c "from database import Base; print('OK')"` 오류 없음 |
| 4 | `models.py` — Task 모델 7필드 정의 및 테이블 생성 | ✅ | `tasks.db` 파일 생성, `tasks` 테이블 확인 |
| 5 | `schemas.py` — Pydantic 스키마 (Create·Update·Response) 작성 | ✅ | `python -c "from schemas import TaskCreate; print('OK')"` 오류 없음 |
| 6 | `POST /api/tasks` 구현 — 201 반환, title 필수 검증 | ✅ | 201 확인, title 없이 요청 시 400 확인 |
| 7 | `GET /api/tasks` 구현 — 200 반환, description 제외 | ✅ | 응답 JSON에 `description` 필드 없음 확인 |
| 8 | `GET /api/tasks/{id}` 구현 — 200 반환, description 포함, 없는 id → 404 | ✅ | 존재 id → 200·description 포함, 없는 id → 404 각각 확인 |
| 9 | `PUT /api/tasks/{id}` 구현 — 부분 수정 200 반환 | ✅ | `{"status": "in_progress"}` 만 전송 후 나머지 필드 유지 확인 |
| 10 | `DELETE /api/tasks/{id}` 구현 — 204 반환, Swagger UI 전체 확인 | ✅ | `http://localhost:8000/docs` 에서 5개 엔드포인트 확인, pytest 15개 통과 |

---

## Phase 3 — 프론트엔드 ✅ 완료

> **시작 조건**: Phase 2 전체 ✅ 완료 후 진행

| # | 작업 | 상태 | 검증 방법 |
|---|---|---|---|
| 1 | `frontend/` 폴더 구조 생성 (`index.html`, `app.js`, `style.css`) | ✅ | 3개 파일 존재 확인, 브라우저에서 오류 없이 열림 확인 |
| 2 | Tailwind CDN 연결 및 기본 레이아웃 (헤더 + 메인 영역) | ✅ | 브라우저 360px·1280px 양쪽에서 레이아웃 깨짐 없음 확인 |
| 3 | 라이트/다크 테마 토글 구현 (`localStorage` + `prefers-color-scheme` 초기값) | ✅ | 토글 클릭 후 테마 전환, 새로고침 후 상태 유지 확인 |
| 4 | 업무 추가 폼 구현 (`title`, `description`, `status`, `due_at`) — `POST /api/tasks` 연결 | ✅ | 폼 제출 후 201 응답, title 미입력 시 오류 메시지 표시 확인 |
| 5 | 업무 목록 카드 렌더링 (status 배지, `D-N HH:MM`, 마감 초과 빨간색) | ✅ | 카드에 배지·마감 시각 표시, 마감 지난 항목 빨간색 표시 확인 |
| 6 | 수정 모달 구현 (카드 클릭 → 모달 → `PUT /api/tasks/{id}`) | ✅ | 저장 후 목록 즉시 갱신, 모달 닫힘 확인 |
| 7 | 삭제 기능 구현 (휴지통 아이콘 → 확인 다이얼로그 → `DELETE /api/tasks/{id}`) | ✅ | 확인 시 카드 제거, 취소 시 그대로 유지 확인 |
| 8 | 3초 폴링 연결, 360px 반응형 최종 점검, 성공 기준 5개 통과 후 `git push` | ✅ | `01-product.md` 성공 기준 5개 전항목 확인, E2E 16개 통과, push 완료 |

---

## 최종 결과 — 2026-05-14

| 항목 | 결과 |
|---|---|
| Phase 1 설계 | ✅ 10/10 |
| Phase 2 백엔드 | ✅ 10/10 |
| Phase 3 프론트엔드 | ✅ 8/8 |
| pytest (백엔드) | ✅ 15/15 |
| Playwright E2E | ✅ 16/16 |
| MVP 성공 기준 | ✅ 5/5 |
