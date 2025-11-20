# port 模块使用指南

## 模块用途
`ansible.builtin.wait_for` 模块用于端口健康探测，通过检查目标主机端口的可用性来验证服务状态。此模块特别适用于集群部署、滚动更新、依赖链路中确保服务可用性等场景。相比直接连接测试，wait_for 提供了重试、超时、延迟等灵活控制机制，并支持通过 `delegate_to: localhost` 从控制节点进行远程检查，避免实际连接到目标服务。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `port` | int | 要检查的端口号 | 80、443、3306、5432、8080 等 |
| `host` | str | 目标主机地址（默认 localhost） | IP 地址、域名、FQDN 等 |
| `timeout` | int | 最大等待时间（秒，默认 300） | 10、30、60、120 等 |
| `delay` | int | 开始检查前的延迟时间（秒，默认 0） | 5、10、30 等 |
| `sleep` | int | 检查间隔时间（秒，默认 1） | 1、5、10 等 |
| `state` | str | 期望的端口状态 | started（开放）、stopped（关闭） |
| `connect_timeout` | int | 单次连接超时时间（秒） | 3、5、10 等 |
| `active_connection_states` | list | 认定为活跃的连接状态 | ["ESTABLISHED", "FIN_WAIT1"] 等 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `elapsed` | 等待花费的秒数 | 15.234 |
| `state` | 最终检测到的状态 | started、stopped、drained |
| `failed` | 检查是否失败 | true、false |

## 常见字段说明

### 端口状态类型
- **started**：端口已开放并可连接（服务已启动）
- **stopped**：端口已关闭（服务已停止）
- **drained**：端口仍在开放但没有活跃连接

### 连接控制参数
- **timeout**：总体等待时间上限，防止单次检查时间过长
- **delay**：给服务预留启动时间，避免过早检查导致失败
- **sleep**：控制检查频率，避免过于频繁的连接尝试
- **connect_timeout**：单次连接尝试的超时时间

## 使用情境

### 服务启动验证
**场景**：应用部署后验证服务是否真正可用
- 部署应用 → 启动服务 → wait_for 验证端口 → 继续后续任务

### 滚动更新协调
**场景**：分批次更新服务，确保每批次完成后再继续
- 更新第一批 → wait_for 验证 → 更新第二批 → wait_for 验证

### 多服务依赖管理
**场景**：有依赖关系的服务启动顺序控制
- 启动数据库 → wait_for 验证 → 启动应用 → wait_for 验证

### 远程主机健康检查
**场景**：从控制节点检查远程服务状态
- 使用 `delegate_to: localhost` 从本地检查远程服务可用性

### 批量端口监控
**场景**：同时检查多个关键服务端口
- 使用 loop 批量检查端口列表，提高效率

## 适用场景

### 服务启动验证
**场景**：应用部署后验证服务是否真正可用
- 部署应用 → 启动服务 → wait_for 验证端口 → 继续后续任务

### 滚动更新协调
**场景**：分批次更新服务，确保每批次完成后再继续
- 更新第一批 → wait_for 验证 → 更新第二批 → wait_for 验证

### 多服务依赖管理
**场景**：有依赖关系的服务启动顺序控制
- 启动数据库 → wait_for 验证 → 启动应用 → wait_for 验证

### 远程主机健康检查
**场景**：从控制节点检查远程服务状态
- 使用 `delegate_to: localhost` 从本地检查远程服务可用性

## 安全注意事项

1. **使用 delegate_to: localhost**：从控制节点检查远程服务，避免在目标主机上执行不必要的连接
2. **check_mode 预览**：在 `--check` 模式下验证配置逻辑，避免实际连接尝试
3. **合理超时设置**：根据服务启动特性设置合适的 timeout，避免假失败或等待过久
4. **网络隔离**：在受限网络环境中，确保控制节点能够访问目标端口
5. **连接频率控制**：适当设置 sleep 参数，避免对目标服务造成连接压力
6. **敏感信息保护**：使用 `no_log: true` 保护端口检查过程中的敏感信息
7. **错误处理**：结合 `ignore_errors` 和 `failed_when` 灵活处理检查失败

## 最佳实践

### 1. 分层检查策略
```yaml
# 基础端口检查（快速验证）
- name: 等待基础端口开放
  ansible.builtin.wait_for:
    host: "{{ target_host }}"
    port: 80
    timeout: 10
  delegate_to: localhost

# 应用就绪检查（包含启动延迟）
- name: 等待应用完全就绪
  ansible.builtin.wait_for:
    host: "{{ target_host }}"
    port: 8080
    delay: 5
    timeout: 60
    sleep: 5
  delegate_to: localhost
```

### 2. 批量端口检查
```yaml
# 使用循环检查多个端口
- name: 批量检查服务端口
  ansible.builtin.wait_for:
    host: "{{ item.host }}"
    port: "{{ item.port }}"
    timeout: "{{ item.timeout | default(30) }}"
  loop: "{{ port_check_list }}"
  delegate_to: localhost
  no_log: true
```

### 3. 条件性端口检查
```yaml
# 根据环境变量决定是否检查
- name: 生产环境服务验证
  ansible.builtin.wait_for:
    host: "{{ app_host }}"
    port: "{{ app_port }}"
    timeout: 120
  delegate_to: localhost
  when: 
    - ansible_environment == "production"
    - enable_service_check | bool
  check_mode: "{{ ansible_check_mode }}"
```

## 测试步骤

### 1. 基础功能测试
```bash
# 检查本地端口
ansible-playbook network/port/playbook.yml --check

# 检查远程端口（需要配置 inventory）
ansible-playbook network/port/playbook.yml -i inventory.ini --check
```

### 2. 超时机制测试
```bash
# 测试连接超时（访问不存在的端口）
ansible-playbook network/port/playbook.yml -e "port_check_timeout=5" --check
```

### 3. 批量检查测试
```bash
# 测试多端口批量检查
ansible-playbook network/port/playbook.yml -e "enable_batch_check=true" --check
```

## 常见问题

### wait_for 超时失败怎么办？
1. 检查目标服务是否真正启动
2. 验证网络连通性（防火墙、安全组）
3. 调整 timeout 和 delay 参数
4. 使用 `delegate_to: localhost` 从控制节点检查

### 如何避免对生产服务造成影响？
1. 使用合理的 sleep 参数控制检查频率
2. 设置适当的 connect_timeout 避免长时间占用连接
3. 在测试环境验证参数设置
4. 使用 check_mode 预览配置逻辑

### 批量检查时如何优化性能？
1. 使用 async 进行并行检查
2. 设置合理的超时时间
3. 按服务重要性分组检查
4. 使用条件判断跳过不必要的检查

## 依赖说明

### 必需依赖
- **Ansible builtin 模块**：`ansible.builtin.wait_for`（内置，无需额外安装）

### 系统要求
- **控制节点**：能够访问目标主机的指定端口
- **网络环境**：控制节点到目标主机的网络连通性
- **Python 环境**：Ansible 运行所需的 Python 环境

### 可选依赖
- **网络工具**：telnet、nc、nmap 等用于手动验证端口状态
- **监控工具**：用于集成端口检查结果的监控系统

## 相关示例

### 基础端口检查示例
```yaml
- name: 检查 Web 服务端口
  ansible.builtin.wait_for:
    host: "{{ web_server_ip }}"
    port: 80
    state: started
    timeout: 30
  delegate_to: localhost
  register: web_port_status
  no_log: true
```

### 服务启动后验证示例
```yaml
- name: 启动应用服务
  ansible.builtin.systemd:
    name: myapp
    state: started

- name: 等待应用服务就绪
  ansible.builtin.wait_for:
    host: "{{ inventory_hostname }}"
    port: 8080
    delay: 10
    timeout: 120
    sleep: 5
  delegate_to: localhost
  register: app_ready
```

### 批量端口监控示例
```yaml
- name: 批量检查关键服务端口
  ansible.builtin.wait_for:
    host: "{{ item.host }}"
    port: "{{ item.port }}"
    timeout: "{{ item.timeout | default(30) }}"
    state: "{{ item.state | default('started') }}"
  loop: "{{ critical_ports }}"
  delegate_to: localhost
  loop_control:
    label: "{{ item.host }}:{{ item.port }}"
  no_log: true
```