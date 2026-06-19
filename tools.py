#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具模块 - 定义Agent可调用的工具函数
"""

import json
import os
from datetime import datetime, timedelta


# ========== 员工信息数据库（模拟） ==========
EMPLOYEE_DB = {
    "EMP001": {"name": "张三", "department": "技术研发部", "position": "高级工程师", "salary": 25000, "leave_balance": 10},
    "EMP002": {"name": "李四", "department": "产品部", "position": "产品经理", "salary": 22000, "leave_balance": 8},
    "EMP003": {"name": "王五", "department": "市场部", "position": "市场总监", "salary": 30000, "leave_balance": 15},
    "EMP004": {"name": "赵六", "department": "财务部", "position": "财务主管", "salary": 28000, "leave_balance": 12},
    "EMP005": {"name": "孙七", "department": "人力资源部", "position": "HR经理", "salary": 26000, "leave_balance": 9},
}

# ========== 报销记录（模拟） ==========
EXPENSE_DB = {
    "EXP001": {"employee": "张三", "amount": 3500, "status": "待审批", "date": "2024-06-15", "type": "差旅"},
    "EXP002": {"employee": "李四", "amount": 1200, "status": "已审批", "date": "2024-06-14", "type": "办公用品"},
    "EXP003": {"employee": "王五", "amount": 8500, "status": "已驳回", "date": "2024-06-13", "type": "客户招待"},
}

# ========== 请假记录（模拟） ==========
LEAVE_DB = [
    {"id": "LEAVE001", "employee": "张三", "type": "年假", "days": 3, "start": "2024-07-01", "end": "2024-07-03", "status": "待审批"},
    {"id": "LEAVE002", "employee": "李四", "type": "病假", "days": 1, "start": "2024-06-20", "end": "2024-06-20", "status": "已批准"},
]

# ========== 工单记录（模拟） ==========
TICKET_DB = [
    {"id": "TK001", "title": "电脑无法开机", "submitter": "张三", "status": "处理中", "assignee": "IT支持", "created": "2024-06-19"},
    {"id": "TK002", "title": "申请新显示器", "submitter": "李四", "status": "待处理", "assignee": "IT支持", "created": "2024-06-18"},
]


# ========== 工具定义 ==========
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "query_employee",
            "description": "查询员工信息，包括部门、职位、薪资、剩余假期等",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "员工工号，如 EMP001"
                    },
                    "employee_name": {
                        "type": "string",
                        "description": "员工姓名，如 张三"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_expense",
            "description": "查询报销记录和报销状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "expense_id": {
                        "type": "string",
                        "description": "报销单号，如 EXP001"
                    },
                    "employee_name": {
                        "type": "string",
                        "description": "员工姓名，查询该员工的所有报销"
                    },
                    "status": {
                        "type": "string",
                        "description": "报销状态筛选：待审批、已审批、已驳回"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_leave_request",
            "description": "创建请假申请",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "请假员工姓名"
                    },
                    "leave_type": {
                        "type": "string",
                        "description": "请假类型：年假、病假、事假、婚假、产假"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "开始日期，格式：YYYY-MM-DD"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "结束日期，格式：YYYY-MM-DD"
                    },
                    "reason": {
                        "type": "string",
                        "description": "请假原因"
                    }
                },
                "required": ["employee_name", "leave_type", "start_date", "end_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_leave",
            "description": "查询请假记录",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "员工姓名"
                    },
                    "status": {
                        "type": "string",
                        "description": "状态筛选：待审批、已批准、已驳回"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "创建IT支持工单",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "工单标题"
                    },
                    "submitter": {
                        "type": "string",
                        "description": "提交人姓名"
                    },
                    "description": {
                        "type": "string",
                        "description": "问题详细描述"
                    },
                    "priority": {
                        "type": "string",
                        "description": "优先级：低、中、高、紧急"
                    }
                },
                "required": ["title", "submitter"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_tickets",
            "description": "查询IT支持工单",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "工单号"
                    },
                    "submitter": {
                        "type": "string",
                        "description": "提交人姓名"
                    },
                    "status": {
                        "type": "string",
                        "description": "状态筛选：待处理、处理中、已完成"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description": "生成企业数据报表",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "description": "报表类型：员工统计、部门统计、报销统计、请假统计"
                    }
                },
                "required": ["report_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期和时间",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# ========== 工具执行函数 ==========
def execute_tool(tool_name: str, arguments: dict) -> str:
    """执行指定的工具函数"""
    try:
        if tool_name == "query_employee":
            return json.dumps(query_employee(**arguments), ensure_ascii=False)
        elif tool_name == "query_expense":
            return json.dumps(query_expense(**arguments), ensure_ascii=False)
        elif tool_name == "create_leave_request":
            return json.dumps(create_leave_request(**arguments), ensure_ascii=False)
        elif tool_name == "query_leave":
            return json.dumps(query_leave(**arguments), ensure_ascii=False)
        elif tool_name == "create_ticket":
            return json.dumps(create_ticket(**arguments), ensure_ascii=False)
        elif tool_name == "query_tickets":
            return json.dumps(query_tickets(**arguments), ensure_ascii=False)
        elif tool_name == "generate_report":
            return json.dumps(generate_report(**arguments), ensure_ascii=False)
        elif tool_name == "get_current_time":
            return json.dumps(get_current_time(), ensure_ascii=False)
        else:
            return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"工具执行失败: {str(e)}"}, ensure_ascii=False)


def query_employee(employee_id: str = None, employee_name: str = None) -> dict:
    """查询员工信息"""
    if employee_id:
        emp = EMPLOYEE_DB.get(employee_id)
        if emp:
            return {"found": True, "employee_id": employee_id, **emp}
        return {"found": False, "message": f"未找到工号为 {employee_id} 的员工"}
    
    if employee_name:
        for emp_id, emp in EMPLOYEE_DB.items():
            if emp["name"] == employee_name:
                return {"found": True, "employee_id": emp_id, **emp}
        return {"found": False, "message": f"未找到名为 {employee_name} 的员工"}
    
    # 返回所有员工
    return {"found": True, "employees": [{"id": k, **v} for k, v in EMPLOYEE_DB.items()]}


def query_expense(expense_id: str = None, employee_name: str = None, status: str = None) -> dict:
    """查询报销记录"""
    if expense_id:
        exp = EXPENSE_DB.get(expense_id)
        if exp:
            return {"found": True, "expense_id": expense_id, **exp}
        return {"found": False, "message": f"未找到报销单 {expense_id}"}
    
    results = []
    for exp_id, exp in EXPENSE_DB.items():
        if employee_name and exp["employee"] != employee_name:
            continue
        if status and exp["status"] != status:
            continue
        results.append({"id": exp_id, **exp})
    
    return {"found": len(results) > 0, "expenses": results, "total": len(results)}


def create_leave_request(employee_name: str, leave_type: str, start_date: str, end_date: str, reason: str = "") -> dict:
    """创建请假申请"""
    # 计算请假天数
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end - start).days + 1
    
    leave_id = f"LEAVE{len(LEAVE_DB) + 1:03d}"
    new_leave = {
        "id": leave_id,
        "employee": employee_name,
        "type": leave_type,
        "days": days,
        "start": start_date,
        "end": end_date,
        "reason": reason,
        "status": "待审批",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    LEAVE_DB.append(new_leave)
    
    return {
        "success": True,
        "message": f"请假申请已提交",
        "leave_id": leave_id,
        "days": days,
        "status": "待审批"
    }


def query_leave(employee_name: str = None, status: str = None) -> dict:
    """查询请假记录"""
    results = []
    for leave in LEAVE_DB:
        if employee_name and leave["employee"] != employee_name:
            continue
        if status and leave["status"] != status:
            continue
        results.append(leave)
    
    return {"found": len(results) > 0, "leaves": results, "total": len(results)}


def create_ticket(title: str, submitter: str, description: str = "", priority: str = "中") -> dict:
    """创建IT支持工单"""
    ticket_id = f"TK{len(TICKET_DB) + 1:03d}"
    new_ticket = {
        "id": ticket_id,
        "title": title,
        "submitter": submitter,
        "description": description,
        "priority": priority,
        "status": "待处理",
        "assignee": "IT支持",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    TICKET_DB.append(new_ticket)
    
    return {
        "success": True,
        "message": f"工单已创建",
        "ticket_id": ticket_id,
        "status": "待处理"
    }


def query_tickets(ticket_id: str = None, submitter: str = None, status: str = None) -> dict:
    """查询工单"""
    if ticket_id:
        for ticket in TICKET_DB:
            if ticket["id"] == ticket_id:
                return {"found": True, "ticket": ticket}
        return {"found": False, "message": f"未找到工单 {ticket_id}"}
    
    results = []
    for ticket in TICKET_DB:
        if submitter and ticket["submitter"] != submitter:
            continue
        if status and ticket["status"] != status:
            continue
        results.append(ticket)
    
    return {"found": len(results) > 0, "tickets": results, "total": len(results)}


def generate_report(report_type: str) -> dict:
    """生成企业数据报表"""
    if report_type == "员工统计":
        dept_count = {}
        for emp in EMPLOYEE_DB.values():
            dept = emp["department"]
            dept_count[dept] = dept_count.get(dept, 0) + 1
        return {
            "report_type": "员工统计",
            "total_employees": len(EMPLOYEE_DB),
            "by_department": dept_count
        }
    
    elif report_type == "部门统计":
        departments = {}
        for emp in EMPLOYEE_DB.values():
            dept = emp["department"]
            if dept not in departments:
                departments[dept] = {"count": 0, "positions": []}
            departments[dept]["count"] += 1
            departments[dept]["positions"].append(emp["position"])
        return {
            "report_type": "部门统计",
            "departments": departments
        }
    
    elif report_type == "报销统计":
        status_count = {}
        total_amount = 0
        for exp in EXPENSE_DB.values():
            status = exp["status"]
            status_count[status] = status_count.get(status, 0) + 1
            if exp["status"] == "已审批":
                total_amount += exp["amount"]
        return {
            "report_type": "报销统计",
            "total_records": len(EXPENSE_DB),
            "by_status": status_count,
            "approved_amount": total_amount
        }
    
    elif report_type == "请假统计":
        type_count = {}
        for leave in LEAVE_DB:
            leave_type = leave["type"]
            type_count[leave_type] = type_count.get(leave_type, 0) + 1
        return {
            "report_type": "请假统计",
            "total_records": len(LEAVE_DB),
            "by_type": type_count
        }
    
    return {"error": f"未知报表类型: {report_type}"}


def get_current_time() -> dict:
    """获取当前时间"""
    now = datetime.now()
    return {
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()]
    }
