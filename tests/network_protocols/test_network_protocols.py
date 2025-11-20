"""网络协议模块示例的结构与文档校验"""

from pathlib import Path
from typing import Dict

import pytest
import yaml

MODULES = ["ping", "uri", "dns"]
FQCN_EXPECTATIONS = {
    "ping": "ansible.builtin.ping",
    "uri": "ansible.builtin.uri",
    "dns": "community.general.dig",
}
EXTERNAL_DEPS = {
    "ping": "ansible.builtin (内置)",
    "uri": "ansible.builtin (内置)",
    "dns": "community.general collection",
}
PROTOCOL_KEYWORDS = {
    "ping": ["ICMP", "连通性", "ping", "存活"],
    "uri": ["HTTP", "API", "validate_certs", "no_log", "token"],
    "dns": ["DNS", "查询", "dig", "nsupdate", "zone", "TSIG"],
}


class TestNetworkProtocolsFixtures:
    """提供网络协议模块路径的公共 fixture"""

    @pytest.fixture(scope="class")
    def network_protocols_root(self) -> Path:
        return Path(__file__).parent.parent.parent / "network_protocols"

    @pytest.fixture(scope="class")
    def module_dirs(self, network_protocols_root: Path) -> Dict[str, Path]:
        return {name: network_protocols_root / name for name in MODULES}


class TestNetworkProtocolsReadme(TestNetworkProtocolsFixtures):
    """校验 network_protocols 根目录的 README 内容"""

    def test_network_protocols_readme_exists(
        self, network_protocols_root: Path
    ) -> None:
        readme = network_protocols_root / "README.md"
        assert readme.exists(), "network_protocols 根目录缺少 README.md"

    def test_network_protocols_readme_contains_module_overview(
        self, network_protocols_root: Path
    ) -> None:
        content = (network_protocols_root / "README.md").read_text(encoding="utf-8")
        assert "ping" in content, "network_protocols/README.md 应包含 ping 模块说明"
        assert "uri" in content, "network_protocols/README.md 应包含 uri 模块说明"
        assert "dns" in content, "network_protocols/README.md 应包含 dns 模块说明"

    def test_network_protocols_readme_contains_protocol_info(
        self, network_protocols_root: Path
    ) -> None:
        content = (network_protocols_root / "README.md").read_text(encoding="utf-8")
        assert (
            "ICMP" in content or "ping" in content.lower()
        ), "network_protocols/README.md 应提及 ICMP 协议"
        assert (
            "HTTP" in content or "API" in content
        ), "network_protocols/README.md 应提及 HTTP 协议"
        assert (
            "DNS" in content or "dig" in content
        ), "network_protocols/README.md 应提及 DNS 协议"

    def test_network_protocols_readme_contains_security_tips(
        self, network_protocols_root: Path
    ) -> None:
        content = (network_protocols_root / "README.md").read_text(encoding="utf-8")
        assert (
            "validate_certs" in content or "SSL" in content
        ), "network_protocols/README.md 应包含 SSL 验证相关内容"
        assert (
            "check_mode" in content or "预览" in content
        ), "network_protocols/README.md 应包含 check_mode 相关内容"
        assert (
            "no_log" in content or "敏感" in content or "token" in content
        ), "network_protocols/README.md 应包含敏感信息保护相关内容"

    def test_network_protocols_readme_contains_vault_reference(
        self, network_protocols_root: Path
    ) -> None:
        content = (network_protocols_root / "README.md").read_text(encoding="utf-8")
        assert (
            "Vault" in content or "vault" in content or "加密" in content
        ), "network_protocols/README.md 应提及 Vault 或加密存储"


class TestModuleDocumentation(TestNetworkProtocolsFixtures):
    """校验各网络协议模块 README 的章节与内容"""

    REQUIRED_SECTIONS = ["模块用途", "主要参数", "返回值", "使用情境"]

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
                assert section in content, f"{name} README.md 缺少 {section} 章节"
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

    def test_module_readmes_contain_protocol_keywords(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        for name, path in module_dirs.items():
            content = (path / "README.md").read_text(encoding="utf-8")
            keywords = PROTOCOL_KEYWORDS.get(name, [])
            found_keywords = [kw for kw in keywords if kw in content]
            assert (
                len(found_keywords) > 0
            ), f"{name} README.md 应包含协议相关关键词: {keywords}"


class TestPlaybooks(TestNetworkProtocolsFixtures):
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

    def test_playbooks_reference_vars_files(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查所有 playbook 都引用了 vars 文件"""
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "vars_files" in content or "vars_file" in content, (
                f"{name} playbook 应引用 vars/example_vars.yml"
            )

    def test_uri_playbook_contains_security_practices(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 uri 模块 playbook 包含安全实践"""
        if "uri" in module_dirs:
            path = module_dirs["uri"]
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            # 应该包含 validate_certs 的提及
            assert "validate_certs" in content, (
                "uri playbook 应使用 validate_certs: true"
            )
            # 应该包含 no_log 的提及
            assert "no_log" in content, (
                "uri playbook 应使用 no_log 隐藏敏感信息"
            )

    def test_dns_playbook_contains_check_mode_reference(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 dns 模块 playbook 提及 check_mode"""
        if "dns" in module_dirs:
            path = module_dirs["dns"]
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            # check_mode 在 README 或 playbook 中被提及
            assert (
                "check_mode" in content or "预览" in content
            ), "dns playbook 应提及 check_mode 用于预览"

    def test_ping_playbook_contains_connectivity_check(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 ping 模块 playbook 包含连通性检查逻辑"""
        if "ping" in module_dirs:
            path = module_dirs["ping"]
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert (
                "pong" in content or "连接" in content or "successful" in content
            ), "ping playbook 应包含连通性检查逻辑"


class TestVarsFiles(TestNetworkProtocolsFixtures):
    """校验示例变量的注释、安全提示与语法"""

    WARNING_KEYWORDS = ["占位", "重要", "请勿", "⚠", "警告", "环境", "生产"]

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

    def test_vars_files_contain_protocol_specific_keywords(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 vars 文件包含协议特定关键词"""
        for name, path in module_dirs.items():
            content = (path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
            keywords = PROTOCOL_KEYWORDS.get(name, [])
            # 至少包含一个协议特定关键词
            found_keywords = [kw for kw in keywords if kw in content]
            assert (
                len(found_keywords) > 0
            ), f"{name} example_vars.yml 应包含协议相关变量: {keywords}"

    def test_uri_vars_contain_validate_certs_example(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 uri vars 文件包含 validate_certs 设置"""
        if "uri" in module_dirs:
            path = module_dirs["uri"]
            content = (path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
            assert (
                "validate_certs" in content
            ), "uri example_vars.yml 应包含 validate_certs 变量"

    def test_uri_vars_contain_token_warning(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 uri vars 文件包含 token 安全警告"""
        if "uri" in module_dirs:
            path = module_dirs["uri"]
            content = (path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
            assert (
                "token" in content.lower() or "api" in content.lower()
            ), "uri example_vars.yml 应包含 API Token 相关变量"
            assert (
                "Vault" in content or "vault" in content or "加密" in content
            ), "uri example_vars.yml 应包含 Vault 加密说明"

    def test_dns_vars_contain_zone_config(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 dns vars 文件包含区域配置"""
        if "dns" in module_dirs:
            path = module_dirs["dns"]
            content = (path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
            # 应该包含 dns_zone 或 zone 相关变量
            assert (
                "dns_" in content or "zone" in content.lower()
            ), "dns example_vars.yml 应包含 DNS 区域相关变量"

    def test_dns_vars_contain_tsig_reference(
        self, module_dirs: Dict[str, Path]
    ) -> None:
        """检查 dns vars 文件提及 TSIG"""
        if "dns" in module_dirs:
            path = module_dirs["dns"]
            content = (path / "vars" / "example_vars.yml").read_text(encoding="utf-8")
            assert (
                "TSIG" in content or "Vault" in content or "秘钥" in content
            ), "dns example_vars.yml 应提及 TSIG 认证或密钥保护"


class TestNetworkProtocolsIntegration(TestNetworkProtocolsFixtures):
    """测试网络协议模块与 metadata/modules.yaml 的集成"""

    def test_modules_yaml_contains_network_protocols_category(self) -> None:
        metadata_file = Path(__file__).parent.parent.parent / "metadata" / "modules.yaml"
        assert metadata_file.exists(), "metadata/modules.yaml 文件不存在"

        with metadata_file.open("r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        assert "network_protocols" in metadata, (
            "metadata/modules.yaml 应包含 network_protocols 分类"
        )

    def test_modules_yaml_network_protocols_has_topics(self) -> None:
        metadata_file = Path(__file__).parent.parent.parent / "metadata" / "modules.yaml"
        with metadata_file.open("r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        if "network_protocols" in metadata:
            network_protocols_section = metadata["network_protocols"]
            assert "topics" in network_protocols_section, (
                "network_protocols 分类应包含 topics 列表"
            )
            assert len(network_protocols_section["topics"]) >= 3, (
                "network_protocols 分类应至少包含三个模块"
            )

    def test_modules_yaml_network_protocols_has_title_and_description(self) -> None:
        metadata_file = Path(__file__).parent.parent.parent / "metadata" / "modules.yaml"
        with metadata_file.open("r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        if "network_protocols" in metadata:
            section = metadata["network_protocols"]
            assert "title" in section, (
                "network_protocols 分类应有 title 字段"
            )
            assert "description" in section, (
                "network_protocols 分类应有 description 字段"
            )

    def test_modules_yaml_network_protocols_topics_have_required_fields(self) -> None:
        metadata_file = Path(__file__).parent.parent.parent / "metadata" / "modules.yaml"
        with metadata_file.open("r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        if "network_protocols" in metadata:
            topics = metadata["network_protocols"].get("topics", [])
            for topic in topics:
                assert "id" in topic, "每个 topic 应有 id 字段"
                assert "name" in topic, "每个 topic 应有 name 字段"
                assert "doc" in topic, "每个 topic 应有 doc 字段"
                assert "example" in topic, "每个 topic 应有 example 字段"
                assert "summary" in topic, "每个 topic 应有 summary 字段"


class TestRootReadme(TestNetworkProtocolsFixtures):
    """测试根 README 是否包含网络协议模块信息"""

    def test_root_readme_mentions_network_protocols_category(self) -> None:
        root_readme = Path(__file__).parent.parent.parent / "README.md"
        content = root_readme.read_text(encoding="utf-8")

        assert (
            "network_protocols" in content or "协议" in content
        ), "根 README.md 应包含网络协议模块相关内容"

    def test_root_readme_provides_network_protocols_link(self) -> None:
        root_readme = Path(__file__).parent.parent.parent / "README.md"
        content = root_readme.read_text(encoding="utf-8")

        # 检查是否提供了指向 network_protocols 的链接或引用
        assert (
            "network_protocols/README.md" in content
            or "network_protocols" in content
        ), "根 README.md 应提供指向 network_protocols 的链接"

    def test_root_readme_structure_includes_network_protocols(self) -> None:
        root_readme = Path(__file__).parent.parent.parent / "README.md"
        content = root_readme.read_text(encoding="utf-8")

        # 检查是否在仓库结构中提及网络协议
        assert (
            "network_protocols" in content.lower()
        ), "根 README.md 仓库结构部分应包含 network_protocols"

    def test_root_readme_includes_network_protocols_in_advanced_chapters(
        self,
    ) -> None:
        root_readme = Path(__file__).parent.parent.parent / "README.md"
        content = root_readme.read_text(encoding="utf-8")

        # 检查是否在进阶章节列表中提及网络协议
        has_network_protocols_mention = (
            "network_protocols" in content or "协议" in content
        )
        assert (
            has_network_protocols_mention
        ), "根 README.md 的进阶章节应包含网络协议模块的链接"
