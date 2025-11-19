# pip 模块使用指南

## 模块简介
`ansible.builtin.pip` 模块用于管理 Python 包的安装、升级和卸载，支持 PyPI 包、本地包、Git 仓库包等多种安装方式。该模块是 Python 应用依赖管理的核心工具，适用于虚拟环境管理、应用部署和开发环境配置。

## 主要参数

### 基础配置
- `name`：包名称，支持单个包名或包列表
- `state`：包状态，可选值：
  - `present`：确保包存在（默认）
  - `absent`：删除包
  - `latest`：安装或升级到最新版本
  - `forcereinstall`：强制重新安装

### 版本控制
- `version`：指定包版本（如 `1.2.3`、`>=1.0,<2.0`）
- `executable`：指定 pip 可执行文件路径
- `virtualenv`：虚拟环境路径
- `virtualenv_command`：虚拟环境创建命令

### 高级选项
- `requirements`：requirements.txt 文件路径
- `extra_args`：额外的 pip 命令行参数
- `chdir`：执行命令前切换的工作目录
- `umask`：文件创建权限掩码

## 返回值
- `changed`：是否执行了变更操作
- `cmd`：执行的 pip 命令
- `msg`：操作结果描述信息
- `name`：处理的包名称
- `requirements`：requirements 文件路径（如果使用）
- `state`：目标状态
- `version`：安装的包版本

## 常见使用场景

### 1. 安装单个 Python 包
```yaml
- name: 安装 Flask Web 框架
  ansible.builtin.pip:
    name: flask
    state: present
    version: "2.3.2"
```

### 2. 批量安装依赖包
```yaml
- name: 从 requirements.txt 安装应用依赖
  ansible.builtin.pip:
    requirements: "{{ app_path }}/requirements.txt"
    virtualenv: "{{ app_venv_path }}"
    state: present
```

### 3. 虚拟环境管理
```yaml
- name: 在虚拟环境中安装科学计算包
  ansible.builtin.pip:
    name:
      - numpy
      - pandas
      - matplotlib
      - scipy
    virtualenv: "{{ project_venv }}"
    state: present
```

### 4. 从 Git 仓库安装开发版本
```yaml
- name: 安装 GitHub 上的开发版本包
  ansible.builtin.pip:
    name: git+https://github.com/user/repo.git@develop#egg=package_name
    state: forcereinstall
```

### 5. 升级包到最新版本
```yaml
- name: 升级所有安全相关包
  ansible.builtin.pip:
    name:
      - requests
      - urllib3
      - certifi
    state: latest
```

### 6. 卸载不需要的包
```yaml
- name: 清理开发依赖包
  ansible.builtin.pip:
    name:
      - pytest
      - black
      - flake8
    state: absent
```

## 安全注意事项

### 包安全
- 使用可信的 PyPI 源，避免恶意包
- 固定包版本避免供应链攻击
- 定期更新安全补丁和依赖包
- 使用包哈希验证确保完整性

### 权限控制
- 避免在系统级别安装包，优先使用虚拟环境
- 使用专用用户运行 Python 应用
- 限制 pip 的网络访问权限

### 环境隔离
- 为每个项目创建独立的虚拟环境
- 使用 `virtualenv` 参数指定环境路径
- 避免全局包冲突和依赖污染

## 最佳实践

### 依赖管理
- 使用 requirements.txt 管理项目依赖
- 区分开发和生产环境依赖
- 定期审计和更新依赖包

### 版本控制
- 使用语义化版本号
- 锁定关键依赖包版本
- 测试包升级的兼容性

### 环境配置
- 为不同环境创建不同的虚拟环境
- 使用环境变量管理配置差异
- 实施依赖包缓存策略

## 测试步骤
1. 确认 Python 和 pip 已安装
2. 在 `vars/example_vars.yml` 中配置包参数
3. 使用 `--check` 模式预览包变更
4. 验证虚拟环境和包安装状态
5. 测试应用功能是否正常

## 常见问题
- **包安装失败**：检查网络连接和 PyPI 源配置
- **版本冲突**：使用虚拟环境隔离依赖
- **权限问题**：检查虚拟环境目录权限
- **依赖缺失**：安装系统级开发依赖包

## 相关模块
- [virtualenv](https://docs.ansible.com/ansible/latest/collections/community/general/virtualenv_module.html) - 虚拟环境管理
- [package](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/package_module.html) - 系统包管理
- [git](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/git_module.html) - Git 仓库管理