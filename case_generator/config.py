# config.py
# API配置和模型列表

# API配置
API_KEY = "sk-9ZxzEXFBPm3NqguTGE3AQtma8EU4DrMxrAljxVwlJHyM1Xtm"  # 替换为你的API key
# API_KEY = "sk-HfR6iCIlpzt2qJcWsKnKJBcm9e193ofSimofkq6VTqHfJ9pw"  # 替换为你的API key
BASE_URL = "https://api.agicto.cn/v1"

# 生成模型列表（使用普通模型，避免thinking模型的特殊参数问题）
GEN_MODELS = {
    "qwen": "qwen3-next-80b-a3b-instruct",
    "ernie": "ernie-x1-turbo-32k",
    "hunyuan": "hunyuan-t1-latest",
    "doubao": "Doubao-Seed-1.6",
    "minimax": "minimax-m2",
    "glm": "glm-4-plus",
}

# 评估模型列表
EVAL_MODELS = {
    "gpt-5": "gpt-5.1",
    "gemini-3": "gemini-3-pro-preview",
    "deepseek-v3": "deepseek-v3.2",
    "kimi-k2": "kimi-k2-0711-preview",
}

# 领域映射（文件夹名 -> 中文名）
DOMAINS = {
    "SE": "软件工程",
    "AI": "人工智能",
    "Algorithm": "算法基础",
    "Architecture": "体系结构与组织",
    "DataManagement": "数据管理",
    "Society": "社会、伦理与职业化",
}

# 专家案例文件映射（领域代码 -> 文件名）
EXAMPLE_FILES = {
    "SE": "SE_example.md",
    "AI": "AI_example.md",
    "Algorithm": "Algorithm_example.md",
    "Architecture": "Architecture_example.md",
    "DataManagement": "DataManagement_example.md",
    "Society": "Society_example.md",
}

# 专家案例选题（用于提示中显示）
EXAMPLE_TOPICS = {
    "SE": "数据分析库性能测试程序",
    "AI": "智能驾驶中的卡尔曼滤波形式模型与算法",
    "Algorithm": "求最小生成树的Prim形式模型与算法",
    "Architecture": "Base64邮件编码",
    "DataManagement": "二十大报告中英文文本信息熵计算",
    "Society": "计算机科技史：创新与发展中的中国力量",
}

# 提示方法
PROMPT_METHODS = ["simple", "cot", "gjmz"]
