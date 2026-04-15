# cyber-report-analyzer

网络安全报告分析工具（原型项目）。

## 项目目标

构建面向企业网络安全报告的半自动分析流程：
- PDF文本与截图提取
- OCR识别与字段归一化
- 规则判定（PASS/FAIL/REVIEW）
- 证据溯源与简要结果输出

## 当前代码结构

- src/parser: PDF解析骨架
- src/ocr: OCR流程骨架
- src/rules_engine: 规则引擎骨架
- src/model_review: 模型复核骨架
- src/evidence: 证据映射骨架
- src/reporting: 报告汇总导出骨架
- src/web: Web服务占位
- src/storage: 存储层占位

## 说明

当前版本为协同开发初始化代码骨架，用于团队并行开发与持续集成搭建。
