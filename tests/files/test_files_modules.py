"""文件操作模块文档与示例结构测试"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List

import pytest
import yaml

MODULES: List[str] = [
    "copy",
    "template",
    "lineinfile",
    "stat",
    "file",
    "find",
    "synchronize",
    "fetch",
    "unarchive",
    "archive",
    "replace",
    "blockinfile",
]

EXPECTED_FQCN = {
    "copy": "ansible.builtin.copy",
    "template": "ansible.builtin.template",
    "lineinfile": "ansible.builtin.lineinfile",
    "stat": "ansible.builtin.stat",
    "file": "ansible.builtin.file",
    "find": "ansible.builtin.find",
    "synchronize": "ansible.posix.synchronize",
    "fetch": "ansible.builtin.fetch",
    "unarchive": "ansible.builtin.unarchive",
    "archive": "ansible.builtin.archive",
    "replace": "ansible.builtin.replace",
    "blockinfile": "ansible.builtin.blockinfile",
}

EXTRA_FILES = {
    "copy": [
        "files/web_app.conf",
        "files/motd_banner.txt",
    ],
    "template": [
        "templates/web_app.conf.j2",
        "templates/nginx_site.conf.j2",
        "templates/app.service.j2",
        "templates/env_config.j2",
    ],
    "synchronize": [
        "source_dir/index.html",
        "source_dir/assets/style.css",
    ],
    "fetch": [
        "files/access.log",
        "files/error.log",
        "files/config_checksum.txt",
    ],
    "unarchive": [
        "files/demo_config.tar.gz",
        "files/demo_config/index.html",
        "files/demo_config/config.ini",
    ],
    "archive": [
        "source_dir/index.html",
        "source_dir/README.md",
        "source_dir/config/app.conf",
    ],
}


def _has_chinese_comment(content: str) -> bool:
    """检查文本中是否存在中文注释（# 开头且包含中文字符）。"""

    for line in content.splitlines():
        if "#" in line:
            hash_index = line.index("#")
            comment = line[hash_index:]
            if any("\u4e00" <= ch <= "\u9fff" for ch in comment):
                return True
    return False


def _collect_tasks(play_data: Iterable[dict]) -> List[dict]:
    tasks: List[dict] = []
    for play in play_data:
        if not isinstance(play, dict):
            continue
        for section in ("tasks", "pre_tasks", "post_tasks", "handlers"):
            section_tasks = play.get(section, [])
            if isinstance(section_tasks, dict):
                section_tasks = [section_tasks]
            tasks.extend(task for task in section_tasks if isinstance(task, dict))
    return tasks


class TestFilesModules:
    @pytest.fixture(scope="class")
    def files_root(self) -> Path:
        return Path(__file__).parent.parent.parent / "files"

    @pytest.fixture(scope="class")
    def module_dirs(self, files_root: Path) -> Dict[str, Path]:
        return {name: files_root / name for name in MODULES}

    def test_readmes_exist_and_have_chinese_comment(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            readme = path / "README.md"
            assert readme.exists(), f"{name} 模块缺少 README.md"
            content = readme.read_text(encoding="utf-8")
            assert _has_chinese_comment(content), f"{name} README.md 需要包含中文注释"

    def test_playbooks_exist_are_yaml_and_have_chinese_comment(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            playbook = path / "playbook.yml"
            assert playbook.exists(), f"{name} 模块缺少 playbook.yml"
            content = playbook.read_text(encoding="utf-8")
            try:
                yaml.safe_load(content)
            except yaml.YAMLError as err:  # pragma: no cover - 错误路径
                pytest.fail(f"{name} playbook.yml 解析失败: {err}")
            assert _has_chinese_comment(content), f"{name} playbook 需要包含中文注释"

    def test_playbooks_use_expected_modules(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            playbook = path / "playbook.yml"
            data = yaml.safe_load(playbook.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                pytest.fail(f"{name} playbook 结构应为列表形式的 play 定义")
            tasks = _collect_tasks(data)
            expected = EXPECTED_FQCN[name]
            matched = any(expected in task for task in tasks)
            assert matched, f"{name} playbook 需包含模块 {expected} 的任务"

    def test_example_vars_exist_and_contain_chinese(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            vars_file = path / "vars" / "example_vars.yml"
            assert vars_file.exists(), f"{name} 模块缺少 vars/example_vars.yml"
            content = vars_file.read_text(encoding="utf-8")
            try:
                yaml.safe_load(content)
            except yaml.YAMLError as err:  # pragma: no cover
                pytest.fail(f"{name} example_vars.yml 解析失败: {err}")
            assert any("\u4e00" <= ch <= "\u9fff" for ch in content), (
                f"{name} example_vars.yml 需包含中文注释"
            )

    def test_extra_files_exist_for_templates_and_copy(self, module_dirs: Dict[str, Path]) -> None:
        for name, files in EXTRA_FILES.items():
            module_path = module_dirs[name]
            for relative in files:
                target = module_path / relative
                assert target.exists(), f"{name} 模块缺少示例文件: {relative}"

    def test_root_readme_links(self, files_root: Path) -> None:
        readme = files_root / "README.md"
        content = readme.read_text(encoding="utf-8")
        for module in MODULES:
            assert f"({module}/README.md)" in content, f"files README 缺少 {module} 模块链接"
