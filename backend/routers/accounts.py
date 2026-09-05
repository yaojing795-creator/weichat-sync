# -*- coding: utf-8 -*-
"""账号管理路由：增删改查微信账号"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import models
from database import get_db
from auth import get_current_user
from schemas import WeChatAccountCreate, WeChatAccountOut, WeChatAccountUpdate
from services.wechat_service import wechat_sim

router = APIRouter(prefix="/api/accounts", tags=["微信账号"])


@router.get("/", response_model=List[WeChatAccountOut])
def list_accounts(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户的所有微信账号"""
    accounts = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.user_id == current_user.id
    ).order_by(models.WeChatAccount.created_at.desc()).all()
    return accounts


@router.post("/", response_model=WeChatAccountOut)
def create_account(
    req: WeChatAccountCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加微信账号"""
    # 检查wxid是否已被当前用户或其他用户占用
    existing = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.wxid == req.wxid
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该微信ID已被添加")
    
    account = models.WeChatAccount(
        user_id=current_user.id,
        wxid=req.wxid,
        nickname=req.nickname,
        avatar_url=req.avatar_url,
        status="offline",
        created_at=datetime.utcnow(),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.put("/{account_id}", response_model=WeChatAccountOut)
def update_account(
    account_id: int,
    req: WeChatAccountUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新微信账号信息"""
    account = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.id == account_id,
        models.WeChatAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    if req.nickname is not None:
        account.nickname = req.nickname
    if req.avatar_url is not None:
        account.avatar_url = req.avatar_url
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除微信账号"""
    account = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.id == account_id,
        models.WeChatAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    db.delete(account)
    db.commit()
    return {"ok": True}


@router.post("/{account_id}/online")
def online_account(
    account_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """账号上线（模拟云端连接）"""
    account = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.id == account_id,
        models.WeChatAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    # 模拟启动云端会话
    session_id = wechat_sim.start_session(account_id, account.wxid)
    account.session_id = session_id
    account.status = "online"
    account.last_online = datetime.utcnow()
    account.error_msg = None
    db.commit()
    return {"ok": True, "session_id": session_id}


@router.post("/{account_id}/offline")
def offline_account(
    account_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """账号下线"""
    account = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.id == account_id,
        models.WeChatAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    if account.session_id:
        wechat_sim.stop_session(account.session_id)
    account.status = "offline"
    account.last_offline = datetime.utcnow()
    db.commit()
    return {"ok": True}


@router.get("/{account_id}/logs")
def get_account_logs(
    account_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """获取账号的转发日志"""
    account = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.id == account_id,
        models.WeChatAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    logs = db.query(models.ForwardLog).filter(
        models.ForwardLog.account_id == account_id
    ).order_by(models.ForwardLog.created_at.desc()).limit(limit).all()
    return logs
