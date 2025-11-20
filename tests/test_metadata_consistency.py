"""验证 metadata/modules.yaml 与实际模块目录、README 之间的一致性。"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
METADATA_FILE = REPO_ROOT / "metadata" / "modules.yaml"
ROOT_README = REPO_ROOT / "README.md"


def _collect_topic_entries(data: Dict[str, dict]) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for category, payload in data.items():
        for topic in payload.get("topics", []):
            topic_copy = {"category": category, **topic}
            entries.append(topic_copy)
    return entries


_METADATA_DICT = yaml.safe_load(METADATA_FILE.read_text(encoding="utf-8"))
_TOPIC_ENTRIES = _collect_topic_entries(_METADATA_DICT)


@pytest.fixture(scope="module")
def metadata() -> Dict[str, dict]:
    return _METADATA_DICT


@pytest.fixture(scope="module")
def root_readme_content() -> str:
    return ROOT_README.read_text(encoding="utf-8")


def test_root_readme_mentions_all_categories(metadata: Dict[str, dict], root_readme_content: str) -> None:
    for category, payload in metadata.items():
        title = payload.get("title", category)
        assert (
            category in root_readme_content or title in root_readme_content
        ), f"根 README.md 需要提及分类 {category} ({title})"


@pytest.mark.parametrize(
    "topic",
    _TOPIC_ENTRIES,
    ids=lambda topic: topic["id"],
)
def test_metadata_paths_exist(topic: Dict[str, str]) -> None:
    doc_path = REPO_ROOT / topic["doc"]
    example_path = REPO_ROOT / topic["example"]
    assert doc_path.exists(), f"metadata 中的文档路径不存在: {topic['doc']}"
    assert example_path.exists(), f"metadata 中的示例路径不存在: {topic['example']}"


@pytest.mark.parametrize(
    "topic",
    _TOPIC_ENTRIES,
    ids=lambda topic: f"fields::{topic['id']}",
)
def test_metadata_topics_have_required_fields(topic: Dict[str, str]) -> None:
    for field in ("id", "name", "doc", "example", "summary"):
        assert field in topic, f"topic 缺少字段 {field}: {topic}"
