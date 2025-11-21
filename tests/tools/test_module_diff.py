"""Unit tests for module_diff.py with mocked ansible-doc output."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from tools import module_diff


@pytest.fixture
def sample_priorities(tmp_path: Path) -> Path:
    """Create sample priorities configuration."""
    priorities_file = tmp_path / "priorities.yml"
    priorities = {
        "default_priority": "P2",
        "modules": {
            "ansible.builtin.copy": "P1",
            "ansible.builtin.template": "P1",
            "ansible.builtin.file": "P1",
            "ansible.builtin.user": "P1",
            "ansible.builtin.service": "P1",
            "ansible.builtin.lineinfile": "P2",
            "ansible.builtin.stat": "P2",
            "ansible.builtin.find": "P2",
            "ansible.builtin.raw": "P3",
        },
        "category_priorities": {
            "files": "P1",
            "system": "P1",
            "applications": "P2",
            "network": "P2",
        },
    }
    with open(priorities_file, "w", encoding="utf-8") as f:
        yaml.dump(priorities, f)
    return priorities_file


@pytest.fixture
def sample_modules_metadata(tmp_path: Path) -> Path:
    """Create sample modules metadata."""
    metadata_file = tmp_path / "modules.yaml"
    metadata = {
        "files": {
            "key": "files",
            "title": "文件操作模块",
            "topics": [
                {
                    "id": "copy",
                    "name": "Copy 模块",
                    "dependencies": ["ansible.builtin.copy", "ansible.builtin.debug"],
                },
                {
                    "id": "template",
                    "name": "Template 模块",
                    "dependencies": ["ansible.builtin.template"],
                },
            ],
        },
        "system": {
            "key": "system",
            "title": "系统管理模块",
            "topics": [
                {
                    "id": "user",
                    "name": "User 模块",
                    "dependencies": ["ansible.builtin.user", "ansible.builtin.group"],
                },
            ],
        },
    }
    with open(metadata_file, "w", encoding="utf-8") as f:
        yaml.dump(metadata, f)
    return metadata_file


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    """Create sample repository structure."""
    root = tmp_path / "repo"
    
    # Create files category with modules
    files_dir = root / "files"
    (files_dir / "copy").mkdir(parents=True)
    (files_dir / "copy" / "README.md").write_text("# Copy module", encoding="utf-8")
    (files_dir / "copy" / "playbook.yml").write_text("---\n", encoding="utf-8")
    
    (files_dir / "template").mkdir(parents=True)
    (files_dir / "template" / "README.md").write_text("# Template module", encoding="utf-8")
    
    (files_dir / "file").mkdir(parents=True)
    (files_dir / "file" / "README.md").write_text("# File module", encoding="utf-8")
    
    # Create system category
    system_dir = root / "system"
    (system_dir / "user").mkdir(parents=True)
    (system_dir / "user" / "README.md").write_text("# User module", encoding="utf-8")
    
    (system_dir / "service").mkdir(parents=True)
    (system_dir / "service" / "README.md").write_text("# Service module", encoding="utf-8")
    
    return root


@pytest.fixture
def mocked_ansible_doc_output() -> str:
    """Sample ansible-doc -l output."""
    return """ansible.builtin.copy                            Copy files to remote locations
ansible.builtin.template                        Template a file out to a target host
ansible.builtin.file                            Manage files and file properties
ansible.builtin.lineinfile                      Manage lines in text files
ansible.builtin.stat                            Retrieve file or file system status
ansible.builtin.find                            Return a list of files based on specific criteria
ansible.builtin.user                            Manage user accounts
ansible.builtin.group                           Add or remove groups
ansible.builtin.service                         Manage services
ansible.builtin.systemd                         Manage systemd units
ansible.builtin.command                         Execute commands on targets
ansible.builtin.shell                           Execute shell commands on targets
ansible.builtin.raw                             Executes a low-down and dirty command
ansible.builtin.debug                           Print statements during execution
ansible.builtin.apt                             Manages apt-packages
ansible.builtin.yum                             Manages packages with yum
community.general.apache2_module                Enables or disables Apache modules
community.docker.docker_container               Manage docker containers
"""


def test_parse_ansible_doc_output(mocked_ansible_doc_output: str) -> None:
    """Test parsing ansible-doc output."""
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=Path("dummy"),
        modules_path=Path("dummy"),
        cache_path=Path("dummy"),
        root=Path("dummy"),
    )
    
    modules = analyzer._parse_ansible_doc_output(mocked_ansible_doc_output)
    
    assert len(modules) > 0
    assert "ansible.builtin.copy" in modules
    assert modules["ansible.builtin.copy"].name == "copy"
    assert modules["ansible.builtin.copy"].collection == "ansible.builtin"
    assert "Copy files" in modules["ansible.builtin.copy"].description
    
    assert "community.docker.docker_container" in modules
    assert modules["community.docker.docker_container"].collection == "community.docker"


def test_fallback_module_list() -> None:
    """Test fallback module list when ansible-doc unavailable."""
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=Path("dummy"),
        modules_path=Path("dummy"),
        cache_path=Path("dummy"),
        root=Path("dummy"),
    )
    
    modules = analyzer._fallback_module_list()
    
    assert len(modules) > 0
    assert "ansible.builtin.copy" in modules
    assert "ansible.builtin.template" in modules
    assert "ansible.builtin.file" in modules


def test_load_priorities(sample_priorities: Path, tmp_path: Path) -> None:
    """Test loading priorities configuration."""
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=sample_priorities,
        modules_path=Path("dummy"),
        cache_path=Path("dummy"),
        root=Path("dummy"),
    )
    
    analyzer.load_priorities()
    
    assert analyzer.priorities_config["default_priority"] == "P2"
    assert analyzer.priorities_config["modules"]["ansible.builtin.copy"] == "P1"
    assert analyzer.priorities_config["category_priorities"]["files"] == "P1"


def test_load_metadata(sample_modules_metadata: Path) -> None:
    """Test loading modules metadata."""
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=Path("dummy"),
        modules_path=sample_modules_metadata,
        cache_path=Path("dummy"),
        root=Path("dummy"),
    )
    
    analyzer.load_metadata()
    
    assert "files" in analyzer.modules_metadata
    assert "system" in analyzer.modules_metadata
    assert "ansible.builtin.copy" in analyzer.covered_modules["files"]
    assert "ansible.builtin.template" in analyzer.covered_modules["files"]
    assert "ansible.builtin.user" in analyzer.covered_modules["system"]


def test_load_filesystem_modules(sample_repo: Path) -> None:
    """Test scanning filesystem for module directories."""
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=Path("dummy"),
        modules_path=Path("dummy"),
        cache_path=Path("dummy"),
        root=sample_repo,
    )
    
    analyzer.load_filesystem_modules()
    
    assert "files" in analyzer.filesystem_modules
    assert "system" in analyzer.filesystem_modules
    assert "copy" in analyzer.filesystem_modules["files"]
    assert "template" in analyzer.filesystem_modules["files"]
    assert "file" in analyzer.filesystem_modules["files"]
    assert "user" in analyzer.filesystem_modules["system"]
    assert "service" in analyzer.filesystem_modules["system"]


def test_get_module_priority(sample_priorities: Path) -> None:
    """Test priority resolution logic."""
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=sample_priorities,
        modules_path=Path("dummy"),
        cache_path=Path("dummy"),
        root=Path("dummy"),
    )
    analyzer.load_priorities()
    
    # Explicit module priority
    assert analyzer.get_module_priority("ansible.builtin.copy") == "P1"
    assert analyzer.get_module_priority("ansible.builtin.raw") == "P3"
    
    # Category priority
    assert analyzer.get_module_priority("unknown.module", "files") == "P1"
    assert analyzer.get_module_priority("unknown.module", "network") == "P2"
    
    # Default priority
    assert analyzer.get_module_priority("unknown.module") == "P2"


def test_infer_module_category() -> None:
    """Test category inference from module names."""
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=Path("dummy"),
        modules_path=Path("dummy"),
        cache_path=Path("dummy"),
        root=Path("dummy"),
    )
    
    # Test inference from module name
    assert analyzer.infer_module_category("ansible.builtin.copy") == "files"
    assert analyzer.infer_module_category("ansible.builtin.template") == "files"
    assert analyzer.infer_module_category("ansible.builtin.user") == "system"
    assert analyzer.infer_module_category("ansible.builtin.service") == "system"
    assert analyzer.infer_module_category("ansible.builtin.apt") == "applications"
    assert analyzer.infer_module_category("ansible.builtin.shell") == "commands"
    assert analyzer.infer_module_category("ansible.builtin.firewalld") == "network"
    assert analyzer.infer_module_category("community.mysql.mysql_db") == "database"
    assert analyzer.infer_module_category("amazon.aws.ec2_instance") == "cloud"
    assert analyzer.infer_module_category("community.docker.docker_container") == "applications"


def test_cache_functionality(
    tmp_path: Path,
    sample_priorities: Path,
    sample_modules_metadata: Path,
    mocked_ansible_doc_output: str,
) -> None:
    """Test ansible-doc cache save and load."""
    cache_path = tmp_path / "cache.json"
    
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=sample_priorities,
        modules_path=sample_modules_metadata,
        cache_path=cache_path,
        root=tmp_path,
    )
    
    # Mock subprocess to return our sample output
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mocked_ansible_doc_output
        mock_run.return_value = mock_result
        
        # First call should execute ansible-doc and cache
        modules1 = analyzer.fetch_ansible_doc_list(use_cache=False)
        assert len(modules1) > 0
        assert cache_path.exists()
    
    # Second call should load from cache
    analyzer2 = module_diff.ModuleDiffAnalyzer(
        priorities_path=sample_priorities,
        modules_path=sample_modules_metadata,
        cache_path=cache_path,
        root=tmp_path,
    )
    modules2 = analyzer2.fetch_ansible_doc_list(use_cache=True)
    
    assert len(modules2) == len(modules1)
    assert "ansible.builtin.copy" in modules2


def test_full_analysis(
    tmp_path: Path,
    sample_priorities: Path,
    sample_modules_metadata: Path,
    sample_repo: Path,
    mocked_ansible_doc_output: str,
) -> None:
    """Test complete analysis workflow."""
    cache_path = tmp_path / "cache.json"
    
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=sample_priorities,
        modules_path=sample_modules_metadata,
        cache_path=cache_path,
        root=sample_repo,
    )
    
    # Mock subprocess
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mocked_ansible_doc_output
        mock_run.return_value = mock_result
        
        report = analyzer.analyze()
    
    # Check overall statistics
    assert report.total_ansible_modules > 0
    assert report.total_covered > 0
    assert report.total_missing >= 0
    assert 0 <= report.overall_coverage <= 100
    
    # Check category statistics exist
    assert len(report.categories) > 0
    
    # Check coverage details
    assert len(report.coverage_details) > 0
    
    # Verify specific modules
    copy_coverage = next((c for c in report.coverage_details if c.module == "ansible.builtin.copy"), None)
    assert copy_coverage is not None
    assert copy_coverage.status == "covered"
    assert copy_coverage.priority == "P1"
    assert copy_coverage.in_ansible_doc
    assert copy_coverage.in_metadata
    assert copy_coverage.in_filesystem


def test_find_duplicates(
    sample_priorities: Path,
    sample_modules_metadata: Path,
    sample_repo: Path,
) -> None:
    """Test duplicate detection."""
    # Create a scenario with duplicates
    metadata_file = sample_modules_metadata
    with open(metadata_file, encoding="utf-8") as f:
        metadata = yaml.safe_load(f)
    
    # Add same module to multiple categories
    metadata["applications"] = {
        "key": "applications",
        "topics": [
            {
                "id": "apt",
                "name": "Apt",
                "dependencies": ["ansible.builtin.copy"],  # Duplicate with files
            }
        ],
    }
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        yaml.dump(metadata, f)
    
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=sample_priorities,
        modules_path=metadata_file,
        cache_path=Path("dummy"),
        root=sample_repo,
    )
    analyzer.load_metadata()
    
    # Create mock coverage details
    coverage_details = [
        module_diff.ModuleCoverage(
            module="ansible.builtin.copy",
            status="covered",
            category="files",
            priority="P1",
            in_metadata=True,
        ),
        module_diff.ModuleCoverage(
            module="ansible.builtin.copy",
            status="covered",
            category="applications",
            priority="P1",
            in_metadata=True,
        ),
    ]
    
    duplicates = analyzer._find_duplicates(coverage_details)
    
    assert len(duplicates) > 0
    dup = next((d for d in duplicates if d["module"] == "ansible.builtin.copy"), None)
    assert dup is not None
    assert dup["count"] >= 2


def test_find_inconsistencies() -> None:
    """Test inconsistency detection."""
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=Path("dummy"),
        modules_path=Path("dummy"),
        cache_path=Path("dummy"),
        root=Path("dummy"),
    )
    
    coverage_details = [
        # In metadata but not filesystem
        module_diff.ModuleCoverage(
            module="ansible.builtin.missing",
            status="covered",
            category="files",
            priority="P1",
            in_metadata=True,
            in_filesystem=False,
        ),
        # In filesystem but not metadata
        module_diff.ModuleCoverage(
            module="ansible.builtin.orphan",
            status="unknown",
            category="files",
            priority="P2",
            in_metadata=False,
            in_filesystem=True,
        ),
        # Consistent
        module_diff.ModuleCoverage(
            module="ansible.builtin.good",
            status="covered",
            category="files",
            priority="P1",
            in_metadata=True,
            in_filesystem=True,
        ),
    ]
    
    inconsistencies = analyzer._find_inconsistencies(coverage_details)
    
    assert len(inconsistencies) == 2
    issues = {inc["module"]: inc["issue"] for inc in inconsistencies}
    assert issues["ansible.builtin.missing"] == "in_metadata_but_not_filesystem"
    assert issues["ansible.builtin.orphan"] == "in_filesystem_but_not_metadata"


def test_json_report_generation(
    tmp_path: Path,
    sample_priorities: Path,
    sample_modules_metadata: Path,
    sample_repo: Path,
    mocked_ansible_doc_output: str,
) -> None:
    """Test JSON report generation."""
    cache_path = tmp_path / "cache.json"
    json_output = tmp_path / "report.json"
    
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=sample_priorities,
        modules_path=sample_modules_metadata,
        cache_path=cache_path,
        root=sample_repo,
    )
    
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mocked_ansible_doc_output
        mock_run.return_value = mock_result
        
        report = analyzer.analyze()
    
    analyzer.write_json_report(report, json_output)
    
    assert json_output.exists()
    
    with open(json_output, encoding="utf-8") as f:
        data = json.load(f)
    
    assert "generated_at" in data
    assert "total_ansible_modules" in data
    assert "categories" in data
    assert "coverage_details" in data


def test_markdown_report_generation(
    tmp_path: Path,
    sample_priorities: Path,
    sample_modules_metadata: Path,
    sample_repo: Path,
    mocked_ansible_doc_output: str,
) -> None:
    """Test Markdown report generation."""
    cache_path = tmp_path / "cache.json"
    md_output = tmp_path / "report.md"
    
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=sample_priorities,
        modules_path=sample_modules_metadata,
        cache_path=cache_path,
        root=sample_repo,
    )
    
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mocked_ansible_doc_output
        mock_run.return_value = mock_result
        
        report = analyzer.analyze()
    
    analyzer.write_markdown_report(report, md_output)
    
    assert md_output.exists()
    
    content = md_output.read_text(encoding="utf-8")
    assert "Ansible Module Coverage Report" in content
    assert "Overall Statistics" in content
    assert "Category Coverage" in content
    assert "Priority Breakdown" in content


def test_priority_filtering(
    tmp_path: Path,
    sample_priorities: Path,
    sample_modules_metadata: Path,
    sample_repo: Path,
    mocked_ansible_doc_output: str,
) -> None:
    """Test priority filtering in summary."""
    cache_path = tmp_path / "cache.json"
    
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=sample_priorities,
        modules_path=sample_modules_metadata,
        cache_path=cache_path,
        root=sample_repo,
    )
    
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mocked_ansible_doc_output
        mock_run.return_value = mock_result
        
        report = analyzer.analyze()
    
    # Check that we have modules with different priorities
    priorities = {c.priority for c in report.coverage_details}
    assert "P1" in priorities
    
    p1_missing = [c for c in report.coverage_details if c.status == "missing" and c.priority == "P1"]
    p2_missing = [c for c in report.coverage_details if c.status == "missing" and c.priority == "P2"]
    
    # Should have different counts for different priorities
    assert len(p1_missing) != len(p2_missing) or len(p1_missing) == 0


def test_graceful_fallback_on_ansible_doc_failure(
    tmp_path: Path,
    sample_priorities: Path,
    sample_modules_metadata: Path,
    sample_repo: Path,
) -> None:
    """Test graceful fallback when ansible-doc fails."""
    cache_path = tmp_path / "cache.json"
    
    analyzer = module_diff.ModuleDiffAnalyzer(
        priorities_path=sample_priorities,
        modules_path=sample_modules_metadata,
        cache_path=cache_path,
        root=sample_repo,
    )
    
    # Mock subprocess to simulate ansible-doc failure
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "ansible-doc: command not found"
        mock_run.return_value = mock_result
        
        modules = analyzer._execute_ansible_doc()
    
    # Should fallback to common modules list
    assert len(modules) > 0
    assert "ansible.builtin.copy" in modules
