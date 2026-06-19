#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多Agent协作模块 - 多个专业Agent协同工作
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

AGENT_DIR = "agent_data"
AGENT_CONFIG_FILE = os.path.join(AGENT_DIR, "agents.json")
AGENT_HISTORY_FILE = os.path.join(AGENT_DIR, "agent_history.json")


def ensure_agent_dir():
    """确保Agent目录存在"""
    os.makedirs(AGENT_DIR, exist_ok=True)


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
    ensure_agent_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========== Agent定义 ==========

DEFAULT_AGENTS = {
    "hr_agent": {
        "id": "hr_agent",
        "name": "HR助手",
        "description": "负责人事相关问题，如考勤、请假、薪资、福利、培训等",
        "expertise": ["考勤管理", "请假制度", "薪资福利", "员工培训", "绩效考核", "招聘入职"],
        "system_prompt": """你是一位专业的人力资源助手，专门处理人事相关问题。

你的职责：
1. 解答员工关于考勤、请假、薪资、福利等问题
2. 协助处理入职、离职、转正等人事流程
3. 提供培训信息和职业发展建议
4. 处理绩效考核相关问题

回答要求：
- 基于公司制度和政策回答
- 保持专业、友好、耐心
- 引用相关制度条款
- 提供具体的操作指引""",
        "icon": "👤",
        "active": True
    },
    "finance_agent": {
        "id": "finance_agent",
        "name": "财务助手",
        "description": "负责财务相关问题，如报销、预算、发票、税务等",
        "expertise": ["费用报销", "预算管理", "发票处理", "税务咨询", "工资发放", "财务报表"],
        "system_prompt": """你是一位专业的财务助手，专门处理财务相关问题。

你的职责：
1. 解答报销流程和标准
2. 协助处理发票和税务问题
3. 提供预算和费用咨询
4. 处理工资和社保相关问题

回答要求：
- 基于财务制度回答
- 保持严谨、准确
- 提供具体的金额和标准
- 注意财务合规性""",
        "icon": "💰",
        "active": True
    },
    "it_agent": {
        "id": "it_agent",
        "name": "IT支持助手",
        "description": "负责IT技术支持，如电脑问题、软件使用、网络故障等",
        "expertise": ["电脑故障", "软件安装", "网络问题", "账号权限", "数据恢复", "系统使用"],
        "system_prompt": """你是一位专业的IT技术支持助手，专门处理技术相关问题。

你的职责：
1. 解答电脑和软件使用问题
2. 协助处理网络和账号问题
3. 提供技术培训和指导
4. 处理系统故障和数据问题

回答要求：
- 提供清晰的操作步骤
- 使用通俗易懂的语言
- 给出多种解决方案
- 注意信息安全""",
        "icon": "💻",
        "active": True
    },
    "admin_agent": {
        "id": "admin_agent",
        "name": "行政助手",
        "description": "负责行政事务，如会议室预订、办公用品、快递收发等",
        "expertise": ["会议室预订", "办公用品", "快递收发", "访客接待", "环境维护", "资产管理"],
        "system_prompt": """你是一位专业的行政助手，专门处理行政事务。

你的职责：
1. 协助预订会议室和设备
2. 处理办公用品申请
3. 管理快递和信件收发
4. 协助访客接待和安排

回答要求：
- 提供具体的时间和地点
- 说明申请流程
- 提供联系方式
- 保持热情服务""",
        "icon": "🏢",
        "active": True
    },
    "coordinator_agent": {
        "id": "coordinator_agent",
        "name": "协调助手",
        "description": "负责协调和分发任务给其他专业Agent",
        "expertise": ["任务分发", "问题协调", "流程跟踪", "信息汇总"],
        "system_prompt": """你是一位协调助手，负责将用户的问题分发给合适的专业Agent。

你的职责：
1. 分析用户问题类型
2. 将问题分发给对应的专业Agent
3. 汇总多个Agent的回复
4. 跟踪问题处理进度

处理流程：
1. 判断问题属于哪个领域
2. 如果是单一领域问题，直接转给对应Agent
3. 如果是跨领域问题，协调多个Agent
4. 汇总回复并返回给用户""",
        "icon": "🎯",
        "active": True
    }
}


# ========== Agent管理 ==========

def get_agents() -> dict:
    """获取所有Agent配置"""
    agents = load_json(AGENT_CONFIG_FILE)
    if not agents:
        # 使用默认配置
        agents = DEFAULT_AGENTS
        save_json(AGENT_CONFIG_FILE, agents)
    return agents


def get_agent(agent_id: str) -> Optional[dict]:
    """获取指定Agent"""
    agents = get_agents()
    return agents.get(agent_id)


def get_active_agents() -> List[dict]:
    """获取所有活跃的Agent"""
    agents = get_agents()
    return [agent for agent in agents.values() if agent.get("active", True)]


def match_agent(question: str) -> Optional[dict]:
    """根据问题匹配最合适的Agent"""
    agents = get_active_agents()
    
    # 关键词匹配
    keywords_map = {
        "hr_agent": ["考勤", "打卡", "请假", "休假", "年假", "病假", "事假", "薪资", "工资", "奖金", "福利", "社保", "公积金", "培训", "绩效", "考核", "入职", "离职", "转正", "劳动合同"],
        "finance_agent": ["报销", "费用", "发票", "预算", "税务", "工资", "社保", "公积金", "财务", "付款", "收款", "账单"],
        "it_agent": ["电脑", "电脑", "软件", "网络", "账号", "密码", "系统", "打印机", "邮箱", "VPN", "服务器", "数据"],
        "admin_agent": ["会议室", "预订", "办公用品", "快递", "访客", "接待", "资产", "设备", "环境", "卫生"]
    }
    
    # 计算每个Agent的匹配分数
    scores = {}
    for agent in agents:
        agent_id = agent["id"]
        if agent_id == "coordinator_agent":
            continue
        
        score = 0
        keywords = keywords_map.get(agent_id, [])
        for keyword in keywords:
            if keyword in question:
                score += 1
        
        if score > 0:
            scores[agent_id] = score
    
    # 返回得分最高的Agent
    if scores:
        best_agent_id = max(scores, key=scores.get)
        return get_agent(best_agent_id)
    
    # 如果没有匹配，返回协调助手
    return get_agent("coordinator_agent")


# ========== Agent协作 ==========

def route_to_agent(question: str, user_id: str, target_agent_id: str = None) -> dict:
    """将问题路由到指定Agent"""
    if target_agent_id:
        agent = get_agent(target_agent_id)
    else:
        agent = match_agent(question)
    
    if not agent:
        return {
            "success": False,
            "message": "未找到合适的Agent处理此问题"
        }
    
    return {
        "success": True,
        "agent_id": agent["id"],
        "agent_name": agent["name"],
        "agent_description": agent["description"],
        "system_prompt": agent["system_prompt"]
    }


def get_agent_response(question: str, agent_id: str, context: str = "") -> str:
    """获取Agent的回复（用于协调多个Agent）"""
    agent = get_agent(agent_id)
    if not agent:
        return f"未找到Agent: {agent_id}"
    
    # 构建Agent回复格式
    response = f"**{agent['icon']} {agent['name']}**\n\n"
    response += f"问题已转交给{agent['name']}处理。\n"
    response += f"专业领域：{'、'.join(agent['expertise'][:3])}..."
    
    return response


def collaborate_agents(question: str, user_id: str) -> dict:
    """多Agent协作处理复杂问题"""
    # 分析问题涉及的领域
    agents = get_active_agents()
    relevant_agents = []
    
    # 关键词匹配
    keywords_map = {
        "hr_agent": ["考勤", "请假", "薪资", "福利", "培训", "绩效"],
        "finance_agent": ["报销", "费用", "发票", "预算", "财务"],
        "it_agent": ["电脑", "软件", "网络", "账号", "系统"],
        "admin_agent": ["会议室", "办公用品", "快递", "访客"]
    }
    
    for agent in agents:
        agent_id = agent["id"]
        if agent_id == "coordinator_agent":
            continue
        
        keywords = keywords_map.get(agent_id, [])
        for keyword in keywords:
            if keyword in question:
                relevant_agents.append(agent)
                break
    
    # 如果涉及多个领域，需要协作
    if len(relevant_agents) > 1:
        return {
            "need_collaboration": True,
            "agents": relevant_agents,
            "message": f"此问题涉及多个领域，需要{len(relevant_agents)}个Agent协作处理"
        }
    elif len(relevant_agents) == 1:
        return {
            "need_collaboration": False,
            "agents": relevant_agents,
            "message": f"此问题由{relevant_agents[0]['name']}处理"
        }
    else:
        return {
            "need_collaboration": False,
            "agents": [get_agent("coordinator_agent")],
            "message": "此问题由协调助手处理"
        }


# ========== 工具定义 ==========
MULTI_AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "route_to_specialist",
            "description": "将问题转交给专业Agent处理",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "用户的问题"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "目标Agent ID：hr_agent、finance_agent、it_agent、admin_agent"
                    },
                    "reason": {
                        "type": "string",
                        "description": "转交原因"
                    }
                },
                "required": ["question", "agent_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_agents",
            "description": "列出所有可用的专业Agent",
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
            "name": "collaborate_agents",
            "description": "协调多个Agent协作处理复杂问题",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "用户的问题"
                    },
                    "agent_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "需要协作的Agent ID列表"
                    }
                },
                "required": ["question"]
            }
        }
    }
]


def execute_agent_tool(tool_name: str, arguments: dict) -> str:
    """执行Agent协作工具"""
    try:
        if tool_name == "route_to_specialist":
            question = arguments.get("question", "")
            agent_id = arguments.get("agent_id", "")
            reason = arguments.get("reason", "")
            
            agent = get_agent(agent_id)
            if not agent:
                return json.dumps({"error": f"未找到Agent: {agent_id}"}, ensure_ascii=False)
            
            result = {
                "success": True,
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "agent_icon": agent["icon"],
                "expertise": agent["expertise"],
                "message": f"问题已转交给{agent['name']}，专业领域：{'、'.join(agent['expertise'][:3])}"
            }
            return json.dumps(result, ensure_ascii=False)
        
        elif tool_name == "list_agents":
            agents = get_active_agents()
            agent_list = []
            for agent in agents:
                agent_list.append({
                    "id": agent["id"],
                    "name": agent["name"],
                    "icon": agent["icon"],
                    "description": agent["description"],
                    "expertise": agent["expertise"][:3]
                })
            return json.dumps({"agents": agent_list}, ensure_ascii=False)
        
        elif tool_name == "collaborate_agents":
            question = arguments.get("question", "")
            agent_ids = arguments.get("agent_ids", [])
            
            if not agent_ids:
                # 自动匹配
                collab_result = collaborate_agents(question, "")
                agents = collab_result.get("agents", [])
            else:
                agents = [get_agent(aid) for aid in agent_ids if get_agent(aid)]
            
            result = {
                "success": True,
                "agents": [{
                    "id": a["id"],
                    "name": a["name"],
                    "icon": a["icon"]
                } for a in agents],
                "message": f"已协调{len(agents)}个Agent协作处理"
            }
            return json.dumps(result, ensure_ascii=False)
        
        else:
            return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"工具执行失败: {str(e)}"}, ensure_ascii=False)


# ========== 获取Agent系统提示词 ==========

def get_agent_system_prompt(agent_id: str) -> str:
    """获取Agent的系统提示词"""
    agent = get_agent(agent_id)
    if agent:
        return agent.get("system_prompt", "")
    return ""


def get_all_agent_prompts() -> dict:
    """获取所有Agent的系统提示词"""
    agents = get_agents()
    return {aid: agent["system_prompt"] for aid, agent in agents.items()}
