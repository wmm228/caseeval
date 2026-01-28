# prompts/gjmz.py
# 纲举目张法提示模板（两阶段）

GJMZ_STAGE1_PROMPT = '''你是一名计算学科教学案例架构师，擅长基于"抽象—理论—设计"三形态规划案例结构，能够将学科知识点转化为可教学、可评测的结构化框架，并将专业品行融入建模、论证与工程实现的全过程。

请根据输入的学科领域与案例选题，参考高水平专家案例的结构与深度，生成一份结构化的案例纲要。

【纲要格式】

## 1. 教学目标
- 知识维度：（从事实性知识/概念性知识/程序性知识/元认知知识中选1个）
- 认知维度：（从记忆/理解/应用/分析/评估/创造中选1个）
- 能力产出：列出3项可观察、可评价的能力（用动词开头）

## 2. 抽象形态
- 问题场景：（一句话描述真实场景）
- 输入/输出/约束/目标：（各一句话）
- 形式模型：Model = (元素1, 元素2, ...)
- 各元素含义：（每个元素一句话）
- 是否需要算法过程：是/否

## 3. 理论形态
- 是否需要形式化论证：是/否
- 核心原理：（一句话）
- 若需要形式化论证：
    - 前提/公理：（列出条目）
    - 命题/定理：（列出核心结论）
    - 证明思路：（一句话）
    - 复杂度：时间O(?)，空间O(?)
- 若不需要形式化论证：
    - 论证要点：（列出）
    - 适用边界：（说明）

## 4. 设计形态
- 是否需要Python代码：是/否
- 需求分析：（列出4条：功能/性能/边界/安全或伦理）
- 实现要点：（核心模块/函数/类名称）
- 测试要点：（正常/边界/异常各1条）

## 5. 专业品行
- 选定品行：（列出3-5个）
- 体现环节：（每个品行对应建模/论证/实现/测试/复盘中的哪个）
- 评价方式：（每个品行的评价方式）

## 6. 激励、唤醒和鼓励
- 可执行路径：（列出3条）
- 课堂组织方式：（建议）

## 7. 习题
- 模型扩展题：方向是___
- 质疑假设题：方向是___
- 工程权衡题：方向是___
- 伦理合规题：方向是___
- 实验设计题：方向是___

【参考案例（参考其结构深度与内容粒度来规划纲要）】
学科领域：{example_domain}
案例选题：{example_topic}
案例内容：
{example_content}

【输入】
学科领域：{domain}
案例选题：{topic}

只输出纲要，不要任何解释。'''


GJMZ_STAGE2_PROMPT = '''你是一名计算学科教学案例撰写专家，擅长基于"抽象—理论—设计"三形态组织案例内容，能够将研究问题转化为可教学、可评测的结构化案例，并将专业品行贯穿于建模、论证与工程实现的全过程。

请根据提供的【案例纲要】，严格按照纲要中的每一项设计决策，展开撰写完整的教学案例。

你必须严格模仿【参考案例】的写作风格、表达方式、段落结构和内容深度。参考案例是高水平专家撰写的标杆，你的输出应在结构、风格、专业性上与其高度一致。

【参考案例】
学科领域：{example_domain}
案例选题：{example_topic}
案例内容：
{example_content}

【输入】
学科领域：{domain}
案例选题：{topic}

【案例纲要】
{outline}

只输出案例正文，不要任何解释。'''


def get_gjmz_stage1_prompt(domain: str, topic: str, example_domain: str, example_topic: str, example_content: str) -> str:
    return GJMZ_STAGE1_PROMPT.format(
        domain=domain,
        topic=topic,
        example_domain=example_domain,
        example_topic=example_topic,
        example_content=example_content
    )


def get_gjmz_stage2_prompt(domain: str, topic: str, example_domain: str, example_topic: str, example_content: str, outline: str) -> str:
    return GJMZ_STAGE2_PROMPT.format(
        domain=domain,
        topic=topic,
        example_domain=example_domain,
        example_topic=example_topic,
        example_content=example_content,
        outline=outline
    )
