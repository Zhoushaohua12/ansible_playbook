from pathlib import Path
import re

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_advanced_readme_has_debug_section():
    content = read(REPO_ROOT / "advanced" / "README.md")
    assert "如何调试/常见错误" in content


PLAYBOOK_EXPECTATIONS = {
    "advanced/block_rescue/playbook.yml": ["block:", "rescue:", "always:"],
    "advanced/when_conditions/playbook.yml": ["when:"],
    "advanced/loop_iteration/playbook.yml": ["loop:", "loop_control:", "loop_var"],
    "advanced/set_fact_vars/playbook.yml": ["set_fact", "db_release_info"],
    "advanced/handlers_notify/playbook.yml": ["notify:", "handlers:"],
    "advanced/include_tasks/playbook.yml": ["include_tasks"]
}


@pytest.mark.parametrize("relative_path, markers", PLAYBOOK_EXPECTATIONS.items())
def test_playbooks_contain_expected_markers(relative_path, markers):
    content = read(REPO_ROOT / relative_path)
    for marker in markers:
        assert marker in content, f"{relative_path} 缺少 {marker}"


def test_include_task_child_file_has_chinese_comment():
    child = REPO_ROOT / "advanced" / "include_tasks" / "child_task.yml"
    assert child.exists(), "子任务文件不存在"
    content = read(child)
    assert re.search(r"#[^\n]*[\u4e00-\u9fff]", content), "子任务文件需要中文注释"
