# synchronize 模块使用指南

## 模块用途
`ansible.posix.synchronize` 模块基于 `rsync` 命令实现高效的文件和目录同步，适用于大规模文件传输、增量备份、代码部署等场景。相比 `copy` 模块，它能显著提升传输速度。

## 主要参数
- `src`：源目录或文件路径（必需）
- `dest`：目标路径（必需）
- `mode`：同步模式（`push` 或 `pull`，默认 `push`）
- `delete`：是否删除目标目录中多余的文件（默认 false）
- `recursive`：是否递归同步目录（默认 true）
- `rsync_opts`：传递给 rsync 的额外选项
- `checksum`：是否使用校验和比较（默认 false，使用时间戳和大小）
- `archive`：是否使用归档模式（保留权限、时间戳等，默认 true）
- `compress`：是否启用压缩传输（默认 true）
- `links`：是否复制符号链接
- `times`：是否保留时间戳
- `dirs`：是否复制目录（不递归）
- `partial`：支持断点续传
- `link_dest`：使用硬链接进行增量备份

## 返回值
- `changed`：文件是否发生变化
- `cmd`：实际执行的 rsync 命令
- `stdout` / `stderr`：rsync 输出内容

## 前置条件
- **控制节点和目标主机都需要安装 rsync**
- 使用 `mode: pull` 时，源主机也需要 rsync
- 目标主机需要 SSH 访问权限

## 使用场景

### 代码部署
将构建好的应用代码快速同步到多台服务器。

### 增量备份
定期备份文件到远程服务器，只传输变化的部分。

### 静态资源同步
将静态网站或媒体文件批量分发到 Web 服务器。

### 配置文件分发
将大量配置文件目录同步到集群节点。

## 最佳实践

### 基础目录同步
```yaml
- name: 同步应用代码到远程主机
  ansible.posix.synchronize:
    src: /local/app/dist/
    dest: /var/www/html/
    delete: yes  # 删除目标目录中多余的文件
```

### 排除特定文件
```yaml
- name: 同步代码（排除版本控制文件）
  ansible.posix.synchronize:
    src: /local/app/
    dest: /opt/app/
    rsync_opts:
      - "--exclude=.git"
      - "--exclude=node_modules"
      - "--exclude=*.log"
```

### 增量备份
```yaml
- name: 增量备份数据
  ansible.posix.synchronize:
    src: /data/
    dest: /backup/data/
    archive: yes
    checksum: yes
    delete: no  # 保留目标目录的旧文件
```

### Pull 模式（从远程主机拉取）
```yaml
- name: 从远程主机拉取日志
  ansible.posix.synchronize:
    mode: pull
    src: /var/log/app/
    dest: /local/backup/logs/
```

### 使用校验和确保一致性
```yaml
- name: 同步配置文件（使用校验和）
  ansible.posix.synchronize:
    src: /local/config/
    dest: /etc/myapp/
    checksum: yes
    rsync_opts:
      - "--exclude=*.bak"
```

## 注意事项

### 路径末尾的斜杠
- `src: /path/dir/` 表示同步目录内容
- `src: /path/dir` 表示同步整个目录（包括目录本身）

### delete 参数风险
- `delete: yes` 会删除目标目录中不存在于源目录的文件
- 建议先使用 `--check` 模式预览变化
- 对于生产环境，慎用此参数

### delegate_to 行为
- 使用 `delegate_to` 时，src 和 dest 的含义会改变
- 建议明确指定 `mode: push` 或 `mode: pull`

### 性能优化
- 使用 `compress: yes` 在低带宽网络中压缩传输
- 对于大文件，可启用 `partial: yes` 支持断点续传
- 使用 `checksum: no`（默认）通过时间戳比较，速度更快

### 编码问题
- rsync 默认处理二进制文件，对中文路径支持良好
- 确保文件系统编码一致（UTF-8）

## 常见陷阱

### 忘记安装 rsync
```yaml
# 确保 rsync 已安装
- name: 安装 rsync
  ansible.builtin.package:
    name: rsync
    state: present
```

### 混淆 push 和 pull
```yaml
# push：控制节点 → 远程主机（默认）
- name: 推送文件到远程
  ansible.posix.synchronize:
    src: /local/file
    dest: /remote/file
    mode: push

# pull：远程主机 → 控制节点
- name: 从远程拉取文件
  ansible.posix.synchronize:
    src: /remote/file
    dest: /local/file
    mode: pull
```

### delete 参数误删文件
```yaml
# ❌ 危险：可能删除目标目录的重要文件
- name: 同步（危险示例）
  ansible.posix.synchronize:
    src: /source/
    dest: /dest/
    delete: yes

# ✅ 安全：先使用 --check 预览
- name: 预览同步变化
  ansible.posix.synchronize:
    src: /source/
    dest: /dest/
    delete: yes
  check_mode: yes
```

## 测试步骤
1. 确保控制节点和目标主机都安装了 rsync
2. 在 `vars/example_vars.yml` 中配置源和目标路径
3. 准备源目录和测试文件
4. 使用 `--check` 模式预览同步操作
5. 实际执行并验证目标目录内容
6. 测试增量同步（修改源文件后再次执行）

## 常见问题
- **rsync not found**：目标主机未安装 rsync，使用 `package` 模块安装
- **Permission denied**：检查 SSH 权限和目标目录权限
- **路径问题**：注意源路径末尾的 `/` 会影响同步行为
- **删除了不该删除的文件**：慎用 `delete: yes`，建议先 dry-run

## 与其他模块的比较
- **synchronize vs copy**：synchronize 适合大规模文件和目录，copy 适合单个文件或小批量
- **synchronize vs template**：synchronize 用于静态文件，template 用于动态配置
- **synchronize vs git**：synchronize 用于通用文件同步，git 用于源码版本控制

## 相关示例
- [copy 模块](../copy/README.md) - 单文件传输
- [file 模块](../file/README.md) - 文件系统基础操作
- [find 模块](../find/README.md) - 文件查找

## 参考资源
- [rsync 官方文档](https://rsync.samba.org/documentation.html)
- [ansible.posix collection](https://docs.ansible.com/ansible/latest/collections/ansible/posix/synchronize_module.html)
