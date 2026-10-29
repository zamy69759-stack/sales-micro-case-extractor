#!/usr/bin/env python3
"""查找候选重复案例；只提示，不删除或覆盖文件。"""
from __future__ import annotations

import argparse
import csv
import re
from difflib import SequenceMatcher
from pathlib import Path


def normalize(value: str) -> str:
    return re.sub(r"[\W_]+", "", value.lower())


def score(candidate: dict[str, str], row: dict[str, str]) -> tuple[float, list[str]]:
    reasons: list[str] = []
    title_score = SequenceMatcher(None, normalize(candidate.get("标题", "")), normalize(row.get("标题", ""))).ratio()
    total = title_score * 0.35
    if candidate.get("客户代称") and candidate.get("客户代称") == row.get("客户代称"):
        total += 0.25; reasons.append("同一客户")
    if candidate.get("订单号") and candidate.get("订单号") == row.get("订单号"):
        total += 0.30; reasons.append("同一订单号")
    if candidate.get("事件日期") and candidate.get("事件日期") == row.get("事件日期"):
        total += 0.10; reasons.append("同一事件日期")
    if title_score >= 0.65:
        reasons.append(f"标题相似度 {title_score:.0%}")
    return min(total, 1.0), reasons


def find(index_path: Path, candidate: dict[str, str], threshold: float = 0.55) -> list[dict[str, object]]:
    if not index_path.exists():
        return []
    with index_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    matches = []
    for row in rows:
        value, reasons = score(candidate, row)
        if value >= threshold:
            matches.append({"案例编号": row.get("案例编号", ""), "标题": row.get("标题", ""), "得分": round(value, 3), "原因": reasons})
    return sorted(matches, key=lambda item: float(item["得分"]), reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--customer", default="")
    parser.add_argument("--date", default="")
    parser.add_argument("--order", default="")
    args = parser.parse_args()
    candidate = {"标题": args.title, "客户代称": args.customer, "事件日期": args.date, "订单号": args.order}
    matches = find(args.index, candidate)
    if not matches:
        print("未发现候选重复案例。")
        return 0
    print("发现候选重复案例（请人工决定更新或新建；程序不会删除）：")
    for item in matches:
        print(f"- {item['案例编号']}｜{item['标题']}｜得分 {item['得分']}｜{', '.join(item['原因'])}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
