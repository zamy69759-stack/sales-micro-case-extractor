#!/usr/bin/env python3
"""严格校验销售微案例的固定 YAML 元数据与 12 章结构。"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

KEYS = [
    "知识类型", "案例编号", "案例标题", "案例状态", "一级分类", "二级分类",
    "适用场景", "来源文件", "来源载体", "信息完整度", "是否可作为已验证成功案例",
]
SECTIONS = [
    "一、案例一句话概括", "二、客户与订单背景", "三、客户提出的问题",
    "四、业务员当时的想法与难点", "五、客户真实意图分析（推断，非事实）",
    "六、处理思路", "七、参考沟通话术（知识库整理示范，非真实已发送邮件）",
    "八、实际执行与客户反馈", "九、可复用经验", "十、适用边界与风险提醒",
    "十一、后续补全字段", "十二、知识库检索问答",
]
PLACEHOLDERS = ("[事实型概述", "[客户关系", "{案例标题}", "[学员未来会搜索")


def _front_matter(text: str) -> tuple[list[tuple[str, str]], str]:
    if not text.startswith("---\n"):
        raise ValueError("文件必须以 YAML 分隔符 --- 开始")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("缺少 YAML 结束分隔符 ---")
    pairs: list[tuple[str, str]] = []
    for number, line in enumerate(text[4:end].splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([^:#][^:]*):\s*(.*)$", line)
        if not match:
            raise ValueError(f"YAML 第 {number} 行无法解析：{line}")
        pairs.append((match.group(1).strip(), match.group(2).strip()))
    return pairs, text[end + 5:]


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return ["文件不存在"]
    if not path.parent.exists():
        errors.append("输出路径不存在")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["文件不是有效 UTF-8"]
    try:
        pairs, body = _front_matter(text)
    except ValueError as exc:
        return [str(exc)]
    keys = [key for key, _ in pairs]
    values = dict(pairs)
    if keys != KEYS:
        errors.append(f"YAML 键必须恰好为固定 11 项且顺序一致；实际为：{keys}")
    if values.get("知识类型") != "销售微案例":
        errors.append("知识类型必须为‘销售微案例’")
    if values.get("是否可作为已验证成功案例") not in {"是", "否"}:
        errors.append("是否可作为已验证成功案例只能为‘是’或‘否’")
    scenarios = values.get("适用场景", "")
    if not (scenarios.startswith("[") and scenarios.endswith("]")):
        errors.append("适用场景必须使用 YAML 列表格式，如 [] 或 [投诉, 交期]")
    title_count = len(re.findall(r"(?m)^# 销售微案例｜.+$", body))
    if title_count != 1:
        errors.append("正文必须恰有一个‘# 销售微案例｜标题’")
    headings = re.findall(r"(?m)^## (.+)$", body)
    if headings != SECTIONS:
        errors.append("12 个章节的名称、顺序或出现次数不正确")
    success = values.get("案例状态") == "已验证成功"
    allowed = values.get("是否可作为已验证成功案例") == "是"
    if success != allowed:
        errors.append("案例状态与‘是否可作为已验证成功案例’不一致")
    if allowed:
        section8 = body.split("## 八、实际执行与客户反馈", 1)[-1].split("## 九、", 1)[0]
        evidence_terms = ("证据", "来源", "订单", "邮件", "审核")
        if not any(term in section8 for term in evidence_terms):
            errors.append("成功案例第八章缺少结果证据或审核说明")
    if any(marker in text for marker in PLACEHOLDERS):
        errors.append("仍含模板占位说明，不能作为正式案例")
    if "真实已发送" in body and "来源" not in body:
        errors.append("声称真实发送的话术必须注明来源")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_file", type=Path)
    args = parser.parse_args()
    errors = validate(args.case_file)
    if errors:
        print("校验失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"校验通过：{args.case_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
