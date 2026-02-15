---
name: maintain
description: 知识库整体维护。"维护/体检/健康检查/清理标签/修复结构/知识库维护"时触发。
user-invocable: true
argument-hint: "[留空全面诊断，或指定：tags/structure/smells/indexes/full]"
---

# Maintain 知识库维护

对知识库执行健康检查与修复。覆盖标签、结构、知识坏味道、索引四个维度。

## 触发

- `/maintain` — 全面诊断报告（不自动修复，展示后让用户选择）
- `/maintain tags` — 标签深度维护（冷门合并/描述填充/type迁移/近义去重）
- `/maintain structure` — L2/L3 分形文档修复
- `/maintain smells` — 知识坏味道巡检
- `/maintain indexes` — 索引重建
- `/maintain full` — 完整治理循环（indexes → 诊断 → 引导修复 → 再 indexes）
- 自然语言："维护"、"体检"、"健康检查"、"清理标签"、"修复结构"、"知识库维护"

## 前置条件

1. 读取 `6-System/indexes/kb_health.json`
2. 如果不存在或 generated_at 超过 7 天，先运行：
   ```bash
   python3 6-System/scripts/build_pointers.py
   ```
3. 读取 `6-System/state/maintenance.json` 了解上次维护时间

---

## `/maintain`（无参数）— 全面诊断

读 `kb_health.json`，分四维度展示报告：

```
知识库健康报告 ({日期})
================================
总览: {critical} 严重 / {warning} 警告 / {info} 信息

[标签] 总标签 {N}
  冷门: {N} 个标签仅关联 1 篇
  缺描述: {N} 个标签无含义说明
  模板描述: {N} 个标签使用占位符描述
  非标type: {N} 个文件使用未定义 type
  近义疑似: {N} 组标签可能重复

[结构]
  L2 缺失: {N} 个目录有内容无 CLAUDE.md
  L2 过时: {N} 个目录成员清单与实际不符
  L3 问题: {N} 个文件元数据异常

[知识味道]
  僵化文件: {N} 篇 (active 超过 180 天未更新)
  孤岛候选: {N} 篇 (无标签且无链接)
  断裂引用: {N} 处 ([[]] 指向不存在文件)
  Inbox 堆积: {N} 篇
  空目录: {N} 处

[索引]
  指针: {N} 天前 | 概览: {N} 天前
  {过期提示}

处理哪个维度？(tags / structure / smells / indexes / full)
```

用户选择后进入对应子命令。

---

## `/maintain tags` — 标签深度维护

读 `kb_health.json` 的 `tags` 部分，执行四阶段：

### Phase 1: 诊断展示

```
标签健康报告 ({日期})
=========================
总标签数: {total}

[冷门标签] {N} 个标签仅关联 1 篇文件
  {tag1}(1篇) | {tag2}(1篇) | ...

[空描述] {N} 个标签无含义说明
  {tag1} | {tag2} | ...

[模板描述] {N} 个标签使用占位符描述
  {tag1} | {tag2} | ...

[非标准type] {N} 个文件使用未定义的 type 值
  {type1}({M}篇) → 建议: {映射}

[近义疑似] {N} 组标签可能重复
  "{tag1}" vs "{tag2}" | ...

需要处理哪些？(输入编号，或 all)
```

如果有参数（如 `/maintain tags cold`），直接跳到对应分组。

### Phase 2: 逐组处理

#### 冷门标签（cold）
1. 遍历冷门标签，对每个标签：
   - 读关联文件，理解标签的实际语义
   - 查找 tag_vocabulary.md 中是否有更通用的已有标签可替代
2. 三种处置建议：
   - **保留**：有独立语义价值（如项目名 MyWear、ForReel）
   - **合并**：改关联文件的 tags 字段为更通用的标签（如 "易拉宝"→"营销"）
   - **待观察**：语义不确定，标记但不动
3. 展示处置方案，用户确认后执行：
   - 修改关联文件的 frontmatter tags
   - build_pointers.py 下次运行会自动清理 tag_vocabulary.md 中计数为 0 的标签

#### 空描述/模板描述（desc）
1. 对每个缺描述标签，读 tag_vocabulary.md 中的涉及领域 + 关联文件内容
2. 基于理解生成简洁描述（15-30字，说明标签的独特语义）
3. 直接写入 tag_vocabulary.md 对应行（A 类自动执行）
4. 模板描述同样替换为有辨识度的描述

#### 非标准 type（type）
1. 读取 tag_vocabulary.md 结构标签表的废弃映射
2. 按映射关系迁移文件的 frontmatter type：
   - 沉淀 → 笔记
   - 临时草稿 → 笔记（同时设 status: draft）
   - 草稿 → 笔记（同时设 status: draft）
   - 系统提示词 → 提示词
   - 文案 → 作品
   - 成品 → 作品
   - 文档 → 作品
3. 无映射的野生 type → 展示给用户决定
4. 确需新增结构标签 → 更新 tag_vocabulary.md 结构标签表（A 类）

#### 近义标签（similar）
1. 展示疑似对，每对附上描述和关联文件数
2. 让用户判断：合并（选保留哪个）/ 保留两个
3. 合并时：修改所有关联文件的 tags + 更新 tag_vocabulary.md

### Phase 3: 回环检查

1. 运行 `python3 6-System/scripts/build_pointers.py` 重建索引
2. 确认 kb_health.json 已更新
3. 输出变更摘要

### Phase 4: 记录维护时间

更新 `6-System/state/maintenance.json` 的 `modules.tags`：

```json
{
  "last_run": "2026-02-15T12:00:00Z",
  "actions": ["cold:12merged", "desc:8filled", "type:4migrated"]
}
```

同时更新顶层 `last_run`。

---

## `/maintain structure` — L2/L3 修复

读 `kb_health.json` 的 `structure` 部分。

### 工作流

1. 展示三类问题：
   - **L2 缺失**：目录有内容但无 CLAUDE.md
   - **L2 过时**：成员清单与实际文件不一致（extra_files / ghost_files）
   - **L3 问题**：frontmatter 缺失必填字段或 para 值与实际路径不匹配

2. L2 缺失处理：
   - 列出目录下所有文件
   - AI 推断目录职责，生成 L2（含成员清单）
   - 用户确认后写入

3. L2 过时处理：
   - 展示差异（哪些文件不在清单里、清单里哪些文件不存在）
   - 读取新增文件理解内容 → 补充成员条目
   - 删除幽灵条目
   - 更新 L2

4. L3 问题处理：
   - `missing_para` / `missing_type` / `missing_status` → 读文件推断 → 补全
   - `para_mismatch` → 根据实际路径修正 para 值

5. 回环重建 + 记录到 `maintenance.json.modules.structure`

---

## `/maintain smells` — 知识坏味道巡检

读 `kb_health.json` 的 `smells` 部分。

### 工作流

1. 展示代码初筛结果：
   - **僵化文件**：status=active 但 >180 天未更新
   - **孤岛候选**：无 tags 且正文无 `[[]]` 链接
   - **断裂引用**：`[[]]` 指向不存在的文件
   - **Inbox 堆积**：0-Inbox 中文件数
   - **空目录**：有 L2 但无成员文件

2. AI 逐项判断处置：
   - 僵化 → 读文件 → 建议归档（改 status: stale, 移至 4-Archives）或建议更新
   - 孤岛 → 读文件 → 建议补标签/链接
   - 断裂 → 建议删除引用或建议创建被引文件
   - Inbox → 提示使用 `/intake` 处理
   - 空目录 → 建议删除或说明用途

3. 用户确认后执行修复

4. 回环 + 记录到 `maintenance.json.modules.smells`

---

## `/maintain indexes` — 索引重建

运行索引构建脚本：

```bash
python3 6-System/scripts/build_pointers.py
python3 6-System/scripts/build_para_overview.py
```

输出构建结果，记录到 `maintenance.json.modules.indexes`。

---

## `/maintain full` — 完整治理循环

按优先级执行全部维度：

1. 先运行 `/maintain indexes`（确保数据新鲜）
2. 展示全面诊断报告
3. 按严重性引导修复：
   - critical → `/maintain structure`（L2 缺失优先）
   - warning → `/maintain structure`（L3 问题）+ `/maintain smells`（僵化文件）
   - info → `/maintain tags`
4. 最后再跑一次 `/maintain indexes` 确认干净

---

## 变更分级

| 操作 | 级别 | 说明 |
|------|------|------|
| 补充标签描述 | A 类 | 直接写入 tag_vocabulary.md |
| type 迁移（按废弃映射） | A 类 | 修改 frontmatter |
| 冷门标签合并 | A 类 | 先展示方案，用户确认后执行 |
| 近义标签合并 | A 类 | 先展示方案，用户确认后执行 |
| 新增结构标签 | A 类 | 直接加到 tag_vocabulary.md |
| L2 创建/更新 | A 类 | 用户确认后写入 |
| L3 修复 | A 类 | frontmatter 字段补全/修正 |
| 知识味道处置 | A 类 | 用户确认后执行 |
| 删除结构标签 | B 类 | 需审批 |
| 索引重建 | A 类 | 直接执行 |

## 边界

- 不自动删除任何文件或标签，只提建议（用户确认后才动）
- 不修改文件正文内容，只改 frontmatter
- 冷门标签中的项目名（如 MyWear、ForReel）默认建议保留
- 处理过程中发现的 L2 成员清单不一致，顺手修复
