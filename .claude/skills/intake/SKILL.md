---
name: intake
description: 将 Inbox 内容归档到知识库。"归档/入库/整理 inbox"时触发。
user-invocable: true
argument-hint: "[文件名，留空则扫描整个 Inbox]"
---

# Intake 归档入库

将 0-Inbox/ 中的原始内容归纳内化到 PARA 系统。

## 触发

- `/intake` 或 `/intake 文件名`
- 自然语言："帮我整理 inbox"、"归档一下"、"这篇文章放哪"

## 工作流

1. **扫描** 0-Inbox/（或用户指定文件），列出待归档内容
2. **分析** 每篇内容：
   - 读内容，理解本质
   - 判断 PARA 归属（Project / Area / Resource / Archive）
   - 读目标目录的 L2（CLAUDE.md）了解现有分类和成员
   - 读目标目录下已有文件的 frontmatter，学习该目录的 domain/type/tags 惯例
3. **展示归档方案**，让用户确认：
   - 目标路径
   - 建议文件名（简洁中文关键词.md）
   - 完整 frontmatter
   - 建议标签（从 `6-System/indexes/tag_vocabulary.md` 选取，优先复用已有标签）
4. **执行**（用户确认后）：
   - 格式化文档：写入 frontmatter、规范标题格式
   - 写入目标位置
   - 更新目标目录的 L2 成员清单
   - 删除 Inbox 中的原文件

## Frontmatter 模板

```yaml
---
status: active
domain: [读目标目录 L2 和同目录文件确定]
para: resource | area | project
parent: [父目录路径，如 3-Resources/创作]
type: [从 tag_vocabulary.md 结构标签表选取；确需新增时先添加到 tag_vocabulary.md]
layer: [仅 resource 必填：现象/本质/哲学]
tags: [从 tag_vocabulary.md 选取，1-3个]
summary: [一句话摘要]
created: YYYY-MM-DD
updated: YYYY-MM-DD
reviewed_at: YYYY-MM-DD
---
```

## 标签规则

- 归档前读取 `6-System/indexes/tag_vocabulary.md`
- 优先从已有主题标签中选取
- 确实没有合适的 → 新增标签，同时更新词汇表（添加含义和涉及领域）
- 不要发明与已有标签含义重叠的新标签
- 确需新增结构标签（type）时，同步更新 tag_vocabulary.md 结构标签表，写清含义

## layer 判断

| layer | 特征 | 举例 |
|-------|------|------|
| 现象 | 原始信息、笔记、数据、案例 | 课程笔记、会议记录、案例拆解 |
| 本质 | 提炼的模式、方法、框架 | 方法论、决策模型、写作指南 |
| 哲学 | 普适原则、价值观、信念 | 第一性原理、复利思维 |

## 归档后

- 确认 L2 成员清单已更新
- 确认 Inbox 原文件已移除
- 如涉及新的分类体系（新子目录），属 B 类变更，需写审批提案

## 关键要点

1. **不改动原始内容**：只提取关键信息写入 frontmatter，原文保留不动
2. **重复检测**：归档前检查是否有内容相似的文件已存在，如有则在 frontmatter 标注"重复文件"
3. **文件名规范**：使用简洁中文关键词，如 "AI时尚造型-情境解码器.md"
4. **para 转换**：Inbox 文件的 para:inbox → 实际 para 值（resource/project/area）
5. **domain 转换**：Inbox 文件的 domain:收集 → 实际 domain 值
6. **删除操作**：确认移动完成后删除 Inbox 原文件
