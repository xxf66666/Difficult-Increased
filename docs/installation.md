# 安装与调用

本仓库提供一个完整的 `task-difficulty-design` 技能目录和一个仅用 Python 标准库的复制安装器。需要 Python 3.9 或更新版本；安装本身不调用模型、不联网、不修改 agent 配置。仓库克隆到哪里与技能安装到哪里是两回事。

## 安装位置

截至 **2026-10-02** 核对的官方文档，本安装器使用以下路径：

| Agent | 用户范围：本机各项目可用 | 项目范围：指定项目可用 |
| --- | --- | --- |
| Codex | `~/.agents/skills/task-difficulty-design/` | `<项目>/.agents/skills/task-difficulty-design/` |
| Claude Code | `~/.claude/skills/task-difficulty-design/` | `<项目>/.claude/skills/task-difficulty-design/` |

来源：[OpenAI 官方 Build skills](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)、[Claude Code 官方 skills 文档](https://code.claude.com/docs/en/skills#choose-where-skills-load)。这是本地技能安装，不会替你配置云端会话或其他 agent。

Codex 的当前官方安装位置表使用 `.agents/skills`。本安装器不额外复制到 `.codex/skills`，以免同名版本重复。若你的特定旧版本或发行版明确要求其他目录，核对其支持情况后使用下文 `--target-dir`；本仓库不宣称所有版本都识别旧目录。

## 用户范围安装

在终端运行下面的命令。先看预览，再执行安装；所有命令均在仓库根目录执行。

```bash
git clone https://github.com/xxf66666/Difficult-Increased.git
cd Difficult-Increased
python3 scripts/install.py --agent both --scope user --dry-run
python3 scripts/install.py --agent both --scope user
```

仅安装到一个 agent 时，把 `both` 改成 `codex` 或 `claude`。省略 `--scope` 时默认为 `user`；必须显式提供 `--agent` 或 `--target-dir`，空命令不会直接安装。

## 项目范围安装

先把示例路径替换为真实存在的项目目录。含空格或中文的路径保留引号。

```bash
python3 scripts/install.py --agent both --scope project --project-dir "/path/to/project" --dry-run
python3 scripts/install.py --agent both --scope project --project-dir "/path/to/project"
```

项目范围适合团队共享与项目内版本管理；安装后自行决定是否将生成的 `.agents/skills/`、`.claude/skills/` 纳入该项目 Git。避免在用户范围和项目范围长期保留不同版本的同名技能。

## 其他 agent 或自定义路径

确认目标 agent 支持目录式 `SKILL.md`，并查清它的技能发现路径后，再指定技能根目录：

```bash
python3 scripts/install.py --target-dir "/path/to/agent/skills" --dry-run
python3 scripts/install.py --target-dir "/path/to/agent/skills"
```

最终位置是 `/path/to/agent/skills/task-difficulty-design/`。`--target-dir` 不能与 `--agent`、`--scope`、`--project-dir` 同用。此选项只负责复制，不能证明其他 agent 已识别或能正确调用技能。

若手工安装，也要复制整个 `skills/task-difficulty-design/` 目录，保留内部相对路径；只复制 `SKILL.md` 会丢失引用材料。

## 更新、冲突与备份

安装器会比较文件内容、目录结构和可执行标记。内容相同则跳过；目标存在不同内容则报错退出，默认不会覆盖。`both` 模式先完成两处冲突检查，再写入文件。

```bash
git pull --ff-only
python3 scripts/install.py --agent both --scope user --force --dry-run
python3 scripts/install.py --agent both --scope user --force
```

`--force` 先把旧目录完整移到备份区，再替换技能目录，不会把已删除的旧文件混入新版本。备份目录会显示在终端中，例如：

```text
~/.agents/.task-difficulty-design-backups/<UTC时间戳>-<随机后缀>/
~/.claude/.task-difficulty-design-backups/<UTC时间戳>-<随机后缀>/
```

项目安装备份放在项目相应的 `.agents/`、`.claude/` 下。自定义安装备份位于技能根目录的上一级目录中的 `.task-difficulty-design-backups/`。备份放在 `skills/` 外，避免旧版技能再次被发现。安装器不自动删除备份。

恢复时，先退出正在使用该技能的会话，把当前 `task-difficulty-design/` 移到技能发现目录之外，再把所需的备份目录移动回原安装路径并命名为 `task-difficulty-design`。保留希望追回的本地改动。

安装器拒绝源目录与目标重叠、`..` 路径、技能目录中的符号链接、生成的配置路径中的符号链接，以及非常规文件。现有符号链接安装请自行确认链接去向后调整；`--force` 不绕过这些检查。多目标写入不是跨目录事务；若发生权限或磁盘错误，查看输出中已完成的目标，修复错误后重新运行。

## 调用与确认

Codex 中输入：

```text
$task-difficulty-design
请改进当前题目的 prompt 和输入附件，在保留真实业务与可解性的前提下提升难度和必要轮次。先精读原始材料，给出具体改题方案。
```

Claude Code 中输入：

```text
/task-difficulty-design 请改进当前题目的 prompt 和输入附件，提升难度和必要轮次。
```

也可以直接说“使用 task-difficulty-design 技能”，并说明项目路径和要处理的题目与附件。安装只让技能可被发现，具体任务仍需提供材料。

Codex 官方说明会自动检测技能变化；未出现时重启 Codex。Claude Code 官方说明支持技能变化检测，新建顶层技能目录后可运行 `/reload-skills`；版本不支持时重新启动会话。见 [OpenAI 技能创建与加载说明](https://learn.chatgpt.com/docs/build-skills)、[Claude Code 技能更新说明](https://code.claude.com/docs/en/skills#edit-a-skill-during-a-session)。安装成功应以目标目录完整存在且 agent 能实际加载为准，单看复制成功还不能证明模型已按技能执行。

## 卸载

关闭使用该技能的会话，把实际安装的 `task-difficulty-design/` 目录移到 agent 技能发现目录之外，确认不再需要后再删除。若同时安装了两个 agent 或多个项目，要分别处理每个安装位置。不要删除整个 `.agents/skills/` 或 `.claude/skills/`，其中可能有其他技能。备份目录和仓库克隆保留与否由你决定。

## 安装器自检

```bash
python3 -m unittest discover -s tests -p 'test_install.py' -v
```

测试使用临时目录和独立 `HOME`，验证用户/项目/自定义安装、预览无写入、重复安装、冲突保护、强制更新备份、源目录与链接保护、失败恢复。不会安装到真实用户目录。测试通过仅证明安装器行为，不证明题目难度或轮次达标。
