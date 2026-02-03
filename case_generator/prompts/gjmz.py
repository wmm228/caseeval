# prompts/gjmz.py
# Outline-Detail (GJMZ) Method Prompt Template (Two Stages)

GJMZ_STAGE1_PROMPT = '''You are a computing teaching case architect, specializing in planning case structure based on the "Abstraction-Theory-Design" three-form structure. You can transform subject knowledge points into teachable and evaluable structured frameworks, and integrate professional conduct into the entire process of modeling, argumentation, and engineering implementation.

Please generate a structured case outline based on the input subject domain and case topic, referring to the structure and depth of high-level expert cases.

【Outline Format】

## 1. Teaching Objectives
- Knowledge Dimension: (Select 1 from Factual/Conceptual/Procedural/Metacognitive Knowledge)
- Cognitive Dimension: (Select 1 from Remember/Understand/Apply/Analyze/Evaluate/Create)
- Capability Output: List 3 observable and evaluable capabilities (Start with verbs)

## 2. Abstraction Form
- Problem Scenario: (One sentence describing the real scenario)
- Input/Output/Constraints/Goal: (One sentence for each)
- Formal Model: Model = (Element 1, Element 2, ...)
- Meaning of each element: (One sentence for each element)
- Whether algorithm process is needed: Yes/No

## 3. Theory Form
- Whether formal argumentation is needed: Yes/No
- Core Principle: (One sentence)
- If formal argumentation is needed:
    - Premises/Axioms: (List items)
    - Propositions/Theorems: (List core conclusions)
    - Proof Idea: (One sentence)
    - Complexity: Time O(?), Space O(?)
- If formal argumentation is not needed:
    - Argumentation Points: (List items)
    - Applicable Boundaries: (Explain)

## 4. Design Form
- Whether Python code is needed: Yes/No
- Requirement Analysis: (List 4 items: Function/Performance/Boundary/Security or Ethics)
- Implementation Points: (Core Module/Function/Class Names)
- Testing Points: (1 item each for Normal/Boundary/Abnormal)

## 5. Professional Conduct
- Selected Conduct: (List 3-5 items)
- Embodiment Link: (Which one of Modeling/Argumentation/Implementation/Testing/Review corresponds to each conduct)
- Evaluation Method: (Evaluation method for each conduct)

## 6. Ways to Motivate, Awaken, and Encourage
- Executable Paths: (List 3 items)
- Classroom Organization Method: (Suggestion)

## 7. Exercises
- Model Extension Question: Direction is ___
- Questioning Assumption Question: Direction is ___
- Engineering Trade-off Question: Direction is ___
- Ethics Compliance Question: Direction is ___
- Experimental Design Question: Direction is ___

【Reference Case (Refer to its structure depth and content granularity to plan the outline)】
Domain: {example_domain}
Case Topic: {example_topic}
Case Content:
{example_content}

【Input】
Domain: {domain}
Case Topic: {topic}

Output only the outline, without any explanation.'''


GJMZ_STAGE2_PROMPT = '''You are an expert in writing computing teaching cases, specializing in organizing case content based on the "Abstraction-Theory-Design" three-form structure. You can transform research problems into teachable and evaluable structured cases, and integrate professional conduct into the entire process of modeling, argumentation, and engineering implementation.

Please strictly follow every design decision in the provided 【Case Outline】 to expand and write a complete teaching case.

You must strictly imitate the writing style, expression, paragraph structure, and content depth of the 【Reference Case】. The reference case is a benchmark written by high-level experts, and your output should be highly consistent with it in structure, style, and professionalism.

【Reference Case】
Domain: {example_domain}
Case Topic: {example_topic}
Case Content:
{example_content}

【Input】
Domain: {domain}
Case Topic: {topic}

【Case Outline】
{outline}

Output only the case text, without any explanation.'''


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
