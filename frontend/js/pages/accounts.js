// 账号管理页面逻辑
let accountsList = [];

async function loadAccounts() {
  accountsList = await api.getAccounts();
  renderAccounts(accountsList);
}

function renderAccounts(list) {
  const container = document.getElementById('accounts-list');
  if (!list.length) {
    container.innerHTML = `<div class="empty-state"><div class="icon">💬</div><p>暂无微信账号，请先添加账号</p></div>`;
    return;
  }
  container.innerHTML = list.map(acc => `
    <div class="card" style="margin-bottom:14px;">
      <div style="display:flex;align-items:center;gap:14px;">
        <div style="width:48px;height:48px;border-radius:50%;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;flex-shrink:0;">
          ${(acc.nickname || acc.wxid || '?')[0].toUpperCase()}
        </div>
        <div style="flex:1;">
          <div style="font-weight:600;font-size:15px;">${escHtml(acc.nickname || acc.wxid)}</div>
          <div style="font-size:12px;color:var(--text-light);margin-top:3px;">ID: ${escHtml(acc.wxid)}</div>
          <div style="font-size:12px;color:var(--text-light);margin-top:2px;">
            状态: <span class="tag tag-${acc.status === 'online' ? 'online' : 'offline'}">${acc.status === 'online' ? '在线' : '离线'}</span>
            ${acc.error_msg ? ` <span class="tag tag-danger" title="${escHtml(acc.error_msg)}">⚠ 错误</span>` : ''}
          </div>
          ${acc.last_online ? `<div style="font-size:11px;color:#aaa;margin-top:3px;">最后上线: ${formatRelative(acc.last_online)}</div>` : ''}
          ${acc.last_offline ? `<div style="font-size:11px;color:#aaa;margin-top:1px;">最后离线: ${formatRelative(acc.last_offline)}</div>` : ''}
        </div>
        <div style="display:flex;gap:8px;flex-shrink:0;">
          ${acc.status !== 'online'
            ? `<button class="btn btn-green btn-sm" onclick="onlineAccount(${acc.id})">上线</button>`
            : `<button class="btn btn-gray btn-sm" onclick="offlineAccount(${acc.id})">下线</button>`
          }
          <button class="btn btn-red btn-sm" onclick="deleteAccount(${acc.id})">删除</button>
        </div>
      </div>
    </div>
  `).join('');
}

async function onlineAccount(id) {
  try {
    await api.accountOnline(id);
    toast('账号已上线', 'success');
    await loadAccounts();
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function offlineAccount(id) {
  try {
    await api.accountOffline(id);
    toast('账号已下线', 'info');
    await loadAccounts();
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function deleteAccount(id) {
  if (!await confirmAction('确定要删除该微信账号吗？')) return;
  try {
    await api.deleteAccount(id);
    toast('账号已删除', 'success');
    await loadAccounts();
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function showAddAccountModal() {
  showModal('modal-add-account');
  document.getElementById('input-wxid').value = '';
  document.getElementById('input-nickname').value = '';
}

async function submitAddAccount() {
  const wxid = document.getElementById('input-wxid').value.trim();
  const nickname = document.getElementById('input-nickname').value.trim();
  if (!wxid) { toast('请输入微信ID', 'warning'); return; }
  try {
    await api.createAccount({ wxid, nickname: nickname || null });
    toast('账号添加成功', 'success');
    hideModal('modal-add-account');
    await loadAccounts();
  } catch (e) {
    toast(e.message, 'error');
  }
}

window.loadAccounts = loadAccounts;
window.onlineAccount = onlineAccount;
window.offlineAccount = offlineAccount;
window.deleteAccount = deleteAccount;
window.showAddAccountModal = showAddAccountModal;
window.submitAddAccount = submitAddAccount;
