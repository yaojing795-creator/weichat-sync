# 云端微信跟圈 SaaS 系统

> 微信朋友圈自动同步管理系统 - 原型版本 v1.0.0

## 系统架构

```
前端 (HTML/CSS/JS SPA) → FastAPI 后端 → SQLite 数据库
                              ↓
                        asyncio 同步调度器
                              ↓
                        微信模拟器 (WeChatSimulator)
```

## 功能清单

| 功能 | 状态 |
|------|------|
| 用户注册/登录 (JWT认证) | ✅ |
| 微信账号管理 (CRUD+上下线) | ✅ |
| 跟圈任务配置 (源好友ID+延迟) | ✅ |
| 自动转发 (文字/图片/视频) | ✅ |
| 多任务并行 (asyncio协程) | ✅ |
| 状态面板 (在线/转发/日志) | ✅ |
| 异常处理 (掉线告警+自动重连) | ✅ |
| 权限区分 (管理员/普通用户) | ✅ |

## 默认账号

- **管理员**: `admin` / `admin123`
- 首次登录后请立即修改密码

## 快速开始

```bash
cd backend
pip3 install -r ../requirements.txt
python3 main.py
```

访问 http://localhost:8765

## 部署到公网

### 方式一：Railway（最简单）
1. 将本仓库推送到 GitHub
2. 登录 https://railway.app
3. New Project → Deploy from GitHub repo
4. 添加环境变量 `JWT_SECRET=任意随机字符串`
5. 获得访问网址

### 方式二：Render
1. 推送到 GitHub
2. https://render.com → New Web Service
3. Build: `pip install -r requirements.txt`
4. Start: `python backend/main.py`
5. 环境变量 `PORT=8080`

### 方式三：Docker
```bash
docker build -t weichat-sync .
docker run -p 8765:8765 -e JWT_SECRET=your-secret weichat-sync
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户 |
| GET | `/api/accounts/` | 获取账号列表 |
| POST | `/api/accounts/` | 添加账号 |
| POST | `/api/accounts/{id}/online` | 账号上线 |
| POST | `/api/accounts/{id}/offline` | 账号下线 |
| GET | `/api/tasks/` | 获取任务列表 |
| POST | `/api/tasks/` | 创建任务 |
| POST | `/api/tasks/{id}/start` | 启动任务 |
| POST | `/api/tasks/{id}/stop` | 停止任务 |
| GET | `/api/tasks/stats` | 统计概览 |
| GET | `/api/admin/users` | 查看所有用户 (管理员) |
| GET | `/api/admin/stats` | 平台统计 (管理员) |

## 目录结构

```
weichat-sync/
├── backend/
│   ├── main.py              # FastAPI 主入口
│   ├── database.py          # SQLAlchemy 配置
│   ├── models.py            # 数据模型
│   ├── schemas.py           # Pydantic 模式
│   ├── auth.py              # JWT 认证
│   ├── routers/
│   │   ├── auth.py          # 认证路由
│   │   ├── accounts.py      # 账号管理
│   │   ├── tasks.py         # 跟圈任务
│   │   └── admin.py         # 管理员接口
│   └── services/
│       ├── wechat_service.py # 微信模拟器
│       └── sync_service.py   # 同步调度器
├── frontend/
│   ├── index.html           # 单页应用
│   ├── css/style.css        # 样式
│   └── js/                  # 前端逻辑
├── deploy.sh                # 一键启动脚本
├── requirements.txt
└── README.md
```

## ⚠️ 注意事项

1. 本系统为原型演示，微信服务使用模拟器
2. 实际生产需对接真实微信Hook协议或企业微信API
3. 逆向微信协议存在法律风险，请合规使用
