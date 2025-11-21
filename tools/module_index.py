#!/usr/bin/env python3
"""Generate module metadata, docs, JSON index and query helpers."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METADATA = ROOT / "metadata" / "modules.yaml"
DEFAULT_DIFF = ROOT / "metadata" / "ansible_doc_diff.json"
DEFAULT_DOCS = ROOT / "docs" / "MODULE_INDEX.md"
DEFAULT_JSON = ROOT / "reports" / "module_index.json"
DEFAULT_COMPARISON = ROOT / "reports" / "module_comparison.md"
CATEGORY_EXCLUDES = {
    ".git",
    ".github",
    ".pytest_cache",
    ".mypy_cache",
    "metadata",
    "tests",
    "venv",
    "collections",
    "docs",
    "reports",
    "tools",
    "__pycache__",
}
TASK_CONTROL_KEYS = {
    "action",
    "any_errors_fatal",
    "args",
    "async",
    "become",
    "become_flags",
    "become_method",
    "become_user",
    "cacheable",
    "changed_when",
    "check_mode",
    "collections",
    "delay",
    "delegate_facts",
    "delegate_to",
    "diff",
    "environment",
    "failed_when",
    "ignore_errors",
    "ignore_unreachable",
    "listen",
    "loop",
    "loop_control",
    "max_fail_percentage",
    "module_defaults",
    "name",
    "no_log",
    "notify",
    "poll",
    "register",
    "retries",
    "run_once",
    "tags",
    "throttle",
    "until",
    "vars",
    "vars_files",
    "warn",
    "when",
    "with_items",
    "with_list",
    "with_sequence",
    "with_nested",
    "with_subelements",
    "with_dict",
}
PRIORITY_ALIASES = {
    "critical": "critical",
    "urgent": "critical",
    "high": "high",
    "core": "high",
    "p1": "high",
    "medium": "medium",
    "med": "medium",
    "default": "medium",
    "low": "low",
    "minor": "low",
    "info": "info",
    "informational": "info",
    "experimental": "experimental",
}
PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
    "experimental": 5,
}
MAX_SUMMARY = 240


@dataclass
class TopicIndex:
    """Topic metadata captured from the directory tree."""

    id: str
    name: str
    doc: str
    example: str
    summary: str
    dependencies: List[str] = field(default_factory=list)
    coverage: Dict[str, Any] = field(default_factory=dict)

    def to_metadata(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "doc": self.doc,
            "example": self.example,
            "summary": self.summary,
        }
        if self.dependencies:
            data["dependencies"] = self.dependencies
        if self.coverage:
            data["coverage"] = self.coverage
        return data


@dataclass
class CategoryIndex:
    """Category metadata derived from module directories."""

    key: str
    title: str
    description: str
    external_dependencies: List[str] = field(default_factory=list)
    topics: List[TopicIndex] = field(default_factory=list)
    learning_path: List[Dict[str, Any]] = field(default_factory=list)

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "external_dependencies": self.external_dependencies,
            "topics": [topic.to_metadata() for topic in self.topics],
            "learning_path": self.learning_path,
            "stats": {"total_topics": len(self.topics)},
        }


def humanize_identifier(value: str) -> str:
    """Best-effort conversion from snake_case to Title Case."""
    if not value:
        return value
    parts = re.split(r"[_\-]+", value)
    return " ".join(word.capitalize() for word in parts if word)


def strip_markdown(text: str) -> str:
    """Remove minimal Markdown syntax for summaries."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = text.replace("<br>", " ").replace("<br/>", " ")
    return text.strip()


def extract_title(markdown_path: Path, fallback: str) -> str:
    try:
        lines = markdown_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return fallback
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            return strip_markdown(line.lstrip("# ")) or fallback
    return fallback


def extract_summary(markdown_path: Path, fallback: str) -> str:
    try:
        lines = markdown_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return fallback
    summary_lines: List[str] = []
    in_code_block = False
    for raw in lines:
        line = raw.strip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not line:
            if summary_lines:
                break
            continue
        if line.startswith("#"):
            continue
        if line.startswith(">"):
            line = line.lstrip("> ")
        cleaned = strip_markdown(line)
        if not cleaned:
            continue
        summary_lines.append(cleaned)
        if len(" ".join(summary_lines)) >= MAX_SUMMARY:
            break
    if not summary_lines:
        return fallback
    summary = re.sub(r"\s+", " ", " ".join(summary_lines)).strip()
    if len(summary) > MAX_SUMMARY:
        summary = summary[:MAX_SUMMARY].rstrip() + "…"
    return summary


def normalize_priority(value: Optional[str]) -> str:
    if not value:
        return "medium"
    lowered = str(value).strip().lower()
    return PRIORITY_ALIASES.get(lowered, lowered)


def derive_collection(module_fqcn: str) -> str:
    if not module_fqcn:
        return ""
    if "." not in module_fqcn:
        return "ansible.builtin"
    parts = module_fqcn.split(".")
    if len(parts) >= 2:
        return ".".join(parts[:2])
    return module_fqcn


def to_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def parse_playbook_dependencies(playbook_path: Path) -> List[str]:
    if not playbook_path.exists():
        return []
    try:
        data = yaml.safe_load(playbook_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return []

    modules: set[str] = set()

    def extract_from_task(task: Any) -> None:
        if not isinstance(task, dict):
            return
        for key in ("block", "rescue", "always"):
            if key in task and isinstance(task[key], list):
                for nested in task[key]:
                    extract_from_task(nested)
        for key, value in task.items():
            if key in ("block", "rescue", "always"):
                continue
            if key in TASK_CONTROL_KEYS:
                if key in {"action", "local_action"}:
                    module_value: Optional[str] = None
                    if isinstance(value, dict):
                        module_value = value.get("module") or value.get("_raw_params")
                    elif isinstance(value, str):
                        module_value = value.strip().split()[0]
                    if module_value:
                        modules.add(module_value)
                continue
            modules.add(key)

    def walk_tasks(items: Any) -> None:
        if isinstance(items, list):
            for task in items:
                extract_from_task(task)
        elif isinstance(items, dict):
            extract_from_task(items)

    plays: Sequence[Any]
    if isinstance(data, list):
        plays = data
    elif isinstance(data, dict):
        plays = [data]
    else:
        plays = []

    for play in plays:
        if isinstance(play, dict):
            for section in ("tasks", "pre_tasks", "post_tasks", "handlers"):
                section_items = play.get(section)
                walk_tasks(section_items)
            if "block" in play:
                walk_tasks(play.get("block"))
        else:
            walk_tasks(play)

    return sorted(modules)


def load_diff_entries(diff_path: Optional[Path]) -> List[Dict[str, Any]]:
    if diff_path is None or not diff_path.exists():
        return []
    try:
        raw = json.loads(diff_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[module-index] 无法解析 {diff_path}: {exc}", file=sys.stderr)
        return []

    entries: List[Dict[str, Any]] = []
    iterable: Iterable[Any]
    if isinstance(raw, list):
        iterable = raw
    elif isinstance(raw, dict):
        if "entries" in raw and isinstance(raw["entries"], list):
            iterable = raw["entries"]
        else:
            expanded: List[Dict[str, Any]] = []
            for category, bucket in raw.items():
                if not isinstance(bucket, list):
                    continue
                for entry in bucket:
                    if isinstance(entry, dict):
                        enriched = dict(entry)
                        enriched.setdefault("category", category)
                        expanded.append(enriched)
            iterable = expanded
    else:
        iterable = []

    for entry in iterable:
        if not isinstance(entry, dict):
            continue
        category = entry.get("category")
        module_id = entry.get("id") or entry.get("module")
        if not category or not module_id:
            continue
        normalized = {
            "category": category,
            "id": module_id,
            "name": entry.get("name") or humanize_identifier(module_id),
            "status": entry.get("status", "missing"),
            "priority": normalize_priority(entry.get("priority")),
            "doc_url": entry.get("doc_url"),
            "notes": entry.get("notes"),
            "prerequisites": entry.get("prerequisites")
            or entry.get("depends_on")
            or [],
            "suggested_next": entry.get("suggested_next", []),
        }
        entries.append(normalized)
    return entries


class DiffIndex:
    """Helper to match ansible-doc diff entries to categories/topics."""

    def __init__(self, entries: List[Dict[str, Any]]):
        self._data: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        for entry in entries:
            category = entry.get("category")
            module_id = entry.get("id")
            if category and module_id:
                self._data[category][module_id] = entry

    def consume_topic(self, category: str, module_id: str) -> Optional[Dict[str, Any]]:
        return self._data.get(category, {}).pop(module_id, None)

    def consume_remaining(self, category: str) -> List[Dict[str, Any]]:
        bucket = self._data.pop(category, {})
        entries = list(bucket.values())
        entries.sort(key=lambda item: (
            PRIORITY_ORDER.get(item.get("priority", "medium"), 99),
            item.get("id", "")
        ))
        return entries

    def remaining_categories(self) -> List[str]:
        return sorted(cat for cat, entries in self._data.items() if entries)


class ModuleIndexBuilder:
    """Generate category/module metadata from the repository tree."""

    def __init__(self, root: Path, diff_entries: Optional[List[Dict[str, Any]]] = None):
        self.root = root
        self.diff = DiffIndex(diff_entries or [])

    def build(self) -> Dict[str, Any]:
        categories: "OrderedDict[str, CategoryIndex]" = OrderedDict()
        for path in sorted(self.root.iterdir(), key=lambda item: item.name):
            if not path.is_dir() or path.name in CATEGORY_EXCLUDES or path.name.startswith("."):
                continue
            category = self._build_category(path)
            if not category.topics and not category.learning_path:
                continue
            categories[path.name] = category

        for leftover in self.diff.remaining_categories():
            suggestions = self.diff.consume_remaining(leftover)
            if not suggestions:
                continue
            category = CategoryIndex(
                key=leftover,
                title=humanize_identifier(leftover),
                description="尚未在仓库中实现的 ansible-doc 模块条目。",
                external_dependencies=[],
                topics=[],
                learning_path=[self._format_learning_entry(entry) for entry in suggestions],
            )
            categories[leftover] = category

        total_topics = sum(len(cat.topics) for cat in categories.values())
        total_recommendations = sum(len(cat.learning_path) for cat in categories.values())
        return {
            "categories": OrderedDict(
                (key, category.to_metadata()) for key, category in categories.items()
            ),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_categories": len(categories),
                "total_topics": total_topics,
                "pending_recommendations": total_recommendations,
            },
        }

    def _build_category(self, category_dir: Path) -> CategoryIndex:
        title = extract_title(category_dir / "README.md", humanize_identifier(category_dir.name))
        description = extract_summary(
            category_dir / "README.md",
            "该章节收录来自仓库的示例，详见 README。",
        )
        topics: List[TopicIndex] = []
        dependency_collections: set[str] = set()
        for topic_dir in sorted(category_dir.iterdir(), key=lambda item: item.name):
            if not topic_dir.is_dir() or topic_dir.name.startswith("."):
                continue
            topic = self._build_topic(category_dir.name, topic_dir)
            if not topic:
                continue
            topics.append(topic)
            for dep in topic.dependencies:
                collection = derive_collection(dep)
                if collection:
                    dependency_collections.add(collection)

        topics.sort(key=lambda topic: topic.id)
        category = CategoryIndex(
            key=category_dir.name,
            title=title,
            description=description,
            external_dependencies=sorted(dependency_collections),
            topics=topics,
        )
        remaining = self.diff.consume_remaining(category_dir.name)
        if remaining:
            category.learning_path = [self._format_learning_entry(entry) for entry in remaining]
        return category

    def _build_topic(self, category_name: str, topic_dir: Path) -> Optional[TopicIndex]:
        readme = topic_dir / "README.md"
        playbook = topic_dir / "playbook.yml"
        doc_path = to_relative(readme, self.root) if readme.exists() else ""
        example_path = to_relative(playbook, self.root) if playbook.exists() else ""
        name = extract_title(readme, humanize_identifier(topic_dir.name))
        summary = extract_summary(readme, "查看 README 了解详细示例。")
        dependencies = parse_playbook_dependencies(playbook)
        diff_entry = self.diff.consume_topic(category_name, topic_dir.name)
        if diff_entry:
            coverage: Dict[str, Any] = {
                "status": diff_entry.get("status", "missing"),
                "priority": diff_entry.get("priority", "medium"),
            }
            if diff_entry.get("notes"):
                coverage["notes"] = diff_entry["notes"]
            if diff_entry.get("doc_url"):
                coverage["doc_url"] = diff_entry["doc_url"]
            if diff_entry.get("suggested_next"):
                coverage["suggested_next"] = diff_entry["suggested_next"]
        else:
            coverage = {"status": "covered", "priority": "n/a"}
        return TopicIndex(
            id=topic_dir.name,
            name=name,
            doc=doc_path,
            example=example_path,
            summary=summary,
            dependencies=dependencies,
            coverage=coverage,
        )

    @staticmethod
    def _format_learning_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
        priority = entry.get("priority", "medium")
        return {
            "id": entry.get("id"),
            "name": entry.get("name") or humanize_identifier(entry.get("id", "")),
            "priority": priority,
            "status": entry.get("status", "missing"),
            "doc_url": entry.get("doc_url"),
            "notes": entry.get("notes"),
            "prerequisites": entry.get("prerequisites", []),
            "suggested_next": entry.get("suggested_next", []),
        }


def build_module_index(
    root: Path = ROOT,
    diff_entries: Optional[List[Dict[str, Any]]] = None,
    diff_path: Optional[Path] = None,
) -> Dict[str, Any]:
    entries = diff_entries
    if entries is None:
        entries = load_diff_entries(diff_path or DEFAULT_DIFF)
    builder = ModuleIndexBuilder(root, entries)
    return builder.build()


def write_metadata(index: Dict[str, Any], output_path: Path = DEFAULT_METADATA) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(index["categories"])
    payload["_generated_at"] = index["generated_at"]
    with output_path.open("w", encoding="utf-8") as handler:
        yaml.safe_dump(payload, handler, allow_unicode=True, sort_keys=False)


def write_json(index: Dict[str, Any], output_path: Path = DEFAULT_JSON) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handler:
        json.dump(index, handler, ensure_ascii=False, indent=2)


def write_markdown(index: Dict[str, Any], output_path: Path = DEFAULT_DOCS) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("# 模块索引 (Module Index)")
    lines.append("")
    lines.append(f"- 生成时间: {index['generated_at']}")
    summary = index.get("summary", {})
    lines.append(
        f"- 覆盖统计: {summary.get('total_categories', 0)} 个章节 / {summary.get('total_topics', 0)} 个模块"
    )
    lines.append(
        f"- 待补充模块: {summary.get('pending_recommendations', 0)} 项 (来自 ansible-doc 差异)"
    )
    lines.append("")

    for category, payload in index["categories"].items():
        title = payload.get("title") or humanize_identifier(category)
        lines.append(f"## {title} (`{category}`)")
        lines.append("")
        lines.append(payload.get("description", ""))
        lines.append("")
        external = payload.get("external_dependencies") or []
        if external:
            lines.append("**外部依赖**: " + ", ".join(external))
            lines.append("")
        lines.append("| 模块 | 摘要 | 示例 | 覆盖状态 |")
        lines.append("| --- | --- | --- | --- |")
        for topic in payload.get("topics", []):
            doc = topic.get("doc")
            name = topic.get("name", topic.get("id"))
            module_cell = f"[{name}]({doc})" if doc else name
            summary_text = (topic.get("summary") or "").replace("|", "\\|")
            example = topic.get("example") or "—"
            coverage = topic.get("coverage") or {}
            status = coverage.get("status", "unknown")
            priority = coverage.get("priority")
            status_cell = status if priority in (None, "n/a") else f"{status} ({priority})"
            lines.append(f"| {module_cell} | {summary_text} | `{example}` | {status_cell} |")
        learning_path = payload.get("learning_path") or []
        if learning_path:
            lines.append("")
            lines.append("### 学习路径建议")
            lines.append("")
            lines.append("| 优先级 | 模块 | 前置实践 | 官方文档 | 备注 |")
            lines.append("| --- | --- | --- | --- | --- |")
            for suggestion in learning_path:
                prereqs = ", ".join(suggestion.get("prerequisites", [])) or "—"
                doc_link = suggestion.get("doc_url")
                doc_cell = f"[link]({doc_link})" if doc_link else "—"
                notes = (suggestion.get("notes") or "—").replace("|", "\\|")
                lines.append(
                    f"| {suggestion.get('priority')} | `{suggestion.get('id')}` | {prereqs} | {doc_cell} | {notes} |"
                )
        lines.append("")

    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def write_comparison_report(index: Dict[str, Any], output_path: Path = DEFAULT_COMPARISON) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Stage 4 模块覆盖对比", ""]
    lines.append(f"- 生成时间: {index['generated_at']}")
    summary = index.get("summary", {})
    lines.append(f"- 待补充模块总数: {summary.get('pending_recommendations', 0)}")
    lines.append("- 数据来源: metadata/ansible_doc_diff.json")
    lines.append("")
    has_items = False
    for category, payload in index["categories"].items():
        learning_path = payload.get("learning_path") or []
        if not learning_path:
            continue
        has_items = True
        title = payload.get("title") or humanize_identifier(category)
        lines.append(f"## {title} (`{category}`)")
        lines.append("")
        lines.append("| 模块 | 优先级 | 前置实践 | 官方文档 | 备注 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for suggestion in learning_path:
            prereqs = ", ".join(suggestion.get("prerequisites", [])) or "—"
            doc_link = suggestion.get("doc_url")
            doc_cell = f"[link]({doc_link})" if doc_link else "—"
            notes = (suggestion.get("notes") or "—").replace("|", "\\|")
            lines.append(
                f"| `{suggestion.get('id')}` | {suggestion.get('priority')} | {prereqs} | {doc_cell} | {notes} |"
            )
        lines.append("")
    if not has_items:
        lines.append("diff 数据为空，暂无对比结果。")
        lines.append("")
    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def query_modules(index: Dict[str, Any], term: str) -> List[Dict[str, Any]]:
    needle = term.lower()
    matches: List[Dict[str, Any]] = []
    for category, payload in index["categories"].items():
        for topic in payload.get("topics", []):
            haystack = " ".join(
                [
                    topic.get("id", ""),
                    topic.get("name", ""),
                    topic.get("summary", ""),
                    " ".join(topic.get("dependencies", [])),
                ]
            ).lower()
            if needle in haystack:
                matches.append(
                    {
                        "category": category,
                        "category_title": payload.get("title", category),
                        "id": topic.get("id"),
                        "name": topic.get("name"),
                        "summary": topic.get("summary"),
                        "doc": topic.get("doc"),
                        "example": topic.get("example"),
                        "dependencies": topic.get("dependencies", []),
                        "coverage": topic.get("coverage", {}),
                    }
                )
    return matches


def render_query_results(results: List[Dict[str, Any]], term: str) -> str:
    if not results:
        return f"未找到与 '{term}' 匹配的模块。"
    lines: List[str] = []
    for item in results:
        coverage = item.get("coverage", {})
        status = coverage.get("status", "unknown")
        priority = coverage.get("priority")
        status_text = status if priority in (None, "n/a") else f"{status} ({priority})"
        lines.append(f"[{item['category']}] {item['name']} / {item['summary']}")
        lines.append(f"  - 文档: {item.get('doc') or '—'}")
        lines.append(f"  - 示例: {item.get('example') or '—'}")
        deps = ", ".join(item.get("dependencies", [])) or "无"
        lines.append(f"  - 依赖模块: {deps}")
        lines.append(f"  - 覆盖状态: {status_text}")
    return "\n".join(lines)


def render_learning_path(index: Dict[str, Any]) -> str:
    lines: List[str] = []
    total = 0
    for category, payload in index["categories"].items():
        suggestions = payload.get("learning_path") or []
        if not suggestions:
            continue
        total += len(suggestions)
        title = payload.get("title") or humanize_identifier(category)
        lines.append(f"{title} ({category})")
        for suggestion in suggestions:
            prereqs = ", ".join(suggestion.get("prerequisites", [])) or "—"
            doc_link = suggestion.get("doc_url") or "无官方链接"
            notes = suggestion.get("notes") or ""
            lines.append(
                f"  - [{suggestion.get('priority')}] {suggestion.get('id')}: 前置 {prereqs}; 文档 {doc_link}; {notes}"
            )
    if not lines:
        return "diff 文件为空，暂无学习路径建议。"
    lines.insert(0, f"共 {total} 个待补充模块：")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Module metadata automation helper")
    parser.add_argument("--root", type=Path, default=ROOT, help="项目根目录")
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA, help="metadata/modules.yaml 输出路径")
    parser.add_argument("--docs-output", type=Path, default=DEFAULT_DOCS, help="docs/MODULE_INDEX.md 输出路径")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON, help="reports/module_index.json 输出路径")
    parser.add_argument("--diff-path", type=Path, default=DEFAULT_DIFF, help="ansible-doc 差异 JSON 路径")
    parser.add_argument("--generate", action="store_true", help="生成 metadata/docs/json 输出")
    parser.add_argument("--query", type=str, help="查询模块摘要，例如 --query copy")
    parser.add_argument("--learning-path", action="store_true", help="打印学习路径建议")
    parser.add_argument(
        "--comparison-report",
        nargs="?",
        const=str(DEFAULT_COMPARISON),
        help="生成 Stage 4 Markdown 对比报告，可传入自定义路径",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    index = build_module_index(root=args.root, diff_path=args.diff_path)

    performed = False
    if args.generate:
        write_metadata(index, args.metadata)
        write_markdown(index, args.docs_output)
        write_json(index, args.json_output)
        print(f"✅ 已更新 {args.metadata}, {args.docs_output}, {args.json_output}")
        performed = True
    if args.comparison_report:
        write_comparison_report(index, Path(args.comparison_report))
        print(f"📝 已生成 Stage 4 报告: {args.comparison_report}")
        performed = True
    if args.query:
        results = query_modules(index, args.query)
        print(render_query_results(results, args.query))
        performed = True
    if args.learning_path:
        print(render_learning_path(index))
        performed = True

    if not performed:
        parser.print_help()


if __name__ == "__main__":
    main()
