# git 模块使用指南

## 模块简介
`ansible.builtin.git` 模块用于管理 Git 仓库的克隆、更新和版本控制操作。该模块支持从各种 Git 仓库获取源码，管理分支切换、标签检出等版本控制任务，是持续部署和源码管理的核心工具。

## 主要参数

### 仓库配置
- `repo`：Git 仓库的 URL（支持 HTTP/HTTPS、SSH、Git 协议）
- `dest`：目标目录路径，用于存放克隆的仓库
- `version`：要检出的版本，可以是：
  - 分支名（如 `main`、`develop`）
  - 标签名（如 `v1.2.3`）
  - commit hash（如 `a1b2c3d4`）
  - `HEAD`（默认，最新提交）

### 认证配置
- `key_file`：SSH 私钥文件路径
- `accept_hostkey`：是否自动接受主机密钥（默认：false）
- `ssh_opts`：额外的 SSH 选项

### 操作控制
- `force`：是否强制覆盖本地修改（默认：false）
- `depth`：克隆深度，用于浅克隆（如 `1` 表示仅最新提交）
- `clone`：是否执行克隆操作（默认：true）
- `update`：是否更新现有仓库（默认：true）

### 高级选项
- `refspec`：自定义 refspec 用于获取特定引用
- `remote`：远程仓库名称（默认：`origin`）
- `track_submodules`：是否初始化和更新子模块（默认：false）

## 返回值
- `after`：操作后的 commit hash
- `before`：操作前的 commit hash
- `changed`：是否执行了变更操作
- `remote_url_changed`：远程 URL 是否发生变更

## 常见使用场景

### 1. 基础源码部署
```yaml
- name: 克隆应用源码
  ansible.builtin.git:
    repo: https://github.com/company/webapp.git
    dest: /opt/webapp
    version: main
    force: true
```

### 2. 版本发布部署
```yaml
- name: 部署指定版本的应用
  ansible.builtin.git:
    repo: git@github.com:company/api-service.git
    dest: /opt/api-service
    version: "v2.1.0"  # 部署特定标签版本
    key_file: /home/deploy/.ssh/deploy_key
    accept_hostkey: true
```

### 3. 持续部署流水线
```yaml
- name: 获取最新代码并构建
  ansible.builtin.git:
    repo: "{{ git_repository }}"
    dest: "{{ app_source_path }}"
    version: "{{ git_branch }}"
    force: true
  register: git_result

- name: 仅在代码更新时执行构建
  ansible.builtin.command: npm run build
  args:
    chdir: "{{ app_source_path }}"
  when: git_result.changed

- name: 重启应用服务
  ansible.builtin.service:
    name: "{{ app_service_name }}"
    state: restarted
  when: git_result.changed
```

### 4. 多环境部署
```yaml
- name: 部署开发环境
  ansible.builtin.git:
    repo: "{{ app_repo }}"
    dest: "/opt/{{ app_name }}-dev"
    version: develop
  when: deploy_env == "development"

- name: 部署生产环境
  ansible.builtin.git:
    repo: "{{ app_repo }}"
    dest: "/opt/{{ app_name }}-prod"
    version: "{{ production_tag }}"
  when: deploy_env == "production"
```

### 5. 子模块管理
```yaml
- name: 克隆包含子模块的项目
  ansible.builtin.git:
    repo: https://github.com/company/complex-app.git
    dest: /opt/complex-app
    version: main
    track_submodules: true
    recursive: true
```

## 安全注意事项

### 认证安全
- 使用 SSH 密钥认证而非密码认证
- 定期轮换部署密钥
- 限制密钥文件权限（600）

### 仓库安全
- 使用 HTTPS 或 SSH 协议，避免未加密的 Git 协议
- 验证仓库 URL 的真实性
- 使用已知的可信仓库

### 代码安全
- 验证检出的代码签名（如果支持）
- 实施代码扫描和安全检查
- 限制特定分支的部署权限

## 最佳实践

### 版本管理
- 使用语义化版本标签
- 保持分支策略的一致性
- 实施代码审查流程

### 部署策略
- 使用蓝绿部署减少停机时间
- 实施回滚机制
- 保留部署历史记录

### 性能优化
- 使用浅克隆减少网络传输
- 合理设置更新频率
- 缓存常用依赖

## 测试步骤
1. 配置 Git 仓库访问权限
2. 在 `vars/example_vars.yml` 中设置仓库参数
3. 验证网络连接和认证配置
4. 测试不同版本的检出操作
5. 验证子模块和依赖管理

## 常见问题
- **认证失败**：检查 SSH 密钥权限和仓库访问权限
- **网络连接问题**：确认防火墙和代理设置
- **版本冲突**：确保目标版本在仓库中存在
- **权限问题**：检查目标目录的写权限

## 相关模块
- [file](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/file_module.html) - 文件和目录管理
- [command](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/command_module.html) - 执行构建命令
- [service](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/service_module.html) - 服务管理

## CI/CD 集成示例

### GitHub Actions 集成
```yaml
# .github/workflows/deploy.yml
- name: 部署到服务器
  uses: ansible/ansible-playbook-action@v2
  with:
    playbook: applications/git/playbook.yml
    inventory: production
    extra-vars: |
      git_version=${{ github.ref_name }}
      deploy_env=production
```

### Jenkins Pipeline 集成
```groovy
stage('Deploy') {
    steps {
        sh '''
        ansible-playbook applications/git/playbook.yml \
          -i production \
          -e "git_version=${BUILD_TAG}" \
          -e "deploy_env=production"
        '''
    }
}
```
