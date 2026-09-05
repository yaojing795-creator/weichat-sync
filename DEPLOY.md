# 云端微信跟圈 SaaS - 部署指南

## 一、本地运行（开发测试）

### 前置要求
- Python 3.8+
- pip 包管理器

### 快速启动
```bash
cd weichat-sync
./deploy.sh
```
访问 http://localhost:8765
- 管理员账号: `admin` / `admin123`

---

## 二、部署到 Railway（推荐，免费额度）

### 步骤
1. 登录 https://railway.app
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择本项目的 GitHub 仓库（需先推送到 GitHub）
4. Railway 会自动检测 Python 项目并部署

### 环境变量配置
在 Railway Dashboard 中添加：
```
PORT=8080
JWT_SECRET=your-random-secret-key-here
```

### 获取访问地址
部署完成后，Railway 会分配一个类似 `https://weichat-sync-xxxx.up.railway.app` 的地址。

---

## 三、部署到 Render（免费）

### 步骤
1. 登录 https://render.com
2. 点击 "New +" → "Web Service"
3. 连接 GitHub 仓库
4. 配置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python backend/main.py`
   - Environment: Python 3
5. 添加环境变量 `PORT=8080`

### 获取访问地址
部署后获得类似 `https://weichat-sync.onrender.com` 的网址。

---

## 四、部署到 Vercel（需配合 Serverless）

Vercel 更适合静态前端，本后端需改用 Serverless 函数。适合想快速展示前端的场景。

---

## 五、部署到腾讯云/阿里云（生产环境）

### 使用 Docker 部署
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8765
CMD ["python", "backend/main.py"]
```

### 服务器要求
- 2核4G以上
- Ubuntu 20.04+
- 开通防火墙端口 8765

### nginx 反向代理配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 六、上线后的账号信息

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |

⚠️ **首次登录后请立即修改管理员密码！**

---

## 七、注意事项

1. **本系统为原型演示**，微信服务部分使用模拟器，实际对接需接入真实微信Hook协议
2. **逆向微信协议存在法律风险**，请确保合规使用
3. 生产环境建议更换 JWT_SECRET 为强随机字符串
4. 定期备份 SQLite 数据库文件
