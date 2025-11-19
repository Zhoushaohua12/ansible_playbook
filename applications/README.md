# 应用管理模块指南

## 概述
应用管理是 DevOps 自动化的核心场景，涵盖软件包安装、容器部署、源码管理等关键操作。Ansible 通过统一的管理接口，支持从传统软件包到现代容器化应用的全生命周期管理。

## 适用场景
本模块适用于以下应用管理场景：

### 软件包管理
- **系统软件包**：通过 `yum`、`apt` 等包管理器安装系统依赖和工具软件
- **应用部署**：部署预编译的应用程序包（如 RPM、DEB 包）
- **依赖管理**：统一管理应用运行所需的系统依赖库

### 容器化部署
- **Docker 容器**：通过 `docker_container` 模块管理容器生命周期
- **镜像管理**：通过 `docker_image` 模块构建、推送和管理镜像
- **容器编排**：通过 `kubernetes` 模块管理 K8s 资源和容器编排
- **CI/CD 流水线**：集成镜像构建和部署流程

### 语言依赖管理
- **Python 依赖**：通过 `pip` 模块管理 Python 包和虚拟环境
- **Node.js 依赖**：通过 `npm` 模块管理前端依赖和 Node.js 应用
- **跨平台支持**：支持多种语言和平台的依赖管理

### 源码部署
- **Git 仓库**：通过 `git` 模块克隆应用源码
- **版本控制**：管理应用版本发布和回滚
- **持续部署**：集成 CI/CD 流水线实现自动化部署

## 目标受众
- **DevOps 工程师**：需要自动化应用部署和运维
- **系统管理员**：负责服务器环境配置和应用管理
- **开发人员**：需要了解 Ansible 在应用部署中的应用
- **运维团队**：寻求标准化应用部署流程

## 模块清单

| 模块 | 用途 | 典型场景 | 适用平台 |
|------|------|----------|----------|
| `docker_container` | Docker 容器管理 | 容器化应用部署、微服务管理 | Linux/Unix |
| `docker_image` | Docker 镜像管理 | 镜像构建、推送、CI/CD 流水线 | Linux/Unix |
| `kubernetes` | Kubernetes 资源管理 | K8s 资源部署、容器编排 | Kubernetes 集群 |
| `pip` | Python 包管理 | Python 依赖管理、虚拟环境 | 所有平台 |
| `npm` | Node.js 包管理 | 前端依赖、Node.js 应用部署 | 所有平台 |
| `git` | Git 仓库管理 | 源码部署、版本控制、CI/CD | 所有平台 |
| `package` | 通用包管理 | 跨平台软件包安装 | 所有平台 |
| `yum` | RPM 包管理 | Red Hat/CentOS 系统包管理 | RHEL/CentOS/Fedora |
| `apt` | DEB 包管理 | Debian/Ubuntu 系统包管理 | Debian/Ubuntu |

## 使用原则

### 幂等性设计
- 所有模块都支持幂等操作，可安全重复执行
- 通过 `state` 参数精确控制应用状态
- 使用条件判断避免不必要的变更

### 平台兼容性
- 优先使用通用模块（如 `package`）实现跨平台兼容
- 根据目标系统选择合适的包管理器
- 容器化部署提供更好的环境一致性

### 安全考虑
- 使用受信任的镜像源和软件仓库
- 实施镜像签名验证和包完整性检查
- 限制容器权限和网络访问

## 快速开始

### 选择合适的模块
1. **容器化应用** → 使用 `docker_container` + `docker_image`
2. **Kubernetes 编排** → 使用 `kubernetes`
3. **Python 应用** → 使用 `pip` + 其他模块组合
4. **Node.js 应用** → 使用 `npm` + 其他模块组合
5. **源码部署** → 使用 `git` + 其他模块组合
6. **系统软件** → 根据系统选择 `yum`/`apt` 或通用 `package`

### 典型工作流
```bash
# 1. 语法检查
ansible-playbook applications/[module]/playbook.yml --syntax-check

# 2. Dry-Run 预览
ansible-playbook applications/[module]/playbook.yml --check

# 3. 执行部署
ansible-playbook applications/[module]/playbook.yml

# 4. 验证结果
ansible-playbook applications/[module]/playbook.yml --check
```

## 最佳实践

### 容器部署
- 使用具体版本标签而非 `latest`
- 配置健康检查和重启策略
- 设置资源限制和网络隔离
- 使用 Kubernetes 管理容器编排

### 镜像管理
- 多阶段构建优化镜像大小
- 使用 .dockerignore 排除不必要文件
- 定期扫描镜像安全漏洞
- 实施镜像版本锁定策略

### 语言依赖
- 使用虚拟环境隔离依赖
- 锁定依赖包版本确保一致性
- 定期更新安全补丁和依赖
- 使用私有仓库加速下载

### 包管理
- 锁定软件包版本确保环境一致性
- 使用本地镜像仓库加速部署
- 定期更新安全补丁

### 源码部署
- 使用 Git 标签或 commit hash 精确控制版本
- 实施代码审查和安全扫描
- 配置部署回滚机制

## 相关模块
- [命令执行模块](../commands/README.md) - 应用部署中的命令执行
- [Web 服务管理](../web/README.md) - 与 Web 服务器集成
- [存储管理](../storage/README.md) - 应用数据存储配置
- [版本控制](../version_control/README.md) - Git、GitHub、GitLab 等版本控制集成

## 注意事项
- **容器示例建议在本地或 CI 环境仅做语法检查**，避免在生产环境直接运行
- **包管理操作需要 root 权限**，请确保适当的权限配置
- **Git 操作需要网络访问**，请检查防火墙和代理设置
