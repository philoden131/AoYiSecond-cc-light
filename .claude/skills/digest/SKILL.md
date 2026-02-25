---
name: digest
description: 总结当前对话并归入系统。"总结对话/归入系统/收纳一下/内化"时触发。
user-invocable: true
argument-hint: "[留空则全量总结，或指定关注点如'只记项目信息']"
---

# Digest 对话收纳

将当前对话中的有价值信息提取并归入系统的持久化层。

## 触发

- `/digest` 或 `/digest 只记项目信息`
- 自然语言："总结一下这次对话"、"归入系统"、"收纳一下"、"记住我们聊的"

## 工作流

### Step 1：扫描当前对话，提取五类信息

| 类型 | 识别信号 | 目标位置 |
|------|----------|----------|
| 项目上下文 | 新项目、阶段变化、产品定义、目标人群、关键决策 | `5-Identity/CONTEXT.md` |
| 新观察到的偏好（未确认） | 本次对话首次出现的工作习惯、交互偏好、品味倾向 | `6-System/memory/candidates.md`（暂存） |
| 已确认的稳定偏好 | 通过本次 /digest 用户明确确认的候选条目 | `5-Identity/PROFILE.md` 或 `6-System/memory/MEMORY.md` |
| 可复用知识/模式 | 方法论、框架、模板、成功的任务执行模式 | PARA 对应位置 或 `6-System/patterns/` |
| Identity 相关 | 使命/目标/信念/策略变化 | `6-System/pending_approvals.md`（B类审批） |

### Step 2：读取 candidates.md，处理待确认候选

读取 `6-System/memory/candidates.md`，展示所有待确认候选条目：

```
发现 candidates.md 中有 N 条待确认偏好：
- [2026-02-25] 观察：偏好用类比理解复杂概念 | 来源：记忆系统设计讨论
  → 确认晋升到 PROFILE.md？[是/否/场景化]
```

用户确认后：
- 确认 → 写入 `5-Identity/PROFILE.md`（或 `MEMORY.md` 如果是操作性规则），从 candidates.md 删除
- 否决 → 从 candidates.md 删除
- 发现冲突 → 尝试场景化合并；场景化失败 → 升 B 类写入 `pending_approvals.md`

### Step 3：展示本次新提取结果

向用户展示：
- 提取到的每条信息
- 分类和目标位置
- 如有 Identity 变更，标注需要审批

格式示例：
```
本次对话提取：

[项目上下文] → CONTEXT.md
- 外挂大脑记忆系统完成阶段一改造（PROFILE.md / candidates.md / patterns/ 新建）

[新偏好候选] → candidates.md（暂存，下次 /digest 确认）
- 从产品/体验角度理解技术决策的倾向

[可复用模式] → 6-System/patterns/
- 系统架构设计方法：先诊断问题 → 决策文档 → 分阶段执行

确认写入？
```

### Step 4：用户确认后执行

按确认范围写入：

**更新 CONTEXT.md**：
- 活跃项目：更新或新增项目条目
- 近期关注：更新关注点
- 近期决策：追加新决策
- A 类变更，直接写入

**写入 candidates.md**（新观察的偏好）：
- 追加格式：`- [日期] 观察：[内容] | 来源：[对话主题]`
- A 类，直接追加

**晋升到 PROFILE.md**（candidates.md 确认的条目）：
- 写入对应分类下
- A 类，直接写入
- 注意：如与现有条目冲突，先尝试场景化

**写入 patterns/**（可复用任务模式）：
- 文件命名：`[任务类型]-[具体方法].md`
- 按模板格式写入

**创建新笔记**（可复用知识，如有）：
- 按 intake 流程处理：确定 PARA 归属、写 frontmatter、选标签、更新 L2

**Identity 提案**（如有）：
- 写入 `6-System/pending_approvals.md`，包含依据和回滚方案
- 提醒用户审批

### Step 5：报告变更

列出所有实际写入：
```
已完成：
- CONTEXT.md：更新外挂大脑系统改造进度
- candidates.md：新增 1 条偏好候选
- PROFILE.md：从 candidates.md 晋升 2 条确认偏好
- 6-System/patterns/system-架构设计流程.md：新建模式文件
```

## CONTEXT.md 写入规范

项目条目支持子信息展开：

```markdown
## 活跃项目
- MyWear：可穿戴产品，进入营销阶段
  - 定义：AI 驱动的个性化穿搭推荐
  - 受众：北美 25-35 岁健身人群
  - 阶段：产品定义完成 → 营销冷启动
  - 关键决策：先做 TikTok + Instagram，暂不做 Google Ads
```

不是所有项目都需要子信息。一行能说清的就一行。

## 边界

- 不重复已在 CONTEXT.md 中存在的信息（先读再写）
- 不捏造对话中没有的信息
- 不自动执行 Identity 变更
- 新观察到的偏好先写 candidates.md，不直接写 PROFILE.md（要经用户确认）
- 如果对话纯闲聊没有可提取信息，直接说"本次对话无需归档"
