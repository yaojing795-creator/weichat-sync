// 管理员页面逻辑
let adminStats = null;

async function loadAdminStats() {
  adminStats = await api.adminGetStats();
  renderAdminStats(adminStats);
}

function renderAdminStats(s) {
  document.getElementById('admin-stat-users').textContent = s.total_users;
  document.getElementById('admin-stat-accounts').textContent = s.total_accounts;
  document.getElementById('admin-stat-online').textContent = s.online_accounts;
  document.getElementById('admin-stat-tasks').textContent = s.total_tasks;
  document.getElementById('admin-stat-running').textContent = s.running_tasks;
  document.getElementById('admin-stat-today').textContent = s.today_forwards;
  document.getElementById('admin-stat-success').textContent = s.today_success;
  document.getElementById('admin-stat-failed').textContent = s.today_failed;
}

async function loadAdminUsers() {
  const users = await api.adminGetUsers();
  const container = document.getElementById('admin-users-list');
  container.innerHTML = users.length ? users.map(u => `
    <tr>
      <td>${u.id}</td>
      <td>${escHtml(u.username)}</td>
      <td>${escHtml(u.email || '-')}</td>
      <td><span class="tag tag-${u.is_admin ? 'warning' : 'info'}">${u.is_admin ? '管理员' : '普通用户'}</span></td>
      <td><span class="tag tag-${u.is_active ? 'success' : 'danger'}">${u.is_active ? '正常' : '禁用'}</span></td>
      <td>${formatDate(u.created_at)}</td>
      <td>
        <button class="btn ${u.is_active ? 'btn-gray' : 'btn-green'} btn-sm" onclick="toggleUser(${u.id}, ${!u.is_active})">
          ${u.is_active ? '禁用' : '启用'}
        </button>
      </td>
    </tr>`).join('') : '<tr><td colspan="7" style="text-align:center;color:#aaa;">暂无用户</td></tr>';
}

async function toggleUser(userId, activate) {
  try {
    await api.adminToggleUser(userId);
    toast(activate ? '用户已启用' : '用户已禁用', 'success');
    await loadAdminUsers();
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function loadAdminTasks() {
  const tasks = await api.adminGetTasks();
  const accounts = await api.getAccounts(); // 当前管理员自己的账号做参考
  const container = document.getElementById('admin-tasks-list');
  container.innerHTML = tasks.length ? tasks.map(t => {
    const user = {}; // 实际应获取用户名，简化处理
    return `
    <tr>
      <td>${t.id}</td>
      <td>${escHtml(t.source_wxid)}</td>
      <td>${escHtml(t.account_id)}</td>
      <td><span class="tag tag-${t.is_running ? 'online' : 'offline'}">${t.is_running ? '运行中' : '已停止'}</span></td>
      <td>${t.delay_seconds}s</td>
      <td>${t.total_forwarded}</td>
      <td>${formatDate(t.created_at)}</td>
    </tr>`;
  }).join('') : '<tr><td colspan="7" style="text-align:center;color:#aaa;">暂无任务</td></tr>';
}

window.loadAdminStats = loadAdminStats;
window.loadAdminUsers = loadAdminUsers;
window.loadAdminTasks = loadAdminTasks;
window.toggleUser = toggleUser;
