# S2阶段 Issue 清单（2026-04-21 至 2026-05-20）

配套执行文档：docs/github/S2-协同开发执行手册.md

使用建议：
- 先按模块创建 P0 Issue，再补充 P1
- 所有 Issue 必须打全标签（type、stage、module、priority）
- 关键链路问题优先处理 parser 与 ocr

执行规则：
- 所有字段输出必须对齐 `StructuredField` 语义。
- parser/OCR 任务必须保留来源页码、片段或图片引用。
- 存储任务必须支持结果回放，不能只做临时变量。
- 关闭 Issue 前必须说明对 S3 规则输入是否有影响。

## A. 徐志翔

1. [S2][management] 冻结S2范围与M2验收标准
- 截止：2026-04-24
- 标签：type:docs stage:S2 module:docs priority:P0
- 验收：发布S2范围说明与M2验收清单草案

2. [S2][rules] S2字段闭环验收评审
- 截止：2026-05-19
- 标签：type:feature stage:S2 module:rules priority:P1
- 验收：字段抽取闭环评审通过

## B. 刘文旭

3. [S2][model] 字段归一化协议与适配层
- 截止：2026-05-08
- 标签：type:feature stage:S2 module:model priority:P0
- 验收：结构化字段协议文档与适配代码完成

4. [S2][web] 任务接口联调
- 截止：2026-05-18
- 标签：type:feature stage:S2 module:web priority:P1
- 验收：任务状态查询与结果拉取接口联调通过

## C. 邱馨甜

5. [S2][rules] field_mapping-v0.2 完成
- 截止：2026-05-06
- 标签：type:feature stage:S2 module:rules priority:P0
- 验收：映射表覆盖核心字段并评审通过

6. [S2][test] 抽取字段校核规则
- 截止：2026-05-16
- 标签：type:test stage:S2 module:rules priority:P1
- 验收：字段校核规则文档与样例完成

## D. 叶泽东

7. [S2][parser] PDF解析与截图分离主流程
- 截止：2026-05-10
- 标签：type:feature stage:S2 module:parser priority:P0
- 验收：单报告解析成功并输出结构化中间结果

8. [S2][storage] 结构化数据存储链路
- 截止：2026-05-18
- 标签：type:feature stage:S2 module:deploy priority:P1
- 验收：字段记录可保存并可回读

## E. 王牧秋

9. [S2][ocr] OCR批处理流程实现
- 截止：2026-05-09
- 标签：type:feature stage:S2 module:ocr priority:P0
- 验收：批处理识别可运行并输出结果

10. [S2][ocr] OCR后处理与纠错规则首版
- 截止：2026-05-18
- 标签：type:feature stage:S2 module:ocr priority:P1
- 验收：误识别修正策略文档与代码完成

## F. 吴世豪

11. [S2][ci] 解析与OCR回归测试基线
- 截止：2026-05-05
- 标签：type:test stage:S2 module:ci priority:P0
- 验收：parser/ocr回归套件纳入CI

12. [S2][test] M2阶段回归报告发布
- 截止：2026-05-20
- 标签：type:docs stage:S2 module:docs priority:P1
- 验收：提交M2回归报告与缺陷闭环清单

## S2提交节奏要求

- 每日：每人至少1次Push
- 周三22:00：中期同步Push
- 周日 22:00：合并稳定分支到 develop
- 2026-05-20：打里程碑标签 v0.2-m2
