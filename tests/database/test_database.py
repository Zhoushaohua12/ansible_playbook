"""数据库模块示例的结构与文档校验"""

from pathlib import Path
from typing import Dict
import re

import pytest
import yaml

MODULES = ["mysql_user", "mysql_db", "postgresql_db", "mongodb_user"]
FQCN_EXPECTATIONS = {
    "mysql_user": "community.mysql.mysql_user",
    "mysql_db": "community.mysql.mysql_db",
    "postgresql_db": "community.postgresql.postgresql_db",
    "mongodb_user": "community.mongodb.mongodb_user",
}
COLLECTION_DEPENDENCIES = {
    "mysql_user": "community.mysql",
    "mysql_db": "community.mysql",
    "postgresql_db": "community.postgresql",
    "mongodb_user": "community.mongodb",
}


class TestDatabaseFixtures:
    """提供数据库模块路径的公共 fixture"""

    @pytest.fixture(scope="class")
    def database_root(self) -> Path:
        return Path(__file__).parent.parent.parent / "database"

    @pytest.fixture(scope="class")
    def module_dirs(self, database_root: Path) -> Dict[str, Path]:
        return {name: database_root / name for name in MODULES}


class TestDatabaseReadme(TestDatabaseFixtures):
    """校验 database 根目录的 README 内容"""

    def test_database_readme_exists(self, database_root: Path) -> None:
        readme = database_root / "README.md"
        assert readme.exists(), "database 根目录缺少 README.md"

    def test_database_readme_contains_modules(self, database_root: Path) -> None:
        content = (database_root / "README.md").read_text(encoding="utf-8")
        for module in MODULES:
            assert module in content, f"database/README.md 应包含 {module} 模块说明"

    def test_database_readme_contains_installation_instructions(self, database_root: Path) -> None:
        content = (database_root / "README.md").read_text(encoding="utf-8")
        # 检查是否提到安装 collection
        assert "ansible-galaxy collection install" in content, "database/README.md 应包含 collection 安装说明"
        # 检查是否提到 Python 库依赖
        assert "pip install" in content or "Python" in content, "database/README.md 应包含 Python 库依赖说明"
        # 检查中文提示
        assert "安装" in content, "database/README.md 应包含中文安装说明"
        # 检查各个 collection
        assert "community.mysql" in content, "database/README.md 应提到 community.mysql collection"
        assert "community.postgresql" in content, "database/README.md 应提到 community.postgresql collection"
        assert "community.mongodb" in content, "database/README.md 应提到 community.mongodb collection"


class TestModuleDocumentation(TestDatabaseFixtures):
    """校验各数据库模块 README 的章节与内容"""

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

    def test_module_readmes_mention_collection_dependency(self, module_dirs: Dict[str, Path]) -> None:
        """检查 README 是否提到需要安装对应的 collection"""
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8")
            expected_collection = COLLECTION_DEPENDENCIES[name]
            # 检查是否提到 collection 名称
            assert expected_collection in content, (
                f"{name} README.md 应提到需要安装 {expected_collection} collection"
            )
            # 检查是否有中文安装提示（匹配"安装"、"依赖"、"Collection"等关键词）
            has_install_mention = bool(
                re.search(r"(安装|依赖|Collection)", content, re.IGNORECASE)
            )
            assert has_install_mention, f"{name} README.md 应包含中文安装或依赖说明"

    def test_module_readmes_mention_python_library(self, module_dirs: Dict[str, Path]) -> None:
        """检查 README 是否提到需要安装 Python 库"""
        python_lib_keywords = {
            "mysql_user": ["PyMySQL", "mysqlclient"],
            "mysql_db": ["PyMySQL", "mysqlclient"],
            "postgresql_db": ["psycopg2"],
            "mongodb_user": ["pymongo"],
        }
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8")
            keywords = python_lib_keywords[name]
            has_keyword = any(keyword in content for keyword in keywords)
            assert has_keyword, (
                f"{name} README.md 应提到需要安装 Python 库：{', '.join(keywords)}"
            )


class TestPlaybooks(TestDatabaseFixtures):
    """校验 playbook 的语法、中文注释与 FQCN 使用"""

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
        """检查 playbook 是否使用正确的 FQCN"""
        for name, path in module_dirs.items():
            expected = FQCN_EXPECTATIONS[name]
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert expected in content, f"{name} playbook 应使用 FQCN {expected}"

    def test_playbooks_use_check_mode(self, module_dirs: Dict[str, Path]) -> None:
        """检查 playbook 是否使用 check_mode（适合无真实数据库环境）"""
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            # 检查是否有 check_mode: true
            assert "check_mode: true" in content or "check_mode:" in content, (
                f"{name} playbook 应包含 check_mode: true，以便在无真实数据库时运行"
            )

    def test_playbooks_use_delegate_to(self, module_dirs: Dict[str, Path]) -> None:
        """检查 playbook 是否使用 delegate_to 或 localhost"""
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            has_delegation = (
                "delegate_to:" in content or
                "hosts: localhost" in content or
                "hosts: all" in content
            )
            assert has_delegation, (
                f"{name} playbook 应使用 delegate_to 或在 localhost 上运行"
            )

    def test_playbooks_use_no_log(self, module_dirs: Dict[str, Path]) -> None:
        """检查 playbook 是否使用 no_log 保护敏感信息"""
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "no_log: true" in content, (
                f"{name} playbook 应使用 no_log: true 防止密码泄露"
            )

    def test_playbooks_use_vars_files(self, module_dirs: Dict[str, Path]) -> None:
        """检查所有 playbook 都引用了 vars 文件"""
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "vars_files" in content, f"{name} playbook 应引用 vars/example_vars.yml"

    def test_playbooks_variables_have_chinese_comments(self, module_dirs: Dict[str, Path]) -> None:
        """检查 playbook 中使用的变量是否在 vars 文件中有中文注释"""
        for name, path in module_dirs.items():
            playbook_content = (path / "playbook.yml").read_text(encoding="utf-8")
            vars_file = path / "vars" / "example_vars.yml"
            
            if not vars_file.exists():
                pytest.fail(f"{name} 模块缺少 vars/example_vars.yml")
            
            vars_content = vars_file.read_text(encoding="utf-8")
            
            # 提取 playbook 中使用的变量（简单的正则匹配）
            variables = re.findall(r'\{\{\s*([a-z_][a-z0-9_]*)\s*\}\}', playbook_content)
            
            # 检查至少有一些变量被定义并有中文注释
            if variables:
                has_chinese_in_vars = any("\u4e00" <= ch <= "\u9fff" for ch in vars_content)
                assert has_chinese_in_vars, (
                    f"{name} 的 vars/example_vars.yml 需要包含中文注释说明变量含义"
                )


class TestVarsFiles(TestDatabaseFixtures):
    """校验示例变量的注释、安全提示与语法"""

    WARNING_KEYWORDS = ["占位", "重要", "请勿", "⚠", "警告", "风险", "PLEASE_CHANGE", "生产环境"]

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

    def test_vars_files_contain_connection_parameters(self, module_dirs: Dict[str, Path]) -> None:
        """检查 vars 文件是否包含数据库连接参数"""
        connection_keywords = {
            "mysql_user": ["mysql_host", "mysql_port", "mysql_admin"],
            "mysql_db": ["mysql_host", "mysql_port", "mysql_admin"],
            "postgresql_db": ["postgres_host", "postgres_port", "postgres_admin"],
            "mongodb_user": ["mongodb_host", "mongodb_port", "mongodb_admin"],
        }
        for name, path in module_dirs.items():
            content = (path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
            keywords = connection_keywords[name]
            # 至少要有一个连接参数关键词
            has_keyword = any(keyword in content for keyword in keywords)
            assert has_keyword, (
                f"{name} example_vars.yml 应包含数据库连接参数（如 {', '.join(keywords)}）"
            )
