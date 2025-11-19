# 云资源与多云编排章节

## 章节概述
本章节聚焦云计算与多云环境中的算力交付，汇总了 AWS、Azure、GCP、OpenStack、阿里云等典型平台的 Ansible Playbook 示例。所有 Playbook 默认以 `--check` 模式/`check_mode: true` 执行，帮助读者在没有真实凭证的情况下模拟变更；示例同时提供中文注释、依赖安装说明、认证方式提示，并强调 **切勿在仓库中存放真实密钥**。

## 模块列表
| 模块目录 | 使用模块(FQCN) | 主要用途 | 关键依赖 |
|----------|----------------|----------|----------|
| [aws_ec2](aws_ec2/README.md) | `community.aws.ec2_instance` | 预演 EC2 实例生命周期与标签策略 | `community.aws`、`boto3`、AWS CLI/环境凭证 |
| [azure_vm](azure_vm/README.md) | `azure.azcollection.azure_rm_virtualmachine` | 管理 Azure VM、磁盘与网络接口 | `azure.azcollection`、`azure-identity`、服务主体凭证 |
| [gcp_compute](gcp_compute/README.md) | `google.cloud.gcp_compute_instance` | 通过服务账号 Dry Run 创建 GCE 实例 | `google.cloud`、`google-auth`、Service Account JSON |
| [openstack_server](openstack_server/README.md) | `openstack.cloud.server` | 使用 clouds.yaml 管理私有云虚机 | `openstack.cloud`、`openstacksdk`、clouds.yaml 认证 |
| [aliyun_ecs](aliyun_ecs/README.md) | `alibaba.cloud.ali_ecs` | 规划阿里云 ECS 计算与网络属性 | `alibaba.cloud`、`aliyun-python-sdk-core`、RAM 访问密钥 |

## 认证与依赖准备
### Collection 安装
```bash
ansible-galaxy collection install community.aws azure.azcollection google.cloud openstack.cloud alibaba.cloud
```

### Python/CLI 依赖
- **AWS**：`pip install boto3 botocore`；使用 `aws configure` 或环境变量导入密钥。
- **Azure**：`pip install azure-identity azure-mgmt-compute`，并创建具备最小权限的 Service Principal（`az ad sp create-for-rbac`）。
- **GCP**：`pip install google-auth google-auth-httplib2 google-api-python-client`，下载仅具必要 IAM 角色的 Service Account JSON。
- **OpenStack**：`pip install openstacksdk` 并维护 `~/.config/openstack/clouds.yaml`。
- **阿里云**：`pip install aliyun-python-sdk-core`，在 RAM 控制台创建访问密钥并限制到指定项目。

> **认证提示**：所有示例默认从 `vars/example_vars.yml` 读取占位符或通过环境变量/Ansible Vault 注入。运行前请先执行 `ansible-vault encrypt cloud/<module>/vars/example_vars.yml`，或将密钥放入 CI 的 Vault/Secret Manager 中。任何真实凭证必须通过 `no_log: true` 防止泄露。

## 模拟运行步骤
1. 进入模块目录（例：`cd cloud/aws_ec2`）。
2. 根据中文注释修改 `vars/example_vars.yml`，保留 `REPLACE_`/`your_` 占位并加入 Vault 提示。
3. 运行 `ansible-playbook playbook.yml --syntax-check`，随后执行 `ansible-playbook playbook.yml --check` 进行 Dry Run。
4. 真正部署前，确认依赖集合与 SDK 已安装，且凭证来自 Vault 或环境变量。

## 文件结构
```
cloud/
├── README.md
├── aws_ec2/
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── azure_vm/
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── gcp_compute/
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── openstack_server/
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
└── aliyun_ecs/
    ├── README.md
    ├── playbook.yml
    └── vars/example_vars.yml
```

## 安全注意事项
1. **最小权限**：为每个示例创建只读或 Dry Run 用的角色，例如 AWS IAM `ReadOnlyAccess` + `ec2:RunInstances` 受限策略。
2. **Vault 强制**：默认注释提醒使用 `ansible-vault encrypt vars/example_vars.yml`，严禁在仓库中出现真实 Access Key。
3. **网络隔离**：在安全组/VNet/VPC 中仅开放演练所需端口，所有示例通过 `check_mode: true` 避免误创建资源。
4. **日志脱敏**：Playbook 统一设置 `no_log: true`，并在 README 中强调如何使用 `no_log: true` 和环境变量。

## 与其他章节协同
- **virtualization/**：在本地 libvirt/VMware 集群中演练拓扑，再把成熟架构迁移至云平台。
- **system/** 与 **network/**：云实例真正创建后，可复用系统/网络章节的硬化 Playbook。
- **monitoring/**：Dry Run 完成后，将配置推送到监控章节提供的 playbook，实现云主机可观测性。

## 快速导航
- [AWS EC2 模块说明](aws_ec2/README.md)
- [Azure VM 模块说明](azure_vm/README.md)
- [GCP Compute 模块说明](gcp_compute/README.md)
- [OpenStack Server 模块说明](openstack_server/README.md)
- [阿里云 ECS 模块说明](aliyun_ecs/README.md)
