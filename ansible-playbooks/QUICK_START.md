# Ansible Playbooks Hub - 快速上手指南

本指南用于帮助你在几分钟内完成环境准备、依赖安装、Inventory 定制以及 Playbook 执行前的验证。所有步骤均以中文说明，适用于 Ubuntu/Debian、RHEL/CentOS、Rocky Linux 以及其他常见企业 Linux 发行版。

---

## ✅ 前提条件

| 组件 | 最低版本 | 备注 |
|------|-----------|------|
| Python | 3.8+ | 建议使用 `python3 -m venv` 创建隔离环境 |
| Ansible | 2.15+ | 需开启 FQCN 支持，确保 `ansible --version` 正常 |
| SSH | OpenSSH 8+ | 目标主机需允许基于密钥的 SSH 访问 |
| 系统 | Ubuntu 20.04+/22.04+, Debian 11+, RHEL 8+/9+, CentOS 7, Rocky 9 | 其他兼容发行版可参考 system-init Playbook 自定义 |

---

## 📦 安装依赖

```bash
# 1. 创建并激活虚拟环境（可选）
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装 Python 依赖
pip install --upgrade pip
pip install -r requirements.txt

# 3. 安装必备 Collections
ansible-galaxy collection install -r collections/requirements.yml

# 4. （可选）安装共享角色依赖
# ansible-galaxy role install -r ansible-playbooks/requirements.yml

# 5. 验证版本
ansible --version
ansible-galaxy collection list | grep community
```

> **提示**：默认读取 `ansible-playbooks/ansible.cfg`。如果你在仓库根目录执行命令，可显式指定：
> `ANSIBLE_CONFIG=ansible-playbooks/ansible.cfg ansible-playbook ...`

---

## 🗺️ 准备 Inventory 与变量

1. 复制示例 Inventory：
   ```bash
   cp ansible-playbooks/inventory/hosts my-hosts.ini
   export ANSIBLE_INVENTORY=my-hosts.ini
   ```
2. 根据真实环境修改各组主机：`init_servers`、`nginx_servers`、`database_servers`、`app_servers`、`monitoring_servers`、`backup_servers`。
3. 为不同环境创建独立的 `group_vars`：
   ```bash
   cp ansible-playbooks/inventory/group_vars/all.yml group_vars/all.yml
   cp ansible-playbooks/inventory/group_vars/nginx_servers.yml group_vars/nginx_servers.yml
   ```
4. 替换所有 `vault_` 前缀的占位符，并使用 Ansible Vault 加密：
   ```bash
   ansible-vault encrypt group_vars/all.yml group_vars/database_servers.yml
   ansible-vault view group_vars/database_servers.yml
   ```
5. 使用 `ansible-inventory` 验证：
   ```bash
   ansible-inventory -i my-hosts.ini --list
   ansible all -i my-hosts.ini -m ping
   ```

---

## 🧪 运行前验证

| 操作 | 命令示例 | 说明 |
|------|-----------|------|
| 语法检查 | `ansible-playbook --syntax-check system-init/bootstrap.yml` | 在不连接远端主机的情况下验证语法 |
| Dry-run（检查模式） | `ansible-playbook -i inventory/hosts system-init/bootstrap.yml --check --diff` | 观察将要发生的变更 |
| 限制主机范围 | `ansible-playbook -i inventory/hosts web-services/nginx-install.yml -l nginx_servers` | 只对选定主机执行 |
| 按标签执行 | `ansible-playbook -i inventory/hosts application-deploy/lnmp-stack-deploy.yml --tags "packages,config"` | 精准执行特定步骤 |
| 跳过标签 | `ansible-playbook -i inventory/hosts monitoring/prometheus-install.yml --skip-tags verify` | 忽略耗时的校验步骤 |
| 列出标签/主机 | `ansible-playbook application-deploy/docker-install.yml --list-tags --list-hosts` | 快速了解影响范围 |

> **最佳实践**：任何会修改系统的 Playbook 都应先执行 `--syntax-check` 和 `--check`，随后再进行真实部署。

---

## 🔧 常见执行场景

### 1. 新主机初始化
```bash
ansible-playbook -i inventory/hosts system-init/ubuntu-debian-init.yml --check
ansible-playbook -i inventory/hosts system-init/ubuntu-debian-init.yml --tags hardening
```

### 2. 部署高可用 Nginx
```bash
ansible-playbook -i inventory/hosts web-services/nginx-install.yml --syntax-check
ansible-playbook -i inventory/hosts web-services/nginx-install.yml --check -l nginx_servers
ansible-playbook -i inventory/hosts web-services/nginx-install.yml --tags "packages,config,reload"
```

### 3. 发布 LNMP / Node.js 应用
```bash
ansible-playbook -i inventory/hosts application-deploy/lnmp-stack-deploy.yml --check
ansible-playbook -i inventory/hosts application-deploy/nodejs-app-deploy.yml --tags deploy --limit app_servers
```

### 4. 监控与备份
```bash
ansible-playbook -i inventory/hosts monitoring/prometheus-install.yml --check
ansible-playbook -i inventory/hosts maintenance/backup-strategy.yml --tags verify
```

---

## 🆘 故障排除

### SSH 连接失败
```bash
# 测试连通性并查看详细日志
ansible all -i inventory/hosts -m ping -vvv
ssh -i ~/.ssh/id_rsa ubuntu@10.20.0.21 -o StrictHostKeyChecking=no

# 刷新 ssh-agent
ssh-add ~/.ssh/id_rsa
ssh-add -L
```
- 确认 `ansible_user`、`ansible_port`、`ansible_ssh_private_key_file` 与目标主机一致。
- 如果在 CI 中执行，可关闭 `host_key_checking`（已在 `ansible.cfg` 默认关闭）。

### Vault / 认证错误
```bash
ansible-playbook -i inventory/hosts database/mysql-8.0-install.yml --ask-vault-pass
ansible-vault decrypt group_vars/database_servers.yml
```
- 检查所有 `vault_*` 变量是否已加密，避免提交明文凭证。
- 使用 `--vault-password-file ~/.vault_pass.txt` 自动化解密流程。

### 配置差异或变量未生效
```bash
# 查看 Ansible 实际生效的配置
ansible-config dump --only-changed

# 检查 Inventory 解析结果
ansible-inventory -i inventory/hosts --graph

# 打印特定变量
ansible -i inventory/hosts nginx_servers -m debug -a 'var=hostvars[inventory_hostname]'
```
- 确认 `ANSIBLE_CONFIG`、`ANSIBLE_INVENTORY` 环境变量是否指向预期文件。
- 若 handler 未触发，可加 `--tags handler` 或 `--force-handlers` 排查。

### 其他建议
- 使用 `-vvv` 增强调试信息：`ansible-playbook ... -vvv`
- 通过 `--limit host1,host2` 缩小影响范围
- 在执行危险操作前使用 `--check --diff` 预览文件变化

---

## 📚 下一步
- 阅读 [README.md](./README.md) 了解整体目录结构、支持的操作系统以及 FQCN/标签规范。
- 根据场景进入对应子目录（system-init、web-services、database、application-deploy、monitoring、maintenance）查看详细 Playbook。
- 为共享逻辑创建/复用 `ansible-playbooks/roles/` 下的角色，统一变量命名与标签。

如需更多帮助，请在问题出现时附上 `-vvv` 日志与 `ansible-config dump --only-changed` 的输出，便于快速定位。祝你自动化愉快！
