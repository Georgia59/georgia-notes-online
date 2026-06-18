import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

from add_file_to_index import load_json, normalize_record, save_json, sort_key, validate_record


REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "data" / "files.json"
TASK_LOG_PATH = REPO_ROOT / "tasks" / "task-log.md"


def resolve_repo_path(value):
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def ensure_under(path, parent, label):
    try:
        path.relative_to(parent)
    except ValueError as exc:
        raise ValueError(f"{label} 必须位于 {parent.relative_to(REPO_ROOT).as_posix()} 目录下。") from exc


def append_task_log(record):
    TASK_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = (
        f"- 发布资料：{record['title']}，类型：{record['type']}，"
        f"路径：`{record['path']}`，日期：{record['date']}。\n"
    )
    with TASK_LOG_PATH.open("a", encoding="utf-8", newline="\n") as file:
        file.write(line)


def main():
    parser = argparse.ArgumentParser(description="将 review/ 中已确认的资料发布到 files/ 并更新索引。")
    parser.add_argument("--metadata", help="发布草案 JSON 路径，通常为 review/...publish-draft.json。")
    parser.add_argument("--review-path", help="待发布文件路径，必须位于 review/ 下。")
    parser.add_argument("--dest-name", help="发布后的文件名；默认沿用 review 文件名。")
    parser.add_argument("--note-id", help="同一笔记多格式共用的稳定英文短名。")
    parser.add_argument("--course", help="课程名称，例如 医学影像学。")
    parser.add_argument("--category", help="课程目录，例如 imaging。")
    parser.add_argument("--title", help="文件标题。")
    parser.add_argument("--type", help="文件类型，例如 PDF、Word、PPT、HTML。")
    parser.add_argument("--date", default=date.today().isoformat(), help="发布日期，格式 YYYY-MM-DD。")
    parser.add_argument("--source", help="公开可显示的来源类型。")
    parser.add_argument("--tags", help="英文逗号或中文逗号分隔的标签。")
    parser.add_argument("--description", help="一句话简介。")
    args = parser.parse_args()

    try:
        if args.metadata:
            metadata_path = resolve_repo_path(args.metadata)
            with metadata_path.open("r", encoding="utf-8") as file:
                draft = json.load(file)
            if "metadata" in draft:
                record_data = draft["metadata"]
                review_path_value = args.review_path or draft.get("review_path")
            else:
                record_data = draft
                review_path_value = args.review_path
            if not review_path_value:
                print("发布失败：使用普通元数据 JSON 时必须提供 --review-path。")
                return 1
            dest_name = args.dest_name
        else:
            missing = [
                name
                for name in ["review_path", "course", "category", "title", "type", "source", "tags", "description"]
                if not getattr(args, name)
            ]
            if missing:
                print("发布失败：缺少参数。")
                for name in missing:
                    print(f"- --{name.replace('_', '-')}")
                return 1
            review_path_value = args.review_path
            dest_name = args.dest_name
            record_data = {
                "note_id": args.note_id,
                "course": args.course,
                "category": args.category,
                "title": args.title,
                "type": args.type,
                "date": args.date,
                "source": args.source,
                "tags": args.tags,
                "description": args.description,
            }

        review_path = resolve_repo_path(review_path_value)
        review_root = (REPO_ROOT / "review").resolve()
        ensure_under(review_path, review_root, "--review-path")

        if not review_path.exists() or not review_path.is_file():
            print(f"发布失败：待发布文件不存在：{review_path}")
            return 1

        record = normalize_record(record_data)
        record = {key: value for key, value in record.items() if value not in (None, "")}

        if "path" in record:
            dest_path = (REPO_ROOT / record["path"]).resolve()
            dest_name = dest_path.name
        else:
            dest_name = dest_name or review_path.name
            dest_path = (REPO_ROOT / "files" / record["category"] / dest_name).resolve()
            record["path"] = dest_path.relative_to(REPO_ROOT).as_posix()

        ensure_under(dest_path, (REPO_ROOT / "files").resolve(), "目标路径")

        if dest_path.exists():
            print(f"发布失败：目标文件已存在：{dest_path.relative_to(REPO_ROOT).as_posix()}")
            return 1

        errors = validate_record(record)
        if errors:
            print("发布失败：")
            for error in errors:
                print(f"- {error}")
            return 1

        files = load_json(INDEX_PATH)
        existing_paths = {item.get("path") for item in files}
        if record["path"] in existing_paths:
            print(f"发布失败：索引中已存在路径：{record['path']}")
            return 1

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(review_path), str(dest_path))
        files.append(record)
        files.sort(key=sort_key, reverse=True)
        save_json(INDEX_PATH, files)
        append_task_log(record)

        print(f"发布成功：{record['path']}")
        print("请继续运行 scripts/pre_publish_check.py 和 scripts/validate_files.py。")
        return 0
    except json.JSONDecodeError as exc:
        print(f"发布失败：JSON 格式错误：{exc}")
        return 1
    except Exception as exc:
        print(f"发布失败：{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
