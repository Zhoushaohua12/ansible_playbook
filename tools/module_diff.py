#!/usr/bin/env python3
"""Module diff analyzer for Ansible modules.

This script:
1. Executes ansible-doc -l to get available modules
2. Compares with modules declared in metadata/modules.yaml
3. Compares with actual category directories
4. Produces reports showing coverage gaps, duplicates, and inconsistencies
5. Groups modules by category and priority (P1/P2/P3)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIORITIES = ROOT / "metadata" / "module_priorities.yml"
DEFAULT_MODULES = ROOT / "metadata" / "modules.yaml"
DEFAULT_JSON_OUTPUT = ROOT / "reports" / "module_diff.json"
DEFAULT_MD_OUTPUT = ROOT / "reports" / "module_diff.md"
DEFAULT_CACHE = ROOT / ".cache" / "ansible_doc_cache.json"

CATEGORY_EXCLUDES = {
    ".git",
    ".github",
    ".pytest_cache",
    ".mypy_cache",
    "metadata",
    "tests",
    "venv",
    "collections",
    "docs",
    "reports",
    "tools",
    "__pycache__",
}


@dataclass
class ModuleInfo:
    """Information about an Ansible module."""

    name: str
    collection: str = ""
    description: str = ""
    category: str = ""
    priority: str = "P2"
    
    @property
    def full_name(self) -> str:
        """Return fully qualified module name."""
        return f"{self.collection}.{self.name}" if self.collection else self.name


@dataclass
class ModuleCoverage:
    """Coverage information for a module."""

    module: str
    status: str  # covered, missing, undocumented
    category: str
    priority: str
    in_ansible_doc: bool = False
    in_metadata: bool = False
    in_filesystem: bool = False
    notes: str = ""


@dataclass
class CategoryStats:
    """Statistics for a category."""

    category: str
    total_ansible_doc: int = 0
    total_covered: int = 0
    total_missing: int = 0
    total_undocumented: int = 0
    coverage_percentage: float = 0.0
    priority_breakdown: Dict[str, int] = field(default_factory=dict)


@dataclass
class DiffReport:
    """Complete diff report."""

    generated_at: str
    total_ansible_modules: int
    total_covered: int
    total_missing: int
    total_undocumented: int
    overall_coverage: float
    categories: Dict[str, CategoryStats]
    coverage_details: List[ModuleCoverage]
    duplicates: List[Dict[str, Any]]
    inconsistencies: List[Dict[str, Any]]


class ModuleDiffAnalyzer:
    """Analyzes differences between ansible-doc, metadata, and filesystem."""

    def __init__(
        self,
        priorities_path: Path,
        modules_path: Path,
        cache_path: Path,
        root: Path,
    ):
        self.priorities_path = priorities_path
        self.modules_path = modules_path
        self.cache_path = cache_path
        self.root = root
        self.priorities_config: Dict[str, Any] = {}
        self.modules_metadata: Dict[str, Any] = {}
        self.ansible_modules: Dict[str, ModuleInfo] = {}
        self.covered_modules: Dict[str, Set[str]] = defaultdict(set)
        self.filesystem_modules: Dict[str, Set[str]] = defaultdict(set)

    def load_priorities(self) -> None:
        """Load module priorities configuration."""
        if not self.priorities_path.exists():
            print(f"Warning: Priorities file not found: {self.priorities_path}")
            self.priorities_config = {"default_priority": "P2", "modules": {}, "category_priorities": {}}
            return
        
        with open(self.priorities_path, encoding="utf-8") as f:
            self.priorities_config = yaml.safe_load(f) or {}

    def load_metadata(self) -> None:
        """Load modules metadata from modules.yaml."""
        if not self.modules_path.exists():
            print(f"Warning: Modules metadata not found: {self.modules_path}")
            self.modules_metadata = {}
            return
        
        with open(self.modules_path, encoding="utf-8") as f:
            self.modules_metadata = yaml.safe_load(f) or {}
        
        # Extract covered modules by category
        for category, data in self.modules_metadata.items():
            if isinstance(data, dict) and "topics" in data:
                for topic in data["topics"]:
                    if isinstance(topic, dict) and "dependencies" in topic:
                        for dep in topic["dependencies"]:
                            self.covered_modules[category].add(dep)

    def load_filesystem_modules(self) -> None:
        """Scan filesystem for module directories."""
        for item in self.root.iterdir():
            if not item.is_dir() or item.name in CATEGORY_EXCLUDES:
                continue
            
            category = item.name
            # Look for subdirectories that represent modules
            for subdir in item.iterdir():
                if subdir.is_dir() and not subdir.name.startswith("_"):
                    # Check if it has README.md or playbook.yml
                    if (subdir / "README.md").exists() or (subdir / "playbook.yml").exists():
                        self.filesystem_modules[category].add(subdir.name)

    def fetch_ansible_doc_list(self, use_cache: bool = True) -> Dict[str, ModuleInfo]:
        """Fetch list of modules from ansible-doc -l."""
        if use_cache and self.cache_path.exists():
            print(f"Loading ansible-doc cache from {self.cache_path}")
            with open(self.cache_path, encoding="utf-8") as f:
                cached = json.load(f)
                return {
                    name: ModuleInfo(**data)
                    for name, data in cached.items()
                }
        
        modules = self._execute_ansible_doc()
        
        # Save to cache
        if modules:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(
                    {name: asdict(info) for name, info in modules.items()},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            print(f"Saved ansible-doc cache to {self.cache_path}")
        
        return modules

    def _execute_ansible_doc(self) -> Dict[str, ModuleInfo]:
        """Execute ansible-doc -l and parse output."""
        try:
            print("Executing ansible-doc -l (this may take a moment)...")
            result = subprocess.run(
                ["ansible-doc", "-l", "-t", "module"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            if result.returncode != 0:
                print(f"Warning: ansible-doc failed with code {result.returncode}")
                print(f"stderr: {result.stderr}")
                return self._fallback_module_list()
            
            return self._parse_ansible_doc_output(result.stdout)
        
        except FileNotFoundError:
            print("Warning: ansible-doc command not found, using fallback")
            return self._fallback_module_list()
        except subprocess.TimeoutExpired:
            print("Warning: ansible-doc timed out, using fallback")
            return self._fallback_module_list()
        except Exception as e:
            print(f"Warning: Error executing ansible-doc: {e}")
            return self._fallback_module_list()

    def _parse_ansible_doc_output(self, output: str) -> Dict[str, ModuleInfo]:
        """Parse ansible-doc -l output."""
        modules = {}
        # Pattern: module_name    Description text
        pattern = re.compile(r"^(\S+)\s+(.*)$")
        
        for line in output.strip().split("\n"):
            match = pattern.match(line)
            if match:
                full_name = match.group(1)
                description = match.group(2).strip()
                
                # Split into collection and module name
                parts = full_name.split(".")
                if len(parts) >= 3:
                    collection = ".".join(parts[:-1])
                    name = parts[-1]
                else:
                    collection = ""
                    name = full_name
                
                modules[full_name] = ModuleInfo(
                    name=name,
                    collection=collection,
                    description=description,
                )
        
        return modules

    def _fallback_module_list(self) -> Dict[str, ModuleInfo]:
        """Return a fallback list of common modules when ansible-doc is unavailable."""
        print("Using fallback module list (ansible-doc unavailable)")
        common_modules = [
            "ansible.builtin.copy",
            "ansible.builtin.template",
            "ansible.builtin.file",
            "ansible.builtin.lineinfile",
            "ansible.builtin.stat",
            "ansible.builtin.find",
            "ansible.builtin.fetch",
            "ansible.builtin.assemble",
            "ansible.builtin.blockinfile",
            "ansible.builtin.replace",
            "ansible.builtin.unarchive",
            "ansible.builtin.archive",
            "ansible.builtin.service",
            "ansible.builtin.systemd",
            "ansible.builtin.user",
            "ansible.builtin.group",
            "ansible.builtin.package",
            "ansible.builtin.apt",
            "ansible.builtin.yum",
            "ansible.builtin.dnf",
            "ansible.builtin.command",
            "ansible.builtin.shell",
            "ansible.builtin.script",
            "ansible.builtin.raw",
            "ansible.builtin.wait_for",
            "ansible.builtin.uri",
            "ansible.builtin.get_url",
            "ansible.builtin.ping",
            "ansible.builtin.debug",
            "ansible.builtin.set_fact",
            "ansible.builtin.include_tasks",
            "ansible.builtin.import_tasks",
            "ansible.posix.synchronize",
            "ansible.posix.firewalld",
            "ansible.posix.mount",
            "ansible.posix.sysctl",
        ]
        
        modules = {}
        for full_name in common_modules:
            parts = full_name.split(".")
            collection = ".".join(parts[:-1])
            name = parts[-1]
            modules[full_name] = ModuleInfo(
                name=name,
                collection=collection,
                description="(fallback list - ansible-doc unavailable)",
            )
        
        return modules

    def get_module_priority(self, module_name: str, category: str = "") -> str:
        """Get priority for a module."""
        # Check explicit module priority
        if module_name in self.priorities_config.get("modules", {}):
            return self.priorities_config["modules"][module_name]
        
        # Check category priority
        if category and category in self.priorities_config.get("category_priorities", {}):
            return self.priorities_config["category_priorities"][category]
        
        # Return default
        return self.priorities_config.get("default_priority", "P2")

    def infer_module_category(self, module_name: str) -> str:
        """Infer category from module name or covered modules."""
        # Check if module is in any category's covered modules
        for category, modules in self.covered_modules.items():
            if module_name in modules:
                return category
        
        # Try to infer from module name
        name_lower = module_name.lower()
        if "file" in name_lower or "copy" in name_lower or "template" in name_lower:
            return "files"
        elif "user" in name_lower or "group" in name_lower or "service" in name_lower:
            return "system"
        elif "apt" in name_lower or "yum" in name_lower or "package" in name_lower:
            return "applications"
        elif "shell" in name_lower or "command" in name_lower or "script" in name_lower:
            return "commands"
        elif "firewall" in name_lower or "port" in name_lower or "wait" in name_lower:
            return "network"
        elif "mysql" in name_lower or "postgresql" in name_lower or "mongodb" in name_lower:
            return "database"
        elif "ec2" in name_lower or "aws" in name_lower or "azure" in name_lower or "gcp" in name_lower:
            return "cloud"
        elif "docker" in name_lower or "kubernetes" in name_lower or "k8s" in name_lower:
            return "applications"
        elif "lvol" in name_lower or "filesystem" in name_lower or "mount" in name_lower:
            return "storage"
        elif "virt" in name_lower or "vmware" in name_lower or "qemu" in name_lower:
            return "virtualization"
        elif "apache" in name_lower or "nginx" in name_lower or "uri" in name_lower:
            return "web"
        
        return "other"

    def analyze(self) -> DiffReport:
        """Perform complete analysis."""
        print("\n=== Module Diff Analysis ===\n")
        
        # Load all data
        self.load_priorities()
        self.load_metadata()
        self.load_filesystem_modules()
        self.ansible_modules = self.fetch_ansible_doc_list()
        
        # Analyze coverage
        coverage_details: List[ModuleCoverage] = []
        all_modules = set(self.ansible_modules.keys())
        
        # Add all modules from metadata
        for category_modules in self.covered_modules.values():
            all_modules.update(category_modules)
        
        # Analyze each module
        for module_name in sorted(all_modules):
            category = self.infer_module_category(module_name)
            priority = self.get_module_priority(module_name, category)
            
            in_ansible_doc = module_name in self.ansible_modules
            in_metadata = any(module_name in mods for mods in self.covered_modules.values())
            
            # Check filesystem - try to match module name
            in_filesystem = False
            for cat_modules in self.filesystem_modules.values():
                # Extract the module short name for matching
                short_name = module_name.split(".")[-1]
                if short_name in cat_modules:
                    in_filesystem = True
                    break
            
            # Determine status
            if in_metadata and in_filesystem:
                status = "covered"
            elif in_ansible_doc and not in_metadata:
                status = "missing"
            elif in_metadata and not in_ansible_doc:
                status = "undocumented"
            else:
                status = "unknown"
            
            coverage = ModuleCoverage(
                module=module_name,
                status=status,
                category=category,
                priority=priority,
                in_ansible_doc=in_ansible_doc,
                in_metadata=in_metadata,
                in_filesystem=in_filesystem,
            )
            coverage_details.append(coverage)
        
        # Calculate statistics
        category_stats: Dict[str, CategoryStats] = {}
        for coverage in coverage_details:
            if coverage.category not in category_stats:
                category_stats[coverage.category] = CategoryStats(
                    category=coverage.category,
                    priority_breakdown={},
                )
            
            stats = category_stats[coverage.category]
            
            if coverage.in_ansible_doc:
                stats.total_ansible_doc += 1
            
            if coverage.status == "covered":
                stats.total_covered += 1
            elif coverage.status == "missing":
                stats.total_missing += 1
            elif coverage.status == "undocumented":
                stats.total_undocumented += 1
            
            # Priority breakdown
            if coverage.priority not in stats.priority_breakdown:
                stats.priority_breakdown[coverage.priority] = 0
            stats.priority_breakdown[coverage.priority] += 1
        
        # Calculate coverage percentages
        for stats in category_stats.values():
            if stats.total_ansible_doc > 0:
                stats.coverage_percentage = (stats.total_covered / stats.total_ansible_doc) * 100
        
        # Find duplicates (modules covered in multiple categories)
        duplicates = self._find_duplicates(coverage_details)
        
        # Find inconsistencies (in metadata but not in filesystem, or vice versa)
        inconsistencies = self._find_inconsistencies(coverage_details)
        
        # Overall statistics
        total_ansible = len([c for c in coverage_details if c.in_ansible_doc])
        total_covered = len([c for c in coverage_details if c.status == "covered"])
        total_missing = len([c for c in coverage_details if c.status == "missing"])
        total_undocumented = len([c for c in coverage_details if c.status == "undocumented"])
        overall_coverage = (total_covered / total_ansible * 100) if total_ansible > 0 else 0
        
        report = DiffReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_ansible_modules=total_ansible,
            total_covered=total_covered,
            total_missing=total_missing,
            total_undocumented=total_undocumented,
            overall_coverage=overall_coverage,
            categories=category_stats,
            coverage_details=coverage_details,
            duplicates=duplicates,
            inconsistencies=inconsistencies,
        )
        
        return report

    def _find_duplicates(self, coverage_details: List[ModuleCoverage]) -> List[Dict[str, Any]]:
        """Find modules that appear in multiple categories."""
        module_categories: Dict[str, List[str]] = defaultdict(list)
        
        for coverage in coverage_details:
            if coverage.in_metadata:
                module_categories[coverage.module].append(coverage.category)
        
        duplicates = []
        for module, categories in module_categories.items():
            if len(categories) > 1:
                duplicates.append({
                    "module": module,
                    "categories": categories,
                    "count": len(categories),
                })
        
        return sorted(duplicates, key=lambda x: x["count"], reverse=True)

    def _find_inconsistencies(self, coverage_details: List[ModuleCoverage]) -> List[Dict[str, Any]]:
        """Find inconsistencies between metadata and filesystem."""
        inconsistencies = []
        
        for coverage in coverage_details:
            if coverage.in_metadata and not coverage.in_filesystem:
                inconsistencies.append({
                    "module": coverage.module,
                    "category": coverage.category,
                    "issue": "in_metadata_but_not_filesystem",
                    "description": "Module is declared in metadata but directory not found",
                })
            elif coverage.in_filesystem and not coverage.in_metadata:
                inconsistencies.append({
                    "module": coverage.module,
                    "category": coverage.category,
                    "issue": "in_filesystem_but_not_metadata",
                    "description": "Module directory exists but not in metadata",
                })
        
        return inconsistencies

    def write_json_report(self, report: DiffReport, output_path: Path) -> None:
        """Write JSON report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict for JSON serialization
        report_dict = asdict(report)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        print(f"\nJSON report written to: {output_path}")

    def write_markdown_report(self, report: DiffReport, output_path: Path) -> None:
        """Write Markdown report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [
            "# Ansible Module Coverage Report",
            "",
            f"Generated: {report.generated_at}",
            "",
            "## Overall Statistics",
            "",
            f"- **Total Ansible Modules**: {report.total_ansible_modules}",
            f"- **Covered Modules**: {report.total_covered}",
            f"- **Missing Modules**: {report.total_missing}",
            f"- **Undocumented Modules**: {report.total_undocumented}",
            f"- **Overall Coverage**: {report.overall_coverage:.1f}%",
            "",
        ]
        
        # Category statistics
        lines.extend([
            "## Category Coverage",
            "",
            "| Category | Total | Covered | Missing | Coverage % |",
            "|----------|-------|---------|---------|------------|",
        ])
        
        for category in sorted(report.categories.keys()):
            stats = report.categories[category]
            lines.append(
                f"| {category} | {stats.total_ansible_doc} | {stats.total_covered} | "
                f"{stats.total_missing} | {stats.coverage_percentage:.1f}% |"
            )
        
        lines.extend(["", ""])
        
        # Priority breakdown
        lines.extend([
            "## Priority Breakdown",
            "",
        ])
        
        priority_totals = {"P1": 0, "P2": 0, "P3": 0}
        for stats in report.categories.values():
            for priority, count in stats.priority_breakdown.items():
                if priority in priority_totals:
                    priority_totals[priority] += count
        
        lines.extend([
            f"- **P1 (Critical/High)**: {priority_totals['P1']} modules",
            f"- **P2 (Medium)**: {priority_totals['P2']} modules",
            f"- **P3 (Low)**: {priority_totals['P3']} modules",
            "",
        ])
        
        # Missing modules by priority
        for priority in ["P1", "P2", "P3"]:
            missing = [c for c in report.coverage_details if c.status == "missing" and c.priority == priority]
            if missing:
                lines.extend([
                    f"## Missing {priority} Modules",
                    "",
                    "| Module | Category | Description |",
                    "|--------|----------|-------------|",
                ])
                
                for coverage in sorted(missing, key=lambda x: (x.category, x.module)):
                    desc = ""
                    if coverage.module in self.ansible_modules:
                        desc = self.ansible_modules[coverage.module].description[:60]
                    lines.append(f"| {coverage.module} | {coverage.category} | {desc} |")
                
                lines.extend(["", ""])
        
        # Duplicates
        if report.duplicates:
            lines.extend([
                "## Duplicates",
                "",
                "Modules that appear in multiple categories:",
                "",
                "| Module | Categories | Count |",
                "|--------|------------|-------|",
            ])
            
            for dup in report.duplicates[:20]:  # Top 20
                categories = ", ".join(dup["categories"])
                lines.append(f"| {dup['module']} | {categories} | {dup['count']} |")
            
            lines.extend(["", ""])
        
        # Inconsistencies
        if report.inconsistencies:
            lines.extend([
                "## Inconsistencies",
                "",
                "Discrepancies between metadata and filesystem:",
                "",
                "| Module | Category | Issue |",
                "|--------|----------|-------|",
            ])
            
            for incons in report.inconsistencies[:30]:  # Top 30
                lines.append(
                    f"| {incons['module']} | {incons['category']} | {incons['description']} |"
                )
            
            lines.extend(["", ""])
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"Markdown report written to: {output_path}")

    def print_summary(self, report: DiffReport, priority_filter: Optional[str] = None) -> None:
        """Print summary to console."""
        print("\n" + "=" * 70)
        print("ANSIBLE MODULE COVERAGE SUMMARY")
        print("=" * 70)
        print(f"\nTotal Ansible Modules: {report.total_ansible_modules}")
        print(f"Covered: {report.total_covered}")
        print(f"Missing: {report.total_missing}")
        print(f"Overall Coverage: {report.overall_coverage:.1f}%")
        
        if priority_filter:
            missing = [
                c for c in report.coverage_details
                if c.status == "missing" and c.priority == priority_filter
            ]
            print(f"\n{priority_filter} Missing Modules: {len(missing)}")
            
            if missing:
                print(f"\nTop {min(10, len(missing))} {priority_filter} missing modules:")
                for i, coverage in enumerate(sorted(missing, key=lambda x: x.module)[:10], 1):
                    print(f"  {i}. {coverage.module} ({coverage.category})")
        else:
            print("\nMissing by Priority:")
            for priority in ["P1", "P2", "P3"]:
                count = len([c for c in report.coverage_details if c.status == "missing" and c.priority == priority])
                print(f"  {priority}: {count} modules")
        
        print("\n" + "=" * 70)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze Ansible module coverage gaps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate reports with cached ansible-doc data
  %(prog)s

  # Refresh ansible-doc cache and generate reports
  %(prog)s --refresh-cache

  # Filter by priority
  %(prog)s --priority P1

  # Show summary only
  %(prog)s --summary

  # Custom output paths
  %(prog)s --json-output custom/path.json --md-output custom/path.md
        """,
    )
    
    parser.add_argument(
        "--priorities",
        type=Path,
        default=DEFAULT_PRIORITIES,
        help=f"Path to module priorities config (default: {DEFAULT_PRIORITIES})",
    )
    parser.add_argument(
        "--modules",
        type=Path,
        default=DEFAULT_MODULES,
        help=f"Path to modules metadata (default: {DEFAULT_MODULES})",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=DEFAULT_CACHE,
        help=f"Path to ansible-doc cache (default: {DEFAULT_CACHE})",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Refresh ansible-doc cache instead of using cached data",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=DEFAULT_JSON_OUTPUT,
        help=f"Path to JSON output (default: {DEFAULT_JSON_OUTPUT})",
    )
    parser.add_argument(
        "--md-output",
        type=Path,
        default=DEFAULT_MD_OUTPUT,
        help=f"Path to Markdown output (default: {DEFAULT_MD_OUTPUT})",
    )
    parser.add_argument(
        "--priority",
        choices=["P1", "P2", "P3"],
        help="Filter by priority level",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary table only (skip file generation)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help=f"Project root directory (default: {ROOT})",
    )
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = ModuleDiffAnalyzer(
        priorities_path=args.priorities,
        modules_path=args.modules,
        cache_path=args.cache,
        root=args.root,
    )
    
    # Refresh cache if requested
    if args.refresh_cache and args.cache.exists():
        print(f"Removing cache: {args.cache}")
        args.cache.unlink()
    
    # Analyze
    report = analyzer.analyze()
    
    # Print summary
    analyzer.print_summary(report, priority_filter=args.priority)
    
    # Generate reports unless summary-only
    if not args.summary:
        analyzer.write_json_report(report, args.json_output)
        analyzer.write_markdown_report(report, args.md_output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
