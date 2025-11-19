"""存储模块示例的结构与文档校验"""

from pathlib import Path
from typing import Dict

import pytest
import yaml

MODULES = ["mount", "lvol", "filesystem"]
FQCN_EXPECTATIONS = {
    "mount": "ansible.posix.mount",
    "lvol": "ansible.builtin.lvol",
    "filesystem": "ansible.builtin.filesystem",
}


class TestStorageFixtures:
    """提供存储模块路径的公共 fixture"""

    @pytest.fixture(scope="class")
    def storage_root(self) -> Path:
        return Path(__file__).parent.parent.parent / "storage"

    @pytest.fixture(scope="class")
    def module_dirs(self, storage_root: Path) -> Dict[str, Path]:
        return {name: storage_root / name for name in MODULES}


class TestStorageReadme(TestStorageFixtures):
    """校验 storage 根目录的 README 内容"""

    def test_storage_readme_exists(self, storage_root: Path) -> None:
        readme = storage_root / "README.md"
        assert readme.exists(), "storage 根目录缺少 README.md"

    def test_storage_readme_mentions_loopback_and_check(self, storage_root: Path) -> None:
        content = (storage_root / "README.md").read_text(encoding="utf-8").lower()
        assert "loop" in content, "storage/README.md 应说明 loopback/loop 设备的用法"
        assert "--check" in content, "storage/README.md 应提醒通过 --check 运行 playbook"


class TestModuleDocumentation(TestStorageFixtures):
    """校验各存储模块 README 的章节与内容"""

    REQUIRED_SECTIONS = ["模块用途", "主要参数", "返回值", "安全注意事项"]

    def test_module_readmes_exist(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            readme = path / "README.md"
            assert readme.exists(), f"{name} 模块缺少 README.md"

    def test_module_readmes_sections_and_testing_guidance(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8")
            for section in self.REQUIRED_SECTIONS:
                assert section in content, f"{name} README.md 缺少 {section} 章节"
            lowered = content.lower()
            assert "loop" in lowered, f"{name} README.md 需说明 loopback/loop 设备的使用"
            assert "--check" in lowered, f"{name} README.md 需说明 ansible-playbook --check 的使用"


class TestPlaybooks(TestStorageFixtures):
    """校验 playbook 的语法、安全提示与 FQCN"""

    def test_playbooks_are_valid_yaml(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            playbook = path / "playbook.yml"
            assert playbook.exists(), f"{name} 模块缺少 playbook.yml"
            with playbook.open("r", encoding="utf-8") as handler:
                try:
                    yaml.safe_load(handler)
                except yaml.YAMLError as err:
                    pytest.fail(f"{name} playbook.yml 解析失败: {err}")

    def test_playbooks_contain_demo_warning_and_chinese(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "仅供" in content or "请勿" in content, f"{name} playbook 需包含仅供演示/请勿生产的安全注释"
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"{name} playbook 需要使用中文任务名或注释"

    def test_playbooks_use_loop_and_vars_files(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "loop:" in content, f"{name} playbook 需要使用 loop 描述临时磁盘准备"
            assert "vars_files" in content, f"{name} playbook 应引用 vars/example_vars.yml"
            assert "ansible_check_mode" in content, f"{name} playbook 需提醒使用 --check 模式"

    def test_playbooks_use_expected_fqcn(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            expected = FQCN_EXPECTATIONS[name]
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert expected in content, f"{name} playbook 应使用 FQCN {expected}"


class TestVarsFiles(TestStorageFixtures):
    """校验示例变量的注释、安全提示与语法"""

    WARNING_KEYWORDS = ["占位", "重要", "请勿", "⚠"]

    def test_vars_files_exist_and_valid_yaml(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            vars_file = path / "vars" / "example_vars.yml"
            assert vars_file.exists(), f"{name} 模块缺少 vars/example_vars.yml"
            try:
                yaml.safe_load(vars_file.read_text(encoding="utf-8"))
            except yaml.YAMLError as err:
                pytest.fail(f"{name} example_vars.yml 解析失败: {err}")

    def test_vars_files_have_chinese_and_warning(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"{name} example_vars.yml 需包含中文注释"
            assert any(keyword in content for keyword in self.WARNING_KEYWORDS), (
                f"{name} example_vars.yml 需提示变量为占位或包含安全警告"
            )
