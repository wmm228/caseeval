# prompts/simple.py
# Simple Prompt Template (No Expert Example)

SIMPLE_PROMPT = '''You are an expert in writing computing teaching cases, specializing in organizing case content based on the "Abstraction-Theory-Design" three-form structure. You can transform research problems into teachable and evaluable structured cases, and integrate professional conduct into the entire process of modeling, argumentation, and design implementation.

The case must include the following parts (titles must be consistent and in fixed order):

1. Teaching Objectives
2. Three Forms of Abstraction, Theory, and Design in this Case
3. Professional Conduct
4. Ways to Motivate, Awaken, and Encourage Students
5. Exercises

Writing Requirements:

- "Teaching Objectives": Align with the Knowledge Dimension and Cognitive Process Dimension of Bloom's Taxonomy. Write a clear one-sentence learning objective.
- "Three Forms of Abstraction, Theory, and Design in this Case": Must include three subheadings and output in order:
    1. Abstraction Form: Provide a problem description of the real scenario, and give a formal model tuple (Model = (...)) and the meaning of each element; algorithm processes or steps can be provided.
    2. Theory Form: Explain the core principles supporting the conceptual model; if the topic requires formal argumentation, provide definitions/assumptions/propositions(theorems)/proofs, and complexity analysis; if not, provide principle explanation, argumentation points, and applicable boundaries.
    3. Design Form: Provide requirements analysis, implementation plan, and testing ideas; if you think an executable program is needed as a deliverable, provide Python implementation and test cases; if not, use text to explain reasonable engineering deliverables.
- "Professional Conduct": Select 3–5 items from the CS2023 Conduct List, explaining how students demonstrate them during the learning process and how to evaluate them.
- "Ways to Motivate, Awaken, and Encourage Students": At least 3 executable practices, such as combining social responsibility/ethics/compliance with engineering trade-offs in this topic.
- "Exercises": At least 5 questions, all open-ended.

Bloom Knowledge Dimensions: Factual Knowledge, Conceptual Knowledge, Procedural Knowledge, Metacognitive Knowledge

Bloom Cognitive Dimensions: Remember, Understand, Apply, Analyze, Evaluate, Create

CS2023 Conduct List: Perseverance, Initiative, Collaboration, Effective Communication, Self-directed Learning, Responsibility, Adaptability, Innovation, Rigor, Agility, Creativity

Please generate a teaching case based on the following input. Output only the final case text, without any explanation or reasoning process.
Domain: {domain}
Case Topic: {topic}'''


def get_simple_prompt(domain: str, topic: str, **kwargs) -> str:
    """Simple prompt does not require expert examples"""
    return SIMPLE_PROMPT.format(domain=domain, topic=topic)
