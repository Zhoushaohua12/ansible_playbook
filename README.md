# Ansible 中文实践指南

本仓库收录了面向中文读者的 Ansible 示例与知识卡片，帮助你在日常运维和自动化项目中迅速定位所需特性。所有示例均可直接运行或作为模板套用到现有 Playbook 中。

## 仓库结构
- `advanced/`：高级特性讲解与示例 Playbook。
- `monitoring/`：主流监控系统的 Ansible 集成示例。
- `storage/`：磁盘、LVM 与文件系统管理的演练场景。
- `web/`：Web 服务器（Nginx、Apache）配置与管理示例。
- `metadata/modules.yaml`：用于索引特性与文档的元数据。
- `tests/`：确保示例结构完整的 pytest 测试。

## 进阶章节
- [高级特性总览](advanced/README.md)
- [监控模块总览](monitoring/README.md)
- [存储模块实践指南](storage/README.md)
- [Web 服务管理指南](web/README.md)

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

## Web 服务章节

### 服务概览
`web/` 目录提供 Nginx、Apache 以及通用 Web 配置的自动化管理示例，涵盖以下场景：
- **反向代理**：将外部请求代理到内网应用服务器（Django、Flask、Node.js 等）
- **静态站点发布**：部署 HTML/CSS/JS 静态资源
- **SSL/TLS 配置**：自动化管理 HTTPS 证书和安全加固
- **负载均衡**：配置多后端服务器的流量分发策略
- **虚拟主机管理**：多域名站点托管

### 模板说明
每个 Web 服务模块都包含完整的配置模板（`.j2` 文件），所有模板均包含中文注释说明关键配置项：
- **Nginx 模板**：`web/nginx/templates/` 包含主配置文件和虚拟主机模板
- **Apache 模板**：`web/apache2/templates/` 包含虚拟主机和安全配置模板
- **通用模板**：`web/web_config/templates/` 包含跨服务器的反向代理和静态站点模板

所有模板支持变量替换，可根据实际需求调整参数（域名、端口、路径、SSL 配置等）。

### 教学声明
⚠️ **重要提示**：本目录下的所有示例主要用于教学和学习目的，在生产环境使用前需要：
1. **安全加固**：根据实际需求调整安全配置（如禁用不必要的模块、配置 WAF、限流保护）
2. **性能调优**：根据服务器硬件资源调整并发参数、缓冲区大小、超时时间
3. **测试验证**：在预发布环境进行压力测试，验证配置正确性和性能表现
4. **监控告警**：建立完善的监控体系（结合 `monitoring/` 目录示例），及时发现异常
5. **备份恢复**：建立配置文件和证书的备份机制，确保可快速恢复

建议先在测试环境运行示例，理解每个配置项的作用后，再根据生产需求定制化。

### 与 system/applications 的配合
Web 服务层通常与应用层配合使用：
- **应用部署**：`system/applications/` 负责安装和启动应用（如 Django、Node.js）
- **Web 层代理**：`web/` 负责配置反向代理，将外部请求转发到应用端口
- **健康检查**：结合 `monitoring/` 监控应用和 Web 服务健康状态

典型工作流：先部署应用 → 配置 Web 服务 → 启用 HTTPS → 配置监控告警

### 快速开始
```bash
# 1. 语法检查
ansible-playbook web/nginx/playbook.yml --syntax-check

# 2. Dry-Run 预览变更
ansible-playbook web/nginx/playbook.yml -i hosts.ini --check

# 3. 执行部署
ansible-playbook web/nginx/playbook.yml -i hosts.ini

# 4. 验证服务状态
curl -I http://your-domain.com
```

### 相关链接
- [Nginx 配置管理](web/nginx/README.md) - 高性能 HTTP 服务器和反向代理
- [Apache2 配置管理](web/apache2/README.md) - 传统开源 Web 服务器
- [通用 Web 配置](web/web_config/README.md) - 跨服务器的通用配置场景