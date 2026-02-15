---
para: resource
domain: AI
type: 体系
tags: [提示词工程, Agent, 架构设计, 逻辑架构]
layer: 本质
status: active
summary: 小Y Agent架构v2.1
created: 2026-02-13
updated: 2026-02-13
reviewed_at: 2026-02-14
---

# 小Y Agent 抽象架构 v2.1（Prompt 引导 + 建议式模板）

> 本版在 v2.1 的基础上吸收 Kode_Ori 的运行风格：工具保持原子化、流程写在提示里、模板是“建议”不是命令。目标是让模型在 prompt 的指引下自主规划，同时保留清晰的可观测性和扩展空间。

## 1. Guiding Ideas

1. **工具越简单，模型越聪明**：每个工具只做一件事，输入输出结构化，失败时给出友好提示。
2. **模板是“提示”而不是“脚本”**：模板告诉模型典型步骤，但模型可以按需调整，只要在 Plan 里说明理由。
3. **判断器帮助而非限制**：`determine_context` 提供“需要衣橱/天气/图像结构化吗？”之类的建议；模型可以采纳或忽略，并记录决策。
4. **角色＝策略人格**：Stylish/Curator/Logistician/Image Artisan 只是不同的策略提示。它们会思考、挑选工具、总结结果，而不直接执行底层逻辑。

## 2. Tools（原子能力）

| 工具                                                                          | 职责                  | 主要出场角色                                            | 说明                                                                                                      |
| --------------------------------------------------------------------------- | ------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `profile_read` / `profile_write`                                            | 操作用户画像              | Planner, Archivist                                | `write` 需 `confirm=true`；提示中列出允许字段。                                                                     |
| `wardrobe_read` / `wardrobe_write` / `wardrobe_stats` / `wardrobe_logUsage` | 操作衣橱与统计             | Planner, Archivist, Stylist, Curator, Logistician | 每个子 action 单独描述，减少模型混淆。                                                                                 |
| `trace_read` / `trace_write`                                                | 记录与回放 Plan          | Planner, Archivist                                | 用于多轮交互与调试。                                                                                              |
| `determine_context`                                                         | 返回任务需要的上下文/建议模板     | Planner                                           | 输出示例：`{ needsWardrobe:true, needsWeather:false, needsImageEdit:false, suggestedTemplate:'OOTD_EVAL' }`。 |
| `process_image_basic`                                                       | 不涉及衣橱的图片点评/解释       | Planner, Stylist, Curator                         | 调用多模态模型；输出 `{ narrative, positives?, issues? }`。                                                        |
| `process_image_structured`                                                  | 需要衣橱的图片解析（拆白、打标、匹配） | Image Artisan, Planner                            | 输入 `{ imagePath, tasks:['segment','tag','match'] }`；输出属性、匹配 ID、置信度。                                     |
| `edit_image`（预留）                                                            | 根据指令编辑图片            | Image Artisan                                     | MVP 返回占位提示，后续接入生成模型。                                                                                    |
| `generate_outfits`                                                          | 生成搭配方案              | Stylist, Curator, Logistician                     | 输入包含 `goal`, `constraints`, `wardrobeSnapshot`；输出附 `differentiators`。                                   |
| `fetch_weather`                                                             | 拉取天气                | Stylist, Logistician                              | 支持单日/多日。                                                                                                |
| `compose_moodboard`（可选）                                                     | 情绪板拼接               | Curator, Image Artisan                            | 使用本地脚本或生成模型。                                                                                            |
| `tryon`（可选）                                                                 | 虚拟试穿                | Stylist, Image Artisan                            | MVP 可返回“未启用”。                                                                                           |
| `todo_read` / `todo_write`（新增）                                              | 任务面板（模型驱动）          | Planner                                           | 文件落地 `trace/todos/<sessionId>.json`，覆盖式写入，便于进度可视化。                                                      |

> 每个工具的 prompt 模板提供：成功示例、失败示例、常见误用提示，确保失败信息可直接反馈给用户。

## 3. Roles（策略人格）

| 角色 | 职责 | 可用工具 | Prompt 重点 |
| --- | --- | --- | --- |
| **Planner** | 理解需求、调用 `determine_context`、生成 Plan、召集角色、汇总结果 | 全部工具（写操作需确认） | Prompt 写明：模板是建议，可调整；调整时更新 Plan 并说明原因。 |
| **Archivist** | 准备/更新上下文，提醒缺失信息 | `profile_*`, `wardrobe_*`, `trace_*`, `similarity` | 在模板中负责“准备上下文”步骤；遇到缺数据主动提示 Planner。 |
| **Stylist** | 穿搭建议、每日推荐、情绪搭配 | `generate_outfits`, `fetch_weather`, `tryon`, `process_image_basic`, `wardrobe_read` | Prompt 中强调：如果衣橱不足，要退回给用户，不要盲猜。 |
| **Curator** | 风格解释、主题挑战、情绪板 | `wardrobe_stats`, `process_image_basic`, `compose_moodboard`, `generate_outfits`, `similarity` | Prompt 中列出如何引用衣橱统计、如何生成灵感板。 |
| **Logistician** | 旅行/场合/购前评估 | `determine_context`, `wardrobe_*`, `fetch_weather`, `generate_outfits`, `similarity`, `trace_*` | Prompt 指导其输出结构化清单；遇到信息缺口请求补充。 |
| **Image Artisan** | 图片理解、拆白打标、以图搜图、图像编辑 | `process_image_basic`, `process_image_structured`, `edit_image`, `tryon`, `similarity` | Prompt 中明确 basic vs structured 的选择逻辑，并提供编辑提示语例。 |

> 角色提示借鉴 Kode_Ori 工具说明风格：列出“什么时候该用/不该用、常见误区、返回格式”。

## 4. 建议式任务模板（Playbooks）

模板结构：
```yaml
templateId: OOTD_EVAL
description: "用户上传 OOTD，希望点评和优化"
recommendedSteps:
  - step: "Image Artisan -> process_image_basic"
    purpose: "先用多模态模型做整体点评"
  - step: "Image Artisan -> process_image_structured"
    condition: "needsWardrobe == true"
  - step: "Archivist -> wardrobe_read"
  - step: "Stylist -> generate_outfits"
  - step: "Planner -> summarize"
allowAdjustments:
  - "如果用户只要文字点评，可在步骤1结束"
  - "如果匹配置信度低，提示用户换图"
failureHints:
  - "process_image_structured 返回 ok:false -> 告知用户图片模糊"
```

**使用方式**：
1. Planner 调用 `determine_context`，拿到 `suggestedTemplate`。
2. Planner 在 prompt 中写：
   - “参考模板 OOTD_EVAL。若你发现不适用，请写出新的 Plan，并在第一步说明原因。”
3. 角色执行时可以增删步骤，只要在 Plan 中记录。

> 模板本身可以保存在配置文件中，便于迭代；也可根据 Trace 数据调整。

## 5. 示例：Plan（文本版）

```
Plan v1 (参考模板 OOTD_EVAL)
1. Image Artisan: process_image_basic -> 理解照片整体穿搭效果
2. Image Artisan: 如果 step1 返回 needsWardrobe=true，则 process_image_structured
3. Archivist: wardrobe_read(ids) 获取匹配衣物详情
4. Stylist: generate_outfits(goal=improve)
5. Planner: 汇总建议，询问用户是否需要试穿或图像编辑

调整记录：如果用户只想要文字点评，跳过步骤2-4，并说明“用户不希望做衣橱比对”。
```

## 6. 重难点与注意事项

1. **判断器的准确率**：`determine_context` 需要大量示例来识别各种用户表达（比如“随便帮我看看”也可能需要衣橱上下文）。设计时要允许 Planner 覆写判断结果。
2. **模板粒度**：模板太细会限制自由，太粗会失去指导意义。建议围绕 6~7 个核心场景（每日推荐、单品搭配、OOTD、风格解释、旅行、购前、主题挑战）编写模板，并在 Trace 中观察是否需要拆分或合并。
3. **工具失败处理**：如同 Kode_Ori，任何工具失败必须带 `hint`，Planner 不要盲目重试，而是把 hint 反馈给用户。
4. **图像处理提示**：`process_image_structured` 的 prompt 要明确“无法识别时不要瞎编”，否则模型可能凭想象返回标签。
5. **多轮更新 Plan**：当用户中途修改需求（例如旅行计划改动），Planner 需更新 Plan 并写入 Trace，避免角色继续执行旧指令。
6. **角色 prompt 的自省**：借鉴 Kode_Ori 工具提示风格，为每个角色写“什么时候不要出场”“常见误区”，避免模型滥用角色。

## 7. Kode_Ori 的具体启示

1. **工具提示写法**：Kode_Ori 在每个工具的 prompt 中写了大量“不要这么用”“失败时该说什么”。我们需要对 `process_image_basic`、`generate_outfits` 等工具做同样的提示设计。
2. **子任务机制**：`TaskTool` 展示了“让模型起一个子 agent 自己完成复杂任务”的好处。可以考虑在小Y中让 Image Artisan/Curator 在个别复杂需求里独立运行，然后把结果返回给主流程。
3. **Trace 透明度**：Kode_Ori 会保存每一步工具调用和结果，方便调试。小Y 应照猫画虎，对 `trace_write` 输出结构化日志（Plan、调整记录、工具响应）。
4. **自由度 + 提醒**：Kode_Ori 的 prompt 会说“当用户问好时，你应该调用 greeting agent”，这种“提示式规则”非常奏效。我们也可以在角色 prompt 里写：“当发现用户上传单品，请主动建议调用 Image Artisan 的 structured 模式”。

## 8. 扩展方向
- 新能力上线流程 = 新工具（或扩展工具） + 新模板 + 角色提示更新，无需改动现有流程。
- 随着 Trace 堆积，可以分析哪些模板被修改频繁，反向调整模板或判断器提示。
- 如果判断器偏差大，可以像 Kode_Ori 那样在 prompt 中加更多“自我反问”提示：执行前再读一次需求，确认是否遗漏上下文。
- 引入“任务面板（Todo）”后，可进一步：为关键场景提供建议的初始清单模板；在 Trace 仪表盘中并列展示 Todo 进度。

---

这个 v2.1 版本既保留了我们原本的“角色 + 模板”优势，又用 Kode_Ori 的方式让模型在 prompt 指导下自由发挥。工具仍然小巧、失败透明；模板只是建议；判断器帮忙但不强迫。这样既优雅，又便于未来扩展。`
是的
#Architecture #StylingAgent #XiaoY
