# Ansible 中文实践指南

本仓库收录了面向中文读者的 Ansible 示例与知识卡片，帮助你在日常运维和自动化项目中迅速定位所需特性。所有示例均可直接运行或作为模板套用到现有 Playbook 中。

## 仓库结构
- `advanced/`：高级特性讲解与示例 Playbook。
- `monitoring/`：主流监控系统的 Ansible 集成示例。
- `storage/`：磁盘、LVM 与文件系统管理的演练场景。
- `metadata/modules.yaml`：用于索引特性与文档的元数据。
- `tests/`：确保示例结构完整的 pytest 测试。

## 进阶章节
- [高级特性总览](advanced/README.md)
- [监控模块总览](monitoring/README.md)
- [存储模块实践指南](storage/README.md)

## 如何学习
按照"阅读文档 → 运行示例 → 修改变量 → 扩展任务"的顺序进行练习。建议先通读对应 README，结合注释理解变量含义，再亲自运行 Playbook 并在失败时参考"如何调试/常见错误"章节。完成基础练习后，可以尝试把同一台主机的需求拆分进多个特性目录中的示例，或根据业务自定义更多 handler、loop 与 include 组合，以加深理解。

## 注意事项
- **存储示例严禁直接在生产环境运行**：`storage/` 下的 playbook 默认通过 loopback 设备和 `--check` 模式演练，请先阅读 [storage/README.md](storage/README.md) 并在沙箱环境验证。
- **强制 Dry-Run**：执行任何存储任务前务必加上 `ansible-playbook --check`，必要时结合 `changed_when: false`/`failed_when: false`，确认计划后再放行。
- **备份优先**：在尝试 mount/LVM/filesystem 实操前，先备份 fstab、VG metadata 以及关键数据，确保可以在出错时回滚。

## 监控模块使用提示

### API 管理最佳实践
- **凭证安全**：使用 Ansible Vault 加密所有 API Key 和密码
- **权限最小化**：为不同监控平台创建专用的 API 用户，限制权限范围
- **定期轮换**：建立定期更新访问凭证的流程
- **环境隔离**：为不同环境（生产、测试、开发）使用独立的 API 凭证

### 安全注意事项
- 不要在代码中硬编码真实密码或 API Key
- 使用 `no_log: true` 保护敏感变量不被记录到日志
- 在运行前使用 `--check` 模式验证配置变更
- 限制 API 访问的源 IP 地址和网络范围

### 相关链接
- [Nagios 监控集成](monitoring/nagios/README.md) - 传统开源监控
- [Datadog 云监控](monitoring/datadog/README.md) - 云原生监控平台  
- [Zabbix 企业监控](monitoring/zabbix/README.md) - 企业级监控解决方案