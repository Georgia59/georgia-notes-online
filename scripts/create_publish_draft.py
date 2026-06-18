import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

from add_file_to_index import normalize_record, validate_record


REPO_ROOT = Path(__file__).resolve().parents[1]


def resolve_path(value):
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    return (Path.cwd() / path).resolve()


def infer_pages_url():
    try:
        remote = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""

    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$", remote)
    if not match:
        return ""

    owner = match.group("owner")
    repo = match.group("repo")
    return f"https://{owner.lower()}.github.io/{repo}/"


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def load_items_json(path_value):
    path = resolve_path(path_value)
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("--items-json must contain a JSON array.")
    return data


def public_path_join(public_dir, filename):
    return f"{public_dir.rstrip('/')}/{filename}"


def normalize_collection_items(raw_items, public_dir):
    items = []
    copy_plan = []

    for item in raw_items:
        if not isinstance(item, dict):
            raise ValueError("Each collection item must be a JSON object.")

        item_base = {
            key: value
            for key, value in item.items()
            if key not in ("file", "filename", "source", "src", "dest_name", "files")
        }

        if isinstance(item.get("files"), list):
            normalized_files = []
            for file in item["files"]:
                if not isinstance(file, dict):
                    raise ValueError("Each item file must be a JSON object.")
                source_name = file.get("source") or file.get("src") or file.get("file") or file.get("filename")
                public_file = {
                    key: value
                    for key, value in file.items()
                    if key not in ("file", "filename", "source", "src", "dest_name")
                }
                dest_name = file.get("dest_name")
                if public_file.get("path"):
                    dest_name = dest_name or Path(public_file["path"]).name
                else:
                    dest_name = dest_name or file.get("filename") or file.get("file") or source_name
                    if not dest_name:
                        raise ValueError("Collection item file needs path, filename, file, or dest_name.")
                    public_file["path"] = public_path_join(public_dir, dest_name)
                source_name = source_name or dest_name
                normalized_files.append(public_file)
                copy_plan.append((source_name, dest_name))
            item_base["files"] = normalized_files
        else:
            source_name = item.get("source") or item.get("src") or item.get("file") or item.get("filename")
            if item_base.get("path"):
                dest_name = item.get("dest_name") or Path(item_base["path"]).name
            else:
                dest_name = item.get("dest_name") or item.get("filename") or item.get("file") or source_name
                if not dest_name:
                    raise ValueError("Collection item needs path, filename, file, or dest_name.")
                item_base["path"] = public_path_join(public_dir, dest_name)
            source_name = source_name or dest_name
            copy_plan.append((source_name, dest_name))

        items.append(item_base)

    seen_destinations = set()
    for _, dest_name in copy_plan:
        if dest_name in seen_destinations:
            raise ValueError(f"Duplicate collection destination filename: {dest_name}")
        seen_destinations.add(dest_name)

    return items, copy_plan


def prepare_review_path(path, force):
    if not path.exists():
        return
    if not force:
        raise FileExistsError(path)
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def build_file_metadata(args, dest_name):
    return normalize_record(
        {
            "note_id": args.note_id,
            "course": args.course,
            "category": args.category,
            "title": args.title,
            "type": args.type,
            "date": args.date,
            "path": f"files/{args.category}/{dest_name}",
            "source": args.source,
            "description": args.description,
        }
    )


def build_collection_metadata(args, dest_name, items):
    return normalize_record(
        {
            "note_id": args.note_id,
            "kind": "collection",
            "course": args.course,
            "category": args.category,
            "title": args.title,
            "type": args.type or "Collection",
            "date": args.date,
            "path": f"files/{args.category}/{dest_name}/",
            "source": args.source,
            "description": args.description,
            "items": items,
        }
    )


def compact_metadata(metadata):
    return {key: value for key, value in metadata.items() if value not in (None, "")}


def copy_collection_files(input_path, review_path, copy_plan):
    review_path.mkdir(parents=True, exist_ok=True)
    for source_name, target_name in copy_plan:
        source_file = input_path / source_name
        if not source_file.is_file():
            raise FileNotFoundError(f"collection source file is missing: {source_file}")
        shutil.copy2(source_file, review_path / target_name)


def make_draft(args, review_path, metadata):
    website_url = (args.website_url or infer_pages_url()).rstrip("/")
    download_url = f"{website_url}/{metadata['path']}" if website_url else ""
    return {
        "needs_user_review": True,
        "website_url": website_url,
        "download_url_after_publish": download_url,
        "review_path": review_path.relative_to(REPO_ROOT).as_posix(),
        "metadata": metadata,
        "review_checklist": [
            "标题是否准确",
            "一句话简介是否适合公开展示",
            "来源是否不暴露原始文件名或本地路径",
            "文件是否适合公开发布",
            "是否确认发布到网站",
        ],
    }


def main():
    parser = argparse.ArgumentParser(
        description="仅在用户要求上传/发布时，复制成品到 review/ 并生成发布草稿。"
    )
    parser.add_argument("--input-path", required=True, help="已生成的单文件路径，或资料集源目录。")
    parser.add_argument("--kind", choices=["file", "collection"], default="file", help="草稿类型：file 或 collection。")
    parser.add_argument("--items-json", help="collection 的章节条目 JSON 数组路径。")
    parser.add_argument("--dest-name", help="发布后的文件名，或 collection 目录名。")
    parser.add_argument("--note-id", help="同一笔记多格式共用的稳定英文短名。")
    parser.add_argument("--course", required=True, help="公开显示的课程名称。")
    parser.add_argument("--category", required=True, help="review/ 和 files/ 下的课程目录名。")
    parser.add_argument("--title", required=True, help="公开显示的资料标题。")
    parser.add_argument("--type", help="文件类型，例如 PDF 或 Collection。")
    parser.add_argument("--date", default=date.today().isoformat(), help="发布日期，格式 YYYY-MM-DD。")
    parser.add_argument("--source", required=True, help="公开显示的来源名称。")
    parser.add_argument("--description", required=True, help="一句话简介。")
    parser.add_argument("--website-url", help="GitHub Pages 首页地址；默认从 origin 自动推断。")
    parser.add_argument("--force", action="store_true", help="允许覆盖 review/ 中已有的同名文件、目录和草稿。")
    args = parser.parse_args()

    try:
        input_path = resolve_path(args.input_path)

        if args.kind == "file":
            if not input_path.is_file():
                print(f"生成草稿失败：输入文件不存在：{input_path}")
                return 1
            dest_name = args.dest_name or input_path.name
            review_path = (REPO_ROOT / "review" / args.category / dest_name).resolve()
            draft_path = review_path.with_suffix(review_path.suffix + ".publish-draft.json")
            metadata = build_file_metadata(args, dest_name)
            copy_plan = None
        else:
            if not input_path.is_dir():
                print(f"生成草稿失败：资料集源目录不存在：{input_path}")
                return 1
            if not args.items_json:
                print("生成草稿失败：collection 需要 --items-json。")
                return 1
            dest_name = args.dest_name or f"{args.date}-{args.note_id or input_path.name}"
            review_path = (REPO_ROOT / "review" / args.category / dest_name).resolve()
            draft_path = review_path.with_name(review_path.name + ".publish-draft.json")
            public_dir = f"files/{args.category}/{dest_name}/"
            items, copy_plan = normalize_collection_items(load_items_json(args.items_json), public_dir)
            metadata = build_collection_metadata(args, dest_name, items)

        metadata = compact_metadata(metadata)
        errors = validate_record(metadata)
        if errors:
            print("生成草稿失败：")
            for error in errors:
                print(f"- {error}")
            return 1

        try:
            prepare_review_path(review_path, args.force)
            prepare_review_path(draft_path, args.force)
        except FileExistsError as exc:
            relative = exc.filename.relative_to(REPO_ROOT).as_posix()
            print(f"生成草稿失败：review 目标已存在：{relative}")
            return 1

        review_path.parent.mkdir(parents=True, exist_ok=True)
        if args.kind == "file":
            shutil.copy2(input_path, review_path)
        else:
            copy_collection_files(input_path, review_path, copy_plan)

        save_json(draft_path, make_draft(args, review_path, metadata))

        print(f"草稿已生成：{draft_path.relative_to(REPO_ROOT).as_posix()}")
        print(f"待检查目标：{review_path.relative_to(REPO_ROOT).as_posix()}")
        print("请用户检查草稿 JSON。确认后再正式发布。")
        return 0
    except Exception as exc:
        print(f"生成草稿失败：{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
