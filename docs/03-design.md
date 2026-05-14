# 03 — Design

## 아키텍처 & 설계 결정 8선

| # | 항목 | **선택** | 대안 | 근거 | 트레이드오프 |
|---|---|---|---|---|---|
| 1 | 백엔드 | **FastAPI** | Django, Express | 비동기 기본 지원, 자동 OpenAPI 문서, 타입 힌트 기반 검증으로 코드량 최소화 | Django보다 ORM·Admin 생태계가 작다. Express보다 JS 개발자에겐 낯설다 |
| 2 | 프론트엔드 | **Vanilla JS + Tailwind CDN** | React, Vue | 빌드 툴 없이 브라우저에서 바로 실행, 의존성 0개, MVP 규모에 프레임워크 오버엔지니어링 방지 | 컴포넌트 재사용성 낮음. 규모 커지면 직접 상태 관리 복잡도 증가 |
| 3 | DB | **SQLite → PostgreSQL + SQLAlchemy** | MySQL, MongoDB | SQLite로 로컬 개발 zero-config, SQLAlchemy로 PostgreSQL 전환 시 코드 변경 최소화 | SQLite는 동시 쓰기 제한. 전환 시 마이그레이션 스크립트 필요 |
| 4 | CSS | **Tailwind only** | styled-components, CSS Modules | 유틸리티 클래스로 HTML에서 스타일 즉시 파악, 빌드 없이 CDN으로 사용 가능, 클래스 네이밍 분쟁 없음 | 클래스 문자열 길어짐. JS-in-CSS 패턴 불가. styled-components는 이 프로젝트에서 **금지** |
| 5 | 실시간 | **폴링 3초 간격** | WebSocket, SSE | MVP에서 인프라 복잡도 최소화. 3초 지연은 팀 업무 현황판 UX에 허용 범위 | 불필요한 요청 발생. 10명 팀 기준 서버 부하 미미. WebSocket은 확장 단계에서 별도 결정 |
| 6 | 상태 관리 | **모듈 변수 + DOM 직접 갱신** | Redux, Zustand, Pinia | 프레임워크 없는 Vanilla JS 환경에서 가장 단순한 패턴. 전역 store 파일 1개로 관리 | 앱 규모 커지면 데이터 흐름 추적 어려움. 프레임워크 도입 시 교체 필요 |
| 7 | 디자인 시스템 | **macOS UI 톤** | Material Design, Ant Design | 01-product 페르소나(Mac 사용 스타트업 팀리더)와 일치. 외부 컴포넌트 라이브러리 의존성 없이 Tailwind 토큰으로 직접 구현 | Material·Ant 컴포넌트 라이브러리 대비 직접 구현 비용 발생 |
| 8 | 테마 | **Tailwind `dark:` + localStorage** | CSS 변수 전환, 외부 테마 라이브러리 | Tailwind 내장 기능으로 별도 라이브러리 없이 구현. `prefers-color-scheme`으로 초기값 자동 감지 | `dark:` 클래스가 HTML 전체에 추가돼 클래스 문자열 길어짐 |

---

## 디자인 토큰 (macOS UI 톤)

| 토큰 | Tailwind 클래스 | 값 | 용도 |
|---|---|---|---|
| 모서리 | `rounded-xl` | `border-radius: 12px` | 카드, 버튼, 입력 필드 |
| 그림자 | `shadow-lg` | 다단계 소프트 섀도 | 카드, 모달 |
| 반투명 배경 | `backdrop-blur-md bg-white/80` | `backdrop-filter: blur(12px)` | 카드, 헤더 |
| 폰트 | `font-sans` | `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` | 전체 |
| 터치 타깃 | `min-h-[44px] min-w-[44px]` | ≥ 44px | 버튼, 아이콘 버튼 |
| 포인트 컬러 | `blue-500 / blue-400` | `#3B82F6 / #60A5FA` | CTA, 배지, 포커스 링 |
| 구분선 | `divide-gray-100 dark:divide-gray-700` | — | 카드 내부 구분 |

---

## 테마 구현 규칙

```
초기값 결정 순서:
1. localStorage에 저장된 값이 있으면 우선 적용
2. 없으면 prefers-color-scheme 미디어 쿼리 결과 적용
3. 그것도 없으면 라이트 모드 기본값
```

- `<html>` 태그에 `class="dark"` 를 토글해 Tailwind `dark:` 변형 전체 활성화
- 토글 버튼 클릭 시 `localStorage.setItem('theme', 'dark' | 'light')` 저장
- 페이지 로드 시 `<head>` 인라인 스크립트로 깜빡임(FOUC) 없이 즉시 적용

---

## 의존성 추가 정책

> 새 라이브러리·패키지를 추가하기 전에 **이 파일(`03-design.md`)에 사유를 먼저 기록**해야 한다.
> 사유 없이 `import` 또는 `<script src>` 추가는 금지.

기록 형식:

```
### [라이브러리명] 도입 사유
- 문제: (기존 스택으로 해결할 수 없는 이유)
- 대안 검토: (대안과 비교 결과)
- 결정: (도입 또는 기각)
```
