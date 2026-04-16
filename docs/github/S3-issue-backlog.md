# S3阶段 Issue 清单（2026-05-21 至 2026-06-20）

配套执行文档：docs/github/S3-协同开发执行手册.md

使用建议：
- 先关闭规则引擎 P0，再推进模型复核 P1
- 所有 Issue 必须附样本输入与预期输出

执行规则：
- 规则类 Issue 必须覆盖 PASS、FAIL、REVIEW 至少两类样例。
- 模型类 Issue 必须说明模型输出是否只作为解释和复核建议。
- 证据类 Issue 必须保留 `field/value/page/snippet/source_type`。
- 关闭 Issue 前必须说明是否改变 `RuleResult` 或 `EvidenceTrace`。

## A. 徐志翔

1. [S3][rules] 冻结规则优先级与冲突处理策略
- 截止：2026-05-26
- 标签：type:feature stage:S3 module:rules priority:P0
- 验收：冲突处理策略文档发布并评审通过

2. [S3][management] M3验收清单发布
- 截止：2026-06-19
- 标签：type:docs stage:S3 module:docs priority:P0
- 验收：M3验收清单发布并团队签收

## B. 刘文旭

3. [S3][model] 语义归一化模块实现
- 截止：2026-06-05
- 标签：type:feature stage:S3 module:model priority:P0
- 验收：归一化模块输出可用于规则复核

4. [S3][model] 辅助复核与解释输出
- 截止：2026-06-17
- 标签：type:feature stage:S3 module:model priority:P1
- 验收：复核结论与解释字段完整输出

## C. 邱馨甜

5. [S3][rules] 首版规则引擎规则集
- 截止：2026-06-08
- 标签：type:feature stage:S3 module:rules priority:P0
- 验收：核心规则可执行并输出三态结果

6. [S3][rules] 待复核触发策略
- 截止：2026-06-18
- 标签：type:test stage:S3 module:rules priority:P1
- 验收：触发条件与阈值策略文档完成

## D. 叶泽东

7. [S3][parser] 提取输出与规则输入适配
- 截止：2026-06-07
- 标签：type:feature stage:S3 module:parser priority:P0
- 验收：提取字段对齐规则引擎输入规范

8. [S3][storage] 判定结果落库与异常处理
- 截止：2026-06-16
- 标签：type:feature stage:S3 module:deploy priority:P1
- 验收：结果可保存并具备异常重试机制

## E. 王牧秋

9. [S3][evidence] 证据追溯增强模块
- 截止：2026-06-10
- 标签：type:feature stage:S3 module:evidence priority:P0
- 验收：每条结果可关联页码片段截图来源

10. [S3][reporting] 简要分析导出接口
- 截止：2026-06-18
- 标签：type:feature stage:S3 module:evidence priority:P1
- 验收：输出问题分布与待复核摘要

## F. 吴世豪

11. [S3][ci] 规则与模型回归门禁
- 截止：2026-06-06
- 标签：type:test stage:S3 module:ci priority:P0
- 验收：规则与模型回归纳入CI门禁

12. [S3][test] M3阶段质量报告
- 截止：2026-06-20
- 标签：type:docs stage:S3 module:docs priority:P1
- 验收：发布M3质量报告与缺陷闭环清单

## S3提交节奏要求

- 每日：规则或模型变更当天必须附测试证据
- 周二：规则更新PR集中评审
- 周四：模型链路PR集中评审
- 周日 22:00：合并稳定分支到 develop
- 2026-06-20：打里程碑标签 v0.3-m3
