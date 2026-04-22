# S4 阶段 Issue 清单（Word 输出一致性版）

配套执行文档：docs/github/S4-协同开发执行手册.md

使用建议：
- 优先保障上传-解析-展示-规则维护-Word 导出主流程。
- 每个缺陷 Issue 必须包含复现步骤和回归结果。

执行规则：
- Web 展示类 Issue 必须附接口响应样例或截图。
- 导出类 Issue 必须验证页面字段和 Word 字段一致。
- 规则维护类 Issue 必须验证保存后立即生效。
- 缺陷类 Issue 必须包含复现步骤、修复说明、回归结果。
- 关闭 Issue 前必须确认不破坏 S3 已冻结结果结构。

## A. 徐志翔

1. [S4][management] 冻结演示路径与 M4 验收标准
- 截止：2026-06-24
- 标签：type:docs stage:S4 module:docs priority:P0
- 验收：演示路径文档与 M4 验收清单草案发布，包含 Word 导出演示

2. [S4][management] M4 验收组织与缺陷收敛检查
- 截止：2026-07-09
- 标签：type:docs stage:S4 module:docs priority:P1
- 验收：缺陷收敛清单与验收纪要完成

## B. 刘文旭

3. [S4][web] 上传与结果查询流程联调
- 截止：2026-07-03
- 标签：type:feature stage:S4 module:web priority:P0
- 验收：上传、查询流程可演示

4. [S4][web] 规则维护与 Word 导出接口完善
- 截止：2026-07-08
- 标签：type:feature stage:S4 module:web priority:P1
- 验收：规则保存后立即生效，筛选与导出接口稳定可用

## C. 邱馨甜

5. [S4][rules] 误判分析样本集与修正规则
- 截止：2026-07-02
- 标签：type:test stage:S4 module:rules priority:P0
- 验收：误判样本集发布并给出修正规则

6. [S4][rules] 命中率优化报告
- 截止：2026-07-08
- 标签：type:docs stage:S4 module:rules priority:P1
- 验收：提交命中率优化记录与结论

## D. 叶泽东

7. [S4][parser] 联调稳定性与异常修复
- 截止：2026-07-04
- 标签：type:feature stage:S4 module:parser priority:P0
- 验收：主流程异常率显著下降

8. [S4][deploy] 联调部署说明更新
- 截止：2026-07-08
- 标签：type:docs stage:S4 module:deploy priority:P1
- 验收：联调部署说明可复现

## E. 王牧秋

9. [S4][evidence] 证据查看功能落地
- 截止：2026-07-03
- 标签：type:feature stage:S4 module:evidence priority:P0
- 验收：支持按结果定位证据页码、段落编号和截图

10. [S4][reporting] 导出一致性校验
- 截止：2026-07-08
- 标签：type:test stage:S4 module:reporting priority:P1
- 验收：Word 导出结果与页面展示一致

## F. 吴世豪

11. [S4][ci] 端到端回归基线
- 截止：2026-06-30
- 标签：type:test stage:S4 module:ci priority:P0
- 验收：S4 主流程回归纳入 CI

12. [S4][test] M4 质量报告发布
- 截止：2026-07-10
- 标签：type:docs stage:S4 module:docs priority:P1
- 验收：发布质量报告与缺陷闭环清单

## S4 提交节奏要求

- 每日：提交联调日志或测试记录
- 周三：联调结果同步
- 周六：回归报告上传
- 周日 22:00：合并稳定分支到 develop
- 2026-07-10：打里程碑标签 v0.4-m4
