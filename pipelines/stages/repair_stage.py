from prompts.module_repair_prompt import build_module_repair_prompt
from utils.code_utils import extract_code


def repair_code(llm, code, errors):
    
    prompt = build_module_repair_prompt(code, errors)
    raw = llm.generate("", prompt)

    return extract_code(raw)