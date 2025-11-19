# stat 模块使用指南

## 模块用途
`ansible.builtin.stat` 模块用于获取远程文件或目录的状态信息，包括是否存在、权限、所有者、大小、哈希值等。通常与 `when` 条件、`register` 和其他文件模块配合使用。

## 主要参数
- `path`：目标文件或目录路径（必需）
- `follow`：是否跟随符号链接（默认 true）
- `get_checksum`：是否计算 sha1 校验和（默认 true）
- `get_mime`：是否获取 MIME 类型（默认 false）
- `get_md5`：是否计算 md5（默认 false，因性能原因可禁用）
- `get_attributes`：是否返回扩展属性（默认 true）
- `get_acl`：是否获取 ACL 信息（默认 false）
- `checksum_algorithm`：指定校验和算法（如 sha256）

## 返回值（stat.stat 字段）
- `exists`：文件是否存在
- `isdir` / `isreg` / `islnk`：是否目录/常规文件/符号链接
- `mode`：权限（八进制字符串）
- `uid` / `gid`：所有者 UID/GID
- `pw_name` / `gr_name`：所有者和组名
- `size`：文件大小（字节）
- `mtime` / `ctime` / `atime`：时间戳
- `checksum`：sha1 校验和（在 `get_checksum` 为 true 时返回）

## 使用场景
- **条件判断**：仅在文件存在时执行后续任务
- **校验权限**：执行前检查文件权限是否符合要求
- **变更验证**：在修改文件前后计算 checksum，确认是否变更
- **文件信息记录**：在部署流程中记录文件元数据

## 示例
```yaml
# 获取文件信息并根据结果执行任务
- name: 获取配置文件状态
  ansible.builtin.stat:
    path: /etc/app.conf
  register: app_conf

- name: 仅当文件存在时执行操作
  ansible.builtin.debug:
    msg: "配置文件大小为 {{ app_conf.stat.size }} 字节"
  when: app_conf.stat.exists
```

### 检查权限
```yaml
- name: 检查私钥权限
  ansible.builtin.stat:
    path: /etc/ssl/private/app.key
  register: key_stat

- name: 确保权限正确
  ansible.builtin.fail:
    msg: "私钥权限应为 0400"
  when: key_stat.stat.mode != '0400'
```

## 注意事项
- stat 模块不会修改任何文件，运行安全
- 每次执行都会访问文件系统，频繁调用可能影响性能
- 在大目录上使用 stat（递归）可能耗时较长

## 常见配合
- **file 模块**：使用 stat 判断文件存在，再决定是否创建或修改
- **copy/template**：部署前检查旧文件信息
- **lineinfile**：判断配置文件是否存在，避免创建临时文件

## 常见问题
- **为什么 `stat` 表示文件不存在？** 检查路径和权限，确保 Ansible 用户有读取权限
- **如何判断文件是否为目录？** 使用 `stat.stat.isdir`
- **如何获取 md5？** 设置 `get_md5: true`

## 相关链接
- [file 模块](../file/README.md)
- [copy 模块](../copy/README.md)
