#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业知识库智能问答Agent
基于RAG技术的企业知识管理系统
"""

import os
import json
import hashlib
import logging
from typing import List, Dict, Any
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from tools import TOOLS_DEFINITION, execute_tool
from memory_module import (
    MEMORY_TOOLS,
    execute_memory_tool,
    update_user_profile,
    add_topic,
    add_tool_usage,
    log_conversation,
    get_personalized_context
)
from workflow_module import (
    WORKFLOW_TOOLS,
    execute_workflow_tool
)
from multi_agent_module import (
    MULTI_AGENT_TOOLS,
    execute_agent_tool,
    match_agent,
    get_agent_system_prompt
)
from analysis_module import (
    ANALYSIS_TOOLS,
    execute_analysis_tool,
    get_data_summary
)
from doc_analysis_module import (
    DOC_ANALYSIS_TOOLS,
    execute_doc_analysis_tool
)
from voice_module import (
    VOICE_TOOLS,
    execute_voice_tool
)
from dashboard_module import (
    DASHBOARD_TOOLS,
    execute_dashboard_tool,
    get_dashboard_html
)
from knowledge_graph_module import (
    KNOWLEDGE_GRAPH_TOOLS,
    execute_knowledge_graph_tool,
    init_knowledge_graph
)
from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_BASE,
    MODEL_NAME,
    VECTOR_DB_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    DOCS_DIR,
    TOP_K,
    MAX_HISTORY,
    HOST,
    PORT,
    LOG_ENABLED,
    LOG_FILE
)

# 配置日志
if LOG_ENABLED:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
logger = logging.getLogger(__name__)

# 初始化OpenAI客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_API_BASE
)

# Flask应用
app = Flask(__name__)

# 存储文档向量和文本
document_chunks = []
document_vectors = []
conversation_history = {}


def ensure_dirs():
    """确保目录存在"""
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)


def read_document(file_path: str) -> str:
    """读取文档内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取文档失败 {file_path}: {str(e)}")
        return ""


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """将文本分割成小块"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def get_embedding(text: str) -> List[float]:
    """获取文本的向量表示（使用DeepSeek API）"""
    try:
        # 使用简单的字符统计作为向量（实际项目中应使用真正的embedding模型）
        # 这里为了简化演示，使用字符频率作为向量
        vector = [0.0] * 100
        for i, char in enumerate(text[:100]):
            vector[i % 100] += ord(char) / 1000
        return vector
    except Exception as e:
        logger.error(f"获取向量失败: {str(e)}")
        return [0.0] * 100


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """计算余弦相似度"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)


def load_documents():
    """加载文档并建立索引"""
    global document_chunks, document_vectors
    
    ensure_dirs()
    document_chunks = []
    document_vectors = []
    
    # 扫描文档目录
    doc_files = []
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(('.txt', '.md', '.json')):
                doc_files.append(os.path.join(root, file))
    
    logger.info(f"找到 {len(doc_files)} 个文档")
    
    for file_path in doc_files:
        content = read_document(file_path)
        if not content:
            continue
        
        # 分割文档
        chunks = split_text(content)
        logger.info(f"文档 {os.path.basename(file_path)} 分割成 {len(chunks)} 个片段")
        
        # 为每个片段创建向量
        for chunk in chunks:
            vector = get_embedding(chunk)
            document_chunks.append({
                'text': chunk,
                'source': os.path.basename(file_path),
                'timestamp': datetime.now().isoformat()
            })
            document_vectors.append(vector)
    
    logger.info(f"共加载 {len(document_chunks)} 个文档片段")
    
    # 保存索引
    save_index()


def save_index():
    """保存索引到文件"""
    index_data = {
        'chunks': document_chunks,
        'vectors': document_vectors
    }
    index_path = os.path.join(VECTOR_DB_PATH, 'index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    logger.info(f"索引已保存到 {index_path}")


def load_index():
    """从文件加载索引"""
    global document_chunks, document_vectors
    
    index_path = os.path.join(VECTOR_DB_PATH, 'index.json')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
            document_chunks = index_data.get('chunks', [])
            document_vectors = index_data.get('vectors', [])
        logger.info(f"从索引加载 {len(document_chunks)} 个文档片段")
        return True
    return False


def search_documents(query: str, top_k: int = TOP_K) -> List[Dict]:
    """搜索相关文档片段（使用关键词匹配）"""
    if not document_chunks:
        return []
    
    # 提取查询关键词
    import re
    keywords = re.findall(r'[\u4e00-\u9fff]+', query)
    if not keywords:
        keywords = [query]
    
    # 计算关键词匹配分数
    scores = []
    for i, chunk in enumerate(document_chunks):
        text = chunk['text']
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += text.count(keyword)
        scores.append((i, score))
    
    # 按分数排序
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # 返回最相关的片段
    results = []
    for idx, score in scores[:top_k]:
        if score > 0:  # 只返回有匹配的结果
            results.append({
                'text': document_chunks[idx]['text'],
                'source': document_chunks[idx]['source'],
                'similarity': score
            })
    
    return results


def get_conversation_history(user_id: str) -> List[Dict]:
    """获取对话历史"""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    return conversation_history[user_id]


def add_to_history(user_id: str, role: str, content: str):
    """添加对话到历史记录"""
    history = get_conversation_history(user_id)
    history.append({"role": role, "content": content})
    if len(history) > MAX_HISTORY * 2:
        history = history[-(MAX_HISTORY * 2):]
        conversation_history[user_id] = history


def answer_question(user_id: str, question: str) -> str:
    """回答问题（支持工具调用、记忆和多Agent协作）"""
    try:
        # 更新用户交互次数
        update_user_profile(user_id, {})
        
        # 匹配最合适的Agent
        matched_agent = match_agent(question)
        agent_prompt = ""
        if matched_agent and matched_agent["id"] != "coordinator_agent":
            agent_prompt = get_agent_system_prompt(matched_agent["id"])
        
        # 搜索相关文档
        relevant_docs = search_documents(question)
        
        # 构建上下文
        context = ""
        if relevant_docs:
            context = "以下是与问题相关的企业知识库内容：\n\n"
            for i, doc in enumerate(relevant_docs, 1):
                context += f"[文档片段 {i}] (来源: {doc['source']})\n{doc['text']}\n\n"
        
        # 获取个性化上下文
        personalized_context = get_personalized_context(user_id)
        
        # 获取数据摘要
        data_summary = get_data_summary()
        
        # 添加用户问题到历史
        add_to_history(user_id, "user", question)
        
        # 构建提示词
        base_prompt = """你是一个企业知识库智能问答助手。你的任务是基于提供的企业文档内容和可用工具，准确回答员工的问题或执行相关操作。

回答要求：
1. 优先使用知识库中的内容回答问题
2. 如果需要查询数据或执行操作，请调用相应的工具
3. 如果知识库中没有相关信息且无法通过工具解决，明确告知用户
4. 回答要简洁、专业、准确
5. 引用文档时注明来源
6. 记住用户的偏好，提供个性化服务
7. 如果问题涉及专业领域，可以转交给专业Agent处理

请用中文回答问题。"""
        
        # 如果有匹配的专业Agent，添加其提示词
        if agent_prompt:
            system_prompt = f"{base_prompt}\n\n【当前处理Agent】\n{matched_agent['name']}：{matched_agent['description']}\n\n{agent_prompt}"
        else:
            system_prompt = base_prompt
        
        messages = [
            {"role": "system", "content": system_prompt},
            *get_conversation_history(user_id)
        ]
        
        # 构建完整上下文
        full_context = ""
        if context:
            full_context += context + "\n\n"
        if personalized_context:
            full_context += personalized_context + "\n\n"
        if data_summary:
            full_context += data_summary + "\n\n"
        
        if full_context:
            messages.append({"role": "user", "content": f"{full_context}用户问题：{question}"})
        else:
            messages.append({"role": "user", "content": question})
        
        # 合并所有工具定义
        all_tools = TOOLS_DEFINITION + MEMORY_TOOLS + WORKFLOW_TOOLS + MULTI_AGENT_TOOLS + ANALYSIS_TOOLS + DOC_ANALYSIS_TOOLS + VOICE_TOOLS + DASHBOARD_TOOLS + KNOWLEDGE_GRAPH_TOOLS
        
        # 调用AI API（支持工具调用）
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=all_tools,
            tool_choice="auto",
            temperature=0.3,
            max_tokens=1500
        )
        
        response_message = response.choices[0].message
        tools_used = []
        
        # 检查是否有工具调用
        if response_message.tool_calls:
            # 执行工具调用
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if LOG_ENABLED:
                    logger.info(f"调用工具: {function_name}({function_args})")
                
                # 执行工具
                if function_name in [t['function']['name'] for t in MEMORY_TOOLS]:
                    tool_result = execute_memory_tool(function_name, function_args, user_id)
                elif function_name in [t['function']['name'] for t in WORKFLOW_TOOLS]:
                    tool_result = execute_workflow_tool(function_name, function_args)
                elif function_name in [t['function']['name'] for t in MULTI_AGENT_TOOLS]:
                    tool_result = execute_agent_tool(function_name, function_args)
                elif function_name in [t['function']['name'] for t in ANALYSIS_TOOLS]:
                    tool_result = execute_analysis_tool(function_name, function_args)
                elif function_name in [t['function']['name'] for t in DOC_ANALYSIS_TOOLS]:
                    tool_result = execute_doc_analysis_tool(function_name, function_args)
                elif function_name in [t['function']['name'] for t in VOICE_TOOLS]:
                    tool_result = execute_voice_tool(function_name, function_args)
                elif function_name in [t['function']['name'] for t in DASHBOARD_TOOLS]:
                    tool_result = execute_dashboard_tool(function_name, function_args)
                elif function_name in [t['function']['name'] for t in KNOWLEDGE_GRAPH_TOOLS]:
                    tool_result = execute_knowledge_graph_tool(function_name, function_args)
                else:
                    tool_result = execute_tool(function_name, function_args)
                    # 记录工具使用
                    add_tool_usage(user_id, function_name)
                
                tools_used.append(function_name)
                
                if LOG_ENABLED:
                    logger.info(f"工具结果: {tool_result}")
                
                # 添加工具结果到消息
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": tool_result
                })
            
            # 再次调用AI，获取最终回复
            final_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.3,
                max_tokens=1500
            )
            
            answer = final_response.choices[0].message.content
        else:
            answer = response_message.content
        
        # 添加AI回复到历史
        add_to_history(user_id, "assistant", answer)
        
        # 记录对话
        log_conversation(user_id, question, answer, tools_used)
        
        # 提取并记录话题
        if len(question) > 5:
            add_topic(user_id, question[:50])
        
        if LOG_ENABLED:
            logger.info(f"用户 {user_id}: {question}")
            logger.info(f"AI回复: {answer}")
        
        return answer
        
    except Exception as e:
        error_msg = f"抱歉，回答问题时出现错误: {str(e)}"
        if LOG_ENABLED:
            logger.error(error_msg)
        return error_msg


# Web界面HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>企业知识库智能问答Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 90%;
            max-width: 800px;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.8;
            font-size: 14px;
        }
        .chat-container {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
        }
        .message.user {
            justify-content: flex-end;
        }
        .message .bubble {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.5;
        }
        .message.user .bubble {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .message.bot .bubble {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .input-area {
            padding: 20px;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #eee;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        .input-area input:focus {
            border-color: #667eea;
        }
        .input-area button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .input-area button:hover {
            background: #5a6fd6;
        }
        .status {
            padding: 10px 20px;
            background: #e8f5e9;
            color: #2e7d32;
            font-size: 12px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>企业知识库智能问答Agent</h1>
            <p>基于RAG技术的企业知识管理系统</p>
        </div>
        <div class="status" id="status">系统就绪，等待提问...</div>
        <div class="chat-container" id="chatContainer"></div>
        <div class="input-area">
            <input type="text" id="questionInput" placeholder="请输入您的问题..." onkeypress="if(event.key==='Enter')askQuestion()">
            <button onclick="askQuestion()">发送</button>
        </div>
    </div>

    <script>
        function addMessage(content, isUser) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            messageDiv.innerHTML = `<div class="bubble">${content}</div>`;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function setStatus(text) {
            document.getElementById('status').textContent = text;
        }

        async function askQuestion() {
            const input = document.getElementById('questionInput');
            const question = input.value.trim();
            if (!question) return;

            addMessage(question, true);
            input.value = '';
            setStatus('正在思考中...');

            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question, user_id: 'web_user'})
                });
                const data = await response.json();
                addMessage(data.answer, false);
                setStatus('系统就绪，等待提问...');
            } catch (error) {
                addMessage('抱歉，出现错误：' + error.message, false);
                setStatus('出现错误，请重试');
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """首页"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/ask', methods=['POST'])
def api_ask():
    """问答API"""
    data = request.json
    question = data.get('question', '')
    user_id = data.get('user_id', 'default')
    
    if not question:
        return jsonify({'error': '问题不能为空'}), 400
    
    answer = answer_question(user_id, question)
    
    return jsonify({
        'question': question,
        'answer': answer,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """上传文档API"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    # 保存文件
    file_path = os.path.join(DOCS_DIR, file.filename)
    file.save(file_path)
    
    # 重新加载文档
    load_documents()
    
    return jsonify({
        'message': f'文件 {file.filename} 上传成功',
        'chunks': len(document_chunks)
    })


@app.route('/api/status')
def api_status():
    """系统状态API"""
    return jsonify({
        'status': 'running',
        'documents': len(document_chunks),
        'model': MODEL_NAME,
        'tools': [t['function']['name'] for t in TOOLS_DEFINITION]
    })


@app.route('/api/tools')
def api_tools():
    """工具列表API"""
    tools_info = []
    for tool in TOOLS_DEFINITION + MEMORY_TOOLS:
        func = tool['function']
        tools_info.append({
            'name': func['name'],
            'description': func['description'],
            'parameters': func['parameters']
        })
    return jsonify({'tools': tools_info})


@app.route('/api/user/<user_id>')
def api_user_profile(user_id):
    """用户画像API"""
    from memory_module import get_user_stats
    stats = get_user_stats(user_id)
    return jsonify(stats)


@app.route('/dashboard')
def dashboard_page():
    """仪表盘页面"""
    return get_dashboard_html()


@app.route('/api/dashboard')
def api_dashboard():
    """仪表盘数据API"""
    from dashboard_module import get_dashboard_data
    data = get_dashboard_data()
    return jsonify(data)


@app.route('/api/knowledge-graph/search')
def api_knowledge_graph_search():
    """知识图谱搜索API"""
    query = request.args.get('q', '')
    from knowledge_graph_module import query_knowledge_graph
    result = query_knowledge_graph(query)
    return jsonify(result)


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              企业知识库智能问答Agent                         ║
║                   (基于RAG技术)                              ║
║                                                              ║
║  功能说明:                                                   ║
║     1. 自动读取企业文档，建立知识库                         ║
║     2. 智能检索相关文档片段                                 ║
║     3. 基于文档内容回答员工问题                             ║
║     4. 支持多轮对话上下文                                   ║
║                                                              ║
║  使用说明:                                                   ║
║     1. 将企业文档放入 documents 目录                        ║
║     2. 访问 http://localhost:8000 使用Web界面               ║
║     3. 或调用 /api/ask API接口                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if DEEPSEEK_API_KEY == "your_api_key_here":
        print("[错误] 请先在config.py中配置DeepSeek API Key!")
        return
    
    print("[启动] 正在初始化...")
    
    # 确保目录存在
    ensure_dirs()
    
    # 初始化知识图谱
    init_knowledge_graph()
    
    # 尝试加载已有索引
    if not load_index():
        # 如果没有索引，加载文档并创建索引
        print("[加载] 正在加载企业文档...")
        load_documents()
    
    print(f"[就绪] 已加载 {len(document_chunks)} 个文档片段")
    print(f"[地址] Web界面: http://localhost:{PORT}")
    print(f"[API] 问答接口: http://localhost:{PORT}/api/ask")
    print("[退出] 按 Ctrl+C 退出程序")
    
    # 启动Web服务
    app.run(host=HOST, port=PORT, debug=False)


if __name__ == '__main__':
    main()
