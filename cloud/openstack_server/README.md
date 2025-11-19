# OpenStack Server 模块演练指南

## 模块用途
`cloud/openstack_server` 示例通过 `openstack.cloud.server` 模块展示如何结合 `clouds.yaml` 与 Ansible Vault 在私有云环境下 Dry Run 虚拟机定义。示例涵盖镜像、规格、网络、Keypair、安全组等常见字段，适合在 OpenStack、DevStack 或托管私有云中进行模拟演练。

## 主要参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `cloud` | `clouds.yaml` 中的配置名称 | `training-cloud` |
| `name` | 云主机名称 | `demo-web-01` |
| `image` | 镜像名称或 ID | `Ubuntu-22.04` |
| `flavor` | 计算规格 | `m1.small` |
| `key_name` | 绑定的 Keypair | `ansible-lab` |
| `network` | 要连接的网络名称 | `tenant-net` |
| `security_groups` | 安全组集合 | `['default', 'web']` |
| `boot_from_volume` | 是否自定义系统盘 | `true` |
| `volume_size` | 系统盘大小（GB） | `40` |
| `meta` | 自定义元数据/标签 | `{env: staging, owner: sre}` |

## 返回值
| 字段 | 说明 |
|------|------|
| `server.id` | 计划中的实例 ID |
| `server.addresses` | 网络/浮动 IP 规划 |
| `server.status` | Dry Run 阶段预期状态 |
| `changed` | 本次计划是否将创建/修改实例 |

## 使用情境
1. **私有云基线**：统一租户内主机命名、网络与 Keypair 策略。
2. **多区域预演**：结合多个 `clouds.yaml` 条目检查 Nova/Neutron Endpoints 与权限。
3. **混合云桥接**：将 virtualization/ 章节中的模板导入 Glance，再通过此 Playbook Dry Run 发布。

## 安全注意事项
1. `clouds.yaml` 中的密码/token 不应提交至仓库；变量文件中仅保留 `openstack_password_placeholder` 等字段，并提示使用 Vault。
2. Playbook 核心任务添加 `no_log: true`，避免在日志中输出 token。
3. Dry Run 时 `state: present` + `check_mode: true` 不会真正创建实例；正式执行前务必在测试项目复核配额。
4. 若使用 Application Credential，请限制有效期并绑定最小角色。

## 依赖与认证
```bash
ansible-galaxy collection install openstack.cloud
pip install openstacksdk
export OS_CLIENT_CONFIG_FILE=~/.config/openstack/clouds.yaml
```
- `clouds.yaml` 示例请参考 OpenStack 官方文档，或将其置于 Vault 保护。
- 确保 `OS_CLOUD` 环境变量与 `vars/example_vars.yml` 中的 `openstack_cloud_name` 对应。

## 模拟运行步骤
1. `cd cloud/openstack_server` 并阅读 README。
2. 在 `vars/example_vars.yml` 中填写云名称、镜像、规格、安全组等占位符，保持凭证字段使用 `REPLACE_` 与 Vault 提示。
3. Dry Run：
   ```bash
   ansible-playbook playbook.yml --syntax-check
   ansible-playbook playbook.yml --check -e openstack_cloud_name=training-cloud
   ```
4. 使用 `ansible-playbook playbook.yml -e state=present` 前请二次确认配额与网络已准备好。

## 延伸阅读
- [openstack.cloud.server 模块](https://docs.ansible.com/ansible/latest/collections/openstack/cloud/server_module.html)
- [cloud/README.md](../README.md)
