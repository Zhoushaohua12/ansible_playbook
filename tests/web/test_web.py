"""Web 服务模块示例的结构与文档校验"""

from pathlib import Path
from typing import Dict

import pytest
import yaml

MODULES = ["nginx", "apache2", "web_config"]


class TestWebFixtures:
    """提供 Web 模块路径的公共 fixture"""

    @pytest.fixture(scope="class")
    def web_root(self) -> Path:
        return Path(__file__).parent.parent.parent / "web"

    @pytest.fixture(scope="class")
    def module_dirs(self, web_root: Path) -> Dict[str, Path]:
        return {name: web_root / name for name in MODULES}


class TestWebReadme(TestWebFixtures):
    """校验 web 根目录的 README 内容"""

    def test_web_readme_exists(self, web_root: Path) -> None:
        readme = web_root / "README.md"
        assert readme.exists(), "web 根目录缺少 README.md"

    def test_web_readme_mentions_nginx_apache_web_config(self, web_root: Path) -> None:
        content = (web_root / "README.md").read_text(encoding="utf-8").lower()
        assert "nginx" in content, "web/README.md 应说明 Nginx 服务"
        assert "apache" in content, "web/README.md 应说明 Apache 服务"
        assert "反向代理" in content or "proxy" in content, "web/README.md 应说明反向代理场景"
        assert "静态站点" in content or "静态" in content, "web/README.md 应说明静态站点发布"

    def test_web_readme_mentions_system_applications_relationship(self, web_root: Path) -> None:
        content = (web_root / "README.md").read_text(encoding="utf-8")
        assert "system/applications" in content or "应用" in content, \
            "web/README.md 应说明与 system/applications 的配合关系"

    def test_web_readme_has_testing_instructions(self, web_root: Path) -> None:
        content = (web_root / "README.md").read_text(encoding="utf-8").lower()
        assert "--syntax-check" in content, "web/README.md 应提供 ansible-playbook --syntax-check 测试说明"
        assert "如何" in content or "测试" in content, "web/README.md 应包含中文测试指导"

    def test_web_readme_has_educational_disclaimer(self, web_root: Path) -> None:
        content = (web_root / "README.md").read_text(encoding="utf-8")
        assert "教学" in content or "学习" in content, "web/README.md 应声明示例主要用于教学目的"


class TestModuleDocumentation(TestWebFixtures):
    """校验各 Web 模块 README 的章节与内容"""

    REQUIRED_SECTIONS = ["服务简介", "常用模块", "参数", "日志路径", "常见部署场景"]

    def test_module_readmes_exist(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            readme = path / "README.md"
            assert readme.exists(), f"{name} 模块缺少 README.md"

    def test_module_readmes_have_required_sections(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8")
            for section in self.REQUIRED_SECTIONS:
                # 部分匹配即可（如"常用模块"或"常用 Ansible 模块"）
                # 检查完整匹配或前两个字匹配
                section_found = section in content or section[:2] in content
                assert section_found, \
                    f"{name} README.md 缺少包含 '{section}' 的章节"

    def test_module_readmes_mention_common_modules(self, module_dirs: Dict[str, Path]) -> None:
        """检查是否提及常用 Ansible 模块（apt/yum、template、service、ufw）"""
        common_modules = ["apt", "template", "service", "ufw"]
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8").lower()
            mentioned_count = sum(1 for mod in common_modules if mod in content)
            assert mentioned_count >= 3, \
                f"{name} README.md 应至少提及 3 个常用模块（apt/yum、template、service、ufw）"

    def test_module_readmes_have_testing_guidance(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8").lower()
            assert "--syntax-check" in content or "--check" in content, \
                f"{name} README.md 需说明如何在本地测试（ansible-playbook --syntax-check/--check）"
            assert "如何" in content or "测试" in content, \
                f"{name} README.md 应包含中文测试指导章节"


class TestPlaybooks(TestWebFixtures):
    """校验 playbook 的语法、中文注释与模块使用"""

    def test_playbooks_are_valid_yaml(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            playbook = path / "playbook.yml"
            assert playbook.exists(), f"{name} 模块缺少 playbook.yml"
            with playbook.open("r", encoding="utf-8") as handler:
                try:
                    yaml.safe_load(handler)
                except yaml.YAMLError as err:
                    pytest.fail(f"{name} playbook.yml 解析失败: {err}")

    def test_playbooks_contain_educational_disclaimer_and_chinese(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "教学" in content or "学习" in content or "仅供" in content, \
                f"{name} playbook 需包含教学声明或仅供演示的注释"
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"{name} playbook 需要使用中文任务名或注释"

    def test_playbooks_use_template_and_service_modules(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "template" in content.lower(), \
                f"{name} playbook 应使用 template 模块部署配置"
            assert "service" in content.lower(), \
                f"{name} playbook 应使用 service 模块管理服务"

    def test_playbooks_have_handlers_with_chinese_names(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "handlers:" in content, f"{name} playbook 应包含 handlers 用于重启服务"
            # 检查 handlers 部分是否有中文
            if "handlers:" in content:
                handlers_section = content.split("handlers:")[1].split("tasks:")[0] if "tasks:" in content else content.split("handlers:")[1]
                has_chinese_handler = any("\u4e00" <= ch <= "\u9fff" for ch in handlers_section)
                assert has_chinese_handler, f"{name} playbook 的 handlers 名称应中文化"

    def test_playbooks_reference_vars_files(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "vars_files" in content or "vars:" in content, \
                f"{name} playbook 应引用 vars/example_vars.yml 或定义变量"


class TestTemplates(TestWebFixtures):
    """校验模板文件存在且包含中文注释"""

    EXPECTED_TEMPLATES = {
        "nginx": ["nginx.conf.j2", "vhost.conf.j2"],
        "apache2": ["apache.conf.j2", "security.conf.j2"],
        "web_config": ["proxy_nginx.conf.j2", "proxy_apache.conf.j2", 
                       "static_nginx.conf.j2", "static_apache.conf.j2"],
    }

    def test_template_directories_exist(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            templates_dir = path / "templates"
            assert templates_dir.exists(), f"{name} 模块缺少 templates 目录"

    def test_expected_templates_exist(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            expected = self.EXPECTED_TEMPLATES.get(name, [])
            for template_name in expected:
                template_file = path / "templates" / template_name
                assert template_file.exists(), f"{name} 模块缺少模板文件 {template_name}"

    def test_templates_contain_chinese_comments(self, module_dirs: Dict[str, Path]) -> None:
        """验证模板文件包含中文注释描述关键段落"""
        for name, path in module_dirs.items():
            templates_dir = path / "templates"
            if templates_dir.exists():
                template_files = list(templates_dir.glob("*.j2"))
                assert len(template_files) > 0, f"{name} templates 目录中没有 .j2 文件"
                
                for template_file in template_files:
                    content = template_file.read_text(encoding="utf-8")
                    has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
                    assert has_chinese, f"{name} 的模板文件 {template_file.name} 需包含中文注释"


class TestVarsFiles(TestWebFixtures):
    """校验示例变量的注释与安全提示"""

    WARNING_KEYWORDS = ["占位", "重要", "请勿", "⚠", "安全"]

    def test_vars_directories_exist(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            vars_dir = path / "vars"
            assert vars_dir.exists(), f"{name} 模块缺少 vars 目录"

    def test_vars_files_exist_and_valid_yaml(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            vars_file = path / "vars" / "example_vars.yml"
            assert vars_file.exists(), f"{name} 模块缺少 vars/example_vars.yml"
            try:
                yaml.safe_load(vars_file.read_text(encoding="utf-8"))
            except yaml.YAMLError as err:
                pytest.fail(f"{name} example_vars.yml 解析失败: {err}")

    def test_vars_files_have_chinese_comments_and_warnings(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"{name} example_vars.yml 需包含中文注释"
            assert any(keyword in content for keyword in self.WARNING_KEYWORDS), \
                f"{name} example_vars.yml 需提示变量为占位或包含安全警告"
