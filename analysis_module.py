#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据分析模块 - 数据报表、趋势分析、可视化图表
"""

import json
import os
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict, Counter

DATA_ANALYSIS_DIR = "analysis_data"
REPORT_FILE = os.path.join(DATA_ANALYSIS_DIR, "reports.json")


def ensure_analysis_dir():
    """确保数据分析目录存在"""
    os.makedirs(DATA_ANALYSIS_DIR, exist_ok=True)


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
    ensure_analysis_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========== 模拟企业数据 ==========

def get_sample_data() -> dict:
    """获取示例企业数据（实际项目中应从数据库获取）"""
    return {
        "employees": [
            {"id": "EMP001", "name": "张三", "department": "技术研发部", "position": "高级工程师", "salary": 25000, "join_date": "2021-03-15", "age": 28},
            {"id": "EMP002", "name": "李四", "department": "产品部", "position": "产品经理", "salary": 22000, "join_date": "2020-06-20", "age": 30},
            {"id": "EMP003", "name": "王五", "department": "市场部", "position": "市场总监", "salary": 30000, "join_date": "2019-01-10", "age": 35},
            {"id": "EMP004", "name": "赵六", "department": "财务部", "position": "财务主管", "salary": 28000, "join_date": "2018-08-05", "age": 32},
            {"id": "EMP005", "name": "孙七", "department": "人力资源部", "position": "HR经理", "salary": 26000, "join_date": "2020-11-15", "age": 29},
            {"id": "EMP006", "name": "周八", "department": "技术研发部", "position": "前端工程师", "salary": 18000, "join_date": "2022-04-01", "age": 25},
            {"id": "EMP007", "name": "吴九", "department": "技术研发部", "position": "后端工程师", "salary": 20000, "join_date": "2021-09-10", "age": 27},
            {"id": "EMP008", "name": "郑十", "department": "产品部", "position": "UI设计师", "salary": 16000, "join_date": "2023-01-15", "age": 24},
        ],
        "expenses": [
            {"id": "EXP001", "employee": "张三", "amount": 3500, "type": "差旅", "date": "2024-06-15", "status": "已审批"},
            {"id": "EXP002", "employee": "李四", "amount": 1200, "type": "办公用品", "date": "2024-06-14", "status": "已审批"},
            {"id": "EXP003", "employee": "王五", "amount": 8500, "type": "客户招待", "date": "2024-06-13", "status": "已驳回"},
            {"id": "EXP004", "employee": "赵六", "amount": 2800, "type": "差旅", "date": "2024-06-12", "status": "已审批"},
            {"id": "EXP005", "employee": "孙七", "amount": 950, "type": "办公用品", "date": "2024-06-11", "status": "待审批"},
            {"id": "EXP006", "employee": "周八", "amount": 4200, "type": "培训", "date": "2024-06-10", "status": "已审批"},
            {"id": "EXP007", "employee": "吴九", "amount": 1800, "type": "差旅", "date": "2024-06-09", "status": "已审批"},
            {"id": "EXP008", "employee": "郑十", "amount": 650, "type": "办公用品", "date": "2024-06-08", "status": "已审批"},
        ],
        "leaves": [
            {"employee": "张三", "type": "年假", "days": 3, "month": 6},
            {"employee": "李四", "type": "病假", "days": 1, "month": 6},
            {"employee": "王五", "type": "事假", "days": 2, "month": 6},
            {"employee": "赵六", "type": "年假", "days": 5, "month": 5},
            {"employee": "孙七", "type": "病假", "days": 2, "month": 5},
            {"employee": "周八", "type": "年假", "days": 1, "month": 6},
            {"employee": "吴九", "type": "事假", "days": 1, "month": 5},
        ],
        "projects": [
            {"name": "企业知识库系统", "status": "进行中", "progress": 75, "manager": "张三", "start_date": "2024-01-15"},
            {"name": "客户管理平台", "status": "进行中", "progress": 45, "manager": "李四", "start_date": "2024-03-01"},
            {"name": "数据分析平台", "status": "已完成", "progress": 100, "manager": "王五", "start_date": "2023-10-01"},
            {"name": "移动办公APP", "status": "计划中", "progress": 10, "manager": "赵六", "start_date": "2024-07-01"},
        ]
    }


# ========== 数据分析函数 ==========

def analyze_employee_distribution() -> dict:
    """分析员工分布"""
    data = get_sample_data()
    employees = data["employees"]
    
    # 部门分布
    dept_count = Counter(emp["department"] for emp in employees)
    
    # 年龄分布
    age_groups = {"25岁以下": 0, "25-30岁": 0, "30-35岁": 0, "35岁以上": 0}
    for emp in employees:
        age = emp["age"]
        if age < 25:
            age_groups["25岁以下"] += 1
        elif age < 30:
            age_groups["25-30岁"] += 1
        elif age < 35:
            age_groups["30-35岁"] += 1
        else:
            age_groups["35岁以上"] += 1
    
    # 薪资分布
    salaries = [emp["salary"] for emp in employees]
    avg_salary = sum(salaries) / len(salaries)
    max_salary = max(salaries)
    min_salary = min(salaries)
    
    return {
        "total_employees": len(employees),
        "department_distribution": dict(dept_count),
        "age_distribution": age_groups,
        "salary_statistics": {
            "average": round(avg_salary, 2),
            "maximum": max_salary,
            "minimum": min_salary,
            "range": max_salary - min_salary
        }
    }


def analyze_expense_trends() -> dict:
    """分析费用趋势"""
    data = get_sample_data()
    expenses = data["expenses"]
    
    # 按类型统计
    type_amounts = defaultdict(float)
    type_count = Counter()
    for exp in expenses:
        type_amounts[exp["type"]] += exp["amount"]
        type_count[exp["type"]] += 1
    
    # 按状态统计
    status_count = Counter(exp["status"] for exp in expenses)
    
    # 总费用
    total_amount = sum(exp["amount"] for exp in expenses)
    
    # 平均费用
    avg_amount = total_amount / len(expenses) if expenses else 0
    
    return {
        "total_expenses": total_amount,
        "expense_count": len(expenses),
        "average_expense": round(avg_amount, 2),
        "by_type": {
            "amounts": dict(type_amounts),
            "counts": dict(type_count)
        },
        "by_status": dict(status_count),
        "top_expenses": sorted(expenses, key=lambda x: x["amount"], reverse=True)[:3]
    }


def analyze_leave_patterns() -> dict:
    """分析请假模式"""
    data = get_sample_data()
    leaves = data["leaves"]
    
    # 按类型统计
    type_days = defaultdict(int)
    type_count = Counter()
    for leave in leaves:
        type_days[leave["type"]] += leave["days"]
        type_count[leave["type"]] += 1
    
    # 按月统计
    month_days = defaultdict(int)
    for leave in leaves:
        month_days[leave["month"]] += leave["days"]
    
    # 总请假天数
    total_days = sum(leave["days"] for leave in leaves)
    
    # 平均请假天数
    avg_days = total_days / len(leaves) if leaves else 0
    
    return {
        "total_leave_days": total_days,
        "leave_count": len(leaves),
        "average_leave_days": round(avg_days, 2),
        "by_type": {
            "days": dict(type_days),
            "counts": dict(type_count)
        },
        "by_month": dict(month_days),
        "most_common_leave": max(type_count.items(), key=lambda x: x[1])[0] if type_count else "无"
    }


def analyze_project_progress() -> dict:
    """分析项目进度"""
    data = get_sample_data()
    projects = data["projects"]
    
    # 按状态统计
    status_count = Counter(p["status"] for p in projects)
    
    # 平均进度
    avg_progress = sum(p["progress"] for p in projects) / len(projects) if projects else 0
    
    # 进度分布
    progress_ranges = {"0-25%": 0, "25-50%": 0, "50-75%": 0, "75-100%": 0}
    for p in projects:
        prog = p["progress"]
        if prog < 25:
            progress_ranges["0-25%"] += 1
        elif prog < 50:
            progress_ranges["25-50%"] += 1
        elif prog < 75:
            progress_ranges["50-75%"] += 1
        else:
            progress_ranges["75-100%"] += 1
    
    return {
        "total_projects": len(projects),
        "average_progress": round(avg_progress, 2),
        "by_status": dict(status_count),
        "progress_distribution": progress_ranges,
        "projects": [{
            "name": p["name"],
            "status": p["status"],
            "progress": p["progress"],
            "manager": p["manager"]
        } for p in projects]
    }


def generate_comprehensive_report() -> dict:
    """生成综合报表"""
    employee_analysis = analyze_employee_distribution()
    expense_analysis = analyze_expense_trends()
    leave_analysis = analyze_leave_patterns()
    project_analysis = analyze_project_progress()
    
    # 生成洞察
    insights = []
    
    # 员工洞察
    if employee_analysis["salary_statistics"]["range"] > 10000:
        insights.append("员工薪资差距较大，建议优化薪酬体系")
    
    # 费用洞察
    if expense_analysis["by_status"].get("待审批", 0) > 0:
        insights.append(f"有{expense_analysis['by_status']['待审批']}笔费用待审批，建议及时处理")
    
    # 请假洞察
    if leave_analysis["most_common_leave"] == "病假":
        insights.append("病假较多，建议关注员工健康")
    
    # 项目洞察
    if project_analysis["average_progress"] < 50:
        insights.append("项目整体进度偏慢，建议加强项目管理")
    
    # 保存报表
    report = {
        "report_id": f"RPT{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now().isoformat(),
        "employee_analysis": employee_analysis,
        "expense_analysis": expense_analysis,
        "leave_analysis": leave_analysis,
        "project_analysis": project_analysis,
        "insights": insights,
        "summary": {
            "total_employees": employee_analysis["total_employees"],
            "total_expenses": expense_analysis["total_expenses"],
            "total_leave_days": leave_analysis["total_leave_days"],
            "total_projects": project_analysis["total_projects"],
            "average_progress": project_analysis["average_progress"]
        }
    }
    
    # 保存到文件
    reports = load_json(REPORT_FILE)
    reports[report["report_id"]] = report
    save_json(REPORT_FILE, reports)
    
    return report


def generate_text_chart(data: dict, chart_type: str = "bar") -> str:
    """生成文本图表"""
    if chart_type == "bar":
        # 柱状图
        lines = []
        max_value = max(data.values()) if data else 1
        for key, value in data.items():
            bar_length = int((value / max_value) * 20)
            bar = "█" * bar_length
            lines.append(f"{key:10} | {bar} {value}")
        return "\n".join(lines)
    
    elif chart_type == "pie":
        # 饼图（文本表示）
        total = sum(data.values())
        lines = []
        for key, value in data.items():
            percentage = (value / total) * 100 if total > 0 else 0
            lines.append(f"{key}: {value} ({percentage:.1f}%)")
        return "\n".join(lines)
    
    return str(data)


# ========== 工具定义 ==========
ANALYSIS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_employees",
            "description": "分析员工分布，包括部门分布、年龄分布、薪资统计",
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
            "name": "analyze_expenses",
            "description": "分析费用趋势，包括按类型、状态统计，找出高额费用",
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
            "name": "analyze_leaves",
            "description": "分析请假模式，包括按类型、月份统计，找出常见请假类型",
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
            "name": "analyze_projects",
            "description": "分析项目进度，包括按状态统计，进度分布",
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
            "name": "generate_analysis_report",
            "description": "生成综合数据分析报表，包含所有维度的分析结果和洞察建议",
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
            "name": "compare_data",
            "description": "对比不同维度的数据，找出差异和趋势",
            "parameters": {
                "type": "object",
                "properties": {
                    "dimension1": {
                        "type": "string",
                        "description": "第一个对比维度：部门、类型、月份、状态"
                    },
                    "dimension2": {
                        "type": "string",
                        "description": "第二个对比维度（可选）"
                    }
                },
                "required": ["dimension1"]
            }
        }
    }
]


def execute_analysis_tool(tool_name: str, arguments: dict) -> str:
    """执行数据分析工具"""
    try:
        if tool_name == "analyze_employees":
            result = analyze_employee_distribution()
            # 添加文本图表
            result["chart"] = generate_text_chart(result["department_distribution"], "bar")
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif tool_name == "analyze_expenses":
            result = analyze_expense_trends()
            result["chart"] = generate_text_chart(result["by_type"]["amounts"], "bar")
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif tool_name == "analyze_leaves":
            result = analyze_leave_patterns()
            result["chart"] = generate_text_chart(result["by_type"]["days"], "bar")
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif tool_name == "analyze_projects":
            result = analyze_project_progress()
            result["chart"] = generate_text_chart(result["by_status"], "pie")
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif tool_name == "generate_analysis_report":
            result = generate_comprehensive_report()
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif tool_name == "compare_data":
            dimension1 = arguments.get("dimension1", "")
            
            if "部门" in dimension1:
                result = analyze_employee_distribution()
                comparison = result["department_distribution"]
            elif "类型" in dimension1 or "费用" in dimension1:
                result = analyze_expense_trends()
                comparison = result["by_type"]["amounts"]
            elif "请假" in dimension1:
                result = analyze_leave_patterns()
                comparison = result["by_type"]["days"]
            elif "项目" in dimension1:
                result = analyze_project_progress()
                comparison = result["by_status"]
            else:
                comparison = {"错误": f"不支持的对比维度: {dimension1}"}
            
            return json.dumps({
                "dimension": dimension1,
                "comparison": comparison,
                "chart": generate_text_chart(comparison, "bar")
            }, ensure_ascii=False, indent=2)
        
        else:
            return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"工具执行失败: {str(e)}"}, ensure_ascii=False)


# ========== 获取分析数据摘要 ==========

def get_data_summary() -> str:
    """获取数据摘要，用于增强AI回复"""
    employee_data = analyze_employee_distribution()
    expense_data = analyze_expense_trends()
    project_data = analyze_project_progress()
    
    summary = f"""【企业数据概览】
- 员工总数：{employee_data['total_employees']}人
- 部门数量：{len(employee_data['department_distribution'])}个
- 平均薪资：{employee_data['salary_statistics']['average']}元
- 费用总额：{expense_data['total_expenses']}元
- 项目总数：{project_data['total_projects']}个
- 平均进度：{project_data['average_progress']}%"""
    
    return summary
