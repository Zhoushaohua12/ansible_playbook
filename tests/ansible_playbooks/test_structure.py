"""
测试 ansible-playbooks/ 工作区结构、文档与配置规范
"""

from pathlib import Path
from typing import List
import pytest
import yaml


PLAYBOOKS_ROOT = Path(__file__).parent.parent.parent / "ansible-playbooks"


class TestPlaybooksHubStructure:
    """验证 Playbook Hub 工作区的目录与文件组织"""

    def test_ansible_cfg_exists(self) -> None:
        """验证工作区配置文件存在"""
        ansible_cfg = PLAYBOOKS_ROOT / "ansible.cfg"
        assert ansible_cfg.exists(), "缺少 ansible.cfg"
        content = ansible_cfg.read_text(encoding="utf-8")
        assert "inventory" in content, "ansible.cfg 应包含 inventory 配置"
        assert "roles_path" in content, "ansible.cfg 应包含 roles_path 配置"

    def test_quick_start_exists(self) -> None:
        """验证快速上手文档存在"""
        quick_start = PLAYBOOKS_ROOT / "QUICK_START.md"
        assert quick_start.exists(), "缺少 QUICK_START.md"

    def test_quick_start_content(self) -> None:
        """验证快速上手文档内容包含必要章节"""
        quick_start = PLAYBOOKS_ROOT / "QUICK_START.md"
        content = quick_start.read_text(encoding="utf-8")

        # 必备章节
        assert "前提条件" in content or "Prerequisites" in content.lower(), "应包含前提条件章节"
        assert "安装依赖" in content, "应包含依赖安装说明"
        assert "ansible-galaxy" in content, "应包含 ansible-galaxy 命令"
        assert "准备 Inventory" in content or "Inventory" in content, "应包含 Inventory 准备说明"

        # 检查关键命令示例
        assert "--syntax-check" in content, "应包含语法检查命令示例"
        assert "--check" in content, "应包含检查模式命令示例"
        assert "--tags" in content, "应包含标签使用示例"
        assert "--limit" in content or "-l" in content, "应包含限制主机范围示例"

        # 故障排除
        assert "故障排除" in content or "troubleshooting" in content.lower(), "应包含故障排除章节"
        assert "SSH" in content, "应包含 SSH 连接故障排除"

    def test_top_level_directories_exist(self) -> None:
        """验证顶层场景目录存在"""
        required_dirs = [
            "system-init",
            "web-services",
            "database",
            "application-deploy",
            "monitoring",
            "maintenance",
            "inventory",
            "roles"
        ]
        for dir_name in required_dirs:
            dir_path = PLAYBOOKS_ROOT / dir_name
            assert dir_path.exists(), f"缺少 {dir_name} 目录"
            assert dir_path.is_dir(), f"{dir_name} 不是目录"

    def test_inventory_structure(self) -> None:
        """验证 inventory 目录结构"""
        inventory_dir = PLAYBOOKS_ROOT / "inventory"
        hosts_file = inventory_dir / "hosts"
        group_vars_dir = inventory_dir / "group_vars"

        assert hosts_file.exists(), "缺少 inventory/hosts 文件"
        assert group_vars_dir.exists(), "缺少 inventory/group_vars 目录"

    def test_inventory_hosts_content(self) -> None:
        """验证 inventory/hosts 文件内容"""
        hosts_file = PLAYBOOKS_ROOT / "inventory" / "hosts"
        content = hosts_file.read_text(encoding="utf-8")

        # 验证场景分组
        required_groups = [
            "[init_servers]",
            "[nginx_servers]",
            "[database_servers]",
            "[app_servers]",
            "[monitoring_servers]",
            "[backup_servers]",
        ]
        for group in required_groups:
            assert group in content, f"inventory/hosts 应包含 {group} 主机组"

        # 验证中文警告
        assert "⚠️" in content, "inventory/hosts 应包含中文警告符号"

    def test_group_vars_files_exist(self) -> None:
        """验证 group_vars 文件存在"""
        group_vars_dir = PLAYBOOKS_ROOT / "inventory" / "group_vars"
        required_files = [
            "all.yml",
            "init_servers.yml",
            "nginx_servers.yml",
            "database_servers.yml",
            "app_servers.yml",
            "monitoring_servers.yml",
            "backup_servers.yml"
        ]
        for filename in required_files:
            file_path = group_vars_dir / filename
            assert file_path.exists(), f"缺少 inventory/group_vars/{filename}"

    def test_group_vars_warning_headers(self) -> None:
        """验证所有 group_vars 文件包含中文警告头"""
        group_vars_dir = PLAYBOOKS_ROOT / "inventory" / "group_vars"
        for yml_file in group_vars_dir.glob("*.yml"):
            content = yml_file.read_text(encoding="utf-8")
            assert "⚠️" in content, f"{yml_file.name} 应包含中文警告符号"
            assert "警告" in content or "警示" in content or "重要" in content, \
                f"{yml_file.name} 应包含中文警告文字"

    def test_group_vars_vault_placeholders(self) -> None:
        """验证 group_vars 文件包含 vault_ 占位符"""
        group_vars_dir = PLAYBOOKS_ROOT / "inventory" / "group_vars"
        for yml_file in group_vars_dir.glob("*.yml"):
            content = yml_file.read_text(encoding="utf-8")
            if yml_file.name == "all.yml":
                # all.yml 必须包含 vault_ 变量
                assert "vault_" in content, f"{yml_file.name} 应包含 vault_ 前缀变量"

    def test_group_vars_valid_yaml(self) -> None:
        """验证所有 group_vars 文件是有效的 YAML"""
        group_vars_dir = PLAYBOOKS_ROOT / "inventory" / "group_vars"
        for yml_file in group_vars_dir.glob("*.yml"):
            try:
                yaml.safe_load(yml_file.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                pytest.fail(f"{yml_file.name} YAML 语法错误: {e}")

    def test_shared_roles_directory(self) -> None:
        """验证共享角色目录与文档"""
        roles_dir = PLAYBOOKS_ROOT / "roles"
        roles_readme = roles_dir / "README.md"

        assert roles_dir.exists(), "缺少共享 roles/ 目录"
        assert roles_readme.exists(), "缺少 roles/README.md"

        content = roles_readme.read_text(encoding="utf-8")
        assert "共用角色" in content or "共享角色" in content, \
            "roles/README.md 应说明共享角色用途"


class TestReadmeDocumentation:
    """验证 README 文档完整性与必备章节"""

    def test_main_readme_has_os_coverage_matrix(self) -> None:
        """验证主 README 包含操作系统覆盖矩阵"""
        readme = PLAYBOOKS_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")

        assert "操作系统" in content or "OS" in content, "应包含 OS 覆盖矩阵"
        assert "Ubuntu" in content, "应列出 Ubuntu 支持"
        assert "RHEL" in content or "CentOS" in content, "应列出 RHEL/CentOS 支持"

    def test_main_readme_has_fqcn_section(self) -> None:
        """验证主 README 说明 FQCN 要求"""
        readme = PLAYBOOKS_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")

        assert "FQCN" in content, "应说明 FQCN 使用规范"
        assert "ansible.builtin" in content or "community." in content, \
            "应给出 FQCN 示例"

    def test_main_readme_has_tags_section(self) -> None:
        """验证主 README 说明标签体系"""
        readme = PLAYBOOKS_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")

        assert "标签" in content or "tags" in content, "应说明标签使用"
        assert "--tags" in content, "应包含 --tags 命令示例"
        assert "--skip-tags" in content, "应包含 --skip-tags 示例"

    def test_main_readme_has_check_mode_section(self) -> None:
        """验证主 README 说明检查模式"""
        readme = PLAYBOOKS_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")

        assert "--check" in content, "应说明 --check 模式使用"
        assert "--syntax-check" in content, "应包含 --syntax-check 示例"
        assert "--diff" in content, "应包含 --diff 示例"

    def test_main_readme_links_to_subdirs(self) -> None:
        """验证主 README 链接所有子目录"""
        readme = PLAYBOOKS_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")

        required_links = [
            "system-init",
            "web-services",
            "database",
            "application-deploy",
            "monitoring",
            "maintenance",
            "QUICK_START.md"
        ]
        for link in required_links:
            assert link in content, f"README 应包含 {link} 链接"

    def test_main_readme_has_variables_organization_section(self) -> None:
        """验证主 README 说明变量组织方式"""
        readme = PLAYBOOKS_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")

        assert "变量" in content or "Variables" in content.lower(), \
            "应说明变量组织方式"
        assert "group_vars" in content or "inventory" in content, \
            "应说明 group_vars 使用"

    def test_main_readme_has_handlers_section(self) -> None:
        """验证主 README 说明 handlers 组织"""
        readme = PLAYBOOKS_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")

        assert "handler" in content.lower(), "应说明 handlers 组织"

    def test_main_readme_has_templates_section(self) -> None:
        """验证主 README 说明 templates 组织"""
        readme = PLAYBOOKS_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")

        assert "template" in content.lower(), "应说明 templates 组织"


class TestWebServicesStructure:
    """验证 web-services/ 目录结构"""

    def test_web_services_directory_structure(self) -> None:
        """验证 web-services 子目录完整性"""
        web_services_dir = PLAYBOOKS_ROOT / "web-services"
        required_subdirs = ["vars", "templates", "handlers", "roles"]

        for subdir in required_subdirs:
            subpath = web_services_dir / subdir
            assert subpath.exists(), f"web-services 缺少 {subdir} 目录"
            assert subpath.is_dir(), f"web-services/{subdir} 不是目录"

    def test_web_services_readme(self) -> None:
        """验证 web-services/README.md 存在且有内容"""
        readme = PLAYBOOKS_ROOT / "web-services" / "README.md"
        assert readme.exists(), "web-services 缺少 README.md"

        content = readme.read_text(encoding="utf-8")
        assert "Nginx" in content or "nginx" in content, "应包含 Nginx 说明"
        assert "Apache" in content or "apache" in content, "应包含 Apache 说明"
        assert "--syntax-check" in content, "应包含语法检查示例"


class TestInventoryIntegration:
    """验证 Inventory 与配置的集成"""

    def test_ansible_cfg_inventory_path(self) -> None:
        """验证 ansible.cfg 指向正确的 inventory 路径"""
        ansible_cfg = PLAYBOOKS_ROOT / "ansible.cfg"
        content = ansible_cfg.read_text(encoding="utf-8")

        assert "inventory/hosts" in content or "inventory = " in content, \
            "ansible.cfg 应配置 inventory 路径"

    def test_ansible_cfg_roles_path(self) -> None:
        """验证 ansible.cfg 配置了 roles_path"""
        ansible_cfg = PLAYBOOKS_ROOT / "ansible.cfg"
        content = ansible_cfg.read_text(encoding="utf-8")

        assert "roles_path" in content, "ansible.cfg 应配置 roles_path"
        assert "roles" in content, "roles_path 应包含共享 roles 目录"

    def test_group_vars_parse_as_yaml(self) -> None:
        """验证所有 group_vars 文件解析为合法 YAML"""
        group_vars_dir = PLAYBOOKS_ROOT / "inventory" / "group_vars"

        for yml_file in group_vars_dir.glob("*.yml"):
            try:
                data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
                # 确保解析后不是 None（空文件）
                assert data is not None or yml_file.stat().st_size < 50, \
                    f"{yml_file.name} 解析结果为空"
            except yaml.YAMLError as e:
                pytest.fail(f"{yml_file.name} YAML 解析失败: {e}")


class TestQuickStartCommands:
    """验证 QUICK_START.md 包含必要的命令示例"""

    def test_quick_start_has_ansible_galaxy_install(self) -> None:
        """验证快速上手包含 ansible-galaxy 安装命令"""
        quick_start = PLAYBOOKS_ROOT / "QUICK_START.md"
        content = quick_start.read_text(encoding="utf-8")

        assert "ansible-galaxy collection install" in content, \
            "应包含 ansible-galaxy collection install 命令"
        assert "requirements.yml" in content, \
            "应引用 requirements.yml"

    def test_quick_start_has_inventory_validation(self) -> None:
        """验证快速上手包含 inventory 验证命令"""
        quick_start = PLAYBOOKS_ROOT / "QUICK_START.md"
        content = quick_start.read_text(encoding="utf-8")

        assert "ansible-inventory" in content or "ansible all" in content, \
            "应包含 inventory 验证命令"

    def test_quick_start_has_syntax_check_example(self) -> None:
        """验证快速上手包含语法检查示例"""
        quick_start = PLAYBOOKS_ROOT / "QUICK_START.md"
        content = quick_start.read_text(encoding="utf-8")

        assert "--syntax-check" in content, "应包含 --syntax-check 命令"

    def test_quick_start_has_check_mode_example(self) -> None:
        """验证快速上手包含检查模式示例"""
        quick_start = PLAYBOOKS_ROOT / "QUICK_START.md"
        content = quick_start.read_text(encoding="utf-8")

        assert "--check" in content, "应包含 --check 命令"

    def test_quick_start_has_limit_example(self) -> None:
        """验证快速上手包含限制主机范围示例"""
        quick_start = PLAYBOOKS_ROOT / "QUICK_START.md"
        content = quick_start.read_text(encoding="utf-8")

        assert "--limit" in content or "-l" in content, \
            "应包含 --limit 或 -l 命令"

    def test_quick_start_has_tags_example(self) -> None:
        """验证快速上手包含标签使用示例"""
        quick_start = PLAYBOOKS_ROOT / "QUICK_START.md"
        content = quick_start.read_text(encoding="utf-8")

        assert "--tags" in content, "应包含 --tags 命令"

    def test_quick_start_has_ssh_troubleshooting(self) -> None:
        """验证快速上手包含 SSH 故障排除"""
        quick_start = PLAYBOOKS_ROOT / "QUICK_START.md"
        content = quick_start.read_text(encoding="utf-8")

        assert "SSH" in content, "应包含 SSH 相关说明"
        assert "连接" in content or "connection" in content.lower(), \
            "应包含连接故障排除"

    def test_quick_start_has_auth_troubleshooting(self) -> None:
        """验证快速上手包含认证故障排除"""
        quick_start = PLAYBOOKS_ROOT / "QUICK_START.md"
        content = quick_start.read_text(encoding="utf-8")

        assert "认证" in content or "auth" in content.lower() or "Vault" in content, \
            "应包含认证相关故障排除"

    def test_quick_start_has_config_troubleshooting(self) -> None:
        """验证快速上手包含配置故障排除"""
        quick_start = PLAYBOOKS_ROOT / "QUICK_START.md"
        content = quick_start.read_text(encoding="utf-8")

        assert "配置" in content or "config" in content.lower(), \
            "应包含配置相关故障排除"
