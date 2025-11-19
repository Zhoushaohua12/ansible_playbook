"""版本控制模块示例的结构与文档校验"""

from pathlib import Path
from typing import Dict

import pytest
import yaml

MODULES = ["git_workflow", "github_release", "gitlab_project", "hg"]
FQCN_EXPECTATIONS = {
    "git_workflow": "ansible.builtin.git",
    "github_release": "community.general.github_release",
    "gitlab_project": "community.general.gitlab_project",
    "hg": "community.general.hg",
}


class TestVersionControlFixtures:
    """提供版本控制模块路径的公共 fixture"""

    @pytest.fixture(scope="class")
    def version_control_root(self) -> Path:
        return Path(__file__).parent.parent.parent / "version_control"

    @pytest.fixture(scope="class")
    def module_dirs(self, version_control_root: Path) -> Dict[str, Path]:
        return {name: version_control_root / name for name in MODULES}


class TestVersionControlReadme(TestVersionControlFixtures):
    """校验 version_control 根目录的 README 内容"""

    def test_version_control_readme_exists(self, version_control_root: Path) -> None:
        readme = version_control_root / "README.md"
        assert readme.exists(), "version_control 根目录缺少 README.md"

    def test_version_control_readme_contains_module_overview(self, version_control_root: Path) -> None:
        content = (version_control_root / "README.md").read_text(encoding="utf-8")
        assert "git_workflow" in content, "version_control/README.md 应包含 git_workflow 模块说明"
        assert "github_release" in content, "version_control/README.md 应包含 github_release 模块说明"
        assert "gitlab_project" in content, "version_control/README.md 应包含 gitlab_project 模块说明"
        assert "hg" in content, "version_control/README.md 应包含 hg 模块说明"
        assert "版本控制" in content, "version_control/README.md 应说明版本控制场景"
        assert "Git" in content, "version_control/README.md 应包含 Git 场景说明"
        assert "GitHub" in content, "version_control/README.md 应包含 GitHub 场景说明"
        assert "GitLab" in content, "version_control/README.md 应包含 GitLab 场景说明"


class TestModuleDocumentation(TestVersionControlFixtures):
    """校验各版本控制模块 README 的章节与内容"""

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

    def test_git_workflow_readme_contains_git_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 git_workflow README 是否包含 Git 特定内容"""
        content = (module_dirs["git_workflow"] / "README.md").read_text(encoding="utf-8")
        assert "repo" in content, "git_workflow README.md 应包含 repo 参数说明"
        assert "version" in content, "git_workflow README.md 应包含 version 参数说明"
        assert "Git" in content, "git_workflow README.md 应包含 Git 相关注释"

    def test_github_release_readme_contains_github_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 github_release README 是否包含 GitHub 特定内容"""
        content = (module_dirs["github_release"] / "README.md").read_text(encoding="utf-8")
        assert "token" in content, "github_release README.md 应包含 token 参数说明"
        assert "release" in content, "github_release README.md 应包含 release 参数说明"
        assert "GitHub" in content, "github_release README.md 应包含 GitHub 相关注释"

    def test_gitlab_project_readme_contains_gitlab_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 gitlab_project README 是否包含 GitLab 特定内容"""
        content = (module_dirs["gitlab_project"] / "README.md").read_text(encoding="utf-8")
        assert "api_url" in content, "gitlab_project README.md 应包含 api_url 参数说明"
        assert "project" in content, "gitlab_project README.md 应包含 project 参数说明"
        assert "GitLab" in content, "gitlab_project README.md 应包含 GitLab 相关注释"

    def test_hg_readme_contains_hg_specific_content(self, module_dirs: Dict[str, Path]) -> None:
        """检查 hg README 是否包含 Mercurial 特定内容"""
        content = (module_dirs["hg"] / "README.md").read_text(encoding="utf-8")
        assert "repo" in content, "hg README.md 应包含 repo 参数说明"
        assert "revision" in content, "hg README.md 应包含 revision 参数说明"
        assert "Mercurial" in content, "hg README.md 应包含 Mercurial 相关注释"


class TestPlaybooks(TestVersionControlFixtures):
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

    def test_git_workflow_playbook_contains_git_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 git_workflow playbook 是否包含 Git 相关任务"""
        content = (module_dirs["git_workflow"] / "playbook.yml").read_text(encoding="utf-8")
        assert "ansible.builtin.git" in content, "git_workflow playbook 应包含 git 任务"
        assert "repo" in content, "git_workflow playbook 应包含 repo 参数"
        # 检查中文注释
        assert "Git" in content, "git_workflow playbook 应包含中文 Git 相关注释"

    def test_github_release_playbook_contains_github_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 github_release playbook 是否包含 GitHub 相关任务"""
        content = (module_dirs["github_release"] / "playbook.yml").read_text(encoding="utf-8")
        assert "community.general.github_release" in content, "github_release playbook 应包含 github_release 任务"
        assert "token" in content, "github_release playbook 应包含 token 参数"
        # 检查中文注释
        assert "GitHub" in content, "github_release playbook 应包含中文 GitHub 相关注释"

    def test_gitlab_project_playbook_contains_gitlab_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 gitlab_project playbook 是否包含 GitLab 相关任务"""
        content = (module_dirs["gitlab_project"] / "playbook.yml").read_text(encoding="utf-8")
        assert "community.general.gitlab_project" in content, "gitlab_project playbook 应包含 gitlab_project 任务"
        assert "api_token" in content, "gitlab_project playbook 应包含 api_token 参数"
        # 检查中文注释
        assert "GitLab" in content, "gitlab_project playbook 应包含中文 GitLab 相关注释"

    def test_hg_playbook_contains_hg_tasks(self, module_dirs: Dict[str, Path]) -> None:
        """检查 hg playbook 是否包含 Mercurial 相关任务"""
        content = (module_dirs["hg"] / "playbook.yml").read_text(encoding="utf-8")
        assert "community.general.hg" in content, "hg playbook 应包含 hg 任务"
        assert "repo" in content, "hg playbook 应包含 repo 参数"
        # 检查中文注释
        assert "Mercurial" in content, "hg playbook 应包含中文 Mercurial 相关注释"

    def test_playbooks_use_vars_files(self, module_dirs: Dict[str, Path]) -> None:
        """检查所有 playbook 都引用了 vars 文件"""
        for name, path in module_dirs.items():
            content = (path / "playbook.yml").read_text(encoding="utf-8")
            assert "vars_files" in content, f"{name} playbook 应引用 vars/example_vars.yml"


class TestVarsFiles(TestVersionControlFixtures):
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

    def test_git_workflow_vars_contains_git_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 git_workflow vars 是否包含 Git 特定变量"""
        content = (module_dirs["git_workflow"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "repo" in content, "git_workflow vars 应包含仓库相关变量"
        assert "version" in content or "branch" in content, "git_workflow vars 应包含版本或分支变量"
        assert "git" in content.lower(), "git_workflow vars 应包含 git 相关变量"

    def test_github_release_vars_contains_github_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 github_release vars 是否包含 GitHub 特定变量"""
        content = (module_dirs["github_release"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "github" in content.lower(), "github_release vars 应包含 github 相关变量"
        assert "token" in content, "github_release vars 应包含 token 相关变量"

    def test_gitlab_project_vars_contains_gitlab_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 gitlab_project vars 是否包含 GitLab 特定变量"""
        content = (module_dirs["gitlab_project"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "gitlab" in content.lower(), "gitlab_project vars 应包含 gitlab 相关变量"
        assert "api" in content, "gitlab_project vars 应包含 API 相关变量"

    def test_hg_vars_contains_hg_specific_vars(self, module_dirs: Dict[str, Path]) -> None:
        """检查 hg vars 是否包含 Mercurial 特定变量"""
        content = (module_dirs["hg"] / "vars" / "example_vars.yml").read_text(encoding="utf-8")
        assert "repo" in content, "hg vars 应包含仓库相关变量"
        assert "revision" in content, "hg vars 应包含版本相关变量"
        assert "hg" in content.lower() or "mercurial" in content.lower(), "hg vars 应包含 hg 或 mercurial 相关变量"


class TestVersionControlSpecific(TestVersionControlFixtures):
    """版本控制模块的专项测试"""

    def test_git_workflow_playbook_has_chinese_comments_for_git_operations(self, module_dirs: Dict[str, Path]) -> None:
        """检查 git_workflow 示例中 Git 操作是否标注中文解释"""
        content = (module_dirs["git_workflow"] / "playbook.yml").read_text(encoding="utf-8")
        # 检查 Git 操作的中文注释
        assert "克隆" in content or "拉取" in content, "git_workflow playbook 中的 Git 操作应有中文注释"
        assert "版本" in content, "git_workflow playbook 中的版本控制应有中文注释"

    def test_github_release_playbook_has_chinese_comments_for_release_operations(self, module_dirs: Dict[str, Path]) -> None:
        """检查 github_release 示例中 Release 操作是否标注中文解释"""
        content = (module_dirs["github_release"] / "playbook.yml").read_text(encoding="utf-8")
        # 检查 Release 操作的中文注释
        assert "发布" in content or "Release" in content, "github_release playbook 中的 Release 操作应有中文注释"
        assert "文件" in content, "github_release playbook 中的文件操作应有中文注释"

    def test_gitlab_project_playbook_has_chinese_comments_for_project_operations(self, module_dirs: Dict[str, Path]) -> None:
        """检查 gitlab_project 示例中项目操作是否标注中文解释"""
        content = (module_dirs["gitlab_project"] / "playbook.yml").read_text(encoding="utf-8")
        # 检查项目操作的中文注释
        assert "项目" in content, "gitlab_project playbook 中的项目操作应有中文注释"
        assert "创建" in content, "gitlab_project playbook 中的创建操作应有中文注释"

    def test_hg_playbook_has_chinese_comments_for_hg_operations(self, module_dirs: Dict[str, Path]) -> None:
        """检查 hg 示例中 Mercurial 操作是否标注中文解释"""
        content = (module_dirs["hg"] / "playbook.yml").read_text(encoding="utf-8")
        # 检查 Mercurial 操作的中文注释
        assert "克隆" in content or "拉取" in content, "hg playbook 中的 Hg 操作应有中文注释"
        assert "版本" in content, "hg playbook 中的版本控制应有中文注释"


class TestMultiModulePlaybooks(TestVersionControlFixtures):
    """测试包含多个模块的 playbook"""

    def test_git_workflow_playbook_with_multiple_environments(self, module_dirs: Dict[str, Path]) -> None:
        """测试 git_workflow playbook 中的多环境场景"""
        content = (module_dirs["git_workflow"] / "playbook.yml").read_text(encoding="utf-8")
        assert "ansible.builtin.git" in content, "git_workflow playbook 应包含 git 任务"
        # 检查多环境相关注释
        assert "环境" in content, "git_workflow playbook 应包含环境相关注释"

    def test_github_release_playbook_with_multiple_files(self, module_dirs: Dict[str, Path]) -> None:
        """测试 github_release playbook 中的多文件场景"""
        content = (module_dirs["github_release"] / "playbook.yml").read_text(encoding="utf-8")
        assert "community.general.github_release" in content, "github_release playbook 应包含 github_release 任务"
        # 检查多文件相关注释
        assert "文件" in content, "github_release playbook 应包含文件相关注释"

    def test_gitlab_project_playbook_with_multiple_projects(self, module_dirs: Dict[str, Path]) -> None:
        """测试 gitlab_project playbook 中的多项目场景"""
        content = (module_dirs["gitlab_project"] / "playbook.yml").read_text(encoding="utf-8")
        assert "community.general.gitlab_project" in content, "gitlab_project playbook 应包含 gitlab_project 任务"
        # 检查多项目相关注释
        assert "项目" in content, "gitlab_project playbook 应包含项目相关注释"

    def test_hg_playbook_with_multiple_branches(self, module_dirs: Dict[str, Path]) -> None:
        """测试 hg playbook 中的多分支场景"""
        content = (module_dirs["hg"] / "playbook.yml").read_text(encoding="utf-8")
        assert "community.general.hg" in content, "hg playbook 应包含 hg 任务"
        # 检查多分支相关注释
        assert "分支" in content, "hg playbook 应包含分支相关注释"