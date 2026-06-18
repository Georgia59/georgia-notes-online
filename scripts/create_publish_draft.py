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


def main():
    parser = argparse.ArgumentParser(description="生成发布前草案：复制文件到 review/ 并写入待检查元数据。")
    parser.add_argument("--input-path", required=True, help="已生成的成品文件路径。")
    parser.add_argument("--dest-name", help="发布后的文件名；默认沿用输入文件名。")
    parser.add_argument("--note-id", help="同一笔记多格式共用的稳定英文短名。")
    parser.add_argument("--course", required=True, help="课程名称，例如 预防医学。")
    parser.add_argument("--category", required=True, help="课程目录，例如 preventive-medicine。")
    parser.add_argument("--title", required=True, help="卡片名称。")
    parser.add_argument("--type", required=True, help="文件类型，例如 PDF、Word、HTML。")
    parser.add_argument("--date", default=date.today().isoformat(), help="发布日期，格式 YYYY-MM-DD。")
    parser.add_argument("--source", required=True, help="公开可显示的来源名称。")
    parser.add_argument("--tags", required=True, help="英文逗号或中文逗号分隔的标签。")
    parser.add_argument("--description", required=True, help="一句话简介。")
    parser.add_argument("--website-url", help="GitHub Pages 首页地址；默认从 origin 自动推断。")
    parser.add_argument("--force", action="store_true", help="允许覆盖 review/ 中已有的同名文件和草案。")
    args = parser.parse_args()

    try:
        input_path = resolve_path(args.input_path)
        if not input_path.exists() or not input_path.is_file():
            print(f"生成草案失败：输入文件不存在：{input_path}")
            return 1

        dest_name = args.dest_name or input_path.name
        review_path = (REPO_ROOT / "review" / args.category / dest_name).resolve()
        draft_path = review_path.with_suffix(review_path.suffix + ".publish-draft.json")

        if review_path.exists() and not args.force:
            print(f"生成草案失败：review 文件已存在：{review_path.relative_to(REPO_ROOT).as_posix()}")
            return 1
        if draft_path.exists() and not args.force:
            print(f"生成草案失败：草案已存在：{draft_path.relative_to(REPO_ROOT).as_posix()}")
            return 1

        metadata = normalize_record(
            {
                "note_id": args.note_id,
                "course": args.course,
                "category": args.category,
                "title": args.title,
                "type": args.type,
                "date": args.date,
                "path": f"files/{args.category}/{dest_name}",
                "source": args.source,
                "tags": args.tags,
                "description": args.description,
            }
        )
        metadata = {key: value for key, value in metadata.items() if value not in (None, "")}

        errors = validate_record(metadata)
        if errors:
            print("生成草案失败：")
            for error in errors:
                print(f"- {error}")
            return 1

        website_url = (args.website_url or infer_pages_url()).rstrip("/")
        download_url = f"{website_url}/{metadata['path']}" if website_url else ""

        review_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(input_path, review_path)

        draft = {
            "needs_user_review": True,
            "website_url": website_url,
            "download_url_after_publish": download_url,
            "review_path": review_path.relative_to(REPO_ROOT).as_posix(),
            "metadata": metadata,
            "review_checklist": [
                "标题是否准确",
                "一句话简介是否符合公开展示",
                "来源是否不暴露原始文件名或本地路径",
                "文件是否适合公开发布",
                "是否确认发布到网站"
            ]
        }
        save_json(draft_path, draft)

        print(f"草案已生成：{draft_path.relative_to(REPO_ROOT).as_posix()}")
        print(f"待检查文件：{review_path.relative_to(REPO_ROOT).as_posix()}")
        if website_url:
            print(f"网站地址：{website_url}/")
        print("请用户检查草案 JSON。确认后再使用 scripts/publish_review_file.py --metadata 发布。")
        return 0
    except Exception as exc:
        print(f"生成草案失败：{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

