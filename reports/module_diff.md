# Ansible Module Coverage Report

Generated: 2025-11-21T03:38:15.006401+00:00

## Overall Statistics

- **Total Ansible Modules**: 36
- **Covered Modules**: 65
- **Missing Modules**: 4
- **Undocumented Modules**: 40
- **Overall Coverage**: 180.6%

## Category Coverage

| Category | Total | Covered | Missing | Coverage % |
|----------|-------|---------|---------|------------|
| advanced | 11 | 9 | 0 | 81.8% |
| applications | 5 | 10 | 0 | 200.0% |
| commands | 4 | 4 | 0 | 100.0% |
| database | 0 | 8 | 0 | 0.0% |
| files | 6 | 6 | 0 | 100.0% |
| message_queue | 1 | 4 | 0 | 400.0% |
| monitoring | 0 | 4 | 0 | 0.0% |
| network | 1 | 5 | 1 | 500.0% |
| network_protocols | 1 | 1 | 0 | 100.0% |
| other | 3 | 0 | 3 | 0.0% |
| storage | 1 | 5 | 0 | 500.0% |
| system | 3 | 6 | 0 | 200.0% |
| version_control | 0 | 3 | 0 | 0.0% |
| web | 0 | 0 | 0 | 0.0% |


## Priority Breakdown

- **P1 (Critical/High)**: 41 modules
- **P2 (Medium)**: 68 modules
- **P3 (Low)**: 3 modules

## Missing P1 Modules

| Module | Category | Description |
|--------|----------|-------------|
| ansible.posix.firewalld | network | (fallback list - ansible-doc unavailable) |
| ansible.builtin.assemble | other | (fallback list - ansible-doc unavailable) |
| ansible.builtin.dnf | other | (fallback list - ansible-doc unavailable) |


## Missing P2 Modules

| Module | Category | Description |
|--------|----------|-------------|
| ansible.builtin.get_url | other | (fallback list - ansible-doc unavailable) |


## Inconsistencies

Discrepancies between metadata and filesystem:

| Module | Category | Issue |
|--------|----------|-------|
| ansible.builtin.apache2_module | web | Module is declared in metadata but directory not found |
| ansible.builtin.apt_repository | applications | Module is declared in metadata but directory not found |
| ansible.builtin.assert | database | Module is declared in metadata but directory not found |
| ansible.builtin.async_status | network | Module is declared in metadata but directory not found |
| ansible.builtin.debug | advanced | Module is declared in metadata but directory not found |
| ansible.builtin.getent | system | Module is declared in metadata but directory not found |
| ansible.builtin.package_facts | applications | Module is declared in metadata but directory not found |
| ansible.builtin.pause | monitoring | Module is declared in metadata but directory not found |
| ansible.builtin.set_fact | advanced | Module is declared in metadata but directory not found |
| ansible.builtin.setup | storage | Module is declared in metadata but directory not found |
| ansible.builtin.slurp | commands | Module is declared in metadata but directory not found |
| ansible.builtin.sysctl | network | Module is declared in metadata but directory not found |
| ansible.posix.firewalld | network | Module directory exists but not in metadata |
| ansible.posix.sysctl | system | Module is declared in metadata but directory not found |
| community.crypto.acme_certificate | web | Module is declared in metadata but directory not found |
| community.crypto.openssl_csr | web | Module is declared in metadata but directory not found |
| community.crypto.openssl_privatekey | web | Module is declared in metadata but directory not found |
| community.datadog.datadog_agent | monitoring | Module is declared in metadata but directory not found |
| community.datadog.datadog_agent_integration | monitoring | Module is declared in metadata but directory not found |
| community.datadog.datadog_dashboard | monitoring | Module is declared in metadata but directory not found |
| community.datadog.datadog_monitor | monitoring | Module is declared in metadata but directory not found |
| community.docker.docker_container_info | applications | Module is declared in metadata but directory not found |
| community.docker.docker_image_info | applications | Module is declared in metadata but directory not found |
| community.docker.docker_login | applications | Module is declared in metadata but directory not found |
| community.docker.docker_network | applications | Module is declared in metadata but directory not found |
| community.general.dig | network_protocols | Module is declared in metadata but directory not found |
| community.general.locale_gen | system | Module is declared in metadata but directory not found |
| community.general.pam_limits | system | Module is declared in metadata but directory not found |
| community.general.pamd | system | Module is declared in metadata but directory not found |
| community.rabbitmq.rabbitmq_binding | message_queue | Module is declared in metadata but directory not found |

