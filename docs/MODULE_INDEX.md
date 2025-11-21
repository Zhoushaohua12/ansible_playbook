# 模块索引 (Module Index)

- 生成时间: 2025-11-21T02:02:08.836766+00:00
- 覆盖统计: 15 个章节 / 106 个模块
- 待补充模块: 5 项 (来自 ansible-doc 差异)

## 高级特性总览 (`advanced`)

本章节汇总了在真实生产环境中最常见的 Ansible 高级特性，并配套可运行的 Playbook 示例。每个小节都会说明它要解决的问题、与其他指令的组合方式以及需要避开的陷阱。

**外部依赖**: ansible.builtin

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [Block / Rescue / Always 组合进阶](advanced/block_always/README.md) | Block 允许把多条任务当作原子单元执行，搭配 rescue 和 always 可以在失败时执行补救并保证收尾逻辑始终运行。本示例在同一个 block 内结合 when 条件、循环和日志清理，展示真实生产场景常见的回滚流程。 | `advanced/block_always/playbook.yml` | covered |
| [Block / Rescue / Always](advanced/block_rescue/README.md) | Block 允许你把一组任务视为一个逻辑单元。当其中任一任务失败时，rescue 分支会被触发；无论成功或失败，always 分支都会执行，用于清理或记录状态。 | `advanced/block_rescue/playbook.yml` | covered |
| [Handler 与 Notify](advanced/handlers_notify/README.md) | Handler 是在任务检测到变更时才执行的收尾动作，例如重启服务或刷新缓存。通过 notify 将多个 handler 组合，可以构建清晰的回调链。 | `advanced/handlers_notify/playbook.yml` | covered |
| [import_playbook 模块复用](advanced/import_playbook/README.md) | import_playbook 在 Play 级别引入其他 Playbook，适用于将大型部署拆分成多个阶段或重用通用 Playbook。与 include_* 不同，import_playbook 在解析阶段就完成合并，无法通过 when 动态控制。 | `advanced/import_playbook/playbook.yml` | covered |
| [import_tasks 静态任务复用](advanced/import_tasks/README.md) | ansible.builtin.import_tasks 在解析阶段加载任务文件，适用于需要在多个 Play 中复用同一批任务且希望拥有一致的执行顺序时。本示例展示如何利用 import_tasks 将配置和清理逻辑拆分为独立文件，并结合 when 与变量控制不同环境的执行路径。 | `advanced/import_tasks/playbook.yml` | covered |
| [Include Tasks](advanced/include_tasks/README.md) | include_tasks 按需加载外部任务文件，使 Playbook 得到模块化拆分。相比 import_tasks，它在运行时动态决定是否加载，适合带条件的场景。 | `advanced/include_tasks/playbook.yml` | covered |
| [循环（loop）](advanced/loop_iteration/README.md) | Loop 用于批量执行任务，比 with_items 更直观，并支持 loop_control 自定义迭代变量，提高可读性。 | `advanced/loop_iteration/playbook.yml` | covered |
| [循环矩阵（Loop Matrix）](advanced/loop_matrix/README.md) | 在需要对多维组合执行任务时，可使用 product 过滤器或 subelements 插件构建循环矩阵。本示例展示如何组合区域、环境、服务端口等多组变量，并通过 loop_control.loop_var 提升可读性。 | `advanced/loop_matrix/playbook.yml` | covered |
| [变量与 set_fact](advanced/set_fact_vars/README.md) | set_fact 可在运行时创建或更新变量，常用于整理前一个任务的输出、生成派生值或跨任务复用的结构化数据。 | `advanced/set_fact_vars/playbook.yml` | covered |
| [条件判断（when）](advanced/when_conditions/README.md) | when 让任务只在满足条件时执行，可读取变量、主机 facts 或任意 Jinja2 表达式。通过组合 and、or 以及 in 等操作符，可以精准控制 Play 行为。 | `advanced/when_conditions/playbook.yml` | covered |

## 应用管理模块指南 (`applications`)

应用管理是 DevOps 自动化的核心场景，涵盖软件包安装、容器部署、源码管理等关键操作。Ansible 通过统一的管理接口，支持从传统软件包到现代容器化应用的全生命周期管理。

**外部依赖**: ansible.builtin, community.docker, community.general, kubernetes.core

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [apt 模块使用指南](applications/apt/README.md) | ansible.builtin.apt 模块是专门用于 Debian 系列发行版（如 Debian、Ubuntu、Linux Mint）的包管理工具。该模块提供了完整的 DEB 包管理功能，包括安装、更新、删除软件包，以及管理软件源和软件依赖，是 Debian 生态系统中应用部署的核心工具。 | `applications/apt/playbook.yml` | covered |
| [docker_container 模块使用指南](applications/docker_container/README.md) | community.docker.docker_container 模块用于管理 Docker 容器的生命周期，包括创建、启动、停止、删除等操作。该模块提供了完整的容器管理功能，支持容器配置、网络设置、卷挂载等高级特性。 | `applications/docker_container/playbook.yml` | covered |
| [docker_image 模块使用指南](applications/docker_image/README.md) | community.docker.docker_image 模块用于管理 Docker 镜像的拉取、构建、推送和删除等操作。该模块提供了完整的镜像生命周期管理功能，支持镜像构建、标签管理、仓库推送等高级特性，是容器化部署和 CI/CD 流水线的核心组件。 | `applications/docker_image/playbook.yml` | covered |
| [git 模块使用指南](applications/git/README.md) | ansible.builtin.git 模块用于管理 Git 仓库的克隆、更新和版本控制操作。该模块支持从各种 Git 仓库获取源码，管理分支切换、标签检出等版本控制任务，是持续部署和源码管理的核心工具。 | `applications/git/playbook.yml` | covered |
| [kubernetes 模块使用指南](applications/kubernetes/README.md) | kubernetes.core.k8s 模块用于管理 Kubernetes 资源的创建、更新、删除和查询等操作。该模块提供了完整的 Kubernetes 资源管理功能，支持 Deployment、Service、ConfigMap、Secret、Ingress 等所有 Kubernetes 资源类型，是容器编排和应用部署的核心工具。 | `applications/kubernetes/playbook.yml` | covered |
| [npm 模块使用指南](applications/npm/README.md) | community.general.npm 模块用于管理 Node.js 包的安装、升级和卸载，支持 npm 包、本地包、Git 仓库包等多种安装方式。该模块是前端应用和 Node.js 服务依赖管理的核心工具，适用于项目构建、依赖安装和生产环境部署。 | `applications/npm/playbook.yml` | covered |
| [package 模块使用指南](applications/package/README.md) | ansible.builtin.package 模块是跨平台的通用包管理器，能够根据目标操作系统自动选择合适的包管理工具（如 yum、apt、dnf、zypper 等）。该模块提供了一个统一的接口来管理软件包的安装、更新和删除，是实现跨平台自动化部署的理想选择。 | `applications/package/playbook.yml` | covered |
| [pip 模块使用指南](applications/pip/README.md) | ansible.builtin.pip 模块用于管理 Python 包的安装、升级和卸载，支持 PyPI 包、本地包、Git 仓库包等多种安装方式。该模块是 Python 应用依赖管理的核心工具，适用于虚拟环境管理、应用部署和开发环境配置。 | `applications/pip/playbook.yml` | covered |
| [yum 模块使用指南](applications/yum/README.md) | ansible.builtin.yum 模块是专门用于 Red Hat 系列发行版（如 RHEL、CentOS、Fedora）的包管理工具。该模块提供了完整的 RPM 包管理功能，包括安装、更新、删除软件包，以及管理软件源和软件组，是 Red Hat 生态系统中应用部署的核心工具。 | `applications/yum/playbook.yml` | covered |

## 云资源与多云编排章节 (`cloud`)

本章节聚焦云计算与多云环境中的算力交付，汇总了 AWS、Azure、GCP、OpenStack、阿里云等典型平台的 Ansible Playbook 示例。所有 Playbook 默认以 --check 模式/check_mode: true 执行，帮助读者在没有真实凭证的情况下模拟变更；示例同时提供中文注释、依赖安装说明、认证方式提示，并强调 切勿在仓库中存放真实密钥。

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [阿里云 ECS 模块演练指南](cloud/aliyun_ecs/README.md) | cloud/aliyun_ecs 目录示范 alibaba.cloud.ali_ecs 模块在 ECS 实例规划、网络与标签治理中的用法。所有任务均启用 check_mode: true 与 no_log: true，确保在没有真实访问密钥的环境下安全地学习/演练。 | `cloud/aliyun_ecs/playbook.yml` | covered |
| [AWS EC2 模块演练指南](cloud/aws_ec2/README.md) | cloud/aws_ec2 示例通过 community.aws.ec2_instance 模块演示如何在 AWS 上定义/标记 EC2 实例、绑定网络组件，并在 check_mode: true 下预览所需资源。示例特别适合想要在无真实凭证的环境中，理解实例创建参数、标签治理与安全组依赖的读者。 | `cloud/aws_ec2/playbook.yml` | covered |
| [Azure VM 模块演练指南](cloud/azure_vm/README.md) | cloud/azure_vm 目录使用 azure.azcollection.azure_rm_virtualmachine 模块演示如何以 Dry Run 方式定义虚拟机规格、映像、网络接口与磁盘。通过中文注释与变量模板，帮助团队在本地快速验证服务主体权限与网络规划，实现多订阅/多区域的一致交付。 | `cloud/azure_vm/playbook.yml` | covered |
| [GCP Compute Engine 模块演练指南](cloud/gcp_compute/README.md) | cloud/gcp_compute 目录使用 google.cloud.gcp_compute_instance 模块，在 Dry Run 下定义 GCE 实例、磁盘、网络与标签，帮助团队提前验证 IAM、服务帐号与 VPC 配置。示例包含详尽中文注释，并引导使用 Service Account JSON 与 Ansible Vault 管理密钥。 | `cloud/gcp_compute/playbook.yml` | covered |
| [OpenStack Server 模块演练指南](cloud/openstack_server/README.md) | cloud/openstack_server 示例通过 openstack.cloud.server 模块展示如何结合 clouds.yaml 与 Ansible Vault 在私有云环境下 Dry Run 虚拟机定义。示例涵盖镜像、规格、网络、Keypair、安全组等常见字段，适合在 OpenStack、DevStack 或托管私有云中进行模拟演练。 | `cloud/openstack_server/playbook.yml` | covered |

## 命令执行模块指南 (`commands`)

本章节介绍 Ansible 中五个核心命令执行模块的使用差异、安全风险与最佳实践。这些模块允许在目标主机上执行命令和脚本（包含交互式输入场景），但各自有不同的适用场景和安全考虑。所有示例均包含中文注释，并强调幂等性和安全防护措施。

**外部依赖**: ansible.builtin

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [command 模块使用指南](commands/command/README.md) | ansible.builtin.command 模块在目标主机上直接执行命令，不经过 shell 处理。这是最安全的命令执行方式，避免了 shell 注入风险，适用于执行简单的系统命令。 | `commands/command/playbook.yml` | covered |
| [expect 模块使用指南](commands/expect/README.md) | ansible.builtin.expect 模块用于执行需要交互式输入的命令，自动响应预期的提示信息。适用于无法通过命令行参数传递密码或确认信息的场景，如 passwd、ssh-keygen、mysql_secure_installation 等需要交互确认的命令。 | `commands/expect/playbook.yml` | covered |
| [raw 模块使用指南](commands/raw/README.md) | ansible.builtin.raw 模块直接通过 SSH 在目标主机执行命令，完全绕过 Ansible 的模块系统。适用于目标主机没有 Python 环境、系统处于引导阶段或需要执行底层系统维护的场景。 | `commands/raw/playbook.yml` | covered |
| [script 模块使用指南](commands/script/README.md) | ansible.builtin.script 模块将本地脚本文件传输到远程主机并执行。适用于需要执行复杂脚本逻辑的场景，同时保持脚本的可维护性和版本控制。 | `commands/script/playbook.yml` | covered |
| [shell 模块使用指南](commands/shell/README.md) | ansible.builtin.shell 模块通过目标主机的系统 shell 执行命令，支持管道符、重定向、环境变量等 shell 特性。适用于需要复杂 shell 操作的场景，但需要注意 shell 注入风险。 | `commands/shell/playbook.yml` | covered |

## 数据库模块实践指南 (`database`)

本目录提供主流数据库系统（MySQL、PostgreSQL、MongoDB）的 Ansible 自动化管理示例，涵盖用户管理、数据库创建、权限授予、主从复制等常见运维场景。所有示例均通过 check_mode 或 delegate_to 方式运行，适合在本地环境学习和测试。

**外部依赖**: ansible.builtin, community.mongodb, community.mysql, community.postgresql

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [MongoDB 数据库管理模块使用指南](database/mongodb_db/README.md) | community.mongodb.mongodb_db 模块用于管理 MongoDB 数据库，支持创建、删除数据库等操作。适用于应用部署、数据库初始化、环境清理等场景。 | `database/mongodb_db/playbook.yml` | covered |
| [mongodb_user 模块使用指南](database/mongodb_user/README.md) | community.mongodb.mongodb_user 模块用于管理 MongoDB 数据库的用户账号，包括创建、删除用户，配置角色和权限。适用于 MongoDB 应用部署、用户权限管理、安全加固等场景。 | `database/mongodb_user/playbook.yml` | covered |
| [mysql_db 模块使用指南](database/mysql_db/README.md) | community.mysql.mysql_db 模块用于管理 MySQL 和 MariaDB 数据库，包括创建、删除数据库，导入导出 SQL 文件，设置字符集和排序规则。适用于应用部署、数据库初始化、备份恢复等场景。 | `database/mysql_db/playbook.yml` | covered |
| [MySQL 主从复制管理模块使用指南](database/mysql_replication/README.md) | community.mysql.mysql_replication 模块用于管理 MySQL 主从复制（Replication）配置和状态，支持启动/停止复制、获取复制状态、配置复制参数等操作。适用于高可用架构部署、数据库容灾、读写分离场景。 | `database/mysql_replication/playbook.yml` | covered |
| [mysql_user 模块使用指南](database/mysql_user/README.md) | community.mysql.mysql_user 模块用于管理 MySQL 和 MariaDB 数据库的用户账号，包括创建、删除用户，设置密码，以及授予或撤销数据库权限。适用于自动化数据库用户生命周期管理、应用部署中的权限配置等场景。 | `database/mysql_user/playbook.yml` | covered |
| [postgresql_db 模块使用指南](database/postgresql_db/README.md) | community.postgresql.postgresql_db 模块用于管理 PostgreSQL 数据库，包括创建、删除数据库，设置 owner、encoding、template 等属性。适用于 PostgreSQL 应用部署、数据库初始化、多租户环境管理等场景。 | `database/postgresql_db/playbook.yml` | covered |
| [PostgreSQL 权限管理模块使用指南](database/postgresql_privs/README.md) | community.postgresql.postgresql_privs 模块用于管理 PostgreSQL 数据库对象的权限（GRANT/REVOKE），支持数据库、表、序列、函数、模式等多种对象类型的权限授予和撤销。适用于权限最小化、安全加固、多租户环境、合规审计等场景。 | `database/postgresql_privs/playbook.yml` | covered |
| [postgresql_user 模块使用指南](database/postgresql_user/README.md) | community.postgresql.postgresql_user 模块用于管理 PostgreSQL 数据库用户（角色），包括创建、删除用户，设置密码，以及授予或撤销数据库权限。适用于自动化数据库用户生命周期管理、应用部署中的权限配置、多租户账号隔离等场景。 | `database/postgresql_user/playbook.yml` | covered |

## 文件操作模块实践指南 (`files`)

文件操作是 Ansible 自动化的基础能力，本章节覆盖从基础文件管理到高级同步操作的完整场景： - 文件传输与分发：将配置文件、脚本、静态资源从控制节点分发到远程主机 - 动态配置生成：使用 Jinja2 模板根据主机变量生成个性化配置文件 - 精确配置修改：在不替换整个文件的情况下修改配置项或添加配置行 - 文件状态检查：获取文件属性、权限、大小、修改时间等元数据 - 批量文件管理：创建、删除、设置权限、符号链接等基础文件系统操作 - 文件查找与清理：根据条件查找文件并批…

**外部依赖**: ansible.builtin, ansible.posix

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [archive 模块使用指南](files/archive/README.md) | ansible.builtin.archive 模块用于在远程主机上创建文件和目录的压缩归档。它支持多种压缩格式，适用于应用部署备份、日志归档、配置文件打包等场景。 | `files/archive/playbook.yml` | covered |
| [blockinfile 模块使用指南](files/blockinfile/README.md) | ansible.builtin.blockinfile 模块用于在文件中插入、更新或删除文本块，支持标记文本块、备份文件、验证插入结果等功能。适用于配置文件管理、脚本插入、注释块维护等场景。 | `files/blockinfile/playbook.yml` | covered |
| [copy 模块使用指南](files/copy/README.md) | ansible.builtin.copy 模块用于将文件从控制节点复制到远程主机，或在远程主机内部复制文件。它是最基础的文件分发模块，适用于静态文件传输场景。 | `files/copy/playbook.yml` | covered |
| [fetch 模块使用指南](files/fetch/README.md) | ansible.builtin.fetch 模块用于从远程主机获取文件到控制节点，与 copy 模块方向相反。它主要用于收集日志文件、配置文件备份、系统信息收集等场景。 | `files/fetch/playbook.yml` | covered |
| [file 模块使用指南](files/file/README.md) | ansible.builtin.file 模块用于管理文件、目录、符号链接和硬链接，包括创建、删除、设置权限、更改所有者等基础文件系统操作。 | `files/file/playbook.yml` | covered |
| [find 模块使用指南](files/find/README.md) | ansible.builtin.find 模块用于在远程主机上按条件查找文件或目录。它支持按文件名、大小、修改时间、权限等条件过滤，并可返回详细的文件属性，用于后续任务处理。 | `files/find/playbook.yml` | covered |
| [lineinfile 模块使用指南](files/lineinfile/README.md) | ansible.builtin.lineinfile 模块用于确保文件中存在或修改特定行，非常适合精确修改配置文件而不需要替换整个文件的场景。 | `files/lineinfile/playbook.yml` | covered |
| [replace 模块使用指南](files/replace/README.md) | ansible.builtin.replace 模块用于根据正则表达式替换文件中的内容，支持多行替换、备份文件、验证替换结果等功能。适用于配置文件修改、日志处理、批量文本替换等场景。 | `files/replace/playbook.yml` | covered |
| [stat 模块使用指南](files/stat/README.md) | ansible.builtin.stat 模块用于获取远程文件或目录的状态信息，包括是否存在、权限、所有者、大小、哈希值等。通常与 when 条件、register 和其他文件模块配合使用。 | `files/stat/playbook.yml` | covered |
| [synchronize 模块使用指南](files/synchronize/README.md) | ansible.posix.synchronize 模块基于 rsync 命令实现高效的文件和目录同步，适用于大规模文件传输、增量备份、代码部署等场景。相比 copy 模块，它能显著提升传输速度。 | `files/synchronize/playbook.yml` | covered |
| [template 模块使用指南](files/template/README.md) | ansible.builtin.template 模块将 Jinja2 模板渲染后部署到远程主机，非常适合需要根据变量、主机事实或条件生成动态配置文件的场景。 | `files/template/playbook.yml` | covered |
| [unarchive 模块使用指南](files/unarchive/README.md) | ansible.builtin.unarchive 模块用于解压缩文件到远程主机，支持 tar、zip、gz、bz2、xz 等多种压缩格式。它是应用部署、软件安装、配置文件分发等场景的核心模块。 | `files/unarchive/playbook.yml` | covered |

### 学习路径建议

| 优先级 | 模块 | 前置实践 | 官方文档 | 备注 |
| --- | --- | --- | --- | --- |
| high | `assemble` | copy, template | [link](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/assemble_module.html) | 将碎片化配置组装成完整文件，可接在 copy/template 之后演示差异化发布。 |
| medium | `xattr` | file | [link](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/xattr_module.html) | 补充 ACL/SELinux/自定义元数据场景，延伸 file 模块章节。 |

## 消息队列管理 (`message_queue`)

本章节提供主流消息队列系统（RabbitMQ、Kafka）的 Ansible 自动化管理示例，涵盖用户管理、队列配置、Topic 管理等核心运维场景。

**外部依赖**: ansible.builtin, community.general, community.rabbitmq

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [Kafka Topic 管理](message_queue/kafka_topic/README.md) | 本模块提供 Apache Kafka Topic 的自动化管理功能，支持创建 Topic、配置分区、副本和保留策略。 | `message_queue/kafka_topic/playbook.yml` | covered |
| [RabbitMQ 队列管理](message_queue/rabbitmq_queue/README.md) | 本模块提供 RabbitMQ 队列和交换机的自动化管理功能，支持创建队列、配置参数、绑定交换机和设置路由规则。 | `message_queue/rabbitmq_queue/playbook.yml` | covered |
| [RabbitMQ 用户管理](message_queue/rabbitmq_user/README.md) | 本模块提供 RabbitMQ 用户、虚拟主机和权限的自动化管理功能，支持创建用户、配置权限、管理虚拟主机和标签。 | `message_queue/rabbitmq_user/playbook.yml` | covered |

## 监控模块 (`monitoring`)

本章节提供主流监控系统的 Ansible 集成示例，帮助您快速搭建和维护监控基础设施。

**外部依赖**: ansible.builtin, community.datadog, community.general, community.zabbix

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [Datadog 监控集成](monitoring/datadog/README.md) | 本模块提供 Datadog 云原生监控平台的自动化配置功能，支持基础设施监控、应用性能监控（APM）、日志聚合和告警管理。 | `monitoring/datadog/playbook.yml` | covered |
| [ELK Stack 日志聚合集成](monitoring/elk/README.md) | 本模块提供 ELK (Elasticsearch, Logstash, Kibana) Stack 日志聚合和分析平台的自动化配置功能，支持日志收集、索引管理、可视化和告警。 | `monitoring/elk/playbook.yml` | covered |
| [Nagios 监控集成](monitoring/nagios/README.md) | 本模块提供 Nagios 监控系统的自动化配置功能，支持主机管理、服务监控、告警配置等核心操作。 | `monitoring/nagios/playbook.yml` | covered |
| [Prometheus 监控集成](monitoring/prometheus/README.md) | 本模块提供 Prometheus 开源监控系统的自动化配置功能，支持指标抓取、服务发现、告警规则配置和多目标监控。 | `monitoring/prometheus/playbook.yml` | covered |
| [Splunk 日志管理集成](monitoring/splunk/README.md) | 本模块提供 Splunk 企业级日志聚合和分析平台的自动化配置功能，支持日志转发、索引管理、数据输入配置和 API 集成。 | `monitoring/splunk/playbook.yml` | covered |
| [Zabbix 监控集成](monitoring/zabbix/README.md) | 本模块提供 Zabbix 企业级开源监控系统的自动化配置功能，支持分布式监控、自动发现、模板管理和告警配置。 | `monitoring/zabbix/playbook.yml` | covered |

### 学习路径建议

| 优先级 | 模块 | 前置实践 | 官方文档 | 备注 |
| --- | --- | --- | --- | --- |
| high | `grafana_dashboard` | prometheus_monitoring, datadog_monitoring | [link](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_dashboard_module.html) | 完善监控章节，加入 dashboard 自动化与告警学习路径。 |

## 网络模块实践指南 (`network`)

本章节介绍 Ansible 中网络配置与监控的核心模块，涵盖防火墙规则管理（firewalld/ufw/iptables）、网络连接监控（wait_for）、端口健康探测（port）、静态路由管理（route）、网络接口管理（interface/nmcli）、VLAN 配置（vlan）和网卡绑定（bonding）。这些模块广泛应用于安全加固、容器编排、多层部署、网络配置管理、高可用网络架构等场景，所有示例均包含中文注释和最佳实践说明。

**外部依赖**: ansible.builtin, ansible.posix, community.general

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [网络接口绑定（Bonding）模块使用指南](network/bonding/README.md) | community.general.nmcli 模块用于配置网络接口绑定（Network Interface Bonding），也称为链路聚合或网卡绑定。通过将多个物理网络接口聚合为一个逻辑接口，实现网络冗余、负载均衡和带宽聚合。广泛应用于服务器高可用架构、数据中心网络和关键业务系统。 | `network/bonding/playbook.yml` | covered |
| [firewalld 模块使用指南](network/firewalld/README.md) | community.general.firewalld 模块用于管理 RHEL/CentOS/Fedora 系统的动态防火墙。与静态 iptables 不同，firewalld 支持在线更新规则而无需重启服务，并引入了 zone（区域）的概念，可根据网络信任级别应用不同的策略。 | `network/firewalld/playbook.yml` | covered |
| [interface 模块使用指南](network/interface/README.md) | community.general.nmcli 模块用于管理 Linux 系统的网络接口配置，通过 NetworkManager 的命令行工具实现接口的创建、修改、删除和状态管理。此模块适用于服务器网络配置、虚拟化管理、容器网络、VPN 连接等场景，能够统一管理不同类型的网络接口（以太网、VLAN、Bridge、Bond 等）。 | `network/interface/playbook.yml` | covered |
| [iptables 模块使用指南](network/iptables/README.md) | community.general.iptables 模块用于直接管理 Linux 内核的 iptables 防火墙规则。相比高层抽象的 firewalld/ufw，iptables 提供了对防火墙的细粒度控制，包括 NAT、DNAT、SNAT、自定义链等高级功能，适合需要复杂网络配置的场景。 | `network/iptables/playbook.yml` | covered |
| [nmcli 模块使用指南](network/nmcli/README.md) | community.general.nmcli 模块用于通过 NetworkManager 命令行工具管理网络连接，支持创建、修改、删除网络连接，配置 IP 地址、DNS、网关等网络参数。适用于服务器网络配置、网络接口管理、网络故障恢复等场景。 | `network/nmcli/playbook.yml` | covered |
| [port 模块使用指南](network/port/README.md) | ansible.builtin.wait_for 模块用于端口健康探测，通过检查目标主机端口的可用性来验证服务状态。此模块特别适用于集群部署、滚动更新、依赖链路中确保服务可用性等场景。相比直接连接测试，wait_for 提供了重试、超时、延迟等灵活控制机制，并支持通过 delegate_to: localhost 从控制节点进行远程检查，避免实际连接到目标服务。 | `network/port/playbook.yml` | covered |
| [route 模块使用指南](network/route/README.md) | ansible.posix.route 模块用于管理系统的静态路由表，支持添加、删除和修改路由规则。此模块适用于多网卡环境、复杂网络拓扑、VPN 配置、容器网络等场景，能够精确控制网络流量的路径选择。通过 Ansible 的幂等性特性，可以确保路由配置的一致性和可重复性。 | `network/route/playbook.yml` | covered |
| [ufw 模块使用指南](network/ufw/README.md) | community.general.ufw 模块用于管理 Ubuntu/Debian 系统的 Uncomplicated Firewall（ufw）。相比复杂的 iptables，ufw 提供了更简洁的界面和默认安全策略，非常适合快速配置基础防火墙规则。 | `network/ufw/playbook.yml` | covered |
| [VLAN 网络配置模块使用指南](network/vlan/README.md) | community.general.nmcli 模块用于配置 VLAN（虚拟局域网）网络接口，实现网络隔离、流量分割和多租户环境管理。VLAN 技术允许在同一物理网络设备上创建多个逻辑隔离的网络，广泛应用于企业网络、数据中心、云平台和多环境部署场景。 | `network/vlan/playbook.yml` | covered |
| [wait_for 模块使用指南](network/wait_for/README.md) | ansible.builtin.wait_for 模块用于等待特定条件满足后再继续执行后续任务。最常见的场景是等待服务端口开放，适用于集群部署、滚动更新、依赖链路中确保服务可用性等场景。相比直接检查，wait_for 提供了重试、超时、延迟等灵活控制。 | `network/wait_for/playbook.yml` | covered |

### 学习路径建议

| 优先级 | 模块 | 前置实践 | 官方文档 | 备注 |
| --- | --- | --- | --- | --- |
| medium | `ethtool` | interface, nmcli | [link](https://docs.ansible.com/ansible/latest/collections/community/general/ethtool_module.html) | 结合 interface/nmcli 示例演示链路调优、速率与双工配置。 |

## 网络协议层通信实践指南 (`network_protocols`)

本章节介绍 Ansible 中网络协议层的通信模块，涵盖 ICMP、HTTP、DNS、LDAP 等协议层的通信与交互。这些模块支持网络连通性检查、REST API 测试、DNS 查询与管理、目录服务访问等应用层场景，强调安全实践（SSL 验证、敏感信息保护、检查模式预览）。

**外部依赖**: ansible.builtin, community.general

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [DNS 模块实践指南](network_protocols/dns/README.md) | community.general.dig 模块用于执行 DNS 查询，支持查询 A、AAAA、CNAME、MX、NS、TXT 等 DNS 记录类型。该模块常用于： - DNS 解析验证与诊断 - 确认 CDN 或负载均衡配置 - 域名可用性检查 - DNS 记录一致性验证 - 与 DNS 管理系统的集成 | `network_protocols/dns/playbook.yml` | covered |
| [LDAP 协议模块使用指南](network_protocols/ldap/README.md) | community.general.ldap_* 系列模块用于与 LDAP（轻量级目录访问协议）服务器进行交互，支持用户认证、目录查询、条目管理、属性修改等操作。适用于统一身份认证、目录服务管理、用户信息同步等场景。 | `network_protocols/ldap/playbook.yml` | covered |
| [Ping 模块实践指南](network_protocols/ping/README.md) | ansible.builtin.ping 模块用于检查 Ansible 与目标主机的连接状态，通过发送 ICMP Echo 请求（ping）验证网络连通性和控制节点到目标主机的 SSH 连接状态。 | `network_protocols/ping/playbook.yml` | covered |
| [URI 模块实践指南](network_protocols/uri/README.md) | ansible.builtin.uri 模块用于执行 HTTP/HTTPS 请求，支持 GET、POST、PUT、DELETE 等多种 HTTP 方法。该模块常用于： - REST API 测试与调用 - HTTP 健康检查 - 获取远程文件或配置 - 与微服务、Kubernetes API、云平台 API 集成 - 应用层服务可用性验证 | `network_protocols/uri/playbook.yml` | covered |

## 存储模块实践指南 (`storage`)

本章节聚焦磁盘与文件系统的基础操作，涵盖从创建模拟磁盘、构建逻辑卷到格式化与挂载的完整流程。示例全部以中文注释编写，并通过 ansible-playbook --check、changed_when: false 等手段，将潜在破坏性操作限制在安全的演练环境中。

**外部依赖**: ansible.builtin, ansible.posix, community.general

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [磁盘信息采集（disk_facts）模块演练指南](storage/disk_facts/README.md) | 本示例展示如何使用 ansible.builtin.setup 模块（gather_facts）采集系统磁盘和块设备信息，获取关于硬件配置、块设备、LVM、分区等的详细数据。通过使用 filter 参数，可以选择性地采集特定的硬件信息（如磁盘列表、分区信息、LVM 卷等）。这对于自动化部署、系统审计和容量规划非常有用。 | `storage/disk_facts/playbook.yml` | covered |
| [filesystem 模块演练指南](storage/filesystem/README.md) | ansible.builtin.filesystem 用于在块设备或镜像文件上创建文件系统，支持 ext4/xfs/btrfs 等格式，并可在 check 模式下预览格式化命令。本示例通过 loopback 设备展示如何在不具备 root 权限的环境中模拟格式化流程。 | `storage/filesystem/playbook.yml` | covered |
| [LVM 卷组（lvg）模块演练指南](storage/lvg/README.md) | community.general.lvg 模块用于在 Linux 系统上创建、扩展和移除 LVM 卷组（Volume Group）。LVM 卷组是由一个或多个物理卷（PV）组成的存储池，在其之上可以创建逻辑卷（LV）。本示例通过 loopback 设备演示如何在非 root 或受限环境中学习 LVM 卷组的基本操作，包括卷组的创建、查询和安全删除。 | `storage/lvg/playbook.yml` | covered |
| [lvol 模块演练指南](storage/lvol/README.md) | ansible.builtin.lvol 用于在某个 VG 中创建或调整逻辑卷（LV），支持精确定义容量、条带数以及稀疏卷。示例通过 loopback 镜像 + 虚拟 VG 展示如何在教学环境中阅读返回值并验证参数组合。 | `storage/lvol/playbook.yml` | covered |
| [mount 模块演练指南](storage/mount/README.md) | ansible.posix.mount 用于声明挂载点与设备之间的关系，可同步更新 /etc/fstab，也能在 check 模式中验证挂载选项是否正确。本示例通过 loopback 镜像演示在受限环境下的安全操作流程。 | `storage/mount/playbook.yml` | covered |
| [Parted 磁盘分区模块演练指南](storage/parted/README.md) | community.general.parted 模块用于在 Linux 系统上使用 GNU Parted 进行磁盘分区操作。它支持创建、删除、修改分区，支持 MBR 和 GPT 分区表，是学习和自动化磁盘管理的强大工具。本示例通过 loopback 设备演示分区创建、查询和验证流程，在受限或非 root 环境中安全地学习磁盘分区操作。 | `storage/parted/playbook.yml` | covered |

## 系统管理模块指南 (`system`)

本章收录了面向系统管理与运维的核心 Ansible 模块，覆盖用户与组管理、服务生命周期控制、主机配置、以及防火墙规则管理等日常运维需求。

**外部依赖**: ansible.builtin, ansible.posix, community.general

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [auditd 审计系统模块使用指南](system/auditd/README.md) | auditd 模块用于配置 Linux 审计守护进程，提供系统级的安全审计功能。通过配置审计规则，可以监控文件访问、系统调用、用户登录等关键安全事件，满足合规性要求（如 PCI DSS、HIPAA）和安全基线标准。适用于安全加固、入侵检测、合规审计等场景。 | `system/auditd/playbook.yml` | covered |
| [authorized_key 模块使用指南](system/authorized_key/README.md) | ansible.builtin.authorized_key 模块用于管理用户的 SSH 授权密钥，支持添加、删除和更新 SSH 公钥。适用于自动化服务器访问权限管理、批量密钥分发、权限回收等场景。 | `system/authorized_key/playbook.yml` | covered |
| [cron 模块使用指南](system/cron/README.md) | ansible.builtin.cron 模块用于管理 cron 定时任务，支持创建、修改和删除用户的定时任务。适用于自动化备份、日志清理、监控检查、定时脚本执行等场景。 | `system/cron/playbook.yml` | covered |
| [firewalld 模块使用指南](system/firewalld/README.md) | community.general.firewalld 模块用于在 RHEL/CentOS/Fedora 系统上管理动态防火墙规则。支持 zone（区域）概念、service（服务）、port（端口）、rich rule（复杂规则）等多种管理方式，可在线更新规则无需重启防火墙服务。 | `system/firewalld/playbook.yml` | covered |
| [group 模块使用指南](system/group/README.md) | ansible.builtin.group 模块用于创建、修改和删除 Linux 用户组，支持指定组 ID (GID)、设置组成员等操作。适用于权限隔离、资源访问控制、与 user 模块协同配置等场景。 | `system/group/playbook.yml` | covered |
| [hostname 模块使用指南](system/hostname/README.md) | ansible.builtin.hostname 模块用于设置 Linux 系统的主机名。支持 systemd、sysvinit 等多种 init 系统，自动修改 /etc/hostname、/etc/hosts 等配置文件，并通过 hostnamectl 命令在运行时应用更改。 | `system/hostname/playbook.yml` | covered |
| [iptables 模块使用指南](system/iptables/README.md) | community.general.iptables 模块用于管理内核级防火墙规则，支持 IPv4 和 IPv6，广泛应用于传统 Linux 系统、容器宿主机、NAT 网关等场景。相比 firewalld 的高层抽象，iptables 提供更低层且灵活的规则控制。 | `system/iptables/playbook.yml` | covered |
| [kernel_tuning 内核调优模块使用指南](system/kernel_tuning/README.md) | kernel_tuning 模块用于配置 Linux 内核参数，通过调整 sysctl 参数来优化系统性能、增强网络安全性、提升系统稳定性。支持内存管理、网络栈优化、安全加固、文件系统调优等场景。适用于性能优化、安全加固、高负载环境配置等场景。 | `system/kernel_tuning/playbook.yml` | covered |
| [locale 模块使用指南](system/locale/README.md) | community.general.locale_gen 模块用于生成和管理系统支持的区域设置（Locale），支持设置字符编码、时间格式、货币符号等。在多语言环境、国际化应用部署、系统本地化配置中提供支持。确保应用程序能够正确处理不同语言的输入、输出和显示。 | `system/locale/playbook.yml` | covered |
| [pam_hardening PAM 安全加固模块使用指南](system/pam_hardening/README.md) | pam_hardening 模块用于配置可插拔认证模块（PAM）的安全策略，通过调整 PAM 配置来增强系统认证安全性。支持密码复杂度策略、登录失败锁定、会话超时、警告横幅等安全加固措施。适用于安全基线加固、合规性配置、多用户环境安全管理等场景。 | `system/pam_hardening/playbook.yml` | covered |
| [reboot 模块使用指南](system/reboot/README.md) | ansible.builtin.reboot 模块用于重启远程主机，支持等待系统重启完成、验证重启状态等功能。适用于系统更新后重启、内核更新、配置变更生效等需要重启系统的场景。 | `system/reboot/playbook.yml` | covered |
| [selinux 模块使用指南](system/selinux/README.md) | ansible.posix.selinux 模块用于管理 SELinux（Security Enhanced Linux）安全策略，支持设置 SELinux 工作模式、切换 SELinux 策略、管理文件安全上下文等。在 RHEL/CentOS 等企业 Linux 系统中提供强制访问控制（MAC），是提升系统安全性的重要手段。适用于安全加固、合规性要求、沙箱隔离等场景。 | `system/selinux/playbook.yml` | covered |
| [service 模块使用指南](system/service/README.md) | ansible.builtin.service 模块用于在 Linux 系统上管理服务的启动、停止、重启和自启动配置。支持 systemd、sysvinit 等多种 init 系统，是跨发行版服务管理的通用解决方案。 | `system/service/playbook.yml` | covered |
| [systemd 模块使用指南](system/systemd/README.md) | ansible.posix.systemd 模块提供底层 systemd 单元管理功能，包括启用/禁用服务、管理单元状态、启用定时器、加载用户级 systemd 单元等。相比 service 模块，systemd 模块提供更细粒度的单元管理控制。 | `system/systemd/playbook.yml` | covered |
| [timezone 模块使用指南](system/timezone/README.md) | ansible.builtin.timezone 模块用于设置系统时区，支持多种操作系统和时区数据库。在服务器集群管理、日志时间戳统一、国际化部署等场景中必不可少。可确保分布式系统的时间一致性，防止由时区差异导致的日志错乱、计划任务失效等问题。 | `system/timezone/playbook.yml` | covered |
| [user 模块使用指南](system/user/README.md) | ansible.builtin.user 模块用于创建、修改和删除 Linux 用户账号，支持管理用户的主组、辅助组、SSH 密钥、sudo 权限等。适用于运维账号创建、应用用户配置、权限隔离等场景。 | `system/user/playbook.yml` | covered |

### 学习路径建议

| 优先级 | 模块 | 前置实践 | 官方文档 | 备注 |
| --- | --- | --- | --- | --- |
| low | `mount` | storage_mount | [link](https://docs.ansible.com/ansible/latest/collections/ansible/posix/mount_module.html) | 结合 storage/mount 的 loopback 练习，展示 system 章节如何自检挂载状态。 |

## 版本控制模块指南 (`version_control`)

版本控制是现代软件开发的基石，涵盖了代码管理、协作开发、发布流程等核心场景。本模块提供 Git、Mercurial、GitHub、GitLab 等主流版本控制系统的 Ansible 自动化示例，支持从基础仓库操作到高级 CI/CD 集成的完整工作流。

**外部依赖**: ansible.builtin, community.general

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [git_workflow 模块使用指南](version_control/git_workflow/README.md) | ansible.builtin.git 模块用于管理 Git 仓库的克隆、拉取、推送、分支和标签等操作。该模块是 Git 工作流自动化的核心工具，支持代码部署、版本发布、持续集成等场景，为 DevOps 流水线提供可靠的版本控制基础。 | `version_control/git_workflow/playbook.yml` | covered |
| [github_release 模块使用指南](version_control/github_release/README.md) | community.general.github_release 模块用于管理 GitHub 仓库的 Release 创建、更新和删除操作。该模块是版本发布自动化的重要工具，支持创建发布版本、上传二进制文件、生成 Release Notes 等功能，适用于 CI/CD 流水线中的发布管理。 | `version_control/github_release/playbook.yml` | covered |
| [gitlab_project 模块使用指南](version_control/gitlab_project/README.md) | community.general.gitlab_project 模块用于管理 GitLab 项目的创建、更新、删除等操作。该模块是 GitLab 平台自动化的核心工具，支持项目管理、成员配置、权限控制等功能，适用于企业级 Git 环境的自动化运维和团队协作管理。 | `version_control/gitlab_project/playbook.yml` | covered |
| [hg 模块使用指南](version_control/hg/README.md) | community.general.hg 模块用于管理 Mercurial（Hg）仓库的克隆、拉取、推送、分支和标签等操作。该模块是 Mercurial 工作流自动化的核心工具，支持代码部署、版本发布、持续集成等场景，为使用 Mercurial 版本控制系统的项目提供可靠的自动化支持。 | `version_control/hg/playbook.yml` | covered |

## 虚拟化与私有云资源章节 (`virtualization`)

virtualization/ 目录面向 本地虚拟化实验室（libvirt + QEMU）与 企业级虚拟化平台（VMware vSphere）。通过统一的中文 README、示例 Playbook 与变量文件，演示如何在不开启真实变更的情况下验证虚拟化资源定义、磁盘操作与主机纳管流程。示例均使用 --check 模式或 check_mode: true，并在文档中强调依赖安装、认证方式、以及如何安全地模拟运行。

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [libvirt_domain 模块演练指南](virtualization/libvirt_domain/README.md) | virtualization/libvirt_domain 目录使用 community.libvirt.libvirt_domain 模块（亦可切换为 community.libvirt.virt）在 check_mode: true 下定义 KVM 虚拟机的 XML、计算/内存、网络及磁盘。示例强调如何在本地实验室或边缘节点验证虚拟机模板，避免误写入宿主机。 | `virtualization/libvirt_domain/playbook.yml` | covered |
| [qemu_img 模块演练指南](virtualization/qemu_img/README.md) | virtualization/qemu_img 使用 community.general.qemu_img 模块演示如何在 Dry Run 环境下规划镜像克隆、格式转换与快照管理。该模块适合本地/实验室场景，用于在真正修改 qcow2/raw 镜像之前验证参数与目标路径。 | `virtualization/qemu_img/playbook.yml` | covered |
| [VMware Host 模块演练指南](virtualization/vmware_host/README.md) | virtualization/vmware_host 示例使用 community.vmware.vmware_host（或 community.vmware.vmware_guest）模块，在 check_mode: true 下演练 ESXi 主机纳管、维护模式与标签策略。示例针对企业级虚拟化场景，帮助 SRE/虚拟化团队在无需触碰真实生产集群的前提下验证 vCenter API、证书与凭证配置。 | `virtualization/vmware_host/playbook.yml` | covered |

## Web 服务管理指南 (`web`)

本目录提供 Nginx、Apache 以及通用 Web 配置的 Ansible 自动化示例，帮助你快速完成反向代理、静态站点发布以及站点配置管理等常见任务。所有 Playbook 均包含中文注释，遵循教学最佳实践，适合在测试环境中学习与验证。

**外部依赖**: ansible.builtin, community.crypto, community.general

| 模块 | 摘要 | 示例 | 覆盖状态 |
| --- | --- | --- | --- |
| [Apache2 Web 服务器管理](web/apache2/README.md) | Apache HTTP Server（通常简称 Apache）是世界上使用最广泛的开源 Web 服务器软件，具有高度模块化、跨平台、稳定可靠等特点。Apache 支持丰富的第三方模块，可轻松集成 PHP、Python、Perl 等动态语言，适合构建传统 Web 应用和内容管理系统。 | `web/apache2/playbook.yml` | covered |
| [HAProxy 负载均衡配置](web/haproxy/README.md) | HAProxy 是一款高性能、开源的 TCP/HTTP 负载均衡和代理解决方案。与 Nginx 相比，HAProxy 在传输层（Layer 4）和应用层（Layer 7）均提供强大的负载均衡能力，支持 SSL/TLS、WebSocket、FastCGI、TCP Socket 等多种协议。HAProxy 特别适合于构建高可用集群、进行 A/B 测试、灰度发布等复杂场景。 | `web/haproxy/playbook.yml` | covered |
| [Nginx Web 服务器管理](web/nginx/README.md) | Nginx 是一款高性能的 HTTP 和反向代理服务器，以其高并发处理能力、低内存占用和灵活的配置著称。常用于静态内容服务、反向代理、负载均衡、API 网关等场景。本示例展示如何使用 Ansible 自动化安装、配置和管理 Nginx 服务。 | `web/nginx/playbook.yml` | covered |
| [SSL 证书自动化管理](web/ssl_certificate/README.md) | SSL/TLS 证书是 HTTPS 通信的基础，用于加密客户端与服务器之间的通信。本示例展示如何使用 Ansible 自动化获取、部署、验证和续期 SSL 证书。我们重点关注使用 Let's Encrypt 提供的免费证书，通过 community.crypto.acme_certificate 模块实现自动化管理，并配合定时任务实现证书自动续期与到期提醒。 | `web/ssl_certificate/playbook.yml` | covered |
| [Web 通用配置管理](web/web_config/README.md) | 本目录提供跨 Web 服务器（Nginx/Apache）的通用配置场景示例，涵盖反向代理、静态站点发布、SSL 证书管理等常见任务。这些示例可作为模板，根据实际使用的 Web 服务器进行调整和扩展。 | `web/web_config/playbook.yml` | covered |
