# Azure VM 模块演练指南

## 模块用途
`cloud/azure_vm` 目录使用 `azure.azcollection.azure_rm_virtualmachine` 模块演示如何以 Dry Run 方式定义虚拟机规格、映像、网络接口与磁盘。通过中文注释与变量模板，帮助团队在本地快速验证服务主体权限与网络规划，实现多订阅/多区域的一致交付。

## 主要参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `resource_group` | 目标资源组 | `rg-ansible-lab` |
| `name` | 虚拟机名称 | `vm-ansible-check` |
| `location` | 部署区域 | `southeastasia` |
| `vm_size` | 规格 | `Standard_B2ms` |
| `admin_username` | 管理账号 | `ansible` |
| `admin_password` | 管理口令（建议 Vault） | `{{ vault_azure_admin_password }}` |
| `image` | 发布商/产品/SKU/版本 | `Canonical / UbuntuServer / 22_04-lts / latest` |
| `network_interfaces` | 绑定的 NIC 名称/子网/公网 IP | `[{name: nic-01, subnet: subnet-web}]` |
| `os_type` | `linux`/`windows` | `linux` |
| `public_ip_allocation_method` | 公网 IP 策略 | `Disabled`（在 Dry Run 中避免计费） |

## 返回值
| 字段 | 说明 |
|------|------|
| `vm.id` | 虚拟机 Resource ID |
| `vm.power_state` | 计划中的电源状态 |
| `vm.tags` | 应用到资源组/实例的标签 |
| `changed` | Dry Run 是否检测到将有变更 |

## 使用情境
1. **跨订阅标准化**：统一标签、命名与磁盘大小，避免团队在不同订阅手工创建。
2. **先验网络验证**：Dry Run VNet 与子网信息，结合 `network/` 章节验证 NSG 策略，然后再将变更放行。
3. **认证演练**：在 CI 中确认 Service Principal 或 Federated Credential 是否拥有所需权限。

## 安全注意事项
1. **服务主体**：使用 `az ad sp create-for-rbac --sdk-auth` 生成的 JSON，存放于 Vault/密钥保管库；在变量文件中仅保留占位符。
2. **no_log**：Playbook 中所有涉及 `client_secret` 或密码的任务都启用了 `no_log: true`。
3. **最小权限**：角色建议基于自定义 RBAC，仅允许 `Microsoft.Compute/virtualMachines/*` + `Microsoft.Network/*` Dry Run 权限。
4. **check_mode**：本示例任务统一 `check_mode: true`，真实部署前请显式移除并再次确认变量。

## 依赖与认证
```bash
ansible-galaxy collection install azure.azcollection
pip install azure-identity azure-mgmt-compute azure-mgmt-network
az login  # 或使用 Federated 身份登录
```
- 将订阅/租户/客户端 ID 写入 `vars/example_vars.yml` 的占位字段，并以 `ansible-vault encrypt` 保护。
- 若在 Air-gapped 环境，需预先下载 `azure.azcollection` 并在离线 Galaxy 装载。

## 模拟运行步骤
1. `cd cloud/azure_vm`，根据 README 提示创建最小权限 Service Principal。
2. 在 `vars/example_vars.yml` 中填写订阅、资源组、映像、VNet 等信息；口令字段保持 `REPLACE_` 或 `{{ vault_* }}`。
3. Dry Run：
   ```bash
   ansible-playbook playbook.yml --syntax-check
   ansible-playbook playbook.yml --check -e azure_subscription_id=xxxx
   ```
4. 观察 `debug` 输出的计划，包括 VNet/VNIC 绑定与标签；若需要执行真实创建，再去除 `check_mode`。

## 延伸阅读
- [azure.azcollection.azure_rm_virtualmachine 文档](https://docs.ansible.com/ansible/latest/collections/azure/azcollection/azure_rm_virtualmachine_module.html)
- [cloud/README.md](../README.md) - 统一查看多云目录的依赖和安全策略
