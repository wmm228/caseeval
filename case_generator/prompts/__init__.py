# prompts/__init__.py
from .simple import get_simple_prompt
from .cot import get_cot_prompt
from .gjmz import get_gjmz_stage1_prompt, get_gjmz_stage2_prompt
from .eval import get_eval_prompt

__all__ = [
    'get_simple_prompt',
    'get_cot_prompt', 
    'get_gjmz_stage1_prompt',
    'get_gjmz_stage2_prompt',
    'get_eval_prompt'
]
