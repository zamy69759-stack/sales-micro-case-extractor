#!/usr/bin/env python3
"""根据 config.json 初始化知识库目录与索引。"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

FIELDS = ["案例编号", "标题", "客户代称", "事件日期", "状态", "订单号", "文件路径"]


def initialize(config_path: Path) -> Path:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output = str(config.get("output_root", "")).strip()
    if not output:
        raise ValueError("config.json 中 output_root 尚未配置")
    root = Path(output).expanduser()
    (root / "待审核").mkdir(parents=True, exist_ok=True)
    (root / "已审核").mkdir(parents=True, exist_ok=True)
    index = root / "索引.csv"
    if not index.exists():
        with index.open("w", encoding="utf-8-sig", newline="") as handle:
            csv.DictWriter(handle, fieldnames=FIELDS).writeheader()
    return root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).parents[1] / "config.json")
    args = parser.parse_args()
    try:
        root = initialize(args.config)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"初始化失败：{exc}")
        return 1
    print(f"知识库已初始化：{root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
