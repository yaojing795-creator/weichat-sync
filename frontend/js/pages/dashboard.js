// 仪表盘页面逻辑
let dashboardData = null;

async function loadDashboard() {
  const stats = await api.getTaskStats();
  dashboardData = stats;
  renderDashboard(stats);
}

function renderDashboard(s) {
  document.getElementById('stat-accounts').textContent = s.total_accounts;
  document.getElementById('stat-online').textContent = s.online_accounts;
  document.getElementById('stat-tasks').textContent = s.total_tasks;
  document.getElementById('stat-running').textContent = s.running_tasks;
  document.getElementById('stat-today').textContent = s.today_forwards;
  document.getElementById('stat-success').textContent = s.today_success;
  document.getElementById('stat-failed').textContent = s.today_failed;
}

async function refreshDashboard() {
  const s = await api.getTaskStats();
  dashboardData = s;
  renderDashboard(s);
}

// 注册到全局
window.loadDashboard = loadDashboard;
window.refreshDashboard = refreshDashboard;
