# S5 阶段 Issue 清单（发布冻结版）

配套执行文档：docs/github/S5-协同开发执行手册.md

使用建议：
- S5 禁止无评估的新功能进入发布分支。
- 优先完成文档齐套与发布质量闭环。

执行规则：
- S5 Issue 只分为发布阻断、文档归档、演示脚本、发布包四类。
- 新功能默认不进入 release 分支，除非负责人确认是阻断项。
- 每个发布修复 Issue 必须说明是否影响演示路径。
- 关闭 Issue 前必须附最终复现命令、截图、日志或文档链接。

## A. 徐志翔

1. [S5][management] 结题交付清单发布
- 截止：2026-07-20
- 标签：type:docs stage:S5 module:docs priority:P0
- 验收：交付清单覆盖全部必交材料

2. [S5][management] 最终验收纪要与结题组织
- 截止：2026-07-31
- 标签：type:docs stage:S5 module:docs priority:P0
- 验收：最终验收纪要归档完成

## B. 刘文旭

3. [S5][model] 发布版接口与模型模块收敛
- 截止：2026-07-22
- 标签：type:feature stage:S5 module:model priority:P1
- 验收：接口说明与发布版一致

4. [S5][web] 演示脚本与运行手册
- 截止：2026-07-28
- 标签：type:docs stage:S5 module:web priority:P1
- 验收：演示脚本可按文档复现

## C. 邱馨甜

5. [S5][rules] 规则库发布说明
- 截止：2026-07-23
- 标签：type:docs stage:S5 module:rules priority:P1
- 验收：规则库版本、来源和变更说明齐备

6. [S5][rules] 规则覆盖统计与结题图表
- 截止：2026-07-29
- 标签：type:docs stage:S5 module:rules priority:P1
- 验收：覆盖统计可用于答辩展示

## D. 叶泽东

7. [S5][deploy] 部署说明完善
- 截止：2026-07-24
- 标签：type:docs stage:S5 module:deploy priority:P1
- 验收：部署说明可从零复现

8. [S5][deploy] 发布包构建脚本
- 截止：2026-07-29
- 标签：type:chore stage:S5 module:deploy priority:P1
- 验收：发布包构建脚本可执行

## E. 王牧秋

9. [S5][evidence] 导出一致性最终检查
- 截止：2026-07-24
- 标签：type:test stage:S5 module:evidence priority:P1
- 验收：Word 导出结果与页面展示一致

10. [S5][reporting] 演示案例说明整理
- 截止：2026-07-29
- 标签：type:docs stage:S5 module:reporting priority:P1
- 验收：演示案例可直接用于结题汇报

## F. 吴世豪

11. [S5][ci] 发布回归与门禁确认
- 截止：2026-07-25
- 标签：type:test stage:S5 module:ci priority:P0
- 验收：发布候选版本回归通过

12. [S5][test] 最终测试报告定稿
- 截止：2026-07-30
- 标签：type:docs stage:S5 module:docs priority:P0
- 验收：最终测试报告提交并归档

## S5 提交节奏要求

- 每日：更新发布风险和阻塞项
- 周三：发布候选版本检查
- 周五：缺陷清零检查
- 2026-07-31：发布里程碑标签 v1.0-final
