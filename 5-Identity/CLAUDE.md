# 5-Identity/
> L2 | 父级: /CLAUDE.md

## 职责

身份定义 - 定义奥一是谁、AI 如何服务奥一。

**变更分级见下方成员清单，不同文件级别不同。**

## 指代规范

- 「奥一」= 用户
- 「AI」= Claude/系统

## 成员清单

- `TELOS.md`: 奥一的身份框架（使命/目标/挑战/策略/信念/框架/模型/经历）→ **B类审批**
- `AI_RULES.md`: AI 行为准则（交互规则/行为要求/角色方法）→ **B类审批**
- `MEMORY.md`: 身份记忆主入口（检索优先级索引，了解奥一时从此处开始）→ **B类审批**
- `CONTEXT.md`: 当前动态上下文（活跃项目/近期关注/近期决策/工作模式）→ **A类自动**
- `PROFILE.md`: AI 观察到的场景化偏好（品味/交互要求/任务偏好）→ **A类写入（经 /digest 确认后晋升），冲突升B类**

## 变更分级

- TELOS.md / AI_RULES.md / MEMORY.md → **B类**，必须审批
- CONTEXT.md → **A类**，AI 在对话中识别到上下文变化时自动更新，或通过 /digest 手动触发
- PROFILE.md → **A类**，新偏好先存 working-memory/candidates.md 暂存，/digest 确认后晋升写入；发现冲突先场景化，场景化失败升B类

## TELOS 快速索引

| 前缀 | 含义 |
|------|------|
| M# | 使命 Mission |
| G# | 目标 Goal |
| C# | 挑战 Challenge |
| S# | 策略 Strategy |
| B# | 信念 Belief |
| FR# | 框架 Frame |
| MO# | 模型 Model |
| TR# | 经历 Trauma |

---

[PROTOCOL]: 变更时更新此头部，然后检查 /CLAUDE.md
**Identity 变更必须经过人工审批**
