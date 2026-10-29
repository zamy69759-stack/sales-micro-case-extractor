# Sales Micro Case Extractor

一个面向外贸销售复盘的 Codex Skill：从客户邮件、聊天、会议纪要或业务员口述中识别单一销售事件，补问缺失事实，并生成可追溯、可审核的 Markdown 知识卡。

## 能力

- 以只读方式扫描 TXT、MD、EML、CSV 资料。
- 按客户、订单和时间线合并同一事件，避免把引用邮件重复计数。
- 区分事实、口述、推断、建议和示范话术。
- 资料不完整时，每轮最多追问三个关键问题。
- 固定输出 11 个 YAML 字段和 12 个正文章节。
- 提供候选重复提醒、知识库初始化和格式校验脚本。
- 不需要 API Key、云数据库或付费依赖。

## 安装

### 方法一：Git 克隆

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills"
git clone <你的GitHub仓库地址> sales-micro-case-extractor
```

### 方法二：下载 ZIP

解压后，把整个 `sales-micro-case-extractor` 文件夹复制到：

- macOS/Linux：`~/.codex/skills/`
- Windows：`%USERPROFILE%\.codex\skills\`

安装后的关键文件应位于：

```text
~/.codex/skills/sales-micro-case-extractor/SKILL.md
```

重新打开 Codex 会话后即可使用。

## 调用示例

```text
$sales-micro-case-extractor 从客户A文件夹的邮件中找出可复盘的销售微案例。
```

也可以直接说：

```text
萃取客户B的这封邮件，资料不够就问我，生成待审核MD。
```

## 目录结构

```text
sales-micro-case-extractor/
├── SKILL.md
├── agents/openai.yaml
├── assets/micro_case.md
├── references/case-format.md
├── scripts/
│   ├── find_duplicates.py
│   ├── init_library.py
│   ├── source_reader.py
│   └── validate_case.py
└── tests/test_scripts.py
```

## 验证

核心功能只需要 Python 3.10+：

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/*.py
```

如果当前电脑已经安装 Codex 的 `skill-creator`，还可以运行官方结构校验：

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

## 文件支持与边界

TXT、MD、EML、CSV 可直接扫描。DOCX、XLSX、PDF 需要环境提供对应解析能力，或者先导出为受支持格式。本 Skill 不发送邮件、不修改原始资料、不上传客户数据，也不会把“客户安排付款”自动推断为“银行已经到账”。

## 隐私

请只处理你有权访问的资料。知识卡和审计记录应避免保存完整敏感邮件、邮箱、电话或其他不必要的个人信息。
