# AWS EC2 模块演练指南

## 模块用途
`cloud/aws_ec2` 示例通过 `community.aws.ec2_instance` 模块演示如何在 AWS 上定义/标记 EC2 实例、绑定网络组件，并在 `check_mode: true` 下预览所需资源。示例特别适合想要在无真实凭证的环境中，理解实例创建参数、标签治理与安全组依赖的读者。

## 主要参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `name` | EC2 实例名称/Tag | `ansible-training` |
| `instance_type` | 计算规格 | `t3.small` |
| `image_id` | AMI ID（建议使用公共 AMI） | `ami-0abcdef1234567890` |
| `region` | 部署区域 | `ap-southeast-1` |
| `key_name` | 登录密钥对名称 | `training-key` |
| `network.subnet_id` | 子网 ID | `subnet-0abc123` |
| `network.security_groups` | 关联安全组 | `['sg-0123abcd']` |
| `network.assign_public_ip` | 是否分配公网 IP | `false` |
| `tags` | 资源标签 | `{Env: demo, Owner: platform}` |
| `wait` | 是否等待实例 ready | `false`（在 Dry Run 中保持 false） |

## 返回值
| 字段 | 说明 |
|------|------|
| `instances` | 包含 instance_id、私网/公网 IP、状态的列表 |
| `tags` | 最终应用的标签集合 |
| `changed` | Dry Run 中用于确认计划是否会修改资源 |

## 使用情境
1. **多账号基线**：在多个 AWS 账号中统一实例命名、标签与网络策略。
2. **安全演练**：结合 `network/` 模块 Dry Run 安全组与 NACL，随后在云平台验证。
3. **混合云迁移**：与 `virtualization/` 中的 libvirt、VMware 模拟相互对照，提前确认规格映射。

## 安全注意事项
1. **凭证隔离**：示例变量使用 `REPLACE_` 前缀并建议通过 `ansible-vault encrypt vars/example_vars.yml` 保护，或改为读取 `AWS_ACCESS_KEY_ID` 环境变量。
2. **无密钥提交**：Playbook 已设置 `no_log: true`；若添加新的任务也需继承 `no_log`，避免在 CI/CD 日志中泄露 access key。
3. **最小权限**：IAM 用户至少需要 `ec2:Describe*` 与 Dry Run 权限；在真实执行前才赋予 `ec2:RunInstances`。
4. **Dry Run 强制**：`check_mode: true` 以及 README 中的 `--check` 步骤确保不会误创建实例。

## 依赖与认证
```bash
ansible-galaxy collection install community.aws
pip install boto3 botocore
aws configure  # 或使用环境变量/IMDS
```
- 推荐使用 `~/.aws/credentials` 或 AWS SSO profile，通过变量 `aws_profile` 切换。
- 若在企业网络执行，请配置代理或 VPC 终端节点，避免阻断 `ec2.amazonaws.com` 调用。

## 模拟运行步骤
1. `cd cloud/aws_ec2` 并阅读 `README.md`。
2. 根据 `vars/example_vars.yml` 的中文注释填写区域、子网、安全组等信息，保持凭证字段为占位符或 `{{ vault_aws_secret }}`。
3. 执行：
   ```bash
   ansible-playbook playbook.yml --syntax-check
   ansible-playbook playbook.yml --check -e aws_profile=training
   ```
4. 观察 `debug` 任务输出的 Dry Run 计划，确认无误后再在受控环境取消 `check_mode`。

## 扩展阅读
- [community.aws.ec2_instance 官方文档](https://docs.ansible.com/ansible/latest/collections/community/aws/ec2_instance_module.html)
- [cloud/README.md](../README.md) - 查看多云目录的依赖与安全提示
