# config.py
# API Configuration and Model List

# API Configuration
API_KEY = ""  # Replace with your API key
BASE_URL = ""

# Generation Model List (Use standard models to avoid special parameter issues with thinking models)
GEN_MODELS = {
    "qwen": "qwen3-next-80b-a3b-instruct",
    "ernie": "ernie-x1-turbo-32k",
    "hunyuan": "hunyuan-t1-latest",
    "doubao": "Doubao-Seed-1.6",
    "minimax": "minimax-m2",
    "glm": "glm-4-plus",
}

# Evaluation Model List
EVAL_MODELS = {
    "gpt-5": "gpt-5.1",
    "gemini-3": "gemini-3-pro-preview",
    "deepseek-v3": "deepseek-v3.2",
    "kimi-k2": "kimi-k2-0711-preview",
}

# Domain Mapping (Folder name -> English name)
DOMAINS = {
    "SE": "Software Engineering",
    "AI": "Artificial Intelligence",
    "Algorithm": "Algorithmic Foundations",
    "Architecture": "Architecture and Organization",
    "DataManagement": "Data Management",
    "Society": "Society, Ethics and Professionalism",
}

# Expert Example File Mapping (Domain code -> Filename)
EXAMPLE_FILES = {
    "SE": "SE_example.md",
    "AI": "AI_example.md",
    "Algorithm": "Algorithm_example.md",
    "Architecture": "Architecture_example.md",
    "DataManagement": "DataManagement_example.md",
    "Society": "Society_example.md",
}

# Expert Example Topics (For display in prompts)
EXAMPLE_TOPICS = {
    "SE": "Performance Testing Program for Data Analysis Library",
    "AI": "Kalman Filter Formal Model and Algorithm in Intelligent Driving",
    "Algorithm": "Prim's Formal Model and Algorithm for Minimum Spanning Tree",
    "Architecture": "Base64 Email Encoding",
    "DataManagement": "Information Entropy Calculation of Chinese and English Text in the 20th National Congress Report",
    "Society": "History of Computer Science and Technology: Chinese Power in Innovation and Development",
}

# Prompt Methods
PROMPT_METHODS = ["simple", "cot", "gjmz"]
