from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

from tools import module_index


def _build_sample_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "files" / "copy").mkdir(parents=True)
    (root / "files" / "README.md").write_text(
        """# 文件操作

借助文件模块覆盖 copy/template/同步等常见需求，强调中文注释与安全提示。
""",
        encoding="utf-8",
    )
    (root / "files" / "copy" / "README.md").write_text(
        """# Copy 模块

`ansible.builtin.copy` 模块用于将文件从控制节点复制到远端主机，适合静态资源发布。
""",
        encoding="utf-8",
    )
    (root / "files" / "copy" / "playbook.yml").write_text(
        """---
- name: 演示文件复制
  hosts: all
  gather_facts: false
  tasks:
    - name: 复制示例文件
      ansible.builtin.copy:
        src: files/sample.conf
        dest: /etc/sample.conf
    - name: 同步目录
      community.general.synchronize:
        src: ./files
        dest: /tmp/demo
""",
        encoding="utf-8",
    )
    return root


@pytest.fixture()
def sample_index(tmp_path: Path) -> tuple[dict, Path]:
    root = _build_sample_repo(tmp_path)
    diff_file = tmp_path / "diff.json"
    diff_file.write_text(
        json.dumps(
            [
                {
                    "category": "files",
                    "id": "assemble",
                    "priority": "high",
                    "status": "missing",
                    "doc_url": "https://example.invalid/assemble",
                    "notes": "拼接多个碎片文件以生成完整配置",
                    "prerequisites": ["copy"],
                }
            ]
        ),
        encoding="utf-8",
    )
    diff_entries = module_index.load_diff_entries(diff_file)
    index = module_index.build_module_index(root=root, diff_entries=diff_entries)
    return index, root


def test_build_index_and_learning_path(sample_index: tuple[dict, Path]) -> None:
    index, _ = sample_index
    assert "files" in index["categories"], "应生成 files 分类"
    files_section = index["categories"]["files"]
    assert files_section["topics"][0]["id"] == "copy"
    assert "ansible.builtin.copy" in " ".join(files_section["topics"][0]["dependencies"])
    assert files_section["learning_path"][0]["id"] == "assemble"
    assert files_section["learning_path"][0]["priority"] == "high"


def test_query_helper_returns_dependencies(sample_index: tuple[dict, Path]) -> None:
    index, _ = sample_index
    results = module_index.query_modules(index, "copy")
    assert results, "query 结果不应为空"
    assert "ansible.builtin.copy" in results[0]["dependencies"]
    rendered = module_index.render_query_results(results, "copy")
    assert "[files]" in rendered


def test_write_outputs_and_reports(tmp_path: Path, sample_index: tuple[dict, Path]) -> None:
    index, _ = sample_index
    metadata_path = tmp_path / "metadata" / "modules.yaml"
    json_path = tmp_path / "reports" / "module_index.json"
    docs_path = tmp_path / "docs" / "MODULE_INDEX.md"
    report_path = tmp_path / "reports" / "module_comparison.md"

    module_index.write_metadata(index, metadata_path)
    module_index.write_json(index, json_path)
    module_index.write_markdown(index, docs_path)
    module_index.write_comparison_report(index, report_path)

    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    assert "files" in metadata
    assert metadata["files"]["topics"][0]["summary"].startswith("ansible.builtin.copy")

    json_blob = json.loads(json_path.read_text(encoding="utf-8"))
    assert "generated_at" in json_blob

    docs_content = docs_path.read_text(encoding="utf-8")
    assert "模块索引" in docs_content
    assert "学习路径建议" in docs_content

    comparison = report_path.read_text(encoding="utf-8")
    assert "Stage 4" in comparison
    assert "assemble" in comparison


def test_index_contains_selection_guide_fields(sample_index: tuple[dict, Path]) -> None:
    """Test that module index contains fields needed for selection guide."""
    index, _ = sample_index
    
    # Check for selection guide related fields
    files_section = index["categories"]["files"]
    topic = files_section["topics"][0]
    
    # Debug: print the topic structure
    print(f"Topic keys: {list(topic.keys())}")
    
    # Should have dependencies for selection guidance
    assert "dependencies" in topic, "Topics should have dependencies for selection guidance"
    assert len(topic["dependencies"]) > 0, "Dependencies should not be empty"
    
    # Should have summary for selection table
    assert "summary" in topic, "Topics should have summary for selection tables"
    assert len(topic["summary"]) > 10, "Summary should be meaningful"
    
    # Should have coverage status
    assert "coverage" in topic, "Topics should have coverage status"


def test_markdown_generation_includes_anchors(tmp_path: Path, sample_index: tuple[dict, Path]) -> None:
    """Test that generated Markdown includes expected anchors."""
    index, _ = sample_index
    docs_path = tmp_path / "docs" / "MODULE_INDEX.md"
    
    module_index.write_markdown(index, docs_path)
    docs_content = docs_path.read_text(encoding="utf-8")
    
    # Check for anchor links in markdown format
    anchor_pattern = r"\[.*?\]\(.*?\.md\)"
    anchors = re.findall(anchor_pattern, docs_content)
    
    assert len(anchors) >= 1, "Generated markdown should contain at least one anchor link"
    
    # Check for specific module anchors
    module_anchors = [anchor for anchor in anchors if "copy" in anchor.lower()]
    assert len(module_anchors) >= 1, "Should contain anchors for specific modules"


def test_metadata_includes_new_fields(tmp_path: Path, sample_index: tuple[dict, Path]) -> None:
    """Test that metadata includes new fields powering selection guide."""
    index, _ = sample_index
    metadata_path = tmp_path / "metadata" / "modules.yaml"
    
    module_index.write_metadata(index, metadata_path)
    metadata_content = metadata_path.read_text(encoding="utf-8")
    metadata = yaml.safe_load(metadata_content)
    
    # Validate new metadata structure
    assert "files" in metadata, "Metadata should contain files category"
    
    files_category = metadata["files"]
    assert "topics" in files_category, "Category should have topics"
    assert "learning_path" in files_category, "Category should have learning path"
    
    # Check topic structure
    topic = files_category["topics"][0]
    required_fields = ["id", "summary", "dependencies", "coverage"]
    for field in required_fields:
        assert field in topic, f"Topic should have {field} field"


def test_json_output_contains_selection_data(tmp_path: Path, sample_index: tuple[dict, Path]) -> None:
    """Test that JSON output contains selection guide data."""
    index, _ = sample_index
    json_path = tmp_path / "reports" / "module_index.json"
    
    module_index.write_json(index, json_path)
    json_content = json_path.read_text(encoding="utf-8")
    json_data = json.loads(json_content)
    
    # Check for selection guide relevant data
    assert "files" in json_data, "JSON should contain files category"
    assert "generated_at" in json_data, "JSON should contain generation timestamp"
    
    # Validate structure for frontend consumption
    files_data = json_data["files"]
    assert "topics" in files_data, "Should have topics array"
    assert isinstance(files_data["topics"], list), "Topics should be an array"
    
    # Check first topic has required fields
    if files_data["topics"]:
        topic = files_data["topics"][0]
        selection_fields = ["id", "summary", "dependencies", "coverage"]
        for field in selection_fields:
            assert field in topic, f"Topic missing selection field: {field}"


def test_learning_path_includes_priority_info(sample_index: tuple[dict, Path]) -> None:
    """Test that learning path includes priority information for selection guide."""
    index, _ = sample_index
    files_section = index["categories"]["files"]
    
    # Should have learning path with priority information
    assert "learning_path" in files_section, "Should have learning path"
    learning_path = files_section["learning_path"]
    
    assert len(learning_path) > 0, "Learning path should not be empty"
    
    # Check learning path items have priority info
    for item in learning_path:
        assert "priority" in item, "Learning path items should have priority"
        assert "id" in item, "Learning path items should have id"
        assert item["priority"] in ["high", "medium", "low"], "Priority should be valid value"


def test_module_diff_integration(tmp_path: Path) -> None:
    """Test integration with module diff for coverage gaps."""
    from tools import module_diff
    
    # Create a sample diff file
    diff_file = tmp_path / "diff.json"
    diff_file.write_text(json.dumps([
        {
            "category": "files",
            "id": "assemble", 
            "priority": "high",
            "status": "missing",
            "doc_url": "https://docs.ansible.com/ansible/latest/collections/ansible/builtin/assemble_module.html",
            "notes": "Assemble fragments into a file",
            "prerequisites": ["copy", "template"]
        }
    ]), encoding="utf-8")
    
    # Load diff entries
    diff_entries = module_index.load_diff_entries(diff_file)
    
    assert len(diff_entries) == 1, "Should load one diff entry"
    assert diff_entries[0]["id"] == "assemble", "Should load correct diff entry"
    assert diff_entries[0]["priority"] == "high", "Should preserve priority information"


def test_regenerated_markdown_structure(tmp_path: Path, sample_index: tuple[dict, Path]) -> None:
    """Test that regenerated markdown maintains expected structure."""
    index, _ = sample_index
    docs_path = tmp_path / "docs" / "MODULE_INDEX.md"
    
    module_index.write_markdown(index, docs_path)
    content = docs_path.read_text(encoding="utf-8")
    
    # Check for required markdown structure elements
    assert "# 模块索引" in content, "Should have main title"
    assert "## " in content, "Should have section headers"
    assert "|" in content, "Should have table structure"
    
    # Check for module table headers
    table_headers = ["模块", "摘要", "示例", "覆盖状态"]
    for header in table_headers:
        assert header in content, f"Should have table header: {header}"
    
    # Check for proper markdown table formatting
    table_row_pattern = r"\|.*\|.*\|.*\|.*\|"
    table_rows = re.findall(table_row_pattern, content)
    assert len(table_rows) > 3, "Should have multiple table rows"


def test_anchor_link_validity(tmp_path: Path, sample_index: tuple[dict, Path]) -> None:
    """Test that anchor links in generated markdown are valid."""
    index, _ = sample_index
    docs_path = tmp_path / "docs" / "MODULE_INDEX.md"
    
    module_index.write_markdown(index, docs_path)
    content = docs_path.read_text(encoding="utf-8")
    
    # Extract all markdown links
    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    links = re.findall(link_pattern, content)
    
    for link_text, link_target in links:
        # Skip external links
        if link_target.startswith(('http://', 'https://', 'mailto:')):
            continue
            
        # For internal links, check basic validity
        assert len(link_target) > 0, f"Link target should not be empty: {link_text}"
        assert not link_target.startswith(' '), f"Link target should not start with space: {link_target}"
        
        # Check for proper anchor/file reference format
        if link_target.endswith('.md'):
            # Should be a valid file reference
            assert '/' in link_target or link_target == '#', f"File link should have path or be anchor: {link_target}"
