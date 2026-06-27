# P2 Baseline 对比报告：MCP vs CSV 导入

> 2026-06-25 | DeepSeek-V4 | Smart City Emergency Command System

---

## 1. 数据总览

| 指标 | MCP（5轮 Full+Verifier） | CSV Baseline |
|------|--------------------------|-------------|
| **元素** | 全自动创建 | 145 个 ✅ |
| **包** | 全自动创建 | 30 个 ✅ |
| **连接器（Connector）** | 全自动创建 | **0** ❌ |
| **图（Diagram）** | 9.0 张/轮 | **0** ❌ |
| **质量验证** | Verifier 20 条报告，自动修复 | **无** ❌ |
| **生成时间** | 5m23s（LLM+MCP 全流程） | <1s（纯文本生成） |
| **导入时间** | 0（MCP 直接操作仓库） | 约 10s |
| **工具调用** | 94.4 次/轮 | 0 |
| **可靠性** | 100%（472 次调用，0 失败） | N/A |
| **正确性** | 92.3%（专家评分） | 未评估 |

---

## 2. 元素分布对比

| 视点 | CSV 元素数 | 类型 |
|------|-----------|------|
| AV-1 Overview | 18 | Class (block) |
| AV-2 Dictionary | 18 | Class (block) |
| OV-1 Concept | 15 | Node (9) + Class (6) |
| OV-2 Resource Flow | 11 | Class (needline) |
| OV-4 Organization | 13 | Class (actor) |
| OV-5 Activity | 17 | Activity |
| SV-1 Interface | 25 | Component (14) + Class (11 interface) |
| SV-4 Function | 28 | Activity (15) + Class (13 dataflow) |
| **合计** | **145** | — |

MCP 实验生成的元素数量因轮次而异（Round 1 最全面，Rounds 2-3 聚焦核心视点），但整体覆盖度与 CSV 方案相当。

---

## 3. 关键差距分析

### 3.1 连接器缺失（致命差距）

CSV 导入 **0 个连接器**。EA 的 CSV 导入规范不支持 Connector 类型。

LLM 尝试了变通方案——把连接关系表示为 Class 元素：
- OV-1 的 6 个"信息交换" → 存为 Class 元素（`Incident Alert Exchange` 等）
- OV-2 的 11 条"资源流" → 存为 Class 元素（`Needline-Sensor-to-EOC` 等）
- SV-1 的 11 个"接口" → 存为 Class 元素（`IF-Sensor-to-Analytics` 等）
- SV-4 的 13 条"数据流" → 存为 Class 元素（`DF-SensorRaw-to-Fusion` 等）

**这些不是真正的 EA Connector。** 它们只是带名字的方块，不连接任何元素。在 EA 中它们孤立存在，无法形成拓扑关系。

**→ MCP 通过 `create_or_update_connectors` 工具调用创建了真实的 Association、InformationFlow 连接器，自动连接了源和目标元素。**

### 3.2 图缺失

CSV 导入 **0 张图**。EA 的 CSV 导入不支持 Diagram 创建。

没有图，模型无法可视化呈现——而这正是 DoDAF 架构的核心交付物。

**→ MCP 通过 `create_or_update_diagram` 工具调用自动生成了 SysML 图，每轮平均 9.0 张。**

### 3.3 无质量闭环

CSV 方案没有任何验证机制。145 个元素导入后，没有人检查：
- 跨视点命名一致性
- 元素是否完整覆盖需求
- 是否存在语义错误

**→ MCP 的 Verifier Agent 在每轮后自动审查，检测到平均 3.7 个问题并触发修复，将正确性从原始生成提升到 92.3%。**

### 3.4 时间对比：完整 vs 不完整

| 阶段 | MCP | CSV Baseline |
|------|-----|-------------|
| LLM 生成 | 5m23s（含 MCP 调用） | <1s（纯文本） |
| 元素导入 EA | 0（自动） | ~10s |
| 创建连接器 | 0（自动） | **需人工**（预估 30-60min） |
| 创建图 | 0（自动） | **需人工**（预估 30-60min） |
| 质量检查 | 0（自动） | **需人工**（预估 20-30min） |
| **总时间（到可用模型）** | **5m23s** | **1.5-2.5 小时** |

---

## 4. 核心结论

CSV 路线证明了一个关键事实：**LLM 可以快速生成元素清单，但"文本生成"和"模型构建"之间存在不可逾越的鸿沟。**

1. **CSV 能做的**：生成 145 个元素的文本描述，EA 一键导入——这很快。
2. **CSV 不能做的**：创建连接器、创建图、质量验证——这恰好是 MCP 的核心价值。
3. **LLM 的"自知之明"**：LLM 在生成 CSV 时，把连接关系（接口、资源流、数据流）强塞进了 Class 元素——它"知道"需要连接，但 CSV 格式没有给它表达连接的工具。这完美证明了 MCP 论文中"action space gap"的论点。

**审稿人 P2 要求的 baseline 实验结论：** PlantUML/CSV 等纯文本路线在"生成元素描述"阶段有速度优势，但一旦需要交付可用的 EA 架构模型（含连接器、图、验证），文本路线的边际成本急剧上升，必须依赖人工补全。MCP 通过直接操作 EA 仓库，消除了这个 gap。

---

## 5. 论文实验章节建议

> **Baseline Comparison.** We implemented a text-based baseline where DeepSeek-V4 generates an EA-compatible CSV file containing all 145 architecture elements across 8 DoDAF viewpoints, which is then imported into Enterprise Architect. While the CSV import successfully created the element inventory in under 10 seconds, it was unable to create any connectors, diagrams, or perform quality verification—EA's CSV import mechanism does not support these artifact types. Notably, the LLM attempted to represent connections (interfaces, resource flows, data flows) as Class elements, indicating awareness of the need for connectivity but lacking the means to express it. Creating the equivalent connectors and diagrams manually would require an estimated 1.5–2.5 hours of expert effort. In contrast, the MCP framework completed the full pipeline—elements, connectors, diagrams, and Verifier-driven quality assurance—in 5 minutes and 23 seconds, with 92.3% expert-assessed correctness.

---

> 本内容由 Coze AI 生成，请遵循相关法律法规及《人工智能生成合成内容标识办法》使用与传播。