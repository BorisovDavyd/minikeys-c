from pathlib import Path

CONFLICT_MARKERS = ("<<<<<<< ", "=======", ">>>>>>>")


def test_no_merge_conflict_markers() -> None:
    root = Path(__file__).resolve().parents[2]
    excluded_dirs = {".git", "node_modules", "dist", "__pycache__", ".venv"}
    current_file = Path(__file__).resolve().relative_to(root)
    offending_files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in excluded_dirs for part in path.parts):
            continue
        relative = path.relative_to(root)
        if relative == current_file:
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        if any(marker in text for marker in CONFLICT_MARKERS):
            offending_files.append(relative)
    assert not offending_files, f"Merge conflict markers found in: {offending_files}"
