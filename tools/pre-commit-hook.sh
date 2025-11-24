#!/bin/bash
# Pre-commit Hook 模板
# 用于 Git 提交前的自动检查
# 安装方法: cp tools/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -e

echo "🔍 运行 pre-commit 检查..."

# 获取所有待提交的文件
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo "✅ 没有文件需要检查"
    exit 0
fi

# 标记：是否有错误
HAS_ERROR=0

# 1. YAML 语法检查
echo ""
echo "📝 检查 YAML 语法..."
YAML_ERROR=0

for file in $STAGED_FILES; do
    if [[ "$file" =~ \.(yml|yaml)$ ]] && [ -f "$file" ]; then
        # 使用 Python PyYAML 检查语法
        if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            echo "  ❌ YAML 语法错误: $file"
            YAML_ERROR=1
            HAS_ERROR=1
        fi
    fi
done

if [ $YAML_ERROR -eq 0 ]; then
    echo "  ✓ YAML 语法检查通过"
fi

# 2. 检查硬编码密码
echo ""
echo "🔒 检查硬编码密码..."
PASSWORD_ERROR=0

for file in $STAGED_FILES; do
    if [[ "$file" =~ \.(yml|yaml)$ ]] && [ -f "$file" ]; then
        # 查找可疑的密码模式（排除常见占位符）
        SUSPICIOUS=$(grep -inE '(password|passwd|secret|token|api_key).*:.*["\047][a-zA-Z0-9!@#$%^&*()_+=\[\]{};:,.<>?/\\|-]{8,}["\047]' "$file" | \
                    grep -v -iE '(vault_|your_|example|placeholder|CHANGE|PLEASE|xxx|change_me|secure_password)' || true)
        
        if [ -n "$SUSPICIOUS" ]; then
            echo "  ❌ 可能存在硬编码密码: $file"
            echo "$SUSPICIOUS" | head -n 3
            PASSWORD_ERROR=1
            HAS_ERROR=1
        fi
    fi
done

if [ $PASSWORD_ERROR -eq 0 ]; then
    echo "  ✓ 未发现硬编码密码"
fi

# 3. 检查变量文件警告头
echo ""
echo "⚠️  检查变量文件警告头..."
WARNING_ERROR=0

for file in $STAGED_FILES; do
    if [[ "$file" =~ vars/example_vars\.yml$ ]] && [ -f "$file" ]; then
        if ! grep -q "⚠️" "$file"; then
            echo "  ❌ 变量文件缺少警告头: $file"
            echo "     请添加: # ⚠️ 警告：本文件仅为示例配置"
            WARNING_ERROR=1
            HAS_ERROR=1
        fi
    fi
done

if [ $WARNING_ERROR -eq 0 ]; then
    echo "  ✓ 变量文件警告头检查通过"
fi

# 4. 检查敏感操作的 no_log
echo ""
echo "🔐 检查 no_log 使用..."
NOLOG_WARNING=0

for file in $STAGED_FILES; do
    if [[ "$file" =~ playbook\.yml$ ]] && [ -f "$file" ]; then
        # 查找包含敏感信息但没有 no_log 的任务
        # 这是一个简化的检查，可能有误报
        LINE_NUM=1
        IN_TASK=0
        TASK_HAS_SENSITIVE=0
        TASK_HAS_NOLOG=0
        TASK_NAME=""
        
        while IFS= read -r line; do
            # 检测任务开始
            if echo "$line" | grep -qE '^[[:space:]]*-[[:space:]]*name:'; then
                # 如果前一个任务有敏感信息但没有 no_log，报告
                if [ $TASK_HAS_SENSITIVE -eq 1 ] && [ $TASK_HAS_NOLOG -eq 0 ]; then
                    echo "  ⚠️  建议为敏感任务添加 no_log: $file"
                    echo "     任务: $TASK_NAME"
                    NOLOG_WARNING=1
                fi
                
                # 重置标记
                IN_TASK=1
                TASK_HAS_SENSITIVE=0
                TASK_HAS_NOLOG=0
                TASK_NAME=$(echo "$line" | sed 's/^[[:space:]]*-[[:space:]]*name:[[:space:]]*//')
            fi
            
            # 检测敏感关键字
            if [ $IN_TASK -eq 1 ]; then
                if echo "$line" | grep -qiE '(password|passwd|secret|token|key|credential)'; then
                    TASK_HAS_SENSITIVE=1
                fi
                
                if echo "$line" | grep -qE 'no_log:[[:space:]]*(true|yes)'; then
                    TASK_HAS_NOLOG=1
                fi
            fi
            
            ((LINE_NUM++))
        done < "$file"
    fi
done

if [ $NOLOG_WARNING -eq 0 ]; then
    echo "  ✓ no_log 使用检查通过"
fi

# 5. 检查 FQCN 使用（仅警告）
echo ""
echo "📦 检查 FQCN 使用（建议）..."
FQCN_WARNING=0

for file in $STAGED_FILES; do
    if [[ "$file" =~ playbook\.yml$ ]] && [ -f "$file" ]; then
        # 查找常见的非 FQCN 模块调用
        NON_FQCN=$(grep -nE '^[[:space:]]+(copy|template|file|service|user|group|apt|yum|command|shell):' "$file" || true)
        
        if [ -n "$NON_FQCN" ]; then
            echo "  ℹ️  建议使用 FQCN: $file"
            echo "     (如 ansible.builtin.copy 代替 copy)"
            FQCN_WARNING=1
        fi
    fi
done

if [ $FQCN_WARNING -eq 0 ]; then
    echo "  ✓ FQCN 使用良好"
fi

# 总结
echo ""
echo "================================"

if [ $HAS_ERROR -eq 1 ]; then
    echo "❌ Pre-commit 检查失败！"
    echo ""
    echo "请修复上述错误后再次提交。"
    echo "如果确认这些错误可以忽略，使用 --no-verify 跳过检查："
    echo "  git commit --no-verify"
    echo ""
    exit 1
else
    if [ $NOLOG_WARNING -eq 1 ] || [ $FQCN_WARNING -eq 1 ]; then
        echo "⚠️  Pre-commit 检查通过（有警告）"
        echo ""
        echo "建议修复上述警告，或使用 --no-verify 跳过："
        echo "  git commit --no-verify"
        echo ""
        # 警告不阻止提交
        exit 0
    else
        echo "✅ Pre-commit 检查全部通过！"
        echo ""
        exit 0
    fi
fi
