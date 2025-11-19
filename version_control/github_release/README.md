# github_release 模块使用指南

## 模块简介
`community.general.github_release` 模块用于管理 GitHub 仓库的 Release 创建、更新和删除操作。该模块是版本发布自动化的重要工具，支持创建发布版本、上传二进制文件、生成 Release Notes 等功能，适用于 CI/CD 流水线中的发布管理。

## 主要参数

### 基础配置
- `user`：GitHub 用户名或组织名
- `repo`：仓库名称
- `action`：操作类型，可选值：
  - `create_release`：创建 Release（默认）
  - `latest_release`：获取最新 Release
  - `list_releases`：列出所有 Release

### Release 配置
- `tag`：版本标签（如 `v1.2.3`）
- `name`：Release 名称
- `body`：Release 描述内容
- `draft`：是否为草稿（默认：false）
- `prerelease`：是否为预发布版本（默认：false）

### 文件上传
- `files`：要上传的文件路径列表
- `file_path`：单个文件上传路径（已弃用，使用 files）

### 认证配置
- `token`：GitHub Personal Access Token
- `password`：GitHub 密码（不推荐，使用 token 替代）

### 高级选项
- `target_commitish`：目标 commit hash
- `draft_release_name`：草稿 Release 名称模板
- `draft_release_body`：草稿 Release 内容模板

## 返回值
- `changed`：是否执行了变更操作
- `msg`：操作结果描述信息
- `release`：Release 详细信息对象
- `url`：Release URL 地址
- `upload_url`：文件上传 URL

## 常见使用场景

### 1. 创建正式发布版本
```yaml
- name: 创建正式 Release
  community.general.github_release:
    user: "{{ github_user }}"
    repo: "{{ github_repo }}"
    token: "{{ github_token }}"
    action: create_release
    tag: "v{{ app_version }}"
    name: "Release v{{ app_version }}"
    body: "{{ release_notes }}"
    draft: false
    prerelease: false
```

### 2. 创建预发布版本
```yaml
- name: 创建预发布版本
  community.general.github_release:
    user: "{{ github_user }}"
    repo: "{{ github_repo }}"
    token: "{{ github_token }}"
    action: create_release
    tag: "v{{ app_version }}-rc.1"
    name: "Release Candidate v{{ app_version }}-rc.1"
    body: "{{ rc_release_notes }}"
    prerelease: true
```

### 3. 上传构建产物
```yaml
- name: 创建 Release 并上传二进制文件
  community.general.github_release:
    user: "{{ github_user }}"
    repo: "{{ github_repo }}"
    token: "{{ github_token }}"
    action: create_release
    tag: "v{{ app_version }}"
    name: "Release v{{ app_version }}"
    body: "{{ release_notes }}"
    files:
      - "{{ build_path }}/app-linux-amd64"
      - "{{ build_path }}/app-linux-arm64"
      - "{{ build_path }}/app-darwin-amd64"
      - "{{ build_path }}/app-windows-amd64.exe"
```

### 4. 创建草稿 Release
```yaml
- name: 创建草稿 Release
  community.general.github_release:
    user: "{{ github_user }}"
    repo: "{{ github_repo }}"
    token: "{{ github_token }}"
    action: create_release
    tag: "v{{ app_version }}-draft"
    name: "Draft Release v{{ app_version }}"
    body: "{{ draft_notes }}"
    draft: true
```

### 5. 获取最新 Release 信息
```yaml
- name: 获取最新 Release
  community.general.github_release:
    user: "{{ github_user }}"
    repo: "{{ github_repo }}"
    token: "{{ github_token }}"
    action: latest_release
  register: latest_release
```

### 6. 列出所有 Release
```yaml
- name: 列出所有 Release
  community.general.github_release:
    user: "{{ github_user }}"
    repo: "{{ github_repo }}"
    token: "{{ github_token }}"
    action: list_releases
  register: all_releases
```

### 7. 批量发布多平台二进制文件
```yaml
- name: 发布多平台二进制文件
  community.general.github_release:
    user: "{{ github_user }}"
    repo: "{{ github_repo }}"
    token: "{{ github_token }}"
    action: create_release
    tag: "v{{ app_version }}"
    name: "Release v{{ app_version }}"
    body: "{{ multi_platform_notes }}"
    files: "{{ binary_files }}"
  vars:
    binary_files:
      - "dist/{{ app_name }}-{{ app_version }}-linux-amd64.tar.gz"
      - "dist/{{ app_name }}-{{ app_version }}-linux-arm64.tar.gz"
      - "dist/{{ app_name }}-{{ app_version }}-darwin-amd64.tar.gz"
      - "dist/{{ app_name }}-{{ app_version }}-windows-amd64.zip"
```

### 8. 自动生成 Release Notes
```yaml
- name: 自动生成 Release Notes
  community.general.github_release:
    user: "{{ github_user }}"
    repo: "{{ github_repo }}"
    token: "{{ github_token }}"
    action: create_release
    tag: "v{{ app_version }}"
    name: "Release v{{ app_version }}"
    body: "{{ lookup('template', 'release_notes.j2') }}"
    target_commitish: "{{ commit_hash }}"
```

## 安全注意事项

### 认证安全
- 使用 Personal Access Token 进行认证
- 限制 Token 权限范围（仅 repo 权限）
- 定期轮换访问令牌
- 使用 Ansible Vault 存储 Token

### 权限控制
- 确保账户有仓库写入权限
- 使用服务账户而非个人账户
- 实施最小权限原则
- 监控 API 调用日志

### 内容安全
- 验证上传文件的完整性
- 扫描二进制文件安全漏洞
- 包含数字签名和校验和
- 避免在 Release Notes 中包含敏感信息

## 最佳实践

### 版本管理
- 使用语义化版本号
- 维护清晰的版本策略
- 自动生成版本标签
- 记录版本变更历史

### 发布流程
- 实施发布审批流程
- 自动化测试验证
- 生成详细的 Release Notes
- 配置发布通知机制

### 文件管理
- 使用标准化的文件命名
- 包含校验和文件
- 提供多平台二进制文件
- 压缩和优化文件大小

## 测试步骤
1. 获取 GitHub Personal Access Token
2. 在 `vars/example_vars.yml` 中配置仓库和认证参数
3. 准备要发布的二进制文件
4. 使用 `--check` 模式预览 Release 操作
5. 验证 Release 创建和文件上传结果

## 常见问题
- **认证失败**：检查 Token 权限和有效期
- **仓库不存在**：检查用户名和仓库名称
- **文件上传失败**：检查文件路径和大小限制
- **标签冲突**：检查标签是否已存在

## 相关模块
- [git](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/git_module.html) - Git 仓库管理
- [github_repo](https://docs.ansible.com/ansible/latest/collections/community/general/github_repo_module.html) - GitHub 仓库管理
- [gitlab_project](https://docs.ansible.com/ansible/latest/collections/community/general/gitlab_project_module.html) - GitLab 项目管理