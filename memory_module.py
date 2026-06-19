#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
记忆模块 - 用户画像和长期记忆
"""

import json
import os
from datetime import datetime
from collections import defaultdict

MEMORY_DIR = "memory_data"
USER_PROFILES_FILE = os.path.join(MEMORY_DIR, "user_profiles.json")
CONVERSATION_LOG_FILE = os.path.join(MEMORY_DIR, "conversation_log.json")


def ensure_memory_dir():
    """确保记忆目录存在"""
    os.makedirs(MEMORY_DIR, exist_ok=True)


def load_json(filepath: str) -> dict:
    """加载JSON文件"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_json(filepath: str, data: dict):
    """保存JSON文件"""
    ensure_memory_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========== 用户画像管理 ==========

def get_user_profile(user_id: str) -> dict:
    """获取用户画像"""
    profiles = load_json(USER_PROFILES_FILE)
    if user_id not in profiles:
        profiles[user_id] = {
            "user_id": user_id,
            "first_seen": datetime.now().isoformat(),
            "interaction_count": 0,
            "preferences": {},
            "topics_discussed": [],
            "tools_used": [],
            "last_active": None
        }
        save_json(USER_PROFILES_FILE, profiles)
    return profiles[user_id]


def update_user_profile(user_id: str, updates: dict):
    """更新用户画像"""
    profiles = load_json(USER_PROFILES_FILE)
    if user_id not in profiles:
        profiles[user_id] = {
            "user_id": user_id,
            "first_seen": datetime.now().isoformat(),
            "interaction_count": 0,
            "preferences": {},
            "topics_discussed": [],
            "tools_used": [],
            "last_active": None
        }
    
    profiles[user_id].update(updates)
    profiles[user_id]["last_active"] = datetime.now().isoformat()
    profiles[user_id]["interaction_count"] = profiles[user_id].get("interaction_count", 0) + 1
    
    save_json(USER_PROFILES_FILE, profiles)
    return profiles[user_id]


def add_topic(user_id: str, topic: str):
    """添加讨论话题"""
    profiles = load_json(USER_PROFILES_FILE)
    if user_id in profiles:
        topics = profiles[user_id].get("topics_discussed", [])
        if topic not in topics:
            topics.append(topic)
            # 只保留最近20个话题
            if len(topics) > 20:
                topics = topics[-20:]
            profiles[user_id]["topics_discussed"] = topics
            save_json(USER_PROFILES_FILE, profiles)


def add_tool_usage(user_id: str, tool_name: str):
    """记录工具使用"""
    profiles = load_json(USER_PROFILES_FILE)
    if user_id in profiles:
        tools = profiles[user_id].get("tools_used", [])
        tools.append({
            "tool": tool_name,
            "timestamp": datetime.now().isoformat()
        })
        # 只保留最近50次工具使用记录
        if len(tools) > 50:
            tools = tools[-50:]
        profiles[user_id]["tools_used"] = tools
        save_json(USER_PROFILES_FILE, profiles)


def set_preference(user_id: str, key: str, value: str):
    """设置用户偏好"""
    profiles = load_json(USER_PROFILES_FILE)
    if user_id in profiles:
        profiles[user_id]["preferences"][key] = value
        save_json(USER_PROFILES_FILE, profiles)


def get_preference(user_id: str, key: str, default: str = None) -> str:
    """获取用户偏好"""
    profiles = load_json(USER_PROFILES_FILE)
    if user_id in profiles:
        return profiles[user_id]["preferences"].get(key, default)
    return default


# ========== 对话历史管理 ==========

def log_conversation(user_id: str, user_message: str, ai_response: str, tools_used: list = None):
    """记录对话历史"""
    log = load_json(CONVERSATION_LOG_FILE)
    
    if user_id not in log:
        log[user_id] = []
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user_message": user_message,
        "ai_response": ai_response,
        "tools_used": tools_used or []
    }
    
    log[user_id].append(entry)
    
    # 只保留最近100条对话记录
    if len(log[user_id]) > 100:
        log[user_id] = log[user_id][-100:]
    
    save_json(CONVERSATION_LOG_FILE, log)


def get_conversation_summary(user_id: str, limit: int = 10) -> list:
    """获取最近对话摘要"""
    log = load_json(CONVERSATION_LOG_FILE)
    if user_id in log:
        return log[user_id][-limit:]
    return []


def get_user_stats(user_id: str) -> dict:
    """获取用户统计信息"""
    profile = get_user_profile(user_id)
    log = load_json(CONVERSATION_LOG_FILE)
    
    total_messages = len(log.get(user_id, []))
    tools_used = profile.get("tools_used", [])
    tool_counts = defaultdict(int)
    for tool_record in tools_used:
        tool_counts[tool_record["tool"]] += 1
    
    return {
        "user_id": user_id,
        "total_interactions": profile.get("interaction_count", 0),
        "total_messages": total_messages,
        "topics_discussed": profile.get("topics_discussed", []),
        "tools_used_summary": dict(tool_counts),
        "first_seen": profile.get("first_seen"),
        "last_active": profile.get("last_active")
    }


# ========== 个性化回复 ==========

def get_personalized_context(user_id: str) -> str:
    """获取个性化上下文，用于增强AI回复"""
    profile = get_user_profile(user_id)
    
    context_parts = []
    
    # 用户偏好
    preferences = profile.get("preferences", {})
    if preferences:
        pref_str = "、".join([f"{k}是{v}" for k, v in preferences.items()])
        context_parts.append(f"用户偏好：{pref_str}")
    
    # 常用话题
    topics = profile.get("topics_discussed", [])
    if topics:
        context_parts.append(f"用户常讨论的话题：{'、'.join(topics[-5:])}")
    
    # 常用工具
    tools = profile.get("tools_used", [])
    if tools:
        tool_names = list(set([t["tool"] for t in tools[-10:]]))
        context_parts.append(f"用户常用的功能：{'、'.join(tool_names)}")
    
    # 交互次数
    count = profile.get("interaction_count", 0)
    if count > 10:
        context_parts.append("这是一位活跃用户")
    
    if context_parts:
        return "【用户画像信息】\n" + "\n".join(context_parts)
    return ""


# ========== 工具定义 ==========
MEMORY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "set_user_preference",
            "description": "设置用户偏好，如喜欢的语言、回复风格、关注的话题等",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "偏好名称，如：语言、回复风格、关注领域"
                    },
                    "value": {
                        "type": "string",
                        "description": "偏好值"
                    }
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_profile_info",
            "description": "获取用户画像和统计信息",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_conversation_history",
            "description": "获取最近的对话历史",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回的对话数量，默认10"
                    }
                },
                "required": []
            }
        }
    }
]


def execute_memory_tool(tool_name: str, arguments: dict, user_id: str) -> str:
    """执行记忆相关工具"""
    try:
        if tool_name == "set_user_preference":
            key = arguments.get("key", "")
            value = arguments.get("value", "")
            set_preference(user_id, key, value)
            return json.dumps({
                "success": True,
                "message": f"已记录您的偏好：{key} = {value}"
            }, ensure_ascii=False)
        
        elif tool_name == "get_user_profile_info":
            stats = get_user_stats(user_id)
            return json.dumps(stats, ensure_ascii=False)
        
        elif tool_name == "get_conversation_history":
            limit = arguments.get("limit", 10)
            history = get_conversation_summary(user_id, limit)
            return json.dumps({
                "history": history,
                "total": len(history)
            }, ensure_ascii=False)
        
        else:
            return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"工具执行失败: {str(e)}"}, ensure_ascii=False)
