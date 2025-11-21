from __future__ import annotations

import json
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
