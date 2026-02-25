# 6-System/
> L2 | 父级: /CLAUDE.md

## 职责

系统运行支持 - 审批、日志、记忆、索引。

**你日常优先关注 `pending_approvals.md` 和 `change_log.md`（异常排查再看 `logs/stop_pipeline.jsonl`）**

## 核心文件

- `pending_approvals.md`: 审批入口（你的主要工作台）
- `change_log.md`: 变更日志
- `state/runtime_state.json`: 运行时状态（startup.py 初始化）
- `logs/stop_pipeline.jsonl`: Stop 审计日志

## 目录结构

```
6-System/
├── pending_approvals.md      # 审批队列
├── change_log.md             # 变更日志
├── memory/                   # 跨会话记忆
│   ├── MEMORY.md             # 已确认的操作性规则和稳定偏好（contextFiles 自动注入）
│   ├── candidates.md         # 新偏好暂存池（不注入，/digest 时晋升到 PROFILE.md）
│   └── daily/                # 日常碎片（Stop hook 自动写入）
├── patterns/                 # 任务智能：成功的执行模式，可复用交互策略（好用轨道）
├── indexes/                  # 检索索引
│   ├── knowledge_pointers.jsonl  # 知识指针（/maintain indexes 重建）
│   └── para_overview.json        # PARA 全局概览（/maintain indexes 重建）
├── scripts/                  # 脚本（/maintain skill 调用）
│   ├── build_pointers.py     # 知识指针构建
│   ├── build_para_overview.py # PARA 概览构建
│   ├── memory_consolidate.py # 记忆整理（压缩、遗忘）
│   └── approve_change.sh     # 提案状态机
├── hooks/                    # Hook 脚本（settings.json 注册）
│   ├── startup.py            # SessionStart: 状态初始化 + 启动摘要
│   ├── stop_audit.py         # Stop: 日常记忆碎片 + 审计日志
│   └── session_export.py     # Stop: 完整对话 MD 导出到 session_logs/
├── state/                    # 运行状态
│   ├── runtime_state.json
│   └── maintenance.json         # 维护状态（/maintain skill 更新）
├── logs/                     # 审计日志
│   └── stop_pipeline.jsonl
├── session_logs/             # 完整对话 MD（session_export.py 自动写入）
├── candidates/               # 候选条目
│   ├── identity/             # Identity 候选（必须审批）
│   └── resources/            # Resources 候选
├── synthesis/                # 综合报告
└── feedback/                 # 反馈信号
```

## 问题排查

- 提案未出现 → 检查 `candidates/` → `pending_approvals.md`
- 变更未执行 → 检查 `pending_approvals.md` → `change_log.md`
- 记忆未写入 → 检查 `logs/stop_pipeline.jsonl` 和 `memory/daily/` 目录

---

[PROTOCOL]: 变更时更新此头部，然后检查 /CLAUDE.md
