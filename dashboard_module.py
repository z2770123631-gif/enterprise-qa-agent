#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
可视化仪表盘模块 - Web管理后台、数据大屏、实时监控
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

DASHBOARD_DIR = "dashboard_data"
DASHBOARD_CONFIG_FILE = os.path.join(DASHBOARD_DIR, "dashboard_config.json")


def ensure_dashboard_dir():
    """确保仪表盘目录存在"""
    os.makedirs(DASHBOARD_DIR, exist_ok=True)


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
    ensure_dashboard_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========== 仪表盘配置 ==========

def get_dashboard_config() -> dict:
    """获取仪表盘配置"""
    config = load_json(DASHBOARD_CONFIG_FILE)
    if not config:
        config = {
            "theme": "light",
            "refresh_interval": 30,
            "widgets": [
                {"id": "overview", "title": "系统概览", "type": "summary", "position": {"x": 0, "y": 0, "w": 12, "h": 2}},
                {"id": "employees", "title": "员工统计", "type": "chart", "chart_type": "pie", "position": {"x": 0, "y": 2, "w": 4, "h": 3}},
                {"id": "expenses", "title": "费用趋势", "type": "chart", "chart_type": "bar", "position": {"x": 4, "y": 2, "w": 4, "h": 3}},
                {"id": "projects", "title": "项目进度", "type": "chart", "chart_type": "progress", "position": {"x": 8, "y": 2, "w": 4, "h": 3}},
                {"id": "notifications", "title": "最新通知", "type": "list", "position": {"x": 0, "y": 5, "w": 6, "h": 3}},
                {"id": "tasks", "title": "待办任务", "type": "list", "position": {"x": 6, "y": 5, "w": 6, "h": 3}}
            ]
        }
        save_json(DASHBOARD_CONFIG_FILE, config)
    return config


# ========== 仪表盘数据 ==========

def get_dashboard_data() -> dict:
    """获取仪表盘数据"""
    from analysis_module import (
        analyze_employee_distribution,
        analyze_expense_trends,
        analyze_leave_patterns,
        analyze_project_progress
    )
    from workflow_module import query_workflows, get_notifications
    from memory_module import get_user_stats
    
    # 获取各项数据
    employee_data = analyze_employee_distribution()
    expense_data = analyze_expense_trends()
    leave_data = analyze_leave_patterns()
    project_data = analyze_project_progress()
    
    # 获取待审批流程
    pending_workflows = query_workflows(status="待审批")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "overview": {
            "total_employees": employee_data.get("total_employees", 0),
            "total_expenses": expense_data.get("total_expenses", 0),
            "total_projects": project_data.get("total_projects", 0),
            "pending_approvals": pending_workflows.get("total", 0)
        },
        "employee_chart": {
            "type": "pie",
            "title": "员工部门分布",
            "data": employee_data.get("department_distribution", {})
        },
        "expense_chart": {
            "type": "bar",
            "title": "费用类型分布",
            "data": expense_data.get("by_type", {}).get("amounts", {})
        },
        "project_chart": {
            "type": "progress",
            "title": "项目进度",
            "data": project_data.get("projects", [])
        },
        "leave_chart": {
            "type": "bar",
            "title": "请假类型分布",
            "data": leave_data.get("by_type", {}).get("days", {})
        }
    }


def get_realtime_stats() -> dict:
    """获取实时统计数据"""
    from workflow_module import load_json as load_workflow
    
    workflows = load_workflow("workflow_data/workflows.json")
    notifications = load_workflow("workflow_data/notifications.json")
    
    # 统计今日数据
    today = datetime.now().strftime("%Y-%m-%d")
    today_workflows = sum(1 for wf in workflows.values() if wf.get("created_at", "").startswith(today))
    
    return {
        "timestamp": datetime.now().isoformat(),
        "today": {
            "new_workflows": today_workflows,
            "total_workflows": len(workflows),
            "unread_notifications": sum(
                sum(1 for n in notifs if not n.get("read", False))
                for notifs in notifications.values()
            )
        },
        "system_status": {
            "api_status": "running",
            "database_status": "connected",
            "memory_usage": "normal"
        }
    }


# ========== 数据大屏 ==========

def get_big_screen_data() -> dict:
    """获取数据大屏数据"""
    dashboard_data = get_dashboard_data()
    realtime_stats = get_realtime_stats()
    
    return {
        "title": "企业智能助手数据大屏",
        "subtitle": "Enterprise AI Assistant Dashboard",
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sections": [
            {
                "title": "核心指标",
                "type": "kpi",
                "items": [
                    {"label": "员工总数", "value": dashboard_data["overview"]["total_employees"], "unit": "人"},
                    {"label": "费用总额", "value": dashboard_data["overview"]["total_expenses"], "unit": "元"},
                    {"label": "项目数量", "value": dashboard_data["overview"]["total_projects"], "unit": "个"},
                    {"label": "待审批", "value": dashboard_data["overview"]["pending_approvals"], "unit": "项"}
                ]
            },
            {
                "title": "员工分布",
                "type": "chart",
                "chart_type": "pie",
                "data": dashboard_data["employee_chart"]["data"]
            },
            {
                "title": "费用分析",
                "type": "chart",
                "chart_type": "bar",
                "data": dashboard_data["expense_chart"]["data"]
            },
            {
                "title": "项目进度",
                "type": "chart",
                "chart_type": "progress",
                "data": dashboard_data["project_chart"]["data"]
            }
        ]
    }


# ========== 报表生成 ==========

def generate_dashboard_report() -> dict:
    """生成仪表盘报表"""
    dashboard_data = get_dashboard_data()
    
    # 生成报表文本
    report = f"""
# 企业数据仪表盘报表

生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}

## 一、核心指标

| 指标 | 数值 |
|------|------|
| 员工总数 | {dashboard_data['overview']['total_employees']}人 |
| 费用总额 | {dashboard_data['overview']['total_expenses']}元 |
| 项目数量 | {dashboard_data['overview']['total_projects']}个 |
| 待审批 | {dashboard_data['overview']['pending_approvals']}项 |

## 二、员工分布

"""
    
    # 添加员工分布数据
    for dept, count in dashboard_data["employee_chart"]["data"].items():
        report += f"- {dept}: {count}人\n"
    
    report += "\n## 三、费用分析\n\n"
    
    # 添加费用数据
    for exp_type, amount in dashboard_data["expense_chart"]["data"].items():
        report += f"- {exp_type}: {amount}元\n"
    
    report += "\n## 四、项目进度\n\n"
    
    # 添加项目数据
    for project in dashboard_data["project_chart"]["data"]:
        report += f"- {project['name']}: {project['progress']}% ({project['status']})\n"
    
    return {
        "success": True,
        "report": report,
        "data": dashboard_data
    }


# ========== 工具定义 ==========
DASHBOARD_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_dashboard",
            "description": "获取仪表盘数据，包含各项统计和图表数据",
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
            "name": "get_realtime_stats",
            "description": "获取实时统计数据，包含今日数据和系统状态",
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
            "name": "get_big_screen",
            "description": "获取数据大屏数据，适合大屏展示",
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
            "name": "generate_dashboard_report",
            "description": "生成仪表盘报表，包含文字描述和数据",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


def execute_dashboard_tool(tool_name: str, arguments: dict) -> str:
    """执行仪表盘工具"""
    try:
        if tool_name == "get_dashboard":
            result = get_dashboard_data()
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif tool_name == "get_realtime_stats":
            result = get_realtime_stats()
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif tool_name == "get_big_screen":
            result = get_big_screen_data()
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif tool_name == "generate_dashboard_report":
            result = generate_dashboard_report()
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        else:
            return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"工具执行失败: {str(e)}"}, ensure_ascii=False)


# ========== 仪表盘HTML模板 ==========

def get_dashboard_html() -> str:
    """获取仪表盘HTML页面"""
    html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>企业智能助手 - 数据仪表盘</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', sans-serif; background: #f5f7fa; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { opacity: 0.8; font-size: 14px; }
        .container { padding: 20px; max-width: 1200px; margin: 0 auto; }
        .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
        .kpi-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .kpi-value { font-size: 32px; font-weight: bold; color: #667eea; }
        .kpi-label { font-size: 14px; color: #666; margin-top: 5px; }
        .chart-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        .chart-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chart-title { font-size: 16px; font-weight: bold; margin-bottom: 15px; color: #333; }
        .bar-chart { display: flex; flex-direction: column; gap: 10px; }
        .bar-item { display: flex; align-items: center; gap: 10px; }
        .bar-label { width: 80px; font-size: 12px; text-align: right; }
        .bar-container { flex: 1; background: #eee; border-radius: 5px; height: 25px; }
        .bar-fill { height: 100%; border-radius: 5px; background: linear-gradient(90deg, #667eea, #764ba2); }
        .bar-value { width: 60px; font-size: 12px; }
        .progress-list { display: flex; flex-direction: column; gap: 12px; }
        .progress-item { display: flex; align-items: center; gap: 10px; }
        .progress-name { width: 120px; font-size: 13px; }
        .progress-bar { flex: 1; background: #eee; border-radius: 10px; height: 20px; overflow: hidden; }
        .progress-fill { height: 100%; border-radius: 10px; transition: width 0.3s; }
        .progress-value { width: 50px; font-size: 13px; text-align: right; }
        .status-good { background: linear-gradient(90deg, #56ab2f, #a8e063); }
        .status-warning { background: linear-gradient(90deg, #f093fb, #f5576c); }
        .footer { text-align: center; padding: 20px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>企业智能助手 - 数据仪表盘</h1>
        <p>Enterprise AI Assistant Dashboard</p>
    </div>
    <div class="container">
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="kpi-value" id="employees">-</div>
                <div class="kpi-label">员工总数</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value" id="expenses">-</div>
                <div class="kpi-label">费用总额</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value" id="projects">-</div>
                <div class="kpi-label">项目数量</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value" id="approvals">-</div>
                <div class="kpi-label">待审批</div>
            </div>
        </div>
        <div class="chart-row">
            <div class="chart-card">
                <div class="chart-title">员工部门分布</div>
                <div class="bar-chart" id="employeeChart"></div>
            </div>
            <div class="chart-card">
                <div class="chart-title">费用类型分布</div>
                <div class="bar-chart" id="expenseChart"></div>
            </div>
        </div>
        <div class="chart-row" style="margin-top: 15px;">
            <div class="chart-card">
                <div class="chart-title">项目进度</div>
                <div class="progress-list" id="projectChart"></div>
            </div>
            <div class="chart-card">
                <div class="chart-title">请假类型分布</div>
                <div class="bar-chart" id="leaveChart"></div>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>更新时间: <span id="updateTime">-</span></p>
    </div>
    <script>
        async function loadData() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                
                // 更新KPI
                document.getElementById('employees').textContent = data.overview.total_employees;
                document.getElementById('expenses').textContent = data.overview.total_expenses.toLocaleString();
                document.getElementById('projects').textContent = data.overview.total_projects;
                document.getElementById('approvals').textContent = data.overview.pending_approvals;
                
                // 更新员工图表
                renderBarChart('employeeChart', data.employee_chart.data);
                
                // 更新费用图表
                renderBarChart('expenseChart', data.expense_chart.data);
                
                // 更新项目进度
                renderProgress('projectChart', data.project_chart.data);
                
                // 更新请假图表
                renderBarChart('leaveChart', data.leave_chart.data);
                
                // 更新时间
                document.getElementById('updateTime').textContent = new Date().toLocaleString();
            } catch (error) {
                console.error('加载数据失败:', error);
            }
        }
        
        function renderBarChart(containerId, data) {
            const container = document.getElementById(containerId);
            const maxValue = Math.max(...Object.values(data));
            
            container.innerHTML = Object.entries(data).map(([key, value]) => `
                <div class="bar-item">
                    <div class="bar-label">${key}</div>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: ${(value/maxValue)*100}%"></div>
                    </div>
                    <div class="bar-value">${value}</div>
                </div>
            `).join('');
        }
        
        function renderProgress(containerId, data) {
            const container = document.getElementById(containerId);
            
            container.innerHTML = data.map(project => `
                <div class="progress-item">
                    <div class="progress-name">${project.name}</div>
                    <div class="progress-bar">
                        <div class="progress-fill ${project.progress >= 75 ? 'status-good' : 'status-warning'}" 
                             style="width: ${project.progress}%"></div>
                    </div>
                    <div class="progress-value">${project.progress}%</div>
                </div>
            `).join('');
        }
        
        // 初始加载
        loadData();
        
        // 每30秒刷新
        setInterval(loadData, 30000);
    </script>
</body>
</html>
"""
    return html
