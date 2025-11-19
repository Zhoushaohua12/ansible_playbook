# libvirt_domain 模块演练指南

## 模块用途
`virtualization/libvirt_domain` 目录使用 `community.libvirt.libvirt_domain` 模块（亦可切换为 `community.libvirt.virt`）在 `check_mode: true` 下定义 KVM 虚拟机的 XML、计算/内存、网络及磁盘。示例强调如何在本地实验室或边缘节点验证虚拟机模板，避免误写入宿主机。

## 主要参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `uri` | libvirt 连接 URI | `qemu:///system` |
| `xml` | 完整 Domain XML 字符串/模板 | 存放于变量 `libvirt_domain_xml` |
| `state` | `present`/`running`/`defined` | `present` |
| `autostart` | 是否开机自启 | `true` |
| `metadata` | 自定义标签（用于 CMDB） | `{env: lab, owner: sre}` |
| `memory` / `vcpus` | 计算规格（若未在 XML 中定义） | `4096`, `2` |

## 返回值
| 字段 | 说明 |
|------|------|
| `domain.name` | 虚拟机名称 |
| `domain.state` | Dry Run 预期状态 |
| `domain.uuid` | 虚拟机 UUID（若已存在） |
| `changed` | 是否会创建/更新定义 |

## 使用情境
1. **本地实验室模板**：使用 Jinja2 渲染 XML，预演 CPU/NUMA/磁盘布局，与 `storage/` 的 loopback 示例联动。
2. **边缘节点批量部署**：在 GitOps 中预先验证跨节点的 vCPU/memory 配置一致性。
3. **混合云桥接**：与 `cloud/aws_ec2` 等模块对照，确保模板与云上规格映射一致。

## 安全注意事项
1. `vars/example_vars.yml` 中的 `libvirt_domain_xml` 仅放置示例 XML；若包含敏感信息（如嵌入 cloud-init 密码），必须使用 Vault。
2. 建议以非 root 用户 + `libvirt` 组执行，避免 Playbook 在默认 URI 下具备删除能力。
3. Playbook 采用 `check_mode: true`，真实部署前请在隔离宿主机中移除该参数并再次复核。
4. 连接远程 libvirt 时请结合 SSH 密钥或 SASL 认证，不要在变量中写明明文密码。

## 依赖与认证
```bash
ansible-galaxy collection install community.libvirt
sudo apt/yum install -y libvirt-daemon qemu-kvm virt-install
pip install libvirt-python lxml
```
- 若需要远程连接，请在 `vars` 中提供 `libvirt_uri: qemu+ssh://user@host/system`，并使用 SSH Agent/密钥。

## 模拟运行步骤
1. `cd virtualization/libvirt_domain`。
2. 根据注释修改 `vars/example_vars.yml`，覆盖 URI、XML、标签等字段。
3. 运行：
   ```bash
   ansible-playbook playbook.yml --syntax-check
   ansible-playbook playbook.yml --check
   ```
4. 检查 `debug` 输出的摘要，确认 CPU/内存/磁盘与预期一致后再放行。

## 参考资料
- [community.libvirt.libvirt_domain 模块](https://docs.ansible.com/ansible/latest/collections/community/libvirt/libvirt_domain_module.html)
- [virtualization/README.md](../README.md)
