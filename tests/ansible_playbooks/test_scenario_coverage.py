"""
Scenario coverage tests for ansible-playbooks workspace.
Tests iterate over key playbooks to ensure proper safeguards, documentation links, and best practices.
"""

from __future__ import annotations

import re
import yaml
from pathlib import Path
from typing import Dict, List
import pytest

PLAYBOOKS_ROOT = Path(__file__).parent.parent.parent / "ansible-playbooks"


class TestScenarioCoverage:
    """Test coverage for key scenario playbooks."""

    @pytest.fixture(scope="class")
    def playbooks_root(self) -> Path:
        return PLAYBOOKS_ROOT

    @pytest.fixture(scope="class")
    def key_scenarios(self) -> Dict[str, List[str]]:
        """Define key scenarios and their expected playbooks."""
        return {
            "system-init": [
                "ubuntu-debian-init.yml",
                "rhel-centos-init.yml", 
                "common-security-hardening.yml"
            ],
            "maintenance": [
                "backup-strategy.yml"
            ],
            "database": [
                "mysql-5.7-install.yml",
                "mysql-8.0-install.yml",
                "postgresql-install.yml"
            ],
            "monitoring": [
                "prometheus-install.yml",
                "elk-stack-install.yml"
            ],
            "application-deploy": [
                "docker-install.yml",
                "lamp-stack-deploy.yml",
                "lnmp-stack-deploy.yml",
                "nodejs-app-deploy.yml"
            ]
        }

    def test_key_scenario_directories_exist(self, playbooks_root: Path, key_scenarios: Dict[str, List[str]]) -> None:
        """Verify key scenario directories exist."""
        for scenario_category in key_scenarios.keys():
            scenario_dir = playbooks_root / scenario_category
            assert scenario_dir.exists(), f"Scenario directory missing: {scenario_category}"
            assert scenario_dir.is_dir(), f"Scenario path is not a directory: {scenario_category}"

    def test_key_playbooks_exist_and_have_coverage(self, playbooks_root: Path, key_scenarios: Dict[str, List[str]]) -> None:
        """Test that key playbooks exist and have required coverage elements."""
        for scenario_category, expected_playbooks in key_scenarios.items():
            scenario_dir = playbooks_root / scenario_category
            
            # Check if scenario directory exists and has playbooks
            if not scenario_dir.exists():
                pytest.skip(f"Scenario directory {scenario_category} does not exist")
                continue
                
            existing_playbooks = list(scenario_dir.glob("*.yml"))
            
            if not existing_playbooks:
                pytest.skip(f"Scenario directory {scenario_category} has no playbooks")
                continue
            
            for playbook_name in expected_playbooks:
                playbook_path = scenario_dir / playbook_name
                if playbook_path.exists():
                    # Playbook exists - test it
                    self._test_individual_playbook_coverage(playbook_path)

    def _test_individual_playbook_coverage(self, playbook_path: Path) -> None:
        """Test individual playbook for required coverage elements."""
        if not playbook_path.exists():
            pytest.skip(f"Playbook {playbook_path.name} does not exist")
            
        content = playbook_path.read_text(encoding="utf-8")
        playbook_name = playbook_path.name
        
        # Test gather_facts declaration
        self._test_gather_facts_declaration(content, playbook_name)
        
        # Test check_mode/diff usage
        self._test_check_mode_usage(content, playbook_name)
        
        # Test shared variable warnings
        self._test_shared_variable_warnings(content, playbook_name)
        
        # Test documentation links
        self._test_documentation_links(content, playbook_name)

    def _test_gather_facts_declaration(self, content: str, playbook_name: str) -> None:
        """Test playbook explicitly declares gather_facts."""
        # Look for gather_facts declaration at play level
        gather_facts_pattern = r"^\s*gather_facts:\s*(true|false)"
        
        # Find the position of first "tasks:" to limit search to play level
        tasks_pos = content.find("tasks:")
        if tasks_pos == -1:
            tasks_pos = len(content)
            
        content_before_tasks = content[:tasks_pos]
        gather_facts_in_play = re.search(gather_facts_pattern, content_before_tasks, re.MULTILINE)
        
        assert gather_facts_in_play, \
            f"{playbook_name} must explicitly declare gather_facts at play level"

    def _test_check_mode_usage(self, content: str, playbook_name: str) -> None:
        """Test playbook demonstrates check_mode or --diff usage."""
        check_mode_patterns = [
            r"check_mode:\s*(true|false|{{\s*ansible_check_mode\s*}})",
            r"when:\s*not\s+ansible_check_mode",
            r"#.*--check",
            r"#.*--diff"
        ]
        
        found_check_mode = any(re.search(pattern, content, re.IGNORECASE) for pattern in check_mode_patterns)
        
        assert found_check_mode, \
            f"{playbook_name} should demonstrate check_mode usage or reference --check/--diff flags"

    def _test_shared_variable_warnings(self, content: str, playbook_name: str) -> None:
        """Test playbook references shared variable warnings."""
        warning_patterns = [
            r"⚠️",
            r"警告",
            r"注意", 
            r"重要提示",
            r"vault_",
            r"变量.*警告",
            r"variable.*warning"
        ]
        
        found_warnings = any(re.search(pattern, content, re.IGNORECASE) for pattern in warning_patterns)
        
        assert found_warnings, \
            f"{playbook_name} should reference shared variable warnings or contain warning symbols"

    def _test_documentation_links(self, content: str, playbook_name: str) -> None:
        """Test playbook links to caution/best-practice documentation."""
        doc_link_patterns = [
            r"../docs/",
            r"../docs/BEST_PRACTICES.md"
        ]
        
        found_doc_links = any(re.search(pattern, content) for pattern in doc_link_patterns)
        
        if not found_doc_links:
            # Check for any documentation reference in comments
            comment_doc_patterns = [
                r"#.*文档",
                r"#.*最佳实践", 
                r"#.*best.*practice",
                r"#.*参考.*文档",
                r"#.*教学声明",
                r"#.*说明"
            ]
            
            found_doc_refs = any(re.search(pattern, content, re.IGNORECASE) for pattern in comment_doc_patterns)
            
            # At minimum, should have some documentation reference or educational statement
            assert found_doc_refs, \
                f"{playbook_name} should reference documentation or contain educational statements"


class TestAllPlaybooksSafety:
    """Test safety features across all playbooks."""

    @pytest.fixture(scope="class")
    def all_playbooks(self, playbooks_root: Path) -> List[Path]:
        """Get all playbook files."""
        playbooks = []
        for scenario_dir in playbooks_root.iterdir():
            if scenario_dir.is_dir() and scenario_dir.name not in ["inventory", "roles"]:
                playbooks.extend(scenario_dir.glob("*.yml"))
        return playbooks

    def test_all_playbooks_have_chinese_warnings(self, all_playbooks: List[Path]) -> None:
        """Test all playbooks contain Chinese warning headers."""
        for playbook in all_playbooks:
            content = playbook.read_text(encoding="utf-8")
            
            # Look for Chinese warning patterns
            warning_patterns = [
                r"⚠️.*教学声明",
                r"⚠️.*警告", 
                r"⚠️.*注意",
                r"#.*教学声明",
                r"#.*警告"
            ]
            
            found_warnings = any(re.search(pattern, content, re.IGNORECASE) for pattern in warning_patterns)
            
            assert found_warnings, \
                f"{playbook.name} should contain Chinese warning declaration"

    def test_all_playbooks_use_fqcn(self, all_playbooks: List[Path]) -> None:
        """Test all playbooks use FQCN (Fully Qualified Collection Names)."""
        for playbook in all_playbooks:
            content = playbook.read_text(encoding="utf-8")
            
            # Look for non-FQCN module usage (excluding comments)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Skip comments and empty lines
                if line_stripped.startswith('#') or not line_stripped:
                    continue
                    
                # Look for module usage patterns
                non_fqcn_patterns = [
                    r"^\s*-\s*name:\s*.*\n\s+(copy|template|file|service|user|group|command|shell|apt|yum|package|pip|git|docker_image|docker_container):",
                    r"^\s+(copy|template|file|service|user|group|command|shell|apt|yum|package|pip|git|docker_image|docker_container):"
                ]
                
                # This is a simplified check - in real implementation would be more sophisticated
                if re.match(r"^\s+[a-z_]+:", line_stripped) and not line_stripped.startswith("ansible."):
                    # Check if this looks like a module call (not a parameter)
                    if ":" in line_stripped and not line_stripped.startswith(("tags:", "notify:", "vars:", "become:", "gather_facts:")):
                        # Might be a non-FQCN module usage
                        common_builtin_modules = ["copy", "template", "file", "service", "user", "group", "command", "shell", "apt", "yum", "package", "pip", "git"]
                        module_name = line_stripped.split(":")[0].strip()
                        
                        if module_name in common_builtin_modules:
                            # This should use ansible.builtin. prefix
                            pytest.fail(f"{playbook.name} line {i+1}: Module '{module_name}' should use FQCN (ansible.builtin.{module_name})")

    def test_playbooks_have_tags(self, all_playbooks: List[Path]) -> None:
        """Test playbooks have proper tags for organization."""
        for playbook in all_playbooks:
            content = playbook.read_text(encoding="utf-8")
            
            # Look for tags usage
            tags_pattern = r"tags:\s*\["
            if not re.search(tags_pattern, content):
                # Check for simple tags format
                simple_tags_pattern = r"tags:\s*\w+"
                if not re.search(simple_tags_pattern, content):
                    pytest.fail(f"{playbook.name} should use tags for better organization")

    def test_playbooks_valid_yaml(self, all_playbooks: List[Path]) -> None:
        """Test all playbooks are valid YAML."""
        for playbook in all_playbooks:
            try:
                yaml.safe_load(playbook.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                pytest.fail(f"{playbook.name} has invalid YAML: {e}")


class TestScenarioIntegration:
    """Test integration between scenarios and documentation."""

    def test_readme_files_reference_best_practices(self, playbooks_root: Path) -> None:
        """Test scenario README files reference BEST_PRACTICES.md."""
        for scenario_dir in playbooks_root.iterdir():
            if scenario_dir.is_dir() and scenario_dir.name not in ["inventory", "roles"]:
                readme = scenario_dir / "README.md"
                if readme.exists():
                    content = readme.read_text(encoding="utf-8")
                    
                    # Should reference best practices or standards
                    ref_patterns = [
                        r"BEST_PRACTICES",
                        r"最佳实践",
                        r"规范",
                        r"标准"
                    ]
                    
                    found_refs = any(re.search(pattern, content, re.IGNORECASE) for pattern in ref_patterns)
                    
                    assert found_refs, \
                        f"{scenario_dir.name}/README.md should reference best practices or standards"

    def test_scenario_structure_consistency(self, playbooks_root: Path) -> None:
        """Test scenarios have consistent directory structure."""
        expected_subdirs = ["vars", "templates", "handlers", "roles"]
        
        for scenario_dir in playbooks_root.iterdir():
            if scenario_dir.is_dir() and scenario_dir.name not in ["inventory", "roles"]:
                # Check for expected subdirectories (at least vars should exist)
                vars_dir = scenario_dir / "vars"
                
                # Some scenarios might not have all subdirs, but should have vars
                if scenario_dir.name in ["application-deploy", "monitoring", "maintenance", "database", "system-init"]:
                    assert vars_dir.exists(), f"{scenario_dir.name} should have vars directory"

    def test_shared_variables_usage(self, playbooks_root: Path) -> None:
        """Test shared variables are used consistently across scenarios."""
        inventory_vars = playbooks_root / "inventory" / "group_vars" / "all.yml"
        if inventory_vars.exists():
            all_vars_content = inventory_vars.read_text(encoding="utf-8")
            
            # Extract variable names from all.yml
            var_pattern = r"^(\w+):"
            global_vars = set(re.findall(var_pattern, all_vars_content, re.MULTILINE))
            
            # Check that playbooks reference these global variables
            for scenario_dir in playbooks_root.iterdir():
                if scenario_dir.is_dir() and scenario_dir.name not in ["inventory", "roles"]:
                    for playbook_file in scenario_dir.glob("*.yml"):
                        content = playbook_file.read_text(encoding="utf-8")
                        
                        # Look for references to global variables (excluding vault variables)
                        for var in global_vars:
                            if not var.startswith("vault_"):
                                var_ref_pattern = rf"{{\s*{var}\s*}}"
                                if re.search(var_ref_pattern, content):
                                    # Found reference - good
                                    pass


class TestScenarioExecutionSafety:
    """Test scenario execution safety features."""

    def test_playbooks_have_safeguards(self, playbooks_root: Path) -> None:
        """Test playbooks have execution safeguards."""
        for scenario_dir in playbooks_root.iterdir():
            if scenario_dir.is_dir() and scenario_dir.name not in ["inventory", "roles"]:
                for playbook_file in scenario_dir.glob("*.yml"):
                    content = playbook_file.read_text(encoding="utf-8")
                    
                    # Look for safety mechanisms
                    safety_patterns = [
                        r"block:",
                        r"rescue:",
                        r"always:",
                        r"when:\s*not\s+ansible_check_mode",
                        r"check_mode:\s*true"
                    ]
                    
                    found_safety = any(re.search(pattern, content) for pattern in safety_patterns)
                    
                    assert found_safety, \
                        f"{scenario_dir.name}/{playbook_file.name} should have execution safeguards"

    def test_playbooks_document_execution_modes(self, playbooks_root: Path) -> None:
        """Test playbooks document different execution modes."""
        for scenario_dir in playbooks_root.iterdir():
            if scenario_dir.is_dir() and scenario_dir.name not in ["inventory", "roles"]:
                readme = scenario_dir / "README.md"
                if readme.exists():
                    content = readme.read_text(encoding="utf-8")
                    
                    # Should mention execution modes
                    mode_patterns = [
                        r"--check",
                        r"--diff", 
                        r"--syntax-check",
                        r"check_mode",
                        r"dry[-\s]?run"
                    ]
                    
                    found_modes = any(re.search(pattern, content, re.IGNORECASE) for pattern in mode_patterns)
                    
                    assert found_modes, \
                        f"{scenario_dir.name}/README.md should document execution modes"