#!/usr/bin/env python3
"""
全面检查优化工具 - Comprehensive Audit Tool
对 ansible_playbook 项目进行全面检查和优化分析
"""

import os
import sys
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
from datetime import datetime

class ComprehensiveAuditor:
    """全面审计工具"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        self.stats = defaultdict(int)
        self.module_categories = [
            'system', 'files', 'network', 'database', 'applications',
            'web', 'storage', 'monitoring', 'message_queue', 'cloud',
            'virtualization', 'version_control', 'advanced', 'network_protocols',
            'commands'
        ]
        
    def run_audit(self) -> Dict[str, Any]:
        """运行完整审计流程"""
        print("🔍 开始全面审计...")
        print("=" * 80)
        
        # A. 项目结构完整性
        print("\n📁 检查项目结构完整性...")
        self.check_project_structure()
        
        # B. 文件内容检查
        print("\n📝 检查文件内容...")
        self.check_file_contents()
        
        # C. 安全性检查
        print("\n🔒 执行安全性检查...")
        self.check_security()
        
        # D. 测试覆盖检查
        print("\n🧪 检查测试覆盖...")
        self.check_test_coverage()
        
        # E. 元数据一致性
        print("\n📋 验证元数据一致性...")
        self.check_metadata_consistency()
        
        # F. 文档导航检查
        print("\n📚 检查文档导航...")
        self.check_documentation()
        
        # G. 依赖和需求检查
        print("\n📦 检查依赖和需求...")
        self.check_dependencies()
        
        # H. 冗余和矛盾检查
        print("\n🔄 检查冗余和矛盾...")
        self.check_redundancy()
        
        # 生成报告
        print("\n📊 生成审计报告...")
        return self.generate_report()
    
    def check_project_structure(self):
        """A. 检查项目结构完整性"""
        # 检查模块分类目录
        for category in self.module_categories:
            category_path = self.project_root / category
            if not category_path.exists():
                self.add_issue('high', f'缺失模块分类目录: {category}/', 
                             f'创建目录: mkdir -p {category}')
                continue
            
            self.stats[f'category_{category}'] = 1
            
            # 检查该分类下的模块
            for module_dir in category_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('.'):
                    self.check_module_structure(module_dir, category)
        
        # 检查关键目录
        critical_dirs = ['tests', 'metadata', 'tools', 'docs', 'collections']
        for dir_name in critical_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                self.add_issue('critical', f'缺失关键目录: {dir_name}/', 
                             f'创建目录: mkdir -p {dir_name}')
            else:
                self.stats[f'dir_{dir_name}'] = 1
    
    def check_module_structure(self, module_path: Path, category: str):
        """检查单个模块的结构完整性"""
        module_name = module_path.name
        self.stats['total_modules'] += 1
        
        # 检查必需文件
        required_files = {
            'README.md': 'medium',
            'playbook.yml': 'critical',
            'vars/example_vars.yml': 'high'
        }
        
        for file_path, priority in required_files.items():
            full_path = module_path / file_path
            if not full_path.exists():
                self.add_issue(priority, 
                             f'模块 {category}/{module_name} 缺失文件: {file_path}',
                             f'创建文件: {full_path}')
            else:
                self.stats[f'has_{file_path.replace("/", "_")}'] += 1
    
    def check_file_contents(self):
        """B. 检查文件内容"""
        # 查找所有 playbook.yml 文件
        for playbook_path in self.project_root.rglob('playbook.yml'):
            self.check_playbook_content(playbook_path)
        
        # 检查所有变量文件
        for vars_file in self.project_root.rglob('vars/example_vars.yml'):
            self.check_vars_file(vars_file)
        
        # 检查所有 README
        for readme in self.project_root.rglob('README.md'):
            self.check_readme_content(readme)
    
    def check_playbook_content(self, playbook_path: Path):
        """检查单个 playbook 内容"""
        self.stats['total_playbooks'] += 1
        
        try:
            with open(playbook_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # YAML 语法检查
            try:
                data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                self.add_issue('critical', 
                             f'YAML 语法错误: {playbook_path}',
                             f'修复 YAML 语法错误: {str(e)}')
                return
            
            if not data or not isinstance(data, list):
                self.add_issue('high', f'Playbook 格式错误: {playbook_path}',
                             'Playbook 应该是一个列表')
                return
            
            for play in data:
                if not isinstance(play, dict):
                    continue
                
                # 检查 gather_facts
                if 'gather_facts' not in play:
                    self.add_issue('medium', 
                                 f'缺少 gather_facts 声明: {playbook_path}',
                                 '添加 gather_facts: true 或 gather_facts: false')
                else:
                    self.stats['has_gather_facts'] += 1
                
                # 检查任务中的模块是否使用 FQCN
                tasks = play.get('tasks', []) + play.get('pre_tasks', []) + play.get('post_tasks', [])
                for task in tasks:
                    if isinstance(task, dict):
                        self.check_task_fqcn(task, playbook_path)
                        self.check_task_chinese(task, playbook_path)
                        self.check_task_no_log(task, playbook_path)
                
                # 检查 handlers
                handlers = play.get('handlers', [])
                for handler in handlers:
                    if isinstance(handler, dict):
                        self.check_handler_chinese(handler, playbook_path)
                        
        except Exception as e:
            self.add_issue('high', f'读取文件失败: {playbook_path}',
                         f'错误: {str(e)}')
    
    def check_task_fqcn(self, task: Dict, playbook_path: Path):
        """检查任务是否使用 FQCN"""
        # 获取模块名（跳过特殊键）
        special_keys = {'name', 'when', 'with_items', 'loop', 'register', 
                       'notify', 'tags', 'become', 'become_user', 'vars',
                       'block', 'rescue', 'always', 'include', 'import_tasks',
                       'include_tasks', 'import_playbook'}
        
        for key in task.keys():
            if key not in special_keys:
                # 检查是否是 FQCN 格式 (namespace.collection.module)
                if key.count('.') < 2 and not key.startswith('ansible.builtin.'):
                    # 一些内置模块可能不使用 FQCN
                    common_builtins = {'debug', 'set_fact', 'assert', 'fail', 
                                      'meta', 'pause', 'wait_for', 'include_vars'}
                    if key not in common_builtins:
                        self.add_issue('low', 
                                     f'模块未使用 FQCN: {key} in {playbook_path}',
                                     f'使用完全限定名，如 ansible.builtin.{key}')
                        self.stats['non_fqcn_modules'] += 1
                    else:
                        self.stats['fqcn_modules'] += 1
                else:
                    self.stats['fqcn_modules'] += 1
    
    def check_task_chinese(self, task: Dict, playbook_path: Path):
        """检查任务名称是否为中文"""
        if 'name' in task:
            name = task['name']
            # 检查是否包含中文字符
            if not re.search(r'[\u4e00-\u9fff]', name):
                self.add_issue('low', 
                             f'任务名称不是中文: "{name}" in {playbook_path}',
                             '使用中文任务名称')
                self.stats['non_chinese_tasks'] += 1
            else:
                self.stats['chinese_tasks'] += 1
    
    def check_task_no_log(self, task: Dict, playbook_path: Path):
        """检查敏感操作是否使用 no_log"""
        sensitive_keywords = ['password', 'passwd', 'secret', 'token', 'key', 
                            'vault', 'credential', 'api_key']
        
        task_str = str(task).lower()
        has_sensitive = any(kw in task_str for kw in sensitive_keywords)
        
        if has_sensitive and not task.get('no_log'):
            self.add_issue('high', 
                         f'敏感操作未使用 no_log: {playbook_path}',
                         '为包含敏感信息的任务添加 no_log: true')
            self.stats['missing_no_log'] += 1
    
    def check_handler_chinese(self, handler: Dict, playbook_path: Path):
        """检查 handler 名称是否为中文"""
        if 'name' in handler:
            name = handler['name']
            if not re.search(r'[\u4e00-\u9fff]', name):
                self.add_issue('medium', 
                             f'Handler 名称不是中文: "{name}" in {playbook_path}',
                             '使用中文 handler 名称')
    
    def check_vars_file(self, vars_path: Path):
        """检查变量文件"""
        self.stats['total_vars_files'] += 1
        
        try:
            with open(vars_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查警告头
            warning_pattern = r'⚠️.*本文件仅为示例.*占位符.*Ansible Vault.*环境变量'
            if not re.search(warning_pattern, content, re.DOTALL):
                self.add_issue('medium', 
                             f'变量文件缺少警告头: {vars_path}',
                             '添加警告: ⚠️ 本文件仅为示例，占位符必须使用 Ansible Vault 或环境变量替换')
                self.stats['vars_missing_warning'] += 1
            else:
                self.stats['vars_has_warning'] += 1
                
        except Exception as e:
            self.add_issue('medium', f'读取变量文件失败: {vars_path}',
                         f'错误: {str(e)}')
    
    def check_readme_content(self, readme_path: Path):
        """检查 README 内容"""
        self.stats['total_readmes'] += 1
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含英文内容（简单检测）
            # 排除代码块和命令
            lines = content.split('\n')
            text_lines = [l for l in lines if not l.strip().startswith('```') 
                         and not l.strip().startswith('#') 
                         and not l.strip().startswith('-')
                         and not l.strip().startswith('`')]
            
            text_content = ' '.join(text_lines)
            # 检查是否有大量英文单词（可能是英文混用）
            english_words = re.findall(r'\b[a-zA-Z]{4,}\b', text_content)
            # 排除常见技术词汇
            tech_words = {'ansible', 'playbook', 'yaml', 'python', 'linux', 
                         'ubuntu', 'centos', 'rhel', 'sudo', 'root', 'user',
                         'group', 'file', 'directory', 'service', 'systemd',
                         'nginx', 'apache', 'mysql', 'postgresql', 'mongodb',
                         'docker', 'kubernetes', 'vault', 'inventory', 'role',
                         'task', 'handler', 'variable', 'template', 'module',
                         'collection', 'galaxy', 'github', 'gitlab', 'aws',
                         'azure', 'gcp', 'openstack', 'vmware', 'libvirt'}
            
            non_tech_english = [w for w in english_words 
                              if w.lower() not in tech_words]
            
            if len(non_tech_english) > 10:
                self.add_issue('low', 
                             f'README 可能包含英文内容: {readme_path}',
                             f'检查并翻译为中文 (发现 {len(non_tech_english)} 个非技术英文词汇)')
                             
        except Exception as e:
            self.add_issue('low', f'读取 README 失败: {readme_path}',
                         f'错误: {str(e)}')
    
    def check_security(self):
        """C. 安全性检查"""
        # 检查所有 YAML 文件中的硬编码敏感信息
        for yml_file in self.project_root.rglob('*.yml'):
            if 'venv' in str(yml_file) or '.git' in str(yml_file):
                continue
            self.check_hardcoded_secrets(yml_file)
    
    def check_hardcoded_secrets(self, file_path: Path):
        """检查硬编码的密码和密钥"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查可疑的硬编码模式
            suspicious_patterns = [
                (r'password:\s*["\']?[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};:,.<>?]{8,}["\']?',
                 '可能存在硬编码密码'),
                (r'api[_-]?key:\s*["\']?[a-zA-Z0-9]{20,}["\']?',
                 '可能存在硬编码 API Key'),
                (r'secret:\s*["\']?[a-zA-Z0-9]{16,}["\']?',
                 '可能存在硬编码 Secret'),
                (r'token:\s*["\']?[a-zA-Z0-9]{20,}["\']?',
                 '可能存在硬编码 Token'),
            ]
            
            for pattern, msg in suspicious_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    matched_text = match.group()
                    # 排除明显的占位符和 vault_ 前缀
                    if ('vault_' in matched_text.lower() or 
                        'your_' in matched_text.lower() or
                        'example' in matched_text.lower() or
                        'placeholder' in matched_text.lower() or
                        '***' in matched_text or
                        'xxx' in matched_text.lower()):
                        continue
                    
                    self.add_issue('critical', 
                                 f'{msg}: {file_path}',
                                 f'使用 vault_ 前缀或 Ansible Vault 加密: {matched_text}')
                    self.stats['potential_hardcoded_secrets'] += 1
                    
        except Exception as e:
            pass  # 跳过无法读取的文件
    
    def check_test_coverage(self):
        """D. 测试覆盖检查"""
        tests_dir = self.project_root / 'tests'
        if not tests_dir.exists():
            self.add_issue('high', '缺少 tests 目录', '创建 tests 目录并添加测试')
            return
        
        # 统计测试文件
        test_files = list(tests_dir.rglob('test_*.py'))
        self.stats['total_test_files'] = len(test_files)
        
        # 检查每个模块分类是否有对应测试
        for category in self.module_categories:
            category_path = self.project_root / category
            if category_path.exists():
                test_file = tests_dir / f'test_{category}.py'
                if not test_file.exists():
                    self.add_issue('medium', 
                                 f'分类 {category} 缺少测试文件',
                                 f'创建 tests/test_{category}.py')
    
    def check_metadata_consistency(self):
        """E. 元数据一致性"""
        metadata_file = self.project_root / 'metadata' / 'modules.yaml'
        
        if not metadata_file.exists():
            self.add_issue('critical', 
                         '缺少 metadata/modules.yaml 文件',
                         '创建元数据文件')
            return
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = yaml.safe_load(f)
            
            if not metadata:
                self.add_issue('critical', 
                             'metadata/modules.yaml 为空',
                             '填充元数据内容')
                return
            
            # 获取实际存在的模块
            actual_modules = set()
            for category in self.module_categories:
                category_path = self.project_root / category
                if category_path.exists():
                    for module_dir in category_path.iterdir():
                        if module_dir.is_dir() and not module_dir.name.startswith('.'):
                            actual_modules.add(f"{category}/{module_dir.name}")
            
            # 获取元数据中的模块
            metadata_modules = set()
            if isinstance(metadata, dict):
                for category, modules in metadata.items():
                    if isinstance(modules, list):
                        for module in modules:
                            if isinstance(module, dict) and 'name' in module:
                                metadata_modules.add(f"{category}/{module['name']}")
            
            # 检查差异
            missing_in_metadata = actual_modules - metadata_modules
            extra_in_metadata = metadata_modules - actual_modules
            
            for module in missing_in_metadata:
                self.add_issue('medium', 
                             f'模块未在元数据中注册: {module}',
                             f'在 metadata/modules.yaml 中添加该模块')
            
            for module in extra_in_metadata:
                self.add_issue('low', 
                             f'元数据中的模块不存在: {module}',
                             f'从 metadata/modules.yaml 中移除或创建该模块')
            
            self.stats['metadata_modules'] = len(metadata_modules)
            self.stats['actual_modules'] = len(actual_modules)
            
        except Exception as e:
            self.add_issue('high', 
                         f'读取元数据文件失败: {str(e)}',
                         '检查并修复元数据文件格式')
    
    def check_documentation(self):
        """F. 文档导航检查"""
        root_readme = self.project_root / 'README.md'
        
        if not root_readme.exists():
            self.add_issue('critical', 
                         '缺少根目录 README.md',
                         '创建根目录 README.md')
            return
        
        try:
            with open(root_readme, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含所有分类的链接
            for category in self.module_categories:
                category_path = self.project_root / category
                if category_path.exists():
                    if f'{category}/' not in content and f'{category}' not in content:
                        self.add_issue('low', 
                                     f'根 README 未提及分类: {category}',
                                     f'在 README.md 中添加 {category} 分类的导航链接')
            
            # 检查每个分类的 README
            for category in self.module_categories:
                category_readme = self.project_root / category / 'README.md'
                if not category_readme.exists():
                    category_path = self.project_root / category
                    if category_path.exists() and any(category_path.iterdir()):
                        self.add_issue('medium', 
                                     f'分类缺少 README: {category}/README.md',
                                     f'创建 {category}/README.md')
                        
        except Exception as e:
            self.add_issue('high', 
                         f'读取根 README 失败: {str(e)}',
                         '检查根 README.md 文件')
    
    def check_dependencies(self):
        """G. 依赖和需求检查"""
        # 检查 requirements.txt
        requirements_txt = self.project_root / 'requirements.txt'
        if not requirements_txt.exists():
            self.add_issue('high', 
                         '缺少 requirements.txt',
                         '创建 requirements.txt 列出 Python 依赖')
        else:
            self.stats['has_requirements_txt'] = 1
            try:
                with open(requirements_txt, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    self.stats['python_dependencies'] = len([l for l in lines 
                                                             if l.strip() and not l.startswith('#')])
            except Exception as e:
                self.add_issue('medium', f'读取 requirements.txt 失败: {str(e)}', '')
        
        # 检查 collections/requirements.yml
        collections_req = self.project_root / 'collections' / 'requirements.yml'
        if not collections_req.exists():
            self.add_issue('high', 
                         '缺少 collections/requirements.yml',
                         '创建 collections/requirements.yml 列出 Ansible Collections')
        else:
            self.stats['has_collections_requirements'] = 1
            try:
                with open(collections_req, 'r', encoding='utf-8') as f:
                    collections = yaml.safe_load(f)
                    if isinstance(collections, dict) and 'collections' in collections:
                        self.stats['ansible_collections'] = len(collections['collections'])
            except Exception as e:
                self.add_issue('medium', f'读取 collections/requirements.yml 失败: {str(e)}', '')
    
    def check_redundancy(self):
        """H. 冗余和矛盾检查"""
        # 检查重复的模块名
        module_names = defaultdict(list)
        
        for category in self.module_categories:
            category_path = self.project_root / category
            if category_path.exists():
                for module_dir in category_path.iterdir():
                    if module_dir.is_dir() and not module_dir.name.startswith('.'):
                        module_names[module_dir.name].append(f"{category}/{module_dir.name}")
        
        # 报告重复
        for module_name, locations in module_names.items():
            if len(locations) > 1:
                self.add_issue('medium', 
                             f'模块名称重复: {module_name}',
                             f'检查这些位置: {", ".join(locations)}')
                self.stats['duplicate_module_names'] += 1
        
        # 检查重复的 handler
        self.check_duplicate_handlers()
    
    def check_duplicate_handlers(self):
        """检查重复定义的 handler"""
        handlers = defaultdict(list)
        
        for playbook_path in self.project_root.rglob('playbook.yml'):
            try:
                with open(playbook_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                if isinstance(data, list):
                    for play in data:
                        if isinstance(play, dict) and 'handlers' in play:
                            for handler in play['handlers']:
                                if isinstance(handler, dict) and 'name' in handler:
                                    handler_name = handler['name']
                                    handlers[handler_name].append(str(playbook_path))
            except:
                pass
        
        for handler_name, locations in handlers.items():
            if len(locations) > 1:
                self.add_issue('low', 
                             f'Handler 名称重复: {handler_name}',
                             f'出现在 {len(locations)} 个文件中')
    
    def add_issue(self, priority: str, description: str, suggestion: str):
        """添加问题到对应优先级列表"""
        self.issues[priority].append({
            'description': description,
            'suggestion': suggestion
        })
    
    def generate_report(self) -> Dict[str, Any]:
        """生成审计报告"""
        report = {
            'audit_date': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'summary': {
                'total_issues': sum(len(issues) for issues in self.issues.values()),
                'critical_issues': len(self.issues['critical']),
                'high_issues': len(self.issues['high']),
                'medium_issues': len(self.issues['medium']),
                'low_issues': len(self.issues['low'])
            },
            'issues': self.issues,
            'statistics': dict(self.stats)
        }
        
        return report
    
    def format_report_markdown(self, report: Dict[str, Any]) -> str:
        """格式化为 Markdown 报告"""
        md = []
        md.append("# 全面审计报告 - Comprehensive Audit Report\n")
        md.append(f"**审计日期**: {report['audit_date']}\n")
        md.append(f"**项目路径**: {report['project_root']}\n")
        md.append("\n---\n")
        
        # 执行摘要
        md.append("\n## 📊 执行摘要 (Executive Summary)\n")
        summary = report['summary']
        md.append(f"- **问题总数**: {summary['total_issues']}\n")
        md.append(f"  - 🔴 Critical: {summary['critical_issues']}\n")
        md.append(f"  - 🟠 High: {summary['high_issues']}\n")
        md.append(f"  - 🟡 Medium: {summary['medium_issues']}\n")
        md.append(f"  - 🟢 Low: {summary['low_issues']}\n")
        
        # 统计信息
        md.append("\n## 📈 统计信息 (Statistics)\n")
        stats = report['statistics']
        
        md.append("\n### 项目规模\n")
        md.append(f"- 总模块数: {stats.get('total_modules', 0)}\n")
        md.append(f"- 总 Playbook 数: {stats.get('total_playbooks', 0)}\n")
        md.append(f"- 总变量文件数: {stats.get('total_vars_files', 0)}\n")
        md.append(f"- 总 README 数: {stats.get('total_readmes', 0)}\n")
        md.append(f"- 总测试文件数: {stats.get('total_test_files', 0)}\n")
        
        md.append("\n### 代码质量指标\n")
        md.append(f"- 使用 FQCN 的模块: {stats.get('fqcn_modules', 0)}\n")
        md.append(f"- 未使用 FQCN 的模块: {stats.get('non_fqcn_modules', 0)}\n")
        md.append(f"- 中文任务名: {stats.get('chinese_tasks', 0)}\n")
        md.append(f"- 非中文任务名: {stats.get('non_chinese_tasks', 0)}\n")
        md.append(f"- 声明 gather_facts 的 playbook: {stats.get('has_gather_facts', 0)}\n")
        
        md.append("\n### 安全性指标\n")
        md.append(f"- 缺少 no_log 的敏感操作: {stats.get('missing_no_log', 0)}\n")
        md.append(f"- 潜在硬编码密钥: {stats.get('potential_hardcoded_secrets', 0)}\n")
        md.append(f"- 包含警告头的变量文件: {stats.get('vars_has_warning', 0)}\n")
        md.append(f"- 缺少警告头的变量文件: {stats.get('vars_missing_warning', 0)}\n")
        
        md.append("\n### 元数据与依赖\n")
        md.append(f"- 元数据中的模块: {stats.get('metadata_modules', 0)}\n")
        md.append(f"- 实际存在的模块: {stats.get('actual_modules', 0)}\n")
        md.append(f"- Python 依赖数: {stats.get('python_dependencies', 0)}\n")
        md.append(f"- Ansible Collections 数: {stats.get('ansible_collections', 0)}\n")
        
        # 详细问题列表
        md.append("\n## 🔍 详细问题列表 (Detailed Issues)\n")
        
        priority_labels = {
            'critical': ('🔴 Critical', 'critical'),
            'high': ('🟠 High', 'high'),
            'medium': ('🟡 Medium', 'medium'),
            'low': ('🟢 Low', 'low')
        }
        
        for priority in ['critical', 'high', 'medium', 'low']:
            label, key = priority_labels[priority]
            issues = report['issues'][key]
            
            if not issues:
                continue
            
            md.append(f"\n### {label} 优先级问题 ({len(issues)} 项)\n")
            
            for i, issue in enumerate(issues, 1):
                md.append(f"\n#### {i}. {issue['description']}\n")
                if issue['suggestion']:
                    md.append(f"**修复建议**: {issue['suggestion']}\n")
        
        # 优化建议
        md.append("\n## 💡 优化建议 (Optimization Recommendations)\n")
        
        if summary['critical_issues'] > 0:
            md.append("\n### 🔴 立即处理 (Immediate Action Required)\n")
            md.append("1. 修复所有 Critical 级别的问题，这些问题可能影响项目的基本功能\n")
            md.append("2. 创建缺失的关键文件和目录\n")
            md.append("3. 修复 YAML 语法错误\n")
            md.append("4. 处理硬编码的敏感信息\n")
        
        if summary['high_issues'] > 0:
            md.append("\n### 🟠 高优先级 (High Priority)\n")
            md.append("1. 补充缺失的必需文件（README.md, playbook.yml 等）\n")
            md.append("2. 为敏感操作添加 no_log 保护\n")
            md.append("3. 创建缺失的测试文件\n")
            md.append("4. 补充依赖声明文件\n")
        
        if summary['medium_issues'] > 0:
            md.append("\n### 🟡 中等优先级 (Medium Priority)\n")
            md.append("1. 补充 gather_facts 声明\n")
            md.append("2. 为变量文件添加警告头\n")
            md.append("3. 同步元数据与实际模块\n")
            md.append("4. 为模块分类创建 README\n")
            md.append("5. 使用中文 handler 名称\n")
        
        if summary['low_issues'] > 0:
            md.append("\n### 🟢 低优先级 (Low Priority)\n")
            md.append("1. 统一使用 FQCN 格式的模块名\n")
            md.append("2. 统一使用中文任务名\n")
            md.append("3. 消除重复的模块和 handler 定义\n")
            md.append("4. 完善文档导航链接\n")
        
        # 最佳实践总结
        md.append("\n## ✨ 最佳实践总结 (Best Practices Summary)\n")
        md.append("\n### 1. 文件结构规范\n")
        md.append("```\n")
        md.append("category/\n")
        md.append("  module_name/\n")
        md.append("    README.md           # 模块说明文档\n")
        md.append("    playbook.yml        # 主 playbook\n")
        md.append("    vars/\n")
        md.append("      example_vars.yml  # 示例变量（带警告头）\n")
        md.append("```\n")
        
        md.append("\n### 2. Playbook 规范\n")
        md.append("- ✅ 明确声明 `gather_facts: true/false`\n")
        md.append("- ✅ 使用 FQCN 格式的模块名（如 `ansible.builtin.copy`）\n")
        md.append("- ✅ 任务名、handler 名、注释统一使用中文\n")
        md.append("- ✅ 敏感操作使用 `no_log: true`\n")
        md.append("- ✅ 支持 `--check` 模式\n")
        
        md.append("\n### 3. 安全规范\n")
        md.append("- ✅ 敏感变量使用 `vault_` 前缀\n")
        md.append("- ✅ 使用 Ansible Vault 加密敏感信息\n")
        md.append("- ✅ 变量文件包含 ⚠️ 警告头\n")
        md.append("- ✅ 不在代码中硬编码密码、密钥\n")
        
        md.append("\n### 4. 文档规范\n")
        md.append("- ✅ 每个模块包含完整的中文 README\n")
        md.append("- ✅ 根 README 包含所有分类的导航\n")
        md.append("- ✅ 每个分类有独立的 README 列出所有模块\n")
        md.append("- ✅ 文档中的技术术语保持英文，说明使用中文\n")
        
        md.append("\n### 5. 测试与元数据\n")
        md.append("- ✅ 每个模块分类有对应的 pytest 测试\n")
        md.append("- ✅ metadata/modules.yaml 与实际模块保持同步\n")
        md.append("- ✅ 定期运行审计工具检查一致性\n")
        
        # 下一步行动
        md.append("\n## 🎯 下一步行动计划 (Action Plan)\n")
        
        total_issues = summary['total_issues']
        if total_issues == 0:
            md.append("\n✅ **恭喜！项目通过了所有审计检查！**\n")
            md.append("\n建议：\n")
            md.append("- 继续保持现有的代码质量标准\n")
            md.append("- 定期运行审计工具确保持续合规\n")
            md.append("- 关注社区最佳实践的更新\n")
        else:
            md.append("\n### 短期目标（1-2周）\n")
            if summary['critical_issues'] > 0:
                md.append(f"1. 修复所有 {summary['critical_issues']} 个 Critical 问题\n")
            if summary['high_issues'] > 0:
                md.append(f"2. 修复所有 {summary['high_issues']} 个 High 问题\n")
            
            md.append("\n### 中期目标（1个月）\n")
            if summary['medium_issues'] > 0:
                md.append(f"1. 修复所有 {summary['medium_issues']} 个 Medium 问题\n")
            md.append("2. 完善文档和测试覆盖\n")
            md.append("3. 统一代码风格\n")
            
            md.append("\n### 长期目标（持续）\n")
            if summary['low_issues'] > 0:
                md.append(f"1. 逐步修复 {summary['low_issues']} 个 Low 问题\n")
            md.append("2. 建立自动化检查流程（CI/CD）\n")
            md.append("3. 定期更新依赖和最佳实践\n")
            md.append("4. 持续改进文档质量\n")
        
        md.append("\n---\n")
        md.append(f"\n*报告生成于 {report['audit_date']}*\n")
        
        return ''.join(md)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='全面审计 Ansible Playbook 项目')
    parser.add_argument('--project-root', default='/home/engine/project',
                       help='项目根目录路径')
    parser.add_argument('--output', default='reports/comprehensive_audit.md',
                       help='输出报告路径')
    parser.add_argument('--json', default='reports/comprehensive_audit.json',
                       help='JSON 报告路径')
    
    args = parser.parse_args()
    
    # 运行审计
    auditor = ComprehensiveAuditor(args.project_root)
    report = auditor.run_audit()
    
    # 生成 Markdown 报告
    markdown_report = auditor.format_report_markdown(report)
    
    # 保存报告
    output_path = Path(args.project_root) / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"\n✅ Markdown 报告已保存: {output_path}")
    
    # 保存 JSON 报告
    if args.json:
        json_path = Path(args.project_root) / args.json
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON 报告已保存: {json_path}")
    
    # 打印摘要
    print("\n" + "=" * 80)
    print("📊 审计完成摘要:")
    print("=" * 80)
    print(f"🔴 Critical: {report['summary']['critical_issues']}")
    print(f"🟠 High:     {report['summary']['high_issues']}")
    print(f"🟡 Medium:   {report['summary']['medium_issues']}")
    print(f"🟢 Low:      {report['summary']['low_issues']}")
    print(f"📝 Total:    {report['summary']['total_issues']}")
    print("=" * 80)
    
    # 如果有严重问题，返回非零退出码
    if report['summary']['critical_issues'] > 0:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
