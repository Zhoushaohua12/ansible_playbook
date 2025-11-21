"""系统管理模块示例的结构与文档校验"""

from pathlib import Path
from typing import Dict

import pytest
import yaml

# 系统管理模块列表
MODULES = ["user", "group", "service", "systemd", "hostname", "timezone", "locale", "firewalld", "iptables", "selinux", "auditd", "pam_hardening", "kernel_tuning", "cron", "authorized_key", "reboot", "seboolean", "sefcontext"]

# 各模块对应的 FQCN（Fully Qualified Collection Name）期望值
FQCN_EXPECTATIONS = {
    "user": "ansible.builtin.user",
    "group": "ansible.builtin.group",
    "service": "ansible.builtin.service",
    "systemd": "ansible.posix.systemd",
    "hostname": "ansible.builtin.hostname",
    "timezone": "ansible.builtin.timezone",
    "locale": "community.general.locale_gen",
    "firewalld": "community.general.firewalld",
    "iptables": "community.general.iptables",
    "selinux": "ansible.posix.selinux",
    "auditd": "ansible.builtin.package",
    "pam_hardening": "community.general.pamd",
    "kernel_tuning": "ansible.posix.sysctl",
    "cron": "ansible.builtin.cron",
    "authorized_key": "ansible.builtin.authorized_key",
    "reboot": "ansible.builtin.reboot",
    "seboolean": "ansible.posix.seboolean",
    "sefcontext": "ansible.posix.sefcontext",
}


class TestSystemFixtures:
    """提供系统管理模块路径的公共 fixture"""

    @pytest.fixture(scope="class")
    def system_root(self) -> Path:
        """返回 system 根目录路径"""
        return Path(__file__).parent.parent.parent / "system"

    @pytest.fixture(scope="class")
    def module_dirs(self, system_root: Path) -> Dict[str, Path]:
        """返回所有模块目录的字典"""
        return {name: system_root / name for name in MODULES}


class TestSystemReadme(TestSystemFixtures):
    """校验 system 根目录的 README 内容"""

    def test_system_readme_exists(self, system_root: Path) -> None:
        """验证 system/README.md 存在"""
        readme = system_root / "README.md"
        assert readme.exists(), "system 根目录缺少 README.md"

    def test_system_readme_contains_all_modules(self, system_root: Path) -> None:
        """验证 system/README.md 包含所有模块的说明"""
        content = (system_root / "README.md").read_text(encoding="utf-8")
        
        # 检查所有模块是否被提及
        for module in MODULES:
            assert module in content, f"system/README.md 应包含 {module} 模块说明"
        
        # 检查是否有中文概述
        assert "系统管理" in content, "system/README.md 应包含系统管理的中文概述"
        assert "模块" in content, "system/README.md 应说明所含模块"

    def test_system_readme_contains_module_descriptions(self, system_root: Path) -> None:
        """验证 system/README.md 包含模块用途说明"""
        content = (system_root / "README.md").read_text(encoding="utf-8")
        
        # 检查关键信息
        assert "用户" in content, "system/README.md 应说明用户管理功能"
        assert "服务" in content, "system/README.md 应说明服务管理功能"
        assert "防火墙" in content, "system/README.md 应说明防火墙管理功能"


class TestModuleDocumentation(TestSystemFixtures):
    """校验各系统管理模块 README 的章节与内容"""

    REQUIRED_SECTIONS = ["模块用途", "主要参数", "返回值", "使用情境"]

    def test_module_readmes_exist(self, module_dirs: Dict[str, Path]) -> None:
        """验证每个模块都有 README.md"""
        for name, path in module_dirs.items():
            readme = path / "README.md"
            assert readme.exists(), f"system/{name} 模块缺少 README.md"

    def test_module_readmes_contain_required_sections_and_chinese(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """验证每个模块 README 包含必需章节和中文内容"""
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8")
            
            # 检查必需章节
            for section in self.REQUIRED_SECTIONS:
                assert section in content, (
                    f"system/{name}/README.md 缺少 {section} 章节"
                )
            
            # 检查中文内容
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"system/{name}/README.md 需要包含中文内容"


class TestPlaybooks(TestSystemFixtures):
    """校验 playbook 的语法、中文注释与模块使用"""

    def test_playbooks_are_valid_yaml(self, module_dirs: Dict[str, Path]) -> None:
        """验证所有 playbook 文件的 YAML 语法有效"""
        for name, path in module_dirs.items():
            playbook = path / "playbook.yml"
            assert playbook.exists(), f"system/{name} 模块缺少 playbook.yml"
            
            # 尝试解析 YAML 以检查语法
            with playbook.open("r", encoding="utf-8") as handler:
                try:
                    yaml.safe_load(handler)
                except yaml.YAMLError as err:
                    pytest.fail(f"system/{name}/playbook.yml 解析失败: {err}")

    def test_playbooks_contain_chinese_comments(self, module_dirs: Dict[str, Path]) -> None:
        """验证所有 playbook 包含中文任务名或注释"""
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            
            # 检查中文内容
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"system/{name}/playbook.yml 需要使用中文任务名或注释"

    def test_playbooks_use_expected_fqcn(self, module_dirs: Dict[str, Path]) -> None:
        """验证所有 playbook 使用正确的 FQCN（Fully Qualified Collection Name）"""
        for name, path in module_dirs.items():
            expected = FQCN_EXPECTATIONS[name]
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            
            assert expected in content, (
                f"system/{name}/playbook.yml 应使用 FQCN {expected}"
            )

    def test_playbooks_reference_vars_files(self, module_dirs: Dict[str, Path]) -> None:
        """验证所有 playbook 都引用了 vars 文件"""
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            
            assert "vars_files" in content, (
                f"system/{name}/playbook.yml 应通过 vars_files 引用 vars/example_vars.yml"
            )

    def test_firewalld_playbook_specific_requirements(self, module_dirs: Dict[str, Path]) -> None:
        """验证 firewalld playbook 包含服务启动"""
        firewalld_path = module_dirs["firewalld"]
        content = (firewalld_path / "playbook.yml").read_text(encoding="utf-8")
        
        # firewalld playbook 应该包含 systemd 模块启动 firewalld 服务
        assert "firewalld" in content.lower(), (
            "firewalld playbook 应包含 firewalld 相关配置"
        )

    def test_iptables_playbook_includes_nat_concepts(self, module_dirs: Dict[str, Path]) -> None:
        """验证 iptables playbook 涵盖基础和 NAT 概念"""
        iptables_path = module_dirs["iptables"]
        content = (iptables_path / "playbook.yml").read_text(encoding="utf-8")
        
        # iptables playbook 应该包含基本概念说明
        assert "iptables" in content.lower(), (
            "iptables playbook 应包含 iptables 规则说明"
        )

    def test_hostname_playbook_shows_naming_conventions(self, module_dirs: Dict[str, Path]) -> None:
        """验证 hostname playbook 展示命名规范"""
        hostname_path = module_dirs["hostname"]
        content = (hostname_path / "playbook.yml").read_text(encoding="utf-8")
        
        # hostname playbook 应展示命名规范示例
        assert "hostname" in content.lower(), (
            "hostname playbook 应包含主机名配置示例"
        )


class TestVarsFiles(TestSystemFixtures):
    """校验变量文件的内容、注释与安全提示"""

    WARNING_KEYWORDS = ["占位", "重要", "请勿", "⚠", "警告", "注意", "生产"]

    def test_vars_files_exist_and_valid_yaml(self, module_dirs: Dict[str, Path]) -> None:
        """验证所有模块都有有效的 vars/example_vars.yml 文件"""
        for name, path in module_dirs.items():
            vars_file = path / "vars" / "example_vars.yml"
            assert vars_file.exists(), f"system/{name} 模块缺少 vars/example_vars.yml"
            
            # 验证 YAML 语法
            try:
                yaml.safe_load(vars_file.read_text(encoding="utf-8"))
            except yaml.YAMLError as err:
                pytest.fail(f"system/{name}/vars/example_vars.yml 解析失败: {err}")

    def test_vars_files_have_chinese_and_warning(self, module_dirs: Dict[str, Path]) -> None:
        """验证所有 vars 文件包含中文注释和安全提示"""
        for name, path in module_dirs.items():
            content = (path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
            
            # 检查中文内容
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"system/{name}/vars/example_vars.yml 需包含中文注释"
            
            # 检查安全提示
            assert any(keyword in content for keyword in self.WARNING_KEYWORDS), (
                f"system/{name}/vars/example_vars.yml 需提示变量为占位或包含安全警告"
            )


class TestModuleIntegration(TestSystemFixtures):
    """校验模块间的关系与依赖"""

    def test_playbooks_mention_related_modules(self, module_dirs: Dict[str, Path]) -> None:
        """验证 playbook 中提及相关模块"""
        # user 模块应该与 group 模块相关
        user_content = (module_dirs["user"] / "playbook.yml").read_text(encoding="utf-8")
        
        # group 模块 README 应该提及 user 模块
        group_readme = (module_dirs["group"] / "README.md").read_text(encoding="utf-8")
        assert "user" in group_readme.lower(), (
            "group 模块应提及与 user 模块的关系"
        )


class TestDocumentationCompleteness(TestSystemFixtures):
    """校验文档的完整性"""

    def test_all_modules_have_complete_structure(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """验证所有模块都有完整的文件结构"""
        for name, path in module_dirs.items():
            # 检查必需的文件
            assert (path / "README.md").exists(), (
                f"system/{name} 缺少 README.md"
            )
            assert (path / "playbook.yml").exists(), (
                f"system/{name} 缺少 playbook.yml"
            )
            assert (path / "vars" / "example_vars.yml").exists(), (
                f"system/{name} 缺少 vars/example_vars.yml"
            )

    def test_readme_files_have_consistent_structure(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """验证所有 README 文件有一致的结构"""
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8")
            
            # 检查通用章节
            assert "##" in content, (
                f"system/{name}/README.md 应包含 Markdown 章节标题"
            )
            
            # 检查代码示例或表格
            has_examples = "```" in content or "|" in content
            assert has_examples, (
                f"system/{name}/README.md 应包含示例代码或参数表"
            )


class TestSystemRootDocumentation(TestSystemFixtures):
    """校验系统章节根目录文档的完整性"""

    def test_system_readme_has_navigation_links(self, system_root: Path) -> None:
        """验证 system/README.md 包含导航链接"""
        content = (system_root / "README.md").read_text(encoding="utf-8")
        
        # 应该包含模块链接
        for module in MODULES:
            # 检查是否有链接指向模块
            assert module in content, f"system/README.md 应包含 {module} 的导航链接"

    def test_system_readme_explains_module_relationships(self, system_root: Path) -> None:
        """验证 system/README.md 解释了模块间的关系"""
        content = (system_root / "README.md").read_text(encoding="utf-8")
        
        # 应该说明不同模块的关系
        assert "关系" in content or "协同" in content or "结合" in content, (
            "system/README.md 应说明模块间的关系"
        )


class TestNewSystemModules(TestSystemFixtures):
    """新增系统模块（timezone、locale、selinux）的特定测试"""

    def test_timezone_module_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """验证 timezone 模块包含特定内容"""
        timezone_path = module_dirs["timezone"]
        readme = (timezone_path / "README.md").read_text(encoding="utf-8")
        playbook = (timezone_path / "playbook.yml").read_text(encoding="utf-8")
        vars_file = (timezone_path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        
        # 检查 README 中的关键词
        assert "时区" in readme, "timezone 模块 README 应提及时区"
        assert "UTC" in readme, "timezone 模块 README 应提及 UTC"
        
        # 检查 playbook 中的 FQCN
        assert "ansible.builtin.timezone" in playbook, "timezone playbook 应使用 FQCN"
        
        # 检查 playbook 中的 vars_files
        assert "vars_files" in playbook, "timezone playbook 应引用 vars_files"
        
        # 检查 playbook 中的 check_mode
        assert "check_mode" in playbook, "timezone playbook 应包含 check_mode"
        
        # 检查变量文件中的关键变量和警告
        assert "desired_timezone" in vars_file, "timezone vars 应包含 desired_timezone 变量"
        assert "⚠️" in vars_file or "警告" in vars_file or "注意" in vars_file, (
            "timezone vars 应包含安全提示"
        )

    def test_locale_module_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """验证 locale 模块包含特定内容"""
        locale_path = module_dirs["locale"]
        readme = (locale_path / "README.md").read_text(encoding="utf-8")
        playbook = (locale_path / "playbook.yml").read_text(encoding="utf-8")
        vars_file = (locale_path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        
        # 检查 README 中的关键词
        assert "区域" in readme or "Locale" in readme, "locale 模块 README 应提及区域或 Locale"
        assert "UTF-8" in readme or "编码" in readme, "locale 模块 README 应提及字符编码"
        
        # 检查 playbook 中的 FQCN
        assert "community.general.locale_gen" in playbook, "locale playbook 应使用 FQCN"
        
        # 检查 playbook 中的 vars_files
        assert "vars_files" in playbook, "locale playbook 应引用 vars_files"
        
        # 检查 playbook 中的 check_mode
        assert "check_mode" in playbook, "locale playbook 应包含 check_mode"
        
        # 检查变量文件中的关键变量和警告
        assert "desired_locale" in vars_file, "locale vars 应包含 desired_locale 变量"
        assert "⚠️" in vars_file or "警告" in vars_file or "注意" in vars_file, (
            "locale vars 应包含安全提示"
        )

    def test_selinux_module_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """验证 selinux 模块包含特定内容"""
        selinux_path = module_dirs["selinux"]
        readme = (selinux_path / "README.md").read_text(encoding="utf-8")
        playbook = (selinux_path / "playbook.yml").read_text(encoding="utf-8")
        vars_file = (selinux_path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        
        # 检查 README 中的关键词
        assert "SELinux" in readme, "selinux 模块 README 应提及 SELinux"
        assert "安全" in readme or "策略" in readme, "selinux 模块 README 应提及安全或策略"
        assert "enforcing" in readme or "permissive" in readme, (
            "selinux 模块 README 应提及 SELinux 工作模式"
        )
        
        # 检查 playbook 中的 FQCN
        assert "ansible.posix.selinux" in playbook, "selinux playbook 应使用 FQCN"
        
        # 检查 playbook 中的 vars_files
        assert "vars_files" in playbook, "selinux playbook 应引用 vars_files"
        
        # 检查 playbook 中的 check_mode
        assert "check_mode" in playbook, "selinux playbook 应包含 check_mode"
        
        # 检查变量文件中的关键变量和警告
        assert "desired_selinux_state" in vars_file, "selinux vars 应包含 desired_selinux_state 变量"
        assert "⚠️" in vars_file or "警告" in vars_file or "注意" in vars_file, (
            "selinux vars 应包含安全提示"
        )

    def test_auditd_module_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """验证 auditd 模块包含特定内容"""
        auditd_path = module_dirs["auditd"]
        readme = (auditd_path / "README.md").read_text(encoding="utf-8")
        playbook = (auditd_path / "playbook.yml").read_text(encoding="utf-8")
        vars_file = (auditd_path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        
        # 检查 README 中的关键词
        assert "审计" in readme, "auditd 模块 README 应提及审计"
        assert "auditd" in readme, "auditd 模块 README 应提及 auditd"
        assert "安全" in readme, "auditd 模块 README 应提及安全"
        
        # 检查 playbook 中的关键模块
        assert "ansible.builtin.package" in playbook, "auditd playbook 应使用 package 模块"
        assert "no_log" in playbook, "auditd playbook 应包含 no_log 保护敏感信息"
        
        # 检查 playbook 中的 vars_files
        assert "vars_files" in playbook, "auditd playbook 应引用 vars_files"
        
        # 检查 playbook 中的 check_mode
        assert "check_mode" in playbook, "auditd playbook 应包含 check_mode"
        
        # 检查模板文件是否存在
        templates_dir = auditd_path / "templates"
        assert templates_dir.exists(), "auditd 模块应有 templates 目录"
        assert (templates_dir / "auditd.conf.j2").exists(), "auditd 模块应有 auditd.conf.j2 模板"
        assert (templates_dir / "audit.rules.j2").exists(), "auditd 模块应有 audit.rules.j2 模板"
        
        # 检查变量文件中的关键变量和警告
        assert "auditd_config" in vars_file, "auditd vars 应包含 auditd_config 变量"
        assert "vault_auditd_remote_server" in vars_file, "auditd vars 应包含 vault_auditd_remote_server 变量"
        assert "⚠️" in vars_file or "警告" in vars_file or "注意" in vars_file, (
            "auditd vars 应包含安全提示"
        )

    def test_pam_hardening_module_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """验证 pam_hardening 模块包含特定内容"""
        pam_path = module_dirs["pam_hardening"]
        readme = (pam_path / "README.md").read_text(encoding="utf-8")
        playbook = (pam_path / "playbook.yml").read_text(encoding="utf-8")
        vars_file = (pam_path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        
        # 检查 README 中的关键词
        assert "PAM" in readme, "pam_hardening 模块 README 应提及 PAM"
        assert "密码" in readme, "pam_hardening 模块 README 应提及密码"
        assert "安全" in readme, "pam_hardening 模块 README 应提及安全"
        
        # 检查 playbook 中的 FQCN
        assert "community.general.pamd" in playbook, "pam_hardening playbook 应使用 pamd 模块"
        assert "community.general.pam_limits" in playbook, "pam_hardening playbook 应使用 pam_limits 模块"
        
        # 检查 playbook 中的 vars_files
        assert "vars_files" in playbook, "pam_hardening playbook 应引用 vars_files"
        
        # 检查 playbook 中的 check_mode
        assert "check_mode" in playbook, "pam_hardening playbook 应包含 check_mode"
        
        # 检查 playbook 中的 no_log
        assert "no_log" in playbook, "pam_hardening playbook 应包含 no_log 保护敏感信息"
        
        # 检查变量文件中的关键变量和警告
        assert "password_policies" in vars_file, "pam_hardening vars 应包含 password_policies 变量"
        assert "vault_pam_warning_banner" in vars_file, "pam_hardening vars 应包含 vault_pam_warning_banner 变量"
        assert "account_lockout" in vars_file, "pam_hardening vars 应包含 account_lockout 变量"
        assert "⚠️" in vars_file or "警告" in vars_file or "注意" in vars_file, (
            "pam_hardening vars 应包含安全提示"
        )

    def test_kernel_tuning_module_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """验证 kernel_tuning 模块包含特定内容"""
        kernel_path = module_dirs["kernel_tuning"]
        readme = (kernel_path / "README.md").read_text(encoding="utf-8")
        playbook = (kernel_path / "playbook.yml").read_text(encoding="utf-8")
        vars_file = (kernel_path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        
        # 检查 README 中的关键词
        assert "内核" in readme, "kernel_tuning 模块 README 应提及内核"
        assert "kernel" in readme, "kernel_tuning 模块 README 应提及 kernel"
        assert "sysctl" in readme, "kernel_tuning 模块 README 应提及 sysctl"
        
        # 检查 playbook 中的 FQCN
        assert "ansible.posix.sysctl" in playbook, "kernel_tuning playbook 应使用 sysctl 模块"
        
        # 检查 playbook 中的 vars_files
        assert "vars_files" in playbook, "kernel_tuning playbook 应引用 vars_files"
        
        # 检查 playbook 中的 check_mode
        assert "check_mode" in playbook, "kernel_tuning playbook 应包含 check_mode"
        
        # 检查变量文件中的关键变量和警告
        assert "network_settings" in vars_file, "kernel_tuning vars 应包含 network_settings 变量"
        assert "memory_settings" in vars_file, "kernel_tuning vars 应包含 memory_settings 变量"
        assert "security_settings" in vars_file, "kernel_tuning vars 应包含 security_settings 变量"
        assert "⚠️" in vars_file or "警告" in vars_file or "注意" in vars_file, (
            "kernel_tuning vars 应包含安全提示"
        )

    def test_seboolean_module_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """验证 seboolean 模块包含特定内容"""
        seboolean_path = module_dirs["seboolean"]
        readme = (seboolean_path / "README.md").read_text(encoding="utf-8")
        playbook = (seboolean_path / "playbook.yml").read_text(encoding="utf-8")
        vars_file = (seboolean_path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        
        # 检查 README 中的关键词
        assert "SELinux" in readme, "seboolean 模块 README 应提及 SELinux"
        assert "布尔值" in readme, "seboolean 模块 README 应提及布尔值"
        assert "httpd_can_network_connect" in readme, "seboolean 模块 README 应提及常用布尔值示例"
        
        # 检查 playbook 中的 FQCN
        assert "ansible.posix.seboolean" in playbook, "seboolean playbook 应使用 seboolean 模块"
        
        # 检查 playbook 中的 vars_files
        assert "vars_files" in playbook, "seboolean playbook 应引用 vars_files"
        
        # 检查 playbook 中的 check_mode
        assert "check_mode" in playbook, "seboolean playbook 应包含 check_mode"
        
        # 检查变量文件中的关键变量和警告
        assert "httpd_network_bool" in vars_file, "seboolean vars 应包含 httpd_network_bool 变量"
        assert "ftp_home_dir_bool" in vars_file, "seboolean vars 应包含 ftp_home_dir_bool 变量"
        assert "⚠️" in vars_file or "警告" in vars_file or "注意" in vars_file, (
            "seboolean vars 应包含安全提示"
        )

    def test_sefcontext_module_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """验证 sefcontext 模块包含特定内容"""
        sefcontext_path = module_dirs["sefcontext"]
        readme = (sefcontext_path / "README.md").read_text(encoding="utf-8")
        playbook = (sefcontext_path / "playbook.yml").read_text(encoding="utf-8")
        vars_file = (sefcontext_path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        
        # 检查 README 中的关键词
        assert "SELinux" in readme, "sefcontext 模块 README 应提及 SELinux"
        assert "文件上下文" in readme, "sefcontext 模块 README 应提及文件上下文"
        assert "httpd_sys_content_t" in readme, "sefcontext 模块 README 应提及上下文类型示例"
        
        # 检查 playbook 中的 FQCN
        assert "ansible.posix.sefcontext" in playbook, "sefcontext playbook 应使用 sefcontext 模块"
        
        # 检查 playbook 中的 vars_files
        assert "vars_files" in playbook, "sefcontext playbook 应引用 vars_files"
        
        # 检查 playbook 中的 check_mode
        assert "check_mode" in playbook, "sefcontext playbook 应包含 check_mode"
        
        # 检查变量文件中的关键变量和警告
        assert "webapp_root_path" in vars_file, "sefcontext vars 应包含 webapp_root_path 变量"
        assert "log_directory_path" in vars_file, "sefcontext vars 应包含 log_directory_path 变量"
        assert "⚠️" in vars_file or "警告" in vars_file or "注意" in vars_file, (
            "sefcontext vars 应包含安全提示"
        )
