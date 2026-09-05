# 云端微信跟圈 SaaS 原型系统

> 微信朋友圈自动同步管理系统 - 原型版本 v1.0.0

## 📋 功能清单

| 功能模块 | 说明 |
|---------|------|
| 用户注册登录 | JWT 认证，密码 bcrypt 加密 |
| 账号管理 | 批量添加微信账号，云端托管上下线 |
| 跟圈配置 | 设置源好友ID，监听朋友圈动态 |
| 自动转发 | 文字/图片/视频自动抓取并转发 |
| 延时转发 | 支持 0-300 秒自定义延迟 |
| 多任务并行 | 多账号同时跟圈，互不干扰 |
| 状态面板 | 在线状态、转发记录、报错日志 |
| 异常处理 | 掉线告警 + 自动重连机制 |
| 权限区分 | 普通用户 / 管理员双角色 |

## 🏗 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    前端 (HTML/CSS/JS)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ 仪表盘   │  │ 账号管理 │  │ 跟圈任务 │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│  ┌──────────┐  ┌──────────┐                        │
│  │ 转发日志 │  │ 系统管理 │ (管理员)                │
│  └──────────┘  └──────────┘                        │
└─────────────────────────────────────────────────────┘
                         │
                         ▼ HTTPS/WebSocket
┌─────────────────────────────────────────────────────┐
│              FastAPI 后端 (Python)                   │
│  ┌─────────────┐  ┌─────────────┐                  │
│  │  REST API   │  │  定时调度器  │                  │
│  │  /api/auth  │  │  心跳巡检    │                  │
│  │  /api/tasks │  │  任务管理    │                  │
│  │  /api/admin │  │  异常告警    │                  │
│  └─────────────┘  └─────────────┘                  │
└─────────────────────────────────────────────────────┘
                         │
                         ▼ SQLAlchemy ORM
┌─────────────────────────────────────────────────────┐
│                  SQLite 数据库                       │
│  users | wechat_accounts | follow_tasks             │
│  forward_logs | system_logs | wechat_posts          │
└─────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 方式一：一键启动（推荐）
```bash
cd weichat-sync
chmod +x deploy.sh
./deploy.sh
```

### 方式二：手动启动
```bash
cd backend
pip3 install -r requirements.txt
python3 main.py
```

### 访问地址
- 本地访问: http://localhost:8765
- 默认管理员: `admin` / `admin123`

## 📁 项目结构

```
weichat-sync/
├── backend/
│   ├── main.py              # 服务入口
│   ├── database.py          # 数据库连接
│   ├── models.py            # 数据模型
│   ├── schemas.py           # API 数据模式
│   ├── auth.py              # 认证工具（纯标准库 JWT）
│   ├── routers/
│   │   ├── auth.py          # 注册/登录接口
│   │   ├── accounts.py      # 账号 CRUD + 上下线
│   │   ├── tasks.py         # 跟圈任务管理
│   │   └── admin.py         # 管理员接口
│   └── services/
│       ├── wechat_service.py # 微信模拟器
│       └── sync_service.py   # 同步任务调度器
├── frontend/
│   ├── index.html           # 单页应用主页面
│   ├── css/style.css        # 样式
│   └── js/
│       ├── api.js           # API 客户端封装
│       ├── utils.js         # 工具函数
│       └── pages/
│           ├── dashboard.js
│           ├── accounts.js
│           ├── tasks.js
│           └── admin.js
├── deploy.sh                # 一键部署脚本
└── README.md               # 本文档
```

## 🔌 API 接口说明

### 认证接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户 |

### 账号管理接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/accounts/` | 获取账号列表 |
| POST | `/api/accounts/` | 添加账号 |
| PUT | `/api/accounts/{id}` | 更新账号 |
| DELETE | `/api/accounts/{id}` | 删除账号 |
| POST | `/api/accounts/{id}/online` | 账号上线 |
| POST | `/api/accounts/{id}/offline` | 账号下线 |
| GET | `/api/accounts/{id}/logs` | 获取转发日志 |

### 跟圈任务接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks/` | 获取任务列表 |
| POST | `/api/tasks/` | 创建任务 |
| PUT | `/api/tasks/{id}` | 更新任务 |
| POST | `/api/tasks/{id}/start` | 启动任务 |
| POST | `/api/tasks/{id}/stop` | 停止任务 |
| DELETE | `/api/tasks/{id}` | 删除任务 |
| GET | `/api/tasks/{id}/logs` | 获取任务日志 |
| GET | `/api/tasks/stats` | 获取统计 |

### 管理员接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/users` | 查看所有用户 |
| GET | `/api/admin/stats` | 平台统计 |
| GET | `/api/admin/accounts` | 所有账号 |
| GET | `/api/admin/tasks` | 所有任务 |
| PUT | `/api/admin/users/{id}/toggle` | 启用/禁用用户 |

## 🔐 环境变量

```bash
export JWT_SECRET="your-secret-key"  # JWT密钥
export PORT=8765                      # 服务端口
export DB_PATH="/path/to/db.db"       # 数据库路径
```

## ⚠️ 注意事项

1. 本系统为**原型演示**，微信服务部分使用模拟器
2. 实际生产需对接真实微信Hook协议或企业微信API
3. 逆向微信协议存在法律风险，请合规使用
4. 默认管理员账号：`admin` / `admin123`，首次登录后请立即修改密码
