# 变更日志

> 记录所有已执行的系统变更

## 日志格式

```
## [时间戳] 变更 #<id>
- 类型：A|B|C
- 操作：<具体操作>
- 影响：<影响的文件>
- 回滚：<回滚命令或状态>
- 执行方式：自动 / 审批后执行
```

---

## 变更记录

### [2025-02-12] 提案 #001 - 新增 AI 行为准则

- 类型：B（Identity 变更）
- 操作：
  - 创建 `5-Identity/AI_RULES.md`
  - 更新 `5-Identity/CLAUDE.md` 成员清单
  - 更新 `.claude/settings.json` contextFiles
  - 清理多余文件（.claude/AGENTS.md、.codex/CLAUDE.md）
- 影响：5-Identity/、.claude/
- 回滚：删除 AI_RULES.md，从 contextFiles 移除
- 执行方式：审批后执行
- 来源：对话中识别用户品味偏好

---

### 系统初始化

**[系统创建]** 初始化
- 类型：C
- 操作：创建完整目录结构和核心文件
- 影响：全部目录
- 回滚：N/A（初始状态）
- 执行方式：手动初始化

---

[PROTOCOL]: 此文件由系统自动维护

### [2026-02-14 14:04:50] AutoCycle #20260214-140450
- 类型：A（自动治理）
- 操作：检测 Inbox=15, bootstrap_l2: created_l2=0, 构建 pointers, PARA 概览: para_overview_built=1;output=6-System/indexes/para_overview.json;total_markdown=211, 执行 fractal_audit, 记忆整理: memory_updated=1;recent_count=4;telos_candidates=0;proposal_created=0, 提案输出: proposal_created=0, 健康指标: health_generated=1;severity=ok;reject_rate=0.0;no_evidence_rate=0.857;learning_effective_rate=1.0, 调优提案: proposal_created=0;reason=health_ok
- 执行方式：自动
- 来源：6-System/scripts/run_cycle.sh

### [2026-02-14 16:15:01] AutoCycle #20260214-161501
- 类型：A（自动治理）
- 操作：检测 Inbox=15, bootstrap_l2: created_l2=0, 构建 pointers, PARA 概览: para_overview_built=1;output=6-System/indexes/para_overview.json;total_markdown=211, 枚举注册: enum_registry_built=1;output=6-System/indexes/enum_registry.json, 执行 fractal_audit, 记忆整理: memory_updated=1;recent_count=8;telos_candidates=0;proposal_created=0, 提案输出: proposal_created=0, 健康指标: health_generated=1;severity=warn;reject_rate=0.0;no_evidence_rate=0.0;learning_effective_rate=0.5;stale_review_rate=1.0, 调优提案: proposal_created=1;proposal_id=004
- 执行方式：自动
- 来源：6-System/scripts/run_cycle.sh

### [2026-02-15] 提案 #006 - 结构标签表扩展 + 标签自维护系统

- 类型：B（分类体系新增）
- 操作：
  - 结构标签表 6→9：新增体系、设定、作品
  - 废弃映射写入 tag_vocabulary.md
  - 3-Resources/CLAUDE.md type 列表改为引用 Source of Truth
  - intake/SKILL.md 改为受控增长规则
  - L1 CLAUDE.md 追加标签卫生规则
  - build_pointers.py 新增 _tag_health_report() 生成 tag_health.json
  - startup.py 新增标签健康摘要 + 维护间隔提醒
  - 新建 maintain-tags skill
- 影响：tag_vocabulary.md, 3-Resources/CLAUDE.md, .claude/CLAUDE.md, intake/SKILL.md, build_pointers.py, startup.py
- 回滚：revert 上述文件，删除 maintain-tags skill 和 tag_health.json
- 执行方式：审批后执行
- 来源：对话中标签系统审计

### [2026-02-14 16:15:33] AutoCycle #20260214-161533
- 类型：A（自动治理）
- 操作：检测 Inbox=15, bootstrap_l2: created_l2=0, 构建 pointers, PARA 概览: para_overview_built=1;output=6-System/indexes/para_overview.json;total_markdown=211, 枚举注册: enum_registry_built=1;output=6-System/indexes/enum_registry.json, 执行 fractal_audit, 记忆整理: memory_updated=1;recent_count=8;telos_candidates=0;proposal_created=0, 提案输出: proposal_created=0, 健康指标: health_generated=1;severity=warn;reject_rate=0.0;no_evidence_rate=0.0;learning_effective_rate=0.533;stale_review_rate=1.0, 调优提案: proposal_created=1;proposal_id=005
- 执行方式：自动
- 来源：6-System/scripts/run_cycle.sh
