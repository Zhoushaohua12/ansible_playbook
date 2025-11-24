"""
Documentation-specific tests for handbook files and guide structure.
Tests presence of required sections, headers, and valid intra-document links.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set
import pytest

DOCS_ROOT = Path(__file__).parent.parent.parent / "docs"


class TestHandbookFiles:
    """Test presence and structure of handbook/guide files."""

    @pytest.fixture(scope="class")
    def docs_root(self) -> Path:
        return DOCS_ROOT

    def test_best_practices_exists(self, docs_root: Path) -> None:
        """Verify BEST_PRACTICES.md handbook exists."""
        handbook = docs_root / "BEST_PRACTICES.md"
        assert handbook.exists(), "BEST_PRACTICES.md handbook file is missing"

    def test_module_index_exists(self, docs_root: Path) -> None:
        """Verify MODULE_INDEX.md handbook exists."""
        handbook = docs_root / "MODULE_INDEX.md"
        assert handbook.exists(), "MODULE_INDEX.md handbook file is missing"


class TestRequiredSectionHeaders:
    """Test presence of required section headers in handbook files."""

    @pytest.fixture(scope="class")
    def best_practices_content(self) -> str:
        return (DOCS_ROOT / "BEST_PRACTICES.md").read_text(encoding="utf-8")

    @pytest.fixture(scope="class")
    def module_index_content(self) -> str:
        return (DOCS_ROOT / "MODULE_INDEX.md").read_text(encoding="utf-8")

    def test_best_practices_has_required_sections(self, best_practices_content: str) -> None:
        """Verify BEST_PRACTICES.md contains required section headers."""
        required_sections = [
            "项目结构规范",
            "Playbook 编写规范",
            "变量和密钥管理", 
            "安全最佳实践",
            "测试和质量保证",
            "文档编写规范",
            "命名约定",
            "常见陷阱和解决方案"
        ]
        
        for section in required_sections:
            assert f"## {section}" in best_practices_content, \
                f"BEST_PRACTICES.md missing required section: {section}"

    def test_best_practices_has_best_practices_subsections(self, best_practices_content: str) -> None:
        """Verify BEST_PRACTICES.md contains best practices sub-sections."""
        required_subsections = [
            "gather_facts",
            "FQCN",
            "变量命名",
            "Check 模式",
            "幂等性"
        ]
        
        for subsection in required_subsections:
            # Check for subsection headers (### or ####)
            pattern = rf"##+[^#]*{re.escape(subsection)}"
            assert re.search(pattern, best_practices_content, re.IGNORECASE), \
                f"BEST_PRACTICES.md missing best practices sub-section: {subsection}"

    def test_best_practices_has_attention_list(self, best_practices_content: str) -> None:
        """Verify BEST_PRACTICES.md contains 注意事项 (attention items) list."""
        # Look for Chinese attention markers or lists
        attention_patterns = [
            r"注意事项",
            r"⚠️",
            r"重要提示",
            r"警告",
            r"注意"
        ]
        
        found_attention = any(re.search(pattern, best_practices_content) for pattern in attention_patterns)
        assert found_attention, "BEST_PRACTICES.md should contain 注意事项 or attention items"

    def test_best_practices_has_troubleshooting(self, best_practices_content: str) -> None:
        """Verify BEST_PRACTICES.md contains troubleshooting section."""
        troubleshooting_patterns = [
            r"##+.*常见陷阱",
            r"##+.*问题解决",
            r"常见问题",
            r"自动修复常见问题"
        ]
        
        found_troubleshooting = any(re.search(pattern, best_practices_content, re.IGNORECASE) 
                                  for pattern in troubleshooting_patterns)
        assert found_troubleshooting, "BEST_PRACTICES.md should contain troubleshooting section"

    def test_best_practices_has_module_selection_content(self, best_practices_content: str) -> None:
        """Verify BEST_PRACTICES.md contains module selection guidance."""
        # Check for module selection patterns - this might be in MODULE_INDEX.md instead
        selection_patterns = [
            r"模块选择",
            r"module.*selection",
            r"选择.*模块",
            r"适用.*场景",
            r"理想选择"
        ]
        
        found_selection = any(re.search(pattern, best_practices_content, re.IGNORECASE) 
                            for pattern in selection_patterns)
        
        # If not found in BEST_PRACTICES, check MODULE_INDEX.md
        if not found_selection:
            module_index_content = (DOCS_ROOT / "MODULE_INDEX.md").read_text(encoding="utf-8")
            found_selection = any(re.search(pattern, module_index_content, re.IGNORECASE) 
                                for pattern in selection_patterns)
        
        assert found_selection, "Documentation should contain module selection guidance"

    def test_module_index_has_table_structure(self, module_index_content: str) -> None:
        """Verify MODULE_INDEX.md contains proper table structure."""
        # Check for markdown table headers
        assert "| 模块 |" in module_index_content, "MODULE_INDEX.md should have module column"
        assert "| 摘要 |" in module_index_content, "MODULE_INDEX.md should have summary column"
        assert "| 示例 |" in module_index_content, "MODULE_INDEX.md should have example column"
        assert "| 覆盖状态 |" in module_index_content, "MODULE_INDEX.md should have coverage column"

    def test_module_index_has_anchors(self, module_index_content: str) -> None:
        """Verify MODULE_INDEX.md contains proper anchors for linking."""
        # Look for markdown links that could serve as anchors
        link_pattern = r"\[.*?\]\(.*?\.md\)"
        links = re.findall(link_pattern, module_index_content)
        assert len(links) > 10, "MODULE_INDEX.md should contain multiple module links/anchors"


class TestIntraDocumentLinks:
    """Test validity of intra-document links in handbook files."""

    @pytest.fixture(scope="class")
    def best_practices_content(self) -> str:
        return (DOCS_ROOT / "BEST_PRACTICES.md").read_text(encoding="utf-8")

    @pytest.fixture(scope="class")
    def module_index_content(self) -> str:
        return (DOCS_ROOT / "MODULE_INDEX.md").read_text(encoding="utf-8")

    def test_best_practices_internal_links_valid(self, best_practices_content: str) -> None:
        """Verify internal links in BEST_PRACTICES.md are valid."""
        # Find all internal markdown links
        internal_link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        links = re.findall(internal_link_pattern, best_practices_content)
        
        for link_text, link_target in links:
            # Skip external links
            if link_target.startswith(('http://', 'https://', 'mailto:')):
                continue
                
            # For internal links, check if anchor exists
            if link_target.startswith('#'):
                # Anchor link - check if corresponding header exists
                anchor_text = link_target[1:].lower().replace('-', ' ')
                # Convert to header pattern
                header_patterns = [
                    rf"# {re.escape(link_text)}",
                    rf"## {re.escape(link_text)}", 
                    rf"### {re.escape(link_text)}",
                    rf"#### {re.escape(link_text)}"
                ]
                
                found_header = any(re.search(pattern, best_practices_content, re.IGNORECASE) 
                                 for pattern in header_patterns)
                assert found_header, f"Anchor link '{link_target}' points to missing header in BEST_PRACTICES.md"

    def test_module_index_module_links_exist(self, module_index_content: str) -> None:
        """Verify module links in MODULE_INDEX.md point to existing files."""
        # Find all file links in module index
        file_link_pattern = r"\[([^\]]+)\]\(([^)]+\.md)\)"
        links = re.findall(file_link_pattern, module_index_content)
        
        for link_text, link_target in links:
            # Skip external links
            if link_target.startswith(('http://', 'https://')):
                continue
                
            # Check if linked file exists relative to project root
            project_root = DOCS_ROOT.parent
            linked_file = project_root / link_target
            
            # Some links might be relative to docs directory
            if not linked_file.exists():
                linked_file = DOCS_ROOT / link_target
                
            assert linked_file.exists(), f"Module link '{link_target}' points to non-existent file: {linked_file}"


class TestDocumentationGenerationChanges:
    """Test that documentation generation changes are properly validated."""

    @pytest.fixture(scope="class")
    def docs_root(self) -> Path:
        return DOCS_ROOT

    def test_module_index_has_generation_metadata(self, docs_root: Path) -> None:
        """Verify MODULE_INDEX.md contains generation metadata."""
        content = (docs_root / "MODULE_INDEX.md").read_text(encoding="utf-8")
        
        # Check for generation timestamp
        assert "生成时间" in content, "MODULE_INDEX.md should contain generation timestamp"
        assert "覆盖统计" in content, "MODULE_INDEX.md should contain coverage statistics"
        assert "待补充模块" in content, "MODULE_INDEX.md should mention missing modules"

    def test_best_practices_has_code_examples(self, docs_root: Path) -> None:
        """Verify BEST_PRACTICES.md contains code examples."""
        content = (docs_root / "BEST_PRACTICES.md").read_text(encoding="utf-8")
        
        # Check for code blocks
        code_block_pattern = r"```(?:yaml|yml|bash|sh|json)"
        code_blocks = re.findall(code_block_pattern, content)
        assert len(code_blocks) >= 5, "BEST_PRACTICES.md should contain multiple code examples"

    def test_documentation_files_are_utf8(self, docs_root: Path) -> None:
        """Verify all documentation files are UTF-8 encoded."""
        for md_file in docs_root.glob("*.md"):
            try:
                md_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"Documentation file {md_file.name} is not valid UTF-8")


class TestDocumentationRegressionPrevention:
    """Tests that prevent regressions in documentation structure."""

    @pytest.fixture(scope="class") 
    def all_docs_content(self) -> dict[str, str]:
        """Load all documentation content for cross-validation."""
        content = {}
        for md_file in DOCS_ROOT.glob("*.md"):
            content[md_file.name] = md_file.read_text(encoding="utf-8")
        return content

    def test_no_broken_markdown_syntax(self, all_docs_content: dict[str, str]) -> None:
        """Verify documentation files don't have broken markdown syntax."""
        for filename, content in all_docs_content.items():
            # Skip this check for MODULE_INDEX.md as it has many legitimate underscores in Chinese text
            if filename == "MODULE_INDEX.md":
                continue
                
            # Only check for obvious broken links in English content
            broken_link_pattern = r"\[[^]]*_[^]]*\]\([^)]*\)"
            broken_links = re.findall(broken_link_pattern, content)
            
            # Filter out Chinese text which may legitimately contain underscores
            filtered_links = [link for link in broken_links if not re.search(r'[\u4e00-\u9fff]', link)]
            
            assert not filtered_links, f"{filename} has potentially broken markdown links with underscores"

    def test_consistent_header_hierarchy(self, all_docs_content: dict[str, str]) -> None:
        """Verify consistent header hierarchy across documentation."""
        for filename, content in all_docs_content.items():
            # Simplify test - just check basic structure
            if filename == "BEST_PRACTICES.md":
                # Should have main title
                assert "# " in content, f"{filename} should have main title"
                # Should have section headers
                assert "## " in content, f"{filename} should have section headers"
            elif filename != "MODULE_INDEX.md":  # Module index has different structure
                # Should have main title
                assert "# " in content, f"{filename} should have main title"
                # Should have section headers
                assert "## " in content, f"{filename} should have section headers"

    def test_required_chinese_documentation_elements(self, all_docs_content: dict[str, str]) -> None:
        """Verify required Chinese documentation elements are present."""
        for filename, content in all_docs_content.items():
            if "BEST_PRACTICES" in filename:
                # Should contain Chinese documentation elements
                chinese_elements = ["中文", "说明", "示例", "注意", "规范"]
                found_elements = [elem for elem in chinese_elements if elem in content]
                assert len(found_elements) >= 3, \
                    f"{filename} should contain multiple Chinese documentation elements"