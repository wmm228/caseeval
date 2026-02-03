# prompts/cot.py
# Chain-of-Thought Prompt Template

COT_PROMPT = '''You are an expert in writing computing teaching cases, specializing in organizing case content based on the "Abstraction-Theory-Design" three-form structure. You can transform research problems into teachable and evaluable structured cases, and integrate professional conduct into the entire process of modeling, argumentation, and design implementation.

The case must include the following parts (titles must be consistent and in fixed order):

1. Teaching Objectives
2. Three Forms of Abstraction, Theory, and Design in this Case
3. Professional Conduct
4. Ways to Motivate, Awaken, and Encourage Students
5. Exercises

[Chain of Thought]
Please think step-by-step before outputting the final case text. Let's think step by step.

Step 1: Teaching Objectives
- Select X from Bloom Knowledge Dimensions
- Select Y from Bloom Cognitive Dimensions
- Formulate a one-sentence "Teaching Objective" embodying X and Y
- Clarify the capability output of this case (Modeling/Argumentation/Design Implementation or combination)

Step 2: Abstraction Form
- Summarize the real scenario and requirement background in one sentence
- Clarify input, output, constraints, and goals
- Design formal model tuple: Model = (...)
- Write down meaning, range, and constraint points for each element
- If algorithm process/steps are needed, list key steps and ensure variables are consistent with Model

Step 3: Theory Form
- Determine if formal argumentation is needed (Yes/No)
- Provide core principle points supporting the conceptual model
- If "Yes": List the main line and key conclusions for Definition/Assumption/Theorem/Proof, and explain key variables for complexity analysis
- If "No": List argumentation points, applicable boundaries, and possible cost/complexity caliber

Step 4: Design Form
- Determine if Python delivery is needed (Yes/No)
- Requirement analysis points: Functions, constraints, and acceptance methods
- Implementation plan points: Modules/Key functions/Data structures or engineering deliverable list
- Testing idea points: At least 1 item each for Normal/Boundary/Abnormal
- If "Yes": Plan the Python implementation and test case coverage points

Step 5: Professional Conduct
- Determine final 3–5 items from CS2023 Conduct List
- Write down embodiment links (Modeling/Argumentation/Implementation/Testing/Review) for each conduct
- Write down evaluation method points (Checklist, Code review points, Reproducible experiments, etc.) for each conduct
- List student common problems and improvement handle points

Step 6: Ways to Motivate, Awaken, and Encourage Students
- List at least 3 executable practices, and bind them to specific links of this topic respectively
- Bind at least 1 item of social responsibility/ethics/compliance and engineering trade-offs to this topic
- Provide classroom organization method points (Discussion, Comparative experiment, Review, etc.)

Step 7: Exercises
- List at least 5 open-ended question points
- Question coverage: Model extension, Questioning assumptions, Engineering trade-offs, Ethics compliance, Experimental design
- Write a one-sentence evaluation focus for each question (Look at what, rather than a unique answer)

[/Chain of Thought]

Bloom Knowledge Dimensions: Factual Knowledge, Conceptual Knowledge, Procedural Knowledge, Metacognitive Knowledge

Bloom Cognitive Dimensions: Remember, Understand, Apply, Analyze, Evaluate, Create

CS2023 Conduct List: Perseverance, Initiative, Collaboration, Effective Communication, Self-directed Learning, Responsibility, Adaptability, Innovation, Rigor, Agility, Creativity

Expert Example (For structure learning only, do not copy content):
Domain: {example_domain}
Case Topic: {example_topic}
Case Content:
{example_content}

Please generate a teaching case based on the following input. Output only the final case text, without any explanation or reasoning process.
Domain: {domain}
Case Topic: {topic}'''


def get_cot_prompt(domain: str, topic: str, example_domain: str, example_topic: str, example_content: str) -> str:
    return COT_PROMPT.format(
        domain=domain,
        topic=topic,
        example_domain=example_domain,
        example_topic=example_topic,
        example_content=example_content
    )
