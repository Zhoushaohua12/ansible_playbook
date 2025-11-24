#!/bin/bash
# 快速修复脚本 - Quick Fix Script
# 自动修复审计中发现的常见问题

set -e

PROJECT_ROOT="${1:-.}"

echo "🔧 开始快速修复 ansible_playbook 项目..."
echo "项目路径: $PROJECT_ROOT"
echo ""

# 创建备份目录
BACKUP_DIR="$PROJECT_ROOT/.audit_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📦 备份目录: $BACKUP_DIR"
echo ""

# 1. 修复 YAML 变量引用（不加引号会导致语法错误）
echo "📝 修复 YAML 变量引用..."
FIXED_COUNT=0

find "$PROJECT_ROOT" -name "playbook.yml" -type f | while read file; do
    # 跳过 venv 和 .git
    if [[ "$file" == *"venv"* ]] || [[ "$file" == *".git"* ]]; then
        continue
    fi
    
    # 备份
    rel_path="${file#$PROJECT_ROOT/}"
    backup_file="$BACKUP_DIR/$rel_path"
    mkdir -p "$(dirname "$backup_file")"
    cp "$file" "$backup_file"
    
    # 检查是否有未加引号的变量引用
    # 匹配模式: ": {{ var }}" 但不是 "": {{ var }}"
    if grep -qE '^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*:[[:space:]]*\{\{' "$file"; then
        # 修复：在变量引用外添加引号
        # 注意：这是简化的修复，可能需要手动验证
        sed -i -E 's/^([[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*:[[:space:]]*)(\{\{[^}]+\}\})/\1"\2"/g' "$file"
        echo "  ✓ 已修复: $rel_path"
        ((FIXED_COUNT++))
    fi
done

echo "  修复了 $FIXED_COUNT 个文件的变量引用"
echo ""

# 2. 添加变量文件警告头
echo "⚠️  添加变量文件警告头..."
WARNING_COUNT=0

find "$PROJECT_ROOT" -path "*/vars/example_vars.yml" -type f | while read file; do
    # 跳过 venv 和 .git
    if [[ "$file" == *"venv"* ]] || [[ "$file" == *".git"* ]]; then
        continue
    fi
    
    if ! grep -q "⚠️" "$file"; then
        # 备份
        rel_path="${file#$PROJECT_ROOT/}"
        backup_file="$BACKUP_DIR/$rel_path"
        mkdir -p "$(dirname "$backup_file")"
        cp "$file" "$backup_file"
        
        # 添加警告头
        temp=$(mktemp)
        cat > "$temp" << 'EOF'
# ⚠️ 警告：本文件仅为示例配置
# ⚠️ 占位符必须使用 Ansible Vault 或环境变量替换
# ⚠️ 请勿在生产环境中直接使用这些示例值

EOF
        # 如果文件已有 --- 分隔符，保留它，否则添加
        if head -n 1 "$file" | grep -q "^---"; then
            tail -n +2 "$file" >> "$temp"
        else
            cat "$file" >> "$temp"
        fi
        
        mv "$temp" "$file"
        echo "  ✓ 已添加: $rel_path"
        ((WARNING_COUNT++))
    fi
done

echo "  为 $WARNING_COUNT 个文件添加了警告头"
echo ""

# 3. 检查 gather_facts 声明（仅报告，不自动修复）
echo "📋 检查 gather_facts 声明..."
MISSING_GATHER_FACTS=()

find "$PROJECT_ROOT" -name "playbook.yml" -type f | while read file; do
    # 跳过 venv 和 .git
    if [[ "$file" == *"venv"* ]] || [[ "$file" == *".git"* ]]; then
        continue
    fi
    
    if ! grep -q "gather_facts:" "$file"; then
        rel_path="${file#$PROJECT_ROOT/}"
        echo "  ⚠️  缺少 gather_facts: $rel_path"
    fi
done
echo ""

# 4. 检查硬编码密码（仅报告）
echo "🔒 检查硬编码密码（示例密码除外）..."
HARDCODED_COUNT=0

find "$PROJECT_ROOT" -type f \( -name "*.yml" -o -name "*.yaml" \) | while read file; do
    # 跳过 venv、.git 和备份
    if [[ "$file" == *"venv"* ]] || [[ "$file" == *".git"* ]] || [[ "$file" == *".audit_backup"* ]]; then
        continue
    fi
    
    # 查找可疑的密码模式（排除常见占位符）
    if grep -iE '(password|passwd|secret|token).*:.*["\047]' "$file" | \
       grep -v -iE '(vault_|your_|example|placeholder|CHANGE|xxx|secure_password|change_me)' | \
       grep -v "⚠️" | grep -v "警告" > /dev/null 2>&1; then
        rel_path="${file#$PROJECT_ROOT/}"
        echo "  ⚠️  可能存在硬编码: $rel_path"
        ((HARDCODED_COUNT++))
    fi
done

if [ $HARDCODED_COUNT -eq 0 ]; then
    echo "  ✓ 未发现明显的硬编码密码"
fi
echo ""

# 5. 生成修复报告
echo "📊 生成修复报告..."
REPORT_FILE="$PROJECT_ROOT/reports/quick_fix_report.txt"
mkdir -p "$(dirname "$REPORT_FILE")"

cat > "$REPORT_FILE" << EOF
快速修复报告
=============
执行时间: $(date)
项目路径: $PROJECT_ROOT
备份路径: $BACKUP_DIR

修复统计:
---------
- YAML 变量引用修复: 已处理
- 变量文件警告头: 已处理
- gather_facts 检查: 已报告（需手动修复）
- 硬编码密码检查: 已报告（需手动修复）

备份说明:
---------
所有被修改的文件都已备份到: $BACKUP_DIR
如需回滚，请运行:
  find $BACKUP_DIR -type f | while read f; do
    rel=\${f#$BACKUP_DIR/}
    cp "\$f" "$PROJECT_ROOT/\$rel"
  done

下一步:
-------
1. 运行语法检查: find . -name "playbook.yml" -exec ansible-playbook --syntax-check {} \;
2. 重新运行审计: venv/bin/python tools/comprehensive_audit.py
3. 手动检查需要 gather_facts 的 playbook
4. 使用 Ansible Vault 加密硬编码密码

EOF

echo "✅ 快速修复完成！"
echo ""
echo "📄 详细报告: $REPORT_FILE"
echo "📦 备份位置: $BACKUP_DIR"
echo ""
echo "🔍 建议运行完整审计验证修复效果:"
echo "   venv/bin/python tools/comprehensive_audit.py"
