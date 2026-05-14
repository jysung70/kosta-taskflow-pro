"""
프론트엔드 E2E 테스트 — Playwright
전제: 백엔드 http://localhost:8000, 프론트엔드 http://localhost:5500 실행 중
"""
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5500"


@pytest.fixture(autouse=True)
def clean_tasks(page: Page):
    """각 테스트 전 DB를 빈 상태로 초기화"""
    import requests
    tasks = requests.get("http://localhost:8000/api/tasks").json()
    for t in tasks:
        requests.delete(f"http://localhost:8000/api/tasks/{t['id']}")
    yield


# ── 페이지 로딩 ──────────────────────────────────────────────────────

def test_page_loads(page: Page):
    """페이지 제목과 헤더가 정상 표시된다"""
    page.goto(BASE_URL)
    expect(page).to_have_title("TaskFlow Pro")
    expect(page.locator("h1")).to_have_text("TaskFlow Pro")


def test_empty_state_message(page: Page):
    """업무가 없으면 빈 상태 메시지가 표시된다"""
    page.goto(BASE_URL)
    page.wait_for_timeout(500)
    expect(page.locator("#empty-msg")).to_have_text("등록된 업무가 없습니다")


# ── 업무 추가 (Create) ────────────────────────────────────────────────

def test_add_task_success(page: Page):
    """업무를 추가하면 카드가 목록에 표시된다"""
    page.goto(BASE_URL)
    page.fill("#input-title", "E2E 테스트 업무")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    expect(page.locator("#task-list")).to_contain_text("E2E 테스트 업무")


def test_add_task_missing_title_shows_error(page: Page):
    """제목 없이 추가하면 오류 메시지가 표시된다"""
    page.goto(BASE_URL)
    page.click("button[type='submit']")
    expect(page.locator("#add-error")).to_have_text("업무 제목을 입력하세요")


def test_add_task_with_status_and_due(page: Page):
    """상태·마감 시각 포함해 추가하면 카드에 배지와 날짜가 표시된다"""
    page.goto(BASE_URL)
    page.fill("#input-title", "마감 업무")
    page.select_option("#input-status", "in_progress")
    page.fill("#input-due-at", "2099-12-31T09:00")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    expect(page.locator("#task-list")).to_contain_text("In Progress")
    expect(page.locator("#task-list")).to_contain_text("D-")


# ── 업무 목록 (Read) ──────────────────────────────────────────────────

def test_task_list_shows_status_badge(page: Page):
    """목록 카드에 status 배지가 표시된다"""
    page.goto(BASE_URL)
    page.fill("#input-title", "배지 확인 업무")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    expect(page.locator("#task-list .rounded-lg").first).to_be_visible()


def test_overdue_task_shows_red(page: Page):
    """마감이 지난 업무는 빨간색 날짜 텍스트가 표시된다"""
    page.goto(BASE_URL)
    page.fill("#input-title", "마감 초과 업무")
    page.fill("#input-due-at", "2020-01-01T00:00")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    overdue_el = page.locator("#task-list .text-red-500")
    expect(overdue_el).to_be_visible()
    expect(overdue_el).to_contain_text("D+")


# ── 업무 수정 (Update) ────────────────────────────────────────────────

def test_edit_modal_opens_on_card_click(page: Page):
    """카드 클릭 시 수정 모달이 열린다"""
    page.goto(BASE_URL)
    page.fill("#input-title", "수정 대상 업무")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    page.locator("[data-action='edit']").first.click()
    expect(page.locator("#modal-overlay")).to_be_visible()
    expect(page.locator("#modal-title")).to_have_value("수정 대상 업무")


def test_edit_task_updates_card(page: Page):
    """수정 모달에서 저장하면 카드 내용이 갱신된다"""
    page.goto(BASE_URL)
    page.fill("#input-title", "수정 전 제목")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    page.locator("[data-action='edit']").first.click()
    page.fill("#modal-title", "수정 후 제목")
    page.select_option("#modal-status", "done")
    page.click("#modal-save")
    page.wait_for_timeout(500)
    expect(page.locator("#task-list")).to_contain_text("수정 후 제목")
    expect(page.locator("#task-list")).to_contain_text("Done")


def test_edit_modal_closes_on_cancel(page: Page):
    """취소 버튼 클릭 시 모달이 닫힌다"""
    page.goto(BASE_URL)
    page.fill("#input-title", "취소 테스트")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    page.locator("[data-action='edit']").first.click()
    page.click("#modal-cancel")
    expect(page.locator("#modal-overlay")).to_be_hidden()


# ── 업무 삭제 (Delete) ────────────────────────────────────────────────

def test_delete_dialog_opens(page: Page):
    """휴지통 클릭 시 삭제 확인 다이얼로그가 열린다"""
    page.goto(BASE_URL)
    page.fill("#input-title", "삭제 대상 업무")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    page.locator("[data-action='delete']").first.click()
    expect(page.locator("#delete-overlay")).to_be_visible()


def test_delete_confirm_removes_card(page: Page):
    """삭제 확인 시 카드가 목록에서 제거된다"""
    page.goto(BASE_URL)
    page.fill("#input-title", "삭제될 업무")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    page.locator("[data-action='delete']").first.click()
    page.click("#delete-confirm")
    page.wait_for_timeout(500)
    expect(page.locator("#task-list")).not_to_contain_text("삭제될 업무")


def test_delete_cancel_keeps_card(page: Page):
    """삭제 취소 시 카드가 그대로 유지된다"""
    page.goto(BASE_URL)
    page.fill("#input-title", "취소되는 삭제")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    page.locator("[data-action='delete']").first.click()
    page.click("#delete-cancel")
    page.wait_for_timeout(300)
    expect(page.locator("#task-list")).to_contain_text("취소되는 삭제")


# ── 테마 토글 ─────────────────────────────────────────────────────────

def test_theme_toggle_switches_dark(page: Page):
    """테마 토글 클릭 시 dark 클래스가 html에 토글된다"""
    page.goto(BASE_URL)
    html = page.locator("html")
    before = "dark" in (html.get_attribute("class") or "")
    page.click("#theme-toggle")
    after = "dark" in (html.get_attribute("class") or "")
    assert before != after, "테마가 전환되지 않았습니다"


def test_theme_persists_after_reload(page: Page):
    """테마 선택이 새로고침 후에도 유지된다"""
    page.goto(BASE_URL)
    page.evaluate("localStorage.setItem('theme', 'dark')")
    page.reload()
    page.wait_for_timeout(300)
    html_class = page.locator("html").get_attribute("class") or ""
    assert "dark" in html_class, "새로고침 후 다크 테마가 유지되지 않았습니다"


# ── 반응형 ────────────────────────────────────────────────────────────

def test_layout_360px(page: Page):
    """360px 너비에서 레이아웃이 깨지지 않는다"""
    page.set_viewport_size({"width": 360, "height": 780})
    page.goto(BASE_URL)
    expect(page.locator("h1")).to_be_visible()
    expect(page.locator("#add-form")).to_be_visible()
