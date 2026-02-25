---
status: active
domain: Identity
para: identity
parent: 5-Identity
type: context
tags: [奥一, 系统规则]
update_level: A
summary: 此文件由 AI 在对话中发现上下文变化时自动更新（A类变更）。
reviewed_at: 2026-02-14
---
# 当前上下文

> 此文件由 AI 在对话中发现上下文变化时自动更新（A类变更）。
> 最后更新：2026-02-14

## 活跃项目
- MyWear：AI穿搭管家，已完成MVP开发，申请Antler加速器中（2026年2月）
- 外挂大脑系统：完成记忆系统改造（阶段零～阶段四+L1全部就位，2026-02-25）
  - 新建：PROFILE.md（场景化偏好）, candidates.md（暂存池）, patterns/（任务智能）, session_export.py（全量对话记录）
  - 核心机制：新偏好 → candidates.md 暂存 → /digest 确认 → 晋升 PROFILE.md

## 近期关注
- Claude Code 深度使用技巧
- 写作系统持续运转中

## 近期决策
- 选择 PARA 而非 Zettelkasten 作为知识框架
- 标签是检索入口，不是分类体系
- 系统以 Claude Code 为驱动器，Obsidian 为存储层
- 记忆系统用 CC 原生 MEMORY.md + CONTEXT.md + session_logs 三层
- PROFILE.md 场景化偏好：新偏好先存 candidates.md，/digest 确认后晋升（A类）
- 全量对话记录用 session_export.py hook 自动保存为 MD（含 AI 回复+时间戳）
- 指针注入方案明确放弃，不实施（复杂度收益不足）
- AI 应把奥一定位为共同建造者（正在通过 #011 审批）

## 工作模式偏好
- 基础设施配置优先永久方案
- 简单优先，不过度设计
- 先出方案后执行，不直接改动

---

[PROTOCOL]: 变更时更新此文档；A类变更可自动写入，涉及 Identity 原则冲突时需提案审批。
