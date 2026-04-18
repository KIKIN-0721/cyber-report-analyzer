# S1-OCR 后处理策略

> 版本：v0.1  
> 阶段：S1（2026-03-31 至 2026-04-20）  
> 负责：王牧秋（OCR 与证据溯源模块）  
> 依据：以项目仓库 `./cyber-report-analyzer` 内接口规范与规则台账为准

---

## 1. 目标与范围

本文档定义从“原始截图”到“结构化字段”的后处理策略，是 OCR 模块（`src/ocr/`）与证据模块（`src/evidence/`）的开发基线。

**S1 必须明确的内容**：
- 首选 OCR 引擎及其调用方式
- 文本清洗、字段提取、纠错归一化的三级流水线
- 首版（S1/S2）必须覆盖的高优先级字段：RSA 密钥长度、TLS 版本、弱算法关键词
- 与模型归一化模块（`src/model_review/`）的职责边界
- 低置信度与异常样本的处理策略

**S1 明确不做的内容**：
- 完整 Web 页面集成
- 全量规则字段的 OCR 提取（P1 规则留待 S2/S3 扩展）
- 端到端性能优化与多引擎并发调度

---

## 2. OCR 引擎选型

### 2.1 默认引擎：PaddleOCR

根据项目架构文档与接口规范，**默认采用 PaddleOCR** 作为首版 OCR 引擎。

**选型依据**：
- 项目接口文档明确将 PaddleOCR 列为能力层 OCR 组件（`docs/architecture/` 系列）
- 中文场景（含中英混合命令行截图、配置界面截图）开源效果稳定
- 本地可私有化部署，无需公网服务，符合企业交付要求
- 团队成员本地环境已预装，降低 S1/S2 环境搭建成本

**调用方式**：
- 单张调用：`paddleocr.PaddleOCR.ocr(image_path)`
- 批量调用：内部循环单张调用，S2 视性能情况引入批处理缓存或并发

### 2.2 备选机制

为降低扫描件、低分辨率截图、特殊字体的识别风险，后处理层预留引擎抽象接口。若 PaddleOCR 在 S2 回归样本中连续出现某类截图识别率低于可接受阈值，可平滑切换或采用**双引擎投票**机制：
- **备选引擎**：EasyOCR（中文场景兼容较好，安装轻量）
- **切换点**：抽象在 `src/ocr/ocr_engine.py`（建议新增），`ocr_pipeline.py` 仅消费标准化输出，不直接耦合 PaddleOCR API
- **S1 不实现切换代码**，但需在 `src/ocr/` 的模块接口中预留该抽象位置

---

## 3. 后处理 Pipeline（三级流水线）

从 PaddleOCR 原始输出到最终 `OCRResultV2` / `StructuredField`，划分为三个阶段：

```
[PaddleOCR 原始输出]
        ↓
┌─────────────────┐
│  Stage 1: 清洗  │  去噪、合并断行、去除无意义符号
└────────┬────────┘
         ↓
┌─────────────────┐
│  Stage 2: 提取  │  正则匹配、关键词命中、字段标准化
└────────┬────────┘
         ↓
┌─────────────────┐
│  Stage 3: 纠错  │  词典替换、常见错字修正、置信度校验
└────────┬────────┘
         ↓
[OCRResultV2 / StructuredField]
```

### 3.1 Stage 1 — 文本清洗

**输入**：PaddleOCR 返回的 `[[[bbox], (text, confidence)], ...]`

**处理规则**：
1. **拼接顺序**：按 bbox 的 `y` 坐标从上到下、`x` 坐标从左到右排序后拼接
2. **断行合并**：若两行文本的 `y` 差值小于平均行高，且 `x` 起始位置接近，视为同一行，以空格连接
3. **去噪**：
   - 删除纯数字页码、页眉页脚中的固定文案（如 `"Page 3 of 10"`）
   - 删除单字符孤立噪声（长度 `== 1` 且为非字母数字符号）
   - 将多个连续空格/换行压缩为单个空格
4. **编码统一**：输出统一为 UTF-8，全角字母数字转半角

**输出**：`raw_text`（对应 `OCRResultV2.raw_text`）

### 3.2 Stage 2 — 字段提取

基于 `src/rules_engine/s1_rulebook.py` 中定义的 P0 规则字段，建立首版提取模式。

| 标准字段名 | 规则来源 | 提取策略 | 示例 |
|-----------|---------|---------|------|
| `crypto.rsa.key_length` | `S1-RSA-001` | 正则：`RSA\s*[-_]?\s*(\d{3,4})\b` 或 `(\d{3,4})\s*[-_]?\s*bit\s*RSA` | `RSA2048` → `2048` |
| `crypto.tls.version` | `S1-TLS-001` | 正则：`TLS\s*v?\s*([0-9](?:\.[0-9])?)` | `TLS 1.2` → `1.2` |
| `crypto.weak` | `S1-WEAK-001` | 关键词白名单命中：MD5、SHA-1、DES、3DES、RC4、ECB | `MD5` / `SHA1` |

**提取规则补充说明**：
- 同一字段允许多次命中（例如一张截图里同时出现 `TLS 1.2` 和 `RSA 2048`），每条命中独立生成一条 `StructuredField`
- 提取后的 `value` 应做最小化归一：仅保留核心数值或标准缩写（如 `2048`、`1.2`、`MD5`）
- 未命中任何模式的文本，保留 `raw_text` 但不生成 `field`，供后续模型复核使用

### 3.3 Stage 3 — 纠错与置信度校验

#### 3.3.1 纠错词典

建立 `src/ocr/correction_dict.yaml`，首版覆盖以下常见 OCR 误差：

```yaml
# 字符形近误识别
corrections:
  - error: "TSL"
    correct: "TLS"
    category: "protocol"
  - error: "SHA1"
    correct: "SHA-1"
    category: "algorithm"
  - error: "SHA 1"
    correct: "SHA-1"
    category: "algorithm"
  - error: "RS A"
    correct: "RSA"
    category: "crypto"
  - error: "TL S"
    correct: "TLS"
    category: "protocol"
  - error: "1.O"    # 字母 O 与数字 0 混淆
    correct: "1.0"
    category: "version"
  - error: "1.l"    # 字母 l 与数字 1 混淆
    correct: "1.1"
    category: "version"
```

**应用规则**：
- 词典纠错在正则提取**之前**执行，避免错误文本无法匹配正则
- 仅对置信度 `< 0.90` 的 token 应用纠错，高置信度文本优先保持原样
- 纠错动作记录到 `correction_type`（`dict` / `regex` / `none`），供下游追溯

#### 3.3.2 置信度阈值策略

| 置信度区间 | 处理策略 |
|-----------|---------|
| `>= 0.90` | 直接提取，进入规则引擎 |
| `0.75 ~ 0.89` | 执行提取，但标记 `confidence_flag: low`，优先进入模型复核或人工复核 |
| `< 0.75` | 提取结果标记为 `REVIEW`，不直接参与硬规则判定，仅作为候选片段供人工确认 |

**说明**：该阈值可在 `src/ocr/config.yaml` 中配置，S2 根据回归样本调优。

---

## 4. 关键字段提取策略（对齐 S1 规则台账）

### 4.1 RSA 密钥长度（`crypto.rsa.key_length`）

**模式库**：
```python
RSA_PATTERNS = [
    re.compile(r"RSA\s*[-_]?\s*(\d{3,4})\b", re.IGNORECASE),
    re.compile(r"\b(\d{3,4})\s*[-_]?\s*bit\s*RSA\b", re.IGNORECASE),
    re.compile(r"Key\s*length\s*:?\s*(\d{3,4})\b", re.IGNORECASE),
]
```

**归一化输出**：仅保留数字字符串，如 `"2048"`、`"3072"`。

### 4.2 TLS 版本（`crypto.tls.version`）

**模式库**：
```python
TLS_PATTERNS = [
    re.compile(r"TLS\s*v?\s*([0-9](?:\.[0-9])?)\b", re.IGNORECASE),
    re.compile(r"SSL\s*v?\s*([0-9](?:\.[0-9])?)\b", re.IGNORECASE),
]
```

**归一化输出**：版本号字符串，如 `"1.2"`、`"1.3"`。若命中 `SSL`，保留原词并在 `snippet` 中记录原始文本，供规则引擎判断。

### 4.3 弱算法关键词（`crypto.weak`）

**模式库**（直接复用 `src/rules_engine/rule_engine.py` 中的 `WEAK_ALGO_PATTERNS`）：
```python
WEAK_ALGO_PATTERNS = {
    "MD5": re.compile(r"\bmd5\b", re.IGNORECASE),
    "SHA-1": re.compile(r"\bsha[\s_-]?1\b", re.IGNORECASE),
    "DES": re.compile(r"\bdes\b", re.IGNORECASE),
    "3DES": re.compile(r"\b3des\b", re.IGNORECASE),
    "RC4": re.compile(r"\brc4\b", re.IGNORECASE),
    "ECB": re.compile(r"\becb\b", re.IGNORECASE),
}
```

**归一化输出**：命中的标准算法名，如 `"MD5"`、`"SHA-1"`。若同一张截图命中多个，生成多条 `StructuredField`。

---

## 5. 与模型归一化模块的分工边界

为避免 OCR 后处理与模型复核（`src/model_review/reviewer.py`）职责重叠，明确分工如下：

| 处理层级 | 负责模块 | 处理内容 | 输出示例 |
|---------|---------|---------|---------|
| **硬规则提取** | `src/ocr/post_processor.py` | 正则、词典、关键词等确定性提取与修正 | `RSA2048` → `field=crypto.rsa.key_length, value=2048` |
| **语义归一化** | `src/model_review/reviewer.py` | 对模糊、口语化、非标准表述做语义理解和归一 | `"Key length 2048"` → `normalized=RSA-2048` |
| **置信度仲裁** | `src/ocr/ocr_pipeline.py` | 基于 OCR 置信度决定是直接放行还是进入复核 | `confidence >= 0.90` 放行，`< 0.75` 强制 REVIEW |

**接口约定**：
- OCR 模块输出 `normalized_text` 和 `confidence`，作为模型复核的输入之一
- 模型复核不对 OCR 原始图片进行二次识别，仅对文本结果做语义处理
- 若 OCR 已能通过正则提取出标准字段，模型复核可跳过或仅做确认

---

## 6. 输出协议（对齐 S2 接口规范）

OCR 模块最终输出必须对齐 `OCRResultV2`：

```json
{
  "image_id": "img-0001",
  "page": 3,
  "raw_text": "TLS1.2 RSA2048",
  "normalized_text": "TLS-1.2 RSA-2048",
  "confidence": 0.91,
  "tokens": ["TLS1.2", "RSA2048"]
}
```

经字段提取器转换后，进入规则引擎的 `StructuredField` 格式：

```json
{
  "field": "crypto.rsa.key_length",
  "value": "2048",
  "source_type": "image_ocr",
  "page": 3,
  "snippet": "RSA2048",
  "confidence": 0.91
}
```

---

## 7. 风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|---------|
| PaddleOCR 对扫描件/低分辨率截图识别率低 | S2 部分样本无法通过 | ① S2 优先保证原生 PDF 和清晰截图；② 扫描件标记为风险样本；③ 预留 EasyOCR 切换接口 |
| 命令行截图存在大量特殊字符和颜色块干扰 | 误识别率高 | 在 Stage 1 增加特殊符号过滤；对命令行截图单独建立后处理模板 |
| 词典无法覆盖全部 OCR 错字 | 偶发性字段提取失败 | 建立持续积累机制，S2 每发现一个新错字模式，立即补充到 `correction_dict.yaml` |
| `page` 信息上游传递缺失 | 证据溯源失败 | S2 第一周与叶泽东（parser）强制对齐 `ParseResultV2.images` 的 `page` 字段 |

---

## 8. 附录：S1 → S2 演进 checklist

- [ ] `docs/architecture/S1-OCR后处理策略.md` 评审通过（S1）
- [ ] `src/ocr/ocr_pipeline.py` 实现 `run_ocr()` 并输出 `OCRResultV2`（S2）
- [ ] `src/ocr/ocr_pipeline.py` 实现 `run_batch_ocr()`（S2）
- [ ] `src/ocr/post_processor.py` 完成 Stage 1~3 流水线（S2）
- [ ] `src/ocr/correction_dict.yaml` 覆盖首版常见错字（S2）
- [ ] `tests/ocr/` 覆盖单张识别、批处理、字段提取三类测试（S2）
