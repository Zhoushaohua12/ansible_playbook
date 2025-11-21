"""网络模块示例的结构与文档校验"""

from pathlib import Path
from typing import Dict

import pytest
import yaml

MODULES = ["firewalld", "ufw", "iptables", "wait_for", "port", "route", "interface", "nmcli", "vlan", "bonding"]
FQCN_EXPECTATIONS = {
    "firewalld": "community.general.firewalld",
    "ufw": "community.general.ufw",
    "iptables": "community.general.iptables",
    "wait_for": "ansible.builtin.wait_for",
    "port": "ansible.builtin.wait_for",
    "route": "ansible.posix.route",
    "interface": "community.general.nmcli",
    "nmcli": "community.general.nmcli",
    "vlan": "community.general.nmcli",
    "bonding": "community.general.nmcli",
}
EXTERNAL_DEPS = {
    "firewalld": "community.general collection",
    "ufw": "community.general collection",
    "iptables": "community.general collection",
    "wait_for": "ansible.builtin (内置)",
    "port": "ansible.builtin (内置)",
    "route": "ansible.posix collection",
    "interface": "community.general collection",
    "nmcli": "community.general collection",
    "vlan": "community.general collection",
    "bonding": "community.general collection",
}


class TestNetworkFixtures:
    """提供网络模块路径的公共 fixture"""

    @pytest.fixture(scope="class")
    def network_root(self) -> Path:
        return Path(__file__).parent.parent.parent / "network"

    @pytest.fixture(scope="class")
    def module_dirs(self, network_root: Path) -> Dict[str, Path]:
        return {name: network_root / name for name in MODULES}


class TestNetworkReadme(TestNetworkFixtures):
    """校验 network 根目录的 README 内容"""

    def test_network_readme_exists(self, network_root: Path) -> None:
        readme = network_root / "README.md"
        assert readme.exists(), "network 根目录缺少 README.md"

    def test_network_readme_contains_module_overview(self, network_root: Path) -> None:
        content = (network_root / "README.md").read_text(encoding="utf-8")
        assert "firewalld" in content, "network/README.md 应包含 firewalld 模块说明"
        assert "ufw" in content, "network/README.md 应包含 ufw 模块说明"
        assert "iptables" in content, "network/README.md 应包含 iptables 模块说明"
        assert "wait_for" in content, "network/README.md 应包含 wait_for 模块说明"
        assert "port" in content, "network/README.md 应包含 port 模块说明"
        assert "route" in content, "network/README.md 应包含 route 模块说明"
        assert "interface" in content, "network/README.md 应包含 interface 模块说明"

    def test_network_readme_contains_system_firewall_distinction(
        self, network_root: Path
    ) -> None:
        content = (network_root / "README.md").read_text(encoding="utf-8")
        assert "system/firewall" in content, (
            "network/README.md 应说明与 system/firewall 的区别"
        )
        assert "防火墙" in content, "network/README.md 应用中文说明防火墙概念"

    def test_network_readme_contains_usage_scenarios(self, network_root: Path) -> None:
        content = (network_root / "README.md").read_text(encoding="utf-8")
        assert "分层环境" in content, "network/README.md 应包含分层部署场景"
        assert "远程主机" in content, "network/README.md 应包含远程主机场景"
        assert "安全" in content, "network/README.md 应包含安全相关内容"


class TestModuleDocumentation(TestNetworkFixtures):
    """校验各网络模块 README 的章节与内容"""

    REQUIRED_SECTIONS = ["模块用途", "主要参数", "返回值", "使用情境", "适用场景"]

    def test_module_readmes_exist(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            readme = path / "README.md"
            assert readme.exists(), f"{name} 模块缺少 README.md"

    def test_module_readmes_contain_required_sections_and_chinese(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8")
            for section in self.REQUIRED_SECTIONS:
                # Check for both "使用情境" and "适用场景" to handle different naming conventions
                if section == "使用情境":
                    has_section = "使用情境" in content or "适用场景" in content
                elif section == "适用场景":
                    has_section = "使用情境" in content or "适用场景" in content
                else:
                    has_section = section in content
                
                assert has_section, f"{name} README.md 缺少 {section} 章节"
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"{name} README.md 需要包含中文内容"

    def test_module_readmes_contain_external_deps(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8")
            expected_dep = EXTERNAL_DEPS[name]
            assert (
                expected_dep in content
                or "community.general" in content
                or "ansible.builtin" in content
            ), f"{name} README.md 应说明外部依赖要求"


class TestPlaybooks(TestNetworkFixtures):
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

    def test_playbooks_contain_chinese_comments(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"{name} playbook 需要使用中文任务名或注释"

    def test_playbooks_use_expected_fqcn(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            expected = FQCN_EXPECTATIONS[name]
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert expected in content, (
                f"{name} playbook 应使用 FQCN {expected}"
            )

    def test_playbooks_reference_ports(self, module_dirs: Dict[str, Path]) -> None:
        """检查 firewall 模块提到了端口配置"""
        firewall_modules = ["firewalld", "ufw", "iptables"]
        for name in firewall_modules:
            if name in module_dirs:
                path = module_dirs[name]
                content = (path / "playbook.yml").read_text(encoding="utf-8")
                # 应该提到端口或服务相关内容
                assert (
                    "port" in content
                    or "service" in content
                    or "端口" in content
                    or "服务" in content
                ), f"{name} playbook 应包含端口或服务相关配置"

    def test_wait_for_playbook_contains_port_monitoring(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 wait_for 模块包含端口监控"""
        wait_for_path = module_dirs["wait_for"]
        content = (wait_for_path / "playbook.yml").read_text(encoding="utf-8")
        assert "port" in content, "wait_for playbook 应包含端口监控示例"

    def test_firewall_playbooks_use_vars_files(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查防火墙模块 playbook 都引用了 vars 文件"""
        for name in ["firewalld", "ufw", "iptables"]:
            if name in module_dirs:
                path = module_dirs[name]
                content = (path / "playbook.yml").read_text(encoding="utf-8")
                assert "vars_files" in content, (
                    f"{name} playbook 应引用 vars/example_vars.yml"
                )

    def test_port_playbook_contains_delegate_to_and_timeout(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 port 模块包含 delegate_to、timeout/sleep/state 参数"""
        port_path = module_dirs["port"]
        content = (port_path / "playbook.yml").read_text(encoding="utf-8")
        assert "delegate_to: localhost" in content, (
            "port playbook 应使用 delegate_to: localhost"
        )
        assert "timeout" in content, "port playbook 应包含 timeout 参数"
        assert "sleep" in content, "port playbook 应包含 sleep 参数"
        assert "state" in content, "port playbook 应包含 state 参数"
        assert "vars_files" in content, "port playbook 应引用 vars 文件"

    def test_route_playbook_contains_ansible_posix_route(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 route 模块包含 ansible.posix.route、state、metric 参数"""
        route_path = module_dirs["route"]
        content = (route_path / "playbook.yml").read_text(encoding="utf-8")
        assert "ansible.posix.route" in content, (
            "route playbook 应使用 ansible.posix.route"
        )
        assert "state" in content, "route playbook 应包含 state 参数"
        assert "metric" in content, "route playbook 应包含 metric 参数"
        assert "vars_files" in content, "route playbook 应引用 vars 文件"

    def test_interface_playbook_contains_nmcli_and_handlers(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 interface 模块包含 community.general.nmcli、become: true、notify/handlers"""
        interface_path = module_dirs["interface"]
        content = (interface_path / "playbook.yml").read_text(encoding="utf-8")
        assert "community.general.nmcli" in content, (
            "interface playbook 应使用 community.general.nmcli"
        )
        assert "become: true" in content, "interface playbook 应使用 become: true"
        assert "handlers:" in content, "interface playbook 应包含 handlers"
        assert "notify:" in content, "interface playbook 应使用 notify"

    def test_new_modules_require_chinese_comments(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查新模块 playbook 包含中文注释"""
        for name in ["port", "route", "interface"]:
            if name in module_dirs:
                path = module_dirs[name]
                content = (path / "playbook.yml").read_text(encoding="utf-8")
                has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
                assert has_chinese, f"{name} playbook 需要使用中文任务名或注释"


class TestVarsFiles(TestNetworkFixtures):
    """校验示例变量的注释、安全提示与语法"""

    WARNING_KEYWORDS = ["占位", "重要", "请勿", "⚠", "警告", "风险", "环境"]

    def test_vars_files_exist_and_valid_yaml(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            vars_file = path / "vars" / "example_vars.yml"
            assert vars_file.exists(), f"{name} 模块缺少 vars/example_vars.yml"
            try:
                yaml.safe_load(vars_file.read_text(encoding="utf-8"))
            except yaml.YAMLError as err:
                pytest.fail(f"{name} example_vars.yml 解析失败: {err}")

    def test_vars_files_have_chinese_and_warning(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        for name, path in module_dirs.items():
            content = (path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in content)
            assert has_chinese, f"{name} example_vars.yml 需包含中文注释"
            assert any(keyword in content for keyword in self.WARNING_KEYWORDS), (
                f"{name} example_vars.yml 需提示变量为示例或包含安全警告"
            )

    def test_firewall_vars_contain_port_config(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查防火墙模块的变量文件包含端口配置"""
        for name in ["firewalld", "ufw", "iptables"]:
            if name in module_dirs:
                path = module_dirs[name]
                content = (path / "vars" / "example_vars.yml").read_text(
                    encoding="utf-8"
                )
                # 应该包含某种端口或服务配置
                assert (
                    "port" in content
                    or "service" in content
                    or "端口" in content
                    or "服务" in content
                ), f"{name} example_vars.yml 应包含端口或服务配置"

    def test_port_vars_contain_timeout_and_warning(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 port 模块变量文件包含超时配置和安全警告"""
        port_path = module_dirs["port"]
        content = (port_path / "vars" / "example_vars.yml").read_text(
            encoding="utf-8"
        )
        assert "timeout" in content, "port example_vars.yml 应包含 timeout 配置"
        assert "sleep" in content, "port example_vars.yml 应包含 sleep 配置"
        assert "delegate_to" in content, "port example_vars.yml 应包含 delegate_to 说明"
        assert any(keyword in content for keyword in self.WARNING_KEYWORDS), (
            "port example_vars.yml 需包含安全警告"
        )

    def test_route_vars_contain_metric_and_warning(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 route 模块变量文件包含 metric 配置和安全警告"""
        route_path = module_dirs["route"]
        content = (route_path / "vars" / "example_vars.yml").read_text(
            encoding="utf-8"
        )
        assert "metric" in content, "route example_vars.yml 应包含 metric 配置"
        assert "gw" in content, "route example_vars.yml 应包含 gw 配置"
        assert "dest" in content, "route example_vars.yml 应包含 dest 配置"
        assert any(keyword in content for keyword in self.WARNING_KEYWORDS), (
            "route example_vars.yml 需包含安全警告"
        )

    def test_interface_vars_contain_autoconnect_and_warning(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 interface 模块变量文件包含 autoconnect 配置和安全警告"""
        interface_path = module_dirs["interface"]
        content = (interface_path / "vars" / "example_vars.yml").read_text(
            encoding="utf-8"
        )
        assert "autoconnect" in content, "interface example_vars.yml 应包含 autoconnect 配置"
        assert "ip4" in content, "interface example_vars.yml 应包含 ip4 配置"
        assert "method4" in content, "interface example_vars.yml 应包含 method4 配置"
        assert any(keyword in content for keyword in self.WARNING_KEYWORDS), (
            "interface example_vars.yml 需包含安全警告"
        )


class TestNetworkModuleIntegration(TestNetworkFixtures):
    """测试网络模块与 metadata/modules.yaml 的集成"""

    def test_modules_yaml_contains_network_category(self) -> None:
        metadata_file = Path(__file__).parent.parent.parent / "metadata" / "modules.yaml"
        assert metadata_file.exists(), "metadata/modules.yaml 文件不存在"
        
        with metadata_file.open("r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)
        
        assert "network" in metadata, (
            "metadata/modules.yaml 应包含 network 分类"
        )

    def test_modules_yaml_network_has_topics(self) -> None:
        metadata_file = Path(__file__).parent.parent.parent / "metadata" / "modules.yaml"
        with metadata_file.open("r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)
        
        if "network" in metadata:
            network_section = metadata["network"]
            assert "topics" in network_section, (
                "network 分类应包含 topics 列表"
            )
            assert len(network_section["topics"]) > 0, (
                "network 分类应至少包含一个模块"
            )

    def test_modules_yaml_network_external_deps(self) -> None:
        metadata_file = Path(__file__).parent.parent.parent / "metadata" / "modules.yaml"
        with metadata_file.open("r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)
        
        if "network" in metadata:
            network_section = metadata["network"]
            if "external_dependencies" in network_section:
                deps = network_section["external_dependencies"]
                assert "community.general" in str(deps), (
                    "network 分类应说明 community.general 依赖"
                )


class TestRootReadme(TestNetworkFixtures):
    """测试根 README 是否包含网络模块信息"""

    def test_root_readme_mentions_network_module(self) -> None:
        root_readme = Path(__file__).parent.parent.parent / "README.md"
        content = root_readme.read_text(encoding="utf-8")
        
        # 检查是否提及网络模块或相关的防火墙模块
        assert (
            "network" in content.lower()
            or "firewall" in content.lower()
            or "防火墙" in content
            or "网络" in content
        ), "根 README.md 应包含网络模块相关内容"

    def test_root_readme_provides_collection_install_guidance(self) -> None:
        root_readme = Path(__file__).parent.parent.parent / "README.md"
        content = root_readme.read_text(encoding="utf-8")
        
        # 检查是否提供了集合安装指导
        assert (
            "ansible-galaxy collection install" in content
            or "community.general" in content
        ), "根 README.md 应提供 ansible-galaxy 集合安装指导"
