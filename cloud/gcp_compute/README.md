# GCP Compute Engine 模块演练指南

## 模块用途
`cloud/gcp_compute` 目录使用 `google.cloud.gcp_compute_instance` 模块，在 Dry Run 下定义 GCE 实例、磁盘、网络与标签，帮助团队提前验证 IAM、服务帐号与 VPC 配置。示例包含详尽中文注释，并引导使用 Service Account JSON 与 Ansible Vault 管理密钥。

## 主要参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `project` | GCP 项目 ID | `ansible-lab` |
| `zone` | 可用区 | `asia-southeast2-a` |
| `name` | 实例名称 | `gce-ansible-check` |
| `machine_type` | 计算规格 | `e2-standard-2` |
| `disks` | 启动磁盘配置（映像、大小、类型） | `[{auto_delete: true, initialize_params: {source_image: projects/debian-cloud/global/images/family/debian-11}}]` |
| `network_interfaces` | 网络/子网/外部 IP | `[{network: default, subnetwork: subnet-app, access_configs: []}]` |
| `service_accounts` | 附加的服务帐号及范围 | `[{email: demo-compute@project.iam.gserviceaccount.com, scopes: ['https://www.googleapis.com/auth/cloud-platform']}]` |
| `labels` | 标签 | `{env: demo, owner: sre}` |

## 返回值
| 字段 | 说明 |
|------|------|
| `targetLink` | 计划操作的实例 SelfLink |
| `status` | Dry Run 预期状态（`RUNNING`/`TERMINATED`） |
| `changed` | 是否会产生资源变更 |

## 使用情境
1. **服务账号核验**：运行 Dry Run 验证 `roles/compute.instanceAdmin.v1`、`roles/iam.serviceAccountUser` 是否配置正确。
2. **VPC 拓扑预演**：与 `network/` 章节联动，提前检查 VPC、子网、标记、标签策略。
3. **标签审计**：统一在 Dry Run 输出阶段对比标签/自定义元数据，确保 FinOps 要求被满足。

## 安全注意事项
1. **Service Account JSON**：绝不将真实 JSON 直接写入仓库；改用 `{{ lookup('file', gcp_service_account_file) }}`、Vault 或 Secret Manager。
2. **no_log**：Playbook 已将核心任务设为 `no_log: true`，防止日志记录服务账号内容。
3. **check_mode**：所有核心任务设置 `check_mode: true`，真实部署前需人工删除该行。
4. **访问边界**：在 IAM 中为服务账号指定组织/文件夹限制，并结合 VPC Service Controls 限制 API 调用范围。

## 依赖与认证
```bash
ansible-galaxy collection install google.cloud
pip install google-auth google-auth-httplib2 google-api-python-client
# 使用 gcloud 为服务账号分配密钥，然后下载 JSON
```
- 将 JSON 路径写入 `vars/example_vars.yml`（例如 `/secure/path/sa.json`）。
- 可结合 `gcloud auth application-default login`，由 `google.auth` 自动检索凭证。

## 模拟运行步骤
1. `cd cloud/gcp_compute` 并阅读 README。
2. 在 `vars/example_vars.yml` 中设置 `gcp_project`、`gcp_zone`、`gcp_network` 等占位参数，保持 `gcp_service_account_file` 指向安全路径。
3. Dry Run：
   ```bash
   ansible-playbook playbook.yml --syntax-check
   ansible-playbook playbook.yml --check -e gcp_project=ansible-lab
   ```
4. 关注 `debug` 输出，确认标签/网络/磁盘策略符合 FinOps/SRE 规范后再移除 `check_mode`。

## 参考资料
- [google.cloud.gcp_compute_instance 模块文档](https://docs.ansible.com/ansible/latest/collections/google/cloud/gcp_compute_instance_module.html)
- [cloud/README.md](../README.md) - 统一依赖与安全清单
