// API 客户端封装
const API_BASE = '/api';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  _headers() {
    const h = { 'Content-Type': 'application/json' };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  }

  async _request(method, path, body) {
    const opts = { method, headers: this._headers(), credentials: 'include' };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API_BASE + path, opts);
    if (res.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      location.href = '/login';
      throw new Error('未授权');
    }
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || '请求失败');
    return data;
  }

  get(path) { return this._request('GET', path); }
  post(path, body) { return this._request('POST', path, body); }
  put(path, body) { return this._request('PUT', path, body); }
  delete(path) { return this._request('DELETE', path); }

  login(username, password) {
    return this.post('/auth/login', { username, password });
  }

  register(username, password, email) {
    return this.post('/auth/register', { username, password, email });
  }

  getMe() { return this.get('/auth/me'); }

  // 账号管理
  getAccounts() { return this.get('/accounts/'); }
  createAccount(data) { return this.post('/accounts/', data); }
  updateAccount(id, data) { return this.put(`/accounts/${id}`, data); }
  deleteAccount(id) { return this.delete(`/accounts/${id}`); }
  accountOnline(id) { return this.post(`/accounts/${id}/online`); }
  accountOffline(id) { return this.post(`/accounts/${id}/offline`); }
  getAccountLogs(id, limit = 50) { return this.get(`/accounts/${id}/logs?limit=${limit}`); }

  // 跟圈任务
  getTasks(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.get(`/tasks/${qs ? '?' + qs : ''}`);
  }
  createTask(data) { return this.post('/tasks/', data); }
  updateTask(id, data) { return this.put(`/tasks/${id}`, data); }
  startTask(id) { return this.post(`/tasks/${id}/start`); }
  stopTask(id) { return this.post(`/tasks/${id}/stop`); }
  deleteTask(id) { return this.delete(`/tasks/${id}`); }
  getTaskLogs(id, limit = 50) { return this.get(`/tasks/${id}/logs?limit=${limit}`); }
  getTaskStats() { return this.get('/tasks/stats'); }

  // 管理员
  isAdmin() {
    const u = JSON.parse(localStorage.getItem('user') || '{}');
    return !!u.is_admin;
  }
  adminGetUsers(page = 1) { return this.get(`/admin/users?page=${page}&size=20`); }
  adminGetStats() { return this.get('/admin/stats'); }
  adminGetAccounts(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.get(`/admin/accounts/${qs ? '?' + qs : ''}`);
  }
  adminGetTasks(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.get(`/admin/tasks/${qs ? '?' + qs : ''}`);
  }
  adminToggleUser(userId) { return this.put(`/admin/users/${userId}/toggle`); }
}

const api = new ApiClient();
