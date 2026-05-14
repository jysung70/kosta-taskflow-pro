import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# 테스트 전용 인메모리 SQLite DB
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


client = TestClient(app)


# ── POST /api/tasks ──────────────────────────────────────────────────
def test_create_task_success():
    res = client.post("/api/tasks", json={"title": "테스트 업무"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "테스트 업무"
    assert data["status"] == "todo"
    assert "description" in data


def test_create_task_with_all_fields():
    res = client.post("/api/tasks", json={
        "title": "전체 필드",
        "description": "설명",
        "status": "in_progress",
        "due_at": "2026-05-12T18:00:00Z",
    })
    assert res.status_code == 201
    assert res.json()["due_at"] is not None


def test_create_task_missing_title():
    res = client.post("/api/tasks", json={"description": "제목 없음"})
    assert res.status_code == 400


def test_create_task_title_too_long():
    res = client.post("/api/tasks", json={"title": "a" * 201})
    assert res.status_code == 400


def test_create_task_invalid_status():
    res = client.post("/api/tasks", json={"title": "잘못된 상태", "status": "unknown"})
    assert res.status_code == 400


# ── GET /api/tasks ───────────────────────────────────────────────────
def test_list_tasks_success():
    client.post("/api/tasks", json={"title": "업무 1"})
    client.post("/api/tasks", json={"title": "업무 2"})
    res = client.get("/api/tasks")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_list_tasks_no_description():
    # 목록 응답에 description 필드가 없어야 한다
    client.post("/api/tasks", json={"title": "업무", "description": "숨겨야 할 설명"})
    res = client.get("/api/tasks")
    assert res.status_code == 200
    assert "description" not in res.json()[0]


# ── GET /api/tasks/{id} ──────────────────────────────────────────────
def test_get_task_success():
    created = client.post("/api/tasks", json={"title": "단건 조회", "description": "설명"}).json()
    res = client.get(f"/api/tasks/{created['id']}")
    assert res.status_code == 200
    assert res.json()["description"] == "설명"


def test_get_task_not_found():
    res = client.get("/api/tasks/999")
    assert res.status_code == 404


# ── PUT /api/tasks/{id} ──────────────────────────────────────────────
def test_update_task_success():
    created = client.post("/api/tasks", json={"title": "수정 전"}).json()
    res = client.put(f"/api/tasks/{created['id']}", json={"status": "in_progress"})
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"
    assert res.json()["title"] == "수정 전"  # 부분 수정: 나머지 필드 유지 확인


def test_update_task_not_found():
    res = client.put("/api/tasks/999", json={"status": "done"})
    assert res.status_code == 404


def test_update_task_invalid_status():
    created = client.post("/api/tasks", json={"title": "업무"}).json()
    res = client.put(f"/api/tasks/{created['id']}", json={"status": "invalid"})
    assert res.status_code == 400


# ── DELETE /api/tasks/{id} ───────────────────────────────────────────
def test_delete_task_success():
    created = client.post("/api/tasks", json={"title": "삭제 대상"}).json()
    res = client.delete(f"/api/tasks/{created['id']}")
    assert res.status_code == 204


def test_delete_task_not_found():
    res = client.delete("/api/tasks/999")
    assert res.status_code == 404


def test_delete_task_then_get_returns_404():
    # 삭제 후 조회 시 404 반환 확인
    created = client.post("/api/tasks", json={"title": "삭제 후 조회"}).json()
    client.delete(f"/api/tasks/{created['id']}")
    res = client.get(f"/api/tasks/{created['id']}")
    assert res.status_code == 404
