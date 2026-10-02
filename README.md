# Difficult-Increased

一份给 **Codex、Claude Code 及兼容 `SKILL.md` 的 Agent** 使用的出题技能。

这个项目来自一个反复出现的痛点：题目已经写了很多材料，模型却依然容易拿高分，或者很快就交卷，难度和执行轮次总达不到要求。技能的目标是提炼可复用的方法，帮助出题人和 Agent **实际改进 prompt 与输入附件，提高判断难度和必要工作量**。

核心入口：[task-difficulty-design / SKILL.md](skills/task-difficulty-design/SKILL.md) · [可复用改造方法](skills/task-difficulty-design/references/transformation-playbook.md) · [安装说明](docs/installation.md)

## 它怎样帮助改题

| 常见问题 | 采用的方法 |
|---|---|
| 题面已经告诉模型怎么算、看哪里、以谁为准 | 保留明确委托与交付要求，把答案导航移回作者材料 |
| 附件太干净，模型直接读总表就完成 | 回到真实原始材料，保留历史项、背景、分歧、冗余与例外 |
| 每份附件刚好对应一个答案 | 保留自然的跨源信息分布，让关键事实需要关联恢复 |
| “最新版本”“综合榜单”直接决定答案 | 让判断回到权限、生效状态、适用对象与当前业务瓶颈 |
| 工作不少，但都是独立的小活 | 让证据判断改变后续计算、方案、执行与交付 |
| 增加文件、页数仍然没有作用 | 使用有不同业务用途的产物、全量对象处理、实质情景重算和必要验证 |
| PDF 缺少专业排版或原始材料上下文 | 新建/重排 PDF 用 TeX，保留源码；浅水印与轻微噪声不遮挡证据 |

每种方法说明适用迹象、具体操作、对难度和轮次的作用，以及怎样检查仍然可解。范围限定为 **prompt、输入附件、判断难度、必要执行与效果验证**，不扩展成项目管理工具。

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
- [提示词与附件](skills/task-difficulty-design/references/prompt-and-attachments.md)、[PDF 制作](skills/task-difficulty-design/references/pdf-authoring.md)。
- [轮次与验证](skills/task-difficulty-design/references/rounds-and-validation.md)：必要工作设计、计数、评分与失败后修复。
- [作者改造记录模板](skills/task-difficulty-design/assets/design-record.md)：把具体改动、判断难点、必要工作和验证证据对应起来。
- [来源与取舍](skills/task-difficulty-design/references/source-notes.md)：三份指定材料、会议纪要和用户口述的抽象过程。

技能不预设所有项目的分数线，也不保证使用后一定达到某个轮次。它提供可执行的改题方法；效果仍需从实际题目、模型产物和原始执行记录验证。

## 维护与验证

```bash
python3 -B -m unittest discover -s tests -v
```

安装测试在临时目录中运行。内容更新后，还应检查相对链接、真实场景适用性，并用独立的小任务检验技能行为。验证记录见 [docs/validation.md](docs/validation.md)。

公开仓库只保留抽象方法、安装工具和来源定位，不收录用户的原始业务附件、未公开完整说明、平台链接或具体题目答案。
