---
status: active
domain: Projects
para: projects
parent: 1-Projects
type: 方案
tags: [系统进化, AI, EvoMap, Claude-Code]
summary: 将 EvoMap 的 AI Agent 自进化思想迁移到奥一的第二大脑系统中，复用现有 Claude Code 基础设施
created: 2026-02-25
---

# 🧬 EvoMap 进化系统 → 第二大脑 迁移方案

> **"一个会话学会，所有会话继承。"**

---

## 〇、你应该怎么读这篇文档

这份文档是一份**建议方案**，描述了如何把 EvoMap 项目中最有价值的设计思想，嫁接到你现有的 Claude Code 第二大脑系统上。

**不需要写任何代码**——所有实现都将由 Claude Code 帮你完成。你只需要：
1. 读懂每个模块"是什么"和"为什么"
2. 决定哪些要、哪些不要
3. 审批后，让 Claude 按方案执行

**阅读顺序建议**：
- 先看 **第一章** 理解总体思路（5 分钟）
- 再看 **第二章** 理解核心概念的翻译（10 分钟）
- **第三章** 是具体落地方案（重点）
- **第四章** 是优先级排序
- **第五章** 是实施路径

---

## 一、总体思路：不是移植代码，而是移植思想

### 1.1 关键判断

EvoMap 的 Capability Evolver 是为 OpenClaw 平台设计的 Node.js 引擎。**直接移植代码到 Claude Code 没有意义**，原因：

| EvoMap 的做法 | 你的场景 |
|:---|:---|
| 用 Node.js 代码跑进化循环 | Claude Code 本身就是"大脑"，不需要额外引擎 |
| 扫描 .jsonl 日志提取信号 | Claude 直接在对话里就能理解上下文 |
| 生成提示词让 Agent 执行 | Claude 本身就是 Agent，直接执行 |
| 需要复杂的安全防护 | 你已有审批机制（pending_approvals.md） |

### 1.2 真正要迁移的是什么

EvoMap 最有价值的不是代码，而是**三个核心思想**：

```
思想 1: 经验结构化
  把"对话中学到的东西"变成可复用的结构化资产（Gene / Capsule），
  而不只是散落在记忆里的文字

思想 2: 信号驱动的自动匹配
  下次遇到类似问题时，系统能自动找到之前成功的解决方案，
  而不是从头开始

思想 3: 可审计的进化轨迹
  每次"学到了什么"都有记录——谁触发的、怎么解决的、效果如何，
  可以回溯、可以审计、可以复盘
```

### 1.3 你已有的基础设施（非常好）

你的第二大脑系统已经具备了很多迁移所需的基础：

| 已有能力 | 对应 EvoMap 概念 |
|:---|:---|
| `MEMORY.md` 长期记忆 | ≈ Agent 的"基因库"（但非结构化） |
| `daily/` 日常碎片 | ≈ 进化事件日志（但只记录了用户说了什么） |
| `pending_approvals.md` 审批 | ≈ 安全模型（Identity 变更需审批） |
| `change_log.md` 变更日志 | ≈ EvolutionEvent 事件记录 |
| `CONTEXT.md` 上下文 | ≈ 环境指纹（当前状态快照） |
| `stop_audit.py` Hook | ≈ 进化循环的"固化"步骤 |
| Skills 目录 | ≈ Gene 的执行层 |
| 三层分形 L1/L2/L3 | ≈ GEP 协议的层次结构 |

**你只需要在现有系统上"生长"出进化层，而不是推倒重来。**

---

## 二、核心概念翻译：EvoMap → 第二大脑

为了让你理解起来更自然，我把 EvoMap 的生物学隐喻翻译成你的第二大脑语境：

### 2.1 概念映射表

| EvoMap 术语 | 第二大脑翻译 | 一句话解释 | 存储位置 |
|:---|:---|:---|:---|
| **Gene（基因）** | **招式** | 一种可复用的"做事方法"。比如"如何写口播稿"、"如何做项目复盘"。 | `6-System/evolution/genes/` |
| **Capsule（基因胶囊）** | **战果** | 一次成功的完整记录。包含：触发条件、用了哪个招式、具体怎么做的、效果如何。 | `6-System/evolution/capsules/` |
| **EvolutionEvent** | **进化日志** | 记录"什么时候、因为什么信号、用了什么招式、结果如何"。 | `6-System/evolution/events.jsonl` |
| **Signal（信号）** | **触发词** | 触发某个招式的关键词或模式。比如"写口播稿"→ 触发"口播稿招式"。 | 招式文件中的 `triggers` 字段 |
| **Mutation（突变）** | **变更声明** | 每次进化前的显式声明："我打算做什么，风险多大"。 | 进化日志的一部分 |
| **Selector（选择器）** | **招式匹配** | 面对一个任务时，自动匹配最合适的招式。 | CLAUDE.md 规则 + 匹配逻辑 |
| **PersonalityState** | 不迁移 | 你的 TELOS 和 AI_RULES 已经覆盖了这个需求 | — |
| **MemoryGraph** | 不迁移 | 过于复杂，用简化版"战果匹配"替代 | — |
| **A2A Protocol** | 不迁移 | 单人使用，不需要跨 Agent 共享 | — |

### 2.2 简化原则

EvoMap 有 26 个 GEP 模块。**你只需要 4 个核心概念**：

```
1. 招式 (Gene)     → 怎么做某件事
2. 战果 (Capsule)  → 某次做成功了的完整记录
3. 进化日志 (Event) → 进化历史的 append-only 记录
4. 匹配规则        → 什么情况下用什么招式
```

---

## 三、具体落地方案

### 3.1 新增目录结构

在 `6-System/` 下新增一个 `evolution/` 目录：

```
6-System/evolution/
├── CLAUDE.md              # L2 - 进化子系统的局部地图
├── genes/                 # 招式库
│   ├── _template.md       # 招式模板（新建招式时参考）
│   └── *.md               # 各个招式文件
├── capsules/              # 战果库
│   └── *.md               # 各个战果文件
├── events.jsonl           # 进化日志（append-only）
└── evolution_state.json   # 进化状态（最近一次进化的摘要）
```

### 3.2 招式（Gene）的格式设计

每个招式是一个 Markdown 文件，**人类可读**，同时头部元数据带结构化信息供 Claude 匹配。

**文件示例**：`6-System/evolution/genes/口播稿写作.md`

```markdown
---
type: gene
id: gene_口播稿写作
category: writing
status: active
triggers:
  - 写口播稿
  - 口播改写
  - 自媒体文案
  - 视频脚本
preconditions:
  - 有源材料（文章/笔记/大纲）
  - 明确目标平台和风格
success_count: 3
fail_count: 0
last_used: 2026-02-20
created: 2026-02-14
---

# 🧬 招式：口播稿写作

## 什么时候用
用户需要把一篇文章/笔记改写成适合视频口播的文案时触发。

## 策略步骤
1. 确认源材料和目标平台
2. 提取核心观点（不超过 3 个）
3. 按 MEMORY.md 中的写作风格偏好改写：
   - 接地气的具体类比 > 泛泛而谈
   - 情感节点要有力，有画面感
   - 带身份感：用"普通人"
   - 金句锋利直接
   - 结尾给愿景，不用 CTA
4. 三段式结构：钩子（前 3 秒抓注意力）→ 价值（核心内容）→ 升华（金句收尾）
5. 输出到 Output/口播版/ 目录，文件名用时间戳格式

## 约束
- 总长度控制在 800-1500 字（3-5 分钟口播）
- 不用"首先、其次、最后"等书面过渡词
- 不用"大家好"开头

## 验证
- 读一遍：是否像"一个人在跟朋友聊天"？
- 画面感检查：每个核心观点是否有具体场景？
- 金句检查：至少 2 句可以单独截图传播的句子？

## 关联战果
- capsule_20260214_口播改写_成功
- capsule_20260205_视频脚本_成功
```

### 3.3 战果（Capsule）的格式设计

每个战果记录一次成功的完整上下文，**是招式的"活证据"**。

**文件示例**：`6-System/evolution/capsules/20260214_口播改写_成功.md`

```markdown
---
type: capsule
id: capsule_20260214_口播改写
gene: gene_口播稿写作
triggers_matched:
  - 口播改写
outcome: success
confidence: 0.9
context_snapshot:
  source: 3-Resources/AI工具/某篇文章.md
  output: Output/口播版/202602-141530-AI工具推荐.md
  session_date: 2026-02-14
created: 2026-02-14
---

# 战果：口播改写 (2026-02-14)

## 触发场景
用户要求把一篇 AI 工具推荐文章改写成口播稿。

## 实际做法
1. 提取了 3 个核心工具推荐
2. 用"你有没有遇到过..."开头做钩子
3. 每个工具配了具体使用场景（"就像你有个24小时在线的助手"）
4. 结尾用"未来已经来了，只是还没有均匀分配"升华

## 成功原因
- 严格遵循了 MEMORY.md 中的写作风格
- 类比选得好（"把它当百度用"这种级别）
- 没有用"大家好"和互动 CTA

## 教训 / 可改进
- 篇幅偏长（1800字），下次控制在 1500 以内
- 第二个工具的类比不够形象

## 用户反馈
用户表示满意，只是要求缩短了结尾部分。
```

### 3.4 进化日志（events.jsonl）

每行一个 JSON 对象，append-only，记录每次进化事件：

```jsonl
{"type":"evolution_event","id":"evt_20260214_1","timestamp":"2026-02-14T15:30:00+08:00","trigger":"用户要求口播改写","gene_used":"gene_口播稿写作","capsule_created":"capsule_20260214_口播改写","intent":"execute","outcome":"success","files_changed":1,"summary":"成功改写口播稿，用户满意"}
{"type":"gene_created","id":"evt_20260220_1","timestamp":"2026-02-20T10:00:00+08:00","gene_id":"gene_项目复盘","trigger":"用户做了一次项目复盘，效果很好","intent":"solidify","summary":"从成功的复盘对话中提炼出复盘招式"}
{"type":"gene_updated","id":"evt_20260222_1","timestamp":"2026-02-22T14:00:00+08:00","gene_id":"gene_口播稿写作","trigger":"用户反馈篇幅偏长","intent":"optimize","change":"约束中增加1500字上限","summary":"根据用户反馈优化招式"}
```

### 3.5 进化协议：如何与现有系统协同

#### 核心规则写入 CLAUDE.md

在 L1 的 `CLAUDE.md` 中新增一个 `<EVOLUTION>` 段落：

```markdown
<EVOLUTION>
进化系统

招式库位于 6-System/evolution/genes/，战果库位于 6-System/evolution/capsules/。

触发匹配（每次任务开始时）：
  1. 识别用户意图中包含的关键词
  2. 扫描 genes/ 目录下各招式文件的 triggers 字段
  3. 如果匹配到招式 → 告诉用户"发现相关招式：《xxx》，是否要参考？"
  4. 如果匹配到多个 → 结合 success_count 和 last_used 推荐最优
  5. 用户确认后 → 加载招式内容作为工作指导

进化沉淀（每次任务完成后）：
  1. 判断本次任务是否有值得记录的经验（新方法/新发现/失败教训）
  2. 如果有 → 主动提议："这次[做法]效果不错，要沉淀为招式/战果吗？"
  3. 用户审批后 → 写入对应文件 + 追加 events.jsonl
  
  沉淀分级（复用已有的变更协议）：
  - A类（自动）：更新已有招式的 success_count / fail_count / last_used
  - B类（需审批）：新建招式、修改招式策略、新建战果
  
招式进化：
  - 同一个招式被使用 3 次以上 → 分析所有战果 → 提议优化策略步骤
  - 一个招式连续失败 2 次 → 标记 status: needs_review → 提醒用户
  - 发现用户的做法比招式更好 → 提议更新招式

不要做：
  - 不要在用户没提到相关话题时主动推销招式
  - 不要自动创建招式（必须经过用户审批）
  - 不要删除任何招式或战果（只标记 status: deprecated）
</EVOLUTION>
```

#### Stop Hook 增强

增强现有的 `stop_audit.py`，在会话结束时**自动检测进化机会**：

```
现有行为（保留）：
  - 写入 daily memory breadcrumb

新增行为：
  - 检查本次会话是否触发了招式（读 evolution_state.json）
  - 如果触发了 → 更新招式的 last_used 和 success_count/fail_count
  - 将进化相关操作追加到 events.jsonl
```

### 3.6 匹配规则设计

匹配不需要写代码，**用 Claude 的自然语言理解能力替代**。

EvoMap 用正则表达式做硬匹配，你用 Claude 的语义理解做柔性匹配：

```
EvoMap 的做法（硬编码）：
  signal = "log_error" → match gene.signals_match 里有 "error" → 选中

你的做法（语义理解）：
  用户说"帮我写个短视频脚本" 
  → Claude 扫描 genes/ 目录
  → 发现"口播稿写作"招式的 triggers 包含"视频脚本"
  → 提示"要不要参考这个招式？"
```

**优势**：不需要精确匹配关键词，Claude 可以理解同义词和语义相近的表达。  
**代价**：每次会话开始时需要扫描 genes/ 目录（文件少的时候可以忽略不计）。

### 3.7 跨会话记忆的实现

你的需求是"上一个会话积累的经验，在新会话自动可用"。实现方式：

```
已有机制（直接复用）：
  - CLAUDE.md 每次会话自动加载 → 招式匹配规则在里面
  - contextFiles 自动注入 → MEMORY.md 等上下文

新增机制：
  - startup.py 增加"进化摘要"：扫描 genes/ 目录，输出招式清单概览
  - 用户开始工作时，Claude 根据对话内容自动匹配招式
  - 如果匹配上了，问用户是否要载入
```

**具体流程**：

```
[新会话开始]
  ↓
startup.py 执行 → 输出包含：
  "📊 招式库概览：12 个招式，最近使用：口播稿写作(2天前)"
  ↓
用户说"帮我写个视频文案"
  ↓
Claude 匹配到"口播稿写作"招式
  ↓
Claude: "发现相关招式《口播稿写作》(成功率100%，用了3次)。要参考这个招式吗？"
  ↓
用户: "好"
  ↓
Claude 加载招式内容，按策略步骤工作
  ↓
[任务完成]
  ↓
Claude: "这次做得不错。要记录为新战果吗？有什么新发现值得更新到招式里？"
  ↓
用户审批后 → 写入战果文件 + 更新进化日志
```

---

## 四、优先级排序：什么必须做，什么可以缓做

### P0 —— 核心骨架（必须做好）

| 项目 | 工作量 | 说明 |
|:---|:---|:---|
| 创建 `6-System/evolution/` 目录结构 | 5 分钟 | 创建目录 + CLAUDE.md + 模板 |
| 设计招式（Gene）模板 | 10 分钟 | 一个 `_template.md` 文件 |
| 设计战果（Capsule）模板 | 10 分钟 | 一个 `_template.md` 文件 |
| 在 L1 CLAUDE.md 中加入 `<EVOLUTION>` 规则 | 15 分钟 | 核心匹配和沉淀规则 |
| 创建 `events.jsonl` 空文件 | 1 分钟 | Append-only 进化日志 |

### P1 —— 让它转起来（强烈推荐）

| 项目 | 工作量 | 说明 |
|:---|:---|:---|
| 增强 `startup.py`：加入招式库概览 | 20 分钟 | 会话开始时展示可用招式 |
| 增强 `stop_audit.py`：进化状态更新 | 20 分钟 | 会话结束时自动更新统计 |
| 手动沉淀 3-5 个你已知的"好方法"为招式 | 30 分钟 | 冷启动招式库 |

### P2 —— 锦上添花（可以以后做）

| 项目 | 工作量 | 说明 |
|:---|:---|:---|
| 创建 `/evolve` 自定义命令 | 10 分钟 | 快捷触发进化沉淀 |
| 创建 `/genes` 自定义命令 | 10 分钟 | 快速浏览招式库 |
| 招式自动健康检查 | 30 分钟 | 检测过时招式、低成功率招式 |
| 进化报告生成 | 20 分钟 | 周/月自动生成进化复盘 |

### P3 —— 远期愿景（暂不实施）

| 项目 | 说明 |
|:---|:---|
| 招式蒸馏 | 从多个战果中自动提炼新招式（对应 EvoMap 的 skillDistiller） |
| 跨项目招式共享 | 在不同项目文件夹之间共享招式库 |
| 招式版本管理 | 用 git 追踪招式的演变历史 |
| 进化仪表盘 | 可视化展示进化历史和招式使用统计 |

---

## 五、实施路径

### 阶段一：搭骨架（第 1 天）

```
Step 1: 创建目录结构
  → 6-System/evolution/
  → 6-System/evolution/genes/
  → 6-System/evolution/capsules/

Step 2: 创建模板文件
  → genes/_template.md
  → capsules/_template.md

Step 3: 创建进化子系统的 L2
  → 6-System/evolution/CLAUDE.md

Step 4: 更新 L1 CLAUDE.md
  → 加入 <EVOLUTION> 段落

Step 5: 创建 events.jsonl 空文件
  → 6-System/evolution/events.jsonl

Step 6: 更新 6-System/CLAUDE.md
  → 在目录结构中加入 evolution/ 说明
```

### 阶段二：冷启动（第 1-3 天）

```
Step 7: 从你现有的工作经验中，手动沉淀 3-5 个招式
  建议的起手招式：
  - 口播稿写作（你已经有多次成功经验）
  - 项目调研（比如这次 EvoMap 的调研就是一个招式）
  - 内容归档入库（你的第二大脑日常操作）
  - Daily 复盘（如果你有固定方法的话）
  - 方案设计（先出方案后执行的工作模式）

Step 8: 为每个招式补充 1-2 个历史战果
  回忆之前做得好的场景，写成战果文件
```

### 阶段三：跑通闭环（第 3-7 天）

```
Step 9: 增强 startup.py
  → 扫描 genes/ 输出招式概览

Step 10: 增强 stop_audit.py  
  → 进化事件追踪

Step 11: 实际使用 2-3 天
  → 自然积累新的招式和战果
  → 验证匹配和沉淀流程是否顺畅

Step 12: 根据使用反馈微调
  → 调整 CLAUDE.md 中的进化规则
  → 优化招式模板格式
```

---

## 六、与 EvoMap 的对应关系清单

| EvoMap 功能 | 迁移方式 | 优先级 |
|:---|:---|:---|
| Gene 基因 | → 招式 (Markdown 文件) | P0 ✅ |
| Capsule 基因胶囊 | → 战果 (Markdown 文件) | P0 ✅ |
| EvolutionEvent 进化事件 | → events.jsonl (append-only) | P0 ✅ |
| Signal 信号提取 | → Claude 语义理解 + triggers 关键词 | P0 ✅ |
| Selector 选择器 | → CLAUDE.md 规则 + Claude 匹配 | P0 ✅ |
| Solidify 固化 | → 用户审批 + 写入文件 | P0 ✅ |
| Mutation 突变声明 | → events.jsonl 中的 intent 字段 | P0 ✅ |
| Strategy 进化策略 | → 不需要（你手动控制方向） | 不迁移 |
| PersonalityState | → TELOS.md + AI_RULES.md（已有） | 不迁移 |
| MemoryGraph 因果图谱 | → 简化为招式的 success/fail 统计 | P1 简化版 |
| CircuitBreaker 断路器 | → 招式 status: needs_review 标记 | P1 |
| Auto-update 自动更新 | → 不需要 | 不迁移 |
| A2A Protocol | → 不需要（单人使用） | 不迁移 |
| SkillDistiller 蒸馏 | → 远期愿景 | P3 |
| Hub Search 全球搜索 | → 不需要 | 不迁移 |
| Blast Radius 爆炸半径 | → 不需要（Claude 不自动执行） | 不迁移 |
| Canary Check 金丝雀 | → 不需要 | 不迁移 |
| Load Awareness 负载感知 | → 不需要 | 不迁移 |

**迁移率**：EvoMap 的 18 个核心功能中，迁移了 7 个核心 + 2 个简化版 + 2 个远期。剩余 7 个因平台差异无需迁移。

---

## 七、关键设计决策说明

### 为什么用 Markdown 而不是 JSON？

EvoMap 用 JSON 存储 Gene 和 Capsule（因为它是程序读的）。你的系统用 Markdown（因为你要能看懂）：
- ✅ 你能直接在 Obsidian 里浏览和编辑
- ✅ Claude 能直接理解 Markdown 内容
- ✅ 头部 YAML frontmatter 提供了足够的结构化信息
- ✅ 与你现有的分形文档体系一致

### 为什么匹配用 Claude 而不是写代码？

EvoMap 用正则表达式做信号匹配（因为它是 Node.js 程序）。你用 Claude 的语义理解：
- ✅ 不需要写代码
- ✅ 能理解同义词（"写文案" ≈ "写口播稿" ≈ "写脚本"）
- ✅ 能理解上下文（"帮我改一下之前那个" → 根据 CONTEXT.md 匹配）
- ⚠️ 代价：每次需要扫描 genes/ 目录。但文件少时（< 50 个招式）影响可忽略

### 为什么审批制而不是全自动？

EvoMap 是全自动的（因为它要无人值守运行）。你的系统是"半自动"：
- 统计更新（success_count, last_used）→ A类自动
- 新建招式/战果 → B类需审批
- 这和你现有的变更协议完全一致，不增加认知负担

---

## 八、风险和注意事项

| 风险 | 应对 |
|:---|:---|
| 招式太多导致匹配慢 | 前期不用担心（< 50 个招式完全没问题）；后期可以加索引 |
| 招式写得太泛，不实用 | 每个招式必须有具体的"策略步骤"和至少 1 个"战果"证明有效 |
| 过度沉淀，什么都想记 | 只沉淀**被复用过或可预见会复用**的方法，一次性的不记 |
| 招式过时但没人清理 | P2 中的健康检查会解决这个问题 |
| startup.py 变慢 | 招式概览只列名称和 triggers，不加载全文 |

---

> **下一步**：你审阅这份方案，告诉我哪些要调整，然后我开始按阶段一执行。
