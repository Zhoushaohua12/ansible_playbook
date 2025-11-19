# docker_image 模块使用指南

## 模块简介
`community.docker.docker_image` 模块用于管理 Docker 镜像的拉取、构建、推送和删除等操作。该模块提供了完整的镜像生命周期管理功能，支持镜像构建、标签管理、仓库推送等高级特性，是容器化部署和 CI/CD 流水线的核心组件。

## 主要参数

### 基础配置
- `name`：镜像名称（如 `nginx:latest`、`registry.example.com/myapp:v1.0`）
- `state`：镜像状态，可选值：
  - `present`：确保镜像存在（默认）
  - `absent`：删除镜像
  - `build`：构建镜像
  - `push`：推送镜像到仓库

### 构建选项
- `build.path`：构建上下文路径
- `build.dockerfile`：Dockerfile 路径（默认：`Dockerfile`）
- `build.args`：构建参数字典
- `build.pull`：构建时是否拉取基础镜像（默认：true）
- `build.cache_from`：缓存源镜像列表

### 推送选项
- `push`：推送配置字典
  - `push`：是否推送（默认：true）

### 高级选项
- `source`：镜像来源，可选值：
  - `pull`：从仓库拉取（默认）
  - `build`：本地构建
  - `load`：从文件加载
  - `local`：本地导入
- `repository`：镜像仓库地址
- `tag`：镜像标签
- `force_source`：是否强制使用指定源

## 返回值
- `image`：镜像详细信息对象
- `changed`：是否执行了变更操作
- `msg`：操作结果描述信息
- `actions_executed`：执行的具体操作列表
- `status`：镜像状态信息

## 常见使用场景

### 1. 拉取公共镜像
```yaml
- name: 拉取 Nginx 镜像
  community.docker.docker_image:
    name: nginx:1.21-alpine
    state: present
    source: pull
```

### 2. 构建自定义镜像
```yaml
- name: 构建 Web 应用镜像
  community.docker.docker_image:
    name: myapp:{{ app_version }}
    state: build
    build:
      path: "{{ app_source_path }}"
      dockerfile: Dockerfile
      args:
        APP_VERSION: "{{ app_version }}"
        BUILD_ENV: "{{ build_env }}"
      pull: true
```

### 3. 推送镜像到私有仓库
```yaml
- name: 推送镜像到私有仓库
  community.docker.docker_image:
    name: "{{ registry_url }}/myapp:{{ app_version }}"
    state: push
    push: true
```

### 4. 镜像标签管理
```yaml
- name: 为镜像添加多个标签
  community.docker.docker_image:
    name: myapp:{{ app_version }}
    repository: "{{ registry_url }}/myapp"
    tag: "{{ item }}"
    state: present
  loop:
    - "{{ app_version }}"
    - "latest"
    - "stable"
```

### 5. 批量拉取基础镜像
```yaml
- name: 拉取所需的基础镜像
  community.docker.docker_image:
    name: "{{ item }}"
    state: present
    source: pull
  loop:
    - "python:3.11-alpine"
    - "node:18-alpine"
    - "redis:7-alpine"
    - "postgres:15-alpine"
```

### 6. 清理旧镜像
```yaml
- name: 删除旧版本镜像
  community.docker.docker_image:
    name: "{{ registry_url }}/myapp:{{ item }}"
    state: absent
  loop: "{{ old_versions }}"
```

### 7. 多阶段构建
```yaml
- name: 构建生产环境镜像（多阶段构建）
  community.docker.docker_image:
    name: myapp:{{ app_version }}-prod
    state: build
    build:
      path: "{{ app_source_path }}"
      dockerfile: Dockerfile.prod
      args:
        NODE_ENV: production
        BUILD_NUMBER: "{{ build_number }}"
      cache_from:
        - myapp:latest
        - node:18-alpine
```

## 安全注意事项

### 镜像安全
- 使用官方镜像或可信的基础镜像
- 定期更新基础镜像获取安全补丁
- 扫描镜像安全漏洞
- 使用镜像签名验证完整性

### 构建安全
- 避免在 Dockerfile 中包含敏感信息
- 使用多阶段构建减少最终镜像大小
- 使用非 root 用户运行应用
- 最小化镜像层数和攻击面

### 仓库安全
- 使用 HTTPS 连接镜像仓库
- 配置仓库访问认证
- 使用私有镜像仓库隔离
- 实施镜像访问权限控制

## 最佳实践

### 版本管理
- 使用语义化版本标签
- 避免 `latest` 标签在生产环境
- 实施镜像版本锁定策略
- 记录镜像变更历史

### 构建优化
- 使用 .dockerignore 排除不必要文件
- 利用 Docker 层缓存优化构建速度
- 合理安排 Dockerfile 指令顺序
- 使用多阶段构建优化镜像大小

### 仓库管理
- 使用镜像仓库代理加速下载
- 实施镜像垃圾回收策略
- 配置镜像保留策略
- 监控仓库存储空间使用

## 测试步骤
1. 确保 Docker 服务已安装并运行
2. 在 `vars/example_vars.yml` 中配置镜像参数
3. 准备应用源码和 Dockerfile
4. 使用 `--check` 模式预览镜像操作
5. 验证镜像构建和推送结果

## 常见问题
- **镜像拉取失败**：检查网络连接和仓库访问权限
- **构建失败**：检查 Dockerfile 语法和构建上下文
- **推送失败**：检查仓库认证和权限配置
- **存储空间不足**：清理无用镜像和容器

## 相关模块
- [docker_container](https://docs.ansible.com/ansible/latest/collections/community/docker/docker_container_module.html) - Docker 容器管理
- [docker_compose](https://docs.ansible.com/ansible/latest/collections/community/docker/docker_compose_module.html) - Docker Compose 管理
- [docker_login](https://docs.ansible.com/ansible/latest/collections/community/docker/docker_login_module.html) - Docker 登录认证