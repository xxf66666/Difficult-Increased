#!/usr/bin/env python3
"""Copy this repository's skill into a local agent skill directory.

Standard library only; no network requests, agent invocation, or configuration edits.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
from datetime import datetime, timezone
from uuid import uuid4


SKILL_NAME = "task-difficulty-design"
SOURCE = Path(__file__).resolve().parent.parent / "skills" / SKILL_NAME


class InstallError(Exception):
    """A validation or installation error safe to show to the user."""


def contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def absolute_path(value: str) -> Path:
    path = Path(value).expanduser()
    if ".." in path.parts:
        raise InstallError("路径不能含有 '..'，请使用明确的目录路径。")
    return Path(os.path.abspath(path))


def reject_links(path: Path, boundary: Path) -> None:
    """Check generated path components before resolving them."""
    if not contains(boundary, path):
        raise InstallError(f"路径超出预期目录：{path}")
    current = path
    while True:
        if current.is_symlink():
            raise InstallError(f"拒绝写入符号链接路径：{current}")
        if current == boundary:
            break
        current = current.parent


def tree_digest(root: Path) -> str:
    """Compare contents, empty directories and executable flags, never links."""
    if root.is_symlink() or not root.is_dir():
        raise InstallError(f"必须是普通目录，不能是符号链接：{root}")
    digest = hashlib.sha256()
    entries = [root] + sorted(root.rglob("*"))
    for path in entries:
        info = path.lstat()
        relative = path.relative_to(root).as_posix().encode("utf-8")
        if stat.S_ISLNK(info.st_mode):
            raise InstallError(f"技能目录中含有符号链接：{path}")
        if stat.S_ISDIR(info.st_mode):
            kind, payload = b"D", b""
        elif stat.S_ISREG(info.st_mode):
            kind = b"X" if info.st_mode & 0o111 else b"F"
            payload = hashlib.sha256(path.read_bytes()).digest()
        else:
            raise InstallError(f"技能目录中含有非常规文件：{path}")
        digest.update(kind + len(relative).to_bytes(8, "big") + relative + payload)
    return digest.hexdigest()


def protect_source(destination: Path, source: Path) -> None:
    target = destination.resolve()
    origin = source.resolve()
    if contains(origin, target) or contains(target, origin):
        raise InstallError(f"安装目标与仓库技能源目录重叠：{destination}")


def build_targets(args: argparse.Namespace) -> list[tuple[Path, Path]]:
    """Return (destination, checked boundary); the skill name is always fixed."""
    if args.target_dir:
        if args.agent or args.scope or args.project_dir:
            raise InstallError("--target-dir 不能与 --agent、--scope 或 --project-dir 同用。")
        base = absolute_path(args.target_dir)
        if base.is_symlink():
            raise InstallError(f"自定义技能根目录不能是符号链接：{base}")
        # An explicitly supplied ancestor may be an OS alias, e.g. /var on macOS.
        base = base.resolve()
        return [(base / SKILL_NAME, base)]
    if not args.agent:
        raise InstallError("请指定 --agent codex|claude|both，或 --target-dir。")
    scope = args.scope or "user"
    if scope == "project":
        if not args.project_dir:
            raise InstallError("项目安装必须通过 --project-dir 指定已有项目目录。")
        base = absolute_path(args.project_dir).resolve()
        if not base.is_dir():
            raise InstallError(f"项目目录不存在或不是目录：{base}")
    else:
        if args.project_dir:
            raise InstallError("--project-dir 只能与 --scope project 同用。")
        base = Path.home().resolve()
    agents = ("codex", "claude") if args.agent == "both" else (args.agent,)
    folders = {"codex": ".agents", "claude": ".claude"}
    return [(base / folders[agent] / "skills" / SKILL_NAME, base) for agent in agents]


def preflight(targets: list[tuple[Path, Path]], source: Path, force: bool) -> list[tuple[Path, str]]:
    source_digest = tree_digest(source)
    if not (source / "SKILL.md").is_file():
        raise InstallError(f"源技能缺少 SKILL.md：{source}")
    plans = []
    for destination, boundary in targets:
        reject_links(destination, boundary)
        protect_source(destination, source)
        # Preflight all targets before any writes; a conflict in 'both' stops both.
        for ancestor in [destination.parent, *destination.parent.parents]:
            if ancestor.exists() and not ancestor.is_dir():
                raise InstallError(f"目标父路径不是目录：{ancestor}")
        if destination.exists():
            if tree_digest(destination) == source_digest:
                plans.append((destination, "unchanged"))
                continue
            if not force:
                raise InstallError(f"目标已有不同内容，未覆盖：{destination}\n确认更新时使用 --force；旧目录会先移到备份区。")
            backup_root = destination.parent.parent / f".{SKILL_NAME}-backups"
            reject_links(backup_root, destination.parent.parent)
            protect_source(backup_root, source)
            if backup_root.exists() and not backup_root.is_dir():
                raise InstallError(f"备份位置不是目录：{backup_root}")
            plans.append((destination, "replace"))
        else:
            plans.append((destination, "install"))
    return plans


def install_one(source: Path, destination: Path, action: str) -> Path | None:
    if action == "unchanged":
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    # Copy successfully before moving the previous installation out of the way.
    with tempfile.TemporaryDirectory(prefix=f".{SKILL_NAME}-stage-", dir=destination.parent) as temporary:
        stage = Path(temporary) / SKILL_NAME
        shutil.copytree(source, stage)
        if action == "replace":
            backup_root = destination.parent.parent / f".{SKILL_NAME}-backups"
            backup_root.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup = backup_root / f"{stamp}-{uuid4().hex[:8]}"
            destination.rename(backup)
        try:
            stage.rename(destination)
        except OSError:
            if backup is not None and not destination.exists():
                backup.rename(destination)
            raise
    return backup


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="安装 task-difficulty-design 技能；默认保留已有不同内容。")
    parser.add_argument("--agent", choices=("codex", "claude", "both"), help="目标 agent")
    parser.add_argument("--scope", choices=("user", "project"), help="默认 user；project 必须指定项目目录")
    parser.add_argument("--project-dir", help="已有项目根目录，仅 scope=project 可用")
    parser.add_argument("--target-dir", help="其他 agent 的技能根目录；会追加 task-difficulty-design")
    parser.add_argument("--dry-run", action="store_true", help="只校验和显示计划，不创建目录或文件")
    parser.add_argument("--force", action="store_true", help="替换不同内容；先完整备份原目录")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        targets = build_targets(args)
        plans = preflight(targets, SOURCE, args.force)
        print(f"技能来源：{SOURCE}")
        for destination, action in plans:
            label = {"unchanged": "内容相同，跳过", "replace": "备份后更新", "install": "新安装"}[action]
            if args.dry_run:
                print(f"[dry-run] {label}：{destination}")
                if action == "replace":
                    print(f"  备份区：{destination.parent.parent / ('.' + SKILL_NAME + '-backups')}")
                continue
            backup = install_one(SOURCE, destination, action)
            print(f"{label}：{destination}")
            if backup:
                print(f"  已备份：{backup}")
        return 0
    except (InstallError, OSError) as exc:
        print(f"安装失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
