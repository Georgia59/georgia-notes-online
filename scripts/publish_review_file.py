import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

from add_file_to_index import (
    indexed_paths,
    is_collection,
    item_files,
    load_json,
    normalize_record,
    save_json,
    sort_key,
    validate_record,
)


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
    item_count = len(record.get("items", [])) if is_collection(record) else 1
    line = (
        f"- 发布资料：{record['title']}，类型：{record['type']}，"
        f"文件数：{item_count}，路径：`{record['path']}`，日期：{record['date']}。\n"
    )
    with TASK_LOG_PATH.open("a", encoding="utf-8", newline="\n") as file:
        file.write(line)


def load_record_from_args(args):
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
            raise ValueError("使用元数据 JSON 时必须提供 review_path，或在草案中包含 review_path。")
        return record_data, review_path_value, args.dest_name

    missing = [
        name
        for name in ["review_path", "course", "category", "title", "type", "source", "description"]
        if not getattr(args, name)
    ]
    if missing:
        raise ValueError("缺少参数：" + ", ".join(f"--{name.replace('_', '-')}" for name in missing))

    record_data = {
        "note_id": args.note_id,
        "course": args.course,
        "category": args.category,
        "title": args.title,
        "type": args.type,
        "date": args.date,
        "source": args.source,
        "description": args.description,
        "downloadUrl": args.download_url,
        "previewUrl": args.preview_url,
    }
    return record_data, args.review_path, args.dest_name


def publish_single_file(record, review_path, dest_name):
    if not review_path.exists() or not review_path.is_file():
        raise ValueError(f"待发布文件不存在：{review_path}")

    if "path" in record:
        dest_path = (REPO_ROOT / record["path"]).resolve()
    else:
        dest_name = dest_name or review_path.name
        dest_path = (REPO_ROOT / "files" / record["category"] / dest_name).resolve()
        record["path"] = dest_path.relative_to(REPO_ROOT).as_posix()

    ensure_under(dest_path, (REPO_ROOT / "files").resolve(), "目标路径")
    if dest_path.exists():
        raise ValueError(f"目标文件已存在：{dest_path.relative_to(REPO_ROOT).as_posix()}")

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(review_path), str(dest_path))
    return record


def publish_collection(record, review_path):
    if not review_path.exists() or not review_path.is_dir():
        raise ValueError(f"待发布 collection 目录不存在：{review_path}")

    if "path" not in record:
        note_id = record.get("note_id") or "collection"
        record["path"] = f"files/{record['category']}/{record['date']}-{note_id}/"

    dest_dir = (REPO_ROOT / record["path"]).resolve()
    ensure_under(dest_dir, (REPO_ROOT / "files").resolve(), "目标路径")
    if dest_dir.exists():
        raise ValueError(f"目标目录已存在：{dest_dir.relative_to(REPO_ROOT).as_posix()}")

    dest_dir.mkdir(parents=True)
    moved_any = False
    for item in record.get("items", []):
        for file in item_files(item):
            dest_item_path = (REPO_ROOT / file["path"]).resolve()
            ensure_under(dest_item_path, dest_dir, "章节目标路径")
            source_item_path = review_path / dest_item_path.name
            if not source_item_path.is_file():
                raise ValueError(f"review 目录缺少章节文件：{source_item_path.name}")
            dest_item_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_item_path), str(dest_item_path))
            moved_any = True

    if not moved_any:
        raise ValueError("collection 没有可发布的章节文件。")

    return record


def main():
    parser = argparse.ArgumentParser(description="将 review/ 中已确认的资料发布到 files/ 并更新索引。")
    parser.add_argument("--metadata", help="发布草案 JSON 路径，通常为 review/...publish-draft.json。")
    parser.add_argument("--review-path", help="待发布文件或 collection 目录路径，必须位于 review/ 下。")
    parser.add_argument("--dest-name", help="发布后的文件名；普通单文件默认沿用 review 文件名。")
    parser.add_argument("--note-id", help="同一笔记多格式共用的稳定英文短名。")
    parser.add_argument("--course", help="课程名称，例如 医学影像学。")
    parser.add_argument("--category", help="课程目录，例如 imaging。")
    parser.add_argument("--title", help="文件标题。")
    parser.add_argument("--type", help="文件类型，例如 PDF、Word、PPT、HTML。")
    parser.add_argument("--date", default=date.today().isoformat(), help="发布日期，格式 YYYY-MM-DD。")
    parser.add_argument("--download-url", help="下载按钮使用的仓库内相对路径。")
    parser.add_argument("--preview-url", help="在线预览按钮使用的仓库内相对 HTML 路径。")
    parser.add_argument("--source", help="公开可显示的来源类型。")
    parser.add_argument("--description", help="一句话简介。")
    args = parser.parse_args()

    try:
        record_data, review_path_value, dest_name = load_record_from_args(args)
        record = normalize_record(record_data)
        record = {key: value for key, value in record.items() if value not in (None, "")}

        review_path = resolve_repo_path(review_path_value)
        review_root = (REPO_ROOT / "review").resolve()
        ensure_under(review_path, review_root, "--review-path")

        errors = validate_record(record)
        if errors:
            print("发布失败：")
            for error in errors:
                print(f"- {error}")
            return 1

        files = load_json(INDEX_PATH)
        existing_paths = {path for item in files for path in indexed_paths(item)}
        duplicates = [path for path in indexed_paths(record) if path in existing_paths]
        if duplicates:
            print("发布失败：索引中已存在路径。")
            for path in duplicates:
                print(f"- {path}")
            return 1

        if is_collection(record):
            record = publish_collection(record, review_path)
        else:
            record = publish_single_file(record, review_path, dest_name)

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
