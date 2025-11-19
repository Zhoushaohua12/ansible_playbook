# git_workflow 模块使用指南

## 模块简介
`ansible.builtin.git` 模块用于管理 Git 仓库的克隆、拉取、推送、分支和标签等操作。该模块是 Git 工作流自动化的核心工具，支持代码部署、版本发布、持续集成等场景，为 DevOps 流水线提供可靠的版本控制基础。

## 主要参数

### 基础配置
- `repo`：Git 仓库 URL（支持 HTTPS 和 SSH）
- `dest`：本地克隆目录路径
- `state`：仓库状态，可选值：
  - `present`：确保仓库存在且为指定版本（默认）
  - `absent`：删除本地仓库目录
  - `latest`：拉取最新代码

### 版本控制
- `version`：指定分支、标签或 commit hash
- `force`：是否强制覆盖本地更改（默认：false）
- `depth`：浅克隆深度（用于减少克隆时间）

### 认证配置
- `key_file`：SSH 私钥文件路径
- `accept_hostkey`：是否接受主机密钥（默认：false）
- `ssh_opts`：额外的 SSH 选项

### 高级选项
- `remote`：远程仓库名称（默认：origin）
- `refspec`：引用规范
- `bare`：是否创建裸仓库（默认：false）
- `recursive`：是否递归初始化子模块（默认：true）

## 返回值
- `changed`：是否执行了变更操作
- `msg`：操作结果描述信息
- `after`：操作后的 commit hash
- `before`：操作前的 commit hash
- `remote_url_changed`：远程 URL 是否变更

## 常见使用场景

### 1. 克隆应用源码
```yaml
- name: 克隆应用源码仓库
  ansible.builtin.git:
    repo: "{{ app_repository_url }}"
    dest: "{{ app_source_path }}"
    version: "{{ app_version }}"
    accept_hostkey: true
```

### 2. 部署特定版本
```yaml
- name: 部署指定版本的应用
  ansible.builtin.git:
    repo: "{{ app_repository_url }}"
    dest: "{{ deploy_path }}"
    version: "v{{ app_version }}"
    force: true
```

### 3. 持续部署拉取最新代码
```yaml
- name: 拉取最新代码进行部署
  ansible.builtin.git:
    repo: "{{ app_repository_url }}"
    dest: "{{ deploy_path }}"
    version: "main"
    force: true
    update: true
```

### 4. 浅克隆优化速度
```yaml
- name: 浅克隆仓库（仅最新代码）
  ansible.builtin.git:
    repo: "{{ app_repository_url }}"
    dest: "{{ temp_path }}"
    depth: 1
    version: "{{ target_branch }}"
```

### 5. 使用 SSH 密钥认证
```yaml
- name: 使用 SSH 密钥克隆私有仓库
  ansible.builtin.git:
    repo: "git@github.com:company/private-repo.git"
    dest: "{{ deploy_path }}"
    version: "{{ target_version }}"
    key_file: "{{ ssh_private_key_path }}"
    accept_hostkey: true
```

### 6. 管理多个分支部署
```yaml
- name: 部署不同环境的分支
  ansible.builtin.git:
    repo: "{{ app_repository_url }}"
    dest: "{{ deploy_path }}"
    version: "{{ item.branch }}"
    force: true
  loop: "{{ deployment_environments }}"
  loop_control:
    label: "{{ item.name }}"
  vars:
    item:
      - name: "production"
        branch: "main"
      - name: "staging"
        branch: "develop"
```

### 7. 子模块递归更新
```yaml
- name: 克隆包含子模块的项目
  ansible.builtin.git:
    repo: "{{ app_repository_url }}"
    dest: "{{ deploy_path }}"
    version: "{{ app_version }}"
    recursive: true
    update: true
```

### 8. 标签管理
```yaml
- name: 切换到指定版本标签
  ansible.builtin.git:
    repo: "{{ app_repository_url }}"
    dest: "{{ deploy_path }}"
    version: "{{ release_tag }}"
    force: true
```

## 安全注意事项

### 认证安全
- 使用 SSH 密钥而非密码认证
- 定期轮换 SSH 密钥
- 限制密钥文件访问权限
- 使用个人访问令牌（PAT）替代密码

### 仓库安全
- 验证仓库 URL 的真实性
- 使用 HTTPS 或 SSH 安全协议
- 启用仓库签名验证
- 避免使用不安全的 git 协议

### 代码安全
- 扫描代码安全漏洞
- 检查恶意代码注入
- 验证 commit 签名
- 实施代码审查流程

## 最佳实践

### 版本管理
- 使用语义化版本标签
- 锁定生产环境版本
- 测试版本兼容性
- 记录版本变更历史

### 部署策略
- 使用蓝绿部署减少停机时间
- 实施金丝雀发布策略
- 配置自动回滚机制
- 维护多环境分支策略

### 性能优化
- 使用浅克隆减少传输时间
- 启用 git 协议优化
- 配置本地缓存策略
- 合理设置克隆深度

## 测试步骤
1. 确保 Git 客户端已安装
2. 配置 SSH 密钥或访问令牌
3. 在 `vars/example_vars.yml` 中配置仓库参数
4. 使用 `--check` 模式预览 Git 操作
5. 验证代码拉取和版本切换结果

## 常见问题
- **克隆失败**：检查网络连接和认证配置
- **版本冲突**：检查分支和标签是否存在
- **权限问题**：检查 SSH 密钥和仓库访问权限
- **子模块问题**：检查子模块配置和访问权限

## 相关模块
- [github_release](https://docs.ansible.com/ansible/latest/collections/community/general/github_release_module.html) - GitHub Release 管理
- [gitlab_project](https://docs.ansible.com/ansible/latest/collections/community/general/gitlab_project_module.html) - GitLab 项目管理
- [hg](https://docs.ansible.com/ansible/latest/collections/community/general/hg_module.html) - Mercurial 仓库管理