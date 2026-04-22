# S2 阶段 Issue 清单（段落级追溯版）

配套执行文档：docs/github/S2-协同开发执行手册.md

使用建议：
- 先做解析、OCR、字段保存，再补样本和回归。
- 所有 Issue 必须打全标签（type、stage、module、priority）。
- 重点关注 section_id、paragraph_id、page 和 source_ref 是否能贯穿全链路。

执行规则：
- 所有字段输出必须对齐 `StructuredField` 语义。
- parser/OCR 任务必须保留来源页码、段落编号、片段或图片引用。
- storage 任务必须支持结果回放，不能只做临时变量。
- 关闭 Issue 前必须说明对 S3 规则输入是否有影响。

## A. 徐志翔

1. [S2][management] 冻结 S2 范围与 M2 验收标准
- 截止：2026-04-24
- 标签：type:docs stage:S2 module:docs priority:P0
- 验收：发布 S2 范围说明与 M2 验收清单草案，明确段落级追溯与 OCR 主链路

2. [S2][management] 样本与输入类型清单整理
- 截止：2026-05-10
- 标签：type:docs stage:S2 module:docs priority:P1
- 验收：样本清单覆盖 PDF、Word、扫描件和截图输入

## B. 刘文旭

3. [S2][model] 结构化字段协议与归一化适配
- 截止：2026-05-08
- 标签：type:feature stage:S2 module:model priority:P0
- 验收：结构化字段协议文档与适配代码完成，包含 section_id、paragraph_id、input_type 和来源类型

4. [S2][web] 任务接口联调
- 截止：2026-05-18
- 标签：type:feature stage:S2 module:web priority:P1
- 验收：任务状态查询、输入类型展示和结果拉取接口联调通过

## C. 邱馨甜

5. [S2][rules] field_mapping-v0.2 完成
- 截止：2026-05-06
- 标签：type:feature stage:S2 module:rules priority:P0
- 验收：映射表覆盖核心字段并评审通过，能映射到主规则库输入

6. [S2][rules] OCR 后处理与纠错规则首版
- 截止：2026-05-16
- 标签：type:test stage:S2 module:ocr priority:P1
- 验收：误识别修正策略文档与代码完成，低置信度可标记

## D. 叶泽东

7. [S2][parser] PDF 与 Word 解析主流程
- 截止：2026-05-10
- 标签：type:feature stage:S2 module:parser priority:P0
- 验收：单报告解析成功并输出结构化中间结果，页码、章节序号、段落编号和图片索引齐全

8. [S2][storage] 结构化数据存储与回放链路
- 截止：2026-05-18
- 标签：type:feature stage:S2 module:storage priority:P1
- 验收：字段记录可保存并可回读，支持 parse/OCR/field 关联查询

## E. 王牧秋

9. [S2][ocr] OCR 批处理主流程实现
- 截止：2026-05-09
- 标签：type:feature stage:S2 module:ocr priority:P0
- 验收：批处理识别可运行并输出结果，OCR 进入主链路

10. [S2][ocr] OCR 后处理与来源合并
- 截止：2026-05-18
- 标签：type:feature stage:S2 module:ocr priority:P1
- 验收：OCR 结果含 raw/normalized/confidence，能回写来源页码和段落编号

## F. 吴世豪

11. [S2][ci] 解析与 OCR 回归测试基线
- 截止：2026-05-05
- 标签：type:test stage:S2 module:ci priority:P0
- 验收：parser/OCR 回归套件纳入 CI，覆盖 PDF 与 Word

12. [S2][test] M2 阶段回归报告发布
- 截止：2026-05-20
- 标签：type:docs stage:S2 module:docs priority:P1
- 验收：提交 M2 回归报告与缺陷闭环清单

## S2 提交节奏要求

- 每日：每人至少 1 次 Push
- 周三 22:00：中期同步 Push
- 周日 22:00：合并稳定分支到 develop
- 2026-05-20：打里程碑标签 v0.2-m2
