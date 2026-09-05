// 跟圈任务页面逻辑
let tasksList = [];
let accountsList = [];

async function loadTasks() {
  [tasksList, accountsList] = await Promise.all([
    api.getTasks(),
    api.getAccounts()
  ]);
  renderTasks(tasksList);
  populateAccountSelect();
}

function populateAccountSelect() {
  const sel = document.getElementById('select-task-account');
  sel.innerHTML = accountsList.map(a =>
    `<option value="${a.id}">${escHtml(a.nickname || a.wxid)} (${a.wxid})</option>`
  ).join('');
}

function renderTasks(list) {
  const container = document.getElementById('tasks-list');
  if (!list.length) {
    container.innerHTML = `<div class="empty-state"><div class="icon">📋</div><p>暂无跟圈任务，点击"新建任务"开始配置</p></div>`;
    return;
  }
  container.innerHTML = list.map(t => {
    const acc = accountsList.find(a => a.id === t.account_id);
    return `
    <div class="card" style="margin-bottom:14px;">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
        <div>
          <div style="font-weight:600;font-size:14px;">监听: ${escHtml(t.source_wxid)}</div>
          <div style="font-size:12px;color:var(--text-light);margin-top:3px;">
            转发到: <strong>${escHtml(acc?.nickname || acc?.wxid || '未知账号')}</strong>
            &nbsp;|&nbsp; 延迟: ${t.delay_seconds}秒
            &nbsp;|&nbsp; 
            <span class="tag tag-${t.is_running ? 'online' : 'offline'}">${t.is_running ? '运行中' : '已停止'}</span>
            &nbsp;|&nbsp;
            已转发: ${t.total_forwarded} 次 | 失败: ${t.total_failed} 次
          </div>
          ${t.last_sync_time ? `<div style="font-size:11px;color:#aaa;margin-top:3px;">最近同步: ${formatRelative(t.last_sync_time)}</div>` : ''}
        </div>
        <div style="display:flex;gap:8px;flex-shrink:0;">
          ${t.is_running
            ? `<button class="btn btn-gray btn-sm" onclick="stopTask(${t.id})">停止</button>`
            : `<button class="btn btn-green btn-sm" onclick="startTask(${t.id})">启动</button>`
          }
          <button class="btn btn-blue btn-sm" onclick="viewTaskLogs(${t.id})">日志</button>
          <button class="btn btn-red btn-sm" onclick="deleteTask(${t.id})">删除</button>
        </div>
      </div>
    </div>`;
  }).join('');
}

async function showAddTaskModal() {
  showModal('modal-add-task');
  await loadTasks(); // 刷新账号列表
  document.getElementById('input-source-wxid').value = '';
  document.getElementById('input-source-nickname').value = '';
  document.getElementById('input-delay').value = '60';
}

async function submitAddTask() {
  const accountId = parseInt(document.getElementById('select-task-account').value);
  const sourceWxid = document.getElementById('input-source-wxid').value.trim();
  const sourceNickname = document.getElementById('input-source-nickname').value.trim();
  const delay = parseInt(document.getElementById('input-delay').value) || 60;
  if (!accountId || !sourceWxid) { toast('请填写完整信息', 'warning'); return; }
  try {
    await api.createTask({ account_id: accountId, source_wxid: sourceWxid, source_nickname: sourceNickname || null, delay_seconds: delay });
    toast('任务创建成功', 'success');
    hideModal('modal-add-task');
    await loadTasks();
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function startTask(id) {
  try {
    await api.startTask(id);
    toast('任务已启动', 'success');
    await loadTasks();
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function stopTask(id) {
  try {
    await api.stopTask(id);
    toast('任务已停止', 'info');
    await loadTasks();
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function deleteTask(id) {
  if (!await confirmAction('确定删除该跟圈任务？')) return;
  try {
    await api.deleteTask(id);
    toast('任务已删除', 'success');
    await loadTasks();
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function viewTaskLogs(taskId) {
  try {
    const logs = await api.getTaskLogs(taskId, 30);
    const container = document.getElementById('task-logs-content');
    if (!logs.length) {
      container.innerHTML = '<div class="empty-state"><p>暂无转发日志</p></div>';
    } else {
      container.innerHTML = `<div class="table-wrap"><table>
        <thead><tr><th>时间</th><th>来源</th><th>类型</th><th>摘要</th><th>状态</th><th>延迟</th></tr></thead>
        <tbody>${logs.map(l => `
          <tr>
            <td>${formatDate(l.created_at)}</td>
            <td>${escHtml(l.source_wxid)}</td>
            <td><span class="tag tag-info">${l.content_type}</span></td>
            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escHtml(l.content_summary)}</td>
            <td><span class="tag tag-${l.status === 'success' ? 'success' : 'danger'}">${l.status === 'success' ? '成功' : '失败'}</span></td>
            <td>${l.delay_applied ?? '-'}s</td>
          </tr>`).join('')}
        </tbody></table></div>`;
    }
    document.getElementById('task-logs-title').textContent = `转发日志（任务ID: ${taskId}）`;
    showModal('modal-task-logs');
  } catch (e) {
    toast(e.message, 'error');
  }
}

window.loadTasks = loadTasks;
window.showAddTaskModal = showAddTaskModal;
window.submitAddTask = submitAddTask;
window.startTask = startTask;
window.stopTask = stopTask;
window.deleteTask = deleteTask;
window.viewTaskLogs = viewTaskLogs;
