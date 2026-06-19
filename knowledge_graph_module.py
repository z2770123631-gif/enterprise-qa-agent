#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知识图谱模块 - 构建企业知识图谱、实体关系挖掘
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict

KNOWLEDGE_GRAPH_DIR = "knowledge_graph"
GRAPH_FILE = os.path.join(KNOWLEDGE_GRAPH_DIR, "graph.json")
ENTITY_FILE = os.path.join(KNOWLEDGE_GRAPH_DIR, "entities.json")
RELATION_FILE = os.path.join(KNOWLEDGE_GRAPH_DIR, "relations.json")


def ensure_kg_dir():
    """确保知识图谱目录存在"""
    os.makedirs(KNOWLEDGE_GRAPH_DIR, exist_ok=True)


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
    ensure_kg_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========== 实体定义 ==========

ENTITY_TYPES = {
    "person": {"name": "人物", "color": "#4CAF50", "icon": "👤"},
    "department": {"name": "部门", "color": "#2196F3", "icon": "🏢"},
    "position": {"name": "职位", "color": "#FF9800", "icon": "💼"},
    "project": {"name": "项目", "color": "#9C27B0", "icon": "📋"},
    "skill": {"name": "技能", "color": "#F44336", "icon": "🔧"},
    "document": {"name": "文档", "color": "#607D8B", "icon": "📄"},
    "process": {"name": "流程", "color": "#795548", "icon": "⚙️"},
    "policy": {"name": "制度", "color": "#00BCD4", "icon": "📜"}
}

RELATION_TYPES = {
    "belongs_to": {"name": "属于", "color": "#4CAF50"},
    "manages": {"name": "管理", "color": "#2196F3"},
    "works_on": {"name": "参与", "color": "#FF9800"},
    "has_skill": {"name": "掌握", "color": "#F44336"},
    "follows": {"name": "遵循", "color": "#9C27B0"},
    "related_to": {"name": "相关", "color": "#607D8B"},
    "creates": {"name": "创建", "color": "#795548"},
    "approves": {"name": "审批", "color": "#00BCD4"}
}


# ========== 实体管理 ==========

def add_entity(entity_id: str, entity_type: str, name: str, properties: dict = None) -> dict:
    """添加实体"""
    entities = load_json(ENTITY_FILE)
    
    entities[entity_id] = {
        "id": entity_id,
        "type": entity_type,
        "name": name,
        "properties": properties or {},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    save_json(ENTITY_FILE, entities)
    
    return {"success": True, "entity_id": entity_id, "message": f"实体 {name} 已添加"}


def get_entity(entity_id: str) -> Optional[dict]:
    """获取实体"""
    entities = load_json(ENTITY_FILE)
    return entities.get(entity_id)


def get_entities_by_type(entity_type: str) -> List[dict]:
    """按类型获取实体"""
    entities = load_json(ENTITY_FILE)
    return [e for e in entities.values() if e.get("type") == entity_type]


def search_entities(query: str) -> List[dict]:
    """搜索实体"""
    entities = load_json(ENTITY_FILE)
    
    results = []
    for entity in entities.values():
        if query.lower() in entity.get("name", "").lower():
            results.append(entity)
    
    return results


# ========== 关系管理 ==========

def add_relation(subject_id: str, predicate: str, object_id: str, properties: dict = None) -> dict:
    """添加关系"""
    relations = load_json(RELATION_FILE)
    
    relation_id = f"R{len(relations) + 1:04d}"
    
    relations[relation_id] = {
        "id": relation_id,
        "subject": subject_id,
        "predicate": predicate,
        "object": object_id,
        "properties": properties or {},
        "created_at": datetime.now().isoformat()
    }
    
    save_json(RELATION_FILE, relations)
    
    return {"success": True, "relation_id": relation_id, "message": "关系已添加"}


def get_entity_relations(entity_id: str) -> List[dict]:
    """获取实体的所有关系"""
    relations = load_json(RELATION_FILE)
    
    results = []
    for rel in relations.values():
        if rel.get("subject") == entity_id or rel.get("object") == entity_id:
            results.append(rel)
    
    return results


# ========== 知识图谱构建 ==========

def build_from_employee_data() -> dict:
    """从员工数据构建知识图谱"""
    from tools import EMPLOYEE_DB
    
    entities_added = 0
    relations_added = 0
    
    # 添加员工实体
    for emp_id, emp in EMPLOYEE_DB.items():
        add_entity(emp_id, "person", emp.get("name", ""), {
            "department": emp.get("department", ""),
            "position": emp.get("position", ""),
            "salary": emp.get("salary", 0)
        })
        entities_added += 1
        
        # 添加部门实体
        dept_id = f"dept_{emp.get('department', '').replace('部', '')}"
        add_entity(dept_id, "department", emp.get("department", ""))
        entities_added += 1
        
        # 添加职位实体
        pos_id = f"pos_{emp.get('position', '')}"
        add_entity(pos_id, "position", emp.get("position", ""))
        entities_added += 1
        
        # 添加员工-部门关系
        add_relation(emp_id, "belongs_to", dept_id)
        relations_added += 1
        
        # 添加员工-职位关系
        add_relation(emp_id, "has_position", pos_id)
        relations_added += 1
    
    return {
        "success": True,
        "entities_added": entities_added,
        "relations_added": relations_added,
        "message": f"已构建 {entities_added} 个实体，{relations_added} 个关系"
    }


def build_from_document_content(content: str, doc_name: str) -> dict:
    """从文档内容构建知识图谱"""
    entities_added = 0
    relations_added = 0
    
    # 提取可能的实体（简单实现）
    # 1. 提取人名（2-4个中文字符）
    person_pattern = r'[\u4e00-\u9fff]{2,4}(?=经理|主管|总监|工程师|设计师)'
    persons = re.findall(person_pattern, content)
    
    # 2. 提取部门
    dept_pattern = r'[\u4e00-\u9fff]+部'
    departments = re.findall(dept_pattern, content)
    
    # 3. 添加实体
    doc_id = f"doc_{doc_name}"
    add_entity(doc_id, "document", doc_name)
    entities_added += 1
    
    for person in set(persons):
        person_id = f"person_{person}"
        add_entity(person_id, "person", person)
        entities_added += 1
        
        # 添加文档-人物关系
        add_relation(doc_id, "mentions", person_id)
        relations_added += 1
    
    for dept in set(departments):
        dept_id = f"dept_{dept}"
        add_entity(dept_id, "department", dept)
        entities_added += 1
        
        # 添加文档-部门关系
        add_relation(doc_id, "mentions", dept_id)
        relations_added += 1
    
    return {
        "success": True,
        "entities_added": entities_added,
        "relations_added": relations_added,
        "persons_found": list(set(persons)),
        "departments_found": list(set(departments))
    }


# ========== 知识图谱查询 ==========

def query_knowledge_graph(query: str) -> dict:
    """查询知识图谱"""
    entities = load_json(ENTITY_FILE)
    relations = load_json(RELATION_FILE)
    
    # 搜索相关实体
    related_entities = search_entities(query)
    
    # 获取这些实体的关系
    related_relations = []
    for entity in related_entities:
        entity_relations = get_entity_relations(entity["id"])
        related_relations.extend(entity_relations)
    
    # 构建图谱数据
    nodes = []
    edges = []
    
    seen_entity_ids = set()
    for entity in related_entities:
        if entity["id"] not in seen_entity_ids:
            nodes.append({
                "id": entity["id"],
                "label": entity["name"],
                "type": entity["type"],
                "color": ENTITY_TYPES.get(entity["type"], {}).get("color", "#999")
            })
            seen_entity_ids.add(entity["id"])
    
    for rel in related_relations:
        edges.append({
            "source": rel["subject"],
            "target": rel["object"],
            "label": RELATION_TYPES.get(rel["predicate"], {}).get("name", rel["predicate"]),
            "color": RELATION_TYPES.get(rel["predicate"], {}).get("color", "#999")
        })
        
        # 添加关系中涉及的实体
        for eid in [rel["subject"], rel["object"]]:
            if eid not in seen_entity_ids:
                entity = get_entity(eid)
                if entity:
                    nodes.append({
                        "id": entity["id"],
                        "label": entity["name"],
                        "type": entity["type"],
                        "color": ENTITY_TYPES.get(entity["type"], {}).get("color", "#999")
                    })
                    seen_entity_ids.add(eid)
    
    return {
        "success": True,
        "query": query,
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges)
    }


def get_graph_statistics() -> dict:
    """获取图谱统计信息"""
    entities = load_json(ENTITY_FILE)
    relations = load_json(RELATION_FILE)
    
    # 实体类型统计
    entity_type_count = defaultdict(int)
    for entity in entities.values():
        entity_type_count[entity.get("type", "unknown")] += 1
    
    # 关系类型统计
    relation_type_count = defaultdict(int)
    for rel in relations.values():
        relation_type_count[rel.get("predicate", "unknown")] += 1
    
    return {
        "total_entities": len(entities),
        "total_relations": len(relations),
        "entity_types": dict(entity_type_count),
        "relation_types": dict(relation_type_count)
    }


def get_entity_neighbors(entity_id: str, depth: int = 1) -> dict:
    """获取实体的邻居节点"""
    entities = load_json(ENTITY_FILE)
    relations = load_json(RELATION_FILE)
    
    visited = set()
    nodes = []
    edges = []
    
    def dfs(current_id: str, current_depth: int):
        if current_depth > depth or current_id in visited:
            return
        
        visited.add(current_id)
        entity = get_entity(current_id)
        if entity:
            nodes.append({
                "id": entity["id"],
                "label": entity["name"],
                "type": entity["type"],
                "color": ENTITY_TYPES.get(entity["type"], {}).get("color", "#999")
            })
        
        # 查找相关关系
        for rel in relations.values():
            neighbor_id = None
            if rel["subject"] == current_id:
                neighbor_id = rel["object"]
            elif rel["object"] == current_id:
                neighbor_id = rel["subject"]
            
            if neighbor_id and neighbor_id not in visited:
                edges.append({
                    "source": rel["subject"],
                    "target": rel["object"],
                    "label": RELATION_TYPES.get(rel["predicate"], {}).get("name", rel["predicate"])
                })
                dfs(neighbor_id, current_depth + 1)
    
    dfs(entity_id, 0)
    
    return {
        "success": True,
        "center": entity_id,
        "nodes": nodes,
        "edges": edges
    }


# ========== 工具定义 ==========
KNOWLEDGE_GRAPH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_knowledge_graph",
            "description": "查询知识图谱，搜索实体和关系",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_entity_info",
            "description": "获取实体详细信息和关系",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "实体ID"
                    }
                },
                "required": ["entity_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_graph_stats",
            "description": "获取知识图谱统计信息",
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
            "name": "add_knowledge",
            "description": "添加知识到图谱（实体和关系）",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_name": {
                        "type": "string",
                        "description": "实体名称"
                    },
                    "entity_type": {
                        "type": "string",
                        "description": "实体类型：person、department、position、project、skill、document、process、policy"
                    },
                    "related_to": {
                        "type": "string",
                        "description": "关联的实体名称（可选）"
                    },
                    "relation_type": {
                        "type": "string",
                        "description": "关系类型：belongs_to、manages、works_on、has_skill、follows、related_to、creates、approves"
                    }
                },
                "required": ["entity_name", "entity_type"]
            }
        }
    }
]


def execute_knowledge_graph_tool(tool_name: str, arguments: dict) -> str:
    """执行知识图谱工具"""
    try:
        if tool_name == "query_knowledge_graph":
            query = arguments.get("query", "")
            result = query_knowledge_graph(query)
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif tool_name == "get_entity_info":
            entity_id = arguments.get("entity_id", "")
            entity = get_entity(entity_id)
            if entity:
                relations = get_entity_relations(entity_id)
                return json.dumps({
                    "success": True,
                    "entity": entity,
                    "relations": relations
                }, ensure_ascii=False, indent=2)
            else:
                return json.dumps({"success": False, "error": f"未找到实体: {entity_id}"}, ensure_ascii=False)
        
        elif tool_name == "get_graph_stats":
            result = get_graph_statistics()
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif tool_name == "add_knowledge":
            entity_name = arguments.get("entity_name", "")
            entity_type = arguments.get("entity_type", "")
            related_to = arguments.get("related_to", "")
            relation_type = arguments.get("relation_type", "")
            
            # 生成实体ID
            entity_id = f"{entity_type}_{entity_name}"
            
            # 添加实体
            add_entity(entity_id, entity_type, entity_name)
            
            # 添加关系
            if related_to and relation_type:
                related_id = f"unknown_{related_to}"
                add_relation(entity_id, relation_type, related_id)
            
            return json.dumps({
                "success": True,
                "entity_id": entity_id,
                "message": f"已添加实体: {entity_name}"
            }, ensure_ascii=False)
        
        else:
            return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"工具执行失败: {str(e)}"}, ensure_ascii=False)


# ========== 初始化知识图谱 ==========

def init_knowledge_graph():
    """初始化知识图谱"""
    from tools import EMPLOYEE_DB
    
    entities = load_json(ENTITY_FILE)
    if not entities:
        build_from_employee_data()
        return {"success": True, "message": "知识图谱已初始化"}
    return {"success": True, "message": "知识图谱已存在"}
