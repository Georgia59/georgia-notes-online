import argparse
import json
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

SOURCE_FILE_EXTENSIONS = {
    ".ppt",
    ".pptx",
    ".pdf",
    ".doc",
    ".docx",
}

RAW_SOURCE_MARKERS = ("原始", "未整理", "课件原文", "教材原文", "扫描原文")

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


def is_collection(record):
    return record.get("kind") == "collection" or record.get("type") == "Collection" or isinstance(record.get("items"), list)


def item_files(item):
    if isinstance(item.get("files"), list) and item["files"]:
        return item["files"]
    if item.get("path"):
        return [{"title": item.get("title"), "type": item.get("type"), "path": item.get("path")}]
    return []


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


def check_public_path(path_value, source_value, label):
    errors = []
    if not path_value:
        return errors

    path_text = str(path_value)
    if Path(path_text).is_absolute():
        errors.append(f"{label} path 是绝对路径：{path_text}")
    if not path_text.startswith("files/"):
        errors.append(f"{label} path 不在 files/ 下：{path_text}")
    if any(pattern.search(path_text) for pattern in LOCAL_PATH_PATTERNS):
        errors.append(f"{label} path 含本地路径：{path_text}")
    if any(pattern.search(str(source_value)) for pattern in LOCAL_PATH_PATTERNS):
        errors.append(f"{label} source 含本地路径：{source_value}")

    file_path = REPO_ROOT / path_text
    if file_path.exists():
        suffix = file_path.suffix.lower()
        if suffix in SOURCE_FILE_EXTENSIONS and any(marker in str(source_value) for marker in RAW_SOURCE_MARKERS):
            errors.append(f"{label} 可能是原始资料而非整理成品：{path_text}")

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

        source_value = str(record.get("source", ""))
        errors.extend(check_public_path(record.get("path", ""), source_value, f"第 {index} 条"))

        if is_collection(record):
            items = record.get("items", [])
            if isinstance(items, list):
                for item_index, item in enumerate(items, start=1):
                    if isinstance(item, dict):
                        for file_index, file in enumerate(item_files(item), start=1):
                            errors.extend(
                                check_public_path(
                                    file.get("path", ""),
                                    source_value,
                                    f"第 {index} 条 items[{item_index}].files[{file_index}]",
                                )
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
