# 6-System/memory/
> L2 | 父级: /.claude/CLAUDE.md

## 职责

会话级与跨会话记忆管理。

## 成员清单

- `MEMORY.md`: **已确认的**操作性规则和稳定偏好（在 contextFiles 里，自动注入）
- `candidates.md`: AI 观察到的新偏好暂存池（**不在 contextFiles**，不自动注入，/digest 时晋升）
- `daily/YYYYMM/YYYYMMDD.md`: 近期会话轨迹（当天进展、用户输入摘要）

## 写入路径

```
AI 观察到新偏好
  → candidates.md（暂存，不注入）
  → /digest 用户确认
    → 晋升到 5-Identity/PROFILE.md（场景化偏好）
    → 或晋升到 MEMORY.md（操作性规则）
    → 或升B类写 pending_approvals.md（冲突/Identity相关）
```

## 治理规则

- **MEMORY.md 只存已确认内容**：操作性规则、经过 /digest 确认的稳定偏好
- **candidates.md 是暂存区**：AI 自动写入，用户不需要操作，/digest 时清理
- 时效信息写 `daily/`

## 读取策略

- 启动时 MEMORY.md 自动注入（contextFiles）
- candidates.md 仅在 /digest 时读取
- daily 按需读取最近 3 天

[PROTOCOL]: 变更时更新此头部，然后检查 /.claude/CLAUDE.md
