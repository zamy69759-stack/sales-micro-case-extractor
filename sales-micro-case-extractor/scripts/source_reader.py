#!/usr/bin/env python3
"""安全扫描并提取常见本地资料；不修改源文件。"""
from __future__ import annotations

import argparse
import csv
import email
import hashlib
import json
import re
from email import policy
from pathlib import Path

TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".eml"}
OPTIONAL_EXTENSIONS = {".docx", ".xlsx", ".pdf"}


def clean_reply(text: str) -> str:
    """移除常见引用回复区，保留当前消息。"""
    patterns = [r"(?im)^On .+ wrote:\s*$", r"(?im)^From:\s+.+$", r"(?m)^>+"]
    positions = [match.start() for pattern in patterns if (match := re.search(pattern, text))]
    return text[:min(positions)].strip() if positions else text.strip()


def read_eml(path: Path) -> dict[str, str]:
    message = email.message_from_bytes(path.read_bytes(), policy=policy.default)
    body = message.get_body(preferencelist=("plain",))
    content = body.get_content() if body else ""
    return {
        "date": str(message.get("date", "")), "from": str(message.get("from", "")),
        "to": str(message.get("to", "")), "subject": str(message.get("subject", "")),
        "body": clean_reply(content),
    }


def read_source(path: Path) -> dict[str, object]:
    ext = path.suffix.lower()
    try:
        if ext in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8")
            return {"status": "ok", "text": clean_reply(text)}
        if ext == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.reader(handle))
            return {"status": "ok", "rows": rows}
        if ext == ".eml":
            return {"status": "ok", "email": read_eml(path)}
        if ext in OPTIONAL_EXTENSIONS:
            return {"status": "needs_optional_reader", "message": f"{ext} 需要可选解析库或先导出为 TXT/CSV"}
        return {"status": "unsupported", "message": "不支持的文件类型；可导出为 EML、TXT、PDF 或 CSV"}
    except (OSError, UnicodeError, email.errors.MessageError) as exc:
        return {"status": "error", "message": f"无法可靠读取：{type(exc).__name__}: {exc}"}


def scan(target: Path) -> list[dict[str, object]]:
    paths = [target] if target.is_file() else sorted(p for p in target.rglob("*") if p.is_file() and not p.name.startswith("._"))
    seen: set[str] = set()
    results = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in seen:
            results.append({"file": str(path), "status": "duplicate_content"})
            continue
        seen.add(digest)
        results.append({"file": str(path), **read_source(path)})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.target.exists():
        print(f"目标不存在：{args.target}")
        return 1
    result = scan(args.target)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        tmp = args.output.with_suffix(args.output.suffix + ".tmp")
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(args.output)
        print(f"扫描结果已写入：{args.output}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
