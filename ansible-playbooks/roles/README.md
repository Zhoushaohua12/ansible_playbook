# 共用角色空间 / Shared Roles Namespace

该目录用于存放在多个场景之间复用的通用 Ansible 角色。例如：

- `base_security/`：系统初始化与应用部署都需要的基线加固任务
- `log_forwarding/`：数据库、监控、备份场景共用的日志采集配置
- `notifications/`：统一的告警与消息推送逻辑

> 当前仓库暂未放置具体角色。添加新的共享角色时请遵循以下约定：
>
> 1. 角色层级必须包含 `tasks/`、`defaults/`、`handlers/`、`vars/`、`meta/` 子目录，并在 `README.md` 中注明用途与标签。
> 2. 变量名称需使用 `role_name_*` 前缀，并在 `defaults/main.yml` 提供合理默认值。
> 3. 所有敏感参数必须使用 `vault_` 前缀并结合 Ansible Vault 加密。
> 4. 在 `ansible-playbooks/README.md` 的目录导航中记录角色说明，便于其他场景引用。
