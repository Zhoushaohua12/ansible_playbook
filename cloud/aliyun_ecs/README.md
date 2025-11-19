# 阿里云 ECS 模块演练指南

## 模块用途
`cloud/aliyun_ecs` 目录示范 `alibaba.cloud.ali_ecs` 模块在 ECS 实例规划、网络与标签治理中的用法。所有任务均启用 `check_mode: true` 与 `no_log: true`，确保在没有真实访问密钥的环境下安全地学习/演练。

## 主要参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `alicloud_region` | 部署 Region | `cn-hongkong` |
| `instance_name` | ECS 实例名称 | `ecs-ansible-check` |
| `instance_type` | 规格 | `ecs.g6.large` |
| `image_id` | 镜像 ID | `ubuntu_22_04_x64_20G_alibase_20230808.vhd` |
| `vswitch_id` | 交换机 ID | `vsw-abc123` |
| `security_group_id` | 安全组 ID | `sg-abc123` |
| `password` / `key_pair_name` | 登录方式（建议使用密钥） | `{{ vault_aliyun_password }}` |
| `internet_charge_type` | 公网计费方式 | `PayByTraffic` |
| `tags` | 标签 | `{Env: demo, Owner: cloud-team}` |

## 返回值
| 字段 | 说明 |
|------|------|
| `instance_id` | Dry Run 计划的实例 ID |
| `public_ip` / `private_ip` | 分配的 IP 地址 |
| `changed` | Dry Run 是否检测到变更 |

## 使用情境
1. **跨 Region 预演**：验证 VPC/VSwitch/安全组在不同 Region 的参数是否一致。
2. **成本审计**：结合标签输出 FinOps 信息，确定实例规格、计费方式符合预算。
3. **混合云接入**：与 `network/` 和 `system/` Playbook 搭配，在真正上线前完成配置编排演练。

## 安全注意事项
1. **RAM 凭证管理**：AccessKey ID/Secret 仅保留占位符，真实值必须由 `ansible-vault` 或环境变量提供。
2. **最小权限策略**：为 RAM 用户附加自定义策略，仅允许 `Ecs:Describe*` 和必要的 `Ecs:RunInstances`，并在 Dry Run 阶段禁用自动付费资源。
3. **日志脱敏**：Playbook 核心任务 `no_log: true` 避免在 CI 中泄露 AccessKey。
4. **Region 限制**：若启用了多账号管理，结合 `Resource Directory`/`RAM` 仅授权特定 Region 的操作。

## 依赖与认证
```bash
ansible-galaxy collection install alibaba.cloud
pip install aliyun-python-sdk-core aliyun-python-sdk-ecs
# 建议使用 aliyun CLI 进行 sts/token 演练
```
- 通过 `aliyun ram CreateAccessKey` 为自动化账号生成密钥，并启用 MFA。
- 在 `vars/example_vars.yml` 提供占位符，并记录“上线前请加密”提示。

## 模拟运行步骤
1. `cd cloud/aliyun_ecs`。
2. 打开 `vars/example_vars.yml`，根据注释填写 Region、VSwitch、安全组、标签等字段，凭证使用 `REPLACE_WITH_ACCESS_KEY` 占位。
3. 执行：
   ```bash
   ansible-playbook playbook.yml --syntax-check
   ansible-playbook playbook.yml --check -e aliyun_region=cn-hangzhou
   ```
4. 核对 `debug` 任务输出，确认 Dry Run 计划后再在受控环境取消 `check_mode`。

## 更多资料
- [alibaba.cloud.ali_ecs 模块](https://docs.ansible.com/ansible/latest/collections/alibaba/cloud/ali_ecs_module.html)
- [cloud/README.md](../README.md)
