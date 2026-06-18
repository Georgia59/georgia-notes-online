import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BANKS_PATH = REPO_ROOT / "data" / "banks.json"

REQUIRED_FIELDS = [
    "course",
    "title",
    "status",
    "lastUpdated",
    "source",
]

LOCAL_PATH_PATTERNS = [
    re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/](?![\\/])[^\s\"'<>]+"),
    re.compile(r"\\\\[A-Za-z0-9_.-]+\\[^\s\"'<>]+"),
    re.compile(r"/Users/[^\s\"'<>]+"),
    re.compile(r"/home/[^\s\"'<>]+"),
]

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def has_local_path(value):
    text = str(value)
    return any(pattern.search(text) for pattern in LOCAL_PATH_PATTERNS)


def is_collection(bank):
    return bank.get("kind") == "collection" or isinstance(bank.get("items"), list)


def validate_qr(value, label, errors):
    if not value:
        return
    if Path(str(value)).is_absolute() or not str(value).startswith("images/banks/"):
        errors.append(f"{label} 的 qr 必须是 images/banks/ 下的相对路径。")
    elif not (REPO_ROOT / str(value)).is_file():
        errors.append(f"{label} 的二维码图片不存在：{value}")


def validate_date(value, label, errors):
    if value and not DATE_PATTERN.match(str(value)):
        errors.append(f"{label} 的 lastUpdated 必须是 YYYY-MM-DD。")


def validate_code(value, label, seen_codes, errors):
    if not value:
        errors.append(f"{label} 缺少必填字段：code")
        return
    if value in seen_codes:
        errors.append(f"{label} 的佛脚码重复：{value}")
    seen_codes.add(value)


def main():
    errors = []

    if not BANKS_PATH.exists():
        print("验证失败：data/banks.json 不存在。")
        return 1

    try:
        banks = json.loads(BANKS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"验证失败：data/banks.json 不是合法 JSON：{exc}")
        return 1

    if not isinstance(banks, list):
        print("验证失败：data/banks.json 必须是 JSON 数组。")
        return 1

    seen_codes = set()
    for index, bank in enumerate(banks, start=1):
        label = f"第 {index} 条题库"
        if not isinstance(bank, dict):
            errors.append(f"{label} 必须是对象。")
            continue

        for field in REQUIRED_FIELDS:
            if bank.get(field) in ("", None):
                errors.append(f"{label} 缺少必填字段：{field}")

        if is_collection(bank):
            items = bank.get("items")
            if not isinstance(items, list) or not items:
                errors.append(f"{label} 是合集，但 items 不是非空数组。")
            else:
                for item_index, item in enumerate(items, start=1):
                    item_label = f"{label} items[{item_index}]"
                    if not isinstance(item, dict):
                        errors.append(f"{item_label} 必须是对象。")
                        continue
                    if not item.get("title"):
                        errors.append(f"{item_label} 缺少必填字段：title")
                    validate_code(item.get("code"), item_label, seen_codes, errors)
                    validate_date(item.get("lastUpdated"), item_label, errors)
                    validate_qr(item.get("qr", ""), item_label, errors)
                    for field, value in item.items():
                        if has_local_path(value):
                            errors.append(f"{item_label} 的 {field} 含本地路径：{value}")
        else:
            validate_code(bank.get("code"), label, seen_codes, errors)

        validate_date(bank.get("lastUpdated"), label, errors)
        validate_qr(bank.get("qr", ""), label, errors)

        for field, value in bank.items():
            if field == "items":
                continue
            if has_local_path(value):
                errors.append(f"{label} 的 {field} 含本地路径：{value}")

    if errors:
        print("验证失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("验证通过：data/banks.json 格式正确。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
