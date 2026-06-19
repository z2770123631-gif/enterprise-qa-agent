# 企业知识库智能问答Agent

基于RAG（检索增强生成）技术和**Function Calling**的企业知识管理系统，能够自动读取企业文档、建立知识库、并回答员工问题或执行相关操作。

## 功能特点

- 自动读取企业文档，建立知识库
- 智能检索相关文档片段
- 基于文档内容回答员工问题
- 支持多轮对话上下文
- **工具调用能力（Function Calling）**
  - 查询员工信息
  - 查询报销记录
  - 创建请假申请
  - 创建IT支持工单
  - 生成数据报表
  - 获取当前时间
- **记忆与个性化**
  - 用户画像自动构建
  - 对话历史记录
  - 个性化回复
  - 偏好设置和记忆
- **流程自动化**
  - 审批流程管理（创建、审批、驳回）
  - 定时任务管理
  - 通知消息管理
  - 异常告警管理
- **多Agent协作**
  - HR助手（人事相关）
  - 财务助手（财务相关）
  - IT支持助手（技术相关）
  - 行政助手（行政事务）
  - 协调助手（任务分发）
- **数据分析能力**
  - 员工分布分析（部门、年龄、薪资）
  - 费用趋势分析（类型、状态、高额费用）
  - 请假模式分析（类型、月份、常见请假）
  - 项目进度分析（状态、进度分布）
  - 综合报表生成（洞察和建议）
- **文档智能分析**
  - 支持PDF、Word、Excel、CSV、TXT、Markdown、JSON等格式
  - 文档内容提取和解析
  - 文档对比和摘要生成
  - 文档搜索和索引
- **语音交互**
  - 文字转语音（TTS）
  - 语音播放URL生成
  - 多种语音类型支持
  - 语音对话模式
- **可视化仪表盘**
  - Web管理后台
  - 数据大屏展示
  - 实时数据监控
  - 图表可视化
- **知识图谱**
  - 实体和关系管理
  - 知识图谱构建
  - 图谱查询和搜索
  - 邻居节点探索
- Web界面和API接口

## 技术栈

- Python 3.10+
- Flask Web框架
- DeepSeek大语言模型API
- RAG技术（检索增强生成）
- Function Calling（工具调用）
- 关键词匹配检索

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API

编辑 `config.py`，填入你的DeepSeek API Key。

### 3. 添加文档

将企业文档（.txt、.md、.json格式）放入 `documents` 目录。

### 4. 启动服务

```bash
python main.py
```

或者双击 `启动服务.bat`

### 5. 访问Web界面

打开浏览器访问：`http://localhost:8000`

## API接口

### 问答接口（支持工具调用）

```
POST /api/ask
Content-Type: application/json

{
    "question": "查询张三的员工信息",
    "user_id": "user123"
}
```

### 上传文档

```
POST /api/upload
Content-Type: multipart/form-data

file: 文档文件
```

### 系统状态

```
GET /api/status
```

### 工具列表

```
GET /api/tools
```

## 可用工具

| 工具名称 | 功能描述 | 示例问题 |
|---------|---------|---------|
| query_employee | 查询员工信息 | "查询张三的员工信息" |
| query_expense | 查询报销记录 | "查看待审批的报销" |
| create_leave_request | 创建请假申请 | "帮我申请3天年假" |
| query_leave | 查询请假记录 | "查询我的请假记录" |
| create_ticket | 创建IT工单 | "电脑无法开机，帮我创建工单" |
| query_tickets | 查询工单状态 | "查询我的工单状态" |
| generate_report | 生成数据报表 | "生成员工统计报表" |
| get_current_time | 获取当前时间 | "现在几点了" |
| set_user_preference | 设置用户偏好 | "记住我喜欢简洁的回复" |
| get_user_profile_info | 获取用户画像 | "查询我的用户画像" |
| create_approval | 创建审批流程 | "创建请假审批流程" |
| approve_workflow | 审批通过 | "通过审批WF0001" |
| reject_workflow | 审批驳回 | "驳回审批WF0001" |
| query_workflows | 查询审批流程 | "查询待审批的流程" |
| create_scheduled_task | 创建定时任务 | "创建每天9点的任务" |
| get_notifications | 获取通知 | "查看我的通知" |
| create_alert | 创建告警 | "创建系统告警" |
| route_to_specialist | 转交专业Agent | "转交给HR助手" |
| list_agents | 列出所有Agent | "有哪些AI助手" |
| collaborate_agents | 协调Agent协作 | "协调多个Agent处理" |
| analyze_employees | 员工分布分析 | "分析员工分布" |
| analyze_expenses | 费用趋势分析 | "分析费用趋势" |
| analyze_leaves | 请假模式分析 | "分析请假模式" |
| analyze_projects | 项目进度分析 | "分析项目进度" |
| generate_analysis_report | 综合分析报表 | "生成综合报表" |
| compare_data | 数据对比 | "对比部门数据" |
| analyze_document | 分析文档 | "分析这个PDF文件" |
| list_documents | 列出文档 | "列出已分析的文档" |
| search_documents | 搜索文档 | "搜索包含关键词的文档" |
| compare_documents | 对比文档 | "对比两个文档" |
| summarize_document | 文档摘要 | "生成文档摘要" |
| text_to_speech | 文字转语音 | "把这段文字转成语音" |
| generate_voice_url | 生成语音URL | "生成语音播放链接" |
| voice_chat | 语音对话模式 | "切换到语音模式" |
| get_dashboard | 获取仪表盘数据 | "获取仪表盘数据" |
| get_realtime_stats | 实时统计 | "获取实时统计" |
| get_big_screen | 数据大屏 | "获取大屏数据" |
| generate_report | 生成报表 | "生成仪表盘报表" |
| query_knowledge_graph | 查询知识图谱 | "查询知识图谱" |
| get_entity_info | 获取实体信息 | "获取实体详情" |
| get_graph_stats | 图谱统计 | "获取图谱统计" |
| add_knowledge | 添加知识 | "添加实体到图谱" |

## 项目结构

```
enterprise-qa-agent/
├── main.py                   # 主程序
├── tools.py                  # 工具模块（Function Calling）
├── memory_module.py          # 记忆模块（用户画像和个性化）
├── workflow_module.py        # 流程自动化模块（审批、任务、通知）
├── multi_agent_module.py     # 多Agent协作模块
├── analysis_module.py        # 数据分析模块（报表、趋势、图表）
├── doc_analysis_module.py    # 文档智能分析模块
├── voice_module.py           # 语音交互模块
├── dashboard_module.py       # 可视化仪表盘模块
├── knowledge_graph_module.py # 知识图谱模块
├── config.py                 # 配置文件
├── requirements.txt          # 依赖列表
├── README.md                 # 项目说明
├── documents/                # 企业文档目录
├── vector_db/                # 向量数据库目录
├── memory_data/              # 记忆数据目录
├── workflow_data/            # 流程数据目录
├── agent_data/               # Agent配置目录
├── analysis_data/            # 分析数据目录
├── doc_analysis_data/        # 文档分析数据目录
├── voice_data/               # 语音数据目录
├── dashboard_data/           # 仪表盘数据目录
└── knowledge_graph/          # 知识图谱数据目录
```

## 应用场景

1. **企业知识管理** - 将分散的文档集中管理，方便员工查询
2. **新员工培训** - 新员工可以快速了解公司制度和流程
3. **HR咨询** - 自动回答员工关于考勤、薪酬、福利等问题
4. **流程自动化** - 自动处理请假、报销、工单等流程
5. **数据分析** - 自动生成各类统计报表

## 扩展方向

1. 接入真正的向量数据库（如Milvus、Pinecone）
2. 支持更多文档格式（PDF、Word、Excel）
3. 添加文档更新和删除功能
4. 实现用户权限管理
5. 部署到云服务器
6. 添加更多工具函数
