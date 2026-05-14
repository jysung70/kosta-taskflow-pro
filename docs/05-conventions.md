# 05 — Conventions

## 명명 규칙

| 대상 | 규칙 | 예시 |
|---|---|---|
| 백엔드 변수·함수·파일명 | `snake_case` | `task_id`, `get_task_by_id`, `task_router.py` |
| 프론트엔드 변수·함수 | `camelCase` | `taskList`, `fetchTasks`, `renderCard` |
| 프론트엔드 컴포넌트 | `PascalCase` | `TaskCard`, `EditModal`, `ThemeToggle` |
| 클래스명 (Python) | `PascalCase` | `TaskCreate`, `TaskResponse` |
| 상수 | `UPPER_SNAKE_CASE` | `MAX_TITLE_LENGTH`, `POLL_INTERVAL_MS` |
| DB 테이블·컬럼 | `snake_case` | `tasks`, `due_at`, `created_at` |
| API 경로 | `kebab-case` (소문자) | `/api/tasks`, `/api/tasks/{task_id}` |

**언어 규칙**
- 모든 식별자(변수, 함수, 클래스, 파일명)는 **영어**로 작성
- 주석은 **한국어**로 작성
- 커밋 메시지 요약은 **한국어**로 작성

---

## 금지 목록

| 금지 | 이유 | 대안 |
|---|---|---|
| `print()` 디버깅 | 운영 환경에 노이즈 남김, 민감 정보 노출 위험 | `logging` 모듈 사용 (`logger.debug / info / error`) |
| `bare except:` | 모든 예외를 삼켜 버그 원인 파악 불가 | `except SpecificError as e:` 로 구체적 예외 명시 |
| 비밀번호·토큰 하드코딩 | 코드 저장소 유출 시 즉각 보안 사고 | `.env` 파일 + `os.getenv("KEY")` 사용, `.env` 는 `.gitignore` 에 포함 |
| `any` 타입 (TypeScript) | 타입 정보 소실, 컴파일 타임 오류 탐지 불가 | 명시적 타입 또는 `unknown` 사용 후 타입 가드 적용 |
| `!important` (CSS) | 우선순위 체계 붕괴, 디버깅 난이도 급증 | 셀렉터 구체성 개선 또는 Tailwind 유틸리티 클래스 활용 |

---

## 폴더 구조

```
taskflow-pro/
├── backend/
│   ├── main.py           # FastAPI 앱 진입점
│   ├── database.py       # SQLAlchemy 세션·Base 설정
│   ├── models.py         # Task ORM 모델
│   ├── schemas.py        # Pydantic 스키마 (Create·Update·Response)
│   ├── router.py         # /api/tasks 라우터
│   ├── requirements.txt  # 의존성 목록
│   └── tests/
│       └── test_tasks.py # pytest 테스트
├── frontend/
│   ├── index.html        # 진입점, Tailwind CDN 포함
│   ├── app.js            # 상태 관리 + DOM 갱신 + API 호출
│   └── style.css         # Tailwind 커스텀 확장만 허용
└── docs/
    ├── 00-overview.md
    ├── 01-product.md
    ├── 02-specs.md
    ├── 03-design.md
    ├── 04-tasks.md
    └── 05-conventions.md
```

---

## 테스트 규칙

**도구**: `pytest` (백엔드), 브라우저 수동 확인 (프론트엔드)

모든 API 엔드포인트는 아래 3가지 케이스를 반드시 테스트한다.

| 케이스 | 내용 |
|---|---|
| 정상 케이스 | 올바른 요청 → 기대 응답 코드 + 응답 바디 확인 |
| 400 케이스 | 필수 필드 누락 또는 형식 오류 → `400 Bad Request` 확인 |
| 404 케이스 | 존재하지 않는 `id` → `404 Not Found` 확인 |

```python
# 테스트 파일 명명: test_<대상>.py
# 테스트 함수 명명: test_<동작>_<시나리오>
# 예시
def test_create_task_success():     ...
def test_create_task_missing_title(): ...
def test_get_task_not_found():      ...
```

---

## 커밋 메시지 규칙

```
<type>: <한국어 요약>

[선택] 본문 — 변경 이유나 맥락이 필요할 때만 작성
```

| type | 사용 시점 |
|---|---|
| `feat` | 새 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 작성·수정 |
| `refactor` | 동작 변경 없는 코드 개선 |
| `test` | 테스트 추가·수정 |
| `chore` | 빌드·설정·의존성 변경 |

**예시**

```
feat: Task 목록 조회 API 구현
fix: due_at 누락 시 500 오류 → 400으로 수정
docs: 04-tasks.md Phase 2 체크리스트 추가
test: DELETE 엔드포인트 404 케이스 테스트 추가
chore: requirements.txt SQLAlchemy 버전 고정
```
