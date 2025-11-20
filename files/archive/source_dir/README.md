# 待归档项目说明文档

## 项目概述
这是一个用于演示 Ansible archive 模块功能的示例项目。项目包含多种类型的文件和目录，用于展示完整的归档操作流程。

## 目录结构
```
source_dir/
├── index.html          # 主页面文件
├── README.md           # 项目说明文档（本文件）
├── config/             # 配置文件目录
│   ├── app.conf        # 应用配置
│   └── database.ini    # 数据库配置
├── logs/               # 日志文件目录
│   ├── app.log         # 应用日志
│   └── error.log       # 错误日志
├── temp/               # 临时文件目录（归档时排除）
│   ├── cache.tmp       # 缓存文件
│   └── upload.tmp      # 上传临时文件
└── assets/             # 资源文件目录
    ├── style.css       # 样式文件
    └── script.js       # 脚本文件
```

## 归档演示功能

### 1. 基础归档
将整个目录打包为 tar.gz 格式的压缩包。

### 2. 排除文件归档
使用 `exclude_path` 参数排除临时文件和目录。

### 3. 格式选择
支持多种归档格式：tar、tar.gz、tar.bz2、zip。

### 4. 安全选项
演示 `remove` 参数的安全使用和注意事项。

## 使用场景

### 应用部署前打包
```bash
# 将应用代码打包准备部署
ansible-playbook archive_playbook.yml
```

### 配置备份
```bash
# 定期备份配置文件
ansible-playbook backup_playbook.yml
```

### 日志归档
```bash
# 将历史日志打包归档
ansible-playbook log_archive_playbook.yml
```

## 安全注意事项

1. **敏感信息保护**：归档前请确保没有包含敏感信息（密码、密钥等）
2. **权限控制**：设置适当的文件权限保护归档文件
3. **删除确认**：使用 `remove: true` 前请确认源文件可以安全删除
4. **磁盘空间**：确保有足够的磁盘空间存储归档文件
5. **路径安全**：避免相对路径和符号链接导致的安全问题

## 最佳实践

1. **版本控制**：在文件名中包含版本号或时间戳
2. **校验机制**：归档后生成校验和验证完整性
3. **分类存储**：按类型或日期分类存储归档文件
4. **定期清理**：定期清理过期的归档文件
5. **监控告警**：设置归档操作的监控和告警

## 相关模块

- [unarchive 模块](../unarchive/README.md) - 解压缩文件
- [copy 模块](../copy/README.md) - 文件复制
- [fetch 模块](../fetch/README.md) - 文件获取
- [synchronize 模块](../synchronize/README.md) - 目录同步

## 技术信息

- **创建时间**: 2024-01-15T10:30:00+08:00
- **用途**: Ansible archive 模块演示
- **支持格式**: tar, tar.gz, tar.bz2, zip
- **依赖工具**: tar, gzip, bzip2, zip

---

*此文档由 Ansible 自动化生成和归档* 🤖