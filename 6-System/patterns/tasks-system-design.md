---
title: 任务系统设计方案
type: pattern
area: system
status: active
created: 2026-02-26
tags: [tasks, workflow, system-design]
summary: 任务捕获、追踪、归档的完整系统设计。含文件清单、变更内容、用户路径走查。实施前的设计规范文档。
---

# 任务系统设计方案

## 设计目标

新开任何一个对话窗口，问一句"我还有什么没做"，cc 能立即回答。
任务从捕获到完成到归档，全程不需要用户记任何额外的事情。

---

## 涉及文件清单

### 新建文件

| 文件路径 | 职责 |
|---------|------|
| `6-System/working-memory/tasks.md` | 统一任务捕获池，唯一的 todo 入口 |
| `6-System/working-memory/done/YYYY-MM.md` | 归档后的已完成记录，按月存储（首次触发时自动创建） |
| `6-System/state/alerts.json` | 持久化系统告警（maintain 超期等），首次超期时自动创建 |

### 修改文件

| 文件路径 | 改什么 |
|---------|--------|
| `6-System/hooks/startup.py` | 加 tasks 自动归档逻辑 + alerts.json 写入/读取逻辑 |
| `.claude/CLAUDE.md`（L1） | 加任务捕获规则 + 路由规则 + 会话状态行协议 |
| `6-System/working-memory/CLAUDE.md` | 成员清单加 tasks.md 和 done/ |
| `1-Projects/CLAUDE.md` | 补全 AI学习小组、短剧APP（当前盲区） |

---

## tasks.md 结构

```markdown
---
title: 任务池
type: working-memory
status: active
---

# 任务池

## 焦点（当前最重要的 1-3 件）
- [~] 写作系统规范完善 → `2-Areas/WritingSystem/CORE.md` | 2026-02-20

## 待办
- [ ] 整理 Inbox 积压 | 2026-02-26
- [ ] 联系某人 | 2026-02-25

## 已完成 · 2026-02
- [x] 归档 AI 翻译文章 → `2-Areas/.../20260226-AI擅长翻译.md` | ✓ 2026-02-26
- [x] 批准 TELOS #015 | ✓ 2026-02-26

---

## 归档规范
- **触发条件**：[x] 条目累计 ≥ 15 条
- **执行方式**：startup.py 在每次会话启动时自动检测并执行，无需手动操作
- **目标路径**：`6-System/working-memory/done/YYYY-MM.md`（按完成日期中的月份分组）
- **完成后**：从本文件删除已归档条目，tasks.md 保持精简
```

---

## 各组件说明

### startup.py 新增的两段逻辑

**任务自动归档**
1. 统计 tasks.md 中所有 `- [x]` 条目数量
2. 如果 ≥ 15 条：按条目末尾的完成日期（`| ✓ YYYY-MM-DD`）分组，写入 `done/YYYY-MM.md`
3. 从 tasks.md 删除已归档条目
4. 在启动摘要字符串中追加：`✓ 已自动归档 18 条 → done/2026-02`

**maintain 持久化告警**
1. 检测 maintain 上次运行时间（已有逻辑，从 `state/maintenance.json` 读取）
2. 如超期（> 10 天）：在 `state/alerts.json` 中写入告警标记（文件不存在则创建）
3. 每次启动都读取 alerts.json：有未清除告警 → 追加到启动摘要
4. /maintain 技能执行完成后：调用清除逻辑，删除 alerts.json 中的对应条目

### alerts.json 结构

```json
{
  "maintain_overdue": {
    "since": "2026-02-16",
    "days": 10,
    "message": "maintain 已 10 天未运行"
  }
}
```

### L1（.claude/CLAUDE.md）新增三条规则

**任务捕获规则**
- 用户明确说"帮我记一下 X / 以后做 X" → 直接写入 tasks.md 待办，追加当天日期，不询问
- 对话中 cc 识别到明确任务意图（但用户没有明确要求记录）→ 问一句"需不需要记到任务里？"
- 用户说某任务"完成了 / 做好了 / 发出去了" → cc 在 tasks.md 中标 [x]，追加完成日期

**路由规则**
- 用户问"我今天做什么 / 还有什么没做 / 我可以做点什么" → 读 `tasks.md` 焦点区和待办区，同时读 `1-Projects/CLAUDE.md`，综合回答
- tasks.md **不在** contextFiles，按需读取，不占用常驻上下文

**会话状态行协议**
- 每次新会话，cc 的第一条回复必须以状态行开头：
  `[状态] {startup摘要内容}`
- 如 alerts.json 有未清除告警，状态行包含：`⚠️ maintain 已 X 天未运行`
- 如本次启动触发了自动归档，状态行包含：`✓ 已自动归档 X 条 → done/YYYY-MM`

---

## 用户路径走查

### 场景一：新开窗口问"我今天要做什么"

```
用户打开新对话
  → startup.py 自动运行
    → 检查 tasks.md [x] 数量 → 假设 8 条，未触发归档
    → 检查 alerts.json → 发现 maintain 超期告警
    → 组装启动摘要字符串：
        "[系统启动] 知识库 209 篇 | 8个待审批 | ⚠️ maintain已10天"
    → 字符串写入 system-reminder（cc 可见，用户不直接看到）

  → cc 收到 system-reminder
  → L1 状态行协议触发（每次会话必须执行）
  → cc 第一句话：
      "[状态] 知识库 209 篇 | 8 个待审批 | ⚠️ maintain 已 10 天未运行"

  → 用户问："我今天要做什么？"
  → L1 路由规则触发 → cc 读取 tasks.md
  → cc 回答：
      "焦点（最重要的）：
       - 写作系统规范完善

       待办（接下来可以做）：
       - 整理 Inbox 积压
       - 联系某人

       另有 2 个进行中的项目：AI学习小组 / 短剧APP
       需要深入了解哪个告诉我。"
```

### 场景二：对话中发现新任务（cc 识别到意图）

```
对话中，用户顺带说："对了，我还要去联系一下投资人"

  → L1 捕获规则触发（识别到任务意图）
  → cc 问："需要记到任务里吗？"
  → 用户："要"
  → cc 写入 tasks.md 待办：
      "- [ ] 联系投资人 | 2026-02-26"
  → cc 确认："已记录到任务池。"
```

### 场景三：用户直接要求记录

```
用户："帮我记一下，下周要做季度复盘"

  → L1 捕获规则触发（明确指令，直接执行，不询问）
  → cc 写入 tasks.md 待办：
      "- [ ] 季度复盘 | 2026-02-26"
  → cc 确认："已记录。"
```

### 场景四：任务完成

```
用户："AI 翻译那篇文章发出去了"

  → L1 捕获规则触发（识别完成信号）
  → cc 在 tasks.md 中找到对应条目，修改为：
      "- [x] 写作系统规范完善 → ... | ✓ 2026-02-26"
  → cc 确认："已标记完成。"
  → （下次 startup 时，如果 [x] 累计 ≥ 15 条，自动归档）
```

### 场景五：自动归档触发

```
startup.py 运行
  → 统计 tasks.md [x] 条目 → 发现 17 条，触发归档
  → 按完成月份分组：
      2026-01: 5 条
      2026-02: 12 条
  → 写入 done/2026-01.md（新建文件，写入5条）
  → 写入 done/2026-02.md（新建文件，写入12条）
  → 从 tasks.md 删除这 17 条
  → 启动摘要追加：
      "✓ 已自动归档 17 条 → done/2026-01, done/2026-02"

  → cc 状态行报告：
      "[状态] ... | ✓ 已自动归档 17 条"
```

### 场景六：复盘"这周/这个月做了什么"

```
用户："我这个月做了哪些事情？"

  → L1 路由规则触发（问完成情况）
  → cc 先读 tasks.md 的 "已完成 · 2026-02" 区块
  → 如该月已归档，读取 done/2026-02.md
  → 整理输出：
      "2026年2月完成的事项：
       - 归档 AI 翻译文章（2/26）→ 2-Areas/WritingSystem/...
       - 批准 TELOS #015（2/26）
       ..."
```

### 场景七：maintain 告警的完整生命周期

```
第1天：startup.py 检测到 maintain 超过 10 天未运行
  → 写入 state/alerts.json：{"maintain_overdue": {"days": 10, ...}}
  → 启动摘要包含告警

第2-N天：每次 startup
  → 读 alerts.json → 告警仍在 → 启动摘要继续包含告警
  → cc 状态行每次都显示 "⚠️ maintain 已 X 天未运行"
  → 告警不会消失，直到用户处理

某天：用户运行 /maintain
  → maintain 技能执行完成
  → 清除 alerts.json 中 maintain_overdue 条目

下次启动：alerts.json 无告警 → 启动摘要不再包含该提示
```

---

## 实施顺序

1. 新建 `6-System/working-memory/tasks.md`（含结构 + 归档规范）
2. 修改 `6-System/hooks/startup.py`：加自动归档 + alerts.json 两段逻辑
3. 修改 `.claude/CLAUDE.md`（L1）：加捕获规则 + 路由规则 + 状态行协议
4. 修改 `6-System/working-memory/CLAUDE.md`：更新成员清单
5. 修改 `1-Projects/CLAUDE.md`：补全 AI学习小组、短剧APP
6. `done/` 目录和 `alerts.json` 在首次触发时由脚本自动创建，无需手动建

---

[PROTOCOL]: 本文件是任务系统的设计规范与运行文档。实施于 2026-02-26。
