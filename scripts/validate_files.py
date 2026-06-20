import json
import sys
from pathlib import Path


REQUIRED_FIELDS = [
    "course",
    "category",
    "title",
    "type",
    "date",
    "source",
    "description",
]


REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "data" / "files.json"


def is_collection(record):
    return record.get("kind") == "collection" or record.get("type") == "Collection" or isinstance(record.get("items"), list)


def item_files(item):
    if isinstance(item.get("files"), list) and item["files"]:
        return item["files"]
    if item.get("path"):
        return [
            {
                "title": item.get("title"),
                "type": item.get("type"),
                "path": item.get("path"),
                "downloadUrl": item.get("downloadUrl"),
                "previewUrl": item.get("previewUrl"),
            }
        ]
    return []


def is_external_url(value):
    return str(value).startswith(("https://", "http://"))


def validate_relative_public_path(path_value, label, errors, required=True):
    if not path_value:
        if required:
            errors.append(f"{label} 缺少 path。")
        return None

    relative_path = Path(str(path_value))
    if relative_path.is_absolute():
        errors.append(f"{label} path 应为仓库内相对路径：{path_value}")
        return None
    if not str(path_value).startswith("files/"):
        errors.append(f"{label} path 必须位于 files/ 下：{path_value}")
    return REPO_ROOT / relative_path


def validate_optional_public_url(path_value, label, field_name, errors):
    if not path_value:
        return None

    if is_external_url(path_value):
        return None

    relative_path = Path(str(path_value))
    if relative_path.is_absolute():
        errors.append(f"{label} {field_name} 应为仓库内相对路径：{path_value}")
        return None
    if not (str(path_value).startswith("files/") or str(path_value).startswith("notes/")):
        errors.append(f"{label} {field_name} 必须位于 files/ 或 notes/ 下：{path_value}")
    return REPO_ROOT / relative_path


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
        label = f"第 {index} 条记录"
        if not isinstance(record, dict):
            errors.append(f"{label} 必须是对象。")
            continue

        for field in REQUIRED_FIELDS:
            if field not in record or record[field] in ("", None):
                errors.append(f"{label} 缺少必填字段：{field}")

        note_id = record.get("note_id")
        if note_id is not None and not isinstance(note_id, str):
            errors.append(f"{label} 的 note_id 必须是字符串。")

        path_value = record.get("path")
        if is_collection(record):
            file_path = validate_relative_public_path(path_value, label, errors)
        elif path_value:
            file_path = validate_relative_public_path(path_value, label, errors)
        else:
            file_path = None
            if not record.get("previewUrl"):
                errors.append(f"{label} 必须包含 path 或 previewUrl。")

        if path_value:
            if path_value in seen_paths:
                errors.append(f"重复路径：{path_value}")
            seen_paths.add(path_value)
        if file_path and not file_path.exists():
            errors.append(f"文件或目录不存在：{path_value}")

        for field_name in ["downloadUrl", "previewUrl"]:
            url_path = validate_optional_public_url(record.get(field_name), label, field_name, errors)
            if url_path and not url_path.exists():
                errors.append(f"{field_name} 指向的文件或目录不存在：{record.get(field_name)}")

        if is_collection(record):
            items = record.get("items")
            if not isinstance(items, list) or not items:
                errors.append(f"{label} 是 collection，但 items 不是非空数组。")
                continue
            for item_index, item in enumerate(items, start=1):
                item_label = f"{label} items[{item_index}]"
                if not isinstance(item, dict):
                    errors.append(f"{item_label} 必须是对象。")
                    continue
                if not item.get("title"):
                    errors.append(f"{item_label} 缺少字段：title")
                files = item_files(item)
                if not files:
                    errors.append(f"{item_label} 必须包含 path，或包含非空 files 数组。")
                    continue
                for file_index, file in enumerate(files, start=1):
                    file_label = f"{item_label} files[{file_index}]" if "files" in item else item_label
                    if not isinstance(file, dict):
                        errors.append(f"{file_label} 必须是对象。")
                        continue
                    for field in ["type", "path"]:
                        if not file.get(field):
                            errors.append(f"{file_label} 缺少字段：{field}")
                    item_path = validate_relative_public_path(file.get("path"), file_label, errors)
                    item_path_value = file.get("path")
                    if item_path_value:
                        if item_path_value in seen_paths:
                            errors.append(f"重复路径：{item_path_value}")
                        seen_paths.add(item_path_value)
                    if item_path and not item_path.is_file():
                        errors.append(f"章节文件不存在：{item_path_value}")
                    for field_name in ["downloadUrl", "previewUrl"]:
                        url_path = validate_optional_public_url(file.get(field_name), file_label, field_name, errors)
                        if url_path and not url_path.exists():
                            errors.append(f"{file_label} {field_name} 指向的文件或目录不存在：{file.get(field_name)}")

    if errors:
        print("验证失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("验证通过：data/files.json 格式正确，所有文件路径都存在。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
