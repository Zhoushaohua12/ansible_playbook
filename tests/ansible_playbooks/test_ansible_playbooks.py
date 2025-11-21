"""Ansible Playbooks 应用监控套件的结构与文档校验"""

from pathlib import Path
from typing import Dict, List
import pytest
import yaml
import json

PLAYBOOKS_ROOT = Path(__file__).parent.parent.parent / "ansible-playbooks"
APPLICATION_DEPLOY = "application-deploy"
MONITORING = "monitoring"
MAINTENANCE = "maintenance"
DATABASE = "database"
WEB_SERVICES = "web-services"

APPLICATION_PLAYBOOKS = [
    "docker-install.yml",
    "lamp-stack-deploy.yml", 
    "lnmp-stack-deploy.yml",
    "nodejs-app-deploy.yml"
]

MONITORING_PLAYBOOKS = [
    "prometheus-install.yml",
    "elk-stack-install.yml"
]

MAINTENANCE_PLAYBOOKS = [
    "backup-strategy.yml"
]

DATABASE_PLAYBOOKS = [
    "mysql-5.7-install.yml",
    "mysql-8.0-install.yml",
    "mysql-master-slave.yml",
    "postgresql-install.yml",
    "postgresql-backup.yml"
]

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
]

REQUIRED_COLLECTIONS = [
    "community.docker",
    "community.mysql", 
    "community.general",
    "community.postgresql",
    "community.crypto",
]


class TestAnsiblePlaybooksFixtures:
    """提供 Ansible Playbooks 路径的公共 fixture"""

    @pytest.fixture(scope="class")
    def playbooks_root(self) -> Path:
        return PLAYBOOKS_ROOT

    @pytest.fixture(scope="class")
    def application_deploy_dir(self, playbooks_root: Path) -> Path:
        return playbooks_root / APPLICATION_DEPLOY

    @pytest.fixture(scope="class")
    def monitoring_dir(self, playbooks_root: Path) -> Path:
        return playbooks_root / MONITORING

    @pytest.fixture(scope="class")
    def maintenance_dir(self, playbooks_root: Path) -> Path:
        return playbooks_root / MAINTENANCE

    @pytest.fixture(scope="class")
    def database_dir(self, playbooks_root: Path) -> Path:
        return playbooks_root / DATABASE

    @pytest.fixture(scope="class")
    def web_services_dir(self, playbooks_root: Path) -> Path:
        return playbooks_root / WEB_SERVICES

    @pytest.fixture(scope="class")
    def application_playbooks(self, application_deploy_dir: Path) -> List[Path]:
        return [application_deploy_dir / pb for pb in APPLICATION_PLAYBOOKS]

    @pytest.fixture(scope="class")
    def monitoring_playbooks(self, monitoring_dir: Path) -> List[Path]:
        return [monitoring_dir / pb for pb in MONITORING_PLAYBOOKS]

    @pytest.fixture(scope="class")
    def maintenance_playbooks(self, maintenance_dir: Path) -> List[Path]:
        return [maintenance_dir / pb for pb in MAINTENANCE_PLAYBOOKS]

    @pytest.fixture(scope="class")
    def database_playbooks(self, database_dir: Path) -> List[Path]:
        return [database_dir / pb for pb in DATABASE_PLAYBOOKS]

    @pytest.fixture(scope="class")
    def web_services_playbooks(self, web_services_dir: Path) -> List[Path]:
        return [web_services_dir / pb for pb in WEB_SERVICES_PLAYBOOKS]


class TestAnsiblePlaybooksStructure(TestAnsiblePlaybooksFixtures):
    """校验 ansible-playbooks 目录结构"""

    def test_playbooks_root_exists(self, playbooks_root: Path) -> None:
        assert playbooks_root.exists(), "ansible-playbooks 目录不存在"

    def test_main_categories_exist(self, playbooks_root: Path) -> None:
        for category in [APPLICATION_DEPLOY, MONITORING, MAINTENANCE, DATABASE, WEB_SERVICES]:
            category_dir = playbooks_root / category
            assert category_dir.exists(), f"缺少 {category} 目录"
            assert category_dir.is_dir(), f"{category} 不是目录"

    def test_application_deploy_structure(self, application_deploy_dir: Path) -> None:
        required_subdirs = ["vars", "templates", "roles", "handlers"]
        for subdir in required_subdirs:
            subpath = application_deploy_dir / subdir
            assert subpath.exists(), f"application-deploy 缺少 {subdir} 目录"
            assert subpath.is_dir(), f"application-deploy/{subdir} 不是目录"

    def test_monitoring_structure(self, monitoring_dir: Path) -> None:
        required_subdirs = ["vars", "templates", "roles", "handlers"]
        for subdir in required_subdirs:
            subpath = monitoring_dir / subdir
            assert subpath.exists(), f"monitoring 缺少 {subdir} 目录"
            assert subpath.is_dir(), f"monitoring/{subdir} 不是目录"

    def test_maintenance_structure(self, maintenance_dir: Path) -> None:
        required_subdirs = ["vars", "templates", "roles", "handlers"]
        for subdir in required_subdirs:
            subpath = maintenance_dir / subdir
            assert subpath.exists(), f"maintenance 缺少 {subdir} 目录"
            assert subpath.is_dir(), f"maintenance/{subdir} 不是目录"

    def test_monitoring_roles_structure(self, monitoring_dir: Path) -> None:
        roles_dir = monitoring_dir / "roles"
        required_roles = ["prometheus", "elk"]
        for role in required_roles:
            role_dir = roles_dir / role
            assert role_dir.exists(), f"monitoring/roles 缺少 {role} 角色"
            assert role_dir.is_dir(), f"monitoring/roles/{role} 不是目录"
            
            # 检查角色子目录
            for subdir in ["tasks", "templates", "handlers", "vars", "defaults", "meta"]:
                subpath = role_dir / subdir
                assert subpath.exists(), f"monitoring/roles/{role} 缺少 {subdir} 目录"

    def test_maintenance_roles_structure(self, maintenance_dir: Path) -> None:
        roles_dir = maintenance_dir / "roles"
        required_roles = ["filesystem_backup", "database_backup", "cloud_sync"]
        for role in required_roles:
            role_dir = roles_dir / role
            assert role_dir.exists(), f"maintenance/roles 缺少 {role} 角色"
            assert role_dir.is_dir(), f"maintenance/roles/{role} 不是目录"
            
            # 检查角色子目录
            for subdir in ["tasks", "templates", "handlers", "vars", "defaults", "meta"]:
                subpath = role_dir / subdir
                assert subpath.exists(), f"maintenance/roles/{role} 缺少 {subdir} 目录"


class TestApplicationDeployPlaybooks(TestAnsiblePlaybooksFixtures):
    """校验应用部署 playbooks"""

    def test_all_application_playbooks_exist(self, application_playbooks: List[Path]) -> None:
        for playbook in application_playbooks:
            assert playbook.exists(), f"缺少应用部署 playbook: {playbook.name}"

    def test_docker_install_content(self, application_deploy_dir: Path) -> None:
        playbook = application_deploy_dir / "docker-install.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "community.docker" in content, "docker-install.yml 应引用 community.docker collection"
        assert "docker" in content.lower(), "docker-install.yml 应包含 Docker 相关任务"
        assert "docker-compose" in content, "docker-install.yml 应支持 Docker Compose"
        
        # 检查中文注释
        assert "教学声明" in content, "docker-install.yml 应包含中文教学声明"
        assert "安装" in content, "docker-install.yml 应包含安装相关中文注释"

    def test_lamp_stack_deploy_content(self, application_deploy_dir: Path) -> None:
        playbook = application_deploy_dir / "lamp-stack-deploy.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "apache2" in content, "lamp-stack-deploy.yml 应包含 Apache 安装"
        assert "php" in content.lower(), "lamp-stack-deploy.yml 应包含 PHP 配置"
        assert "mysql" in content.lower(), "lamp-stack-deploy.yml 应包含 MySQL 配置"
        
        # 检查中文注释
        assert "教学声明" in content, "lamp-stack-deploy.yml 应包含中文教学声明"
        assert "LAMP 栈" in content, "lamp-stack-deploy.yml 应包含 LAMP 栈相关中文"

    def test_lnmp_stack_deploy_content(self, application_deploy_dir: Path) -> None:
        playbook = application_deploy_dir / "lnmp-stack-deploy.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "nginx" in content, "lnmp-stack-deploy.yml 应包含 Nginx 配置"
        assert "php-fpm" in content, "lnmp-stack-deploy.yml 应包含 PHP-FPM 配置"
        assert "mysql" in content.lower(), "lnmp-stack-deploy.yml 应包含 MySQL 配置"
        
        # 检查中文注释
        assert "教学声明" in content, "lnmp-stack-deploy.yml 应包含中文教学声明"
        assert "LNMP 栈" in content, "lnmp-stack-deploy.yml 应包含 LNMP 栈相关中文"

    def test_nodejs_app_deploy_content(self, application_deploy_dir: Path) -> None:
        playbook = application_deploy_dir / "nodejs-app-deploy.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "nodejs" in content.lower(), "nodejs-app-deploy.yml 应包含 Node.js 配置"
        assert "pm2" in content.lower(), "nodejs-app-deploy.yml 应支持 PM2 进程管理"
        assert "systemd" in content, "nodejs-app-deploy.yml 应支持 systemd 服务"
        
        # 检查中文注释
        assert "教学声明" in content, "nodejs-app-deploy.yml 应包含中文教学声明"
        assert "Node.js" in content, "nodejs-app-deploy.yml 应包含 Node.js 相关中文"


class TestMonitoringPlaybooks(TestAnsiblePlaybooksFixtures):
    """校验监控系统 playbooks"""

    def test_all_monitoring_playbooks_exist(self, monitoring_playbooks: List[Path]) -> None:
        for playbook in monitoring_playbooks:
            assert playbook.exists(), f"缺少监控 playbook: {playbook.name}"

    def test_prometheus_install_content(self, monitoring_dir: Path) -> None:
        playbook = monitoring_dir / "prometheus-install.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "prometheus" in content.lower(), "prometheus-install.yml 应包含 Prometheus 配置"
        assert "node_exporter" in content, "prometheus-install.yml 应包含 Node Exporter"
        assert "alertmanager" in content, "prometheus-install.yml 应包含 AlertManager"
        
        # 检查中文注释
        assert "教学声明" in content, "prometheus-install.yml 应包含中文教学声明"
        assert "监控" in content, "prometheus-install.yml 应包含监控相关中文"

    def test_elk_stack_install_content(self, monitoring_dir: Path) -> None:
        playbook = monitoring_dir / "elk-stack-install.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "elasticsearch" in content.lower(), "elk-stack-install.yml 应包含 Elasticsearch"
        assert "logstash" in content.lower(), "elk-stack-install.yml 应包含 Logstash"
        assert "kibana" in content.lower(), "elk-stack-install.yml 应包含 Kibana"
        assert "filebeat" in content.lower(), "elk-stack-install.yml 应包含 Filebeat"
        
        # 检查中文注释
        assert "教学声明" in content, "elk-stack-install.yml 应包含中文教学声明"
        assert "ELK 栈" in content, "elk-stack-install.yml 应包含 ELK 栈相关中文"


class TestMaintenancePlaybooks(TestAnsiblePlaybooksFixtures):
    """校验维护策略 playbooks"""

    def test_all_maintenance_playbooks_exist(self, maintenance_playbooks: List[Path]) -> None:
        for playbook in maintenance_playbooks:
            assert playbook.exists(), f"缺少维护 playbook: {playbook.name}"

    def test_backup_strategy_content(self, maintenance_dir: Path) -> None:
        playbook = maintenance_dir / "backup-strategy.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "filesystem_backup" in content, "backup-strategy.yml 应包含文件系统备份"
        assert "database_backup" in content, "backup-strategy.yml 应包含数据库备份"
        assert "cloud_sync" in content, "backup-strategy.yml 应包含云同步"
        
        # 检查中文注释
        assert "教学声明" in content, "backup-strategy.yml 应包含中文教学声明"
        assert "备份" in content, "backup-strategy.yml 应包含备份相关中文"


class TestVariableFiles(TestAnsiblePlaybooksFixtures):
    """校验变量文件"""

    def test_application_deploy_vars(self, application_deploy_dir: Path) -> None:
        vars_file = application_deploy_dir / "vars" / "default.yml"
        assert vars_file.exists(), "application-deploy 缺少 vars/default.yml"
        
        content = vars_file.read_text(encoding="utf-8")
        assert "docker_enabled" in content, "应包含 Docker 配置变量"
        assert "lamp_enabled" in content, "应包含 LAMP 配置变量"
        assert "lnmp_enabled" in content, "应包含 LNMP 配置变量"
        assert "nodejs_enabled" in content, "应包含 Node.js 配置变量"
        
        # 检查安全警告
        assert "⚠️" in content, "应包含安全警告符号"
        assert "重要提示" in content, "应包含重要提示"

    def test_monitoring_vars(self, monitoring_dir: Path) -> None:
        vars_file = monitoring_dir / "vars" / "default.yml"
        assert vars_file.exists(), "monitoring 缺少 vars/default.yml"
        
        content = vars_file.read_text(encoding="utf-8")
        assert "prometheus_enabled" in content, "应包含 Prometheus 配置变量"
        assert "elasticsearch_version" in content, "应包含 Elasticsearch 版本变量"
        assert "logstash_version" in content, "应包含 Logstash 版本变量"
        assert "kibana_version" in content, "应包含 Kibana 版本变量"
        
        # 检查安全警告
        assert "⚠️" in content, "应包含安全警告符号"
        assert "重要提示" in content, "应包含重要提示"

    def test_maintenance_vars(self, maintenance_dir: Path) -> None:
        vars_file = maintenance_dir / "vars" / "default.yml"
        assert vars_file.exists(), "maintenance 缺少 vars/default.yml"
        
        content = vars_file.read_text(encoding="utf-8")
        assert "backup_enabled" in content, "应包含备份配置变量"
        assert "filesystem_backup_enabled" in content, "应包含文件系统备份变量"
        assert "database_backup_enabled" in content, "应包含数据库备份变量"
        assert "cloud_sync_enabled" in content, "应包含云同步变量"
        
        # 检查安全警告
        assert "⚠️" in content, "应包含安全警告符号"
        assert "重要提示" in content, "应包含重要提示"


class TestTemplateFiles(TestAnsiblePlaybooksFixtures):
    """校验模板文件"""

    def test_application_deploy_templates(self, application_deploy_dir: Path) -> None:
        templates_dir = application_deploy_dir / "templates"
        required_templates = [
            "daemon.json.j2",
            "php.ini.j2", 
            "apache-vhost.conf.j2",
            "nginx-lnmp.conf.j2",
            "nodejs.service.j2"
        ]
        
        for template in required_templates:
            template_file = templates_dir / template
            assert template_file.exists(), f"application-deploy 缺少模板文件: {template}"

    def test_monitoring_templates(self, monitoring_dir: Path) -> None:
        templates_dir = monitoring_dir / "templates"
        required_templates = [
            "prometheus.yml.j2",
            "alertmanager.yml.j2",
            "elasticsearch.yml.j2",
            "logstash.conf.j2",
            "kibana.yml.j2",
            "filebeat.yml.j2"
        ]
        
        for template in required_templates:
            template_file = templates_dir / template
            assert template_file.exists(), f"monitoring 缺少模板文件: {template}"

    def test_maintenance_templates(self, maintenance_dir: Path) -> None:
        templates_dir = maintenance_dir / "templates"
        required_templates = [
            "filesystem_backup.sh.j2",
            "database_backup.sh.j2",
            "cloud_sync.sh.j2",
            "backup_crontab.j2"
        ]
        
        for template in required_templates:
            template_file = templates_dir / template
            assert template_file.exists(), f"maintenance 缺少模板文件: {template}"


class TestReadmeFiles(TestAnsiblePlaybooksFixtures):
    """校验 README 文件"""

    def test_main_readme_exists(self, playbooks_root: Path) -> None:
        readme = playbooks_root / "README.md"
        assert readme.exists(), "ansible-playbooks 根目录缺少 README.md"

    def test_category_readmes_exist(self, playbooks_root: Path) -> None:
        for category in [APPLICATION_DEPLOY, MONITORING, MAINTENANCE, DATABASE, WEB_SERVICES]:
            readme = playbooks_root / category / "README.md"
            assert readme.exists(), f"{category} 目录缺少 README.md"

    def test_main_readme_content(self, playbooks_root: Path) -> None:
        readme = playbooks_root / "README.md"
        content = readme.read_text(encoding="utf-8")
        
        # 检查主要组件说明
        assert "应用部署" in content, "应说明应用部署功能"
        assert "监控系统" in content, "应说明监控系统功能"
        assert "维护策略" in content, "应说明维护策略功能"
        
        # 检查快速开始
        assert "快速开始" in content, "应包含快速开始章节"
        assert "ansible-playbook" in content, "应包含 ansible-playbook 命令示例"

    def test_application_deploy_readme_content(self, application_deploy_dir: Path) -> None:
        readme = application_deploy_dir / "README.md"
        content = readme.read_text(encoding="utf-8")
        
        # 检查部署说明
        assert "Docker" in content, "应说明 Docker 部署"
        assert "LAMP" in content, "应说明 LAMP 栈部署"
        assert "LNMP" in content, "应说明 LNMP 栈部署"
        assert "Node.js" in content, "应说明 Node.js 部署"
        
        # 检查使用示例
        assert "--syntax-check" in content, "应提供语法检查示例"
        assert "ansible-playbook" in content, "应包含 ansible-playbook 命令"

    def test_monitoring_readme_content(self, monitoring_dir: Path) -> None:
        readme = monitoring_dir / "README.md"
        content = readme.read_text(encoding="utf-8")
        
        # 检查监控说明
        assert "Prometheus" in content, "应说明 Prometheus 监控"
        assert "ELK" in content, "应说明 ELK 栈"
        assert "告警" in content, "应说明告警功能"
        
        # 检查使用示例
        assert "--syntax-check" in content, "应提供语法检查示例"
        assert "ansible-playbook" in content, "应包含 ansible-playbook 命令"

    def test_maintenance_readme_content(self, maintenance_dir: Path) -> None:
        readme = maintenance_dir / "README.md"
        content = readme.read_text(encoding="utf-8")
        
        # 检查备份说明
        assert "文件系统备份" in content, "应说明文件系统备份"
        assert "数据库备份" in content, "应说明数据库备份"
        assert "云同步" in content, "应说明云同步功能"
        
        # 检查使用示例
        assert "--syntax-check" in content, "应提供语法检查示例"
        assert "ansible-playbook" in content, "应包含 ansible-playbook 命令"


class TestCollectionsReferences(TestAnsiblePlaybooksFixtures):
    """校验 Ansible Collections 引用"""

    def test_docker_collection_reference(self, application_deploy_dir: Path) -> None:
        docker_playbook = application_deploy_dir / "docker-install.yml"
        content = docker_playbook.read_text(encoding="utf-8")
        assert "community.docker" in content, "docker-install.yml 应引用 community.docker collection"

    def test_mysql_collection_reference(self, application_deploy_dir: Path) -> None:
        lamp_playbook = application_deploy_dir / "lamp-stack-deploy.yml"
        content = lamp_playbook.read_text(encoding="utf-8")
        assert "community.mysql" in content, "lamp-stack-deploy.yml 应引用 community.mysql collection"

    def test_required_collections_mentioned(self, playbooks_root: Path) -> None:
        readme = playbooks_root / "README.md"
        content = readme.read_text(encoding="utf-8")
        
        for collection in REQUIRED_COLLECTIONS:
            assert collection in content, f"README.md 应提及 {collection} collection"


class TestChineseDocumentation(TestAnsiblePlaybooksFixtures):
    """校验中文文档完整性"""

    def test_chinese_comments_in_playbooks(self, application_playbooks: List[Path]) -> None:
        for playbook in application_playbooks:
            content = playbook.read_text(encoding="utf-8")
            assert "教学声明" in content, f"{playbook.name} 应包含中文教学声明"
            assert "⚠️" in content, f"{playbook.name} 应包含警告符号"

    def test_chinese_warnings_in_vars(self, playbooks_root: Path) -> None:
        for category in [APPLICATION_DEPLOY, MONITORING, MAINTENANCE, DATABASE, WEB_SERVICES]:
            vars_file = playbooks_root / category / "vars" / "default.yml"
            content = vars_file.read_text(encoding="utf-8")
            assert "⚠️ 重要提示" in content or "⚠️" in content, f"{category}/vars/default.yml 应包含中文重要提示"

    def test_chinese_readmes(self, playbooks_root: Path) -> None:
        for category in [APPLICATION_DEPLOY, MONITORING, MAINTENANCE, DATABASE, WEB_SERVICES]:
            readme = playbooks_root / category / "README.md"
            content = readme.read_text(encoding="utf-8")
            assert "教学" in content or "学习" in content, f"{category}/README.md 应声明教学用途"


class TestPlaybookSyntax(TestAnsiblePlaybooksFixtures):
    """校验 playbook 语法结构"""

    def test_playbook_yaml_valid(self, application_playbooks: List[Path]) -> None:
        for playbook in application_playbooks:
            try:
                yaml.safe_load(playbook.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                pytest.fail(f"{playbook.name} YAML 语法错误: {e}")

    def test_playbook_has_hosts(self, application_playbooks: List[Path]) -> None:
        for playbook in application_playbooks:
            content = yaml.safe_load(playbook.read_text(encoding="utf-8"))
            if isinstance(content, list):
                for play in content:
                    if isinstance(play, dict):
                        assert "hosts" in play, f"{playbook.name} 中的 play 应定义 hosts"

    def test_playbook_has_become(self, application_playbooks: List[Path]) -> None:
        for playbook in application_playbooks:
            content = yaml.safe_load(playbook.read_text(encoding="utf-8"))
            if isinstance(content, list):
                for play in content:
                    if isinstance(play, dict):
                        assert play.get("become", True), f"{playbook.name} 应使用 become 权限提升"

    def test_playbook_has_vars_files(self, application_playbooks: List[Path]) -> None:
        for playbook in application_playbooks:
            content = yaml.safe_load(playbook.read_text(encoding="utf-8"))
            if isinstance(content, list):
                for play in content:
                    if isinstance(play, dict):
                        assert "vars_files" in play, f"{playbook.name} 应引用 vars_files"


class TestRoleStructure(TestAnsiblePlaybooksFixtures):
    """校验角色结构"""

    def test_prometheus_role_main_task(self, monitoring_dir: Path) -> None:
        main_task = monitoring_dir / "roles" / "prometheus" / "tasks" / "main.yml"
        assert main_task.exists(), "prometheus 角色应包含 tasks/main.yml"

    def test_prometheus_role_templates(self, monitoring_dir: Path) -> None:
        prometheus_templates = monitoring_dir / "roles" / "prometheus" / "templates"
        required_templates = [
            "prometheus.service.j2",
            "alertmanager.service.j2",
            "node_exporter.service.j2",
            "blackbox_exporter.service.j2"
        ]
        
        for template in required_templates:
            template_file = prometheus_templates / template
            assert template_file.exists(), f"prometheus 角色缺少模板: {template}"

    def test_maintenance_roles_main_tasks(self, maintenance_dir: Path) -> None:
        roles = ["filesystem_backup", "database_backup", "cloud_sync"]
        for role in roles:
            main_task = maintenance_dir / "roles" / role / "tasks" / "main.yml"
            assert main_task.exists(), f"{role} 角色应包含 tasks/main.yml"


class TestErrorHandling(TestAnsiblePlaybooksFixtures):
    """校验错误处理"""

    def test_playbooks_have_error_handling(self, application_playbooks: List[Path]) -> None:
        for playbook in application_playbooks:
            content = playbook.read_text(encoding="utf-8")
            # 检查是否包含错误处理相关内容
            assert "failed_when" in content or "ignore_errors" in content or "register" in content, \
                f"{playbook.name} 应包含错误处理机制"

    def test_handlers_defined(self, application_deploy_dir: Path) -> None:
        handlers_dir = application_deploy_dir / "handlers"
        if handlers_dir.exists():
            handlers_files = list(handlers_dir.glob("*.yml"))
            # 至少应该有一些处理程序定义
            assert len(handlers_files) > 0, "application-deploy 应定义一些 handlers"


class TestDatabasePlaybooks(TestAnsiblePlaybooksFixtures):
    """校验数据库 playbooks"""

    def test_all_database_playbooks_exist(self, database_playbooks: List[Path]) -> None:
        for playbook in database_playbooks:
            assert playbook.exists(), f"缺少数据库 playbook: {playbook.name}"

    def test_database_structure(self, database_dir: Path) -> None:
        required_subdirs = ["vars", "templates", "roles", "handlers"]
        for subdir in required_subdirs:
            subpath = database_dir / subdir
            assert subpath.exists(), f"database 缺少 {subdir} 目录"
            assert subpath.is_dir(), f"database/{subdir} 不是目录"

    def test_mysql_57_install_content(self, database_dir: Path) -> None:
        playbook = database_dir / "mysql-5.7-install.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "community.mysql" in content, "mysql-5.7-install.yml 应引用 community.mysql collection"
        assert "mysql" in content.lower(), "mysql-5.7-install.yml 应包含 MySQL 相关配置"
        assert "5.7" in content, "mysql-5.7-install.yml 应明确版本 5.7"
        
        # 检查中文注释
        assert "教学声明" in content, "mysql-5.7-install.yml 应包含中文教学声明"
        assert "数据库" in content, "mysql-5.7-install.yml 应包含数据库相关中文"
        
        # 检查 handlers
        assert "handlers" in content, "mysql-5.7-install.yml 应包含 handlers"
        
        # 检查 vars_files
        assert "vars_files" in content, "mysql-5.7-install.yml 应引用 vars_files"
        assert "vars/default.yml" in content, "mysql-5.7-install.yml 应引用 vars/default.yml"

    def test_mysql_80_install_content(self, database_dir: Path) -> None:
        playbook = database_dir / "mysql-8.0-install.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "community.mysql" in content, "mysql-8.0-install.yml 应引用 community.mysql collection"
        assert "8.0" in content, "mysql-8.0-install.yml 应明确版本 8.0"
        assert "mysql_common" in content, "mysql-8.0-install.yml 应使用 mysql_common 角色"
        
        # 检查中文注释
        assert "教学声明" in content, "mysql-8.0-install.yml 应包含中文教学声明"

    def test_mysql_master_slave_content(self, database_dir: Path) -> None:
        playbook = database_dir / "mysql-master-slave.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "community.mysql" in content, "mysql-master-slave.yml 应引用 community.mysql collection"
        assert "replication" in content.lower(), "mysql-master-slave.yml 应包含复制配置"
        assert "master" in content.lower(), "mysql-master-slave.yml 应包含主服务器配置"
        assert "slave" in content.lower(), "mysql-master-slave.yml 应包含从服务器配置"
        
        # 检查中文注释
        assert "教学声明" in content, "mysql-master-slave.yml 应包含中文教学声明"
        assert "复制" in content, "mysql-master-slave.yml 应包含复制相关中文"
        
        # 检查标签
        assert "--tags replication" in content or "tags:" in content, "mysql-master-slave.yml 应支持标签"

    def test_postgresql_install_content(self, database_dir: Path) -> None:
        playbook = database_dir / "postgresql-install.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "community.postgresql" in content, "postgresql-install.yml 应引用 community.postgresql collection"
        assert "postgresql" in content.lower(), "postgresql-install.yml 应包含 PostgreSQL 配置"
        assert "postgresql_common" in content, "postgresql-install.yml 应使用 postgresql_common 角色"
        
        # 检查中文注释
        assert "教学声明" in content, "postgresql-install.yml 应包含中文教学声明"
        assert "数据库" in content, "postgresql-install.yml 应包含数据库相关中文"

    def test_postgresql_backup_content(self, database_dir: Path) -> None:
        playbook = database_dir / "postgresql-backup.yml"
        content = playbook.read_text(encoding="utf-8")
        
        # 检查关键组件
        assert "community.postgresql" in content, "postgresql-backup.yml 应引用 community.postgresql collection"
        assert "backup" in content.lower(), "postgresql-backup.yml 应包含备份配置"
        assert "postgresql_backup" in content, "postgresql-backup.yml 应使用 postgresql_backup 角色"
        
        # 检查中文注释
        assert "教学声明" in content, "postgresql-backup.yml 应包含中文教学声明"
        assert "备份" in content, "postgresql-backup.yml 应包含备份相关中文"


class TestDatabaseVariables(TestAnsiblePlaybooksFixtures):
    """校验数据库变量文件"""

    def test_database_vars_exist(self, database_dir: Path) -> None:
        vars_file = database_dir / "vars" / "default.yml"
        assert vars_file.exists(), "database 缺少 vars/default.yml"

    def test_database_vars_content(self, database_dir: Path) -> None:
        vars_file = database_dir / "vars" / "default.yml"
        content = vars_file.read_text(encoding="utf-8")
        
        # MySQL 配置变量
        assert "mysql_enabled" in content, "应包含 MySQL 启用变量"
        assert "mysql_version" in content, "应包含 MySQL 版本变量"
        assert "mariadb_enabled" in content, "应包含 MariaDB 启用变量"
        assert "mysql_replication_enabled" in content, "应包含 MySQL 复制变量"
        assert "mysql_backup_enabled" in content, "应包含 MySQL 备份变量"
        
        # PostgreSQL 配置变量
        assert "postgresql_enabled" in content, "应包含 PostgreSQL 启用变量"
        assert "postgresql_version" in content, "应包含 PostgreSQL 版本变量"
        assert "postgresql_replication_enabled" in content, "应包含 PostgreSQL 复制变量"
        assert "postgresql_backup_enabled" in content, "应包含 PostgreSQL 备份变量"
        
        # 安全警告
        assert "⚠️" in content, "应包含安全警告符号"
        assert "重要提示" in content, "应包含重要提示"
        assert "vault_" in content, "应包含 Ansible Vault 变量占位符"


class TestDatabaseTemplates(TestAnsiblePlaybooksFixtures):
    """校验数据库模板文件"""

    def test_mysql_templates_exist(self, database_dir: Path) -> None:
        templates_dir = database_dir / "templates"
        required_templates = [
            "my.cnf.j2",
            "replication.cnf.j2",
            "mysql_backup.sh.j2"
        ]
        
        for template in required_templates:
            template_file = templates_dir / template
            assert template_file.exists(), f"database 缺少 MySQL 模板文件: {template}"

    def test_postgresql_templates_exist(self, database_dir: Path) -> None:
        templates_dir = database_dir / "templates"
        required_templates = [
            "postgresql.conf.j2",
            "pg_hba.conf.j2",
            "postgresql_backup.sh.j2",
            "pgpass.j2"
        ]
        
        for template in required_templates:
            template_file = templates_dir / template
            assert template_file.exists(), f"database 缺少 PostgreSQL 模板文件: {template}"

    def test_templates_have_chinese_annotations(self, database_dir: Path) -> None:
        templates_dir = database_dir / "templates"
        config_templates = ["my.cnf.j2", "postgresql.conf.j2", "pg_hba.conf.j2"]
        
        for template in config_templates:
            template_file = templates_dir / template
            if template_file.exists():
                content = template_file.read_text(encoding="utf-8")
                # 配置模板应包含中文注释
                assert any(char >= '\u4e00' and char <= '\u9fff' for char in content), \
                    f"{template} 应包含中文注释"


class TestDatabaseRoles(TestAnsiblePlaybooksFixtures):
    """校验数据库角色结构"""

    def test_database_roles_exist(self, database_dir: Path) -> None:
        roles_dir = database_dir / "roles"
        required_roles = ["mysql_common", "mysql_replication", "postgresql_common", "postgresql_backup"]
        
        for role in required_roles:
            role_dir = roles_dir / role
            assert role_dir.exists(), f"database/roles 缺少 {role} 角色"
            assert role_dir.is_dir(), f"database/roles/{role} 不是目录"

    def test_database_roles_structure(self, database_dir: Path) -> None:
        roles_dir = database_dir / "roles"
        required_roles = ["mysql_common", "mysql_replication", "postgresql_common", "postgresql_backup"]
        
        for role in required_roles:
            role_dir = roles_dir / role
            # 检查角色子目录
            for subdir in ["tasks", "templates", "handlers", "vars", "defaults", "meta"]:
                subpath = role_dir / subdir
                assert subpath.exists(), f"database/roles/{role} 缺少 {subdir} 目录"

    def test_database_roles_main_tasks(self, database_dir: Path) -> None:
        roles_dir = database_dir / "roles"
        required_roles = ["mysql_common", "mysql_replication", "postgresql_common", "postgresql_backup"]
        
        for role in required_roles:
            main_task = roles_dir / role / "tasks" / "main.yml"
            assert main_task.exists(), f"{role} 角色应包含 tasks/main.yml"

    def test_database_roles_meta(self, database_dir: Path) -> None:
        roles_dir = database_dir / "roles"
        required_roles = ["mysql_common", "mysql_replication", "postgresql_common", "postgresql_backup"]
        
        for role in required_roles:
            meta_file = roles_dir / role / "meta" / "main.yml"
            assert meta_file.exists(), f"{role} 角色应包含 meta/main.yml"


class TestDatabaseHandlers(TestAnsiblePlaybooksFixtures):
    """校验数据库处理程序"""

    def test_database_handlers_exist(self, database_dir: Path) -> None:
        handlers_file = database_dir / "handlers" / "main.yml"
        assert handlers_file.exists(), "database 应包含 handlers/main.yml"

    def test_database_handlers_content(self, database_dir: Path) -> None:
        handlers_file = database_dir / "handlers" / "main.yml"
        content = handlers_file.read_text(encoding="utf-8")
        
        # MySQL handlers
        assert "mysql" in content.lower() or "mariadb" in content.lower(), \
            "handlers 应包含 MySQL/MariaDB 处理程序"
        
        # PostgreSQL handlers
        assert "postgresql" in content.lower(), "handlers 应包含 PostgreSQL 处理程序"


class TestDatabaseReadme(TestAnsiblePlaybooksFixtures):
    """校验数据库 README 文档"""

    def test_database_readme_exists(self, database_dir: Path) -> None:
        readme = database_dir / "README.md"
        assert readme.exists(), "database 目录缺少 README.md"

    def test_database_readme_content(self, database_dir: Path) -> None:
        readme = database_dir / "README.md"
        content = readme.read_text(encoding="utf-8")
        
        # 检查主要功能说明
        assert "MySQL" in content, "应说明 MySQL 功能"
        assert "MariaDB" in content, "应说明 MariaDB 功能"
        assert "PostgreSQL" in content, "应说明 PostgreSQL 功能"
        assert "复制" in content or "replication" in content.lower(), "应说明复制功能"
        assert "备份" in content or "backup" in content.lower(), "应说明备份功能"
        
        # 检查快速开始
        assert "快速开始" in content, "应包含快速开始章节"
        assert "ansible-playbook" in content, "应包含 ansible-playbook 命令示例"
        
        # 检查使用示例
        assert "--syntax-check" in content, "应提供语法检查示例"
        assert "--tags" in content, "应提供标签使用示例"
        
        # 检查安全最佳实践
        assert "安全" in content or "Security" in content, "应包含安全建议"
        assert "Vault" in content, "应说明 Ansible Vault 使用"
        
        # 检查故障排查
        assert "故障排查" in content or "troubleshooting" in content.lower(), "应包含故障排查章节"


class TestDatabasePlaybookSyntax(TestAnsiblePlaybooksFixtures):
    """校验数据库 playbook 语法"""

    def test_database_playbooks_yaml_valid(self, database_playbooks: List[Path]) -> None:
        for playbook in database_playbooks:
            try:
                yaml.safe_load(playbook.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                pytest.fail(f"{playbook.name} YAML 语法错误: {e}")

    def test_database_playbooks_structure(self, database_playbooks: List[Path]) -> None:
        for playbook in database_playbooks:
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

    def test_database_playbooks_error_handling(self, database_playbooks: List[Path]) -> None:
        for playbook in database_playbooks:
            content = playbook.read_text(encoding="utf-8")
            # 检查是否包含错误处理
            assert "block:" in content or "rescue:" in content, \
                f"{playbook.name} 应使用 block/rescue 进行错误处理"
            assert "assert:" in content or "ansible.builtin.assert" in content, \
                f"{playbook.name} 应包含前置检查断言"

    def test_database_playbooks_check_mode_support(self, database_playbooks: List[Path]) -> None:
        for playbook in database_playbooks:
            content = playbook.read_text(encoding="utf-8")
            # 检查是否支持 check_mode
            has_check_mode_guard = "ansible_check_mode" in content or "check_mode:" in content
            # 至少应该在某些任务中考虑 check_mode
            assert has_check_mode_guard or "when:" in content, \
                f"{playbook.name} 应支持或考虑 check_mode"


class TestDatabaseCollections(TestAnsiblePlaybooksFixtures):
    """校验数据库 playbook 的 collection 引用"""

    def test_mysql_playbooks_use_mysql_collection(self, database_dir: Path) -> None:
        mysql_playbooks = [
            "mysql-5.7-install.yml",
            "mysql-8.0-install.yml",
            "mysql-master-slave.yml"
        ]
        
        for playbook_name in mysql_playbooks:
            playbook = database_dir / playbook_name
            content = playbook.read_text(encoding="utf-8")
            assert "community.mysql" in content, \
                f"{playbook_name} 应引用 community.mysql collection"

    def test_postgresql_playbooks_use_postgresql_collection(self, database_dir: Path) -> None:
        pg_playbooks = [
            "postgresql-install.yml",
            "postgresql-backup.yml"
        ]
        
        for playbook_name in pg_playbooks:
            playbook = database_dir / playbook_name
            content = playbook.read_text(encoding="utf-8")
            assert "community.postgresql" in content, \
                f"{playbook_name} 应引用 community.postgresql collection"