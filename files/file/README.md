# file 模块使用指南

## 模块用途
`ansible.builtin.file` 模块用于管理文件、目录、符号链接和硬链接，包括创建、删除、设置权限、更改所有者等基础文件系统操作。

## 主要参数
- `path`：目标文件或目录路径（必需）
- `state`：资源状态
  - `file`：确保文件存在（不创建）
  - `directory`：创建目录（父目录不存在时也会创建）
  - `absent`：删除文件或目录
  - `link`：创建符号链接
  - `hard`：创建硬链接
  - `touch`：创建空文件或更新时间戳
- `mode`：权限（如 '0755'、'u+rwx,g+rx,o+rx'）
- `owner` / `group`：设置所有者和组
- `recurse`：递归设置目录权限（配合 `state: directory`）
- `src`：符号链接或硬链接的源路径
- `force`：强制创建符号链接（覆盖已存在的文件）

## 返回值
- `changed`：文件系统是否发生变化
- `path`：目标路径
- `state`：文件状态（file/directory/link/absent）
- `mode`：文件权限
- `uid` / `gid`：所有者 UID/GID

## 使用场景
- **目录创建**：在部署前创建必要的目录结构
- **权限管理**：批量调整文件或目录权限
- **符号链接**：创建指向配置文件或可执行文件的软链接
- **清理操作**：删除临时文件、过期日志或测试数据
- **文件触碰**：更新文件时间戳或创建标记文件

## 最佳实践

### 创建目录树
```yaml
# 递归创建多级目录
- name: 创建应用目录结构
  ansible.builtin.file:
    path: /opt/app/{{ item }}
    state: directory
    owner: appuser
    group: appgroup
    mode: '0755'
  loop:
    - bin
    - config
    - logs
    - data
```

### 设置文件权限
```yaml
# 修改文件权限和所有者
- name: 设置配置文件权限
  ansible.builtin.file:
    path: /etc/app/app.conf
    owner: root
    group: appgroup
    mode: '0640'
```

### 递归设置目录权限
```yaml
# 递归修改目录及其内容的权限
- name: 修改日志目录权限
  ansible.builtin.file:
    path: /var/log/app
    state: directory
    owner: appuser
    group: appgroup
    mode: '0755'
    recurse: yes
```

### 创建符号链接
```yaml
# 创建指向可执行文件的符号链接
- name: 创建命令符号链接
  ansible.builtin.file:
    src: /opt/app/bin/app-v2.0
    dest: /usr/local/bin/app
    state: link
    force: yes  # 覆盖已存在的链接
```

### 删除文件或目录
```yaml
# 删除临时文件
- name: 清理临时文件
  ansible.builtin.file:
    path: /tmp/install_cache
    state: absent
```

### 创建空文件或更新时间戳
```yaml
# 创建标记文件
- name: 创建部署标记文件
  ansible.builtin.file:
    path: /var/run/app_deployed.flag
    state: touch
    mode: '0644'
```

## 注意事项

### 权限和所有者
- 修改文件所有者需要 root 权限（使用 `become: yes`）
- 权限字符串必须加引号（如 '0755'），避免被解析为八进制数字
- 使用符号模式时注意平台差异（如 macOS 和 Linux）

### 递归操作
- `recurse: yes` 会遍历所有子目录和文件，大目录可能耗时较长
- 递归修改权限时注意不要影响系统关键文件

### 符号链接
- `force: yes` 会覆盖目标路径的已有文件或链接
- 符号链接的 `src` 路径可以是相对路径或绝对路径
- 符号链接本身的权限通常不重要（实际权限由目标文件决定）

### 删除操作
- `state: absent` 会递归删除目录及其内容，谨慎使用
- 删除前建议先使用 `stat` 模块检查文件是否存在

### 幂等性
- file 模块是幂等的，多次执行相同操作不会重复变更
- 使用 `state: file` 时，如果文件不存在会报错（而非创建）

## 常见陷阱

### 忘记使用 become
```yaml
# ❌ 错误：修改系统目录权限但没有提权
- name: 创建系统目录（错误）
  ansible.builtin.file:
    path: /etc/myapp
    state: directory
    mode: '0755'

# ✅ 正确：使用 become 提权
- name: 创建系统目录（正确）
  ansible.builtin.file:
    path: /etc/myapp
    state: directory
    mode: '0755'
  become: yes
```

### 权限字符串未加引号
```yaml
# ❌ 错误：八进制数被错误解析
- name: 设置权限（错误）
  ansible.builtin.file:
    path: /tmp/test
    mode: 0755  # 会被解析为十进制 755

# ✅ 正确：使用引号
- name: 设置权限（正确）
  ansible.builtin.file:
    path: /tmp/test
    mode: '0755'
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中定义路径和权限参数
2. 使用 `--check` 模式预览操作
3. 实际执行并验证文件系统状态
4. 使用 `ls -la` 或 `stat` 检查权限和所有者
5. 测试幂等性（再次执行应显示 ok）

## 常见问题
- **为什么 state: file 失败？** 该状态用于检查文件存在，而非创建，使用 `state: touch` 或 `copy` 创建文件
- **如何批量创建目录？** 使用 `loop` 或 `with_items` 遍历目录列表
- **符号链接指向不存在的文件会失败吗？** 不会，符号链接可以指向不存在的路径（悬空链接）
- **如何递归删除目录？** 使用 `state: absent`，会自动递归删除

## 与其他模块的比较
- **file vs copy**：file 用于管理文件属性，copy 用于传输文件内容
- **file vs template**：file 不涉及文件内容，template 用于生成配置文件
- **file vs synchronize**：file 用于单个文件/目录操作，synchronize 用于批量同步

## 相关示例
- [copy 模块](../copy/README.md) - 文件内容传输
- [stat 模块](../stat/README.md) - 文件状态检查
- [find 模块](../find/README.md) - 文件查找和批量处理
