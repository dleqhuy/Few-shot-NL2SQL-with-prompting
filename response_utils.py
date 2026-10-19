"""Tolerate chat model formatting without changing the DIN-SQL prompts."""
import re


def classification_parts(text, question):
    match = re.search(r'Label\s*:\s*["\x27`]*(NON-NESTED|NESTED|EASY)\b', text, re.I)
    if not match:
        match = re.search(r'\b(NON-NESTED|NESTED|EASY)\b', text, re.I)
    label = match.group(1).upper() if match else "NESTED"
    sub = re.search(r'questions\s*=\s*\[\s*["\x27](.*?)["\x27]\s*\]', text, re.S)
    return label, sub.group(1) if sub else question


def sql_response(text, select_fragment=False):
    text = text.strip()
    fence = re.search(r'```(?:sql)?\s*\n?(.*?)```', text, re.I | re.S)
    if fence:
        text = fence.group(1).strip()
    text = re.sub(r'^SQL\s*:\s*', '', text, flags=re.I).strip()
    if text.startswith('`') and text.endswith('`'):
        text = text[1:-1].strip()
    if select_fragment and not re.match(r'^(SELECT|WITH)\b', text, re.I):
        text = "SELECT " + text
    return text.replace('\r', ' ').replace('\n', ' ')
