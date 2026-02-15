---
name: writing
description: 执行写作任务路由与内容生成。用于“写文章/改文案/标题/开头”等写作请求；不用于系统治理或审批任务。输出写作结果与保存路径。
---

# Writing 写作入口

写作助手，帮助你用奥一的风格和方式写作。

## 触发方式

- 显式：`/writing [原料或任务描述]`
- 自然语言："帮我写篇文章"、"改个标题"、"优化下开头"、"用奥一的风格写..."

## 何时不使用

- 你要做系统治理、规则审批、知识归档（应走 `propose-change` / `intake`）

## 规则文件位置

```
2-Areas/WritingSystem/
├── CORE.md                    # 主体提示词
└── WriteRule/
    ├── 标题写作指南.md
    ├── 爆款开头写作指南.md
    ├── 认知升维写作指南.md
    ├── takeaways写作指南.md
    ├── 文章结构.md
    ├── 事实核查与信息增强指南.md
    ├── 人味提示词.md
    └── 高互动写作.md
```

## 工作流

1. **判断任务类型**
   - 完整写作 → 读取 CORE.md
   - 只写标题 → 读取 标题写作指南.md
   - 只改开头 → 读取 爆款开头写作指南.md
   - 认知升维 → 读取 认知升维写作指南.md
   - 改写人味 → 读取 人味提示词.md

2. **加载规则**
   - 用 Read 工具读取对应规则文件
   - 按规则执行写作任务

3. **检索增强**（可选，用于完整写作时）
   - 写作主题涉及项目/领域知识 → 调用 retrieve 检索相关笔记
   - 检索路径：`6-System/indexes/knowledge_pointers.jsonl`

4. **输出保存**
   - 结果保存到 `2-Areas/WritingSystem/Output/`
   - 格式：`{标题}-{时间戳}.md`

## 任务类型速查

| 任务 | 读取文件 |
|------|----------|
| 完整文章 | CORE.md |
| 标题 | WriteRule/标题写作指南.md |
| 开头 | WriteRule/爆款开头写作指南.md |
| 认知升维 | WriteRule/认知升维写作指南.md |
| Takeaways | WriteRule/takeaways写作指南.md |
| 文章结构 | WriteRule/文章结构.md |
| 人味改写 | WriteRule/人味提示词.md |
