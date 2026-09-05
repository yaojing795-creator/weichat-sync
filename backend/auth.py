# -*- coding: utf-8 -*-
"""认证工具模块：密码加密、JWT令牌生成与验证（纯标准库实现）"""
import os
import hashlib
import hmac
import json
import base64
import time
from datetime import datetime, timedelta
from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import models
from database import get_db

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET", "weichat-sync-dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天有效期

security = HTTPBearer()


def _b64url_encode(data: bytes) -> str:
    """Base64URL 编码（无填充）"""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def _b64url_decode(s: str) -> bytes:
    """Base64URL 解码（补填充）"""
    s = s.replace('-', '+').replace('_', '/')
    padding = 4 - len(s) % 4
    if padding != 4:
        s += '=' * padding
    return base64.b64decode(s)


def hash_password(password: str) -> str:
    """密码加密（bcrypt）"""
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    import bcrypt
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """生成JWT访问令牌（纯标准库实现）"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode["exp"] = int(expire.timestamp())
    to_encode["iat"] = int(datetime.utcnow().timestamp())
    
    header = _b64url_encode(json.dumps({"alg": ALGORITHM, "typ": "JWT"}, separators=(',', ':')).encode())
    payload = _b64url_encode(json.dumps(to_encode, separators=(',', ':')).encode())
    signature = _b64url_encode(hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


def decode_access_token(token: str) -> dict:
    """解码并验证JWT令牌"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        
        header, payload_b64, signature = parts
        
        # 验证签名
        expected_sig = _b64url_encode(hmac.new(SECRET_KEY.encode(), f"{header}.{payload_b64}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(expected_sig, signature):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="签名验证失败")
        
        payload = json.loads(_b64url_decode(payload_b64))
        
        # 检查过期时间
        if payload.get("exp", 0) < int(datetime.utcnow().timestamp()):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌已过期")
        
        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """获取当前登录用户"""
    payload = decode_access_token(credentials.credentials)
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未授权")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    return user


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    """要求管理员权限"""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return current_user
