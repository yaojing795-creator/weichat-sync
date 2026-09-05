# -*- coding: utf-8 -*-
"""跟圈同步服务：监听源好友动态并定时转发"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

import models
from database import SessionLocal
from services.wechat_service import wechat_sim


class SyncTaskManager:
    """同步任务管理器（后台协程调度）"""
    
    def __init__(self):
        self._running_tasks: Dict[int, asyncio.Task] = {}
    
    async def start_task(self, task: models.FollowTask, db: Session):
        """启动跟圈任务"""
        if task.id in self._running_tasks:
            return
        task.is_running = True
        db.commit()
        coro = self._run_task_loop(task.id, db)
        self._running_tasks[task.id] = asyncio.create_task(coro)
    
    async def _run_task_loop(self, task_id: int, db: Session):
        """跟圈任务循环"""
        task = db.query(models.FollowTask).filter(models.FollowTask.id == task_id).first()
        if not task:
            return
        account = db.query(models.WeChatAccount).filter(models.WeChatAccount.id == task.account_id).first()
        if not account:
            return
        
        print(f"[跟圈服务] 任务 {task_id} 启动，监听 {task.source_wxid}")
        
        while task.is_running:
            try:
                # 1. 模拟获取源好友最新朋友圈
                post = await wechat_sim.simulate_friend_post(task.source_wxid)
                if not post:
                    await asyncio.sleep(30)
                    continue
                
                # 2. 防重复：1小时内已转发过则跳过
                existing = db.query(models.ForwardLog).filter(
                    models.ForwardLog.source_wxid == task.source_wxid,
                    models.ForwardLog.status == "success",
                    models.ForwardLog.created_at > datetime.utcnow() - timedelta(hours=1)
                ).first()
                if existing:
                    await asyncio.sleep(60)
                    continue
                
                # 3. 记录待转发
                log = models.ForwardLog(
                    user_id=task.user_id,
                    account_id=task.account_id,
                    task_id=task.id,
                    source_wxid=task.source_wxid,
                    content_type=post["media_types"][0] if post["media_types"] else "text",
                    content_summary=post["content"][:50] if post["content"] else "",
                    status="pending",
                    delay_applied=task.delay_seconds,
                    created_at=datetime.utcnow(),
                )
                db.add(log)
                db.commit()
                db.refresh(log)
                
                # 4. 应用延迟后转发
                if task.delay_seconds > 0:
                    await asyncio.sleep(task.delay_seconds)
                
                # 5. 执行转发
                result = await wechat_sim.simulate_forward(account.wxid, post)
                
                if result["success"]:
                    log.status = "success"
                    log.finished_at = datetime.utcnow()
                    task.total_forwarded += 1
                else:
                    log.status = "failed"
                    log.error_msg = result.get("error", "未知错误")
                    log.finished_at = datetime.utcnow()
                    task.total_failed += 1
                
                db.commit()
                task.last_sync_time = datetime.utcnow()
                db.commit()
                
                await asyncio.sleep(random.randint(60, 180))
                
            except asyncio.CancelledError:
                print(f"[跟圈服务] 任务 {task_id} 被取消")
                break
            except Exception as e:
                print(f"[跟圈服务] 任务 {task_id} 异常: {e}")
                await asyncio.sleep(30)
        
        print(f"[跟圈服务] 任务 {task_id} 已停止")
    
    async def stop_task(self, task_id: int, db: Session):
        """停止跟圈任务"""
        task = db.query(models.FollowTask).filter(models.FollowTask.id == task_id).first()
        if not task:
            return
        task.is_running = False
        db.commit()
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()
            del self._running_tasks[task_id]
    
    def get_running_count(self) -> int:
        return len(self._running_tasks)
    
    async def shutdown_all(self, db: Optional[Session] = None):
        """关闭所有任务"""
        if db:
            tasks = db.query(models.FollowTask).filter(models.FollowTask.is_running == True).all()
            for task in tasks:
                await self.stop_task(task.id, db)
        print("[跟圈服务] 所有任务已停止")


sync_manager = SyncTaskManager()


async def start_all_running_tasks():
    """服务启动时恢复所有运行中的任务"""
    db = SessionLocal()
    try:
        tasks = db.query(models.FollowTask).filter(
            models.FollowTask.is_enabled == True,
            models.FollowTask.is_running == True
        ).all()
        for task in tasks:
            await sync_manager.start_task(task, db)
        print(f"[跟圈服务] 恢复了 {len(tasks)} 个运行中的任务")
    finally:
        db.close()
