# find 模块使用指南

## 模块用途
`ansible.builtin.find` 模块用于在远程主机上按条件查找文件或目录。它支持按文件名、大小、修改时间、权限等条件过滤，并可返回详细的文件属性，用于后续任务处理。

## 主要参数
- `paths`：要搜索的起始路径（必需，可为列表）
- `patterns`：匹配的文件名模式（支持通配符）
- `use_regex`：是否使用正则表达式匹配
- `file_type`：限制文件类型（`file`、`directory`、`link`、`any`）
- `age`：按修改时间过滤（如 `1d`、`4h`、`30m`）
- `age_stamp`：使用 `mtime`、`ctime` 或 `atime`（默认 `mtime`）
- `size`：按大小过滤（如 `100k`、`1m`）
- `recurse`：是否递归搜索（默认 true）
- `hidden`：是否包含隐藏文件
- `follow`：是否跟随符号链接
- `contains`：匹配文件内容（正则）
- `excludes`：排除的路径或模式

## 返回值
- `matched`：匹配到的文件数量
- `files`：文件列表（包含 path、mode、uid、gid、size、mtime 等信息）

## 使用场景
- 日志清理：查找并删除超过一定时间的日志文件
- 临时文件管理：查找 `/tmp` 下的过期文件
- 配置检查：查找缺失或多余的配置文件
- 备份管理：查找大型文件用于归档或迁移

## 示例
```yaml
# 查找超过 7 天的日志文件
- name: 查找过期日志
  ansible.builtin.find:
    paths: /var/log/myapp
    patterns: '*.log'
    age: 7d
    age_stamp: mtime
  register: expired_logs

- name: 删除过期日志
  ansible.builtin.file:
    path: "{{ item.path }}"
    state: absent
  loop: "{{ expired_logs.files }}"
```

```yaml
# 查找超过 100MB 的文件
- name: 查找大文件
  ansible.builtin.find:
    paths: /data
    size: 100m
  register: large_files
```

## 注意事项
- `find` 模块默认递归搜索，目录层次深时可能耗时较长
- 在大目录中查找前，可使用 `excludes` 排除无关路径
- `find` 模块只搜索，不会修改文件，需要配合其他模块处理结果
- 使用 `loop: "{{ result.files }}"` 处理匹配到的文件
- `age` 和 `size` 参数支持 `+`、`-` 前缀控制大于/小于，默认表示大于等于

## 性能优化
- 限制搜索路径范围，避免对整个文件系统递归
- 合理使用 `patterns`、`file_type` 和 `excludes` 减少匹配数量
- 对于超级用户执行的任务，可使用 `depth` 参数限制深度

## 常见问题
- **没有匹配结果**：检查路径、通配符或权限是否正确
- **执行缓慢**：路径过大或文件过多，考虑增加过滤条件
- **循环失败**：确保在 `register` 后引用 `result.files`

## 与其他模块关系
- **与 file 模块**：find 负责定位，file 负责后续删除或修改
- **与 synchronize 模块**：可先用 find 筛选文件，再批量同步
- **与 stat 模块**：find 返回的每个文件对象类似 stat 输出，可直接使用

## 相关链接
- [file 模块](../file/README.md)
- [synchronize 模块](../synchronize/README.md)
