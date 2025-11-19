# npm 模块使用指南

## 模块简介
`community.general.npm` 模块用于管理 Node.js 包的安装、升级和卸载，支持 npm 包、本地包、Git 仓库包等多种安装方式。该模块是前端应用和 Node.js 服务依赖管理的核心工具，适用于项目构建、依赖安装和生产环境部署。

## 主要参数

### 基础配置
- `name`：包名称，支持单个包名或包列表
- `path`：Node.js 项目路径（包含 package.json）
- `state`：包状态，可选值：
  - `present`：确保包存在（默认）
  - `absent`：删除包
  - `latest`：安装或升级到最新版本

### 版本控制
- `version`：指定包版本（如 `1.2.3`、`^1.0.0`）
- `global`：是否全局安装（默认：false）
- `production`：是否只安装生产依赖（默认：false）

### 高级选项
- `executable`：指定 npm 可执行文件路径
- `npmrc`：.npmrc 配置文件路径
- `registry`：npm 注册表地址
- `ignore_scripts`：是否忽略包的安装脚本

## 返回值
- `changed`：是否执行了变更操作
- `msg`：操作结果描述信息
- `name`：处理的包名称
- `state`：目标状态
- `version`：安装的包版本
- `path`：项目路径

## 常见使用场景

### 1. 安装单个 npm 包
```yaml
- name: 安装 Express Web 框架
  community.general.npm:
    name: express
    state: present
    version: "4.18.2"
    path: "{{ app_path }}"
```

### 2. 全局安装 CLI 工具
```yaml
- name: 全局安装 PM2 进程管理器
  community.general.npm:
    name: pm2
    state: present
    global: true
```

### 3. 安装项目依赖
```yaml
- name: 安装项目所有依赖
  community.general.npm:
    path: "{{ project_path }}"
    state: present
    production: false
```

### 4. 只安装生产依赖
```yaml
- name: 安装生产环境依赖
  community.general.npm:
    path: "{{ project_path }}"
    state: present
    production: true
```

### 5. 升级包到最新版本
```yaml
- name: 升级安全相关包
  community.general.npm:
    name:
      - lodash
      - request
      - moment
    state: latest
    path: "{{ project_path }}"
```

### 6. 从 Git 仓库安装包
```yaml
- name: 安装 GitHub 上的开发版本包
  community.general.npm:
    name: "git+https://github.com/user/repo.git#v2.0.0"
    state: present
    path: "{{ project_path }}"
```

### 7. 卸载开发依赖
```yaml
- name: 卸载开发工具
  community.general.npm:
    name:
      - nodemon
      - jest
      - eslint
    state: absent
    path: "{{ project_path }}"
```

## 安全注意事项

### 包安全
- 使用可信的 npm 注册表，避免恶意包
- 固定包版本避免供应链攻击
- 定期更新安全补丁和依赖包
- 使用 `npm audit` 检查安全漏洞

### 权限控制
- 避免使用 `sudo` 运行 npm
- 使用专用用户运行 Node.js 应用
- 限制 npm 的全局安装权限
- 配置合适的文件权限

### 网络安全
- 使用企业内部 npm 镜像
- 配置 HTTPS 注册表
- 实施包签名验证
- 限制网络访问范围

## 最佳实践

### 依赖管理
- 使用 package.json 管理项目依赖
- 区分开发和生产环境依赖
- 定期审计和更新依赖包
- 使用 `package-lock.json` 锁定版本

### 版本控制
- 使用语义化版本号
- 遵循语义化版本范围
- 测试包升级的兼容性
- 记录版本变更原因

### 环境配置
- 为不同环境使用不同的 .npmrc 配置
- 使用环境变量管理配置差异
- 实施依赖包缓存策略
- 配置代理和镜像源

## 测试步骤
1. 确认 Node.js 和 npm 已安装
2. 在 `vars/example_vars.yml` 中配置包参数
3. 使用 `--check` 模式预览包变更
4. 验证 node_modules 和包安装状态
5. 测试应用构建和运行

## 常见问题
- **包安装失败**：检查网络连接和 npm 源配置
- **版本冲突**：检查 package.json 和 package-lock.json
- **权限问题**：检查目录权限和 npm 配置
- **依赖缺失**：检查 Node.js 版本兼容性

## 相关模块
- [yarn](https://docs.ansible.com/ansible/latest/collections/community/general/yarn_module.html) - Yarn 包管理器
- [npm](https://docs.ansible.com/ansible/latest/collections/community/general/npm_module.html) - npm 包管理器
- [git](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/git_module.html) - Git 仓库管理