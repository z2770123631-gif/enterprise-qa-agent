# 企业知识库智能问答Agent配置文件

# DeepSeek API配置
DEEPSEEK_API_KEY = "your_api_key_here"
DEEPSEEK_API_BASE = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

# 向量数据库配置
VECTOR_DB_PATH = "vector_db"  # 向量数据库存储路径
CHUNK_SIZE = 500  # 文档分块大小（字符数）
CHUNK_OVERLAP = 50  # 分块重叠字符数

# 文档配置
DOCS_DIR = "documents"  # 企业文档存放目录

# 问答配置
TOP_K = 3  # 检索最相关的文档片段数量
MAX_HISTORY = 10  # 保存的历史对话轮数

# 服务器配置
HOST = "0.0.0.0"
PORT = 8000

# 日志配置
LOG_ENABLED = True
LOG_FILE = "qa_agent.log"
