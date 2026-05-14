# 02 — Specs

## 데이터 모델

### Task

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|---|---|---|---|---|
| `id` | INTEGER (PK, AUTO_INCREMENT) | — | 자동 생성 | 고유 식별자 |
| `title` | VARCHAR(200) | ✅ | — | 업무 제목 |
| `description` | TEXT | — | NULL | 업무 상세 설명 |
| `status` | ENUM | — | `todo` | `todo` / `in_progress` / `done` |
| `due_at` | DATETIME (UTC) | — | NULL | 마감 시각, 선택 입력 |
| `created_at` | DATETIME (UTC) | — | 자동 생성 | 생성 시각 |
| `updated_at` | DATETIME (UTC) | — | 자동 갱신 | 최종 수정 시각 |

---

## 검증 규칙

| 조건 | 응답 |
|---|---|
| `title` 누락 또는 빈 문자열 | `400 Bad Request` |
| `title` 200자 초과 | `400 Bad Request` |
| `status` 허용값 외 값 입력 | `400 Bad Request` |
| `due_at` ISO 8601 형식 아님 | `400 Bad Request` |
| 존재하지 않는 `id` 로 조회·수정·삭제 요청 | `404 Not Found` |

`due_at` 허용 형식 예시: `2026-05-12T18:00:00Z`, `2026-05-12T18:00:00+09:00`

---

## REST API

### 엔드포인트 목록

| 메서드 | 경로 | 설명 | 성공 응답 |
|---|---|---|---|
| `POST` | `/api/tasks` | 업무 생성 | `201 Created` |
| `GET` | `/api/tasks` | 업무 목록 조회 | `200 OK` |
| `GET` | `/api/tasks/:id` | 업무 단건 조회 | `200 OK` |
| `PUT` | `/api/tasks/:id` | 업무 수정 (부분 수정 허용) | `200 OK` |
| `DELETE` | `/api/tasks/:id` | 업무 삭제 | `204 No Content` |

---

### POST `/api/tasks` — 업무 생성

**Request Body**
```json
{
  "title": "디자인 시안 검토",
  "description": "피그마 링크 확인 후 피드백 작성",
  "status": "todo",
  "due_at": "2026-05-12T18:00:00Z"
}
```

**Response `201`**
```json
{
  "id": 1,
  "title": "디자인 시안 검토",
  "description": "피그마 링크 확인 후 피드백 작성",
  "status": "todo",
  "due_at": "2026-05-12T18:00:00Z",
  "created_at": "2026-05-14T09:00:00Z",
  "updated_at": "2026-05-14T09:00:00Z"
}
```

---

### GET `/api/tasks` — 업무 목록 조회

> `description` 필드는 목록 응답에서 **제외**한다.

**Response `200`**
```json
[
  {
    "id": 1,
    "title": "디자인 시안 검토",
    "status": "todo",
    "due_at": "2026-05-12T18:00:00Z",
    "created_at": "2026-05-14T09:00:00Z",
    "updated_at": "2026-05-14T09:00:00Z"
  }
]
```

---

### GET `/api/tasks/:id` — 업무 단건 조회

> `description` 필드를 **포함**한다.

**Response `200`**
```json
{
  "id": 1,
  "title": "디자인 시안 검토",
  "description": "피그마 링크 확인 후 피드백 작성",
  "status": "todo",
  "due_at": "2026-05-12T18:00:00Z",
  "created_at": "2026-05-14T09:00:00Z",
  "updated_at": "2026-05-14T09:00:00Z"
}
```

---

### PUT `/api/tasks/:id` — 업무 수정

> 전송한 필드만 수정한다. 누락된 필드는 기존 값을 유지한다.

**Request Body** (부분 수정 예시)
```json
{
  "status": "in_progress"
}
```

**Response `200`** — 수정된 전체 Task 객체 반환 (단건 조회와 동일한 형태)

---

### DELETE `/api/tasks/:id` — 업무 삭제

**Response `204 No Content`** — 본문 없음

---

## 화면 명세

### 추가 — 입력 폼

| 필드 | UI 요소 | 비고 |
|---|---|---|
| `title` | 텍스트 입력 | 필수, 200자 제한 |
| `description` | 텍스트영역 | 선택 |
| `status` | 셀렉트 박스 | 기본값 `todo` |
| `due_at` | 날짜+시간 picker | 선택, 형식: `YYYY-MM-DD HH:mm` |

> 수정 모달에서 카드 클릭 시 `GET /api/tasks/{id}` 단건 조회로 `description` 포함 전체 필드를 로드한다.

---

### 목록 — 업무 카드

각 업무는 카드 형태로 표시한다.

```
┌─────────────────────────────────────┐
│  [todo 배지]  디자인 시안 검토        │
│  D-3  18:00                         │
└─────────────────────────────────────┘
```

| 요소 | 표시 규칙 |
|---|---|
| `status` 배지 | `todo` / `in_progress` / `done` 색상 구분 |
| `due_at` | `D-N HH:MM` 형식, 마감 초과 시 빨간색 표시 |
| `description` | 목록에서 미표시 |

---

### 수정 — 카드 클릭 → 모달

- 카드 클릭 시 수정 모달이 열린다.
- 모달 안에 `title`, `description`, `status`, `due_at` 수정 폼을 표시한다.
- 저장 버튼 클릭 시 `PUT /api/tasks/:id` 호출 후 모달 닫기.

---

### 삭제 — 휴지통 아이콘 → 확인 → DELETE

1. 카드의 휴지통 아이콘 클릭
2. 확인 다이얼로그 표시: "이 업무를 삭제할까요?"
3. 확인 시 `DELETE /api/tasks/:id` 호출
4. 목록에서 해당 카드 즉시 제거
