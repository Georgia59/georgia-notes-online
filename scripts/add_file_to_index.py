import argparse
import json
import sys
from datetime import date
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


def load_json(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("data/files.json 必须是 JSON 数组。")
    return data


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def parse_tags(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    normalized = value.replace("，", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def is_collection(record):
    return record.get("kind") == "collection" or record.get("type") == "Collection" or isinstance(record.get("items"), list)


def normalize_record(record):
    normalized = dict(record)
    normalized["tags"] = parse_tags(normalized.get("tags"))
    if not normalized.get("date"):
        normalized["date"] = date.today().isoformat()
    if is_collection(normalized):
        normalized["kind"] = "collection"
        normalized["type"] = normalized.get("type") or "Collection"
    return normalized


def validate_public_path(path_value, field_name):
    errors = []
    if not path_value:
        errors.append(f"缺少路径字段：{field_name}")
        return errors
    path_text = str(path_value)
    if Path(path_text).is_absolute():
        errors.append(f"{field_name} 应使用仓库内相对路径。")
    if not path_text.startswith("files/"):
        errors.append(f"{field_name} 必须指向 files/ 下的成品位置。")
    return errors


def item_files(item):
    if isinstance(item.get("files"), list) and item["files"]:
        return item["files"]
    if item.get("path"):
        return [{"title": item.get("title"), "type": item.get("type"), "path": item.get("path")}]
    return []


def validate_record(record):
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in record or record[field] in ("", None):
            errors.append(f"缺少必填字段：{field}")

    if "tags" in record and not isinstance(record["tags"], list):
        errors.append("字段 tags 必须是数组，或在命令行中使用逗号分隔。")

    if "path" in record:
        errors.extend(validate_public_path(record["path"], "path"))

    if is_collection(record):
        items = record.get("items")
        if not isinstance(items, list) or not items:
            errors.append("collection 记录必须包含非空 items 数组。")
        else:
            seen_item_paths = set()
            for index, item in enumerate(items, start=1):
                if not isinstance(item, dict):
                    errors.append(f"items[{index}] 必须是对象。")
                    continue
                if not item.get("title"):
                    errors.append(f"items[{index}] 缺少字段：title")
                files = item_files(item)
                if not files:
                    errors.append(f"items[{index}] 必须包含 path，或包含非空 files 数组。")
                    continue
                for file_index, file in enumerate(files, start=1):
                    file_label = f"items[{index}].files[{file_index}]" if "files" in item else f"items[{index}]"
                    if not isinstance(file, dict):
                        errors.append(f"{file_label} 必须是对象。")
                        continue
                    for field in ["type", "path"]:
                        if not file.get(field):
                            errors.append(f"{file_label} 缺少字段：{field}")
                    item_path = file.get("path")
                    if item_path:
                        errors.extend(validate_public_path(item_path, f"{file_label}.path"))
                        if item_path in seen_item_paths:
                            errors.append(f"collection 内重复章节路径：{item_path}")
                        seen_item_paths.add(item_path)

    return errors


def build_record_from_args(args):
    if args.metadata:
        metadata_path = Path(args.metadata)
        if not metadata_path.is_absolute():
            metadata_path = Path.cwd() / metadata_path
        with metadata_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get("metadata", data) if isinstance(data, dict) else data

    return {
        "note_id": args.note_id,
        "course": args.course,
        "category": args.category,
        "title": args.title,
        "type": args.type,
        "date": args.date,
        "path": args.path,
        "source": args.source,
        "tags": args.tags,
        "description": args.description,
    }


def sort_key(record):
    return (record.get("date") or "", record.get("title") or "")


def indexed_paths(record):
    paths = []
    if record.get("path"):
        paths.append(record["path"])
    if is_collection(record):
        for item in record.get("items", []):
            paths.extend(file.get("path") for file in item_files(item) if file.get("path"))
    return paths


def main():
    parser = argparse.ArgumentParser(description="将生成文件记录追加到 data/files.json。")
    parser.add_argument("--metadata", help="包含完整文件信息的 JSON 元数据路径。")
    parser.add_argument("--note-id", help="同一笔记多格式共用的稳定英文短名。")
    parser.add_argument("--course", help="课程名称，例如 医学影像学。")
    parser.add_argument("--category", help="课程目录，例如 imaging。")
    parser.add_argument("--title", help="文件标题。")
    parser.add_argument("--type", help="文件类型，例如 PDF、Word、PPT、HTML。")
    parser.add_argument("--date", help="生成日期，格式 YYYY-MM-DD。")
    parser.add_argument("--path", help="仓库内相对文件路径。")
    parser.add_argument("--source", help="来源说明，例如 本地 PPT。")
    parser.add_argument("--tags", help="英文逗号或中文逗号分隔的标签。")
    parser.add_argument("--description", help="简短说明。")
    args = parser.parse_args()

    try:
        record = normalize_record(build_record_from_args(args))
        errors = validate_record(record)
        if errors:
            print("添加失败：")
            for error in errors:
                print(f"- {error}")
            return 1

        files = load_json(INDEX_PATH)
        existing_paths = {path for item in files for path in indexed_paths(item)}
        duplicates = [path for path in indexed_paths(record) if path in existing_paths]
        if duplicates:
            print("添加失败：路径已存在，未重复添加。")
            for path in duplicates:
                print(f"- {path}")
            return 1

        files.append(record)
        files.sort(key=sort_key, reverse=True)
        save_json(INDEX_PATH, files)
        print(f"添加成功：{record['path']}")
        return 0
    except json.JSONDecodeError as exc:
        print(f"添加失败：JSON 格式错误：{exc}")
        return 1
    except Exception as exc:
        print(f"添加失败：{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
