# 审计工具使用指南 - Audit Tools Guide

本文档详细介绍 ansible_playbook 项目的所有审计和优化工具。

---

## 🎯 工具概览

| 工具 | 用途 | 运行频率 | 优先级 |
|------|------|----------|--------|
| **comprehensive_audit.py** | 全面项目审计 | 每周/重大变更后 | ⭐⭐⭐⭐⭐ |
| **quick_fix.sh** | 自动修复常见问题 | 按需/审计后 | ⭐⭐⭐⭐ |
| **audit_monitor.sh** | 监控质量趋势 | 每日/CI中 | ⭐⭐⭐⭐ |
| **pre-commit-hook.sh** | 提交前检查 | 每次提交 | ⭐⭐⭐⭐⭐ |
| **audit_report.py** | 基础审计 | 按需 | ⭐⭐⭐ |
| **module_index.py** | 模块索引管理 | 模块变更后 | ⭐⭐⭐ |
| **module_diff.py** | 模块覆盖分析 | 按需 | ⭐⭐⭐ |

---

## 📦 工具详解

### 1. comprehensive_audit.py - 全面审计工具

**最全面的项目检查工具**，覆盖8大维度。

#### 功能

- ✅ **项目结构完整性**：检查所有模块分类、必需文件
- ✅ **文件内容质量**：YAML 语法、FQCN、gather_facts、中文命名
- ✅ **安全性检查**：硬编码密钥、no_log、变量文件警告
- ✅ **测试覆盖**：检查测试文件是否完整
- ✅ **元数据一致性**：验证 metadata/modules.yaml
- ✅ **文档导航**：README 完整性、导航链接
- ✅ **依赖管理**：requirements.txt、collections
- ✅ **冗余检测**：重复模块、重复 handler

#### 使用方法

```bash
# 基础用法
venv/bin/python tools/comprehensive_audit.py

# 自定义输出
venv/bin/python tools/comprehensive_audit.py \
  --output reports/my_audit.md \
  --json reports/my_audit.json

# 指定项目路径
venv/bin/python tools/comprehensive_audit.py \
  --project-root /path/to/project
```

#### 输出文件

- **reports/comprehensive_audit.md** - 详细的 Markdown 报告
- **reports/comprehensive_audit.json** - 机器可读的 JSON 数据

#### 报告结构

```
# 全面审计报告

## 执行摘要
- 问题统计（Critical/High/Medium/Low）

## 统计信息
- 项目规模
- 代码质量指标
- 安全性指标
- 元数据与依赖

## 详细问题列表
- 按优先级分类的所有问题
- 每个问题的修复建议

## 优化建议
- 立即处理
- 高优先级
- 中等优先级
- 低优先级

## 最佳实践总结
- 文件结构规范
- Playbook 规范
- 安全规范
- 文档规范
- 测试与元数据

## 下一步行动计划
- 短期目标
- 中期目标
- 长期目标
```

#### 退出码

- **0** - 无 Critical 问题
- **1** - 存在 Critical 问题

#### 使用场景

- ✅ 新功能开发完成后
- ✅ 重大重构后
- ✅ 发布前检查
- ✅ 每周质量检查
- ✅ 代码审查前

---

### 2. quick_fix.sh - 快速修复工具

**自动修复常见问题**，节省手动修改时间。

#### 功能

- 🔧 自动修复 YAML 变量引用格式错误
- 🔧 批量添加变量文件警告头
- 🔍 检查缺少 gather_facts 的 playbook
- 🔍 扫描潜在的硬编码密码

#### 使用方法

```bash
# 在项目根目录运行
./tools/quick_fix.sh

# 指定项目路径
./tools/quick_fix.sh /path/to/project
```

#### 安全特性

- ✅ **自动备份**：修改前备份所有文件到 `.audit_backup_*` 目录
- ✅ **可回滚**：提供回滚命令恢复原状
- ✅ **详细日志**：记录所有修改操作

#### 输出文件

- **reports/quick_fix_report.txt** - 修复操作报告
- **.audit_backup_YYYYMMDD_HHMMSS/** - 备份目录

#### 修复示例

**问题**：YAML 变量引用格式错误
```yaml
# 修复前
memory: {{ vm_memory }}

# 修复后
memory: "{{ vm_memory }}"
```

**问题**：缺少变量文件警告头
```yaml
# 修复前
---
db_host: localhost

# 修复后
# ⚠️ 警告：本文件仅为示例配置
# ⚠️ 占位符必须使用 Ansible Vault 或环境变量替换
# ⚠️ 请勿在生产环境中直接使用这些示例值

db_host: localhost
```

#### 注意事项

⚠️ 修复后请务必：
1. 运行语法检查：`ansible-playbook --syntax-check`
2. 重新审计：`venv/bin/python tools/comprehensive_audit.py`
3. 手动检查修改的文件
4. 运行测试：`pytest tests/`

---

### 3. audit_monitor.sh - 审计监控工具

**持续监控代码质量**，跟踪改进趋势。

#### 功能

- 📊 自动运行全面审计
- 📈 记录历史数据
- 🔔 触发质量告警
- 📉 生成趋势图表
- 🏆 计算质量评分

#### 使用方法

```bash
# 运行单次监控
./tools/audit_monitor.sh

# 指定项目路径
./tools/audit_monitor.sh /path/to/project

# 添加到 crontab（每天早上9点）
0 9 * * * cd /path/to/project && ./tools/audit_monitor.sh >> /var/log/audit_monitor.log 2>&1
```

#### 输出文件

- **reports/audit_history/audit_TIMESTAMP.json** - 历史审计数据
- **reports/audit_history/audit_TIMESTAMP.md** - 历史审计报告
- **reports/audit_history/audit_trend.csv** - CSV 格式趋势数据
- **reports/audit_history/daily_summary_DATE.md** - 每日摘要
- **reports/audit_history/latest_metrics.txt** - 最新指标
- **reports/audit_history/alerts.log** - 告警日志

#### 质量评分算法

```
质量评分 = 100 - (Critical × 5) - (High × 2) - (Medium × 1)
最低分 = 0
最高分 = 100

评级：
- 90-100: 优秀 🏆
- 70-89:  良好 ✅
- 50-69:  需要改进 ⚠️
- 0-49:   严重 🚨
```

#### 告警条件

- 🚨 存在 Critical 问题
- 🚨 High 问题 > 50 个
- 🚨 问题总数增加 > 20 个

#### 趋势分析

CSV 格式数据可以导入到：
- Excel/Google Sheets 生成图表
- Grafana 可视化监控
- 自定义脚本分析

示例 CSV：
```csv
timestamp,critical,high,medium,low,total
20251124_091530,53,116,215,878,1262
20251124_101530,48,110,200,850,1208
```

#### 退出码

- **0** - 正常（无 Critical，High < 50）
- **1** - 有大量 High 问题
- **2** - 有 Critical 问题

---

### 4. pre-commit-hook.sh - Pre-commit Hook

**在提交前自动检查**，防止低质量代码进入仓库。

#### 功能

- ✅ YAML 语法验证
- ✅ 硬编码密码检测
- ✅ 变量文件警告头检查
- ⚠️ no_log 使用建议
- ℹ️ FQCN 使用建议

#### 安装方法

```bash
# 复制到 Git hooks 目录
cp tools/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 验证安装
ls -l .git/hooks/pre-commit
```

#### 使用效果

```bash
$ git commit -m "添加新模块"

🔍 运行 pre-commit 检查...

📝 检查 YAML 语法...
  ✓ YAML 语法检查通过

🔒 检查硬编码密码...
  ✓ 未发现硬编码密码

⚠️  检查变量文件警告头...
  ❌ 变量文件缺少警告头: system/newmodule/vars/example_vars.yml
     请添加: # ⚠️ 警告：本文件仅为示例配置

================================
❌ Pre-commit 检查失败！

请修复上述错误后再次提交。
如果确认这些错误可以忽略，使用 --no-verify 跳过检查：
  git commit --no-verify
```

#### 跳过检查

有时需要临时跳过检查：

```bash
# 跳过 pre-commit 检查
git commit --no-verify -m "your message"

# 或设置环境变量
SKIP_PRECOMMIT=1 git commit -m "your message"
```

⚠️ **注意**：不建议频繁跳过检查，应修复问题后再提交。

#### 自定义检查

编辑 `.git/hooks/pre-commit` 文件可以：
- 添加自定义检查规则
- 调整检查严格程度
- 集成其他工具（如 pylint、yamllint）

---

### 5. audit_report.py - 基础审计工具

**原有的审计工具**，提供基础的代码风格和文档检查。

#### 功能

- 代码风格检查
- 安全性基础检查
- 文档规范检查
- 测试覆盖统计

#### 使用方法

```bash
# 基础用法
venv/bin/python tools/audit_report.py

# 自定义输出
venv/bin/python tools/audit_report.py --output reports/basic_audit.md

# JSON 格式
venv/bin/python tools/audit_report.py --json reports/audit_data.json

# 跳过测试
venv/bin/python tools/audit_report.py --skip-tests
```

#### 与 comprehensive_audit.py 的区别

| 特性 | audit_report.py | comprehensive_audit.py |
|------|----------------|----------------------|
| 检查维度 | 4个 | 8个 |
| 问题分级 | 简单 | 详细（4个优先级） |
| 修复建议 | 基础 | 详细且可操作 |
| 统计信息 | 基本 | 全面 |
| 元数据检查 | 无 | 有 |
| 冗余检测 | 无 | 有 |

**建议**：使用 `comprehensive_audit.py` 替代此工具。

---

### 6. module_index.py - 模块索引管理

**管理模块元数据和索引**。

#### 功能

- 生成 metadata/modules.yaml
- 生成 docs/MODULE_INDEX.md
- 生成 reports/module_index.json
- 生成模块对比报告
- 查询模块信息
- 生成学习路径

#### 使用方法

```bash
# 生成所有索引
venv/bin/python tools/module_index.py --generate --comparison-report

# 查询模块
venv/bin/python tools/module_index.py --query copy

# 查看学习路径
venv/bin/python tools/module_index.py --learning-path
```

详细用法参考项目 README。

---

### 7. module_diff.py - 模块覆盖分析

**分析模块覆盖情况**，识别缺失的模块。

#### 功能

- 执行 ansible-doc -l 获取官方模块列表
- 对比项目已有模块
- 按优先级分类缺失模块
- 生成统计报告

#### 使用方法

```bash
# 运行分析
venv/bin/python tools/module_diff.py

# 刷新缓存
venv/bin/python tools/module_diff.py --refresh-cache

# 按优先级过滤
venv/bin/python tools/module_diff.py --priority P1

# 仅显示摘要
venv/bin/python tools/module_diff.py --summary
```

详细用法参考项目 README。

---

## 🚀 推荐工作流

### 日常开发

```bash
# 1. 开发前：安装 pre-commit hook
cp tools/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 2. 开发中：随时运行快速检查
ansible-playbook playbook.yml --syntax-check
pytest tests/

# 3. 开发后：提交前自动检查
git add .
git commit -m "添加新功能"  # 自动运行 pre-commit

# 4. 提交后：如果有问题，快速修复
./tools/quick_fix.sh
git add .
git commit -m "修复审计问题"
```

### 每周检查

```bash
# 运行全面审计
venv/bin/python tools/comprehensive_audit.py

# 查看报告
cat reports/comprehensive_audit.md

# 根据优先级修复问题
# 1. 先修复 Critical
# 2. 再修复 High
# 3. 逐步处理 Medium 和 Low
```

### 发布前

```bash
# 1. 完整审计
venv/bin/python tools/comprehensive_audit.py

# 2. 确保无 Critical 和 High 问题
# 如果有，必须修复

# 3. 更新元数据
venv/bin/python tools/module_index.py --generate --comparison-report

# 4. 运行完整测试
pytest tests/ -v

# 5. 语法检查
find . -name "playbook.yml" -exec ansible-playbook --syntax-check {} \;

# 6. 标记版本
git tag -a v1.0.0 -m "Release v1.0.0"
```

### CI/CD 集成

```yaml
# .github/workflows/audit.yml
name: Quality Audit

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m venv venv
          venv/bin/pip install -r requirements.txt
      
      - name: Run comprehensive audit
        run: |
          venv/bin/python tools/comprehensive_audit.py
      
      - name: Check for critical issues
        run: |
          CRITICAL=$(python3 -c "import json; print(json.load(open('reports/comprehensive_audit.json'))['summary']['critical_issues'])")
          if [ "$CRITICAL" -gt 0 ]; then
            echo "❌ Found $CRITICAL critical issues"
            exit 1
          fi
      
      - name: Upload audit report
        uses: actions/upload-artifact@v2
        with:
          name: audit-report
          path: reports/comprehensive_audit.md
```

---

## 📊 监控仪表板示例

如果你使用 Grafana 等监控工具，可以用 audit_trend.csv 数据创建仪表板：

### 指标面板

1. **问题趋势图**
   - X 轴：时间
   - Y 轴：问题数量
   - 系列：Critical, High, Medium, Low

2. **质量评分**
   - 当前评分（0-100）
   - 目标线（如 90 分）

3. **告警统计**
   - 本周告警次数
   - 告警类型分布

4. **修复进度**
   - 已修复问题数
   - 待修复问题数
   - 修复速率

---

## 🎓 最佳实践

### 1. 定期审计

```bash
# 每周一运行
0 9 * * 1 cd /path/to/project && ./tools/audit_monitor.sh

# 查看趋势
weekly_report.sh  # 自定义脚本
```

### 2. 团队协作

- 新成员加入时：阅读 `docs/BEST_PRACTICES.md`
- Code Review 时：参考 `COMPREHENSIVE_AUDIT_SUMMARY.md`
- 发现新问题：更新审计工具和最佳实践文档

### 3. 持续改进

- 记录常见问题和解决方案
- 定期更新 pre-commit hook 规则
- 根据审计结果调整开发流程

### 4. 文档同步

- 修改代码规范时，同步更新文档
- 添加新工具时，更新本指南
- 发现新的最佳实践，及时分享

---

## 🔧 故障排查

### 问题：审计工具运行缓慢

**原因**：大量文件需要检查

**解决**：
```bash
# 排除不需要检查的目录
# 编辑 comprehensive_audit.py
# 在 check_* 方法中添加过滤条件
if 'venv' in str(path) or '.git' in str(path):
    continue
```

### 问题：quick_fix.sh 修改错误

**原因**：正则表达式匹配不准确

**解决**：
```bash
# 1. 从备份恢复
backup_dir=".audit_backup_YYYYMMDD_HHMMSS"
find "$backup_dir" -type f | while read f; do
    rel="${f#$backup_dir/}"
    cp "$f" "$rel"
done

# 2. 手动修复问题文件
# 3. 报告问题给维护者
```

### 问题：pre-commit hook 太严格

**原因**：某些警告不应阻止提交

**解决**：
```bash
# 编辑 .git/hooks/pre-commit
# 将某些检查从错误改为警告
# 或使用 --no-verify 临时跳过
git commit --no-verify -m "message"
```

---

## 📚 相关文档

- **[COMPREHENSIVE_AUDIT_SUMMARY.md](COMPREHENSIVE_AUDIT_SUMMARY.md)** - 全面审计总结报告
- **[docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md)** - 最佳实践指南
- **[AUDIT_REPORT.md](AUDIT_REPORT.md)** - 原审计报告
- **[README.md](README.md)** - 项目主文档

---

**最后更新**: 2025-11-24  
**维护者**: Ansible Playbook 团队  
**问题反馈**: 请创建 Issue 或联系维护者
