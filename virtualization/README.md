# 虚拟化与私有云资源章节

## 章节概述
`virtualization/` 目录面向 **本地虚拟化实验室**（libvirt + QEMU）与 **企业级虚拟化平台**（VMware vSphere）。通过统一的中文 README、示例 Playbook 与变量文件，演示如何在不开启真实变更的情况下验证虚拟化资源定义、磁盘操作与主机纳管流程。示例均使用 `--check` 模式或 `check_mode: true`，并在文档中强调依赖安装、认证方式、以及如何安全地模拟运行。

## 模块列表
| 模块目录 | 使用模块(FQCN) | 覆盖场景 | 关键依赖 |
|----------|----------------|----------|----------|
| [libvirt_domain](libvirt_domain/README.md) | `community.libvirt.libvirt_domain` | 定义/更新 KVM 虚拟机，适合本地实验室与边缘节点 | `community.libvirt`、libvirt-dbus/libvirtd、`qemu-kvm` |
| [vmware_host](vmware_host/README.md) | `community.vmware.vmware_host` | VMware 集群主机纳管、维护模式、证书验证 | `community.vmware`、Python `PyVmomi`、vCenter API 账号 |
| [qemu_img](qemu_img/README.md) | `community.general.qemu_img` | 管理 qcow2/raw 镜像、备份/克隆/转换 | `community.general`、`qemu-img` CLI、充足磁盘空间 |

## 依赖与认证准备
- **Collections**：`ansible-galaxy collection install community.libvirt community.vmware community.general`
- **Python 库**：
  - libvirt：`pip install libvirt-python lxml`
  - VMware：`pip install pyvmomi`，并确保 vCenter 提供具最小权限的 API 用户
- **系统工具**：
  - 安装 `libvirt-daemon`, `virt-install`, `qemu-kvm`, `virt-manager`
  - `qemu-img` 需来自 `qemu-utils`/`qemu-kvm` 包
  - VMware 环境需开放 443/API 端口并准备可信证书

## 凭证与安全
1. `vars/example_vars.yml` 仅包含占位字符串或 `{{ vault_* }}` 引用，所有真实口令请使用 `ansible-vault encrypt` 保护。
2. Playbook 中涉及密码/Token 的任务均设置 `no_log: true`，并提醒通过环境变量、HashiCorp Vault、或 Ansible Vault 注入。
3. 对本地实验室依旧推荐启用非特权 libvirt socket，通过 `ansible.builtin.command` 连接 `/var/run/libvirt/libvirt-sock-ro`。
4. VMware 管理账号需启用 MFA/应用密码，并限制到指定的 Datacenter。

## 模拟运行与验证
1. 进入模块目录并阅读 README（例如 `virtualization/libvirt_domain/README.md`）。
2. 根据中文注释修改 `vars/example_vars.yml`，保留 `REPLACE_` 前缀并在注释中提示“上线前请使用 Vault”。
3. 执行语法检查：`ansible-playbook playbook.yml --syntax-check`
4. Dry Run：`ansible-playbook playbook.yml --check`，本章节所有核心任务同样设置了 `check_mode: true`，即便忘记 `--check` 也不会真正创建/删除资源。
5. 需要进一步验证时，可在隔离的 libvirt/ESXi 沙箱执行正式命令。

## 文件结构
```
virtualization/
├── README.md
├── libvirt_domain/
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── vmware_host/
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
└── qemu_img/
    ├── README.md
    ├── playbook.yml
    └── vars/example_vars.yml
```

## 与其他章节的关系
- **cloud/**：先在 virtualization 中模拟主机/镜像，再将成熟拓扑迁移到 AWS/Azure/GCP/OpenStack/ECS。
- **system/**：虚拟机模板准备完成后，可直接调用 system 模块完成用户、服务、网络基线配置。
- **storage/**：`qemu_img` 示例可与 storage 章节的 loopback/LVM 演练联动，统一演示磁盘格式化与挂载。

## 学习路径建议
1. **本地实验室**：从 `libvirt_domain` 入手，理解 XML/网络/磁盘参数；再练习 `qemu_img` 进行镜像快照与转换。
2. **企业虚拟化**：将思路迁移至 `vmware_host`，学习如何在 vCenter 中纳管 ESXi、维护模式以及证书验证。
3. **混合场景**：结合 cloud 章节，用同一套变量与标签策略管理本地与公有云资源。

## 快速导航
- [libvirt_domain 模块说明](libvirt_domain/README.md)
- [vmware_host 模块说明](vmware_host/README.md)
- [qemu_img 模块说明](qemu_img/README.md)
