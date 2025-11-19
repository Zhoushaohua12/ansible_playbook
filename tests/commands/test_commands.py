"""命令模块示例的结构与文档校验"""

from pathlib import Path
from typing import Dict

import pytest
import yaml

MODULES = ["shell", "command", "raw", "script", "expect"]
FQCN_EXPECTATIONS = {
    "shell": "ansible.builtin.shell",
    "command": "ansible.builtin.command", 
    "raw": "ansible.builtin.raw",
    "script": "ansible.builtin.script",
    "expect": "ansible.builtin.expect",
}


class TestCommandsFixtures:
    """提供命令模块路径的公共 fixture"""

    @pytest.fixture(scope="class")
    def commands_root(self) -> Path:
        return Path(__file__).parent.parent.parent / "commands"

    @pytest.fixture(scope="class")
    def module_dirs(self, commands_root: Path) -> Dict[str, Path]:
        return {name: commands_root / name for name in MODULES}


class TestCommandsReadme(TestCommandsFixtures):
    """校验 commands 根目录的 README 内容"""

    def test_commands_readme_exists(self, commands_root: Path) -> None:
        readme = commands_root / "README.md"
        assert readme.exists(), "commands 根目录缺少 README.md"

    def test_commands_readme_contains_module_comparison(self, commands_root: Path) -> None:
        content = (commands_root / "README.md").read_text(encoding="utf-8")
        assert "shell" in content, "commands/README.md 应包含 shell 模块说明"
        assert "command" in content, "commands/README.md 应包含 command 模块说明"
        assert "raw" in content, "commands/README.md 应包含 raw 模块说明"
        assert "script" in content, "commands/README.md 应包含 script 模块说明"
        assert "expect" in content, "commands/README.md 应包含 expect 模块说明"
        assert "安全风险" in content, "commands/README.md 应说明安全风险"


class TestModuleDocumentation(TestCommandsFixtures):
    """校验各命令模块 README 的章节与内容"""

    REQUIRED_SECTIONS = ["模块用途", "主要参数", "返回值", "安全注意事项"]

    def test_module_readmes_exist(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            readme = path / "README.md"
            assert readme.exists(), f"{name} 模块缺少 README.md"

    def test_module_readmes_contain_required_sections_and_chinese(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8")
            for section in self.REQUIRED_SECTIONS:
                assert section in content, f"{name} README.md 缺少 {section} 章节"
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"{name} README.md 需要包含中文内容"


class TestPlaybooks(TestCommandsFixtures):
    """校验 playbook 的语法、中文注释与安全规范"""

    def test_playbooks_are_valid_yaml(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            playbook = path / "playbook.yml"
            assert playbook.exists(), f"{name} 模块缺少 playbook.yml"
            with playbook.open("r", encoding="utf-8") as handler:
                try:
                    yaml.safe_load(handler)
                except yaml.YAMLError as err:
                    pytest.fail(f"{name} playbook.yml 解析失败: {err}")

    def test_playbooks_contain_chinese_comments(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"{name} playbook 需要使用中文任务名或注释"

    def test_playbooks_use_expected_fqcn(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            expected = FQCN_EXPECTATIONS[name]
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert expected in content, f"{name} playbook 应使用 FQCN {expected}"

    def test_shell_playbook_safety_requirements(self, module_dirs: Dict[str, Path]) -> None:
        """检查 shell 模块的安全要求"""
        shell_path = module_dirs["shell"]
        content = (shell_path / "playbook.yml").read_text(encoding="utf-8")
        
        # 检查是否包含安全说明
        assert "warn: false" in content or "set -e" in content, (
            "shell playbook 应包含 warn: false 或 set -e 等安全说明"
        )

    def test_command_playbook_no_shell_usage(self, module_dirs: Dict[str, Path]) -> None:
        """检查 command 模块未启用 shell"""
        command_path = module_dirs["command"]
        content = (command_path / "playbook.yml").read_text(encoding="utf-8")
        
        # 确保 command 模块示例中没有启用 shell
        lines = content.split('\n')
        in_command_task = False
        
        for line in lines:
            line_stripped = line.strip()
            if 'ansible.builtin.command:' in line_stripped:
                in_command_task = True
                continue
            elif line_stripped.startswith('ansible.builtin.') and ':' in line_stripped:
                in_command_task = False
                continue
            
            if in_command_task and ('shell:' in line_stripped or '|>' in line_stripped):
                pytest.fail("command playbook 不应在 command 任务中使用 shell 特性")

    def test_raw_playbook_chinese_warning(self, module_dirs: Dict[str, Path]) -> None:
        """检查 raw 模块包含中文安全提醒"""
        raw_path = module_dirs["raw"]
        content = (raw_path / "playbook.yml").read_text(encoding="utf-8")
        
        # 检查是否包含中文安全提醒
        assert "中文" in content and ("提醒" in content or "警告" in content), (
            "raw playbook 应包含中文安全提醒，说明会越过 Python 依赖"
        )

    def test_script_playbook_references_script_file(self, module_dirs: Dict[str, Path]) -> None:
        """检查 script 模块引用了现有脚本文件并有中文注释"""
        script_path = module_dirs["script"]
        content = (script_path / "playbook.yml").read_text(encoding="utf-8")
        
        # 检查是否引用了脚本文件
        assert "files/" in content or ".sh" in content, (
            "script playbook 应引用现有的 .sh 脚本文件"
        )
        
        # 检查是否有中文注释
        has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
        assert has_chinese, "script playbook 需要包含中文注释"

    def test_playbooks_use_vars_files(self, module_dirs: Dict[str, Path]) -> None:
        """检查所有 playbook 都引用了 vars 文件"""
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "vars_files" in content, f"{name} playbook 应引用 vars/example_vars.yml"


class TestVarsFiles(TestCommandsFixtures):
    """校验示例变量的注释、安全提示与语法"""

    WARNING_KEYWORDS = ["占位", "重要", "请勿", "⚠", "警告", "风险"]

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


class TestScriptModuleFiles(TestCommandsFixtures):
    """校验 script 模块的额外文件结构"""

    def test_script_module_has_files_directory(self, module_dirs: Dict[str, Path]) -> None:
        script_path = module_dirs["script"]
        files_dir = script_path / "files"
        assert files_dir.exists(), "script 模块缺少 files 目录"

    def test_script_module_has_shell_script(self, module_dirs: Dict[str, Path]) -> None:
        script_path = module_dirs["script"]
        script_file = script_path / "files" / "example.sh"
        assert script_file.exists(), "script 模块缺少 files/example.sh"
        
        # 检查脚本是否有 shebang
        content = script_file.read_text(encoding="utf-8")
        assert content.startswith("#!"), "example.sh 应包含 shebang 行"
        
        # 检查脚本是否有中文注释
        has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
        assert has_chinese, "example.sh 应包含中文注释"