# -*- coding: utf-8 -*-
"""管理员路由：查看全平台数据、管理用户"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

import models
from database import get_db
from auth import require_admin
from schemas import WeChatAccountOut, FollowTaskOut, ForwardLogOut, SystemLogOut, UserOut

router = APIRouter(prefix="/api/admin", tags=["管理员"])


@router.get("/users", response_model=List[UserOut])
def list_all_users(
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 20
):
    """管理员查看用户列表"""
    offset = (page - 1) * size
    users = db.query(models.User).order_by(models.User.created_at.desc()).offset(offset).limit(size).all()
    return users


@router.get("/stats")
def get_platform_stats(
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员查看平台整体统计"""
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_users = db.query(models.User).filter(models.User.is_active == True).count()
    total_accounts = db.query(models.WeChatAccount).count()
    online_accounts = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.status == "online"
    ).count()
    total_tasks = db.query(models.FollowTask).count()
    running_tasks = db.query(models.FollowTask).filter(
        models.FollowTask.is_running == True
    ).count()
    
    today_forwards = db.query(models.ForwardLog).filter(
        models.ForwardLog.created_at >= today
    ).count()
    today_success = db.query(models.ForwardLog).filter(
        models.ForwardLog.status == "success",
        models.ForwardLog.created_at >= today
    ).count()
    today_failed = db.query(models.ForwardLog).filter(
        models.ForwardLog.status == "failed",
        models.ForwardLog.created_at >= today
    ).count()
    
    return {
        "total_users": total_users,
        "total_accounts": total_accounts,
        "online_accounts": online_accounts,
        "total_tasks": total_tasks,
        "running_tasks": running_tasks,
        "today_forwards": today_forwards,
        "today_success": today_success,
        "today_failed": today_failed,
    }


@router.get("/accounts", response_model=List[WeChatAccountOut])
def list_all_accounts(
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    page: int = 1,
    size: int = 50
):
    """管理员查看账号列表"""
    query = db.query(models.WeChatAccount)
    if user_id is not None:
        query = query.filter(models.WeChatAccount.user_id == user_id)
    if status_filter in ("online", "offline"):
        query = query.filter(models.WeChatAccount.status == status_filter)
    
    offset = (page - 1) * size
    accounts = query.order_by(models.WeChatAccount.created_at.desc()).offset(offset).limit(size).all()
    return accounts


@router.get("/tasks", response_model=List[FollowTaskOut])
def list_all_tasks(
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    page: int = 1,
    size: int = 50
):
    """管理员查看任务列表"""
    query = db.query(models.FollowTask)
    if user_id is not None:
        query = query.filter(models.FollowTask.user_id == user_id)
    
    offset = (page - 1) * size
    tasks = query.order_by(models.FollowTask.created_at.desc()).offset(offset).limit(size).all()
    return tasks


@router.get("/logs", response_model=List[SystemLogOut])
def list_system_logs(
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
    level: Optional[str] = None,
    module: Optional[str] = None,
    page: int = 1,
    size: int = 50
):
    """管理员查看系统日志"""
    query = db.query(models.SystemLog)
    if level:
        query = query.filter(models.SystemLog.level == level)
    if module:
        query = query.filter(models.SystemLog.module == module)
    
    offset = (page - 1) * size
    logs = query.order_by(models.SystemLog.created_at.desc()).offset(offset).limit(size).all()
    return logs


@router.put("/users/{user_id}/toggle")
def toggle_user_status(
    user_id: int,
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员启用/禁用用户"""
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能操作自己")
    
    target.is_active = not target.is_active
    db.commit()
    return {"ok": True, "is_active": target.is_active}
