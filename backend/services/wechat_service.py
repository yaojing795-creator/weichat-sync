# -*- coding: utf-8 -*-
"""微信服务模块
注：本模块为原型演示，模拟微信客户端行为。
实际生产环境需要对接微信Hook协议或企业微信API。
"""
import asyncio
import random
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

import models
from database import engine


class WeChatSimulator:
    """微信模拟器（原型用）"""
    
    # 模拟好友数据池
    _FAKE_FRIENDS = [
        {"wxid": "wx_friend_001", "nickname": "张三"},
        {"wxid": "wx_friend_002", "nickname": "李四"},
        {"wxid": "wx_friend_003", "nickname": "王五"},
        {"wxid": "wx_friend_004", "nickname": "赵六"},
        {"wxid": "wx_friend_005", "nickname": "朋友圈活跃用户"},
    ]
    
    # 模拟动态内容
    _FAKE_POSTS = [
        {"content": "今天天气真好，出去散散步~", "has_media": False},
        {"content": "分享一张美景", "has_media": True, "media_types": ["image"]},
        {"content": "美食打卡", "has_media": True, "media_types": ["image", "image"]},
        {"content": "生活碎片📸", "has_media": True, "media_types": ["image"]},
        {"content": "转发一篇好文章", "has_media": False},
        {"content": "周末出游记录", "has_media": True, "media_types": ["image", "image", "image"]},
        {"content": "一段有趣的视频分享", "has_media": True, "media_types": ["video"]},
        {"content": "今日感悟：坚持就是胜利💪", "has_media": False},
    ]
    
    def __init__(self):
        self._sessions: Dict[str, Dict] = {}  # session_id -> session info
    
    def start_session(self, account_id: int, wxid: str) -> str:
        """启动云端会话（模拟登录）"""
        session_id = f"session_{account_id}_{int(datetime.now().timestamp())}"
        self._sessions[session_id] = {
            "account_id": account_id,
            "wxid": wxid,
            "status": "online",
            "connected_at": datetime.utcnow(),
        }
        return session_id
    
    def stop_session(self, session_id: str) -> bool:
        """停止会话（模拟下线）"""
        if session_id in self._sessions:
            self._sessions[session_id]["status"] = "offline"
            self._sessions[session_id]["disconnected_at"] = datetime.utcnow()
            return True
        return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        return self._sessions.get(session_id)
    
    async def simulate_friend_post(self, source_wxid: str) -> Optional[Dict]:
        """模拟好友发布朋友圈"""
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # 随机选择动态内容
        post_template = random.choice(self._FAKE_POSTS)
        post_id = f"post_{source_wxid}_{int(datetime.now().timestamp())}_{random.randint(1000,9999)}"
        
        # 生成模拟媒体URL
        media_urls = []
        if post_template.get("has_media"):
            for mt in post_template.get("media_types", []):
                if mt == "image":
                    media_urls.append(f"https://fake-cdn.example.com/img/{post_id}_{random.randint(1,9)}.jpg")
                elif mt == "video":
                    media_urls.append(f"https://fake-cdn.example.com/vid/{post_id}.mp4")
        
        return {
            "post_id": post_id,
            "wxid": source_wxid,
            "content": post_template["content"],
            "media_urls": media_urls,
            "media_types": post_template.get("media_types", []),
            "publish_time": datetime.utcnow(),
        }
    
    async def simulate_forward(self, account_wxid: str, post: Dict) -> Dict:
        """模拟转发朋友圈"""
        await asyncio.sleep(random.uniform(0.2, 0.8))
        
        # 模拟成功率 95%
        success = random.random() < 0.95
        return {
            "success": success,
            "post_id": post["post_id"],
            "error": None if success else "模拟接口超时",
        }
    
    def get_all_sessions(self) -> List[Dict]:
        """获取所有会话"""
        return list(self._sessions.values())


# 全局模拟器实例
wechat_sim = WeChatSimulator()


def init_default_admin(db: Session):
    """初始化默认管理员账号"""
    from auth import hash_password
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        admin = models.User(
            username="admin",
            password_hash=hash_password("admin123"),
            email="admin@weichat.local",
            is_admin=True,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"[初始化] 默认管理员账号已创建: admin / admin123")
