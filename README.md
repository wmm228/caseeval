# Teaching Case Generator

## Dataset Access

You can access the generated teaching cases and related resources via the following link:
[Google Drive Folder](https://drive.google.com/drive/folders/11U79vXjey2yFRTrjCq8iV3sZbuVDizKr?usp=drive_link)

## Project Structure

```
case_generator/
├── config.py                 # Configuration file (API keys, model list, domain mapping)
├── generator.py              # Main generation script
├── test_api.py               # API testing script
├── prompts/                  # Prompt templates
│   ├── __init__.py
│   ├── simple.py            # Simple prompt (without expert examples)
│   ├── cot.py               # Chain-of-Thought prompt
│   └── gjmz.py              # Outline-Detail (GJMZ) method (Two-stage)
├── data/                     # Domain and topic data
│   ├── SE/SE.txt
│   ├── AI/AI.txt
│   ├── Algorithm/Algorithm.txt
│   ├── Architecture/Architecture.txt
│   ├── DataManagement/DataManagement.txt
│   └── Society/Society.txt
├── examples/                 # Expert examples (one per domain)
│   ├── SE_example.md
│   ├── AI_example.md
│   ├── Algorithm_example.md
│   ├── Architecture_example.md
│   ├── DataManagement_example.md
│   └── Society_example.md
└── outputs/                  # Generation results
    └── {model}/              # Grouped by model
        ├── {domain}_summary.json
        ├── simple/{domain}/  # Simple prompt results
        ├── cot/{domain}/     # Chain-of-Thought results
        └── gjmz/{domain}/    # Outline-Detail results
```

## Quick Start

### 1. Configure API Key

Edit `config.py` and enter your API key:

```python
API_KEY = "YOUR_API_KEY"
```

### 2. Prepare Expert Examples

Rename and place expert example files into the `examples/` directory:
- `SE_example.md` - Software Engineering
- `AI_example.md` - Artificial Intelligence
- `Algorithm_example.md` - Algorithmic Foundations
- `Architecture_example.md` - Architecture and Organization
- `DataManagement_example.md` - Data Management
- `Society_example.md` - Society, Ethics and Professionalism

### 3. Test API Connection

```bash
python test_api.py
```

### 4. Generate Cases

```bash
# Test a single case
python generator.py --domain SE --topic "Calendar Generator" --model qwen

# Generate all cases for a domain
python generator.py --domain SE --model qwen --all

# List topics
python generator.py --domain SE --list-topics
```

## Command Arguments

| Argument | Description | Options |
|----------|-------------|---------|
| `--domain` | Domain code | SE, AI, Algorithm, Architecture, DataManagement, Society |
| `--topic` | Case topic | Topic name corresponding to the domain txt file |
| `--model` | Model code | qwen, ernie, hunyuan, doubao, minimax, glm |
| `--all` | Generate all cases for the domain | No value required |
| `--list-topics` | List topics | No value required |

## Three Prompting Methods

| Method | Description | Uses Expert Example |
|--------|-------------|---------------------|
| simple | Simple prompt, only writing requirements | ❌ No |
| cot | Chain-of-Thought prompt, step-by-step thinking | ✅ Yes |
| gjmz | Outline-Detail (GJMZ) method, two-stage generation | ✅ Yes |

## Output Structure

```
outputs/
└── qwen/                           # Model name
    ├── SE_summary.json             # Domain summary
    ├── simple/                     # Method
    │   └── SE/                     # Domain
    │       ├── Calendar Generator.md
    │       └── ...
    ├── cot/
    │   └── SE/
    │       └── ...
    └── gjmz/
        └── SE/
            ├── Calendar Generator_outline.md  # Outline
            ├── Calendar Generator.md          # Complete case
            └── ...
```

## Token Statistics

Token usage is counted for each generation, and a summary is output after batch generation:

```
Token Statistics: Input=12345 | Output=67890 | Total=80235
```

## Available Models

| Code | Model Name |
|------|------------|
| qwen | qwen-plus |
| ernie | ernie-4.0-8k |
| hunyuan | hunyuan-pro |
| doubao | doubao-pro-32k |
| minimax | minimax-abab6.5s-chat |
| glm | glm-4-plus |

## Notes

1. Ensure expert example filenames match the `EXAMPLE_FILES` mapping in `config.py`.
2. Batch generation automatically adds a 1-second interval to avoid rate limits.
3. Failed generations automatically retry 3 times with increasing intervals.
