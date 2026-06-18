import json
import sys
from pathlib import Path


REQUIRED_FIELDS = [
    "course",
    "category",
    "title",
    "type",
    "date",
    "path",
    "source",
    "tags",
    "description",
]


REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "data" / "files.json"


def main():
    errors = []

    if not INDEX_PATH.exists():
        print("验证失败：data/files.json 不存在。")
        return 1

    try:
        with INDEX_PATH.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except json.JSONDecodeError as exc:
        print(f"验证失败：data/files.json 不是合法 JSON：{exc}")
        return 1

    if not isinstance(records, list):
        print("验证失败：data/files.json 必须是 JSON 数组。")
        return 1

    seen_paths = set()
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"第 {index} 条记录必须是对象。")
            continue

        for field in REQUIRED_FIELDS:
            if field not in record or record[field] in ("", None):
                errors.append(f"第 {index} 条记录缺少必填字段：{field}")

        tags = record.get("tags")
        if "tags" in record and not isinstance(tags, list):
            errors.append(f"第 {index} 条记录的 tags 必须是数组。")

        note_id = record.get("note_id")
        if note_id is not None and not isinstance(note_id, str):
            errors.append(f"第 {index} 条记录的 note_id 必须是字符串。")

        path_value = record.get("path")
        if not path_value:
            continue

        relative_path = Path(path_value)
        if relative_path.is_absolute():
            errors.append(f"第 {index} 条记录 path 应为仓库内相对路径：{path_value}")
            continue

        if path_value in seen_paths:
            errors.append(f"重复路径：{path_value}")
        seen_paths.add(path_value)

        file_path = REPO_ROOT / relative_path
        if not file_path.exists():
            errors.append(f"文件不存在：{path_value}")

    if errors:
        print("验证失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("验证通过：data/files.json 格式正确，所有文件路径都存在。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
