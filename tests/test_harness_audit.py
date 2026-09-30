"""CLI contracts for package checking and the existing full-harness audit."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "skills/build-agent-harness/scripts/harness_audit.py"
PLANS = REPOSITORY / "skills/build-agent-harness/assets/PLANS.md"


class HarnessAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "sample-skill"
        self.package.mkdir()
        self.entrypoint = self.package / "SKILL.md"
        self.entrypoint.write_text(
            "---\nname: sample-skill\ndescription: Audit sample instructions.\n---\n\n"
            "# Sample skill\n\nRead [guidance](references/guide.md).\n",
            encoding="utf-8",
        )
        (self.package / "references").mkdir()
        (self.package / "references/guide.md").write_text("# Guidance\n", encoding="utf-8")

    def run_cli(self, *arguments, structured=True):
        command = [sys.executable, str(SCRIPT), *map(str, arguments)]
        if structured:
            command.append("--json")
        process = subprocess.run(
            command, cwd=self.root, capture_output=True, text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False,
        )
        self.assertEqual(process.stderr, "", process.stderr)
        return process.returncode, json.loads(process.stdout) if structured else process.stdout

    def check_package(self):
        return self.run_cli("validate-skill", "--skill-dir", self.package)

    def assert_package_error(self, expected):
        status, result = self.check_package()
        self.assertEqual(status, 1, result)
        self.assertFalse(result["ok"])
        self.assertIn(expected, {item["code"] for item in result["errors"]})

    def snapshot(self):
        return {
            str(path.relative_to(self.root)): path.read_bytes()
            for path in self.root.rglob("*") if path.is_file()
        }

    def test_package_stays_scoped_inside_git_repository_and_is_read_only(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        (self.root / "AGENTS.md").write_text("Unrelated malformed instructions", encoding="utf-8")
        before = self.snapshot()
        status, result = self.check_package()
        self.assertEqual(status, 0, result)
        self.assertEqual(result["root"], str(self.package.resolve()))
        self.assertEqual(result["summary"]["markdown_files"], 2)
        self.assertEqual(result["errors"], [])
        self.assertEqual(before, self.snapshot())
        status, output = self.run_cli("validate-skill", "--skill-dir", self.package, structured=False)
        self.assertEqual(status, 0)
        self.assertIn("Skill package validation: PASS", output)
        self.assertEqual(before, self.snapshot())

    def test_missing_entrypoint_is_a_validation_failure(self):
        self.entrypoint.unlink()
        self.assert_package_error("missing-skill-entrypoint")

    def test_broken_reference_in_supporting_document_is_reported(self):
        (self.package / "references/guide.md").write_text(
            "See [missing](missing.md).\n", encoding="utf-8"
        )
        self.assert_package_error("broken-local-link")

    def test_invalid_frontmatter_and_discovery_metadata(self):
        cases = [
            ("# No metadata\n", "invalid-skill-frontmatter"),
            ("---\nname: sample-skill\n---\n", "missing-skill-field"),
            ("---\nname: Sample_Skill\ndescription: Sample\n---\n", "invalid-skill-name"),
            ("---\nname: another-skill\ndescription: Sample\n---\n", "skill-directory-mismatch"),
        ]
        for content, expected in cases:
            with self.subTest(expected=expected):
                self.entrypoint.write_text(content, encoding="utf-8")
                self.assert_package_error(expected)

    def test_invalid_markdown_in_resources_is_reported(self):
        resource = self.package / "references/guide.md"
        for content, expected in [
            (b"```python\nprint('unfinished')\n", "unclosed-fence"),
            (b"# Missing newline", "missing-final-newline"),
            (b"\xff\n", "invalid-utf8"),
        ]:
            with self.subTest(expected=expected):
                resource.write_bytes(content)
                self.assert_package_error(expected)

    def test_warning_does_not_fail_validation(self):
        with self.entrypoint.open("a", encoding="utf-8") as stream:
            stream.write("\n[Nonportable path](/example/path.md)\n")
        status, result = self.check_package()
        self.assertEqual(status, 0, result)
        self.assertIn("absolute-local-link", {item["code"] for item in result["warnings"]})

    def test_assets_are_not_subject_to_repository_baseline_rules(self):
        (self.package / "assets").mkdir()
        (self.package / "assets/AGENTS.md").write_text("# A template\n", encoding="utf-8")
        (self.package / "assets/PLANS.md").write_text("A sample plan.\n", encoding="utf-8")
        status, result = self.check_package()
        self.assertEqual(status, 0, result)
        self.assertEqual(result["summary"]["markdown_files"], 4)

    def test_invalid_package_path_is_runtime_error(self):
        for path in (self.root / "absent", self.entrypoint):
            with self.subTest(path=path):
                status, result = self.run_cli("validate-skill", "--skill-dir", path)
                self.assertEqual(status, 2, result)
                self.assertFalse(result["ok"])
                self.assertIn("runtime_error", result)

    def create_full_harness(self):
        sections = [
            "Project overview", "Before starting", "Autonomy", "ExecPlans",
            "Repository invariants", "Documentation index", "Commands", "Completion",
        ]
        (self.root / "AGENTS.md").write_text(
            "# AGENTS.md\n\nInstructions for this single project.\n\n"
            + "\n".join(f"## {title}\n\nProject-specific guidance.\n" for title in sections),
            encoding="utf-8",
        )
        (self.root / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        (self.root / "PLANS.md").write_bytes(PLANS.read_bytes())
        sections = ["System purpose", "Layers", "Runtime flow", "Data contracts", "Verification"]
        (self.root / "ARCHITECTURE.md").write_text(
            "# ARCHITECTURE.md — Sample project\n\nCurrent architecture.\n\n"
            + "\n".join(f"## {index}. {title}\n\nCurrent facts.\n" for index, title in enumerate(sections, 1)),
            encoding="utf-8",
        )

    def test_full_harness_contract_still_passes_and_inventory_is_read_only(self):
        self.create_full_harness()
        before = self.snapshot()
        status, inventory = self.run_cli("--root", self.root, "inventory", "--project-boundary", ".")
        self.assertEqual(status, 0, inventory)
        self.assertEqual(inventory["plans_template"]["status"], "matches")
        status, result = self.run_cli("--root", self.root, "validate", "--project-boundary", ".")
        self.assertEqual(status, 0, result)
        self.assertEqual(result["summary"]["project_boundaries"], 1)
        self.assertEqual(before, self.snapshot())

    def test_full_harness_still_rejects_plan_drift_and_missing_architecture(self):
        self.create_full_harness()
        (self.root / "PLANS.md").write_text("Customized plan\n", encoding="utf-8")
        (self.root / "ARCHITECTURE.md").unlink()
        status, result = self.run_cli("--root", self.root, "validate", "--project-boundary", ".")
        self.assertEqual(status, 1, result)
        codes = {item["code"] for item in result["errors"]}
        self.assertIn("noncanonical-plans", codes)
        self.assertIn("missing-project-architecture", codes)


if __name__ == "__main__":
    unittest.main()
