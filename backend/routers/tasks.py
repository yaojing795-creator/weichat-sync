# -*- coding: utf-8 -*-
"""跟圈任务路由：创建、管理、状态查询"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

import models
from database import get_db
from auth import get_current_user
from schemas import FollowTaskCreate, FollowTaskOut, ForwardLogOut
from services.sync_service import sync_manager

router = APIRouter(prefix="/api/tasks", tags=["跟圈任务"])


@router.get("/", response_model=List[FollowTaskOut])
def list_tasks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    account_id: Optional[int] = None,
    status_filter: Optional[str] = Query(None, alias="status")
):
    """获取当前用户的跟圈任务列表"""
    query = db.query(models.FollowTask).filter(
        models.FollowTask.user_id == current_user.id
    )
    if account_id is not None:
        query = query.filter(models.FollowTask.account_id == account_id)
    if status_filter == "running":
        query = query.filter(models.FollowTask.is_running == True)
    elif status_filter == "stopped":
        query = query.filter(models.FollowTask.is_running == False)
    
    tasks = query.order_by(models.FollowTask.created_at.desc()).all()
    return tasks


@router.post("/", response_model=FollowTaskOut)
def create_task(
    req: FollowTaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建跟圈任务"""
    # 验证账号属于当前用户
    account = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.id == req.account_id,
        models.WeChatAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="目标账号不存在或无权限")
    
    # 检查是否已有相同源的重复任务
    existing = db.query(models.FollowTask).filter(
        models.FollowTask.user_id == current_user.id,
        models.FollowTask.account_id == req.account_id,
        models.FollowTask.source_wxid == req.source_wxid
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该源好友已在当前账号上存在跟圈任务")
    
    task = models.FollowTask(
        user_id=current_user.id,
        account_id=req.account_id,
        source_wxid=req.source_wxid,
        source_nickname=req.source_nickname,
        delay_seconds=req.delay_seconds,
        is_enabled=True,
        is_running=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=FollowTaskOut)
def update_task(
    task_id: int,
    req: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新跟圈任务配置"""
    task = db.query(models.FollowTask).filter(
        models.FollowTask.id == task_id,
        models.FollowTask.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if "is_enabled" in req:
        task.is_enabled = bool(req["is_enabled"])
    if "delay_seconds" in req:
        delay = int(req["delay_seconds"])
        if 0 <= delay <= 300:
            task.delay_seconds = delay
    if "source_nickname" in req:
        task.source_nickname = req["source_nickname"]
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/start")
def start_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """启动跟圈任务"""
    task = db.query(models.FollowTask).filter(
        models.FollowTask.id == task_id,
        models.FollowTask.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.is_running:
        return {"ok": True, "message": "任务已在运行中"}
    
    # 检查账号是否在线
    account = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.id == task.account_id
    ).first()
    if not account or account.status != "online":
        raise HTTPException(status_code=400, detail="目标账号未在线，请先让账号上线")
    
    import asyncio
    asyncio.create_task(sync_manager.start_task(task, db))
    return {"ok": True}


@router.post("/{task_id}/stop")
def stop_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """停止跟圈任务"""
    task = db.query(models.FollowTask).filter(
        models.FollowTask.id == task_id,
        models.FollowTask.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    import asyncio
    asyncio.create_task(sync_manager.stop_task(task_id, db))
    return {"ok": True}


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除跟圈任务"""
    task = db.query(models.FollowTask).filter(
        models.FollowTask.id == task_id,
        models.FollowTask.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.is_running:
        import asyncio
        asyncio.create_task(sync_manager.stop_task(task_id, db))
    
    db.delete(task)
    db.commit()
    return {"ok": True}


@router.get("/{task_id}/logs", response_model=List[ForwardLogOut])
def get_task_logs(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """获取任务的转发日志"""
    task = db.query(models.FollowTask).filter(
        models.FollowTask.id == task_id,
        models.FollowTask.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    logs = db.query(models.ForwardLog).filter(
        models.ForwardLog.task_id == task_id
    ).order_by(models.ForwardLog.created_at.desc()).limit(limit).all()
    return logs


@router.get("/stats")
def get_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的统计概览"""
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 账号统计
    total_accounts = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.user_id == current_user.id
    ).count()
    online_accounts = db.query(models.WeChatAccount).filter(
        models.WeChatAccount.user_id == current_user.id,
        models.WeChatAccount.status == "online"
    ).count()
    offline_accounts = total_accounts - online_accounts
    
    # 任务统计
    total_tasks = db.query(models.FollowTask).filter(
        models.FollowTask.user_id == current_user.id
    ).count()
    running_tasks = db.query(models.FollowTask).filter(
        models.FollowTask.user_id == current_user.id,
        models.FollowTask.is_running == True
    ).count()
    
    # 今日转发统计
    today_forwards = db.query(models.ForwardLog).filter(
        models.ForwardLog.user_id == current_user.id,
        models.ForwardLog.created_at >= today
    ).count()
    today_success = db.query(models.ForwardLog).filter(
        models.ForwardLog.user_id == current_user.id,
        models.ForwardLog.status == "success",
        models.ForwardLog.created_at >= today
    ).count()
    today_failed = db.query(models.ForwardLog).filter(
        models.ForwardLog.user_id == current_user.id,
        models.ForwardLog.status == "failed",
        models.ForwardLog.created_at >= today
    ).count()
    
    return {
        "total_accounts": total_accounts,
        "online_accounts": online_accounts,
        "offline_accounts": offline_accounts,
        "total_tasks": total_tasks,
        "running_tasks": running_tasks,
        "today_forwards": today_forwards,
        "today_success": today_success,
        "today_failed": today_failed,
    }
