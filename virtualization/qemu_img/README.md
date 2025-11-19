# qemu_img 模块演练指南

## 模块用途
`virtualization/qemu_img` 使用 `community.general.qemu_img` 模块演示如何在 Dry Run 环境下规划镜像克隆、格式转换与快照管理。该模块适合本地/实验室场景，用于在真正修改 qcow2/raw 镜像之前验证参数与目标路径。

## 主要参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `src` | 源镜像路径 | `/var/lib/libvirt/images/base.qcow2` |
| `dest` | 目标镜像路径 | `/var/lib/libvirt/images/app01.qcow2` |
| `backing_file` | 可选的基线镜像 | `/var/lib/libvirt/images/base.qcow2` |
| `size` | 创建/扩容大小 | `20G` |
| `format` | 目标格式 | `qcow2`/`raw` |
| `state` | `present` / `absent` / `info` | `present` |
| `force` | 是否覆盖已有文件 | `false` |

## 返回值
| 字段 | 说明 |
|------|------|
| `cmd` | 计划执行的 `qemu-img` 命令 |
| `stdout` | `--check` 模式下的输出 |
| `changed` | Dry Run 是否会导致镜像被创建/更新 |

## 使用情境
1. **镜像模板克隆**：快速复制 `base.qcow2` 并预演后续 cloud-init/virt-install 步骤。
2. **格式转换**：在将镜像导入 VMware/Azure 前，先 Dry Run `qcow2 -> vmdk/vhd` 转换命令。
3. **容量审计**：结合 `storage/` 章节的 loopback/LVM 演练，评估磁盘空间需求。

## 安全注意事项
1. **磁盘路径提示**：变量文件中包含“请勿将生产路径写入示例”的中文警告，并建议在 `/tmp` 或 `~/images` 目录练习；若必须保存真实路径，请将变量文件使用 Ansible Vault 加密。
2. **检查模式**：Playbook 默认 `check_mode: true`，即便误操作也不会真正修改镜像；正式操作请在备份后移除该参数。
3. **权限控制**：执行用户应具备对镜像目录的写权限；在共享环境中请使用专用实验账户。
4. **日志脱敏**：虽然镜像命令少涉及密钥，仍建议避免输出真实路径/文件名，可通过变量控制。

## 依赖与认证
```bash
ansible-galaxy collection install community.general
sudo apt/yum install -y qemu-img qemu-utils
```
- 确保宿主机磁盘空间充足，并提前创建用于练习的目录。

## 模拟运行步骤
1. `cd virtualization/qemu_img`。
2. 根据 `vars/example_vars.yml` 的警示修改源/目标路径、大小与格式。
3. 执行：
   ```bash
   ansible-playbook playbook.yml --syntax-check
   ansible-playbook playbook.yml --check
   ```
4. 观察 `debug` 输出的命令计划，确认无误后再去除 `check_mode` 并在安全环境中执行。

## 参考资料
- [community.general.qemu_img 模块](https://docs.ansible.com/ansible/latest/collections/community/general/qemu_img_module.html)
- [virtualization/README.md](../README.md)
