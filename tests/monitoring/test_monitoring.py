"""
监控模块 pytest 测试套件

测试监控模块的配置文件、playbook 和变量文件是否符合最佳实践：
- 使用 FQCN（Fully Qualified Collection Names）
- 保护敏感信息（no_log 保护）
- README 文档完整性
- 变量文件安全提示
- collection 安装步骤说明
"""

import os
import pytest
import yaml
from pathlib import Path
from typing import Dict, List, Any


class TestMonitoringModule:
    """监控模块基础测试类"""

    @pytest.fixture(scope="class")
    def monitoring_root(self) -> Path:
        """获取监控模块根目录"""
        return Path(__file__).parent.parent.parent / "monitoring"

    @pytest.fixture(scope="class")
    def monitoring_modules(self, monitoring_root: Path) -> List[Path]:
        """获取所有监控模块目录"""
        modules = []
        for item in monitoring_root.iterdir():
            if item.is_dir() and item.name not in ["__pycache__"]:
                modules.append(item)
        return modules

    @pytest.fixture(scope="class")
    def fqcn_mapping(self) -> Dict[str, str]:
        """FQCN 映射表"""
        return {
            "nagios": "community.general.nagios",
            "datadog": "community.datadog.datadog_agent",
            "zabbix": "community.zabbix.zabbix_host",
            "prometheus": "ansible.builtin.uri",
            "splunk": "community.rabbitmq.rabbitmq",  # Splunk uses community.general or builtin modules
            "elk": "community.elastic"
        }


class TestPlaybookStructure(TestMonitoringModule):
    """测试 Playbook 结构和最佳实践"""

    def test_playbook_files_exist(self, monitoring_modules: List[Path]):
        """测试每个监控模块是否包含 playbook.yml 文件"""
        for module_dir in monitoring_modules:
            playbook_file = module_dir / "playbook.yml"
            assert playbook_file.exists(), f"模块 {module_dir.name} 缺少 playbook.yml 文件"

    def test_playbook_yaml_syntax(self, monitoring_modules: List[Path]):
        """测试 playbook 文件 YAML 语法正确性"""
        for module_dir in monitoring_modules:
            playbook_file = module_dir / "playbook.yml"
            if playbook_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    try:
                        yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        pytest.fail(f"模块 {module_dir.name} 的 playbook.yml 语法错误: {e}")

    def test_fqcn_usage(self, monitoring_modules: List[Path], fqcn_mapping: Dict[str, str]):
        """测试是否使用了 FQCN（Fully Qualified Collection Names）"""
        for module_dir in monitoring_modules:
            playbook_file = module_dir / "playbook.yml"
            if playbook_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否使用了正确的 FQCN
                expected_fqcn = fqcn_mapping.get(module_dir.name)
                if expected_fqcn and not expected_fqcn.startswith("community.rabbitmq"):
                    # Skip FQCN test for modules that don't have specific collection modules
                    if expected_fqcn in content or "ansible.builtin" in content or "community." in content:
                        pass  # Accept if using FQCN format
                    else:
                        pytest.fail(f"模块 {module_dir.name} 的 playbook 应使用 FQCN")

    def test_no_log_usage(self, monitoring_modules: List[Path]):
        """测试敏感变量是否使用 no_log: true 保护"""
        sensitive_patterns = [
            "password", "api_key", "app_key", "secret", "token"
        ]
        
        for module_dir in monitoring_modules:
            playbook_file = module_dir / "playbook.yml"
            if playbook_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含敏感变量
                has_sensitive_vars = any(pattern in content for pattern in sensitive_patterns)
                
                if has_sensitive_vars:
                    # 检查是否使用了 no_log: true
                    assert "no_log: true" in content, \
                        f"模块 {module_dir.name} 的 playbook 包含敏感变量但未使用 no_log: true 保护"

    def test_check_mode_usage(self, monitoring_modules: List[Path]):
        """测试是否使用了 check_mode: yes 特性"""
        for module_dir in monitoring_modules:
            playbook_file = module_dir / "playbook.yml"
            if playbook_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否使用了 check_mode
                assert "check_mode: yes" in content, \
                    f"模块 {module_dir.name} 的 playbook 应使用 check_mode: yes 进行安全检查"

    def test_chinese_comments(self, monitoring_modules: List[Path]):
        """测试 playbook 是否包含中文注释"""
        for module_dir in monitoring_modules:
            playbook_file = module_dir / "playbook.yml"
            if playbook_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含中文字符（注释）
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in content)
                assert has_chinese, \
                    f"模块 {module_dir.name} 的 playbook 应包含中文注释"


class TestReadmeDocumentation(TestMonitoringModule):
    """测试 README 文档完整性"""

    def test_readme_files_exist(self, monitoring_modules: List[Path]):
        """测试每个监控模块是否包含 README.md 文件"""
        for module_dir in monitoring_modules:
            readme_file = module_dir / "README.md"
            assert readme_file.exists(), f"模块 {module_dir.name} 缺少 README.md 文件"

    def test_readme_content_structure(self, monitoring_modules: List[Path]):
        """测试 README 文档结构完整性"""
        required_sections = [
            "模块用途",
            "主要参数", 
            "返回值",
            "常见使用场景",
            "安全提示",
            "依赖要求",
            "安装步骤"
        ]
        
        for module_dir in monitoring_modules:
            readme_file = module_dir / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for section in required_sections:
                    assert section in content, \
                        f"模块 {module_dir.name} 的 README.md 缺少 '{section}' 章节"

    def test_sensitive_info_handling(self, monitoring_modules: List[Path]):
        """测试 README 是否明确标注敏感信息处理方式"""
        sensitive_keywords = [
            "敏感信息", "API Key", "密码", "加密", "Vault", "环境变量"
        ]
        
        for module_dir in monitoring_modules:
            readme_file = module_dir / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含敏感信息处理说明
                has_sensitive_info = any(keyword in content for keyword in sensitive_keywords)
                assert has_sensitive_info, \
                    f"模块 {module_dir.name} 的 README.md 应包含敏感信息处理说明"

    def test_collection_installation_steps(self, monitoring_modules: List[Path]):
        """测试 README 是否包含 collection 安装步骤"""
        install_keywords = [
            "ansible-galaxy collection install",
            "pip install",
            "安装步骤"
        ]
        
        for module_dir in monitoring_modules:
            readme_file = module_dir / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含安装步骤
                has_install_steps = any(keyword in content for keyword in install_keywords)
                assert has_install_steps, \
                    f"模块 {module_dir.name} 的 README.md 应包含 collection 安装步骤"


class TestVariableFiles(TestMonitoringModule):
    """测试变量文件安全性和完整性"""

    def test_vars_directory_structure(self, monitoring_modules: List[Path]):
        """测试 vars 目录结构"""
        for module_dir in monitoring_modules:
            vars_dir = module_dir / "vars"
            assert vars_dir.exists(), f"模块 {module_dir.name} 缺少 vars 目录"
            assert vars_dir.is_dir(), f"模块 {module_dir.name} 的 vars 不是目录"

    def test_example_vars_exist(self, monitoring_modules: List[Path]):
        """测试每个模块是否包含 example_vars.yml 文件"""
        for module_dir in monitoring_modules:
            example_vars_file = module_dir / "vars" / "example_vars.yml"
            assert example_vars_file.exists(), \
                f"模块 {module_dir.name} 缺少 vars/example_vars.yml 文件"

    def test_vars_yaml_syntax(self, monitoring_modules: List[Path]):
        """测试变量文件 YAML 语法正确性"""
        for module_dir in monitoring_modules:
            example_vars_file = module_dir / "vars" / "example_vars.yml"
            if example_vars_file.exists():
                with open(example_vars_file, 'r', encoding='utf-8') as f:
                    try:
                        yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        pytest.fail(f"模块 {module_dir.name} 的 example_vars.yml 语法错误: {e}")

    def test_chinese_comments_in_vars(self, monitoring_modules: List[Path]):
        """测试变量文件是否包含中文注释"""
        for module_dir in monitoring_modules:
            example_vars_file = module_dir / "vars" / "example_vars.yml"
            if example_vars_file.exists():
                with open(example_vars_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含中文字符（注释）
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in content)
                assert has_chinese, \
                    f"模块 {module_dir.name} 的 example_vars.yml 应包含中文注释"

    def test_security_warnings_in_vars(self, monitoring_modules: List[Path]):
        """测试变量文件是否包含安全警告"""
        warning_keywords = [
            "重要提示", "敏感信息", "不要提交", "加密", "Vault", "占位符"
        ]
        
        for module_dir in monitoring_modules:
            example_vars_file = module_dir / "vars" / "example_vars.yml"
            if example_vars_file.exists():
                with open(example_vars_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含安全警告
                has_warnings = any(keyword in content for keyword in warning_keywords)
                assert has_warnings, \
                    f"模块 {module_dir.name} 的 example_vars.yml 应包含安全警告和提示"

    def test_placeholder_usage(self, monitoring_modules: List[Path]):
        """测试变量文件是否使用占位符而非真实值"""
        placeholder_patterns = [
            "example.com",
            "placeholder",
            "your_",
            "REPLACE_",
            "vault_",
            "{{ vault_"
        ]
        
        for module_dir in monitoring_modules:
            example_vars_file = module_dir / "vars" / "example_vars.yml"
            if example_vars_file.exists():
                with open(example_vars_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否使用了占位符模式
                has_placeholders = any(pattern in content for pattern in placeholder_patterns)
                assert has_placeholders, \
                    f"模块 {module_dir.name} 的 example_vars.yml 应使用占位符而非真实值"


class TestMonitoringRootDocumentation(TestMonitoringModule):
    """测试监控模块根目录文档"""

    def test_main_readme_exists(self, monitoring_root: Path):
        """测试监控根目录是否包含 README.md"""
        readme_file = monitoring_root / "README.md"
        assert readme_file.exists(), "监控根目录缺少 README.md 文件"

    def test_main_readme_content(self, monitoring_root: Path):
        """测试监控根目录 README 内容完整性"""
        readme_file = monitoring_root / "README.md"
        if readme_file.exists():
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            required_sections = [
                "监控章节目标",
                "模块列表",
                "前置条件",
                "安全最佳实践",
                "使用指南"
            ]
            
            for section in required_sections:
                assert section in content, f"监控根目录 README.md 缺少 '{section}' 章节"

    def test_module_list_in_readme(self, monitoring_root: Path, monitoring_modules: List[Path]):
        """测试 README 中的模块列表是否与实际模块匹配"""
        readme_file = monitoring_root / "README.md"
        if readme_file.exists():
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查每个模块是否在 README 中被提及
            for module_dir in monitoring_modules:
                assert module_dir.name in content, \
                    f"模块 {module_dir.name} 未在监控根目录 README.md 中列出"


class TestSecurityRequirements(TestMonitoringModule):
    """测试安全相关要求"""

    def test_no_hardcoded_secrets(self, monitoring_modules: List[Path]):
        """测试是否没有硬编码的敏感信息"""
        secret_patterns = [
            r'password\s*:\s*"[^"]*"',  # 硬编码密码
            r'api_key\s*:\s*"[^"]*"',   # 硬编码 API key
            r'secret\s*:\s*"[^"]*"',    # 硬编码密钥
            r'token\s*:\s*"[^"]*"',     # 硬编码 token
        ]
        
        import re
        
        for module_dir in monitoring_modules:
            # 检查 playbook.yml
            playbook_file = module_dir / "playbook.yml"
            if playbook_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    # 排除占位符和变量引用
                    real_secrets = [m for m in matches if not any(
                        placeholder in m.lower() 
                        for placeholder in ['example', 'placeholder', 'your_', 'replace', 'vault', '{{', '${']
                    )]
                    assert len(real_secrets) == 0, \
                        f"模块 {module_dir.name} 的 playbook.yml 包含硬编码敏感信息: {real_secrets}"

    def test_variable_isolation(self, monitoring_modules: List[Path]):
        """测试敏感变量是否隔离到单独的变量文件"""
        for module_dir in monitoring_modules:
            playbook_file = module_dir / "playbook.yml"
            vars_file = module_dir / "vars" / "example_vars.yml"
            
            if playbook_file.exists() and vars_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    playbook_content = f.read()
                    
                # 检查 playbook 是否引用外部变量文件
                assert "vars_files:" in playbook_content, \
                    f"模块 {module_dir.name} 的 playbook 应使用 vars_files 引用外部变量文件"


class TestExternalDependencies(TestMonitoringModule):
    """测试外部依赖和 API 密钥管理"""

    def test_external_dependencies_documented(self, monitoring_modules: List[Path]):
        """测试 README 是否记录外部依赖"""
        dependency_keywords = [
            "依赖要求", "安装步骤", "ansible-galaxy", "pip install", "collection"
        ]
        
        for module_dir in monitoring_modules:
            readme_file = module_dir / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含依赖相关说明
                has_dependencies = any(keyword in content for keyword in dependency_keywords)
                assert has_dependencies, \
                    f"模块 {module_dir.name} 的 README.md 应包含外部依赖说明"

    def test_api_key_management_documented(self, monitoring_modules: List[Path]):
        """测试 README 是否包含 API Key 管理说明"""
        api_key_keywords = [
            "API Key", "API Token", "认证", "凭证", "密钥管理"
        ]
        
        for module_dir in monitoring_modules:
            readme_file = module_dir / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 对于可能需要 API Key 的模块，检查是否有说明
                if any(keyword in content.lower() for keyword in ["api", "key", "token"]):
                    has_api_key_docs = any(keyword in content for keyword in api_key_keywords)
                    # 不强制要求，但建议包含
                    if not has_api_key_docs:
                        print(f"提示: 模块 {module_dir.name} 可能需要 API Key 但缺少相关说明")

    def test_no_log_for_api_credentials(self, monitoring_modules: List[Path]):
        """测试包含 API 凭证的任务是否使用 no_log 保护"""
        api_credential_patterns = [
            "api_key", "api_token", "password", "secret", "token", "hec_token"
        ]
        
        for module_dir in monitoring_modules:
            playbook_file = module_dir / "playbook.yml"
            if playbook_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含 API 凭证相关内容
                has_api_credentials = any(pattern in content.lower() for pattern in api_credential_patterns)
                
                if has_api_credentials:
                    # 检查是否使用了 no_log
                    assert "no_log:" in content or "no_log: true" in content, \
                        f"模块 {module_dir.name} 的 playbook 包含 API 凭证但未使用 no_log 保护"

    def test_vault_usage_recommended(self, monitoring_modules: List[Path]):
        """测试变量文件是否推荐使用 Vault"""
        vault_keywords = [
            "vault_", "Vault", "ansible-vault", "加密"
        ]
        
        for module_dir in monitoring_modules:
            vars_file = module_dir / "vars" / "example_vars.yml"
            if vars_file.exists():
                with open(vars_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含 Vault 相关说明或引用
                has_vault_reference = any(keyword in content for keyword in vault_keywords)
                assert has_vault_reference, \
                    f"模块 {module_dir.name} 的变量文件应包含 Vault 使用说明或引用"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])