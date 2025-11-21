"""Web Services (Nginx) Playbooks 结构与文档校验"""

from pathlib import Path
from typing import List
import pytest
import yaml

PLAYBOOKS_ROOT = Path(__file__).parent.parent.parent / "ansible-playbooks"
WEB_SERVICES = "web-services"

WEB_SERVICES_PLAYBOOKS = [
    "nginx-install-configure.yml",
    "nginx-vhost-https.yml",
    "nginx-loadbalancer.yml",
    "nginx-reverse-proxy.yml",
]

WEB_SERVICES_TEMPLATES = [
    "nginx.conf.j2",
    "virtual_host.conf.j2",
    "ssl.conf.j2",
    "load_balancer.conf.j2",
    "reverse_proxy.conf.j2",
    "fastcgi_params.j2",
    "upstream_map.j2",
    "upstreams.conf.j2",
    "https_vhost.conf.j2",
    "http_redirect.conf.j2",
    "status.conf.j2",
    "proxy_headers.j2",
    "logrotate.nginx.j2",
]


class TestWebServicesFixtures:
    """提供 Web Services Playbooks 路径的公共 fixture"""

    @pytest.fixture(scope="class")
    def playbooks_root(self) -> Path:
        return PLAYBOOKS_ROOT

    @pytest.fixture(scope="class")
    def web_services_dir(self, playbooks_root: Path) -> Path:
        return playbooks_root / WEB_SERVICES

    @pytest.fixture(scope="class")
    def web_services_playbooks(self, web_services_dir: Path) -> List[Path]:
        return [web_services_dir / pb for pb in WEB_SERVICES_PLAYBOOKS]


class TestWebServicesStructure(TestWebServicesFixtures):
    """校验 web-services 目录结构"""

    def test_web_services_dir_exists(self, web_services_dir: Path) -> None:
        assert web_services_dir.exists(), "web-services 目录不存在"
        assert web_services_dir.is_dir(), "web-services 不是目录"

    def test_web_services_structure(self, web_services_dir: Path) -> None:
        required_subdirs = ["vars", "templates", "roles", "handlers"]
        for subdir in required_subdirs:
            subpath = web_services_dir / subdir
            assert subpath.exists(), f"web-services 缺少 {subdir} 目录"
            assert subpath.is_dir(), f"web-services/{subdir} 不是目录"

    def test_web_services_roles_structure(self, web_services_dir: Path) -> None:
        roles_dir = web_services_dir / "roles"
        required_roles = ["nginx_common", "nginx_ssl", "nginx_proxy"]
        for role in required_roles:
            role_dir = roles_dir / role
            assert role_dir.exists(), f"web-services/roles 缺少 {role} 角色"
            assert role_dir.is_dir(), f"web-services/roles/{role} 不是目录"
            
            # 检查角色子目录
            for subdir in ["tasks", "templates", "handlers", "vars", "defaults", "meta"]:
                subpath = role_dir / subdir
                assert subpath.exists(), f"web-services/roles/{role} 缺少 {subdir} 目录"


class TestWebServicesPlaybooks(TestWebServicesFixtures):
    """校验 Web Services playbooks"""

    def test_all_web_services_playbooks_exist(self, web_services_playbooks: List[Path]) -> None:
        for playbook in web_services_playbooks:
            assert playbook.exists(), f"缺少 web-services playbook: {playbook.name}"

    def test_nginx_install_configure_content(self, web_services_dir: Path) -> None:
        playbook = web_services_dir / "nginx-install-configure.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "nginx" in content.lower(), "nginx-install-configure.yml 应包含 Nginx 相关配置"
        assert "nginx_common" in content, "nginx-install-configure.yml 应使用 nginx_common 角色"
        
        # 检查中文注释
        assert "教学声明" in content, "nginx-install-configure.yml 应包含中文教学声明"
        assert "安装" in content, "nginx-install-configure.yml 应包含安装相关中文注释"
        
        # 检查 handlers
        assert "handlers" in content, "nginx-install-configure.yml 应包含 handlers"
        
        # 检查 vars_files
        assert "vars_files" in content, "nginx-install-configure.yml 应引用 vars_files"
        assert "vars/default.yml" in content, "nginx-install-configure.yml 应引用 vars/default.yml"

    def test_nginx_vhost_https_content(self, web_services_dir: Path) -> None:
        playbook = web_services_dir / "nginx-vhost-https.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "community.crypto" in content, "nginx-vhost-https.yml 应引用 community.crypto collection"
        assert "nginx_ssl" in content, "nginx-vhost-https.yml 应使用 nginx_ssl 角色"
        assert "https" in content.lower(), "nginx-vhost-https.yml 应包含 HTTPS 配置"
        
        # 检查中文注释
        assert "教学声明" in content, "nginx-vhost-https.yml 应包含中文教学声明"
        assert "SSL" in content or "ssl" in content, "nginx-vhost-https.yml 应包含 SSL 相关配置"

    def test_nginx_loadbalancer_content(self, web_services_dir: Path) -> None:
        playbook = web_services_dir / "nginx-loadbalancer.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "nginx_proxy" in content, "nginx-loadbalancer.yml 应使用 nginx_proxy 角色"
        assert "负载均衡" in content, "nginx-loadbalancer.yml 应包含负载均衡相关中文"
        
        # 检查中文注释
        assert "教学声明" in content, "nginx-loadbalancer.yml 应包含中文教学声明"

    def test_nginx_reverse_proxy_content(self, web_services_dir: Path) -> None:
        playbook = web_services_dir / "nginx-reverse-proxy.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "nginx_proxy" in content, "nginx-reverse-proxy.yml 应使用 nginx_proxy 角色"
        assert "反向代理" in content, "nginx-reverse-proxy.yml 应包含反向代理相关中文"
        
        # 检查中文注释
        assert "教学声明" in content, "nginx-reverse-proxy.yml 应包含中文教学声明"


class TestWebServicesVariables(TestWebServicesFixtures):
    """校验 Web Services 变量文件"""

    def test_web_services_vars_exist(self, web_services_dir: Path) -> None:
        vars_file = web_services_dir / "vars" / "default.yml"
        assert vars_file.exists(), "web-services 缺少 vars/default.yml"

    def test_web_services_vars_content(self, web_services_dir: Path) -> None:
        vars_file = web_services_dir / "vars" / "default.yml"
        content = vars_file.read_text(encoding="utf-8")
        
        # Nginx 安装配置变量
        assert "nginx_enabled" in content, "应包含 Nginx 启用变量"
        assert "nginx_version" in content, "应包含 Nginx 版本变量"
        assert "nginx_install_method" in content, "应包含安装方式变量"
        
        # SSL 配置变量
        assert "nginx_ssl_enabled" in content, "应包含 SSL 启用变量"
        assert "nginx_ssl_protocols" in content, "应包含 SSL 协议变量"
        assert "nginx_ssl_self_signed_enabled" in content, "应包含自签名证书变量"
        
        # 虚拟主机配置
        assert "nginx_vhosts" in content, "应包含虚拟主机配置变量"
        assert "nginx_https_vhosts" in content, "应包含 HTTPS 虚拟主机配置"
        
        # 反向代理配置
        assert "nginx_reverse_proxy_enabled" in content, "应包含反向代理启用变量"
        assert "nginx_reverse_proxy_vhosts" in content, "应包含反向代理配置"
        
        # 负载均衡配置
        assert "nginx_load_balancer_enabled" in content, "应包含负载均衡启用变量"
        assert "nginx_load_balancers" in content, "应包含负载均衡器配置"
        
        # 性能调优
        assert "nginx_worker_processes" in content, "应包含 worker 进程配置"
        assert "nginx_worker_connections" in content, "应包含 worker 连接数配置"
        
        # 安全配置
        assert "nginx_rate_limit_enabled" in content, "应包含限流配置"
        assert "nginx_security_enabled" in content, "应包含安全配置"
        
        # 缓存配置
        assert "nginx_cache_enabled" in content, "应包含缓存配置"
        
        # 安全警告
        assert "⚠️" in content, "应包含安全警告符号"
        assert "重要提示" in content, "应包含重要提示"


class TestWebServicesTemplates(TestWebServicesFixtures):
    """校验 Web Services 模板文件"""

    def test_web_services_templates_exist(self, web_services_dir: Path) -> None:
        templates_dir = web_services_dir / "templates"
        
        for template in WEB_SERVICES_TEMPLATES:
            template_file = templates_dir / template
            assert template_file.exists(), f"web-services 缺少模板文件: {template}"

    def test_templates_have_chinese_annotations(self, web_services_dir: Path) -> None:
        templates_dir = web_services_dir / "templates"
        config_templates = ["nginx.conf.j2", "ssl.conf.j2", "load_balancer.conf.j2"]
        
        for template in config_templates:
            template_file = templates_dir / template
            if template_file.exists():
                content = template_file.read_text(encoding="utf-8")
                # 配置模板应包含中文注释
                assert any(char >= '\u4e00' and char <= '\u9fff' for char in content), \
                    f"{template} 应包含中文注释"


class TestWebServicesRoles(TestWebServicesFixtures):
    """校验 Web Services 角色结构"""

    def test_web_services_roles_exist(self, web_services_dir: Path) -> None:
        roles_dir = web_services_dir / "roles"
        required_roles = ["nginx_common", "nginx_ssl", "nginx_proxy"]
        
        for role in required_roles:
            role_dir = roles_dir / role
            assert role_dir.exists(), f"web-services/roles 缺少 {role} 角色"
            assert role_dir.is_dir(), f"web-services/roles/{role} 不是目录"

    def test_web_services_roles_structure(self, web_services_dir: Path) -> None:
        roles_dir = web_services_dir / "roles"
        required_roles = ["nginx_common", "nginx_ssl", "nginx_proxy"]
        
        for role in required_roles:
            role_dir = roles_dir / role
            # 检查角色子目录
            for subdir in ["tasks", "templates", "handlers", "vars", "defaults", "meta"]:
                subpath = role_dir / subdir
                assert subpath.exists(), f"web-services/roles/{role} 缺少 {subdir} 目录"

    def test_web_services_roles_main_tasks(self, web_services_dir: Path) -> None:
        roles_dir = web_services_dir / "roles"
        required_roles = ["nginx_common", "nginx_ssl", "nginx_proxy"]
        
        for role in required_roles:
            main_task = roles_dir / role / "tasks" / "main.yml"
            assert main_task.exists(), f"{role} 角色应包含 tasks/main.yml"

    def test_web_services_roles_meta(self, web_services_dir: Path) -> None:
        roles_dir = web_services_dir / "roles"
        required_roles = ["nginx_common", "nginx_ssl", "nginx_proxy"]
        
        for role in required_roles:
            meta_file = roles_dir / role / "meta" / "main.yml"
            assert meta_file.exists(), f"{role} 角色应包含 meta/main.yml"


class TestWebServicesHandlers(TestWebServicesFixtures):
    """校验 Web Services 处理程序"""

    def test_web_services_handlers_exist(self, web_services_dir: Path) -> None:
        handlers_file = web_services_dir / "handlers" / "main.yml"
        assert handlers_file.exists(), "web-services 应包含 handlers/main.yml"

    def test_web_services_handlers_content(self, web_services_dir: Path) -> None:
        handlers_file = web_services_dir / "handlers" / "main.yml"
        content = handlers_file.read_text(encoding="utf-8")
        
        # Nginx handlers
        assert "nginx" in content.lower(), "handlers 应包含 Nginx 处理程序"
        assert "restart nginx" in content or "reload nginx" in content, \
            "handlers 应包含重启或重载 Nginx 的处理程序"
        assert "verify nginx config" in content or "nginx -t" in content, \
            "handlers 应包含验证 Nginx 配置的处理程序"


class TestWebServicesReadme(TestWebServicesFixtures):
    """校验 Web Services README 文档"""

    def test_web_services_readme_exists(self, web_services_dir: Path) -> None:
        readme = web_services_dir / "README.md"
        assert readme.exists(), "web-services 目录缺少 README.md"

    def test_web_services_readme_content(self, web_services_dir: Path) -> None:
        readme = web_services_dir / "README.md"
        content = readme.read_text(encoding="utf-8")
        
        # 检查主要功能说明
        assert "Nginx" in content, "应说明 Nginx 功能"
        assert "HTTPS" in content or "SSL" in content, "应说明 HTTPS/SSL 功能"
        assert "反向代理" in content or "reverse proxy" in content.lower(), "应说明反向代理功能"
        assert "负载均衡" in content or "load balanc" in content.lower(), "应说明负载均衡功能"
        
        # 检查安装方式说明
        assert "包管理器" in content or "package" in content, "应说明包管理器安装"
        assert "源码" in content or "source" in content, "应说明源码安装"
        
        # 检查使用示例
        assert "ansible-playbook" in content, "应包含 ansible-playbook 命令示例"
        assert "--syntax-check" in content, "应提供语法检查示例"
        assert "--tags" in content, "应提供标签使用示例"
        
        # 检查安全最佳实践
        assert "安全" in content or "security" in content.lower(), "应包含安全建议"
        
        # 检查故障排查
        assert "故障排查" in content or "troubleshooting" in content.lower(), "应包含故障排查章节"


class TestWebServicesPlaybookSyntax(TestWebServicesFixtures):
    """校验 Web Services playbook 语法"""

    def test_web_services_playbooks_yaml_valid(self, web_services_playbooks: List[Path]) -> None:
        for playbook in web_services_playbooks:
            try:
                yaml.safe_load(playbook.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                pytest.fail(f"{playbook.name} YAML 语法错误: {e}")

    def test_web_services_playbooks_structure(self, web_services_playbooks: List[Path]) -> None:
        for playbook in web_services_playbooks:
            content = yaml.safe_load(playbook.read_text(encoding="utf-8"))
            if isinstance(content, list):
                for play in content:
                    if isinstance(play, dict):
                        assert "hosts" in play, f"{playbook.name} 中的 play 应定义 hosts"
                        assert "gather_facts" in play, f"{playbook.name} 应启用 gather_facts"
                        assert "become" in play, f"{playbook.name} 应使用 become 权限提升"
                        assert "vars_files" in play, f"{playbook.name} 应引用 vars_files"
                        assert "handlers" in play, f"{playbook.name} 应定义 handlers"
                        assert "tasks" in play, f"{playbook.name} 应包含 tasks"

    def test_web_services_playbooks_error_handling(self, web_services_playbooks: List[Path]) -> None:
        for playbook in web_services_playbooks:
            content = playbook.read_text(encoding="utf-8")
            # 检查是否包含错误处理
            assert "block:" in content or "rescue:" in content, \
                f"{playbook.name} 应使用 block/rescue 进行错误处理"
            assert "assert:" in content or "ansible.builtin.assert" in content, \
                f"{playbook.name} 应包含前置检查断言"


class TestWebServicesCollections(TestWebServicesFixtures):
    """校验 Web Services playbook 的 collection 引用"""

    def test_https_playbooks_use_crypto_collection(self, web_services_dir: Path) -> None:
        https_playbook = web_services_dir / "nginx-vhost-https.yml"
        content = https_playbook.read_text(encoding="utf-8")
        assert "community.crypto" in content, \
            "nginx-vhost-https.yml 应引用 community.crypto collection"
