# URI 模块实践指南

## 模块用途

`ansible.builtin.uri` 模块用于执行 HTTP/HTTPS 请求，支持 GET、POST、PUT、DELETE 等多种 HTTP 方法。该模块常用于：
- REST API 测试与调用
- HTTP 健康检查
- 获取远程文件或配置
- 与微服务、Kubernetes API、云平台 API 集成
- 应用层服务可用性验证

## 主要参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `url` | 是 | 目标 HTTP/HTTPS URL |
| `method` | 否 | HTTP 方法（GET、POST、PUT、DELETE 等，默认 GET） |
| `body` | 否 | 请求体（POST/PUT 请求时使用，可为 JSON/XML） |
| `headers` | 否 | 自定义请求头（字典格式） |
| `user` / `password` | 否 | HTTP 基础认证用户名和密码 |
| `force_basic_auth` | 否 | 是否强制使用基础认证（默认 false） |
| `validate_certs` | 否 | 是否验证 SSL 证书（默认 true，**生产环境必须启用**） |
| `status_code` | 否 | 期望的 HTTP 状态码（默认 200） |
| `timeout` | 否 | 请求超时时间（秒） |

## 返回值

| 字段 | 说明 |
|------|------|
| `status` | HTTP 状态码 |
| `url` | 最终请求 URL |
| `body` | 响应体内容 |
| `headers` | 响应头字典 |
| `elapsed` | 请求耗时（秒） |

## 使用情境

### 场景 1：REST API 健康检查

验证 API 服务的可用性和响应状态：

```yaml
- name: 检查 Kubernetes API 健康状态
  ansible.builtin.uri:
    url: "https://{{ kubernetes_api_host }}:6443/healthz"
    method: GET
    validate_certs: true
    timeout: 10
  register: k8s_health
  failed_when: k8s_health.status != 200
```

### 场景 2：POST 请求与数据提交

向 API 提交数据并处理响应：

```yaml
- name: 提交日志到远程服务
  ansible.builtin.uri:
    url: "https://logs.example.com/api/logs"
    method: POST
    headers:
      Authorization: "Bearer {{ api_token }}"
      Content-Type: "application/json"
    body_format: json
    body:
      message: "deployment started"
      level: info
    validate_certs: true
    no_log: true  # 隐藏 token
  register: log_response
```

### 场景 3：条件化请求与错误处理

根据响应内容进行后续决策：

```yaml
- name: 查询服务状态
  ansible.builtin.uri:
    url: "https://api.example.com/status"
    method: GET
    validate_certs: true
  register: status_check
  
- name: 仅在服务就绪时继续
  debug:
    msg: "服务已就绪"
  when: status_check.json.state == 'ready'
```

## 安全注意事项

1. **SSL/TLS 验证**：
   - 必须使用 `validate_certs: true`，禁止跳过证书验证
   - 仅在测试环境或自签名证书下临时使用 `validate_certs: false`
   - 生产环境应使用受信任的 CA 证书

2. **认证信息保护**：
   - 所有包含 Token、密钥、密码的请求必须使用 `no_log: true`
   - 使用 Ansible Vault 存储 API Token，避免在 playbook 中明文显示
   - 在请求头中传递认证信息时特别注意 `no_log: true`

3. **HTTP 状态码验证**：
   - 使用 `status_code` 参数验证期望的响应状态
   - 明确定义哪些状态码表示成功，哪些表示失败
   - 处理重定向（3xx）和客户端错误（4xx）

4. **超时与重试**：
   - 设置合理的 `timeout` 值，避免长时间阻塞
   - 对不稳定的 API 使用重试机制（`retries`、`delay`）
   - 监控请求耗时，识别性能问题

5. **请求头定制**：
   - 避免在 User-Agent 中暴露系统信息
   - 使用标准的 HTTP 请求头，避免自定义非标准头
   - 在提交表单数据时使用适当的 Content-Type

## 相关链接

- [Ansible uri 模块官方文档](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/uri_module.html)
- [HTTP 状态码参考](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status)
- [Ansible Vault 加密变量](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
- [REST API 最佳实践](https://restfulapi.net/)
