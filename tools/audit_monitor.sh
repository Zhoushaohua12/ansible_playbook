#!/bin/bash
# 审计监控脚本 - Audit Monitoring Script
# 用于定期运行审计并跟踪质量趋势

set -e

PROJECT_ROOT="${1:-.}"
REPORT_DIR="$PROJECT_ROOT/reports/audit_history"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_ONLY=$(date +%Y%m%d)

# 创建报告目录
mkdir -p "$REPORT_DIR"

echo "📊 运行审计监控 ($TIMESTAMP)..."
echo "项目路径: $PROJECT_ROOT"
echo ""

# 运行完整审计
echo "🔍 执行全面审计..."
JSON_REPORT="$REPORT_DIR/audit_${TIMESTAMP}.json"
MD_REPORT="$REPORT_DIR/audit_${TIMESTAMP}.md"

cd "$PROJECT_ROOT"
venv/bin/python tools/comprehensive_audit.py \
    --output "$MD_REPORT" \
    --json "$JSON_REPORT"

# 提取关键指标
if [ -f "$JSON_REPORT" ]; then
    CRITICAL=$(python3 -c "import json; print(json.load(open('$JSON_REPORT'))['summary']['critical_issues'])")
    HIGH=$(python3 -c "import json; print(json.load(open('$JSON_REPORT'))['summary']['high_issues'])")
    MEDIUM=$(python3 -c "import json; print(json.load(open('$JSON_REPORT'))['summary']['medium_issues'])")
    LOW=$(python3 -c "import json; print(json.load(open('$JSON_REPORT'))['summary']['low_issues'])")
    TOTAL=$(python3 -c "import json; print(json.load(open('$JSON_REPORT'))['summary']['total_issues'])")
    
    echo ""
    echo "📈 当前审计结果:"
    echo "  🔴 Critical: $CRITICAL"
    echo "  🟠 High:     $HIGH"
    echo "  🟡 Medium:   $MEDIUM"
    echo "  🟢 Low:      $LOW"
    echo "  📝 Total:    $TOTAL"
    echo ""
    
    # 检查是否有历史数据
    LATEST_HISTORY="$REPORT_DIR/latest_metrics.txt"
    if [ -f "$LATEST_HISTORY" ]; then
        # 读取上次的数据
        source "$LATEST_HISTORY"
        
        echo "📊 与上次审计对比:"
        
        # 计算差异
        CRITICAL_DIFF=$((CRITICAL - PREV_CRITICAL))
        HIGH_DIFF=$((HIGH - PREV_HIGH))
        MEDIUM_DIFF=$((MEDIUM - PREV_MEDIUM))
        LOW_DIFF=$((LOW - PREV_LOW))
        TOTAL_DIFF=$((TOTAL - PREV_TOTAL))
        
        # 显示趋势
        show_trend() {
            local value=$1
            local label=$2
            if [ $value -lt 0 ]; then
                echo "  ✅ $label: $value (改善)"
            elif [ $value -gt 0 ]; then
                echo "  ⚠️  $label: +$value (增加)"
            else
                echo "  ➡️  $label: 无变化"
            fi
        }
        
        show_trend $CRITICAL_DIFF "Critical"
        show_trend $HIGH_DIFF "High"
        show_trend $MEDIUM_DIFF "Medium"
        show_trend $LOW_DIFF "Low"
        show_trend $TOTAL_DIFF "Total"
        echo ""
        
        # 生成趋势报告
        TREND_FILE="$REPORT_DIR/trend_${DATE_ONLY}.txt"
        cat >> "$TREND_FILE" << EOF
$TIMESTAMP,$CRITICAL,$HIGH,$MEDIUM,$LOW,$TOTAL
EOF
    fi
    
    # 保存当前指标
    cat > "$LATEST_HISTORY" << EOF
PREV_TIMESTAMP="$TIMESTAMP"
PREV_CRITICAL=$CRITICAL
PREV_HIGH=$HIGH
PREV_MEDIUM=$MEDIUM
PREV_LOW=$LOW
PREV_TOTAL=$TOTAL
EOF
    
    # 生成趋势图表数据（CSV 格式）
    TREND_CSV="$REPORT_DIR/audit_trend.csv"
    if [ ! -f "$TREND_CSV" ]; then
        echo "timestamp,critical,high,medium,low,total" > "$TREND_CSV"
    fi
    echo "$TIMESTAMP,$CRITICAL,$HIGH,$MEDIUM,$LOW,$TOTAL" >> "$TREND_CSV"
    
    # 检查是否需要告警
    echo "🚨 检查告警条件..."
    ALERT_TRIGGERED=0
    ALERT_MESSAGE=""
    
    if [ $CRITICAL -gt 0 ]; then
        ALERT_TRIGGERED=1
        ALERT_MESSAGE="${ALERT_MESSAGE}\n⚠️  发现 $CRITICAL 个严重问题！请立即处理！"
    fi
    
    if [ $HIGH -gt 50 ]; then
        ALERT_TRIGGERED=1
        ALERT_MESSAGE="${ALERT_MESSAGE}\n⚠️  High 级别问题超过 50 个（当前 $HIGH）"
    fi
    
    if [ -f "$LATEST_HISTORY" ] && [ $TOTAL_DIFF -gt 20 ]; then
        ALERT_TRIGGERED=1
        ALERT_MESSAGE="${ALERT_MESSAGE}\n⚠️  问题总数增加超过 20 个（+$TOTAL_DIFF）"
    fi
    
    if [ $ALERT_TRIGGERED -eq 1 ]; then
        echo ""
        echo "🚨 告警触发！"
        echo -e "$ALERT_MESSAGE"
        echo ""
        
        # 保存告警日志
        ALERT_LOG="$REPORT_DIR/alerts.log"
        echo "[$TIMESTAMP] ALERT TRIGGERED" >> "$ALERT_LOG"
        echo -e "$ALERT_MESSAGE" >> "$ALERT_LOG"
        echo "" >> "$ALERT_LOG"
        
        # 可以在这里集成通知系统（Slack、Email 等）
        # 示例：
        # if command -v mail &> /dev/null; then
        #     echo -e "审计告警\n$ALERT_MESSAGE\n\n查看详情: $MD_REPORT" | \
        #         mail -s "[Ansible Audit] 质量告警" admin@example.com
        # fi
        
        echo "告警已记录到: $ALERT_LOG"
    else
        echo "  ✅ 无告警触发"
    fi
    
    echo ""
    
    # 生成每日摘要
    DAILY_SUMMARY="$REPORT_DIR/daily_summary_${DATE_ONLY}.md"
    cat > "$DAILY_SUMMARY" << EOF
# 每日审计摘要 - $DATE_ONLY

## 最新审计 ($TIMESTAMP)

### 问题统计
- 🔴 Critical: $CRITICAL
- 🟠 High: $HIGH
- 🟡 Medium: $MEDIUM
- 🟢 Low: $LOW
- 📝 Total: $TOTAL

### 详细报告
- [JSON 报告]($JSON_REPORT)
- [Markdown 报告]($MD_REPORT)

### 质量评分
EOF
    
    # 计算质量评分（满分 100）
    QUALITY_SCORE=$((100 - CRITICAL * 5 - HIGH * 2 - MEDIUM * 1))
    if [ $QUALITY_SCORE -lt 0 ]; then
        QUALITY_SCORE=0
    fi
    
    echo "**${QUALITY_SCORE}/100**" >> "$DAILY_SUMMARY"
    echo "" >> "$DAILY_SUMMARY"
    
    if [ $QUALITY_SCORE -ge 90 ]; then
        echo "🏆 **优秀** - 代码质量优秀，继续保持！" >> "$DAILY_SUMMARY"
    elif [ $QUALITY_SCORE -ge 70 ]; then
        echo "✅ **良好** - 代码质量良好，还有提升空间。" >> "$DAILY_SUMMARY"
    elif [ $QUALITY_SCORE -ge 50 ]; then
        echo "⚠️  **需要改进** - 建议优先处理 Critical 和 High 问题。" >> "$DAILY_SUMMARY"
    else
        echo "🚨 **严重** - 存在大量问题，需要立即采取行动！" >> "$DAILY_SUMMARY"
    fi
    
    echo ""
    echo "📄 报告已生成:"
    echo "  - JSON: $JSON_REPORT"
    echo "  - Markdown: $MD_REPORT"
    echo "  - 每日摘要: $DAILY_SUMMARY"
    echo "  - 趋势数据: $TREND_CSV"
    
    # 清理旧报告（保留最近 30 天）
    echo ""
    echo "🧹 清理旧报告..."
    find "$REPORT_DIR" -name "audit_*.json" -mtime +30 -delete
    find "$REPORT_DIR" -name "audit_*.md" -mtime +30 -delete
    echo "  ✓ 已删除 30 天前的报告"
    
    echo ""
    echo "✅ 审计监控完成！"
    echo ""
    echo "质量评分: ${QUALITY_SCORE}/100"
    
    # 根据评分返回退出码
    if [ $CRITICAL -gt 0 ]; then
        exit 2  # 有严重问题
    elif [ $HIGH -gt 50 ]; then
        exit 1  # 有大量高优先级问题
    else
        exit 0  # 正常
    fi
else
    echo "❌ 审计失败：未生成报告文件"
    exit 1
fi
