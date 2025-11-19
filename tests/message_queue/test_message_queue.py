"""
消息队列模块 pytest 测试套件

测试消息队列模块的配置文件、playbook 和变量文件是否符合最佳实践：
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


class TestMessageQueueModule:
    """消息队列模块基础测试类"""

    @pytest.fixture(scope="class")
    def message_queue_root(self) -> Path:
        """获取消息队列模块根目录"""
        return Path(__file__).parent.parent.parent / "message_queue"

    @pytest.fixture(scope="class")
    def message_queue_modules(self, message_queue_root: Path) -> List[Path]:
        """获取所有消息队列模块目录"""
        modules = []
        for item in message_queue_root.iterdir():
            if item.is_dir() and item.name not in ["__pycache__"]:
                modules.append(item)
        return modules

    @pytest.fixture(scope="class")
    def fqcn_mapping(self) -> Dict[str, str]:
        """FQCN 映射表"""
        return {
            "rabbitmq_user": "community.rabbitmq.rabbitmq_user",
            "rabbitmq_queue": "community.rabbitmq.rabbitmq_queue",
            "kafka_topic": "community.general.kafka_topic"
        }


class TestPlaybookStructure(TestMessageQueueModule):
    """测试 Playbook 结构和最佳实践"""

    def test_playbook_files_exist(self, message_queue_modules: List[Path]):
        """测试每个消息队列模块是否包含 playbook.yml 文件"""
        for module_dir in message_queue_modules:
            playbook_file = module_dir / "playbook.yml"
            assert playbook_file.exists(), f"模块 {module_dir.name} 缺少 playbook.yml 文件"

    def test_playbook_yaml_syntax(self, message_queue_modules: List[Path]):
        """测试 playbook 文件 YAML 语法正确性"""
        for module_dir in message_queue_modules:
            playbook_file = module_dir / "playbook.yml"
            if playbook_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    try:
                        yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        pytest.fail(f"模块 {module_dir.name} 的 playbook.yml 语法错误: {e}")

    def test_fqcn_usage(self, message_queue_modules: List[Path], fqcn_mapping: Dict[str, str]):
        """测试是否使用了 FQCN（Fully Qualified Collection Names）"""
        for module_dir in message_queue_modules:
            playbook_file = module_dir / "playbook.yml"
            if playbook_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否使用了正确的 FQCN
                expected_fqcn = fqcn_mapping.get(module_dir.name)
                if expected_fqcn:
                    assert expected_fqcn in content, \
                        f"模块 {module_dir.name} 的 playbook 应使用 FQCN: {expected_fqcn}"

    def test_chinese_comments(self, message_queue_modules: List[Path]):
        """测试 playbook 是否包含中文注释"""
        for module_dir in message_queue_modules:
            playbook_file = module_dir / "playbook.yml"
            if playbook_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含中文字符（注释）
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in content)
                assert has_chinese, \
                    f"模块 {module_dir.name} 的 playbook 应包含中文注释"

    def test_vars_files_reference(self, message_queue_modules: List[Path]):
        """测试 playbook 是否引用外部变量文件"""
        for module_dir in message_queue_modules:
            playbook_file = module_dir / "playbook.yml"
            if playbook_file.exists():
                with open(playbook_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否引用了 vars_files
                assert "vars_files:" in content, \
                    f"模块 {module_dir.name} 的 playbook 应使用 vars_files 引用外部变量文件"


class TestReadmeDocumentation(TestMessageQueueModule):
    """测试 README 文档完整性"""

    def test_readme_files_exist(self, message_queue_modules: List[Path]):
        """测试每个消息队列模块是否包含 README.md 文件"""
        for module_dir in message_queue_modules:
            readme_file = module_dir / "README.md"
            assert readme_file.exists(), f"模块 {module_dir.name} 缺少 README.md 文件"

    def test_readme_content_structure(self, message_queue_modules: List[Path]):
        """测试 README 文档结构完整性"""
        required_sections = [
            "模块用途",
            "主要参数", 
            "返回值",
            "常见使用场景",
            "安全提示",
            "依赖要求"
        ]
        
        for module_dir in message_queue_modules:
            readme_file = module_dir / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for section in required_sections:
                    assert section in content, \
                        f"模块 {module_dir.name} 的 README.md 缺少 '{section}' 章节"

    def test_sensitive_info_handling(self, message_queue_modules: List[Path]):
        """测试 README 是否明确标注敏感信息处理方式"""
        sensitive_keywords = [
            "敏感信息", "密码", "加密", "Vault", "凭证"
        ]
        
        for module_dir in message_queue_modules:
            readme_file = module_dir / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含敏感信息处理说明
                has_sensitive_info = any(keyword in content for keyword in sensitive_keywords)
                assert has_sensitive_info, \
                    f"模块 {module_dir.name} 的 README.md 应包含敏感信息处理说明"

    def test_collection_installation_steps(self, message_queue_modules: List[Path]):
        """测试 README 是否包含 collection 安装步骤"""
        install_keywords = [
            "ansible-galaxy collection install",
            "pip install",
            "安装步骤"
        ]
        
        for module_dir in message_queue_modules:
            readme_file = module_dir / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含安装步骤
                has_install_steps = any(keyword in content for keyword in install_keywords)
                assert has_install_steps, \
                    f"模块 {module_dir.name} 的 README.md 应包含 collection 安装步骤"


class TestVariableFiles(TestMessageQueueModule):
    """测试变量文件安全性和完整性"""

    def test_vars_directory_structure(self, message_queue_modules: List[Path]):
        """测试 vars 目录结构"""
        for module_dir in message_queue_modules:
            vars_dir = module_dir / "vars"
            assert vars_dir.exists(), f"模块 {module_dir.name} 缺少 vars 目录"
            assert vars_dir.is_dir(), f"模块 {module_dir.name} 的 vars 不是目录"

    def test_example_vars_exist(self, message_queue_modules: List[Path]):
        """测试每个模块是否包含 example_vars.yml 文件"""
        for module_dir in message_queue_modules:
            example_vars_file = module_dir / "vars" / "example_vars.yml"
            assert example_vars_file.exists(), \
                f"模块 {module_dir.name} 缺少 vars/example_vars.yml 文件"

    def test_vars_yaml_syntax(self, message_queue_modules: List[Path]):
        """测试变量文件 YAML 语法正确性"""
        for module_dir in message_queue_modules:
            example_vars_file = module_dir / "vars" / "example_vars.yml"
            if example_vars_file.exists():
                with open(example_vars_file, 'r', encoding='utf-8') as f:
                    try:
                        yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        pytest.fail(f"模块 {module_dir.name} 的 example_vars.yml 语法错误: {e}")

    def test_chinese_comments_in_vars(self, message_queue_modules: List[Path]):
        """测试变量文件是否包含中文注释"""
        for module_dir in message_queue_modules:
            example_vars_file = module_dir / "vars" / "example_vars.yml"
            if example_vars_file.exists():
                with open(example_vars_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含中文字符（注释）
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in content)
                assert has_chinese, \
                    f"模块 {module_dir.name} 的 example_vars.yml 应包含中文注释"

    def test_security_warnings_in_vars(self, message_queue_modules: List[Path]):
        """测试变量文件是否包含安全警告"""
        warning_keywords = [
            "重要提示", "敏感信息", "不要提交", "加密", "Vault"
        ]
        
        for module_dir in message_queue_modules:
            example_vars_file = module_dir / "vars" / "example_vars.yml"
            if example_vars_file.exists():
                with open(example_vars_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含安全警告
                has_warnings = any(keyword in content for keyword in warning_keywords)
                assert has_warnings, \
                    f"模块 {module_dir.name} 的 example_vars.yml 应包含安全警告和提示"

    def test_vault_usage(self, message_queue_modules: List[Path]):
        """测试变量文件是否使用 Vault 变量引用"""
        vault_patterns = [
            "vault_",
            "{{ vault_",
            "ansible-vault"
        ]
        
        for module_dir in message_queue_modules:
            example_vars_file = module_dir / "vars" / "example_vars.yml"
            if example_vars_file.exists():
                with open(example_vars_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否使用了 Vault 模式
                has_vault_usage = any(pattern in content for pattern in vault_patterns)
                assert has_vault_usage, \
                    f"模块 {module_dir.name} 的 example_vars.yml 应使用 Vault 变量引用"


class TestMessageQueueRootDocumentation(TestMessageQueueModule):
    """测试消息队列模块根目录文档"""

    def test_main_readme_exists(self, message_queue_root: Path):
        """测试消息队列根目录是否包含 README.md"""
        readme_file = message_queue_root / "README.md"
        assert readme_file.exists(), "消息队列根目录缺少 README.md 文件"

    def test_main_readme_content(self, message_queue_root: Path):
        """测试消息队列根目录 README 内容完整性"""
        readme_file = message_queue_root / "README.md"
        if readme_file.exists():
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            required_sections = [
                "章节目标",
                "模块列表",
                "前置条件",
                "安全最佳实践",
                "使用指南"
            ]
            
            for section in required_sections:
                assert section in content, f"消息队列根目录 README.md 缺少 '{section}' 章节"

    def test_module_list_in_readme(self, message_queue_root: Path, message_queue_modules: List[Path]):
        """测试 README 中的模块列表是否与实际模块匹配"""
        readme_file = message_queue_root / "README.md"
        if readme_file.exists():
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查每个模块是否在 README 中被提及
            for module_dir in message_queue_modules:
                assert module_dir.name in content, \
                    f"模块 {module_dir.name} 未在消息队列根目录 README.md 中列出"


class TestSecurityRequirements(TestMessageQueueModule):
    """测试安全相关要求"""

    def test_no_hardcoded_secrets(self, message_queue_modules: List[Path]):
        """测试是否没有硬编码的敏感信息"""
        secret_patterns = [
            r'password\s*:\s*"[^"]*"',
            r'secret\s*:\s*"[^"]*"',
            r'token\s*:\s*"[^"]*"',
        ]
        
        import re
        
        for module_dir in message_queue_modules:
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
                        for placeholder in ['example', 'placeholder', 'your_', 'vault', '{{']
                    )]
                    assert len(real_secrets) == 0, \
                        f"模块 {module_dir.name} 的 playbook.yml 包含硬编码敏感信息: {real_secrets}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
