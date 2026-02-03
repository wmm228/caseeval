# prompts/eval.py

EVAL_PROMPT = '''You are a computing teaching case quality assessment expert. You will score a teaching case based on the grading criteria provided below.

Scoring Range: Integer 1-5 for each dimension.

Assessment Dimensions (6 scores in order from top to bottom):
1. Structure Consistency
2. Topic Relevance
3. Content Clarity
4. Concept Completeness (Corresponding to Abstraction Form)
5. Theory Correctness (Corresponding to Theory Form)
6. Design Feasibility (Corresponding to Design Form)

Standard Case Structure (A teaching case must strictly include the following 6 parts):
1. Teaching Objectives
   - Must include Bloom's Knowledge Dimension: Factual, Conceptual, Procedural, Metacognitive Knowledge (None can be missing).
   - Must include Bloom's Cognitive Dimension: Remember, Understand, Apply, Analyze, Evaluate, Create (None can be missing).
2. Three Forms of Abstraction, Theory, and Design in this Case (Core part, must be expanded in detail)
   2.1 Abstraction Form
       - Problem Description: Must have, detailed discussion of the topic (application scenario/background/research question), only one or two sentences description is considered unqualified.
       - Formal Model: Must have, formal tuple abstracting the research question (must be tuple form, e.g. (S, I, O, C)), and the meaning of each element must be clearly defined.
       - Algorithm Process (Optional): If algorithm is involved, full pseudo-code or step description must be included, only listing key steps is considered incomplete.
   2.2 Theory Form
       - Generally includes: Principle reference, Theorem proof, Mathematical formula (Must have derivation process).
       - Complexity Analysis: If there is an algorithm process, detailed time complexity and space complexity analysis must be present (Check correctness and necessity of formulas/theorems), only giving conclusion is considered unqualified.
   2.3 Design Form
       - Python Code (Optional): If technical implementation is involved, code must be complete and runnable, placeholders (like `# TODO`) are strictly prohibited.
       - Test Cases (Optional): If there is code, specific test inputs and expected outputs must be provided.
       - Teaching Design Activity (Optional): If no code (e.g. social subjects), specific implementation scenarios (e.g. aesthetic works etc.) should be included, and must have specific operation steps or evaluation indicators.
3. Professional Conduct
   - Source: CS2023 Professional Conduct Elements (Perseverance, Initiative, Collaboration, Effective Communication, Self-directed Learning, Responsibility, Adaptability, Innovation, Rigor, Agility, Creativity).
   - Assessment: Check if conduct elements are closely integrated with case content, mechanical copying is strictly prohibited.
4. Ways to Motivate, Awaken, and Encourage Students
   - Content: Focus on relevance of subject content with professional conduct or curriculum ideology.
   - Assessment: Content must be specific and vivid, empty slogans are strictly prohibited.
5. Exercises (Open-ended Questions)
   - Must include at least one open-ended question, and the question must have inquiry value.

Common Deduction Items (Checklist, violation of any item must result in deduction):
- [Structure] Missing any of the above 6 parts: Structure Consistency directly deducted to below 3 points.
- [Abstraction] Formal model is not in tuple form, or missing key definitions: Concept Completeness deduct 1-2 points.
- [Abstraction] Algorithm process incomplete, only wrote key parts or pseudo-code non-standard: Concept Completeness deduct 1-2 points.
- [Theory] Has algorithm but missing complexity analysis, or only gives conclusion without derivation: Theory Correctness deduct 1-2 points.
- [Theory] Theory proof missing or logic jump: Theory Correctness deduct 1-2 points.
- [Design] Has code but missing test cases, or test cases have no expected output: Design Feasibility deduct 1-2 points.
- [Design] Code incomplete, unable to run or contains placeholders: Design Feasibility deduct 2-3 points.
- [Content] Existence of irrelevant content (e.g. irrelevant finance/medical scenario discussion): Topic Relevance deduct 1-2 points.
- [Content] Retained "Chain of Thought" thinking process (e.g. "I am thinking...", "First..."): Content Clarity deduct 1-2 points.
- [Content] Problem description too simple (less than 100 words), unclear or logically chaotic: Content Clarity deduct 1-2 points.
- [Content] Content redundancy, existence of large amount of repetitive expressions: Content Clarity deduct 1 point.

Assessment Dimensions and Scoring Criteria (5-point scale):

1) Structure Consistency
- 1 point: Structure seriously missing, three forms mostly missing, other necessary parts also have many omissions, overall framework hard to identify.
- 2 points: Structure incomplete, three forms have obvious omissions or content extremely thin (e.g. only titles), other parts also exist omissions.
- 3 points: Structure basically complete, three forms all involved but content of some form is insufficient (e.g. formal model non-standard, code no test), other parts complete but titles or order adjusted.
- 4 points: Structure complete, three forms content substantial and distinct levels, all parts titles standard, order correct, only minor formatting detail issues.
- 5 points: Structure fully complies with specifications, three forms content complete, in-depth, clear levels, all parts highly consistent with expert cases.

2) Topic Relevance
- 1 point: Content seriously deviates from given topic, discusses wrong domain or concept, most content irrelevant to topic.
- 2 points: Content basically relevant to topic, but exists obvious off-topic parts (e.g. introduced irrelevant scenarios), core concepts although involved, but failed to penetrate throughout three forms.
- 3 points: Content generally on topic, three forms all revolve around topic, but have small amount of irrelevant content (e.g. irrelevant background introduction) or some parts weakly associated with topic.
- 4 points: Content closely sticks to topic, three forms and professional conduct all relevant to topic, narrative always revolves around core concepts, only very few deviations.
- 5 points: Content highly focused, completely on topic, from problem description to formal model, theoretical analysis, design implementation, conduct cultivation all closely revolve around topic.

3) Content Clarity
- 1 point: Expression chaotic, sentences not smooth, logic jumps seriously, professional terms used incorrectly, difficult to understand case content.
- 2 points: Expression relatively vague, some sentences unclear or ambiguous, exists "Chain of Thought" residue (e.g. "I am thinking..."), transition between three forms not natural enough.
- 3 points: Expression basically clear, most content understandable, but exists redundancy, repetition or expression not concise enough, or exists small amount of format errors.
- 4 points: Expression clear and smooth, logic coherent, professional terms used accurately, transition between three forms natural, only few expressions can be optimized.
- 5 points: Expression precise, concise, smooth, logic rigorous, distinct levels, professional terms standard, all content clear at a glance.

4) Concept Completeness (Corresponding to Abstraction Form)
- 1 point: Abstraction form seriously missing, no formal model or model completely wrong, missing algorithm process, key concepts undefined.
- 2 points: Abstraction form incomplete, formal model missing key elements (e.g. not tuple) or element meaning unclear, algorithm process incomplete or concept definition has omissions.
- 3 points: Abstraction form basically complete, has formal model but explanation of some elements not clear enough, has algorithm process but steps not detailed enough (e.g. only list key steps).
- 4 points: Abstraction form relatively complete, formal model standard, element meaning clear, algorithm process clear, concept definition accurate.
- 5 points: Abstraction form complete and standard, formal model rigorous (tuple form and definition complete), algorithm process exhaustive, concept definition accurate and complete, comparable to expert case level.

5) Theory Correctness (Corresponding to Theory Form)
- 1 point: Theory form exists serious errors, core principle explanation wrong, complexity analysis completely wrong, or theorem conclusion exists fundamental fallacy.
- 2 points: Theory form exists obvious errors, principle understanding has deviation, complexity analysis has large discrepancy (e.g. only gives wrong conclusion), affects credibility and teaching value of case.
- 3 points: Theory form basically correct, principle explanation roughly accurate but not deep enough, complexity analysis reasonable but not precise enough or missing derivation process.
- 4 points: Theory form accurate, principle explanation correct and has certain depth, complexity analysis correct and has brief derivation, only very few flaws.
- 5 points: Theory form completely accurate and in-depth, principle argumentation rigorous, complexity analysis precise and derivation complete, can be used as teaching reference material.

6) Design Feasibility (Corresponding to Design Form)
- 1 point: Design form seriously unreasonable, code exists obvious logic errors or unable to run, teaching activity design detached from reality, inoperable.
- 2 points: Design form has large defects, code implementation incomplete (e.g. contains placeholders) or has errors, teaching activity design feasibility low, missing specific operation steps.
- 3 points: Design form basically reasonable, code logic roughly correct but may have small problems, missing test cases or running results, teaching activity design basically feasible but not detailed enough.
- 4 points: Design form reasonable and feasible, code implementation correct, structure clear and has running example, teaching activity design specific, strong operability.
- 5 points: Design form excellent, code standard, efficient, has complete running example and test, teaching activity design complete, innovative, has strong practical guidance value.

Scoring Requirements:
- Must give an integer score of 1-5 for each dimension.
- Strictly prohibited to output Markdown code block markers (e.g. ```json).
- Strictly prohibited to output any explanation, analysis, reasoning process or extra text.
- JSON must contain and only contain the following 6 fields:
  structure_consistency, topic_relevance, content_clarity, concept_completeness, theory_correctness, design_feasibility

# Scoring Reference Example (Few-Shot)
Below are scoring references for "Expression Evaluation" case under different generation qualities. Please carefully read case performance description and corresponding scoring reasons to understand scoring criteria.

【Example 1: Average Quality Case】
**Case Performance**:
- [Structure] Includes teaching objectives, three forms etc. all parts, structure basically complete.
- [Content] Problem description relatively concise, missing detailed concept definition of input, output and constraints.
- [Theory] Algorithm process relatively complete, but completely missing theoretical proof steps or argumentation process.
- [Design] Provided code and test cases, but did not provide test running results.
**Reference Scoring**:
{{
  "structure_consistency": 4,  // Structure complete, but slightly inferior in detail fullness compared to perfect case
  "topic_relevance": 5,        // Content closely sticks to "Expression Evaluation" topic
  "content_clarity": 5,        // Language expression clear and smooth
  "concept_completeness": 3,   // Deduction point: Missing input/output constraint definition
  "theory_correctness": 3,     // Deduction point: Missing proof/argumentation steps
  "design_feasibility": 3      // Deduction point: Missing running results, verification insufficient
}}

【Example 2: Poor Quality Case】
**Case Performance**:
- [Structure] Problem description only one sentence, content extremely thin; algorithm process incomplete, only wrote key parts.
- [Content] Discussion mixed with irrelevant finance scenario discussion; text retained "Chain of Thought" thinking process (e.g. "I am thinking..."), causing reading not smooth.
- [Design] No code, no test cases, only listed some key parameters.
**Reference Scoring**:
{{
  "structure_consistency": 3,  // Structure although full but content thin, not rigorous enough
  "topic_relevance": 4,        // Finance scenario discussion caused slight off-topic
  "content_clarity": 4,        // Chain of Thought residue affected content purity and logic smoothness
  "concept_completeness": 2,   // Serious deduction point: Description too brief, algorithm incomplete
  "theory_correctness": 3,     // Theory explanation not deep enough
  "design_feasibility": 2      // Serious deduction point: No code no test, almost infeasible
}}

【Example 3: High Quality Case】
**Case Performance**:
- [Structure] Structure very complete, distinct levels, content substantial.
- [Content] Problem description detailed, concept definition (input/output/constraints) perfect; includes complete algorithm pseudo-code.
- [Theory] Strictly includes proof steps and complexity analysis, theoretical argumentation rigorous.
- [Design] Includes complete code, detailed test cases and corresponding running results.
**Reference Scoring**:
{{
  "structure_consistency": 5,  // Structure perfect, meets expert standard
  "topic_relevance": 5,        // Highly focused
  "content_clarity": 5,        // Expression precise
  "concept_completeness": 5,   // Concept complete, pseudo-code clear
  "theory_correctness": 5,     // Theory accurate and in-depth
  "design_feasibility": 5      // Design complete, strong operability
}}

Input Information:
Domain: {domain}
Case Topic: {topic}

Case Text to be Evaluated (Possibly Markdown):
{case_content}'''


def get_eval_prompt(domain: str, topic: str, case_content: str, **kwargs) -> str:
    return EVAL_PROMPT.format(domain=domain, topic=topic, case_content=case_content)
