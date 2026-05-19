import re


def extract_code(text: str) -> str:
    fenced = re.findall(r"```python(.*?)```", text, re.DOTALL)
    if fenced:
        return fenced[0].strip()

    fenced_any = re.findall(r"```(.*?)```", text, re.DOTALL)
    if fenced_any:
        return fenced_any[0].strip()

    return text.strip()
