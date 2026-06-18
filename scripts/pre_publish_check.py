import json
import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "data" / "files.json"

PUBLIC_TEXT_EXTENSIONS = {
    ".html",
    ".css",
    ".js",
    ".json",
    ".md",
    ".txt",
    ".csv",
    ".svg",
}

SKIP_DIRS = {
    ".git",
    "local-sources",
    "review",
    "work",
    "outputs",
    "__pycache__",
}

RAW_SOURCE_EXTENSIONS = {
    ".ppt",
    ".pptx",
    ".pdf",
    ".doc",
    ".docx",
}

LOCAL_PATH_PATTERNS = [
    re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/](?![\\/])[^\s\"'<>]+"),
    re.compile(r"\\\\[A-Za-z0-9_.-]+\\[^\s\"'<>]+"),
    re.compile(r"/Users/[^\s\"'<>]+"),
    re.compile(r"/home/[^\s\"'<>]+"),
]

PRIVACY_PATTERNS = [
    ("疑似手机号", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("疑似身份证号", re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")),
    ("疑似病历号", re.compile(r"(病历号|住院号|门诊号|检查号)\s*[:：]?\s*[A-Za-z0-9-]{4,}")),
]


def iter_public_text_files():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(REPO_ROOT).parts
        if any(part in SKIP_DIRS for part in relative_parts):
            continue
        if path.suffix.lower() in PUBLIC_TEXT_EXTENSIONS:
            yield path


def check_text_file(path):
    errors = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return errors

    relative = path.relative_to(REPO_ROOT).as_posix()
    for pattern in LOCAL_PATH_PATTERNS:
        match = pattern.search(text)
        if match:
            errors.append(f"{relative} 含疑似本地路径：{match.group(0)}")

    for label, pattern in PRIVACY_PATTERNS:
        match = pattern.search(text)
        if match:
            errors.append(f"{relative} 含{label}：{match.group(0)}")

    return errors


def check_index():
    errors = []
    if not INDEX_PATH.exists():
        return ["data/files.json 不存在。"]

    try:
        records = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"data/files.json 不是合法 JSON：{exc}"]

    if not isinstance(records, list):
        return ["data/files.json 必须是 JSON 数组。"]

    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"第 {index} 条索引不是对象。")
            continue

        path_value = str(record.get("path", ""))
        source_value = str(record.get("source", ""))

        if Path(path_value).is_absolute():
            errors.append(f"第 {index} 条 path 是绝对路径：{path_value}")
        if path_value and not path_value.startswith("files/"):
            errors.append(f"第 {index} 条 path 不在 files/ 下：{path_value}")
        if any(pattern.search(source_value) for pattern in LOCAL_PATH_PATTERNS):
            errors.append(f"第 {index} 条 source 含本地路径：{source_value}")

        file_path = REPO_ROOT / path_value if path_value else None
        if file_path and file_path.exists():
            suffix = file_path.suffix.lower()
            if suffix in RAW_SOURCE_EXTENSIONS and "整理" not in source_value and "成品" not in source_value:
                errors.append(
                    f"第 {index} 条可能是原始资料而非整理成品：{path_value}。"
                )

    return errors


def main():
    parser = argparse.ArgumentParser(description="发布前检查公开区是否存在明显隐私或路径风险。")
    parser.parse_args()

    errors = []
    errors.extend(check_index())
    for path in iter_public_text_files():
        errors.extend(check_text_file(path))

    if errors:
        print("发布前检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("发布前检查通过：未发现明显本地路径、隐私字段或索引发布风险。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
