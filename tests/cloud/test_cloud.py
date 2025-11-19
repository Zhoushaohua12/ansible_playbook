"""云资源章节结构与安全校验"""

from pathlib import Path
from typing import Dict

import pytest
import yaml

MODULES = [
    "aws_ec2",
    "azure_vm",
    "gcp_compute",
    "openstack_server",
    "aliyun_ecs",
]

FQCN_EXPECTATIONS = {
    "aws_ec2": "community.aws.ec2_instance",
    "azure_vm": "azure.azcollection.azure_rm_virtualmachine",
    "gcp_compute": "google.cloud.gcp_compute_instance",
    "openstack_server": "openstack.cloud.server",
    "aliyun_ecs": "alibaba.cloud.ali_ecs",
}

WARNING_KEYWORDS = ["⚠", "Vault", "占位", "请勿", "REPLACE", "敏感"]
PLACEHOLDER_PATTERNS = ["REPLACE", "your_", "{{ vault", "lookup('env'"]


class TestCloudFixtures:
    """公共 fixture"""

    @pytest.fixture(scope="class")
    def cloud_root(self) -> Path:
        return Path(__file__).parent.parent.parent / "cloud"

    @pytest.fixture(scope="class")
    def module_dirs(self, cloud_root: Path) -> Dict[str, Path]:
        return {name: cloud_root / name for name in MODULES}


class TestCloudReadmes(TestCloudFixtures):
    def test_cloud_root_readme(self, cloud_root: Path) -> None:
        readme = cloud_root / "README.md"
        assert readme.exists(), "cloud/ 需包含 README.md"
        content = readme.read_text(encoding="utf-8")
        for module in MODULES:
            assert module in content, f"cloud/README.md 应介绍 {module} 模块"
        assert "ansible-galaxy collection install" in content, "需提供依赖安装指令"
        assert "认证" in content or "凭证" in content, "需强调认证方式"
        assert "Dry Run" in content or "check_mode" in content, "需说明默认 Dry Run"

    def test_root_readme_mentions_cloud(self) -> None:
        root_readme = Path(__file__).parent.parent.parent / "README.md"
        content = root_readme.read_text(encoding="utf-8")
        assert "cloud/" in content, "根 README 需列出 cloud 目录"
        assert "云资源" in content, "根 README 需描述云资源章节"


class TestCloudModuleDocs(TestCloudFixtures):
    REQUIRED_SECTIONS = ["模块用途", "主要参数", "返回值", "使用情境", "安全注意事项"]

    def test_each_module_readme_sections(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            readme = path / "README.md"
            assert readme.exists(), f"{name} 缺少 README.md"
            content = readme.read_text(encoding="utf-8")
            for section in self.REQUIRED_SECTIONS:
                assert section in content, f"{name} README 应包含 {section}"
            assert "Vault" in content or "凭证" in content, f"{name} README 需强调凭证保护"
            assert any("\u4e00" <= ch <= "\u9fff" for ch in content), f"{name} README 需包含中文内容"


class TestCloudPlaybooks(TestCloudFixtures):
    def test_playbooks_are_valid_yaml(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            playbook = path / "playbook.yml"
            assert playbook.exists(), f"{name} 缺少 playbook.yml"
            with playbook.open(encoding="utf-8") as fh:
                try:
                    yaml.safe_load(fh)
                except yaml.YAMLError as err:
                    pytest.fail(f"{name} playbook.yml 解析失败: {err}")

    def test_playbooks_use_expected_fqcn(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert FQCN_EXPECTATIONS[name] in content, f"{name} playbook 需使用 {FQCN_EXPECTATIONS[name]}"
            assert "check_mode: true" in content, f"{name} playbook 需默认 Dry Run"
            assert "no_log: true" in content, f"{name} playbook 需启用 no_log"
            assert "vars_files" in content, f"{name} playbook 需引用 vars/example_vars.yml"
            assert any("\u4e00" <= ch <= "\u9fff" for ch in content), f"{name} playbook 需包含中文注释"


class TestCloudVars(TestCloudFixtures):
    def test_vars_files(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            vars_file = path / "vars" / "example_vars.yml"
            assert vars_file.exists(), f"{name} 缺少 vars/example_vars.yml"
            try:
                yaml.safe_load(vars_file.read_text(encoding="utf-8"))
            except yaml.YAMLError as err:
                pytest.fail(f"{name} vars 文件解析失败: {err}")
            content = vars_file.read_text(encoding="utf-8")
            assert any(keyword in content for keyword in WARNING_KEYWORDS), f"{name} vars 需包含安全提示"
            assert any(pattern in content for pattern in PLACEHOLDER_PATTERNS), f"{name} vars 需使用占位符"
            assert any("\u4e00" <= ch <= "\u9fff" for ch in content), f"{name} vars 需包含中文注释"


class TestCloudMetadata:
    def test_metadata_cloud_section(self) -> None:
        metadata = Path(__file__).parent.parent.parent / "metadata" / "modules.yaml"
        data = yaml.safe_load(metadata.read_text(encoding="utf-8"))
        assert "cloud" in data, "metadata/modules.yaml 需包含 cloud 节点"
        topics = {topic["id"] for topic in data["cloud"]["topics"]}
        for module in MODULES:
            assert module in topics, f"metadata cloud.topics 缺少 {module}"


class TestCloudReadmeLinks(TestCloudFixtures):
    def test_each_module_listed_in_root_list(self, module_dirs: Dict[str, Path]) -> None:
        cloud_readme = (Path(__file__).parent.parent.parent / "cloud" / "README.md").read_text(encoding="utf-8")
        for module in module_dirs:
            assert module in cloud_readme, f"cloud/README.md 需列出 {module}"
