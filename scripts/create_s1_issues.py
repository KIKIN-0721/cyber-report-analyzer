from __future__ import annotations

import argparse
import subprocess
from typing import Dict, List


ISSUES: List[Dict[str, str]] = [
    {
        "title": "[S1][rules] 冻结首版规则边界与优先级",
        "owner": "徐志翔",
        "due": "2026-04-16",
        "labels": "type:feature,stage:S1,module:rules,priority:P0",
        "body": "目标：形成规则台账V0.1，明确P0/P1规则项。\nDoD：规则项清单评审通过并归档。",
    },
    {
        "title": "[S1][management] M1验收标准发布",
        "owner": "徐志翔",
        "due": "2026-04-17",
        "labels": "type:docs,stage:S1,module:docs,priority:P0",
        "body": "目标：发布里程碑M1验收清单。\nDoD：团队确认并签收。",
    },
    {
        "title": "[S1][model] 语义归一化输入输出协议草案",
        "owner": "刘文旭",
        "due": "2026-04-17",
        "labels": "type:feature,stage:S1,module:model,priority:P1",
        "body": "目标：定义模型输入输出字段与约束。\nDoD：接口文档合并到docs/architecture。",
    },
    {
        "title": "[S1][web] 后端接口初版定义",
        "owner": "刘文旭",
        "due": "2026-04-19",
        "labels": "type:feature,stage:S1,module:web,priority:P1",
        "body": "目标：完成上传、任务查询、结果查询接口草案。\nDoD：OpenAPI草案提交。",
    },
    {
        "title": "[S1][rules] 字段映射与别名表 V0.1",
        "owner": "邱馨甜",
        "due": "2026-04-16",
        "labels": "type:feature,stage:S1,module:rules,priority:P0",
        "body": "目标：建立核心字段映射关系。\nDoD：字段映射文档审阅通过。",
    },
    {
        "title": "[S1][test] 样本用例设计 V0.1",
        "owner": "邱馨甜",
        "due": "2026-04-19",
        "labels": "type:test,stage:S1,module:docs,priority:P1",
        "body": "目标：覆盖核心规则样本用例。\nDoD：不少于20条测试样本说明。",
    },
    {
        "title": "[S1][parser] PDF文本与截图分离最小可运行链路",
        "owner": "叶泽东",
        "due": "2026-04-18",
        "labels": "type:feature,stage:S1,module:parser,priority:P0",
        "body": "目标：单PDF可提取文本与图片。\nDoD：输出文件可用于后续OCR。",
    },
    {
        "title": "[S1][deploy] 本地开发环境脚本初版",
        "owner": "叶泽东",
        "due": "2026-04-20",
        "labels": "type:chore,stage:S1,module:deploy,priority:P1",
        "body": "目标：实现一键安装依赖与启动。\nDoD：新成员30分钟内完成环境搭建。",
    },
    {
        "title": "[S1][ocr] OCR后处理策略文档",
        "owner": "王牧秋",
        "due": "2026-04-17",
        "labels": "type:feature,stage:S1,module:ocr,priority:P1",
        "body": "目标：定义降噪、纠错、关键字段提取策略。\nDoD：策略文档合并。",
    },
    {
        "title": "[S1][evidence] 证据映射数据结构 V0.1",
        "owner": "王牧秋",
        "due": "2026-04-19",
        "labels": "type:feature,stage:S1,module:evidence,priority:P1",
        "body": "目标：定义字段命中与页码/截图关联模型。\nDoD：结构定义文件提交。",
    },
    {
        "title": "[S1][ci] 最小CI流程搭建",
        "owner": "吴世豪",
        "due": "2026-04-17",
        "labels": "type:test,stage:S1,module:ci,priority:P0",
        "body": "目标：PR触发基础检查。\nDoD：CI执行语法与测试。",
    },
    {
        "title": "[S1][test] 测试规范与回归模板",
        "owner": "吴世豪",
        "due": "2026-04-20",
        "labels": "type:docs,stage:S1,module:docs,priority:P1",
        "body": "目标：发布缺陷记录模板与回归流程。\nDoD：团队按模板提测。",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create S1 GitHub issues with gh CLI.")
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument(
        "--assignee",
        action="append",
        default=[],
        help="map owner name to GitHub login, e.g. --assignee 叶泽东=alice",
    )
    return parser.parse_args()


def parse_assignee_map(values: List[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"invalid --assignee value: {item}")
        owner, login = item.split("=", 1)
        mapping[owner.strip()] = login.strip()
    return mapping


def run_command(args: List[str]) -> None:
    completed = subprocess.run(args, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(args)}")


def main() -> int:
    args = parse_args()
    assignee_map = parse_assignee_map(args.assignee)

    for issue in ISSUES:
        owner = issue["owner"]
        body = f"负责人：{owner}\n截止日期：{issue['due']}\n\n{issue['body']}"
        command = [
            "gh",
            "issue",
            "create",
            "--repo",
            args.repo,
            "--title",
            issue["title"],
            "--body",
            body,
            "--label",
            issue["labels"],
        ]
        assignee = assignee_map.get(owner)
        if assignee:
            command.extend(["--assignee", assignee])

        run_command(command)
        print(f"Created issue: {issue['title']}")

    print("Done. S1 issues created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
