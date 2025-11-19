# template 模块使用指南

## 模块用途
`ansible.builtin.template` 模块将 Jinja2 模板渲染后部署到远程主机，非常适合需要根据变量、主机事实或条件生成动态配置文件的场景。

## 主要参数
- `src`：模板路径（通常位于模板目录 `templates/` 下）
- `dest`：目标文件路径（可包含变量）
- `mode`：设置渲染后文件的权限
- `owner` / `group`：设置文件的所有者和所属组
- `backup`：在覆盖目标文件前创建备份
- `force`：控制是否仅在内容变化时写入（默认为 true）
- `block_start_string`/`block_end_string`：自定义 Jinja2 起始/结束分隔符
- `newline_sequence`：控制换行符（适用于跨平台）
- `variable_start_string`/`variable_end_string`：自定义变量分隔符
- `trim_blocks`/`lstrip_blocks`：处理模板中的空行

## 返回值
- `changed`：文件是否发生变化
- `dest`：目标文件路径
- `checksum`：渲染文件的校验和
- `uid` / `gid`：文件所属用户和组
- `mode`：文件权限

## 典型场景
### 多环境配置
根据环境变量（dev/staging/prod）渲染不同的配置项，例如数据库地址、日志级别。

### 模板化服务配置
Nginx、Apache、Systemd、Prometheus 等服务的配置文件通常包含大量可变量化的部分。

### 中文文案和国际化
将中文提示、错误信息统一维护在模板中，便于多语言支持。

## 示例片段
```yaml
# 根据变量渲染配置文件
- name: 渲染应用配置
  ansible.builtin.template:
    src: templates/app.conf.j2
    dest: /etc/myapp/app.conf
    owner: appuser
    group: appgroup
    mode: '0640'
    backup: yes  # 中文注释：备份旧配置文件，防止误覆盖
```

## 注意事项
### 1. 编码一致性
- 模板文件、变量文件、目标文件都应使用 UTF-8 编码，避免中文乱码
- Windows 编辑器需关闭 BOM，Jinja2 对 BOM 支持有限

### 2. 幂等性
- template 默认会比较内容差异，仅在渲染结果变化时写入
- 使用 `--diff` 可查看渲染前后的差异，便于审查

### 3. 模板语法错误
- 渲染时出现 `template error` 通常由于 Jinja2 语法错误或变量不存在
- 建议在 playbook 中使用 `default` 过滤器，防止变量缺失

### 4. 安全与敏感信息
- 模板中引用的密码或密钥应存储在加密的 vars 文件或 Ansible Vault 中
- 对于包含敏感信息的模板文件，权限应设置为 `0600` 或 `0640`

### 5. 多行字符串与缩进
- 使用 `|`（pipe）或 `>`（folded）保留多行文本
- 结合 `indent` 过滤器保证嵌套结构的缩进正确

## 测试步骤
1. 在 `vars/example_vars.yml` 中定义模板变量
2. 编辑 `templates/*.j2` 模板并添加中文注释
3. 运行 `ansible-playbook playbook.yml --syntax-check`
4. 使用 `ansible-playbook playbook.yml --check --diff` 查看渲染结果
5. 确认渲染文件的权限、内容、中文显示正常

## 常见问题
- **变量未定义**：使用 `{{ variable | default('fallback') }}` 提供默认值
- **中文乱码**：确认模板与目标文件均为 UTF-8 编码
- **缩进错乱**：配合 `indent`、`trim_blocks` 等参数调整
- **复杂逻辑**：可在模板中使用 `{% if ... %}`、`{% for ... %}`、过滤器等语法

## 相关资源
- [Jinja2 模板语法](https://jinja.palletsprojects.com/)
- [Ansible template 模块文档](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html)
- [copy 模块](../copy/README.md) - 用于静态文件分发
