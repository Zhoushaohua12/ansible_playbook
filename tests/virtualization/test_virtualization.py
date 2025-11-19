"""虚拟化章节结构校验"""

from pathlib import Path
from typing import Dict

import pytest
import yaml

MODULES = ["libvirt_domain", "vmware_host", "qemu_img"]
FQCN_EXPECTATIONS = {
    "libvirt_domain": "community.libvirt.libvirt_domain",
    "vmware_host": "community.vmware.vmware_host",
    "qemu_img": "community.general.qemu_img",
}
WARNING_KEYWORDS = ["⚠", "Vault", "占位", "请勿", "REPLACE", "敏感"]


class TestVirtualizationFixtures:
    @pytest.fixture(scope="class")
    def virtualization_root(self) -> Path:
        return Path(__file__).parent.parent.parent / "virtualization"

    @pytest.fixture(scope="class")
    def module_dirs(self, virtualization_root: Path) -> Dict[str, Path]:
        return {name: virtualization_root / name for name in MODULES}


class TestVirtualizationReadmes(TestVirtualizationFixtures):
    REQUIRED_SECTIONS = ["模块用途", "主要参数", "返回值", "使用情境", "安全注意事项"]

    def test_virtualization_root_readme(self, virtualization_root: Path) -> None:
        readme = virtualization_root / "README.md"
        assert readme.exists(), "virtualization/README.md 缺失"
        content = readme.read_text(encoding="utf-8")
        assert "本地虚拟化" in content, "需强调本地虚拟化场景"
        assert "企业级" in content or "企业虚拟化" in content, "需区分企业虚拟化"
        assert "ansible-galaxy collection install" in content, "需说明依赖安装"
        assert "Dry Run" in content or "check_mode" in content, "需说明 Dry Run"

    def test_root_readme_mentions_virtualization(self) -> None:
        root_readme = Path(__file__).parent.parent.parent / "README.md"
        content = root_readme.read_text(encoding="utf-8")
        assert "virtualization/" in content, "根 README 需列出 virtualization 目录"
        assert "虚拟化" in content, "根 README 需描述虚拟化章节"

    def test_module_readme_sections(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            readme = path / "README.md"
            assert readme.exists(), f"{name} 缺少 README.md"
            content = readme.read_text(encoding="utf-8")
            for section in self.REQUIRED_SECTIONS:
                assert section in content, f"{name} README 缺少 {section}"
            assert any("\u4e00" <= ch <= "\u9fff" for ch in content), f"{name} README 需包含中文"
            assert "Vault" in content or "凭证" in content, f"{name} README 需强调凭证保护"


class TestVirtualizationPlaybooks(TestVirtualizationFixtures):
    def test_playbooks_are_valid(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            playbook = path / "playbook.yml"
            assert playbook.exists(), f"{name} 缺少 playbook.yml"
            with playbook.open(encoding="utf-8") as fh:
                try:
                    yaml.safe_load(fh)
                except yaml.YAMLError as err:
                    pytest.fail(f"{name} playbook.yml 解析失败: {err}")

    def test_playbooks_requirements(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert FQCN_EXPECTATIONS[name] in content, f"{name} playbook 需使用 {FQCN_EXPECTATIONS[name]}"
            assert "check_mode: true" in content, f"{name} playbook 需默认 check_mode"
            assert "no_log: true" in content, f"{name} playbook 需启用 no_log"
            assert "vars_files" in content, f"{name} playbook 应引用 vars/example_vars.yml"
            assert any("\u4e00" <= ch <= "\u9fff" for ch in content), f"{name} playbook 需包含中文"


class TestVirtualizationVars(TestVirtualizationFixtures):
    def test_vars_files(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            vars_file = path / "vars" / "example_vars.yml"
            assert vars_file.exists(), f"{name} 缺少 vars/example_vars.yml"
            try:
                yaml.safe_load(vars_file.read_text(encoding="utf-8"))
            except yaml.YAMLError as err:
                pytest.fail(f"{name} vars/example_vars.yml 解析失败: {err}")
            content = vars_file.read_text(encoding="utf-8")
            assert any(keyword in content for keyword in WARNING_KEYWORDS), f"{name} vars 需包含安全提示"
            assert any("\u4e00" <= ch <= "\u9fff" for ch in content), f"{name} vars 需包含中文"


class TestVirtualizationMetadata:
    def test_metadata_virtualization(self) -> None:
        metadata = Path(__file__).parent.parent.parent / "metadata" / "modules.yaml"
        data = yaml.safe_load(metadata.read_text(encoding="utf-8"))
        assert "virtualization" in data, "metadata 需包含 virtualization 节点"
        topic_ids = {topic["id"] for topic in data["virtualization"]["topics"]}
        for module in MODULES:
            assert module in topic_ids, f"metadata virtualization.topics 缺少 {module}"
