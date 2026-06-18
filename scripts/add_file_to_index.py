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


def normalize_record(record):
    normalized = dict(record)
    normalized["tags"] = parse_tags(normalized.get("tags"))
    if not normalized.get("date"):
        normalized["date"] = date.today().isoformat()
    return normalized


def validate_record(record):
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in record or record[field] in ("", None):
            errors.append(f"缺少必填字段：{field}")
    if "tags" in record and not isinstance(record["tags"], list):
        errors.append("字段 tags 必须是数组，或在命令行中使用逗号分隔。")
    if "path" in record and Path(str(record["path"])).is_absolute():
        errors.append("字段 path 应使用仓库内相对路径，例如 files/imaging/example.pdf。")
    return errors


def build_record_from_args(args):
    if args.metadata:
        metadata_path = Path(args.metadata)
        if not metadata_path.is_absolute():
            metadata_path = Path.cwd() / metadata_path
        with metadata_path.open("r", encoding="utf-8") as file:
            return json.load(file)

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


def main():
    parser = argparse.ArgumentParser(description="将生成文件记录追加到 data/files.json。")
    parser.add_argument("--metadata", help="包含完整文件信息的 JSON 元数据路径。")
    parser.add_argument("--note-id", help="同一笔记多格式共用的稳定英文短名，例如 acute-osteomyelitis-review。")
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
        existing_paths = {item.get("path") for item in files}
        if record["path"] in existing_paths:
            print(f"添加失败：路径已存在，未重复添加：{record['path']}")
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
