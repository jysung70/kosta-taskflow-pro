const API_BASE = 'http://localhost:8000/api/tasks';
const POLL_INTERVAL_MS = 3000;

// ── 상태 ─────────────────────────────────────────────────────────────
let tasks = [];
let editingTaskId = null;
let deletingTaskId = null;

// ── API ──────────────────────────────────────────────────────────────

async function fetchTasks() {
  try {
    const res = await fetch(API_BASE);
    tasks = await res.json();
    renderTasks();
  } catch (e) {
    // 서버 미응답 시 조용히 무시 (폴링 특성상 일시적 오류 허용)
  }
}

async function createTask(data) {
  const res = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw await res.json();
  return res.json();
}

async function updateTask(id, data) {
  const res = await fetch(`${API_BASE}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw await res.json();
  return res.json();
}

async function deleteTask(id) {
  const res = await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
  if (!res.ok) throw await res.json();
}

// ── 렌더링 ───────────────────────────────────────────────────────────

const STATUS_BADGE = {
  todo:        'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  in_progress: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300',
  done:        'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
};
const STATUS_LABEL = { todo: 'Todo', in_progress: 'In Progress', done: 'Done' };

function formatDueAt(dueAtStr) {
  if (!dueAtStr) return null;
  const due = new Date(dueAtStr);
  const now = new Date();
  const diffDays = Math.floor((due - now) / 86_400_000);
  const hhmm = due.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
  const tag = diffDays >= 0 ? `D-${diffDays}` : `D+${Math.abs(diffDays)}`;
  return { text: `${tag} ${hhmm}`, overdue: due < now };
}

function toDatetimeLocal(isoStr) {
  if (!isoStr) return '';
  const d = new Date(isoStr);
  // datetime-local 입력 포맷: YYYY-MM-DDTHH:mm (로컬 시각 기준)
  return new Date(d.getTime() - d.getTimezoneOffset() * 60_000)
    .toISOString()
    .slice(0, 16);
}

function escapeHtml(str) {
  return String(str).replace(
    /[&<>"']/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])
  );
}

function renderCard(task) {
  const due = formatDueAt(task.due_at);
  const badge = STATUS_BADGE[task.status] ?? STATUS_BADGE.todo;
  const label = STATUS_LABEL[task.status] ?? task.status;

  const div = document.createElement('div');
  div.className =
    'bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-xl shadow-lg p-4 ' +
    'flex items-center gap-3 hover:shadow-xl transition-shadow duration-150';
  div.dataset.taskId = task.id;

  div.innerHTML = `
    <div class="flex-1 min-w-0 cursor-pointer" data-action="edit">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="shrink-0 px-2 py-0.5 rounded-lg text-xs font-medium ${badge}">${label}</span>
        <span class="text-gray-900 dark:text-white font-medium truncate">${escapeHtml(task.title)}</span>
      </div>
      ${due
        ? `<p class="mt-1 text-xs ${due.overdue ? 'text-red-500' : 'text-gray-400 dark:text-gray-500'}">${due.text}</p>`
        : ''}
    </div>
    <button
      class="shrink-0 min-h-[44px] min-w-[44px] flex items-center justify-center rounded-xl text-lg
             text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
      data-action="delete" aria-label="삭제">🗑</button>
  `;
  return div;
}

function renderTasks() {
  const list = document.getElementById('task-list');
  const empty = document.getElementById('empty-msg');
  list.innerHTML = '';

  if (tasks.length === 0) {
    empty.textContent = '등록된 업무가 없습니다';
    return;
  }
  empty.textContent = '';
  tasks.forEach(t => list.appendChild(renderCard(t)));
}

// ── 추가 폼 ──────────────────────────────────────────────────────────

document.getElementById('add-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const title   = document.getElementById('input-title').value.trim();
  const status  = document.getElementById('input-status').value;
  const dueAt   = document.getElementById('input-due-at').value;
  const errEl   = document.getElementById('add-error');

  if (!title) { errEl.textContent = '업무 제목을 입력하세요'; return; }
  errEl.textContent = '';

  const payload = { title, status };
  if (dueAt) payload.due_at = new Date(dueAt).toISOString();

  try {
    await createTask(payload);
    e.target.reset();
    await fetchTasks();
  } catch {
    errEl.textContent = '추가 실패 — 입력값을 확인하세요';
  }
});

// ── 카드 클릭 (이벤트 위임) ──────────────────────────────────────────

document.getElementById('task-list').addEventListener('click', (e) => {
  const card = e.target.closest('[data-task-id]');
  if (!card) return;
  const action = e.target.closest('[data-action]')?.dataset.action;
  const id = Number(card.dataset.taskId);
  if (action === 'delete') openDeleteDialog(id);
  else openEditModal(id);
});

// ── 수정 모달 ────────────────────────────────────────────────────────

function openEditModal(taskId) {
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;
  editingTaskId = taskId;
  document.getElementById('modal-title').value       = task.title;
  document.getElementById('modal-description').value = task.description ?? '';
  document.getElementById('modal-status').value      = task.status;
  document.getElementById('modal-due-at').value      = toDatetimeLocal(task.due_at);
  document.getElementById('modal-error').textContent = '';
  showOverlay('modal-overlay');
}

function closeEditModal() {
  editingTaskId = null;
  hideOverlay('modal-overlay');
}

document.getElementById('modal-cancel').addEventListener('click', closeEditModal);
document.getElementById('modal-overlay').addEventListener('click', (e) => {
  if (e.target === document.getElementById('modal-overlay')) closeEditModal();
});

document.getElementById('modal-save').addEventListener('click', async () => {
  const title       = document.getElementById('modal-title').value.trim();
  const description = document.getElementById('modal-description').value.trim();
  const status      = document.getElementById('modal-status').value;
  const dueAt       = document.getElementById('modal-due-at').value;
  const errEl       = document.getElementById('modal-error');

  if (!title) { errEl.textContent = '업무 제목을 입력하세요'; return; }
  errEl.textContent = '';

  const payload = { title, description: description || null, status,
                    due_at: dueAt ? new Date(dueAt).toISOString() : null };
  try {
    await updateTask(editingTaskId, payload);
    closeEditModal();
    await fetchTasks();
  } catch {
    errEl.textContent = '저장 실패 — 입력값을 확인하세요';
  }
});

// ── 삭제 다이얼로그 ──────────────────────────────────────────────────

function openDeleteDialog(taskId) {
  deletingTaskId = taskId;
  showOverlay('delete-overlay');
}

function closeDeleteDialog() {
  deletingTaskId = null;
  hideOverlay('delete-overlay');
}

document.getElementById('delete-cancel').addEventListener('click', closeDeleteDialog);
document.getElementById('delete-overlay').addEventListener('click', (e) => {
  if (e.target === document.getElementById('delete-overlay')) closeDeleteDialog();
});

document.getElementById('delete-confirm').addEventListener('click', async () => {
  try {
    await deleteTask(deletingTaskId);
  } finally {
    closeDeleteDialog();
    await fetchTasks();
  }
});

// ── 테마 토글 ────────────────────────────────────────────────────────

function applyTheme(dark) {
  document.documentElement.classList.toggle('dark', dark);
  document.getElementById('theme-icon').textContent = dark ? '☀️' : '🌙';
  localStorage.setItem('theme', dark ? 'dark' : 'light');
}

document.getElementById('theme-toggle').addEventListener('click', () => {
  applyTheme(!document.documentElement.classList.contains('dark'));
});

// 초기 아이콘 동기화
applyTheme(document.documentElement.classList.contains('dark'));

// ── 오버레이 표시 제어 ───────────────────────────────────────────────

function showOverlay(id) { document.getElementById(id).style.display = 'flex'; }
function hideOverlay(id) { document.getElementById(id).style.display = 'none'; }

// 초기 상태: 오버레이 숨김
hideOverlay('modal-overlay');
hideOverlay('delete-overlay');

// ── 3초 폴링 시작 ────────────────────────────────────────────────────

fetchTasks();
setInterval(fetchTasks, POLL_INTERVAL_MS);
