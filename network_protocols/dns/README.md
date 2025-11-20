# DNS 模块实践指南

## 模块用途

`community.general.dig` 模块用于执行 DNS 查询，支持查询 A、AAAA、CNAME、MX、NS、TXT 等 DNS 记录类型。该模块常用于：
- DNS 解析验证与诊断
- 确认 CDN 或负载均衡配置
- 域名可用性检查
- DNS 记录一致性验证
- 与 DNS 管理系统的集成

## 主要参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | 要查询的域名 |
| `rdtype` | 否 | DNS 记录类型（A、AAAA、CNAME、MX、NS、TXT 等，默认 A） |
| `nameserver` | 否 | 指定 DNS 服务器地址（不指定则使用系统配置） |
| `query_type` | 否 | 查询类型（通常为 IN 互联网类） |
| `timeout` | 否 | 查询超时时间（秒，默认 5） |

## 返回值

| 字段 | 说明 |
|------|------|
| `result` | 查询结果列表 |
| `nameserver` | 使用的 DNS 服务器 |
| `query` | 原始查询信息 |

## 使用情境

### 场景 1：验证 DNS 记录配置

在部署前验证 DNS 记录是否正确配置：

```yaml
- name: 查询 DNS A 记录
  community.general.dig:
    name: "example.com"
    rdtype: A
  register: dns_result

- name: 验证 DNS 记录
  fail:
    msg: "DNS 配置错误，期望 IP 为 10.0.0.1，实际为 {{ dns_result.result[0] }}"
  when: dns_result.result[0] != '10.0.0.1'
```

### 场景 2：多地区 DNS 解析验证

验证不同地区或 DNS 服务器的 DNS 解析结果是否一致：

```yaml
- name: 查询公共 DNS 服务器（Google）
  community.general.dig:
    name: "cdn.example.com"
    rdtype: A
    nameserver: "8.8.8.8"
  register: google_dns

- name: 查询公共 DNS 服务器（Cloudflare）
  community.general.dig:
    name: "cdn.example.com"
    rdtype: A
    nameserver: "1.1.1.1"
  register: cloudflare_dns

- name: 比较 DNS 结果
  debug:
    msg: |
      Google DNS: {{ google_dns.result }}
      Cloudflare DNS: {{ cloudflare_dns.result }}
      一致性检查：{{ google_dns.result == cloudflare_dns.result }}
```

### 场景 3：记录类型查询

查询不同类型的 DNS 记录：

```yaml
- name: 查询 MX 记录（邮件服务）
  community.general.dig:
    name: "example.com"
    rdtype: MX
  register: mx_records

- name: 查询 CNAME 记录（别名）
  community.general.dig:
    name: "www.example.com"
    rdtype: CNAME
  register: cname_record

- name: 显示查询结果
  debug:
    msg: |
      MX 记录：{{ mx_records.result }}
      CNAME 记录：{{ cname_record.result }}
```

## 安全注意事项

1. **DNS 服务器验证**：
   - 仅查询可信的 DNS 服务器，避免 DNS 中毒
   - 使用可靠的公共 DNS 服务器（Google 8.8.8.8、Cloudflare 1.1.1.1）
   - 在企业环境中使用内网 DNS 服务器

2. **隐私与安全**：
   - DNS 查询通常以明文发送，可能被拦截或监控
   - 在隐私敏感的环境中考虑使用 DNS-over-HTTPS 或 DNS-over-TLS
   - 避免查询包含敏感业务信息的域名

3. **超时控制**：
   - 设置合理的 `timeout` 值，避免长时间阻塞
   - 对网络不稳定的环境增加重试机制
   - 监控查询耗时，识别 DNS 性能问题

4. **TSIG 认证**（如使用 nsupdate）：
   - DNS 区域更新需要 TSIG 密钥认证
   - 密钥应使用 Ansible Vault 加密存储
   - 限制密钥的访问权限，定期轮换

5. **Check Mode（干运行）**：
   - 在执行 DNS 更新前使用 `check_mode: true` 预览变更
   - 验证变更内容无误后再执行正式操作
   - 保留 DNS 变更日志，便于事后审计

## 相关链接

- [community.general.dig 模块](https://docs.ansible.com/ansible/latest/collections/community/general/dig_module.html)
- [DNS 记录类型参考](https://en.wikipedia.org/wiki/List_of_DNS_record_types)
- [RFC 1035 - 域名服务](https://tools.ietf.org/html/rfc1035)
- [TSIG - DNS 认证机制](https://tools.ietf.org/html/rfc2845)
