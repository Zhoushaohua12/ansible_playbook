"""
Unit tests for audit_report tool.

Tests include mocking small fixture trees to ensure collectors correctly flag:
- Missing gather_facts
- Missing Chinese task names
- Security issues (no_log, vault_ usage)
- Warning headers in vars files
- FQCN usage patterns
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.audit_report import AuditCollector


@pytest.fixture
def sample_playbook_repo(tmp_path: Path) -> tuple[Path, dict[str, Path]]:
    """Create a sample repository with various playbook patterns."""
    repo = tmp_path / "test_repo"

    # Create base structure
    (repo / "files" / "copy" / "vars").mkdir(parents=True)
    (repo / "commands" / "shell" / "vars").mkdir(parents=True)
    (repo / "applications" / "docker_container" / "vars").mkdir(parents=True)
    (repo / "security_issue" / "test_module" / "vars").mkdir(parents=True)

    fixtures = {
        "repo": repo,
        "files_copy": repo / "files" / "copy",
        "commands_shell": repo / "commands" / "shell",
        "docker_container": repo / "applications" / "docker_container",
        "security_issue": repo / "security_issue" / "test_module",
    }

    return repo, fixtures


def test_collect_playbooks_with_gather_facts(sample_playbook_repo: tuple[Path, dict[str, Path]]) -> None:
    """Test detection of playbooks with gather_facts."""
    repo, fixtures = sample_playbook_repo

    # Write a good playbook with gather_facts
    (fixtures["files_copy"] / "playbook.yml").write_text(
        """---
- name: copy 模块演练
  hosts: all
  gather_facts: false
  tasks:
    - name: 复制示例文件
      ansible.builtin.copy:
        src: files/sample.conf
        dest: /etc/sample.conf
""",
        encoding="utf-8",
    )

    # Write vars file with warning
    (fixtures["files_copy"] / "vars" / "example_vars.yml").write_text(
        """---
# ⚠️ 本文件仅为示例
sample_path: /tmp/sample
""",
        encoding="utf-8",
    )

    collector = AuditCollector(repo)
    collector.scan()

    assert collector.stats["total_playbooks"] == 1
    assert collector.stats["playbooks_with_gather_facts"] == 1
    assert len(collector.issues["high"]) == 0


def test_detect_missing_gather_facts(sample_playbook_repo: tuple[Path, dict[str, Path]]) -> None:
    """Test detection of missing gather_facts."""
    repo, fixtures = sample_playbook_repo

    # Write a playbook without gather_facts
    (fixtures["commands_shell"] / "playbook.yml").write_text(
        """---
- name: shell 模块演练
  hosts: all
  tasks:
    - name: 执行命令
      ansible.builtin.shell: "echo hello"
""",
        encoding="utf-8",
    )

    (fixtures["commands_shell"] / "vars" / "example_vars.yml").write_text(
        "# ⚠️ Example\nshell_cmd: 'echo test'\n",
        encoding="utf-8",
    )

    collector = AuditCollector(repo)
    collector.scan()

    assert collector.stats["total_playbooks"] == 1
    assert collector.stats["playbooks_with_gather_facts"] == 0

    high_issues = collector.issues["high"]
    gather_facts_issues = [
        i for i in high_issues
        if "gather_facts" in i.get("issue", "").lower()
    ]
    assert len(gather_facts_issues) > 0


def test_detect_missing_warning_in_vars(sample_playbook_repo: tuple[Path, dict[str, Path]]) -> None:
    """Test detection of missing warning headers in vars files."""
    repo, fixtures = sample_playbook_repo

    (fixtures["files_copy"] / "playbook.yml").write_text(
        "---\n- name: test\n  hosts: all\n  gather_facts: false\n  tasks: []\n",
        encoding="utf-8",
    )

    # Vars file WITHOUT warning
    (fixtures["files_copy"] / "vars" / "example_vars.yml").write_text(
        "# Example variables\nsample_var: value\n",
        encoding="utf-8",
    )

    collector = AuditCollector(repo)
    collector.scan()

    assert collector.stats["total_vars_files"] == 1
    assert collector.stats["vars_with_warning"] == 0

    high_issues = collector.issues["high"]
    warning_issues = [
        i for i in high_issues
        if "warning" in i.get("issue", "").lower()
    ]
    assert len(warning_issues) > 0


def test_detect_missing_no_log_for_sensitive_data(sample_playbook_repo: tuple[Path, dict[str, Path]]) -> None:
    """Test detection of sensitive data without no_log protection."""
    repo, fixtures = sample_playbook_repo

    # Create playbook with sensitive data but no no_log
    (fixtures["docker_container"] / "playbook.yml").write_text(
        """---
- name: docker container 演练
  hosts: all
  gather_facts: false
  tasks:
    - name: 创建容器
      community.docker.docker_container:
        name: myapp
        image: myapp:latest
        env:
          DATABASE_URL: "postgresql://user:password@db"
          REDIS_PASSWORD: "secretpass"
""",
        encoding="utf-8",
    )

    (fixtures["docker_container"] / "vars" / "example_vars.yml").write_text(
        "# ⚠️ Example\ncontainer_password: example\n",
        encoding="utf-8",
    )

    collector = AuditCollector(repo)
    collector.scan()

    high_issues = collector.issues["high"]
    nolog_issues = [
        i for i in high_issues
        if "no_log" in i.get("issue", "").lower()
    ]
    assert len(nolog_issues) > 0


def test_detect_vault_prefix_usage(sample_playbook_repo: tuple[Path, dict[str, Path]]) -> None:
    """Test detection of vault_ prefixed variables."""
    repo, fixtures = sample_playbook_repo

    (fixtures["security_issue"] / "playbook.yml").write_text(
        """---
- name: secure configuration
  hosts: all
  gather_facts: false
  vars_files:
    - vars/example_vars.yml
  tasks:
    - name: configure app
      ansible.builtin.copy:
        content: "password: {{ vault_password }}"
        dest: /etc/app.conf
      no_log: true
""",
        encoding="utf-8",
    )

    (fixtures["security_issue"] / "vars" / "example_vars.yml").write_text(
        """---
# ⚠️ 本文件仅为示例
vault_password: "{{ lookup('env', 'APP_PASSWORD') }}"
""",
        encoding="utf-8",
    )

    collector = AuditCollector(repo)
    collector.scan()

    assert collector.stats["playbooks_with_vault_vars"] == 1
    assert collector.stats["playbooks_with_no_log"] == 1


def test_detect_chinese_names(sample_playbook_repo: tuple[Path, dict[str, Path]]) -> None:
    """Test detection of Chinese task names."""
    repo, fixtures = sample_playbook_repo

    # Playbook WITH Chinese names
    (fixtures["files_copy"] / "playbook.yml").write_text(
        """---
- name: copy 模块演练
  hosts: all
  gather_facts: false
  tasks:
    - name: 创建目录
      ansible.builtin.file:
        path: /tmp/demo
        state: directory

    - name: 复制示例文件
      ansible.builtin.copy:
        src: files/sample.conf
        dest: /etc/sample.conf

    - name: 验证文件
      ansible.builtin.stat:
        path: /etc/sample.conf
""",
        encoding="utf-8",
    )

    (fixtures["files_copy"] / "vars" / "example_vars.yml").write_text(
        "# ⚠️ Example\ntest: value\n",
        encoding="utf-8",
    )

    collector = AuditCollector(repo)
    collector.scan()

    low_issues = collector.issues["low"]
    name_issues = [
        i for i in low_issues
        if "name" in i.get("issue", "").lower()
    ]
    # Should have few or no issues due to Chinese names
    assert len(name_issues) <= 1


def test_detect_fqcn_usage(sample_playbook_repo: tuple[Path, dict[str, Path]]) -> None:
    """Test detection of FQCN (Fully Qualified Collection Name) usage."""
    repo, fixtures = sample_playbook_repo

    # Playbook WITH FQCN
    (fixtures["files_copy"] / "playbook.yml").write_text(
        """---
- name: file operations
  hosts: all
  gather_facts: false
  tasks:
    - name: 使用FQCN调用模块
      ansible.builtin.copy:
        src: files/test.conf
        dest: /tmp/test.conf

    - name: 调用社区模块
      community.general.synchronize:
        src: /tmp/src
        dest: /tmp/dst
""",
        encoding="utf-8",
    )

    (fixtures["files_copy"] / "vars" / "example_vars.yml").write_text(
        "# ⚠️ Example\ntest: value\n",
        encoding="utf-8",
    )

    collector = AuditCollector(repo)
    collector.scan()

    # Should find FQCN usage
    medium_issues = collector.issues["medium"]
    fqcn_issues = [
        i for i in medium_issues
        if "fqcn" in i.get("issue", "").lower()
    ]
    # Since we have FQCN, this should be minimal or none
    assert len(fqcn_issues) <= 1


def test_audit_report_generation(sample_playbook_repo: tuple[Path, dict[str, Path]]) -> None:
    """Test report generation from audit results."""
    repo, fixtures = sample_playbook_repo

    (fixtures["files_copy"] / "playbook.yml").write_text(
        """---
- name: 文件操作演练
  hosts: all
  gather_facts: false
  tasks:
    - name: 复制文件
      ansible.builtin.copy:
        src: files/sample.conf
        dest: /etc/sample.conf
""",
        encoding="utf-8",
    )

    (fixtures["files_copy"] / "vars" / "example_vars.yml").write_text(
        "# ⚠️ Example warning\ntest: value\n",
        encoding="utf-8",
    )

    collector = AuditCollector(repo)
    collector.scan()

    report = collector.generate_report()

    # Check report structure
    assert "自动化审计报告" in report
    assert "Overview" in report or "概览" in report
    assert "Issues" in report or "问题清单" in report
    assert "Recommendations" in report or "建议" in report

    # Check statistics appear
    assert "gather_facts" in report.lower()
    assert "check_mode" in report.lower()


def test_audit_to_dict_export(sample_playbook_repo: tuple[Path, dict[str, Path]]) -> None:
    """Test conversion to dictionary for JSON export."""
    repo, fixtures = sample_playbook_repo

    (fixtures["files_copy"] / "playbook.yml").write_text(
        "---\n- name: test\n  hosts: all\n  gather_facts: true\n  tasks: []\n",
        encoding="utf-8",
    )

    (fixtures["files_copy"] / "vars" / "example_vars.yml").write_text(
        "# ⚠️ Example\ntest: value\n",
        encoding="utf-8",
    )

    collector = AuditCollector(repo)
    collector.scan()

    data = collector.to_dict()

    assert "timestamp" in data
    assert "statistics" in data
    assert "issues" in data
    assert "categories" in data

    assert data["statistics"]["total_playbooks"] == 1
    assert data["statistics"]["playbooks_with_gather_facts"] == 1

    assert "critical" in data["issues"]
    assert "high" in data["issues"]
    assert "medium" in data["issues"]
    assert "low" in data["issues"]


def test_empty_repository(tmp_path: Path) -> None:
    """Test audit with empty repository."""
    repo = tmp_path / "empty_repo"
    repo.mkdir()

    collector = AuditCollector(repo)
    collector.scan()

    assert collector.stats["total_playbooks"] == 0
    assert collector.stats["total_vars_files"] == 0
    assert len(collector.categories) == 0


def test_playbook_with_check_mode(sample_playbook_repo: tuple[Path, dict[str, Path]]) -> None:
    """Test detection of check_mode usage."""
    repo, fixtures = sample_playbook_repo

    (fixtures["files_copy"] / "playbook.yml").write_text(
        """---
- name: 文件操作
  hosts: all
  gather_facts: false
  tasks:
    - name: 复制文件
      ansible.builtin.copy:
        src: files/sample.conf
        dest: /etc/sample.conf
        check_mode: true
""",
        encoding="utf-8",
    )

    (fixtures["files_copy"] / "vars" / "example_vars.yml").write_text(
        "# ⚠️ Example\ntest: value\n",
        encoding="utf-8",
    )

    collector = AuditCollector(repo)
    collector.scan()

    assert collector.stats["playbooks_with_check_mode"] == 1


def test_multiple_playbooks_statistics(sample_playbook_repo: tuple[Path, dict[str, Path]]) -> None:
    """Test statistics aggregation across multiple playbooks."""
    repo, fixtures = sample_playbook_repo

    # Create 2 good playbooks
    for i, fixture_dir in enumerate(
        [fixtures["files_copy"], fixtures["commands_shell"]]
    ):
        (fixture_dir / "playbook.yml").write_text(
            f"""---
- name: test module {i}
  hosts: all
  gather_facts: false
  tasks:
    - name: 测试任务 {i}
      ansible.builtin.debug:
        msg: "Test {i}"
""",
            encoding="utf-8",
        )

        (fixture_dir / "vars" / "example_vars.yml").write_text(
            "# ⚠️ Example\ntest: value\n",
            encoding="utf-8",
        )

    # Create 1 bad playbook
    (fixtures["docker_container"] / "playbook.yml").write_text(
        """---
- name: bad module
  hosts: all
  tasks:
    - name: task without gather_facts
      ansible.builtin.debug:
        msg: test
""",
        encoding="utf-8",
    )

    (fixtures["docker_container"] / "vars" / "example_vars.yml").write_text(
        "# No warning\ntest: value\n",
        encoding="utf-8",
    )

    collector = AuditCollector(repo)
    collector.scan()

    assert collector.stats["total_playbooks"] == 3
    assert collector.stats["playbooks_with_gather_facts"] == 2
    assert collector.stats["total_vars_files"] == 3
    assert collector.stats["vars_with_warning"] == 2

    # Should have high priority issues
    assert len(collector.issues["high"]) > 0
