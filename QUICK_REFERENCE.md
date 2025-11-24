# 快速参考 - Quick Reference Card

一页纸快速参考，方便日常使用。

---

## 🚀 常用命令

### 审计检查

```bash
# 全面审计
venv/bin/python tools/comprehensive_audit.py

# 快速修复
./tools/quick_fix.sh

# 审计监控
./tools/audit_monitor.sh
```

### 开发流程

```bash
# 1. 安装 pre-commit hook（首次）
cp tools/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 2. 开发完成后检查
ansible-playbook playbook.yml --syntax-check
pytest tests/

# 3. 提交代码（自动检查）
git add .
git commit -m "your message"

# 4. 如果审计发现问题
./tools/quick_fix.sh
git add .
git commit -m "修复审计问题"
```

### 查看报告

```bash
# 查看审计报告
cat reports/comprehensive_audit.md
less reports/comprehensive_audit.json

# 查看趋势
cat reports/audit_history/audit_trend.csv

# 查看每日摘要
cat reports/audit_history/daily_summary_*.md
```

---

## 📋 问题优先级

| 优先级 | 处理时间 | 典型问题 |
|--------|---------|---------|
| 🔴 Critical | 立即 | YAML 错误、硬编码密钥 |
| 🟠 High | 1周内 | no_log 缺失、警告头缺失 |
| 🟡 Medium | 1月内 | gather_facts、测试缺失 |
| 🟢 Low | 持续 | FQCN、文档改进 |

---

## ✅ 代码规范速查

### Playbook 结构

```yaml
---
- name: 功能描述（中文）
  hosts: all
  gather_facts: true  # 必须声明
  become: true
  
  vars_files:
    - vars/example_vars.yml
  
  tasks:
    - name: 任务描述（中文）
      ansible.builtin.copy:  # 使用 FQCN
        src: "{{ source }}"  # 变量用引号
        dest: "{{ dest }}"
      no_log: true  # 敏感操作
      tags:
        - config
```

### 变量文件

```yaml
# ⚠️ 警告：本文件仅为示例配置
# ⚠️ 占位符必须使用 Ansible Vault 或环境变量替换
# ⚠️ 请勿在生产环境中直接使用这些示例值
---
db_password: "{{ vault_db_password }}"  # vault_ 前缀
```

### 常见 FQCN

```yaml
ansible.builtin.copy
ansible.builtin.template
ansible.builtin.service
ansible.builtin.user
ansible.builtin.file
```

---

## 🔒 安全检查清单

- [ ] 敏感信息使用 `vault_` 前缀
- [ ] 敏感任务使用 `no_log: true`
- [ ] 变量文件包含警告头
- [ ] 无硬编码密码
- [ ] 配置文件权限正确（0600/0640）

---

## 📚 文档索引

| 文档 | 用途 |
|------|------|
| [README.md](README.md) | 项目总览 |
| [BEST_PRACTICES.md](docs/BEST_PRACTICES.md) | 编码规范 |
| [AUDIT_TOOLS_GUIDE.md](AUDIT_TOOLS_GUIDE.md) | 工具使用 |
| [COMPREHENSIVE_AUDIT_SUMMARY.md](COMPREHENSIVE_AUDIT_SUMMARY.md) | 审计总结 |
| [AUDIT_COMPLETION_SUMMARY.md](AUDIT_COMPLETION_SUMMARY.md) | 完成报告 |

---

## 🛠️ 故障排查

### Pre-commit 失败

```bash
# 查看错误信息，修复后重新提交
# 或临时跳过
git commit --no-verify -m "message"
```

### YAML 语法错误

```bash
# 使用 Python 检查
python -c "import yaml; yaml.safe_load(open('file.yml'))"

# 使用 Ansible 检查
ansible-playbook file.yml --syntax-check
```

### 快速修复出错

```bash
# 从备份恢复
backup_dir=".audit_backup_YYYYMMDD_HHMMSS"
find "$backup_dir" -type f | while read f; do
    rel="${f#$backup_dir/}"
    cp "$f" "$rel"
done
```

---

## 📊 质量指标

当前状态：
- Critical: 53
- High: 116
- Medium: 215
- Low: 878

目标（1个月）：
- Critical: 0
- High: < 10
- Medium: < 50
- Low: < 500

---

## 💡 提示

- 📝 修改代码前先查 [BEST_PRACTICES.md](docs/BEST_PRACTICES.md)
- 🔍 提交前运行 `ansible-playbook --syntax-check`
- ✅ 每周运行 `audit_monitor.sh` 检查趋势
- 📖 遇到问题查 [AUDIT_TOOLS_GUIDE.md](AUDIT_TOOLS_GUIDE.md)
- 🚨 Critical 问题必须立即修复

---

**打印此页以便随时查看！**
