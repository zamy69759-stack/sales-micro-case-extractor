from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from find_duplicates import find  # noqa: E402
from source_reader import clean_reply, scan  # noqa: E402
from validate_case import validate  # noqa: E402


SECTIONS = [
    "一、案例一句话概括", "二、客户与订单背景", "三、客户提出的问题",
    "四、业务员当时的想法与难点", "五、客户真实意图分析（推断，非事实）",
    "六、处理思路", "七、参考沟通话术（知识库整理示范，非真实已发送邮件）",
    "八、实际执行与客户反馈", "九、可复用经验", "十、适用边界与风险提醒",
    "十一、后续补全字段", "十二、知识库检索问答",
]


def valid_case() -> str:
    metadata = """---
知识类型: 销售微案例
案例编号: CASE001
案例标题: 测试案例
案例状态: 待审核
一级分类: 测试
二级分类: 测试
适用场景: [测试]
来源文件: test.txt
来源载体: 邮件
信息完整度: 部分完整
是否可作为已验证成功案例: 否
---

# 销售微案例｜测试案例
"""
    return metadata + "\n".join(f"\n## {heading}\n待核实（来源：test.txt）。" for heading in SECTIONS) + "\n"


class ScriptSmokeTests(unittest.TestCase):
    def test_valid_case_passes_and_missing_heading_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            case = Path(temp) / "case.md"
            case.write_text(valid_case(), encoding="utf-8")
            self.assertEqual(validate(case), [])
            case.write_text(valid_case().replace("## 九、可复用经验\n", ""), encoding="utf-8")
            self.assertTrue(validate(case))

    def test_scan_detects_duplicate_content_and_removes_quoted_reply(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            content = "当前回复\nOn Tue, someone wrote:\n旧邮件"
            (root / "a.txt").write_text(content, encoding="utf-8")
            (root / "b.txt").write_text(content, encoding="utf-8")
            results = scan(root)
            self.assertEqual(results[0]["text"], "当前回复")
            self.assertEqual(results[1]["status"], "duplicate_content")
            self.assertEqual(clean_reply(content), "当前回复")

    def test_duplicate_finder_uses_customer_order_date_and_title(self):
        with tempfile.TemporaryDirectory() as temp:
            index = Path(temp) / "索引.csv"
            fields = ["案例编号", "标题", "客户代称", "事件日期", "状态", "订单号", "文件路径"]
            with index.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow({"案例编号": "CASE001", "标题": "包装标签错误修正", "客户代称": "客户A", "事件日期": "2026-01-05", "状态": "待审核", "订单号": "PO-1", "文件路径": "case.md"})
            matches = find(index, {"标题": "包装标签错误处理", "客户代称": "客户A", "事件日期": "2026-01-05", "订单号": "PO-1"})
            self.assertEqual(matches[0]["案例编号"], "CASE001")


if __name__ == "__main__":
    unittest.main()
