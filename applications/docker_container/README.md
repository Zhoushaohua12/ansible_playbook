# docker_container 模块使用指南

## 模块简介
`community.docker.docker_container` 模块用于管理 Docker 容器的生命周期，包括创建、启动、停止、删除等操作。该模块提供了完整的容器管理功能，支持容器配置、网络设置、卷挂载等高级特性。

## 主要参数

### 基础配置
- `name`：容器名称，必须唯一
- `image`：Docker 镜像名称和标签（如 `nginx:1.21`）
- `state`：容器状态，可选值：
  - `present`：确保容器存在（默认）
  - `started`：确保容器启动并运行
  - `stopped`：确保容器停止
  - `absent`：删除容器
  - `restarted`：重启容器

### 重启策略
- `restart_policy`：重启策略，可选值：
  - `no`：不重启（默认）
  - `on-failure`：失败时重启
  - `always`：总是重启
  - `unless-stopped`：除非手动停止，否则总是重启
- `restart_retries`：重启尝试次数（默认：0）

### 网络配置
- `ports`：端口映射，格式为 `["主机端口:容器端口"]`
- `networks`：连接的网络列表
- `network_mode`：网络模式（如 `bridge`、`host`）

### 存储配置
- `volumes`：卷挂载，格式为 `["主机路径:容器路径:权限"]`
- `tmpfs`：临时文件系统挂载

### 环境和资源
- `env`：环境变量字典
- `command`：容器启动命令
- `user`：容器运行用户
- `memory_limit`：内存限制
- `cpus`：CPU 限制

## 返回值
- `container`：容器详细信息对象
- `changed`：是否执行了变更操作
- `msg`：操作结果描述信息
- `actions_executed`：执行的具体操作列表

## 常见使用场景

### 1. Web 服务部署
```yaml
- name: 部署 Nginx Web 服务器
  community.docker.docker_container:
    name: web_server
    image: nginx:1.21-alpine
    state: started
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/etc/nginx/conf.d:/etc/nginx/conf.d:ro"
      - "/var/www/html:/usr/share/nginx/html:ro"
    restart_policy: unless-stopped
```

### 2. 数据库服务
```yaml
- name: 部署 PostgreSQL 数据库
  community.docker.docker_container:
    name: postgres_db
    image: postgres:13
    state: started
    env:
      POSTGRES_DB: myapp
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: "{{ db_password }}"
    volumes:
      - "postgres_data:/var/lib/postgresql/data"
    restart_policy: unless-stopped
```

### 3. 持续部署场景
```yaml
- name: 部署应用容器（支持版本回滚）
  community.docker.docker_container:
    name: "{{ app_name }}"
    image: "{{ app_image }}:{{ app_version }}"
    state: started
    env:
      APP_ENV: "{{ deploy_env }}"
      DATABASE_URL: "{{ database_url }}"
    ports:
      - "{{ app_port }}:3000"
    restart_policy: unless-stopped
  register: container_result

- name: 等待容器启动完成
  wait_for:
    port: "{{ app_port }}"
    delay: 10
    timeout: 60
```

### 4. 镜像发布管理
```yaml
- name: 拉取最新镜像并重新部署
  community.docker.docker_container:
    name: "{{ app_name }}"
    image: "{{ registry_url }}/{{ app_image }}:{{ version_tag }}"
    state: restarted
    pull: true
    restart_policy: unless-stopped
```

## 安全注意事项

### 镜像安全
- 使用官方镜像或可信的第三方镜像
- 固定镜像版本标签，避免使用 `latest`
- 定期更新镜像以获取安全补丁

### 权限控制
- 避免使用 `--privileged` 特权模式
- 使用非 root 用户运行容器
- 限制容器的系统调用能力

### 网络安全
- 仅暴露必要的端口
- 使用防火墙规则限制访问
- 配置容器网络隔离

### 数据安全
- 使用数据卷持久化重要数据
- 定期备份容器数据
- 加密敏感的环境变量

## 最佳实践

### 版本管理
- 使用语义化版本标签
- 实施蓝绿部署策略
- 配置健康检查和自动回滚

### 资源管理
- 设置合理的内存和 CPU 限制
- 监控容器资源使用情况
- 配置日志轮转和清理策略

### 监控集成
- 配置容器健康检查
- 集成监控和告警系统
- 实施日志聚合和分析

## 测试步骤
1. 确保 Docker 服务已安装并运行
2. 在 `vars/example_vars.yml` 中配置容器参数
3. 使用 `--check` 模式预览容器变更
4. 验证容器状态和网络连通性
5. 检查应用日志和健康状态

## 常见问题
- **容器无法启动**：检查镜像是否存在、端口是否冲突
- **网络连接问题**：确认端口映射和网络配置正确
- **权限问题**：检查 Docker socket 权限和容器用户配置
- **资源不足**：调整内存和 CPU 限制设置

## 相关模块
- [docker_image](https://docs.ansible.com/ansible/latest/collections/community/docker/docker_image_module.html) - Docker 镜像管理
- [docker_network](https://docs.ansible.com/ansible/latest/collections/community/docker/docker_network_module.html) - Docker 网络管理
- [docker_volume](https://docs.ansible.com/ansible/latest/collections/community/docker/docker_volume_module.html) - Docker 卷管理
