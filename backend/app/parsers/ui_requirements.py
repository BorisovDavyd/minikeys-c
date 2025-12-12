from typing import List


def parse_ui_requirements(text: str) -> List[str]:
    """Very small parser that splits requirements into bullet-like items."""
    parts = []
    for line in text.splitlines():
        line = line.strip("- ")
        if not line:
            continue
        parts.append(line)
    return parts
