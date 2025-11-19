# VMware Host 模块演练指南

## 模块用途
`virtualization/vmware_host` 示例使用 `community.vmware.vmware_host`（或 `community.vmware.vmware_guest`）模块，在 `check_mode: true` 下演练 ESXi 主机纳管、维护模式与标签策略。示例针对企业级虚拟化场景，帮助 SRE/虚拟化团队在无需触碰真实生产集群的前提下验证 vCenter API、证书与凭证配置。

## 主要参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `hostname` | vCenter 地址 | `vcenter.corp.local` |
| `username` / `password` | API 账号（建议 Vault） | `svc-ansible@vsphere.local` |
| `esxi_hostname` | ESXi 主机 FQDN/IP | `esxi-01.lab.local` |
| `cluster_name` | 目标集群 | `Prod-Cluster` |
| `state` | `present` / `absent` / `maintenance` | `present` |
| `validate_certs` | 是否验证证书 | `false`（实验环境可关闭） |
| `license` | （可选）要应用的许可证 | `AAAAA-AAAAA-AAAAA-AAAAA-AAAA` |

## 返回值
| 字段 | 说明 |
|------|------|
| `result.changed` | Dry Run 是否检测到主机状态变化 |
| `result.esxi_hostname` | 主机名/FQDN |
| `result.state` | 目标维护/纳管状态 |

## 使用情境
1. **主机纳管演练**：在引入新 ESXi 节点前，使用 Dry Run 校验凭证、集群名与网络连通性。
2. **维护模式排程**：提前验证 Playbook 是否会把主机置入维护模式，并输出要迁移的工作负载摘要。
3. **证书/安全检查**：确保 vCenter 证书链、生效域账号或 Token 验证流程正确。

## 安全注意事项
1. **凭证保护**：变量文件仅存放占位符或 `{{ vault_vmware_password }}`；真实凭证请用 `ansible-vault encrypt vars/example_vars.yml` 或 CI Secret 注入。
2. **no_log**：模块任务启用 `no_log: true`，避免 API 响应出现在日志中。
3. **网络隔离**：仅在含有 vCenter API 的内网执行 Playbook，并在 README 中提醒启用最小权限角色（如自定义 `AnsibleOperator` 角色）。
4. **check_mode**：所有核心任务 `check_mode: true`，真实执行前请复制 Playbook 并移除此标记。

## 依赖与认证
```bash
ansible-galaxy collection install community.vmware
pip install pyvmomi
# 准备 vCenter 账号：RBAC 仅授予主机管理相关权限
```
- 可使用环境变量 `VMWARE_HOST`/`VMWARE_USER`/`VMWARE_PASSWORD`，或 `export` 至 CI Secret。
- 若企业要求启用代理，请确保 443 端口与 NTP/证书同步可用。

## 模拟运行步骤
1. `cd virtualization/vmware_host`。
2. 在 `vars/example_vars.yml` 中填写 vCenter/集群/ESXi 名称，凭证字段保持 `REPLACE_` 或 `{{ vault_* }}`。
3. Dry Run：
   ```bash
   ansible-playbook playbook.yml --syntax-check
   ansible-playbook playbook.yml --check
   ```
4. 查看 `debug` 输出，确认纳管计划、维护模式与标签信息，确保未直接触碰生产集群。

## 参考资料
- [community.vmware Collection](https://docs.ansible.com/ansible/latest/collections/community/vmware/)
- [virtualization/README.md](../README.md)
