# Difficult-Increased

一份给 **Codex、Claude Code 及兼容 `SKILL.md` 的 Agent** 使用的出题技能。

这个项目来自一个反复出现的痛点：题目已经写了很多材料，模型却依然容易拿高分，或者很快就交卷，难度和执行轮次总达不到要求。技能的目标是提炼可复用的方法，帮助出题人和 Agent **实际改进 prompt 与输入附件，提高判断难度和必要工作量**。

核心入口：[task-difficulty-design / SKILL.md](skills/task-difficulty-design/SKILL.md) · [可复用改造方法](skills/task-difficulty-design/references/transformation-playbook.md) · [安装说明](docs/installation.md)

## 它怎样帮助改题

| 常见问题 | 采用的方法 |
|---|---|
| 题面已经告诉模型怎么算、看哪里、以谁为准 | 保留明确委托与交付要求，把答案导航移回作者材料 |
| 附件太干净，模型直接读总表就完成 | 恢复未经整理的工作面；可主动增加错字、错值、错单位、重复与旧汇总，并用跨源证据支持纠错 |
| 几行文字或数据就单独做成一份附件，一看就在给某个考点递线索 | 作为必须返工的问题处理；恢复完整相关资料和充分自然噪声，再做跨源判断设计 |
| 每份附件刚好对应一个答案 | 保留自然的跨源信息分布，让关键事实需要关联恢复 |
| “最新版本”“综合榜单”直接决定答案 | 让判断回到权限、生效状态、适用对象与当前业务瓶颈 |
| 工作不少，但都是独立的小活 | 让证据判断改变后续计算、方案、执行与交付 |
| 增加文件、页数仍然没有作用 | 使用有不同业务用途的产物、全量对象处理、实质情景重算和必要验证 |
| PDF 过度统一，像作者精修过的报告 | 用 TeX 保证可读，保留来源间版式差异与可恢复的内容错误；无需统一精整 |
| 同一行业的多道题只有标题、数字或输出格式不同 | 从五种方向拆分，按核心决定、证据、约束与交付结果去重，逐题落实难度 |
| 题目有专业难点，考点却只查格式、关键词和“分析合理” | 八项考点写法，明确结果、依据、单位、容差及替代解，检查专业判断是否实际被测到 |

每种方法说明适用迹象、具体操作、对难度和轮次的作用，以及怎样检查仍然可解。范围限定为 **prompt、输入附件、判断难度、必要执行与效果验证**，不扩展成项目管理工具。

**附件硬要求：禁止几行一份、只服务单个考点的输入附件。** 必须保留足够的普通记录、历史项、非关键内容与业务上下文，让模型进行实质筛选和关联。水印、复制行、机械合并小文件或随机填充都不能补足内容；技能中的教学小例也不能直接当附件交付。详见 [具体反例与检查方法](skills/task-difficulty-design/references/prompt-and-attachments.md)。

**业务呈现硬要求：题面和附件不添加“非真实材料”“构造数据”“模拟数据”“脱敏数据”“仅供测评”等作者制作说明。** 正文、文件名、水印、备注、隐藏内容和元数据均适用；制作与缺件记录放在作者侧，保留原资料中影响判断的业务状态、版本和来源信息。

可以有意设计信息分布、规则交叠和前后依赖。关键是让新增关系影响实际结果：跨文件得到的事实改变对象状态，状态改变适用规则，规则改变方案，验证结果再决定是否需要修正。这样，判断难点发生在必须完成的工作里。

**原始记录允许有错。** 可以扩充 CSV、表格和文档，加入错别字、错误数据、错误单位、混合格式与不一致记录；从其他输入证据恢复正确结果，再用于计算和安排。不要在交付前把这些噪声清洗掉，也不要给模型一张错误位置或正确值对照表。详见 [原生错误与可恢复噪声](skills/task-difficulty-design/references/recoverable-noise.md)。

## 安装

需要 Python 3.9+。在终端执行：

```bash
git clone https://github.com/xxf66666/Difficult-Increased.git
cd Difficult-Increased
python3 scripts/install.py --agent both --scope user
```

可将 `both` 换为 `codex` 或 `claude`。安装器默认保留已有不同版本；`--dry-run` 可预览，`--force` 会先备份再更新。项目范围、其他 Agent、自定义目录和卸载见 [安装说明](docs/installation.md)。安装包采用统一技能目录，两个 Agent 使用同一套内容。

## 怎么用

Codex：

```text
$task-difficulty-design
这道题一直达不到难度和轮次要求。请精读现有 prompt 和输入附件，
找出作者替模型做掉的判断与缺少依赖的地方，在原场景内实际改题。
重点改 prompt 和附件；说明每项改动怎样增加难度、怎样增加必要工作，以及可解性依据。
```

Claude Code：

```text
/task-difficulty-design 改进当前题目的 prompt 与输入附件，提升难度和有效轮次，保留真实来源与原场景。
```

只需审查时说明“先审查，不修改”。新题提供业务任务与原始材料；升级题提供现有题面、附件，以及已有失败证据（若有）。无需先准备一套完整评分系统才能开始改题。

## 内容

- [核心改造方法](skills/task-difficulty-design/references/transformation-playbook.md)：4 类 prompt 改造、8 类附件改造，以及把判断难点接到必要工作的方法。
- [难度机制](skills/task-difficulty-design/references/difficulty-mechanisms.md)：证据效力、瓶颈、规则组合、局部不可行、口径和跨阶段一致性。
- [跨文件证据专项](skills/task-difficulty-design/references/cross-file-evidence.md)：7 种方法，含实体拆并、双时间、证据依赖、跨载体约束、调节关系与覆盖边界。
- [跨规则组合专项](skills/task-difficulty-design/references/rule-composition.md)：8 种方法，含部分覆盖、状态触发、非交换顺序、共享资源、精度边界、全局可行与最小修复。
- [难度与执行联动](skills/task-difficulty-design/references/coupled-execution.md)：8 种方法，将竞争解释、判别取证、反例修复、变更传播、不确定性与核验接成必要工作。
- [提示词与附件](skills/task-difficulty-design/references/prompt-and-attachments.md)、[PDF 制作](skills/task-difficulty-design/references/pdf-authoring.md)。
- [原生错误与可恢复噪声](skills/task-difficulty-design/references/recoverable-noise.md)：错字、错值、错单位、错汇总、CSV/表格扩充与不统一版式，把纠错接入后续重算。
- [轮次与验证](skills/task-difficulty-design/references/rounds-and-validation.md)：必要工作设计、计数、评分与失败后修复。
- [同领域多题设计](skills/task-difficulty-design/references/task-portfolio.md)：五种方向拆分、实质去重、H1–H6 能力层次和逐题验证。
- [考点写法与区分度](skills/task-difficulty-design/references/rubric-writing.md)：八项写法、数值容差、开放方案、隐性专业判断与反向检查。
- [作者改造记录模板](skills/task-difficulty-design/assets/design-record.md)：把具体改动、判断难点、必要工作和验证证据对应起来。
- [来源与取舍](skills/task-difficulty-design/references/source-notes.md)：指定材料、会议纪要、用户口述与后续两份出题/考点材料的抽象过程。

具体使用示例：[供应商交付安排](docs/examples/supplier-delivery-redesign.md) · [返修承诺的三套改造组合](docs/examples/repair-commitment-redesign.md)。示例展示怎样把方法用于题面和附件组织，不是已通过难度跑测的提交题目。

技能不预设所有项目的分数线，也不保证使用后一定达到某个轮次。它提供可执行的改题方法；效果仍需从实际题目、模型产物和原始执行记录验证。

## 维护与验证

```bash
python3 -B -m unittest discover -s tests -v
```

安装测试在临时目录中运行。内容更新后，还应检查相对链接、真实场景适用性，并用独立的小任务检验技能行为。验证记录见 [docs/validation.md](docs/validation.md)。

公开仓库只保留抽象方法、安装工具和来源定位，不收录用户的原始业务附件、未公开完整说明、平台链接或具体题目答案。
