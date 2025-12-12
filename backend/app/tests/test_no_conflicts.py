from pathlib import Path
import subprocess

CONFLICT_MARKERS = ("<<<<<<< ", "=======", ">>>>>>>")


def _tracked_files(root: Path) -> list[Path]:
    """Return a list of tracked files to avoid scanning vendored/node artifacts."""
    output = subprocess.check_output(["git", "ls-files"], cwd=root, text=True)
    return [root / line.strip() for line in output.splitlines() if line.strip()]


def test_no_merge_conflict_markers() -> None:
    root = Path(__file__).resolve().parents[2]
    current_file = Path(__file__).resolve().relative_to(root)
    offending_files: list[str] = []

    for path in _tracked_files(root):
        relative = path.relative_to(root)
        if relative == current_file:
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        hit = next((m for m in CONFLICT_MARKERS if m in text), None)
        if hit:
            offending_files.append(f"{relative} (found '{hit.strip()}')")

    assert not offending_files, f"Merge conflict markers found in: {offending_files}"
