from pathlib import Path


def load_markdown(relative_path: str) -> str:
    file_path = Path(relative_path)
    if file_path.exists():
        return file_path.read_text(encoding='utf-8')
    return ""
