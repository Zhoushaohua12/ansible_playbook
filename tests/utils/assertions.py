"""共享的 pytest 断言工具，减少重复解析逻辑。"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

import yaml

WARNING_HEADER = "# ⚠️ 本文件仅为示例，占位符必须使用 Ansible Vault 或环境变量替换"


def has_chinese(text: str) -> bool:
    """判断字符串中是否包含中文字符。"""

    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def load_yaml(path: Path):
    """读取 YAML 文件并返回解析结果。"""

    content = path.read_text(encoding="utf-8")
    return yaml.safe_load(content)


def load_playbook(path: Path) -> List[dict]:
    """解析 playbook.yml 并返回 play 列表。"""

    data = load_yaml(path)
    if not isinstance(data, list):
        raise AssertionError(f"{path} 应为包含多个 play 的列表结构")
    plays = [play for play in data if isinstance(play, dict)]
    if not plays:
        raise AssertionError(f"{path} 没有可解析的 play 定义")
    return plays


def iter_section_items(play: dict, section: str) -> List[dict]:
    """遍历指定 section（tasks/handlers 等）下的任务。"""

    section_value = play.get(section, [])
    if isinstance(section_value, dict):
        section_value = [section_value]
    return [item for item in section_value if isinstance(item, dict)]


def iter_all_tasks(plays: Sequence[dict]) -> List[dict]:
    """收集 tasks/pre_tasks/post_tasks/handlers 中的所有任务。"""

    tasks: List[dict] = []
    for play in plays:
        for section in ("tasks", "pre_tasks", "post_tasks", "handlers"):
            tasks.extend(iter_section_items(play, section))
    return tasks


def assert_playbook_has_common_controls(playbook_path: Path) -> None:
    """断言 playbook 中显式声明 gather_facts、become，并包含至少一个 check_mode 任务。"""

    plays = load_playbook(playbook_path)
    missing_gather = [play.get("name", playbook_path.name) for play in plays if "gather_facts" not in play]
    missing_become = [play.get("name", playbook_path.name) for play in plays if "become" not in play]
    if missing_gather:
        raise AssertionError(f"{playbook_path} 缺少 gather_facts: {missing_gather}")
    if missing_become:
        raise AssertionError(f"{playbook_path} 缺少 become: {missing_become}")

    has_check_mode = any("check_mode" in task for task in iter_all_tasks(plays))
    if not has_check_mode:
        raise AssertionError(f"{playbook_path} 需要至少一个设置了 check_mode 的任务")


def assert_warning_header(vars_path: Path, expected: str = WARNING_HEADER) -> None:
    """确保 vars/example_vars.yml 的首行使用标准警示。"""

    lines = vars_path.read_text(encoding="utf-8").splitlines()
    first_meaningful = next((line for line in lines if line.strip()), "")
    assert first_meaningful == expected, (
        f"{vars_path} 第一行应为标准警示: '{expected}', 实际为 '{first_meaningful}'"
    )


def _extract_notify_values(task: dict) -> Iterable[str]:
    notify_value = task.get("notify")
    if isinstance(notify_value, str):
        yield notify_value
    elif isinstance(notify_value, Iterable):
        for item in notify_value:
            if isinstance(item, str):
                yield item


def assert_handlers_and_notifies_use_chinese(playbook_path: Path) -> None:
    """断言 handlers 的名称/监听值以及 notify 的值都包含中文字符。"""

    plays = load_playbook(playbook_path)
    notify_values: List[str] = []
    handler_names: List[str] = []
    listen_values: List[str] = []

    for play in plays:
        for task in iter_section_items(play, "tasks"):
            notify_values.extend(_extract_notify_values(task))
        for handler in iter_section_items(play, "handlers"):
            name = handler.get("name")
            if isinstance(name, str):
                handler_names.append(name)
            listen = handler.get("listen")
            if isinstance(listen, str):
                listen_values.append(listen)
            elif isinstance(listen, Iterable):
                for item in listen:
                    if isinstance(item, str):
                        listen_values.append(item)

    for value in notify_values:
        assert has_chinese(value), f"{playbook_path} 的 notify 值需包含中文: {value}"
    for value in handler_names + listen_values:
        assert has_chinese(value), f"{playbook_path} 的 handler/listen 需包含中文: {value}"


def assert_vars_contain_vault_reference(vars_path: Path, placeholders: Sequence[str]) -> None:
    """确保 vars 文件中包含指定的 vault_* 占位符。"""

    content = vars_path.read_text(encoding="utf-8")
    for placeholder in placeholders:
        assert placeholder in content, f"{vars_path} 需包含 {placeholder} 占位符"
