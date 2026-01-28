# 教学案例生成器

## 项目结构

```
case_generator/
├── config.py                 # 配置文件（API密钥、模型列表、领域映射）
├── generator.py              # 主生成脚本
├── test_api.py               # API测试脚本
├── prompts/                  # 提示模板
│   ├── __init__.py
│   ├── simple.py            # 简单提示（不含专家案例）
│   ├── cot.py               # 思维链提示
│   └── gjmz.py              # 纲举目张法（两阶段）
├── data/                     # 领域和选题数据
│   ├── SE/SE.txt
│   ├── AI/AI.txt
│   ├── Algorithm/Algorithm.txt
│   ├── Architecture/Architecture.txt
│   ├── DataManagement/DataManagement.txt
│   └── Society/Society.txt
├── examples/                 # 专家案例（每个领域一个）
│   ├── SE_example.md
│   ├── AI_example.md
│   ├── Algorithm_example.md
│   ├── Architecture_example.md
│   ├── DataManagement_example.md
│   └── Society_example.md
└── outputs/                  # 生成结果
    └── {model}/              # 按模型分
        ├── {domain}_summary.json
        ├── simple/{domain}/  # 简单提示结果
        ├── cot/{domain}/     # 思维链结果
        └── gjmz/{domain}/    # 纲举目张结果
```

## 快速开始

### 1. 配置API密钥

编辑 `config.py`，填入你的API密钥：

```python
API_KEY = "你的API_KEY"
```

### 2. 准备专家案例

将专家案例文件重命名并放入 `examples/` 目录：
- `SE_example.md` - 软件工程
- `AI_example.md` - 人工智能
- `Algorithm_example.md` - 算法基础
- `Architecture_example.md` - 体系结构与组织
- `DataManagement_example.md` - 数据管理
- `Society_example.md` - 社会、伦理与职业化

### 3. 测试API连接

```bash
python test_api.py
```

### 4. 生成案例

```bash
# 测试单个案例
python generator.py --domain SE --topic "日历生成器" --model qwen

# 生成一个领域的所有案例
python generator.py --domain SE --model qwen --all

# 查看选题列表
python generator.py --domain SE --list-topics
```

## 命令参数

| 参数 | 说明 | 可选值 |
|------|------|--------|
| `--domain` | 领域代码 | SE, AI, Algorithm, Architecture, DataManagement, Society |
| `--topic` | 案例选题 | 对应领域txt文件中的选题名 |
| `--model` | 模型代码 | qwen, ernie, hunyuan, doubao, minimax, glm |
| `--all` | 生成该领域所有案例 | 无需值 |
| `--list-topics` | 列出选题 | 无需值 |

## 三种提示方法

| 方法 | 说明 | 是否使用专家案例 |
|------|------|------------------|
| simple | 简单提示，只有写作要求 | ❌ 不使用 |
| cot | 思维链提示，分步思考 | ✅ 使用 |
| gjmz | 纲举目张法，两阶段生成 | ✅ 使用 |

## 输出结构

```
outputs/
└── qwen/                           # 模型名
    ├── SE_summary.json             # 领域汇总
    ├── simple/                     # 方法
    │   └── SE/                     # 领域
    │       ├── 日历生成器.md
    │       └── ...
    ├── cot/
    │   └── SE/
    │       └── ...
    └── gjmz/
        └── SE/
            ├── 日历生成器_outline.md  # 纲要
            ├── 日历生成器.md          # 完整案例
            └── ...
```

## Token统计

每次生成都会统计Token使用量，批量生成完成后会输出汇总：

```
Token统计: 输入=12345 | 输出=67890 | 总计=80235
```

## 可用模型

| 代码 | 模型名称 |
|------|----------|
| qwen | qwen-plus |
| ernie | ernie-4.0-8k |
| hunyuan | hunyuan-pro |
| doubao | doubao-pro-32k |
| minimax | minimax-abab6.5s-chat |
| glm | glm-4-plus |

## 注意事项

1. 确保专家案例文件名与 `config.py` 中的 `EXAMPLE_FILES` 映射一致
2. 批量生成时会自动添加1秒间隔避免请求过快
3. 生成失败会自动重试3次，每次间隔递增
