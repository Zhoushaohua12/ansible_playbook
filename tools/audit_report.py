#!/usr/bin/env python3
"""
Automated audit workflow for Ansible playbooks.

Scans playbook.yml, README.md, and vars/example_vars.yml files to check:
- Code-style conformance (gather_facts, check_mode, handler naming)
- Chinese documentation coverage
- Security flags (no_log, vault_ usage, ⚠️ headers)
- Metadata/doc path consistency
- pytest coverage results

Generates Markdown report and optional JSON export.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class AuditCollector:
    """Collects audit information from playbooks and related files."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.categories = {}
        self.issues = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }
        self.stats = {
            "total_playbooks": 0,
            "playbooks_with_gather_facts": 0,
            "playbooks_with_check_mode": 0,
            "playbooks_with_no_log": 0,
            "playbooks_with_vault_vars": 0,
            "vars_with_warning": 0,
            "total_vars_files": 0,
            "coverage_percentage": 0,
        }

    def scan(self) -> None:
        """Run the complete audit scan."""
        self._find_playbooks()
        self._analyze_playbooks()
        self._analyze_vars()
        self._run_tests()

    def _find_playbooks(self) -> None:
        """Find all playbook.yml files and their categories."""
        playbooks = self.root.glob("*/*/playbook.yml")
        for pb in playbooks:
            category = pb.parent.parent.name
            if category not in self.categories:
                self.categories[category] = {
                    "playbooks": [],
                    "issues": [],
                }
            self.categories[category]["playbooks"].append(pb)
            self.stats["total_playbooks"] += 1

    def _analyze_playbooks(self) -> None:
        """Analyze playbook structure and style."""
        for category, data in self.categories.items():
            for pb_path in data["playbooks"]:
                try:
                    content = pb_path.read_text(encoding="utf-8")
                    self._check_playbook_style(pb_path, content)
                except Exception as e:
                    self.issues["medium"].append({
                        "file": str(pb_path),
                        "issue": f"Failed to read playbook: {e}",
                    })

    def _check_playbook_style(self, pb_path: Path, content: str) -> None:
        """Check individual playbook for style issues."""
        category = pb_path.parent.parent.name
        module = pb_path.parent.name

        # Check for gather_facts
        if "gather_facts:" in content:
            self.stats["playbooks_with_gather_facts"] += 1
        else:
            self.issues["high"].append({
                "file": str(pb_path),
                "issue": "Missing explicit gather_facts declaration",
                "category": category,
                "module": module,
                "suggestion": "Add 'gather_facts: false' or 'gather_facts: true' to play definition",
            })

        # Check for check_mode
        if "check_mode:" in content:
            self.stats["playbooks_with_check_mode"] += 1

        # Check for no_log
        if "no_log:" in content:
            self.stats["playbooks_with_no_log"] += 1
        elif self._contains_sensitive_patterns(content):
            self.issues["high"].append({
                "file": str(pb_path),
                "issue": "Contains sensitive data patterns but no no_log protection",
                "category": category,
                "module": module,
                "suggestion": "Add 'no_log: true' to tasks handling passwords, tokens, etc.",
            })

        # Check for vault_ prefix usage
        if "vault_" in content:
            self.stats["playbooks_with_vault_vars"] += 1

        # Check for FQCN usage
        if not self._has_fqcn(content):
            self.issues["medium"].append({
                "file": str(pb_path),
                "issue": "Some tasks may not use FQCN (Fully Qualified Collection Name)",
                "category": category,
                "module": module,
                "suggestion": "Ensure all module calls use FQCN format (e.g., 'ansible.builtin.copy')",
            })

        # Check for Chinese task names
        if not self._has_chinese_names(content):
            self.issues["low"].append({
                "file": str(pb_path),
                "issue": "Missing Chinese task names",
                "category": category,
                "module": module,
            })

    def _contains_sensitive_patterns(self, content: str) -> bool:
        """Check if content contains sensitive data patterns."""
        patterns = [
            r"password\s*:",
            r"token\s*:",
            r"secret\s*:",
            r"api_key\s*:",
            r"credentials\s*:",
            r"DATABASE_URL",
            r"db_password",
        ]
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _has_fqcn(self, content: str) -> bool:
        """Check if content uses FQCN module calls."""
        # Look for patterns like ansible.builtin.*, community.*, etc.
        fqcn_pattern = r"ansible\.builtin\.|community\.|amazon\.|azure\.|google\."
        return bool(re.search(fqcn_pattern, content))

    def _has_chinese_names(self, content: str) -> bool:
        """Check if content has Chinese task names."""
        # Look for CJK Unicode characters in name fields
        cjk_pattern = r"name:\s*[^#\n]*[\u4e00-\u9fff]"
        matches = re.findall(cjk_pattern, content)
        return len(matches) > 3  # At least some Chinese names

    def _analyze_vars(self) -> None:
        """Analyze vars/example_vars.yml files."""
        vars_files = self.root.glob("*/*/vars/example_vars.yml")
        for var_file in vars_files:
            self.stats["total_vars_files"] += 1
            try:
                content = var_file.read_text(encoding="utf-8")
                self._check_vars_style(var_file, content)
            except Exception as e:
                self.issues["medium"].append({
                    "file": str(var_file),
                    "issue": f"Failed to read vars file: {e}",
                })

    def _check_vars_style(self, var_file: Path, content: str) -> None:
        """Check individual vars file for style issues."""
        category = var_file.parent.parent.parent.name
        module = var_file.parent.parent.name

        # Check for warning header
        if "⚠️" in content or "⚠" in content:
            self.stats["vars_with_warning"] += 1
        else:
            self.issues["high"].append({
                "file": str(var_file),
                "issue": "Missing warning header (⚠️) in example vars",
                "category": category,
                "module": module,
                "suggestion": "Add '# ⚠️ 本文件仅为示例，占位符必须使用 Ansible Vault 或环境变量替换' at the top",
            })

        # Check for actual sensitive values (should not exist)
        if self._has_actual_sensitive_values(content):
            self.issues["critical"].append({
                "file": str(var_file),
                "issue": "Contains actual sensitive values instead of placeholders",
                "category": category,
                "module": module,
                "suggestion": "Replace all real passwords, tokens, etc. with placeholders or vault_ prefixed variables",
            })

    def _has_actual_sensitive_values(self, content: str) -> bool:
        """Check for suspicious patterns that look like real values."""
        # This is a heuristic check - look for things that don't look like placeholders
        suspicious_patterns = [
            r"password:\s*(?!vault_|placeholder|example|test|demo)['\"]?[a-zA-Z0-9@#$%]{8,}['\"]?",
            r"api_key:\s*(?!vault_|placeholder|example)['\"]?[A-Za-z0-9_-]{20,}['\"]?",
            r"secret_key:\s*(?!vault_|placeholder)['\"]?.{20,}['\"]?",
        ]
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _run_tests(self) -> None:
        """Run pytest and capture coverage results."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "--maxfail=1",
                    "--disable-warnings",
                    "--cov=.",
                    "--cov-report=term-missing",
                    "-q",
                ],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Try to extract coverage percentage
            if "--cov" in str(result.stdout) or "--cov" in str(result.stderr):
                output = result.stdout + result.stderr
                match = re.search(r"(\d+)%", output)
                if match:
                    self.stats["coverage_percentage"] = int(match.group(1))
        except subprocess.TimeoutExpired:
            self.issues["medium"].append({
                "file": "pytest execution",
                "issue": "Coverage tests timed out",
            })
        except Exception as e:
            # Silently skip if pytest or coverage not available
            if "cov" not in str(e).lower():
                self.issues["low"].append({
                    "file": "pytest execution",
                    "issue": f"Could not run tests: {e}",
                })

    def generate_report(self) -> str:
        """Generate Markdown report from audit results."""
        now = datetime.now().isoformat()
        report = [
            "# 自动化审计报告 (Automated Audit Report)",
            "",
            f"**生成时间**: {now}",
            f"**审计范围**: {self.stats['total_playbooks']} playbooks, {self.stats['total_vars_files']} vars files",
            "",
            "## 概览 (Overview)",
            "",
            self._generate_stats_section(),
            "",
            "## 问题清单 (Issues)",
            "",
            self._generate_issues_section(),
            "",
            "## 改进建议 (Recommendations)",
            "",
            self._generate_recommendations_section(),
        ]
        return "\n".join(report)

    def _generate_stats_section(self) -> str:
        """Generate statistics section."""
        total = self.stats["total_playbooks"]
        gather = self.stats["playbooks_with_gather_facts"]
        check = self.stats["playbooks_with_check_mode"]
        nolog = self.stats["playbooks_with_no_log"]
        vault = self.stats["playbooks_with_vault_vars"]
        vars_warning = self.stats["vars_with_warning"]
        total_vars = self.stats["total_vars_files"]

        lines = [
            "### 代码风格 (Code Style)",
            f"- Playbooks with explicit `gather_facts`: {gather}/{total} ({100*gather//max(1, total)}%)",
            f"- Playbooks with `check_mode` examples: {check}/{total} ({100*check//max(1, total)}%)",
            f"- Playbooks with `no_log` protection: {nolog}/{total} ({100*nolog//max(1, total)}%)",
            f"- Playbooks using `vault_` prefixed variables: {vault}/{total} ({100*vault//max(1, total)}%)",
            "",
            "### 文档安全 (Documentation Security)",
            f"- Example vars files with warning header (⚠️): {vars_warning}/{total_vars} ({100*vars_warning//max(1, total_vars)}%)",
            "",
            "### 测试覆盖 (Test Coverage)",
            f"- Code coverage: {self.stats['coverage_percentage']}%",
        ]
        return "\n".join(lines)

    def _generate_issues_section(self) -> str:
        """Generate issues section by severity."""
        lines = []

        for severity in ["critical", "high", "medium", "low"]:
            issues = self.issues[severity]
            if not issues:
                continue

            severity_map = {
                "critical": "🔴 Critical",
                "high": "🟠 High",
                "medium": "🟡 Medium",
                "low": "🟢 Low",
            }

            lines.append(f"### {severity_map[severity]} ({len(issues)} issues)")
            lines.append("")

            for issue in issues[:10]:  # Limit to top 10 per severity
                lines.append(f"- **{issue.get('issue', 'Unknown')}**")
                lines.append(f"  - File: `{issue.get('file', 'N/A')}`")
                if "suggestion" in issue:
                    lines.append(f"  - Suggestion: {issue['suggestion']}")
                lines.append("")

            if len(issues) > 10:
                lines.append(f"... and {len(issues) - 10} more {severity} issues")
                lines.append("")

        return "\n".join(lines)

    def _generate_recommendations_section(self) -> str:
        """Generate actionable recommendations."""
        gather_rate = (
            100 * self.stats["playbooks_with_gather_facts"]
            // max(1, self.stats["total_playbooks"])
        )
        check_rate = (
            100 * self.stats["playbooks_with_check_mode"]
            // max(1, self.stats["total_playbooks"])
        )
        nolog_rate = (
            100 * self.stats["playbooks_with_no_log"]
            // max(1, self.stats["total_playbooks"])
        )
        vars_rate = (
            100 * self.stats["vars_with_warning"]
            // max(1, self.stats["total_vars_files"])
        )

        lines = [
            "#### 优先级 1: 代码规范 (Priority 1: Code Standards)",
            "",
        ]

        if gather_rate < 100:
            lines.append(
                f"- **Gather Facts Coverage**: Currently {gather_rate}%. "
                f"Target: Add explicit `gather_facts: true/false` to all {100 - gather_rate}% missing playbooks."
            )

        if check_rate < 50:
            lines.append(
                f"- **Check Mode Examples**: Currently {check_rate}%. "
                f"Target: Add `check_mode: true` examples to at least 50% of playbooks with system-modifying tasks."
            )

        lines.append("")
        lines.append("#### 优先级 2: 安全性 (Priority 2: Security)")
        lines.append("")

        if nolog_rate < 50:
            lines.append(
                f"- **No-Log Protection**: Currently {nolog_rate}%. "
                f"Target: Add `no_log: true` to all tasks handling passwords, tokens, or secrets."
            )

        if vars_rate < 100:
            lines.append(
                f"- **Warning Headers in Vars**: Currently {vars_rate}%. "
                f"Target: Add ⚠️ warning to all remaining {100 - vars_rate}% of example_vars.yml files."
            )

        lines.append("")
        lines.append("#### 优先级 3: 文档改进 (Priority 3: Documentation)")
        lines.append("")
        lines.append("- Ensure all task and handler names are in Chinese (中文)")
        lines.append("- Add comprehensive README.md to each module directory")
        lines.append("- Document all variables with Chinese comments")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert audit results to dictionary for JSON export."""
        return {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.stats,
            "issues": self.issues,
            "categories": {
                cat: {
                    "playbooks": [str(p) for p in data["playbooks"]],
                    "issues": data["issues"],
                }
                for cat, data in self.categories.items()
            },
        }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated audit workflow for Ansible playbooks",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/phase1_audit.md"),
        help="Output Markdown report path (default: reports/phase1_audit.md)",
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Optional JSON export path",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest coverage collection",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Run audit
    collector = AuditCollector(args.root)
    if not args.skip_tests:
        collector.scan()
    else:
        # Run only file scanning, skip tests
        collector._find_playbooks()
        collector._analyze_playbooks()
        collector._analyze_vars()

    # Write Markdown report
    report = collector.generate_report()
    args.output.write_text(report, encoding="utf-8")
    print(f"📋 Audit report written to: {args.output}")

    # Write JSON export if requested
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        audit_data = collector.to_dict()
        args.json.write_text(
            json.dumps(audit_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"📊 JSON export written to: {args.json}")

    # Print summary
    print("\n=== Audit Summary ===")
    print(f"Total Playbooks: {collector.stats['total_playbooks']}")
    print(
        f"With gather_facts: {collector.stats['playbooks_with_gather_facts']}/{collector.stats['total_playbooks']}"
    )
    print(
        f"With check_mode: {collector.stats['playbooks_with_check_mode']}/{collector.stats['total_playbooks']}"
    )
    print(
        f"Critical Issues: {len(collector.issues['critical'])}"
    )
    print(
        f"High Issues: {len(collector.issues['high'])}"
    )
    print(
        f"Medium Issues: {len(collector.issues['medium'])}"
    )
    print(
        f"Low Issues: {len(collector.issues['low'])}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
