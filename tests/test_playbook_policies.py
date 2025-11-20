"""统一的 playbook/vars 合规性校验，确保核心规范不会回归。"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import pytest

from tests.utils.assertions import (
    assert_handlers_and_notifies_use_chinese,
    assert_playbook_contains_no_log_task,
    assert_playbook_has_common_controls,
    assert_vars_contain_vault_reference,
    assert_warning_header,
)

REPO_ROOT = Path(__file__).parent.parent
PLAYBOOK_DIRECTORIES = [
    "applications",
    "commands",
    "database",
    "files",
    "message_queue",
    "monitoring",
    "network",
    "network_protocols",
    "system",
    "web",
]


def _collect_files(pattern: str, base_dirs: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for rel_dir in base_dirs:
        base_path = REPO_ROOT / rel_dir
        if not base_path.exists():
            continue
        files.extend(sorted(base_path.glob(pattern)))
    return files


PLAYBOOKS = _collect_files("*/playbook.yml", PLAYBOOK_DIRECTORIES)
VAR_FILES = _collect_files("*/vars/example_vars.yml", PLAYBOOK_DIRECTORIES)

SENSITIVE_PLAYBOOKS = [
    "applications/docker_container",
    "applications/docker_image",
    "applications/kubernetes",
    "database/mysql_db",
    "database/mysql_user",
    "database/postgresql_db",
    "database/postgresql_user",
    "database/mongodb_user",
    "network_protocols/uri",
]

VAULT_PLACEHOLDERS = [
    (
        "applications/docker_container",
        ["vault_redis_password", "vault_app_database_url", "vault_app_secret_key"],
    ),
    ("network_protocols/uri", ["vault_api_token"]),
    (
        "message_queue/rabbitmq_user",
        ["vault_rabbitmq_admin_user", "vault_rabbitmq_admin_password"],
    ),
]


@pytest.mark.parametrize(
    "playbook_path",
    PLAYBOOKS,
    ids=lambda path: str(path.relative_to(REPO_ROOT)),
)
def test_playbooks_have_common_controls(playbook_path: Path) -> None:
    assert_playbook_has_common_controls(playbook_path)


@pytest.mark.parametrize(
    "playbook_path",
    PLAYBOOKS,
    ids=lambda path: f"handlers::{path.relative_to(REPO_ROOT)}",
)
def test_handlers_and_notifies_are_readable(playbook_path: Path) -> None:
    assert_handlers_and_notifies_use_chinese(playbook_path)


@pytest.mark.parametrize(
    "vars_path",
    VAR_FILES,
    ids=lambda path: str(path.relative_to(REPO_ROOT)),
)
def test_vars_files_have_warning_header(vars_path: Path) -> None:
    assert_warning_header(vars_path)


@pytest.mark.parametrize(
    "relative_dir",
    SENSITIVE_PLAYBOOKS,
    ids=lambda value: f"no-log::{value}",
)
def test_sensitive_playbooks_use_no_log(relative_dir: str) -> None:
    playbook_path = REPO_ROOT / relative_dir / "playbook.yml"
    assert playbook_path.exists(), f"敏感模块缺少 playbook: {relative_dir}"
    assert_playbook_contains_no_log_task(playbook_path)


@pytest.mark.parametrize(
    "relative_dir, placeholders",
    VAULT_PLACEHOLDERS,
    ids=lambda value: f"vault::{value[0]}",
)
def test_sensitive_vars_use_vault_placeholders(relative_dir: str, placeholders: list[str]) -> None:
    vars_path = REPO_ROOT / relative_dir / "vars" / "example_vars.yml"
    assert vars_path.exists(), f"敏感模块缺少示例变量: {relative_dir}"
    assert_warning_header(vars_path)
    assert_vars_contain_vault_reference(vars_path, placeholders)
