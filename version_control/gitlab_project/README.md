# gitlab_project 模块使用指南

## 模块简介
`community.general.gitlab_project` 模块用于管理 GitLab 项目的创建、更新、删除等操作。该模块是 GitLab 平台自动化的核心工具，支持项目管理、成员配置、权限控制等功能，适用于企业级 Git 环境的自动化运维和团队协作管理。

## 主要参数

### 基础配置
- `api_url`：GitLab API 地址
- `api_token`：GitLab Personal Access Token
- `name`：项目名称
- `group`：项目所属组（可选）
- `state`：项目状态，可选值：
  - `present`：确保项目存在（默认）
  - `absent`：删除项目

### 项目配置
- `description`：项目描述
- `visibility`：项目可见性，可选值：
  - `private`：私有（默认）
  - `internal`：内部
  - `public`：公开
- `issues_enabled`：是否启用 Issues（默认：true）
- `wiki_enabled`：是否启用 Wiki（默认：true）
- `merge_requests_enabled`：是否启用合并请求（默认：true）
- `builds_enabled`：是否启用 CI/CD（默认：true）

### 高级选项
- `namespace_id`：命名空间 ID
- `path`：项目路径
- `import_url`：导入项目的 URL
- `request_access_enabled`：是否允许请求访问（默认：true）
- `only_allow_merge_if_pipeline_succeeds`：是否仅允许流水线成功时合并（默认：false）
- `only_allow_merge_if_all_discussions_are_resolved`：是否仅允许所有讨论解决后合并（默认：false）

## 返回值
- `changed`：是否执行了变更操作
- `msg`：操作结果描述信息
- `project`：项目详细信息对象
- `error`：错误信息（如果操作失败）

## 常见使用场景

### 1. 创建新项目
```yaml
- name: 创建新的 GitLab 项目
  community.general.gitlab_project:
    api_url: "{{ gitlab_api_url }}"
    api_token: "{{ gitlab_token }}"
    name: "{{ project_name }}"
    description: "{{ project_description }}"
    visibility: private
    state: present
```

### 2. 创建组内项目
```yaml
- name: 在指定组中创建项目
  community.general.gitlab_project:
    api_url: "{{ gitlab_api_url }}"
    api_token: "{{ gitlab_token }}"
    name: "{{ project_name }}"
    group: "{{ gitlab_group }}"
    description: "{{ project_description }}"
    visibility: internal
    state: present
```

### 3. 配置项目高级选项
```yaml
- name: 创建具有高级配置的项目
  community.general.gitlab_project:
    api_url: "{{ gitlab_api_url }}"
    api_token: "{{ gitlab_token }}"
    name: "{{ project_name }}"
    description: "{{ project_description }}"
    visibility: private
    issues_enabled: false
    wiki_enabled: true
    merge_requests_enabled: true
    builds_enabled: true
    request_access_enabled: false
    only_allow_merge_if_pipeline_succeeds: true
    only_allow_merge_if_all_discussions_are_resolved: true
    state: present
```

### 4. 导入外部项目
```yaml
- name: 从 GitHub 导入项目
  community.general.gitlab_project:
    api_url: "{{ gitlab_api_url }}"
    api_token: "{{ gitlab_token }}"
    name: "{{ project_name }}"
    description: "从 GitHub 导入的项目"
    import_url: "{{ github_repo_url }}"
    visibility: private
    state: present
```

### 5. 批量创建项目
```yaml
- name: 批量创建团队项目
  community.general.gitlab_project:
    api_url: "{{ gitlab_api_url }}"
    api_token: "{{ gitlab_token }}"
    name: "{{ item.name }}"
    group: "{{ item.group }}"
    description: "{{ item.description }}"
    visibility: "{{ item.visibility }}"
    state: present
  loop: "{{ team_projects }}"
  loop_control:
    label: "{{ item.name }}"
```

### 6. 更新项目配置
```yaml
- name: 更新项目可见性
  community.general.gitlab_project:
    api_url: "{{ gitlab_api_url }}"
    api_token: "{{ gitlab_token }}"
    name: "{{ project_name }}"
    visibility: public
    description: "更新后的项目描述"
    state: present
```

### 7. 创建模板项目
```yaml
- name: 创建项目模板
  community.general.gitlab_project:
    api_url: "{{ gitlab_api_url }}"
    api_token: "{{ gitlab_token }}"
    name: "{{ template_name }}"
    group: "templates"
    description: "标准项目模板"
    visibility: internal
    issues_enabled: true
    wiki_enabled: true
    merge_requests_enabled: true
    builds_enabled: true
    state: present
```

### 8. 创建 CI/CD 项目
```yaml
- name: 创建启用 CI/CD 的项目
  community.general.gitlab_project:
    api_url: "{{ gitlab_api_url }}"
    api_token: "{{ gitlab_token }}"
    name: "{{ ci_project_name }}"
    description: "持续集成项目"
    visibility: private
    builds_enabled: true
    only_allow_merge_if_pipeline_succeeds: true
    only_allow_merge_if_all_discussions_are_resolved: true
    request_access_enabled: false
    state: present
```

## 安全注意事项

### 认证安全
- 使用 Personal Access Token 进行认证
- 限制 Token 权限范围（api、read_repository 等）
- 定期轮换访问令牌
- 使用 Ansible Vault 存储 Token

### 权限控制
- 确保账户有项目管理权限
- 使用服务账户而非个人账户
- 实施最小权限原则
- 配置项目访问策略

### 数据安全
- 设置合适的项目可见性
- 配置分支保护规则
- 启用代码审查流程
- 监控项目访问日志

## 最佳实践

### 项目管理
- 使用统一的命名约定
- 维护清晰的项目结构
- 配置合适的项目模板
- 实施项目生命周期管理

### 团队协作
- 配置合适的权限级别
- 启用必要的功能模块
- 设置合并策略
- 建立代码审查流程

### CI/CD 集成
- 启用自动化构建
- 配置部署流水线
- 设置环境变量
- 实施质量门禁

## 测试步骤
1. 获取 GitLab Personal Access Token
2. 在 `vars/example_vars.yml` 中配置 GitLab API 和认证参数
3. 确认有足够的权限创建项目
4. 使用 `--check` 模式预览项目操作
5. 验证项目创建和配置结果

## 常见问题
- **认证失败**：检查 Token 权限和有效期
- **权限不足**：检查账户权限和组权限
- **项目已存在**：检查项目名称和路径唯一性
- **导入失败**：检查源仓库访问权限

## 相关模块
- [gitlab_group](https://docs.ansible.com/ansible/latest/collections/community/general/gitlab_group_module.html) - GitLab 组管理
- [gitlab_user](https://docs.ansible.com/ansible/latest/collections/community/general/gitlab_user_module.html) - GitLab 用户管理
- [gitlab_runner](https://docs.ansible.com/ansible/latest/collections/community/general/gitlab_runner_module.html) - GitLab Runner 管理