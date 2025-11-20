"""应用模块示例的结构与文档校验"""

from pathlib import Path
from typing import Dict

import pytest
import yaml

from tests.utils.assertions import (
    assert_handlers_and_notifies_use_chinese,
    assert_playbook_contains_no_log_task,
    assert_playbook_has_common_controls,
    assert_vars_contain_vault_reference,
    assert_warning_header,
)

MODULES = ["docker_container", "docker_image", "kubernetes", "pip", "npm", "git", "package", "yum", "apt"]
FQCN_EXPECTATIONS = {
    "docker_container": "community.docker.docker_container",
    "docker_image": "community.docker.docker_image",
    "kubernetes": "kubernetes.core.k8s",
    "pip": "ansible.builtin.pip",
    "npm": "community.general.npm",
    "git": "ansible.builtin.git",
    "package": "ansible.builtin.package",
    "yum": "ansible.builtin.yum",
    "apt": "ansible.builtin.apt",
}


class TestApplicationsFixtures:
    """提供应用模块路径的公共 fixture"""

    @pytest.fixture(scope="class")
    def applications_root(self) -> Path:
        return Path(__file__).parent.parent.parent / "applications"

    @pytest.fixture(scope="class")
    def module_dirs(self, applications_root: Path) -> Dict[str, Path]:
        return {name: applications_root / name for name in MODULES}


class TestApplicationsReadme(TestApplicationsFixtures):
    """校验 applications 根目录的 README 内容"""

    def test_applications_readme_exists(self, applications_root: Path) -> None:
        readme = applications_root / "README.md"
        assert readme.exists(), "applications 根目录缺少 README.md"

    def test_applications_readme_contains_module_overview(self, applications_root: Path) -> None:
        content = (applications_root / "README.md").read_text(encoding="utf-8")
        assert "docker_container" in content, "applications/README.md 应包含 docker_container 模块说明"
        assert "docker_image" in content, "applications/README.md 应包含 docker_image 模块说明"
        assert "kubernetes" in content, "applications/README.md 应包含 kubernetes 模块说明"
        assert "pip" in content, "applications/README.md 应包含 pip 模块说明"
        assert "npm" in content, "applications/README.md 应包含 npm 模块说明"
        assert "git" in content, "applications/README.md 应包含 git 模块说明"
        assert "package" in content, "applications/README.md 应包含 package 模块说明"
        assert "yum" in content, "applications/README.md 应包含 yum 模块说明"
        assert "apt" in content, "applications/README.md 应包含 apt 模块说明"
        assert "应用管理" in content, "applications/README.md 应说明应用管理场景"
        assert "容器化部署" in content, "applications/README.md 应包含容器化部署场景"
        assert "语言依赖" in content, "applications/README.md 应包含语言依赖场景"
        assert "源码部署" in content, "applications/README.md 应包含源码部署场景"


class TestModuleDocumentation(TestApplicationsFixtures):
    """校验各应用模块 README 的章节与内容"""

    REQUIRED_SECTIONS = ["模块简介", "主要参数", "返回值", "常见使用场景"]

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

    def test_docker_container_readme_contains_docker_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 docker_container README 是否包含 Docker 特定内容"""
        content = (module_dirs["docker_container"] / "README.md").read_text(encoding="utf-8")
        assert "image" in content, "docker_container README.md 应包含 image 参数说明"
        assert "restart_policy" in content, "docker_container README.md 应包含 restart_policy 参数说明"
        assert "容器" in content, "docker_container README.md 应包含容器相关说明"

    def test_git_readme_contains_git_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 git README 是否包含 Git 特定内容"""
        content = (module_dirs["git"] / "README.md").read_text(encoding="utf-8")
        assert "repo" in content, "git README.md 应包含 repo 参数说明"
        assert "version" in content, "git README.md 应包含 version 参数说明"
        assert "持续部署" in content, "git README.md 应包含持续部署场景说明"

    def test_package_readme_contains_package_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 package README 是否包含包管理特定内容"""
        content = (module_dirs["package"] / "README.md").read_text(encoding="utf-8")
        assert "name" in content, "package README.md 应包含 name 参数说明"
        assert "state" in content, "package README.md 应包含 state 参数说明"
        assert "跨平台" in content, "package README.md 应包含跨平台说明"

    def test_yum_readme_contains_yum_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 yum README 是否包含 YUM 特定内容"""
        content = (module_dirs["yum"] / "README.md").read_text(encoding="utf-8")
        assert "update_cache" in content, "yum README.md 应包含 update_cache 参数说明"
        assert "enablerepo" in content, "yum README.md 应包含 enablerepo 参数说明"
        assert "Red Hat" in content, "yum README.md 应包含 Red Hat 系统说明"

    def test_apt_readme_contains_apt_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 apt README 是否包含 APT 特定内容"""
        content = (module_dirs["apt"] / "README.md").read_text(encoding="utf-8")
        assert "update_cache" in content, "apt README.md 应包含 update_cache 参数说明"
        assert "deb" in content, "apt README.md 应包含 deb 参数说明"
        assert "Debian" in content, "apt README.md 应包含 Debian 系统说明"


class TestPlaybooks(TestApplicationsFixtures):
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

    def test_docker_container_playbook_contains_docker_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 docker_container playbook 是否包含 Docker 相关任务"""
        content = (module_dirs["docker_container"] / "playbook.yml").read_text(encoding="utf-8")
        assert "community.docker.docker_container" in content, "docker_container playbook 应包含 docker_container 任务"
        assert "image" in content, "docker_container playbook 应包含 image 参数"
        assert "restart_policy" in content, "docker_container playbook 应包含 restart_policy 参数"
        # 检查中文注释
        assert "容器" in content, "docker_container playbook 应包含中文容器相关注释"

    def test_git_playbook_contains_git_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 git playbook 是否包含 Git 相关任务"""
        content = (module_dirs["git"] / "playbook.yml").read_text(encoding="utf-8")
        assert "ansible.builtin.git" in content, "git playbook 应包含 git 任务"
        assert "repo" in content, "git playbook 应包含 repo 参数"
        assert "version" in content, "git playbook 应包含 version 参数"
        # 检查中文注释
        assert "仓库" in content, "git playbook 应包含中文仓库相关注释"

    def test_package_playbook_contains_package_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 package playbook 是否包含包管理相关任务"""
        content = (module_dirs["package"] / "playbook.yml").read_text(encoding="utf-8")
        assert "ansible.builtin.package" in content, "package playbook 应包含 package 任务"
        assert "name" in content, "package playbook 应包含 name 参数"
        assert "state" in content, "package playbook 应包含 state 参数"
        # 检查中文注释
        assert "软件包" in content, "package playbook 应包含中文软件包相关注释"

    def test_yum_playbook_contains_yum_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 yum playbook 是否包含 YUM 相关任务"""
        content = (module_dirs["yum"] / "playbook.yml").read_text(encoding="utf-8")
        assert "ansible.builtin.yum" in content, "yum playbook 应包含 yum 任务"
        assert "update_cache" in content, "yum playbook 应包含 update_cache 参数"
        # 检查中文注释
        assert "YUM" in content, "yum playbook 应包含中文 YUM 相关注释"

    def test_apt_playbook_contains_apt_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 apt playbook 是否包含 APT 相关任务"""
        content = (module_dirs["apt"] / "playbook.yml").read_text(encoding="utf-8")
        assert "ansible.builtin.apt" in content, "apt playbook 应包含 apt 任务"
        assert "update_cache" in content, "apt playbook 应包含 update_cache 参数"
        # 检查中文注释
        assert "APT" in content, "apt playbook 应包含中文 APT 相关注释"

    def test_docker_image_readme_contains_docker_image_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 docker_image README 是否包含 Docker 镜像特定内容"""
        content = (module_dirs["docker_image"] / "README.md").read_text(encoding="utf-8")
        assert "image" in content, "docker_image README.md 应包含 image 参数说明"
        assert "build" in content, "docker_image README.md 应包含 build 参数说明"
        assert "镜像" in content, "docker_image README.md 应包含镜像相关说明"

    def test_kubernetes_readme_contains_kubernetes_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 kubernetes README 是否包含 K8s 特定内容"""
        content = (module_dirs["kubernetes"] / "README.md").read_text(encoding="utf-8")
        assert "deployment" in content, "kubernetes README.md 应包含 deployment 参数说明"
        assert "service" in content, "kubernetes README.md 应包含 service 参数说明"
        assert "容器编排" in content, "kubernetes README.md 应包含容器编排说明"

    def test_pip_readme_contains_pip_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 pip README 是否包含 Python 包特定内容"""
        content = (module_dirs["pip"] / "README.md").read_text(encoding="utf-8")
        assert "requirements" in content, "pip README.md 应包含 requirements 参数说明"
        assert "virtualenv" in content, "pip README.md 应包含 virtualenv 参数说明"
        assert "Python" in content, "pip README.md 应包含 Python 相关注释"

    def test_npm_readme_contains_npm_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 npm README 是否包含 Node.js 包特定内容"""
        content = (module_dirs["npm"] / "README.md").read_text(encoding="utf-8")
        assert "package.json" in content, "npm README.md 应包含 package.json 参数说明"
        assert "production" in content, "npm README.md 应包含 production 参数说明"
        assert "Node.js" in content, "npm README.md 应包含 Node.js 相关注释"

    def test_docker_image_playbook_contains_docker_image_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 docker_image playbook 是否包含 Docker 镜像相关任务"""
        content = (module_dirs["docker_image"] / "playbook.yml").read_text(encoding="utf-8")
        assert "community.docker.docker_image" in content, "docker_image playbook 应包含 docker_image 任务"
        assert "build" in content, "docker_image playbook 应包含 build 参数"
        # 检查中文注释
        assert "镜像" in content, "docker_image playbook 应包含中文镜像相关注释"

    def test_kubernetes_playbook_contains_kubernetes_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 kubernetes playbook 是否包含 K8s 相关任务"""
        content = (module_dirs["kubernetes"] / "playbook.yml").read_text(encoding="utf-8")
        assert "kubernetes.core.k8s" in content, "kubernetes playbook 应包含 k8s 任务"
        assert "deployment" in content, "kubernetes playbook 应包含 deployment 参数"
        # 检查中文注释
        assert "容器" in content, "kubernetes playbook 应包含中文容器相关注释"

    def test_pip_playbook_contains_pip_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 pip playbook 是否包含 Python 包相关任务"""
        content = (module_dirs["pip"] / "playbook.yml").read_text(encoding="utf-8")
        assert "ansible.builtin.pip" in content, "pip playbook 应包含 pip 任务"
        assert "requirements" in content, "pip playbook 应包含 requirements 参数"
        # 检查中文注释
        assert "Python" in content, "pip playbook 应包含中文 Python 相关注释"

    def test_npm_playbook_contains_npm_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 npm playbook 是否包含 Node.js 包相关任务"""
        content = (module_dirs["npm"] / "playbook.yml").read_text(encoding="utf-8")
        assert "community.general.npm" in content, "npm playbook 应包含 npm 任务"
        assert "package.json" in content, "npm playbook 应包含 package.json 参数"
        # 检查中文注释
        assert "Node.js" in content, "npm playbook 应包含中文 Node.js 相关注释"

    def test_docker_image_vars_contains_docker_image_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 docker_image vars 是否包含 Docker 镜像特定变量"""
        content = (module_dirs["docker_image"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "image" in content or "镜像" in content, "docker_image vars 应包含镜像相关变量"
        assert "build" in content, "docker_image vars 应包含构建相关变量"

    def test_kubernetes_vars_contains_kubernetes_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 kubernetes vars 是否包含 K8s 特定变量"""
        content = (module_dirs["kubernetes"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "deployment" in content, "kubernetes vars 应包含 deployment 相关变量"
        assert "service" in content, "kubernetes vars 应包含 service 相关变量"

    def test_pip_vars_contains_pip_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 pip vars 是否包含 Python 包特定变量"""
        content = (module_dirs["pip"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "requirements" in content, "pip vars 应包含 requirements 相关变量"
        assert "virtualenv" in content, "pip vars 应包含 virtualenv 相关变量"

    def test_npm_vars_contains_npm_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 npm vars 是否包含 Node.js 包特定变量"""
        content = (module_dirs["npm"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "package.json" in content or "package" in content, "npm vars 应包含 package 相关变量"
        assert "npm" in content.lower(), "npm vars 应包含 npm 相关变量"

    def test_playbooks_use_vars_files(self, module_dirs: Dict[str, Path]) -> None:
        """检查所有 playbook 都引用了 vars 文件"""
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "vars_files" in content, f"{name} playbook 应引用 vars/example_vars.yml"


class TestVarsFiles(TestApplicationsFixtures):
    """校验示例变量的注释、安全提示与语法"""

    WARNING_KEYWORDS = ["占位", "重要", "请勿", "⚠", "警告", "风险", "安全"]

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

    def test_docker_container_vars_contains_docker_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 docker_container vars 是否包含 Docker 特定变量"""
        content = (module_dirs["docker_container"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "nginx_image" in content or "image" in content, "docker_container vars 应包含镜像相关变量"
        assert "restart_policy" in content, "docker_container vars 应包含重启策略变量"
        assert "container" in content, "docker_container vars 应包含容器相关变量"

    def test_git_vars_contains_git_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 git vars 是否包含 Git 特定变量"""
        content = (module_dirs["git"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "repo" in content, "git vars 应包含仓库相关变量"
        assert "version" in content or "branch" in content, "git vars 应包含版本或分支变量"
        assert "git" in content.lower(), "git vars 应包含 git 相关变量"

    def test_package_vars_contains_package_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 package vars 是否包含包管理特定变量"""
        content = (module_dirs["package"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "packages" in content, "package vars 应包含包列表变量"
        assert "state" in content, "package vars 应包含状态变量"

    def test_yum_vars_contains_yum_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 yum vars 是否包含 YUM 特定变量"""
        content = (module_dirs["yum"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "yum" in content.lower(), "yum vars 应包含 yum 相关变量"
        assert "packages" in content, "yum vars 应包含包列表变量"

    def test_apt_vars_contains_apt_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 apt vars 是否包含 APT 特定变量"""
        content = (module_dirs["apt"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "apt" in content.lower(), "apt vars 应包含 apt 相关变量"
        assert "packages" in content, "apt vars 应包含包列表变量"


class TestDockerContainerSpecific(TestApplicationsFixtures):
    """Docker Container 模块的专项测试"""

    def test_docker_container_playbook_has_image_and_tag_chinese_comments(self, module_dirs: Dict[str, Path]) -> None:
        """检查 docker 示例中 image/tag 等参数是否标注中文解释"""
        content = (module_dirs["docker_container"] / "playbook.yml").read_text(encoding="utf-8")
        # 检查 image 参数的中文注释
        assert "镜像" in content, "docker_container playbook 中的 image 参数应有中文注释"
        # 检查 restart_policy 参数的中文注释
        assert "重启" in content, "docker_container playbook 中的 restart_policy 参数应有中文注释"


class TestMultiModulePlaybooks(TestApplicationsFixtures):
    """测试包含多个模块的 playbook"""

    def test_package_playbook_with_multiple_modules(self, module_dirs: Dict[str, Path]) -> None:
        """测试 package playbook 中可能包含的 apt+service 等多模块场景"""
        content = (module_dirs["package"] / "playbook.yml").read_text(encoding="utf-8")
        # 如果 playbook 使用同一任务内多个模块，测试需确认关键任务存在
        assert "ansible.builtin.package" in content, "package playbook 应包含 package 任务"
        # 检查中文注释
        assert "软件包" in content, "package playbook 应包含中文软件包相关注释"

    def test_yum_playbook_with_multiple_modules(self, module_dirs: Dict[str, Path]) -> None:
        """测试 yum playbook 中的多模块场景"""
        content = (module_dirs["yum"] / "playbook.yml").read_text(encoding="utf-8")
        assert "ansible.builtin.yum" in content, "yum playbook 应包含 yum 任务"
        # 检查中文注释
        assert "YUM" in content, "yum playbook 应包含中文 YUM 相关注释"

    def test_apt_playbook_with_multiple_modules(self, module_dirs: Dict[str, Path]) -> None:
        """测试 apt playbook 中的多模块场景"""
        content = (module_dirs["apt"] / "playbook.yml").read_text(encoding="utf-8")
        assert "ansible.builtin.apt" in content, "apt playbook 应包含 apt 任务"
        # 检查中文注释
        assert "APT" in content, "apt playbook 应包含中文 APT 相关注释"


class TestApplicationsPolicies(TestApplicationsFixtures):
    """聚合 playbook/vars 的统一策略校验"""

    SENSITIVE_MODULES = {"docker_container", "docker_image", "kubernetes"}
    VAULT_PLACEHOLDERS = {
        "docker_container": ["vault_redis_password", "vault_app_database_url", "vault_app_secret_key"],
    }

    def test_playbooks_declare_controls(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            playbook = path / "playbook.yml"
            assert playbook.exists(), f"{name} 缺少 playbook.yml"
            assert_playbook_has_common_controls(playbook)
            assert_handlers_and_notifies_use_chinese(playbook)

    def test_sensitive_playbooks_mask_secrets(self, module_dirs: Dict[str, Path]) -> None:
        for name in self.SENSITIVE_MODULES:
            playbook = module_dirs[name] / "playbook.yml"
            assert_playbook_contains_no_log_task(playbook)

    def test_vars_files_have_warning_header(self, module_dirs: Dict[str, Path]) -> None:
        for name, path in module_dirs.items():
            vars_file = path / "vars" / "example_vars.yml"
            assert vars_file.exists(), f"{name} 缺少 vars/example_vars.yml"
            assert_warning_header(vars_file)

    def test_sensitive_vars_use_vault_placeholder(self, module_dirs: Dict[str, Path]) -> None:
        for name, placeholders in self.VAULT_PLACEHOLDERS.items():
            vars_file = module_dirs[name] / "vars" / "example_vars.yml"
            assert_vars_contain_vault_reference(vars_file, placeholders)
