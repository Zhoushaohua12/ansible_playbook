# Stage 4 模块覆盖对比

- 生成时间: 2025-11-21T01:43:59.885579+00:00
- 待补充模块总数: 5
- 数据来源: metadata/ansible_doc_diff.json

## 文件操作模块实践指南 (`files`)

| 模块 | 优先级 | 前置实践 | 官方文档 | 备注 |
| --- | --- | --- | --- | --- |
| `assemble` | high | copy, template | [link](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/assemble_module.html) | 将碎片化配置组装成完整文件，可接在 copy/template 之后演示差异化发布。 |
| `xattr` | medium | file | [link](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/xattr_module.html) | 补充 ACL/SELinux/自定义元数据场景，延伸 file 模块章节。 |

## 监控模块 (`monitoring`)

| 模块 | 优先级 | 前置实践 | 官方文档 | 备注 |
| --- | --- | --- | --- | --- |
| `grafana_dashboard` | high | prometheus_monitoring, datadog_monitoring | [link](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_dashboard_module.html) | 完善监控章节，加入 dashboard 自动化与告警学习路径。 |

## 网络模块实践指南 (`network`)

| 模块 | 优先级 | 前置实践 | 官方文档 | 备注 |
| --- | --- | --- | --- | --- |
| `ethtool` | medium | interface, nmcli | [link](https://docs.ansible.com/ansible/latest/collections/community/general/ethtool_module.html) | 结合 interface/nmcli 示例演示链路调优、速率与双工配置。 |

## 系统管理模块指南 (`system`)

| 模块 | 优先级 | 前置实践 | 官方文档 | 备注 |
| --- | --- | --- | --- | --- |
| `mount` | low | storage_mount | [link](https://docs.ansible.com/ansible/latest/collections/ansible/posix/mount_module.html) | 结合 storage/mount 的 loopback 练习，展示 system 章节如何自检挂载状态。 |
