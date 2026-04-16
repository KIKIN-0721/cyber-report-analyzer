# S1阶段 Issue 清单（2026-03-31 至 2026-04-20）

配套执行文档：docs/github/S1-协同开发执行手册.md

使用建议：
- 先阅读执行手册，再按本清单创建Issue
- 创建Issue时必须打全标签（type、stage、module、priority）
- 每日更新Issue状态，周日统一汇总到develop

执行规则：
- 每个 Issue 必须写清输入、输出、完成标准和测试证据。
- P0 任务优先保障“能运行、能验证、能交接”，不追求完整产品能力。
- 涉及接口、字段、规则的变更必须同步更新对应文档。
- 关闭 Issue 前必须附 `pytest` 或手工复现说明。

说明：以下为首批可直接在GitHub创建的任务，已按成员职责和里程碑M1拆解。

## A. 项目负责人 徐志翔

1. [S1][rules] 冻结首版规则边界与优先级
- 截止：2026-04-16
- 标签：type:feature stage:S1 module:rules priority:P0
- 验收：形成规则台账V0.1，明确P0 P1规则项

2. [S1][management] M1验收标准发布
- 截止：2026-04-17
- 标签：type:docs stage:S1 module:docs priority:P0
- 验收：发布M1验收清单，团队签收

## B. 刘文旭

3. [S1][model] 语义归一化输入输出协议草案
- 截止：2026-04-17
- 标签：type:feature stage:S1 module:model priority:P1
- 验收：定义字段标准与接口约定文档

4. [S1][web] 后端接口初版定义
- 截止：2026-04-19
- 标签：type:feature stage:S1 module:web priority:P1
- 验收：完成上传 任务查询 结果查询接口草案

## C. 邱馨甜

5. [S1][rules] 字段映射与别名表 V0.1
- 截止：2026-04-16
- 标签：type:feature stage:S1 module:rules priority:P0
- 验收：完成核心字段映射表并经负责人审阅

6. [S1][test] 样本用例设计 V0.1
- 截止：2026-04-19
- 标签：type:test stage:S1 module:docs priority:P1
- 验收：不少于20条规则测试样本说明

## D. 叶泽东

7. [S1][parser] PDF文本与截图分离最小可运行链路
- 截止：2026-04-18
- 标签：type:feature stage:S1 module:parser priority:P0
- 验收：输入单个PDF，输出文本与图片文件

8. [S1][deploy] 本地开发环境脚本初版
- 截止：2026-04-20
- 标签：type:chore stage:S1 module:deploy priority:P1
- 验收：一键安装依赖与启动脚本可用

## E. 王牧秋

9. [S1][ocr] OCR后处理策略文档
- 截止：2026-04-17
- 标签：type:feature stage:S1 module:ocr priority:P1
- 验收：定义降噪 纠错 关键字段提取策略

10. [S1][evidence] 证据映射数据结构 V0.1
- 截止：2026-04-19
- 标签：type:feature stage:S1 module:evidence priority:P1
- 验收：定义字段 命中片段 页码 截图坐标结构

## F. 吴世豪

11. [S1][ci] 最小CI流程搭建
- 截止：2026-04-17
- 标签：type:test stage:S1 module:ci priority:P0
- 验收：PR触发语法检查与测试执行

12. [S1][test] 测试规范与回归模板
- 截止：2026-04-20
- 标签：type:docs stage:S1 module:docs priority:P1
- 验收：发布缺陷记录模板与回归流程

## S1提交节奏要求

- 每日：每人至少1次Push
- 每周三22:00前：中期同步Push
- 每周日22:00前：合并稳定分支到develop
- 2026-04-20：打里程碑标签 v0.1-m1
