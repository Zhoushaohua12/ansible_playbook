# 网络模块实践指南

## 章节概览
本章节介绍 Ansible 中网络配置与监控的核心模块，涵盖防火墙规则管理（firewalld/ufw/iptables）、网络连接监控（wait_for）、端口健康探测（port）、静态路由管理（route）和网络接口管理（interface）。这些模块广泛应用于安全加固、容器编排、多层部署、网络配置管理等场景，所有示例均包含中文注释和最佳实践说明。

## 与 system/firewall 的区别
本 `network/` 目录专注于**跨系统网络配置与监控**的通用模块：
- **network/ 职责**：防火墙规则管理、端口监控、网络配置下发、接口管理、路由配置（不涉及系统初始化）
- **system/firewall 职责**（若存在）：系统启动、服务启动、初始化脚本等系统级操作

## 模块清单

| 模块 | 功能 | 适用场景 | 外部依赖 |
|------|------|----------|----------|
| **firewalld** | 动态防火墙规则管理 | RHEL/CentOS/Fedora 环境，需要热更新防火墙规则 | firewalld 服务、community.general collection |
| **ufw** | Ubuntu/Debian 防火墙管理 | Debian/Ubuntu 环境，快速配置简化防火墙 | ufw 命令行工具、community.general collection |
| **iptables** | 内核级防火墙和 NAT 规则 | 直接操作内核防火墙规则、NAT 转发、自定义规则链 | iptables 工具、community.general collection |
| **wait_for** | 端口/服务可用性监控 | 等待服务启动、集群协调、滚动更新验证 | 内置模块（无外部依赖） |
| **port** | 端口健康探测 | 从控制节点检查远程服务端口可用性、批量端口监控 | 内置模块（无外部依赖） |
| **route** | 静态路由管理 | 多网卡环境、VPN 配置、容器网络、复杂网络拓扑 | ansible.posix collection、系统路由工具 |
| **interface** | 网络接口管理 | 服务器网络配置、虚拟化管理、高可用网络、移动设备 | community.general collection、NetworkManager 服务 |
| **nmcli** | NetworkManager 网络连接管理 | 以太网、无线、VLAN、网桥、绑定等网络连接配置 | community.general collection、NetworkManager 服务 |

## 涉及模块

### 防火墙管理
- [firewalld 模块](firewalld/README.md)：RHEL 系统防火墙规则管理，支持 zone、service、port 配置
- [ufw 模块](ufw/README.md)：Ubuntu/Debian 防火墙规则管理，支持简化的 allow/deny/delete 操作
- [iptables 模块](iptables/README.md)：内核级防火墙规则管理，支持 NAT、DNAT、SNAT 等高级用途

### 网络监控
- [wait_for 模块](wait_for/README.md)：端口监控与服务可用性验证，支持延时与重试机制
- [port 模块](port/README.md)：端口健康探测，支持批量检查、超时控制和 delegate_to 安全检查

### 网络配置
- [route 模块](route/README.md)：静态路由管理，支持多接口路由、优先级设置和系统兼容性
- [interface 模块](interface/README.md)：网络接口管理，支持以太网、网桥、绑定、VLAN 等接口类型
- [nmcli 模块](nmcli/README.md)：NetworkManager 网络连接管理，支持以太网、无线、VLAN、网桥、绑定等连接配置

## 安全使用建议

### 通用原则
1. **最小权限原则**：仅为必要的端口、源 IP 开放访问权限
2. **分层部署**：在开发/测试环境验证规则后，再部署到生产环境
3. **变更记录**：使用版本控制追踪防火墙规则变更
4. **幂等性设计**：使用 `state` 参数确保规则的重复执行安全性

### 模块特定注意事项
- **firewalld**：避免与 SELinux 政策冲突，使用 zone 隔离规则集
- **ufw**：规则顺序重要，`default` 政策应放在具体规则之前
- **iptables**：直接操作内核，应定期备份和验证规则
- **wait_for**：过长的超时时间会影响 playbook 执行效率，建议设置合理的 delay 和 retries
- **port**：使用 `delegate_to: localhost` 从控制节点检查，避免在目标主机执行不必要的连接
- **route**：路由配置需要 root 权限，修改前备份当前路由表，避免网络中断
- **interface**：接口配置变更可能影响网络连通性，生产环境建议通过控制台操作

## 使用情境

### 分层环境部署
在微服务或多层应用环境中，不同层级的服务需要独立的网络隔离：
- **Web 层**：开放 80/443 端口，限制源 IP 为负载均衡器
- **应用层**：开放特定应用端口（如 8080），限制源 IP 为 Web 层
- **数据库层**：开放 3306/5432 等，仅允许应用层访问

### 远程主机安全加固
在批量部署或云环境中快速统一网络策略：
- 使用 firewalld/ufw 模块批量部署标准安全策略
- 通过 wait_for 和 port 模块验证服务可用性
- 使用 route 模块配置特定网络路由
- 通过 interface 模块标准化网络接口配置
- 结合监控模块（监听告警）形成完整安全链路

### 容器编排与 overlay 网络
在 Kubernetes 或 Docker Swarm 中管理容器网络：
- 管理宿主机防火墙规则，允许容器通信
- 监控应用服务端口可用性
- 配置 NAT 规则支持容器访问外部网络
- 使用 interface 模块管理网桥和容器网络接口
- 通过 route 模块配置容器网络路由

## 环境依赖

### Ansible Collections
```bash
# 安装必要的集合
ansible-galaxy collection install community.general
ansible-galaxy collection install ansible.posix
```

### 系统工具
根据使用的模块安装对应系统工具：
```bash
# firewalld 环境（RHEL/CentOS/Fedora）
yum install -y firewalld

# UFW 环境（Ubuntu/Debian）
apt install -y ufw

# iptables 环境（通用）
# 大多数 Linux 系统已内置，若无则安装
yum install -y iptables
# 或
apt install -y iptables

# 路由管理工具
yum install -y iproute
# 或
apt install -y iproute2

# 网络接口管理工具
yum install -y NetworkManager
# 或
apt install -y network-manager
```

## 文件结构
```
network/
├── README.md                          # 本说明文档
├── firewalld/                         # firewalld 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── ufw/                               # ufw 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── iptables/                          # iptables 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── wait_for/                          # wait_for 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── port/                              # port 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── route/                             # route 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
└── interface/                         # interface 模块示例
    ├── README.md
    ├── playbook.yml
    └── vars/example_vars.yml
```

## 快速开始

### 1. 安装依赖
```bash
# 安装 community.general 和 ansible.posix 集合
ansible-galaxy collection install community.general
ansible-galaxy collection install ansible.posix

# 在目标主机上安装系统工具（根据需要）
# Debian/Ubuntu
sudo apt install -y ufw network-manager iproute2

# RHEL/CentOS
sudo yum install -y firewalld NetworkManager iproute
```

### 2. 运行网络配置
```bash
# 检查语法
ansible-playbook network/firewalld/playbook.yml --syntax-check

# Dry-Run 预览
ansible-playbook network/firewalld/playbook.yml -i hosts.ini --check

# 执行配置
ansible-playbook network/firewalld/playbook.yml -i hosts.ini
```

### 3. 验证网络配置
```bash
# 使用 wait_for 验证服务端口
ansible-playbook network/wait_for/playbook.yml -i hosts.ini

# 使用 port 模块进行端口健康探测
ansible-playbook network/port/playbook.yml -i hosts.ini --check

# 使用 route 模块管理静态路由
ansible-playbook network/route/playbook.yml -i hosts.ini --check

# 使用 interface 模块管理网络接口
ansible-playbook network/interface/playbook.yml -i hosts.ini --check
```

## 测试与验证

### 本地测试
所有 playbook 都支持 `--check` 模式，用于预览变更而不实际修改系统：
```bash
ansible-playbook network/[module]/playbook.yml --check
```

### pytest 验证
自动检查文档结构、中文注释和安全规范：
```bash
# 在项目根目录运行
pytest tests/network/test_network.py -v
```

## 常见问题

### firewalld vs ufw vs iptables 如何选择？
- **firewalld**：RHEL 系统的标准选择，支持 zone 和动态更新
- **ufw**：Ubuntu/Debian 系统，规则简化易维护
- **iptables**：需要高度自定义规则或 NAT 场景

### 如何安全地修改网络配置？
1. 在测试环境验证配置
2. 使用 `--check` 模式预览变更
3. 分阶段更新，保持回滚能力
4. 在修改前备份当前配置
5. 通过控制台或带外管理进行操作

### port 模块与 wait_for 模块的区别？
- **port 模块**：专注于端口健康探测，使用 delegate_to 从控制节点检查，支持批量操作
- **wait_for 模块**：通用等待模块，支持文件、端口、日志等多种等待场景

### route 模块和 interface 模块的使用场景？
- **route 模块**：管理静态路由表，适用于多网卡、VPN、复杂网络拓扑
- **interface 模块**：管理网络接口配置，适用于服务器标准化、虚拟化、高可用网络

## 相关链接
- [firewalld 官方文档](https://firewalld.org/)
- [UFW 官方文档](https://help.ubuntu.com/community/UFW)
- [iptables 官方文档](https://linux.die.net/man/8/iptables)
- [Ansible wait_for 模块](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/wait_for_module.html)
- [Ansible community.general.firewalld](https://docs.ansible.com/ansible/latest/collections/community/general/firewalld_module.html)
- [Ansible community.general.ufw](https://docs.ansible.com/ansible/latest/collections/community/general/ufw_module.html)
- [Ansible community.general.iptables](https://docs.ansible.com/ansible/latest/collections/community/general/iptables_module.html)
- [Ansible ansible.posix.route](https://docs.ansible.com/ansible/latest/collections/ansible/posix/route_module.html)
- [Ansible community.general.nmcli](https://docs.ansible.com/ansible/latest/collections/community/general/nmcli_module.html)
- [NetworkManager 官方文档](https://networkmanager.dev/)
