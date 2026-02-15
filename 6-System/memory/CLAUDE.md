# 6-System/memory/
> L2 | 父级: /.claude/CLAUDE.md

## 职责

会话级与跨会话记忆管理。

- `MEMORY.md`: 长期稳定记忆（偏好、事实、长期约束）
- `daily/YYYYMM/YYYYMMDD.md`: 近期记忆（当天进展、上下文线索）

## 治理规则

- 稳定信息写 `MEMORY.md`
- 时效信息写 `daily/`
- 涉及 Identity 的候选写入审批队列，不直接写入 Identity

## 读取策略

- 启动时默认注入 MEMORY 摘要
- 近期对话按需读取最近 3 天 daily

[PROTOCOL]: 变更时更新此头部，然后检查 /.claude/CLAUDE.md
