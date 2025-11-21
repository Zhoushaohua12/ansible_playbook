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
    "get_url",
    "assemble",
    "slurp",
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
    "get_url": "ansible.builtin.get_url",
    "assemble": "ansible.builtin.assemble",
    "slurp": "ansible.builtin.slurp",
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

    def test_get_url_module_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """验证 get_url 模块包含特定内容"""
        get_url_path = module_dirs["get_url"]
        readme = (get_url_path / "README.md").read_text(encoding="utf-8")
        playbook = (get_url_path / "playbook.yml").read_text(encoding="utf-8")
        vars_file = (get_url_path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        
        # 检查 README 中的关键词
        assert "下载" in readme, "get_url 模块 README 应提及下载"
        assert "URL" in readme, "get_url 模块 README 应提及 URL"
        assert "checksum" in readme, "get_url 模块 README 应提及校验和"
        
        # 检查 playbook 中的 FQCN
        assert "ansible.builtin.get_url" in playbook, "get_url playbook 应使用 get_url 模块"
        
        # 检查 playbook 中的 vars_files
        assert "vars_files" in playbook, "get_url playbook 应引用 vars_files"
        
        # 检查 playbook 中的 check_mode
        assert "check_mode" in playbook, "get_url playbook 应包含 check_mode"
        
        # 检查变量文件中的关键变量和警告
        assert "sample_config_url" in vars_file, "get_url vars 应包含 sample_config_url 变量"
        assert "download_timeout" in vars_file, "get_url vars 应包含 download_timeout 变量"
        assert "⚠️" in vars_file or "警告" in vars_file or "注意" in vars_file, (
            "get_url vars 应包含安全提示"
        )

    def test_assemble_module_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """验证 assemble 模块包含特定内容"""
        assemble_path = module_dirs["assemble"]
        readme = (assemble_path / "README.md").read_text(encoding="utf-8")
        playbook = (assemble_path / "playbook.yml").read_text(encoding="utf-8")
        vars_file = (assemble_path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        
        # 检查 README 中的关键词
        assert "组装" in readme, "assemble 模块 README 应提及组装"
        assert "片段" in readme, "assemble 模块 README 应提及片段"
        assert "配置文件" in readme, "assemble 模块 README 应提及配置文件"
        
        # 检查 playbook 中的 FQCN
        assert "ansible.builtin.assemble" in playbook, "assemble playbook 应使用 assemble 模块"
        
        # 检查 playbook 中的 vars_files
        assert "vars_files" in playbook, "assemble playbook 应引用 vars_files"
        
        # 检查 playbook 中的 check_mode
        assert "check_mode" in playbook, "assemble playbook 应包含 check_mode"
        
        # 检查变量文件中的关键变量和警告
        assert "config_fragments_dir" in vars_file, "assemble vars 应包含 config_fragments_dir 变量"
        assert "assembled_config_path" in vars_file, "assemble vars 应包含 assembled_config_path 变量"
        assert "⚠️" in vars_file or "警告" in vars_file or "注意" in vars_file, (
            "assemble vars 应包含安全提示"
        )

    def test_slurp_module_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """验证 slurp 模块包含特定内容"""
        slurp_path = module_dirs["slurp"]
        readme = (slurp_path / "README.md").read_text(encoding="utf-8")
        playbook = (slurp_path / "playbook.yml").read_text(encoding="utf-8")
        vars_file = (slurp_path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        
        # 检查 README 中的关键词
        assert "读取" in readme, "slurp 模块 README 应提及读取"
        assert "base64" in readme, "slurp 模块 README 应提及 base64"
        assert "敏感" in readme, "slurp 模块 README 应提及敏感信息"
        
        # 检查 playbook 中的 FQCN
        assert "ansible.builtin.slurp" in playbook, "slurp playbook 应使用 slurp 模块"
        
        # 检查 playbook 中的 vars_files
        assert "vars_files" in playbook, "slurp playbook 应引用 vars_files"
        
        # 检查 playbook 中的 check_mode
        assert "check_mode" in playbook, "slurp playbook 应包含 check_mode"
        
        # 检查 playbook 中的 no_log
        assert "no_log" in playbook, "slurp playbook 应包含 no_log 保护敏感信息"
        
        # 检查变量文件中的关键变量和警告
        assert "sample_config_path" in vars_file, "slurp vars 应包含 sample_config_path 变量"
        assert "sensitive_config_path" in vars_file, "slurp vars 应包含 sensitive_config_path 变量"
        assert "⚠️" in vars_file or "警告" in vars_file or "注意" in vars_file, (
            "slurp vars 应包含安全提示"
        )
