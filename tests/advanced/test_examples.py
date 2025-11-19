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
    "advanced/include_tasks/playbook.yml": ["include_tasks"],
    "advanced/block_always/playbook.yml": ["block:", "rescue:", "always:", "when:"],
    "advanced/import_playbook/playbook.yml": ["import_playbook"],
    "advanced/import_tasks/playbook.yml": ["import_tasks", "when:"],
    "advanced/loop_matrix/playbook.yml": ["loop:", "product", "subelements"]
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


def test_import_playbook_stage_files_have_chinese():
    stages = [
        REPO_ROOT / "advanced" / "import_playbook" / "stage1_prepare.yml",
        REPO_ROOT / "advanced" / "import_playbook" / "stage2_deploy.yml",
        REPO_ROOT / "advanced" / "import_playbook" / "stage3_verify.yml",
    ]
    for stage in stages:
        assert stage.exists(), f"缺少 {stage.name}"
        content = read(stage)
        assert re.search(r"[\u4e00-\u9fff]", content), f"{stage.name} 需要中文注释"


def test_import_tasks_task_files_have_chinese():
    tasks = [
        REPO_ROOT / "advanced" / "import_tasks" / "tasks" / "configure.yml",
        REPO_ROOT / "advanced" / "import_tasks" / "tasks" / "cleanup.yml",
    ]
    for task_file in tasks:
        assert task_file.exists(), f"缺少 {task_file.name}"
        content = read(task_file)
        assert re.search(r"[\u4e00-\u9fff]", content), f"{task_file.name} 需要中文注释"
