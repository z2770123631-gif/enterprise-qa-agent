#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
流程自动化模块 - 审批流程、定时任务、异常处理
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

WORKFLOW_DIR = "workflow_data"
WORKFLOW_FILE = os.path.join(WORKFLOW_DIR, "workflows.json")
TASK_FILE = os.path.join(WORKFLOW_DIR, "tasks.json")
NOTIFICATION_FILE = os.path.join(WORKFLOW_DIR, "notifications.json")


def ensure_workflow_dir():
    """确保工作流目录存在"""
    os.makedirs(WORKFLOW_DIR, exist_ok=True)


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
    ensure_workflow_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========== 审批流程管理 ==========

def create_approval_workflow(
    title: str,
    requester: str,
    workflow_type: str,
    description: str,
    approvers: List[str],
    data: dict = None
) -> dict:
    """创建审批流程"""
    workflows = load_json(WORKFLOW_FILE)
    
    workflow_id = f"WF{len(workflows) + 1:04d}"
    
    workflow = {
        "id": workflow_id,
        "title": title,
        "requester": requester,
        "type": workflow_type,
        "description": description,
        "approvers": approvers,
        "current_approver_index": 0,
        "status": "待审批",
        "data": data or {},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "history": [
            {
                "action": "创建",
                "user": requester,
                "timestamp": datetime.now().isoformat(),
                "comment": "提交审批申请"
            }
        ]
    }
    
    workflows[workflow_id] = workflow
    save_json(WORKFLOW_FILE, workflows)
    
    # 创建通知
    if approvers:
        create_notification(
            user_id=approvers[0],
            title=f"新审批待处理: {title}",
            content=f"{requester} 提交了 {workflow_type} 审批申请，请及时处理。",
            related_id=workflow_id
        )
    
    return {
        "success": True,
        "workflow_id": workflow_id,
        "message": f"审批流程已创建，等待 {approvers[0]} 审批"
    }


def approve_workflow(workflow_id: str, approver: str, comment: str = "") -> dict:
    """审批通过"""
    workflows = load_json(WORKFLOW_FILE)
    
    if workflow_id not in workflows:
        return {"success": False, "message": f"未找到流程 {workflow_id}"}
    
    workflow = workflows[workflow_id]
    
    if workflow["status"] != "待审批":
        return {"success": False, "message": f"流程状态不是待审批，当前状态: {workflow['status']}"}
    
    current_index = workflow["current_approver_index"]
    if workflow["approvers"][current_index] != approver:
        return {"success": False, "message": f"当前审批人不是 {approver}"}
    
    # 记录审批历史
    workflow["history"].append({
        "action": "审批通过",
        "user": approver,
        "timestamp": datetime.now().isoformat(),
        "comment": comment or "审批通过"
    })
    
    # 检查是否还有下一个审批人
    if current_index + 1 < len(workflow["approvers"]):
        workflow["current_approver_index"] = current_index + 1
        next_approver = workflow["approvers"][current_index + 1]
        
        # 通知下一个审批人
        create_notification(
            user_id=next_approver,
            title=f"审批待处理: {workflow['title']}",
            content=f"{approver} 已审批通过，请您继续审批。",
            related_id=workflow_id
        )
        
        workflow["updated_at"] = datetime.now().isoformat()
        save_json(WORKFLOW_FILE, workflows)
        
        return {
            "success": True,
            "message": f"审批通过，已转交 {next_approver} 继续审批"
        }
    else:
        # 所有审批人已通过
        workflow["status"] = "已批准"
        workflow["updated_at"] = datetime.now().isoformat()
        save_json(WORKFLOW_FILE, workflows)
        
        # 通知申请人
        create_notification(
            user_id=workflow["requester"],
            title=f"审批已通过: {workflow['title']}",
            content=f"您的 {workflow['type']} 申请已全部审批通过。",
            related_id=workflow_id
        )
        
        return {
            "success": True,
            "message": "审批流程已完成，申请已批准"
        }


def reject_workflow(workflow_id: str, approver: str, reason: str) -> dict:
    """审批驳回"""
    workflows = load_json(WORKFLOW_FILE)
    
    if workflow_id not in workflows:
        return {"success": False, "message": f"未找到流程 {workflow_id}"}
    
    workflow = workflows[workflow_id]
    
    if workflow["status"] != "待审批":
        return {"success": False, "message": f"流程状态不是待审批"}
    
    workflow["status"] = "已驳回"
    workflow["history"].append({
        "action": "审批驳回",
        "user": approver,
        "timestamp": datetime.now().isoformat(),
        "comment": reason
    })
    workflow["updated_at"] = datetime.now().isoformat()
    save_json(WORKFLOW_FILE, workflows)
    
    # 通知申请人
    create_notification(
        user_id=workflow["requester"],
        title=f"审批被驳回: {workflow['title']}",
        content=f"您的 {workflow['type']} 申请被驳回，原因: {reason}",
        related_id=workflow_id
    )
    
    return {
        "success": True,
        "message": f"审批已驳回，原因: {reason}"
    }


def query_workflows(
    requester: str = None,
    approver: str = None,
    status: str = None,
    workflow_type: str = None
) -> dict:
    """查询审批流程"""
    workflows = load_json(WORKFLOW_FILE)
    
    results = []
    for wf_id, wf in workflows.items():
        if requester and wf["requester"] != requester:
            continue
        if approver and approver not in wf["approvers"]:
            continue
        if status and wf["status"] != status:
            continue
        if workflow_type and wf["type"] != workflow_type:
            continue
        results.append({"id": wf_id, **wf})
    
    return {
        "found": len(results) > 0,
        "workflows": results,
        "total": len(results)
    }


# ========== 定时任务管理 ==========

def create_scheduled_task(
    title: str,
    task_type: str,
    schedule: str,
    action: str,
    created_by: str,
    params: dict = None
) -> dict:
    """创建定时任务"""
    tasks = load_json(TASK_FILE)
    
    task_id = f"TASK{len(tasks) + 1:04d}"
    
    task = {
        "id": task_id,
        "title": title,
        "type": task_type,
        "schedule": schedule,
        "action": action,
        "params": params or {},
        "created_by": created_by,
        "status": "活跃",
        "last_run": None,
        "next_run": calculate_next_run(schedule),
        "run_count": 0,
        "created_at": datetime.now().isoformat()
    }
    
    tasks[task_id] = task
    save_json(TASK_FILE, tasks)
    
    return {
        "success": True,
        "task_id": task_id,
        "message": f"定时任务已创建，下次执行: {task['next_run']}"
    }


def calculate_next_run(schedule: str) -> str:
    """计算下次执行时间"""
    now = datetime.now()
    
    if schedule == "每天":
        next_run = now + timedelta(days=1)
        next_run = next_run.replace(hour=9, minute=0, second=0)
    elif schedule == "每周一":
        days_ahead = 7 - now.weekday()
        if days_ahead == 0:
            days_ahead = 7
        next_run = now + timedelta(days=days_ahead)
        next_run = next_run.replace(hour=9, minute=0, second=0)
    elif schedule == "每月1号":
        if now.day == 1:
            next_run = now.replace(day=1) + timedelta(days=32)
            next_run = next_run.replace(day=1, hour=9, minute=0, second=0)
        else:
            next_run = now.replace(day=1) + timedelta(days=32)
            next_run = next_run.replace(day=1, hour=9, minute=0, second=0)
    else:
        next_run = now + timedelta(hours=1)
    
    return next_run.isoformat()


def query_tasks(created_by: str = None, status: str = None) -> dict:
    """查询定时任务"""
    tasks = load_json(TASK_FILE)
    
    results = []
    for task_id, task in tasks.items():
        if created_by and task["created_by"] != created_by:
            continue
        if status and task["status"] != status:
            continue
        results.append({"id": task_id, **task})
    
    return {
        "found": len(results) > 0,
        "tasks": results,
        "total": len(results)
    }


def update_task(task_id: str, updates: dict) -> dict:
    """更新定时任务"""
    tasks = load_json(TASK_FILE)
    
    if task_id not in tasks:
        return {"success": False, "message": f"未找到任务 {task_id}"}
    
    tasks[task_id].update(updates)
    save_json(TASK_FILE, tasks)
    
    return {"success": True, "message": "任务已更新"}


# ========== 通知管理 ==========

def create_notification(user_id: str, title: str, content: str, related_id: str = None) -> dict:
    """创建通知"""
    notifications = load_json(NOTIFICATION_FILE)
    
    if user_id not in notifications:
        notifications[user_id] = []
    
    notification = {
        "id": f"NOTIF{len(notifications[user_id]) + 1:04d}",
        "title": title,
        "content": content,
        "related_id": related_id,
        "read": False,
        "created_at": datetime.now().isoformat()
    }
    
    notifications[user_id].append(notification)
    
    # 只保留最近100条通知
    if len(notifications[user_id]) > 100:
        notifications[user_id] = notifications[user_id][-100:]
    
    save_json(NOTIFICATION_FILE, notifications)
    
    return {"success": True, "notification_id": notification["id"]}


def get_notifications(user_id: str, unread_only: bool = False) -> dict:
    """获取通知"""
    notifications = load_json(NOTIFICATION_FILE)
    
    if user_id not in notifications:
        return {"found": False, "notifications": [], "total": 0}
    
    user_notifications = notifications[user_id]
    
    if unread_only:
        user_notifications = [n for n in user_notifications if not n["read"]]
    
    return {
        "found": len(user_notifications) > 0,
        "notifications": user_notifications,
        "total": len(user_notifications),
        "unread_count": len([n for n in user_notifications if not n["read"]])
    }


def mark_notification_read(user_id: str, notification_id: str) -> dict:
    """标记通知已读"""
    notifications = load_json(NOTIFICATION_FILE)
    
    if user_id not in notifications:
        return {"success": False, "message": "用户没有通知"}
    
    for notif in notifications[user_id]:
        if notif["id"] == notification_id:
            notif["read"] = True
            save_json(NOTIFICATION_FILE, notifications)
            return {"success": True, "message": "通知已标记为已读"}
    
    return {"success": False, "message": f"未找到通知 {notification_id}"}


# ========== 异常告警 ==========

def create_alert(
    alert_type: str,
    title: str,
    description: str,
    severity: str,
    related_data: dict = None
) -> dict:
    """创建异常告警"""
    alert_file = os.path.join(WORKFLOW_DIR, "alerts.json")
    alerts = load_json(alert_file)
    
    alert_id = f"ALERT{len(alerts) + 1:04d}"
    
    alert = {
        "id": alert_id,
        "type": alert_type,
        "title": title,
        "description": description,
        "severity": severity,  # 低、中、高、紧急
        "status": "未处理",
        "related_data": related_data or {},
        "created_at": datetime.now().isoformat(),
        "resolved_at": None
    }
    
    alerts[alert_id] = alert
    save_json(alert_file, alerts)
    
    # 通知相关人员
    if severity in ["高", "紧急"]:
        # 通知管理员
        create_notification(
            user_id="admin",
            title=f"[{severity}级告警] {title}",
            content=description,
            related_id=alert_id
        )
    
    return {
        "success": True,
        "alert_id": alert_id,
        "message": f"告警已创建，严重程度: {severity}"
    }


def resolve_alert(alert_id: str, resolver: str, solution: str) -> dict:
    """解决告警"""
    alert_file = os.path.join(WORKFLOW_DIR, "alerts.json")
    alerts = load_json(alert_file)
    
    if alert_id not in alerts:
        return {"success": False, "message": f"未找到告警 {alert_id}"}
    
    alerts[alert_id]["status"] = "已解决"
    alerts[alert_id]["resolved_at"] = datetime.now().isoformat()
    alerts[alert_id]["resolver"] = resolver
    alerts[alert_id]["solution"] = solution
    save_json(alert_file, alerts)
    
    return {"success": True, "message": "告警已解决"}


def query_alerts(status: str = None, severity: str = None) -> dict:
    """查询告警"""
    alert_file = os.path.join(WORKFLOW_DIR, "alerts.json")
    alerts = load_json(alert_file)
    
    results = []
    for alert_id, alert in alerts.items():
        if status and alert["status"] != status:
            continue
        if severity and alert["severity"] != severity:
            continue
        results.append({"id": alert_id, **alert})
    
    return {
        "found": len(results) > 0,
        "alerts": results,
        "total": len(results)
    }


# ========== 工具定义 ==========
WORKFLOW_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_approval",
            "description": "创建审批流程，如请假审批、报销审批、采购审批等",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "审批标题"
                    },
                    "requester": {
                        "type": "string",
                        "description": "申请人姓名"
                    },
                    "workflow_type": {
                        "type": "string",
                        "description": "审批类型：请假、报销、采购、加班、出差"
                    },
                    "description": {
                        "type": "string",
                        "description": "审批描述"
                    },
                    "approvers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "审批人列表，按顺序审批"
                    }
                },
                "required": ["title", "requester", "workflow_type", "approvers"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "approve_workflow",
            "description": "审批通过一个流程",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "流程ID"
                    },
                    "approver": {
                        "type": "string",
                        "description": "审批人姓名"
                    },
                    "comment": {
                        "type": "string",
                        "description": "审批意见"
                    }
                },
                "required": ["workflow_id", "approver"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reject_workflow",
            "description": "驳回一个审批流程",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "流程ID"
                    },
                    "approver": {
                        "type": "string",
                        "description": "审批人姓名"
                    },
                    "reason": {
                        "type": "string",
                        "description": "驳回原因"
                    }
                },
                "required": ["workflow_id", "approver", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_workflows",
            "description": "查询审批流程",
            "parameters": {
                "type": "object",
                "properties": {
                    "requester": {
                        "type": "string",
                        "description": "按申请人筛选"
                    },
                    "approver": {
                        "type": "string",
                        "description": "按审批人筛选"
                    },
                    "status": {
                        "type": "string",
                        "description": "按状态筛选：待审批、已批准、已驳回"
                    },
                    "workflow_type": {
                        "type": "string",
                        "description": "按类型筛选：请假、报销、采购、加班、出差"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_scheduled_task",
            "description": "创建定时任务，如每日报告、每周汇总等",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "任务标题"
                    },
                    "task_type": {
                        "type": "string",
                        "description": "任务类型：报告、汇总、提醒、检查"
                    },
                    "schedule": {
                        "type": "string",
                        "description": "执行周期：每天、每周一、每月1号"
                    },
                    "action": {
                        "type": "string",
                        "description": "执行的动作描述"
                    },
                    "created_by": {
                        "type": "string",
                        "description": "创建人"
                    }
                },
                "required": ["title", "task_type", "schedule", "action", "created_by"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_notifications",
            "description": "获取用户的通知消息",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "用户ID或姓名"
                    },
                    "unread_only": {
                        "type": "boolean",
                        "description": "是否只返回未读通知"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_alert",
            "description": "创建异常告警",
            "parameters": {
                "type": "object",
                "properties": {
                    "alert_type": {
                        "type": "string",
                        "description": "告警类型：系统、业务、安全、性能"
                    },
                    "title": {
                        "type": "string",
                        "description": "告警标题"
                    },
                    "description": {
                        "type": "string",
                        "description": "告警描述"
                    },
                    "severity": {
                        "type": "string",
                        "description": "严重程度：低、中、高、紧急"
                    }
                },
                "required": ["alert_type", "title", "description", "severity"]
            }
        }
    }
]


def execute_workflow_tool(tool_name: str, arguments: dict) -> str:
    """执行流程自动化工具"""
    try:
        if tool_name == "create_approval":
            result = create_approval_workflow(**arguments)
        elif tool_name == "approve_workflow":
            result = approve_workflow(**arguments)
        elif tool_name == "reject_workflow":
            result = reject_workflow(**arguments)
        elif tool_name == "query_workflows":
            result = query_workflows(**arguments)
        elif tool_name == "create_scheduled_task":
            result = create_scheduled_task(**arguments)
        elif tool_name == "get_notifications":
            result = get_notifications(**arguments)
        elif tool_name == "create_alert":
            result = create_alert(**arguments)
        else:
            result = {"error": f"未知工具: {tool_name}"}
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"工具执行失败: {str(e)}"}, ensure_ascii=False)
