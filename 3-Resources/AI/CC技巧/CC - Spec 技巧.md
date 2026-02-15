---
para: resource
domain: AI
type: 方法论
tags: [提示词工程, ClaudeCode, SpecCoding]
layer: 本质
status: active
summary: AI辅助开发工作流方法论
created: 2026-02-13
updated: 2026-02-13
reviewed_at: 2026-02-14
---

# AI辅助开发工作流方法论


基于您分享的对话，我整理出以下完整的AI辅助开发工作流方法论：

## 🔄 核心工作流程

### 1. **代码分析阶段**

- 使用 **DeepWiki** 让AI扫描现有代码
- AI自动提取和描述业务逻辑
- 将业务逻辑整理到规格说明（spec）中

### 2. **需求文档生成**

- 关键提示词：`"我需要你作为一个产品专家，请基于XXX写一个prd.md"`
- 利用AI对PRD（产品需求文档）的丰富训练数据
- AI生成初版PRD文档

### 3. **迭代优化**

- Review AI生成的PRD
- 持续修改直到需求完全清晰
- 确保开发方向明确后再开始编码

## 🔍 复杂问题解决方案

### 当遇到技术难题时：

1. **使用DeepResearch进行深度分析**
    
    - 这是OpenAI的核心护城河能力
    - 分析技术可行性方案
    - 研究相关开源库实现
2. **方案融合**
    
    - 将DeepResearch结果融合到PRD.md
    - 结合DeepWiki的代码分析
    - 形成完整的技术方案
3. **任务分解**
    
    - 生成详细的TodoList
    - 或调用TaskMaster的MCP进行任务管理

#AICoding #Spec #Workflow #PRD
