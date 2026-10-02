"""Isolated installer tests: fake HOME and fixtures, never real agent settings."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "install.py"
NAME = "task-difficulty-design"
spec = importlib.util.spec_from_file_location("skill_installer", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.repo = self.root / "repository"
        self.source = self.repo / "skills" / NAME
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text("---\nname: task-difficulty-design\n---\nfixture\n", encoding="utf-8")
        (self.source / "references").mkdir()
        (self.source / "references" / "note.md").write_text("参考内容\n", encoding="utf-8")
        (self.source / "empty").mkdir()
        self.script = self.repo / "scripts" / "install.py"
        self.script.parent.mkdir()
        shutil.copy2(SCRIPT, self.script)
        self.home = self.root / "home"
        self.home.mkdir()
        self.project = self.root / "项目 with spaces"
        self.project.mkdir()
        self.env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                        PYTHONDONTWRITEBYTECODE="1")

    def tearDown(self):
        self.temporary.cleanup()

    def run_cli(self, *arguments, expected=0):
        result = subprocess.run([sys.executable, "-B", str(self.script), *arguments], cwd=self.root,
                                env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def destination(self, agent="codex", base=None):
        return (base or self.home) / (".agents" if agent == "codex" else ".claude") / "skills" / NAME

    def test_user_both_installs_complete_tree_in_current_documented_locations(self):
        self.run_cli("--agent", "both")
        for agent in ("codex", "claude"):
            self.assertEqual(installer.tree_digest(self.source), installer.tree_digest(self.destination(agent)))
        self.assertFalse((self.home / ".codex").exists())

    def test_project_scope_with_spaces_does_not_touch_home(self):
        self.run_cli("--agent", "both", "--scope", "project", "--project-dir", str(self.project))
        for agent in ("codex", "claude"):
            self.assertTrue((self.destination(agent, self.project) / "SKILL.md").is_file())
        self.assertEqual(list(self.home.iterdir()), [])

    def test_dry_run_creates_nothing(self):
        result = self.run_cli("--agent", "both", "--dry-run")
        self.assertIn("[dry-run]", result.stdout)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_custom_target_is_skills_root(self):
        root = self.root / "other-agent" / "skills"
        self.run_cli("--target-dir", str(root))
        self.assertTrue((root / NAME / "references" / "note.md").is_file())

    def test_same_content_is_idempotent_even_with_force(self):
        self.run_cli("--agent", "codex")
        before = (self.destination() / "SKILL.md").stat().st_mtime_ns
        result = self.run_cli("--agent", "codex", "--force")
        self.assertIn("内容相同，跳过", result.stdout)
        self.assertEqual(before, (self.destination() / "SKILL.md").stat().st_mtime_ns)
        self.assertFalse((self.home / ".agents" / f".{NAME}-backups").exists())

    def test_conflict_preflight_prevents_partial_both_install(self):
        existing = self.destination("claude")
        existing.mkdir(parents=True)
        (existing / "local.txt").write_text("keep")
        self.run_cli("--agent", "both", expected=1)
        self.assertEqual((existing / "local.txt").read_text(), "keep")
        self.assertFalse((self.home / ".agents").exists())

    def test_force_backs_up_outside_discovery_directory_and_replaces_tree(self):
        self.run_cli("--agent", "codex")
        destination = self.destination()
        (destination / "local.txt").write_text("old local content")
        old_digest = installer.tree_digest(destination)
        self.run_cli("--agent", "codex", "--force")
        backups = list((self.home / ".agents" / f".{NAME}-backups").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual(installer.tree_digest(backups[0]), old_digest)
        self.assertEqual(installer.tree_digest(destination), installer.tree_digest(self.source))
        self.assertFalse((destination / "local.txt").exists())

    def test_force_dry_run_does_not_change_conflicting_installation(self):
        destination = self.destination()
        destination.mkdir(parents=True)
        (destination / "local.txt").write_text("keep")
        self.run_cli("--agent", "codex", "--force", "--dry-run")
        self.assertEqual((destination / "local.txt").read_text(), "keep")
        self.assertFalse((self.home / ".agents" / f".{NAME}-backups").exists())

    def test_requires_explicit_agent_or_target(self):
        self.run_cli(expected=1)

    def test_invalid_parameter_combinations_do_not_write(self):
        cases = [
            ("--agent", "codex", "--target-dir", str(self.root / "other")),
            ("--agent", "codex", "--scope", "project"),
            ("--agent", "codex", "--project-dir", str(self.project)),
            ("--target-dir", str(self.root / "other"), "--scope", "user"),
            ("--agent", "codex", "--scope", "project", "--project-dir", str(self.root / "missing")),
        ]
        for args in cases:
            with self.subTest(args=args):
                self.run_cli(*args, expected=1)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_rejects_parent_traversal(self):
        self.run_cli("--target-dir", str(self.project / ".." / "other"), expected=1)

    def test_rejects_source_and_child_destinations(self):
        for root in (self.source.parent, self.source / "nested"):
            with self.subTest(root=root):
                self.run_cli("--target-dir", str(root), "--force", expected=1)
        self.assertFalse((self.source / "nested").exists())
        self.assertTrue((self.source / "SKILL.md").is_file())

    def test_rejects_source_ancestor_as_destination(self):
        with self.assertRaises(installer.InstallError):
            installer.protect_source(self.repo, self.source)

    def test_rejects_destination_symlink_even_with_force(self):
        destination = self.destination()
        destination.parent.mkdir(parents=True)
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_text("keep")
        destination.symlink_to(outside, target_is_directory=True)
        self.run_cli("--agent", "codex", "--force", expected=1)
        self.assertTrue(destination.is_symlink())
        self.assertEqual((outside / "keep.txt").read_text(), "keep")

    def test_rejects_generated_configuration_directory_symlink(self):
        (self.home / ".agents").symlink_to(self.project, target_is_directory=True)
        self.run_cli("--agent", "codex", expected=1)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_rejects_custom_root_symlink(self):
        link = self.root / "linked-skills"
        link.symlink_to(self.project, target_is_directory=True)
        self.run_cli("--target-dir", str(link), expected=1)

    def test_rejects_symlink_inside_existing_skill(self):
        self.run_cli("--agent", "codex")
        (self.destination() / "link").symlink_to(self.source / "SKILL.md")
        self.run_cli("--agent", "codex", "--force", expected=1)

    def test_rejects_source_symlink_and_missing_manifest(self):
        link = self.source / "linked-file"
        link.symlink_to(self.script)
        self.run_cli("--agent", "codex", expected=1)
        link.unlink()
        (self.source / "SKILL.md").unlink()
        self.run_cli("--agent", "codex", expected=1)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_rejects_file_in_parent_path(self):
        (self.home / ".agents").write_text("do not replace")
        self.run_cli("--agent", "codex", "--force", expected=1)
        self.assertEqual((self.home / ".agents").read_text(), "do not replace")

    def test_rejects_linked_backup_directory_before_changes(self):
        self.run_cli("--agent", "codex")
        (self.destination() / "old.txt").write_text("keep")
        backup_root = self.home / ".agents" / f".{NAME}-backups"
        backup_root.symlink_to(self.project, target_is_directory=True)
        self.run_cli("--agent", "codex", "--force", expected=1)
        self.assertEqual((self.destination() / "old.txt").read_text(), "keep")

    def test_failed_final_rename_restores_previous_installation(self):
        self.run_cli("--agent", "codex")
        destination = self.destination()
        (destination / "local.txt").write_text("must survive")
        old_digest = installer.tree_digest(destination)
        original_rename = Path.rename

        def fail_stage(path, target):
            if "-stage-" in str(path.parent):
                raise OSError("simulated disk failure")
            return original_rename(path, target)

        with patch.object(Path, "rename", fail_stage):
            with self.assertRaises(OSError):
                installer.install_one(self.source, destination, "replace")
        self.assertEqual(installer.tree_digest(destination), old_digest)
        self.assertFalse(list(destination.parent.glob(f".{NAME}-stage-*")))


if __name__ == "__main__":
    unittest.main()
