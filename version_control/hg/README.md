# hg 模块使用指南

## 模块简介
`community.general.hg` 模块用于管理 Mercurial（Hg）仓库的克隆、拉取、推送、分支和标签等操作。该模块是 Mercurial 工作流自动化的核心工具，支持代码部署、版本发布、持续集成等场景，为使用 Mercurial 版本控制系统的项目提供可靠的自动化支持。

## 主要参数

### 基础配置
- `repo`：Mercurial 仓库 URL
- `dest`：本地克隆目录路径
- `state`：仓库状态，可选值：
  - `present`：确保仓库存在且为指定版本（默认）
  - `absent`：删除本地仓库目录
  - `latest`：拉取最新代码

### 版本控制
- `revision`：指定分支、标签或 changeset hash
- `force`：是否强制覆盖本地更改（默认：false）
- `purge`：是否删除未跟踪的文件（默认：false）

### 认证配置
- `ssh_key_file`：SSH 私钥文件路径
- `ssh_opts`：额外的 SSH 选项
- `username`：HTTP 基本认证用户名
- `password`：HTTP 基本认证密码

### 高级选项
- `update`：是否更新到指定版本（默认：true）
- `clone`：是否执行克隆操作（默认：true）
- `pull`：是否执行拉取操作（默认：true）

## 返回值
- `changed`：是否执行了变更操作
- `msg`：操作结果描述信息
- `after`：操作后的 revision
- `before`：操作前的 revision
- `remote_url`：远程仓库 URL

## 常见使用场景

### 1. 克隆 Mercurial 仓库
```yaml
- name: 克隆应用源码仓库
  community.general.hg:
    repo: "{{ app_repository_url }}"
    dest: "{{ app_source_path }}"
    revision: "{{ app_version }}"
```

### 2. 部署指定版本
```yaml
- name: 部署指定版本的应用
  community.general.hg:
    repo: "{{ app_repository_url }}"
    dest: "{{ deploy_path }}"
    revision: "{{ app_version }}"
    force: true
    purge: true
```

### 3. 持续部署拉取最新代码
```yaml
- name: 拉取最新代码进行部署
  community.general.hg:
    repo: "{{ app_repository_url }}"
    dest: "{{ deploy_path }}"
    revision: "default"
    force: true
    update: true
```

### 4. 使用 SSH 密钥认证
```yaml
- name: 使用 SSH 密钥克隆私有仓库
  community.general.hg:
    repo: "ssh://hg@bitbucket.org/company/private-repo"
    dest: "{{ deploy_path }}"
    revision: "{{ target_version }}"
    ssh_key_file: "{{ ssh_private_key_path }}"
```

### 5. 使用 HTTP 基本认证
```yaml
- name: 使用 HTTP 认证克隆仓库
  community.general.hg:
    repo: "https://bitbucket.org/company/private-repo"
    dest: "{{ deploy_path }}"
    revision: "{{ target_version }}"
    username: "{{ hg_username }}"
    password: "{{ hg_password }}"
```

### 6. 管理多个分支部署
```yaml
- name: 部署不同环境的分支
  community.general.hg:
    repo: "{{ app_repository_url }}"
    dest: "{{ item.deploy_path }}"
    revision: "{{ item.branch }}"
    force: true
    purge: true
  loop: "{{ deployment_environments }}"
  loop_control:
    label: "{{ item.name }}"
  vars:
    item:
      - name: "production"
        branch: "stable"
        deploy_path: "/opt/app/prod"
      - name: "staging"
        branch: "default"
        deploy_path: "/opt/app/staging"
```

### 7. 标签管理
```yaml
- name: 切换到指定版本标签
  community.general.hg:
    repo: "{{ app_repository_url }}"
    dest: "{{ deploy_path }}"
    revision: "{{ release_tag }}"
    force: true
    update: true
```

### 8. 清理未跟踪文件
```yaml
- name: 拉取代码并清理未跟踪文件
  community.general.hg:
    repo: "{{ app_repository_url }}"
    dest: "{{ deploy_path }}"
    revision: "{{ target_revision }}"
    force: true
    purge: true
    update: true
```

## 安全注意事项

### 认证安全
- 使用 SSH 密钥而非密码认证
- 定期轮换 SSH 密钥和访问凭证
- 限制密钥文件访问权限
- 使用 HTTPS 安全协议传输

### 仓库安全
- 验证仓库 URL 的真实性
- 使用可信的仓库服务器
- 启用仓库访问日志
- 实施网络访问控制

### 代码安全
- 扫描代码安全漏洞
- 检查恶意代码注入
- 验证 changeset 签名
- 实施代码审查流程

## 最佳实践

### 版本管理
- 使用语义化版本标签
- 维护清晰的分支策略
- 锁定生产环境版本
- 记录版本变更历史

### 部署策略
- 使用 atomic 部署减少停机时间
- 实施蓝绿部署策略
- 配置自动回滚机制
- 维护多环境分支策略

### 性能优化
- 使用浅克隆减少传输时间
- 启用 Mercurial 协议优化
- 配置本地缓存策略
- 合理设置更新频率

## Mercurial 特有特性

### 分支模型
- **命名分支**：永久性分支，适合长期功能开发
- **匿名分支**：临时性分支，适合实验性开发
- **书签**：轻量级分支指针，适合短期工作

### 工作流
- **Centralized Workflow**：集中式工作流，类似 SVN
- **Feature Branch Workflow**：功能分支工作流
- **Forking Workflow**：分叉工作流，适合开源项目

### 高级功能
- **Histedit**：交互式历史编辑
- **Rebase**：变基操作
- **MQ（Mercurial Queues）**：补丁管理
- **Phases**：变更阶段管理（public/draft/secret）

## 测试步骤
1. 确保 Mercurial 客户端已安装
2. 配置 SSH 密钥或访问凭证
3. 在 `vars/example_vars.yml` 中配置仓库参数
4. 使用 `--check` 模式预览 Hg 操作
5. 验证代码拉取和版本切换结果

## 常见问题
- **克隆失败**：检查网络连接和认证配置
- **版本冲突**：检查分支和标签是否存在
- **权限问题**：检查 SSH 密钥和仓库访问权限
- **合并冲突**：检查代码冲突和合并策略

## 相关模块
- [git](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/git_module.html) - Git 仓库管理
- [github_release](https://docs.ansible.com/ansible/latest/collections/community/general/github_release_module.html) - GitHub Release 管理
- [gitlab_project](https://docs.ansible.com/ansible/latest/collections/community/general/gitlab_project_module.html) - GitLab 项目管理

## Mercurial vs Git 对比

| 特性 | Mercurial | Git |
|------|-----------|-----|
| 易用性 | 更简单，学习曲线平缓 | 功能丰富，学习曲线陡峭 |
| 性能 | 大文件处理更好 | 小文件操作更快 |
| 分支模型 | 更直观的命名分支 | 轻量级分支 |
| Windows 支持 | 原生支持优秀 | 改进中 |
| 扩展性 | 强大的扩展系统 | 内置功能丰富 |
| 社区 | 相对较小但活跃 | 非常庞大活跃 |