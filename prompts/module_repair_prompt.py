def build_module_repair_prompt(original_code,errors):

    return f'''
Repair the following Python module.

Current code:

{original_code}

Errors:

{errors}

Rules:

1. Preserve original architecture.
2. Preserve module responsibility.
3. Fix ONLY listed problems.
4. Keep code minimal.
5. Output ONLY valid Python code.
'''