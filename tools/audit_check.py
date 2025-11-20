#!/usr/bin/env python3
"""
审计检查工具 - 自动扫描 Ansible Playbook 仓库合规性

遍历所有 playbook.yml、README.md、vars/example_vars.yml 和 metadata/modules.yaml，
收集并报告关键规范项的符合情况，用于生成 AUDIT_REPORT.md 的统计数据。

使用方法：
    python3 tools/audit_check.py

输出：
    - 控制台输出统计摘要
    - JSON 格式详细报告（可选）
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class AuditChecker:
    """审计检查器主类"""
    
    def __init__(self, project_root: str = "."):
        self.root = Path(project_root)
        self.results = {
            "playbooks": [],
            "vars_files": [],
            "readmes": [],
            "metadata_issues": [],
            "statistics": defaultdict(int)
        }
        
    def run(self):
        """执行完整审计"""
        print("🔍 开始审计检查...")
        print(f"📁 项目根目录: {self.root.absolute()}\n")
        
        self.check_playbooks()
        self.check_vars_files()
        self.check_readmes()
        self.check_metadata_consistency()
        
        self.print_summary()
        
    def check_playbooks(self):
        """检查所有 playbook.yml 文件"""
        print("📋 检查 Playbook 文件...")
        
        playbooks = list(self.root.glob("**/playbook.yml"))
        self.results["statistics"]["total_playbooks"] = len(playbooks)
        
        for playbook_path in playbooks:
            issues = []
            
            try:
                with open(playbook_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查 YAML 可解析性
                try:
                    data = yaml.safe_load(content)
                except yaml.YAMLError as e:
                    issues.append(f"YAML 解析错误: {e}")
                    data = None
                
                if data:
                    # 检查 gather_facts 声明
                    has_gather_facts = self._check_gather_facts(data, content)
                    if not has_gather_facts:
                        issues.append("缺少 gather_facts 声明")
                        self.results["statistics"]["missing_gather_facts"] += 1
                        
                    # 检查 become 声明
                    has_become = self._check_become(data, content)
                    
                    # 检查 vars_files 声明
                    has_vars_files = self._check_vars_files(data, content)
                    
                    # 检查 check_mode 使用
                    has_check_mode = self._check_check_mode(content)
                    if has_check_mode:
                        self.results["statistics"]["with_check_mode"] += 1
                    
                    # 检查 no_log 使用
                    has_no_log = self._check_no_log(content)
                    
                    # 检查中文名称
                    chinese_names = self._check_chinese_names(data)
                    if not chinese_names["play_names_ok"]:
                        issues.append("Play 名称未使用中文")
                    if not chinese_names["task_names_ok"]:
                        issues.append("部分任务名称未使用中文")
                    if not chinese_names["handler_names_ok"]:
                        issues.append("Handler 名称未使用中文")
                        self.results["statistics"]["handler_not_chinese"] += 1
                    
                    # 检查 FQCN 使用
                    fqcn_issues = self._check_fqcn(data, content)
                    if fqcn_issues:
                        issues.extend(fqcn_issues)
                
                if issues:
                    rel_path = playbook_path.relative_to(self.root)
                    self.results["playbooks"].append({
                        "path": str(rel_path),
                        "issues": issues
                    })
                    
            except Exception as e:
                rel_path = playbook_path.relative_to(self.root)
                self.results["playbooks"].append({
                    "path": str(rel_path),
                    "issues": [f"读取错误: {e}"]
                })
        
        print(f"  ✓ 检查了 {len(playbooks)} 个 playbook 文件\n")
    
    def check_vars_files(self):
        """检查所有 vars/example_vars.yml 文件"""
        print("📦 检查变量文件...")
        
        vars_files = list(self.root.glob("**/vars/example_vars.yml"))
        self.results["statistics"]["total_vars_files"] = len(vars_files)
        
        for vars_path in vars_files:
            issues = []
            
            try:
                with open(vars_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查 ⚠️ 警告标识
                has_warning = bool(re.search(r'#\s*⚠️', content[:500]))
                if not has_warning:
                    issues.append("缺少 ⚠️ 警告标识")
                    self.results["statistics"]["missing_warning"] += 1
                
                # 检查是否有敏感信息硬编码
                if self._has_hardcoded_secrets(content):
                    issues.append("可能存在硬编码敏感信息")
                    
            except Exception as e:
                issues.append(f"读取错误: {e}")
            
            if issues:
                rel_path = vars_path.relative_to(self.root)
                self.results["vars_files"].append({
                    "path": str(rel_path),
                    "issues": issues
                })
        
        print(f"  ✓ 检查了 {len(vars_files)} 个变量文件\n")
    
    def check_readmes(self):
        """检查所有 README.md 文件的中文完整性"""
        print("📖 检查 README 文件...")
        
        readmes = [p for p in self.root.glob("**/README.md") 
                   if not any(x in p.parts for x in ['.git', 'venv', 'node_modules'])]
        self.results["statistics"]["total_readmes"] = len(readmes)
        
        for readme_path in readmes:
            issues = []
            
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含实质性中文内容
                chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
                if chinese_chars < 100:  # 少于 100 个中文字符视为不完整
                    issues.append("中文内容不足")
                    self.results["statistics"]["readme_insufficient_chinese"] += 1
                    
            except Exception as e:
                issues.append(f"读取错误: {e}")
            
            if issues:
                rel_path = readme_path.relative_to(self.root)
                self.results["readmes"].append({
                    "path": str(rel_path),
                    "issues": issues
                })
        
        print(f"  ✓ 检查了 {len(readmes)} 个 README 文件\n")
    
    def check_metadata_consistency(self):
        """检查 metadata/modules.yaml 与目录结构的一致性"""
        print("🗂️  检查元数据一致性...")
        
        metadata_path = self.root / "metadata" / "modules.yaml"
        if not metadata_path.exists():
            self.results["metadata_issues"].append("metadata/modules.yaml 不存在")
            print("  ⚠️  metadata/modules.yaml 不存在\n")
            return
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = yaml.safe_load(f)
            
            # 收集元数据中的所有模块
            metadata_modules = set()
            for category, data in metadata.items():
                if isinstance(data, dict) and 'topics' in data:
                    for topic in data['topics']:
                        if 'id' in topic:
                            metadata_modules.add(f"{category}/{topic['id']}")
            
            # 收集实际目录中的模块
            actual_modules = set()
            for playbook_path in self.root.glob("**/playbook.yml"):
                rel_path = playbook_path.relative_to(self.root)
                if len(rel_path.parts) >= 2:
                    module_path = f"{rel_path.parts[0]}/{rel_path.parts[1]}"
                    # 排除测试目录
                    if not module_path.startswith("tests/"):
                        actual_modules.add(module_path)
            
            # 比较差异
            missing_in_metadata = actual_modules - metadata_modules
            missing_in_dirs = metadata_modules - actual_modules
            
            if missing_in_metadata:
                self.results["metadata_issues"].append(
                    f"目录中存在但元数据中缺失: {sorted(missing_in_metadata)}"
                )
            
            if missing_in_dirs:
                self.results["metadata_issues"].append(
                    f"元数据中存在但目录中缺失: {sorted(missing_in_dirs)}"
                )
            
            if not missing_in_metadata and not missing_in_dirs:
                print("  ✓ 元数据与目录结构一致\n")
            else:
                print(f"  ⚠️  发现 {len(missing_in_metadata) + len(missing_in_dirs)} 个不一致项\n")
                
        except Exception as e:
            self.results["metadata_issues"].append(f"检查失败: {e}")
            print(f"  ❌ 检查失败: {e}\n")
    
    def _check_gather_facts(self, data: any, content: str) -> bool:
        """检查是否声明了 gather_facts"""
        if isinstance(data, list):
            for play in data:
                if isinstance(play, dict):
                    if 'gather_facts' in play:
                        return True
        # 备用：在文本中查找
        return bool(re.search(r'gather_facts\s*:', content))
    
    def _check_become(self, data: any, content: str) -> bool:
        """检查是否使用了 become"""
        if isinstance(data, list):
            for play in data:
                if isinstance(play, dict):
                    if 'become' in play:
                        return True
                    tasks = play.get('tasks', [])
                    for task in tasks:
                        if isinstance(task, dict) and 'become' in task:
                            return True
        return bool(re.search(r'become\s*:', content))
    
    def _check_vars_files(self, data: any, content: str) -> bool:
        """检查是否使用了 vars_files"""
        if isinstance(data, list):
            for play in data:
                if isinstance(play, dict) and 'vars_files' in play:
                    return True
        return bool(re.search(r'vars_files\s*:', content))
    
    def _check_check_mode(self, content: str) -> bool:
        """检查是否使用了 check_mode"""
        return bool(re.search(r'check_mode\s*:', content))
    
    def _check_no_log(self, content: str) -> bool:
        """检查是否使用了 no_log"""
        return bool(re.search(r'no_log\s*:', content))
    
    def _check_chinese_names(self, data: any) -> Dict[str, bool]:
        """检查 Play、Task、Handler 名称是否使用中文"""
        result = {
            "play_names_ok": True,
            "task_names_ok": True,
            "handler_names_ok": True
        }
        
        if not isinstance(data, list):
            return result
        
        for play in data:
            if not isinstance(play, dict):
                continue
                
            # 检查 Play 名称
            if 'name' in play:
                if not self._has_chinese(play['name']):
                    result["play_names_ok"] = False
            
            # 检查 Task 名称
            tasks = play.get('tasks', [])
            for task in tasks:
                if isinstance(task, dict) and 'name' in task:
                    if not self._has_chinese(task['name']):
                        result["task_names_ok"] = False
            
            # 检查 Handler 名称
            handlers = play.get('handlers', [])
            for handler in handlers:
                if isinstance(handler, dict) and 'name' in handler:
                    if not self._has_chinese(handler['name']):
                        result["handler_names_ok"] = False
        
        return result
    
    def _has_chinese(self, text: str) -> bool:
        """判断文本是否包含中文字符"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def _check_fqcn(self, data: any, content: str) -> List[str]:
        """检查是否正确使用 FQCN"""
        issues = []
        
        # 常见需要 FQCN 的模块
        common_modules = [
            'copy', 'file', 'template', 'service', 'user', 'group',
            'apt', 'yum', 'package', 'shell', 'command', 'debug'
        ]
        
        for module in common_modules:
            # 查找未使用 FQCN 的模块调用（简化检查）
            pattern = rf'^\s+{module}\s*:' 
            if re.search(pattern, content, re.MULTILINE):
                # 进一步检查是否有对应的 FQCN
                fqcn_pattern = rf'ansible\.builtin\.{module}\s*:|community\.\w+\.{module}\s*:'
                if not re.search(fqcn_pattern, content):
                    issues.append(f"模块 '{module}' 可能未使用 FQCN")
        
        return issues
    
    def _has_hardcoded_secrets(self, content: str) -> bool:
        """检查是否存在硬编码的敏感信息"""
        # 简单检查：查找常见的硬编码模式
        patterns = [
            r'password\s*:\s*["\'](?!vault_|{{)[^"\']+["\']',
            r'token\s*:\s*["\'](?!vault_|{{)[^"\']+["\']',
            r'secret\s*:\s*["\'](?!vault_|{{)[^"\']+["\']',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def print_summary(self):
        """打印审计摘要"""
        print("\n" + "="*60)
        print("📊 审计结果摘要")
        print("="*60)
        
        stats = self.results["statistics"]
        
        print(f"\n📋 Playbook 统计:")
        print(f"  - 总计: {stats.get('total_playbooks', 0)} 个")
        print(f"  - 缺少 gather_facts: {stats.get('missing_gather_facts', 0)} 个")
        print(f"  - 使用 check_mode: {stats.get('with_check_mode', 0)} 个")
        print(f"  - Handler 未中文化: {stats.get('handler_not_chinese', 0)} 个")
        
        print(f"\n📦 变量文件统计:")
        print(f"  - 总计: {stats.get('total_vars_files', 0)} 个")
        print(f"  - 缺少 ⚠️ 警告: {stats.get('missing_warning', 0)} 个")
        
        print(f"\n📖 README 统计:")
        print(f"  - 总计: {stats.get('total_readmes', 0)} 个")
        print(f"  - 中文内容不足: {stats.get('readme_insufficient_chinese', 0)} 个")
        
        print(f"\n🗂️  元数据一致性:")
        if self.results["metadata_issues"]:
            for issue in self.results["metadata_issues"]:
                print(f"  - ⚠️  {issue}")
        else:
            print(f"  - ✓ 无问题")
        
        print("\n" + "="*60)
        print(f"✓ 审计完成！发现以下问题数量:")
        print(f"  - Playbook 问题: {len(self.results['playbooks'])} 个文件")
        print(f"  - 变量文件问题: {len(self.results['vars_files'])} 个文件")
        print(f"  - README 问题: {len(self.results['readmes'])} 个文件")
        print(f"  - 元数据问题: {len(self.results['metadata_issues'])} 项")
        print("="*60 + "\n")


def main():
    """主入口"""
    import sys
    
    # 确定项目根目录
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        # 默认使用脚本所在目录的父目录
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
    
    checker = AuditChecker(project_root)
    checker.run()


if __name__ == "__main__":
    main()
