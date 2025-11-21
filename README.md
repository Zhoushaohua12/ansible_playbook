# Ansible 中文实践指南

本仓库收录了面向中文读者的 Ansible 示例与知识卡片，帮助你在日常运维和自动化项目中迅速定位所需特性。所有示例均可直接运行或作为模板套用到现有 Playbook 中。

## 依赖管理

本项目维护统一的依赖清单，包括 Ansible Collections 和 Python 库：

- **[`collections/requirements.yml`](collections/requirements.yml)**：所有示例所需的 Ansible Collections 集合，包含云平台（AWS、Azure、GCP、OpenStack、阿里云）、虚拟化（libvirt、VMware）、容器（Kubernetes、Docker）、消息队列、数据库、监控等。
  - **安装方式**：`ansible-galaxy collection install -r collections/requirements.yml`

- **[`requirements.txt`](requirements.txt)**：所有示例所需的 Python 依赖库，包括各云平台 SDK、虚拟化库、数据库库、监控库等。
  - **安装方式**：`pip install -r requirements.txt`

## 审计与规范

本项目遵循统一的代码风格和最佳实践规范：

- **[`AUDIT_REPORT.md`](AUDIT_REPORT.md)**：详细的项目审计报告，包含规范检查结果、问题清单（按优先级分类）和改进建议。涵盖 playbook 规范、安全处理、变量文件警示、handler 中文化等重要规范。

所有 Playbook 示例均遵循以下规范：
- 统一使用中文任务名、handler 名称和注释
- 变量文件 (`vars/example_vars.yml`) 文件头必须包含 `⚠️ 本文件仅为示例，占位符必须使用 Ansible Vault 或环境变量替换` 警示
- 敏感信息使用 `vault_*` 前缀，配合 Ansible Vault 加密
- 所有涉及系统变更的 playbook 均提供 `--check` 模式示例

## 仓库结构
- `advanced/`：高级特性讲解与示例 Playbook。
- `applications/`：应用管理模块（软件包/容器/源码部署）的实践指南。
- `cloud/`：多云算力编排示例（AWS、Azure、GCP、OpenStack、阿里云），强调 Dry Run、认证与 Vault。
- `commands/`：命令执行模块（shell、command、raw、script）的使用指南与安全实践。
- `files/`：文件操作模块（copy、template、lineinfile、stat、file、find、synchronize）的中文文档与示例。
- `database/`：数据库管理模块（MySQL、PostgreSQL、MongoDB）的自动化运维示例。
- `message_queue/`：消息队列管理（RabbitMQ、Kafka）的自动化配置与管理示例。
- `monitoring/`：主流监控系统的 Ansible 集成示例（Nagios、Datadog、Zabbix、Prometheus、Splunk、ELK）。
- `network/`：网络配置与防火墙管理（firewalld、ufw、iptables、wait_for、port、route、interface）的完整指南。
- `network_protocols/`：网络协议层通信（ICMP/ping、HTTP/uri、DNS/dig）的模块实践，强调安全验证与敏感信息保护。
- `storage/`：磁盘、LVM 与文件系统管理的演练场景。
- `system/`：系统管理模块（user、group、service、systemd、hostname、timezone、locale、firewalld、iptables、selinux、auditd、pam_hardening、kernel_tuning）的完整指南。
- `virtualization/`：本地/企业虚拟化（libvirt、VMware、qemu-img）演练，展示与云资源协同的最佳实践。
- `web/`：Web 服务器（Nginx、Apache）配置与管理示例。
- `metadata/modules.yaml`：用于索引特性与文档的元数据。
- `tests/`：确保示例结构完整的 pytest 测试。

## 模块索引与学习路径自动化

为了避免手动维护几十个章节的元数据，仓库提供 `tools/module_index.py` 作为统一的自动化入口：

- **生成索引**：优先使用虚拟环境中的 Python 运行 `venv/bin/python tools/module_index.py --generate --comparison-report`。命令会同步产出：
  - `metadata/modules.yaml`：结构化索引文件，供测试与外部工具加载；
  - `docs/MODULE_INDEX.md`：可搜索的 Markdown 索引，包含每个模块的摘要、示例位置与覆盖状态；
  - `reports/module_index.json`：机器可读的索引快照，方便在 CI 或后续自动化中消费；
  - `reports/module_comparison.md`：Stage 4 自动化所需的 Markdown 对比报告，用于展示 ansible-doc 与项目实践之间的缺口。
- **查询模式**：`python tools/module_index.py --query copy` 会输出匹配模块的分类、文档路径、示例路径以及解析到的依赖模块，便于在命令行快速定位素材。
- **学习路径**：`python tools/module_index.py --learning-path` 会分组打印学习路线，按照 priority（high/medium/low）指示下一个应补充的模块。建议优先处理 high 项，medium 项作为规划 backlog，low 项留给长期演进。
- **差异数据**：`metadata/ansible_doc_diff.json` 保存 ansible-doc 与现有目录的 diff。更新该文件后重新运行 `--generate` 即可让新的缺口出现在学习路径与 Stage 4 报告中。

`docs/MODULE_INDEX.md` 中的表格可直接在编辑器/浏览器中搜索（`Cmd/Ctrl + F`），也可以依赖 `reports/module_index.json` 在自定义脚本里实现更复杂的检索逻辑。

## 模块差异分析工具

`tools/module_diff.py` 提供全面的模块覆盖分析，帮助识别项目与 Ansible 官方模块库之间的缺口：

### 核心功能

- **自动获取模块列表**：执行 `ansible-doc -l` 获取所有可用模块（ansible-doc 不可用时自动降级到常用模块列表）
- **多维度对比**：
  - 对比 `metadata/modules.yaml` 中已声明的模块
  - 对比文件系统中实际存在的模块目录
  - 对比 `ansible-doc` 输出的官方模块列表
- **优先级管理**：基于 `metadata/module_priorities.yml` 配置文件，将缺失模块按 P1/P2/P3 分组
- **统计报告**：生成总体覆盖率、分类覆盖率、优先级分布等统计数据
- **问题检测**：自动识别重复定义、元数据与文件系统不一致等问题

### 使用方式

#### 生成完整报告

```bash
# 使用缓存数据生成报告（推荐，速度快）
venv/bin/python tools/module_diff.py

# 刷新 ansible-doc 缓存并生成报告
venv/bin/python tools/module_diff.py --refresh-cache
```

生成的报告文件：
- `reports/module_diff.json`：机器可读的 JSON 格式，包含所有分析数据
- `reports/module_diff.md`：人类可读的 Markdown 格式，包含表格和统计

#### 按优先级筛选

```bash
# 仅查看 P1（高优先级）缺失模块
venv/bin/python tools/module_diff.py --priority P1

# 查看 P2（中等优先级）缺失模块
venv/bin/python tools/module_diff.py --priority P2
```

#### 仅显示摘要

```bash
# 快速查看统计信息，不生成文件
venv/bin/python tools/module_diff.py --summary
```

#### 自定义输出路径

```bash
venv/bin/python tools/module_diff.py \
  --json-output custom/path.json \
  --md-output custom/path.md
```

### 报告解读

#### 模块状态

- **covered**：模块已在 `metadata/modules.yaml` 中声明且文件系统中存在对应目录
- **missing**：模块存在于 `ansible-doc` 输出但项目中尚未覆盖
- **undocumented**：模块在项目元数据中但不在 `ansible-doc` 输出（可能是自定义模块或社区模块）

#### 优先级定义（`metadata/module_priorities.yml`）

- **P1（Critical/High）**：生产环境必备模块，如 copy、template、file、service、user 等
- **P2（Medium）**：特定场景重要模块，如云平台操作、数据库管理、容器编排等
- **P3（Low）**：专用或低频模块，如 raw、expect、capabilities 等

#### 问题类型

- **duplicates**：同一模块在多个分类中重复定义，建议合并或明确主分类
- **inconsistencies**：
  - `in_metadata_but_not_filesystem`：元数据中声明但缺少目录，需要创建对应示例
  - `in_filesystem_but_not_metadata`：目录存在但未在元数据中声明，需要更新 `modules.yaml`

### 工作流建议

1. **定期刷新缓存**：每次 Ansible 版本升级后运行 `--refresh-cache`
2. **优先补充 P1 模块**：参考报告中的 "Missing P1 Modules" 章节
3. **解决不一致问题**：查看 "Inconsistencies" 章节并修复元数据或文件系统
4. **更新优先级配置**：根据团队实际需求调整 `metadata/module_priorities.yml`
5. **集成到 CI**：在 CI 流程中运行 `--summary` 监控覆盖率变化

### 缓存管理

ansible-doc 缓存位于 `.cache/ansible_doc_cache.json`：
- 首次运行或使用 `--refresh-cache` 时会执行 `ansible-doc -l` 并缓存结果
- 缓存可避免频繁调用 ansible-doc（执行较慢）
- ansible-doc 不可用时自动降级到内置常用模块列表
- 建议在每次 Ansible 升级后手动刷新缓存

## 进阶章节
- [高级特性总览](advanced/README.md)
- [应用管理指南](applications/README.md)
- [云资源管理指南](cloud/README.md)
- [命令执行模块指南](commands/README.md)
- [文件操作模块实践指南](files/README.md)
- [数据库管理实践指南](database/README.md)
- [消息队列管理指南](message_queue/README.md)
- [监控模块总览](monitoring/README.md)
- [网络模块实践指南](network/README.md)
- [网络协议层通信指南](network_protocols/README.md)
- [存储模块实践指南](storage/README.md)
- [系统管理模块指南](system/README.md)
- [虚拟化资源指南](virtualization/README.md)
- [Web 服务管理指南](web/README.md)

## 如何学习
按照"阅读文档 → 运行示例 → 修改变量 → 扩展任务"的顺序进行练习。建议先通读对应 README，结合注释理解变量含义，再亲自运行 Playbook 并在失败时参考"如何调试/常见错误"章节。完成基础练习后，可以尝试把同一台主机的需求拆分进多个特性目录中的示例，或根据业务自定义更多 handler、loop 与 include 组合，以加深理解。

## 如何运行示例
1. 进入目标模块目录（如 `cd files/copy`），阅读 `README.md` 了解操作背景与安全提示。
2. 打开 `vars/example_vars.yml`，根据环境调整占位变量，必要时使用 Ansible Vault 保护敏感信息。
3. 使用 `ansible-playbook playbook.yml --syntax-check` 进行语法检查；再使用 `--check` 模式预览变更；确认无误后再执行正式命令。
4. 需要辅助文件的模块请保持目录结构不变：
   - `files/copy` 和 `files/template` 依赖同级的 `files/`、`templates/` 子目录存放示例配置与 Jinja2 模板。
   - `files/synchronize` 使用 `source_dir/` 作为示例站点，请在控制节点保留该目录并安装 `rsync`。
   - 运行这些示例时务必在模块目录下执行，以便 `playbook_dir` 能正确解析相对路径。
5. 结合 `--diff` 选项查看文件内容差异，确保中文注释、编码和权限符合预期。

## 注意事项
- **存储示例严禁直接在生产环境运行**：`storage/` 下的 playbook 默认通过 loopback 设备和 `--check` 模式演练，请先阅读 [storage/README.md](storage/README.md) 并在沙箱环境验证。
- **强制 Dry-Run**：执行任何存储任务前务必加上 `ansible-playbook --check`，必要时结合 `changed_when: false`/`failed_when: false`，确认计划后再放行。
- **备份优先**：在尝试 mount/LVM/filesystem 实操前，先备份 fstab、VG metadata 以及关键数据，确保可以在出错时回滚。

## 命令执行模块注意事项

### 安全使用建议
- **受控环境运行**：命令执行模块建议仅在受控主机上运行，避免在生产环境随意执行
- **模块选择原则**：优先使用 command 模块，需要 shell 特性时使用 shell 模块，无 Python 环境时才使用 raw 模块
- **幂等性控制**：使用 `creates`、`removes`、`changed_when` 确保命令执行的幂等性
- **脚本安全审查**：使用 script 模块时，确保脚本内容经过安全审查，避免恶意代码

### 测试验证建议
- **中文文档检查**：确保所有 README 和 playbook 包含中文注释和任务名
- **安全规范验证**：shell 模块应包含 `warn: false` 或 `set -e`，command 模块不应启用 shell
- **raw 模块提醒**：raw 示例需包含中文安全提醒，说明会绕过 Python 依赖
- **脚本引用检查**：script 模块示例应引用现有 `.sh` 脚本文件并有中文注释

## 文件操作章节
`files/` 目录收录了 copy、template、lineinfile、stat、file、find、synchronize 七大文件模块，覆盖文件创建、传输、配置差异化生成、元数据查询与目录同步的全流程；文档包含中文注释、编码提示与备份策略。

### 模块概览
| 模块 | 场景 | 关键提示 |
|------|------|----------|
| copy | 分发静态配置、证书、脚本 | 启用 `backup`/`remote_src`，确保 UTF-8 编码 |
| template | Jinja2 动态渲染配置 | 使用 `--diff` 检查差异，模板中加入中文注释 |
| lineinfile | 行级配置修改 | 配合 `regexp`、`backup: true`，防止重复行 |
| stat | 文件状态检查 | 结合 `when` 条件，只在文件存在时执行高风险操作 |
| file | 目录/权限/链接管理 | 权限字符串需加引号，必要时 `recurse: true` |
| find | 条件查找文件 | `age`/`size` 过滤大目录，结果可交给 file 模块清理 |
| synchronize | 目录增量同步 | 控制节点与远程均需安装 `rsync`，慎用 `delete: yes` |

### 学习路线
1. `file` → 了解目录/权限管理；
2. `copy` + `stat` → 学习文件分发与状态判断；
3. `lineinfile` → 精确调整配置；
4. `template` → 渲染多环境配置并配合 handler；
5. `find` → 查询并批量处理日志或缓存；
6. `synchronize` → 使用 rsync 进行代码部署与备份。

### 常见陷阱
- **编码问题**：所有示例默认 UTF-8，Windows 编辑器需关闭 BOM；
- **幂等性与备份**：copy/template/lineinfile 均演示 `backup: yes`，运行前可先 `--check --diff`；
- **依赖提醒**：synchronize 需要 ansible.posix collection 与 `rsync`，执行前确保已安装。

### 相关链接
- [copy 模块示例](files/copy/README.md)
- [template 模块示例](files/template/README.md)
- [lineinfile 模块示例](files/lineinfile/README.md)
- [stat 模块示例](files/stat/README.md)
- [file 模块示例](files/file/README.md)
- [find 模块示例](files/find/README.md)
- [synchronize 模块示例](files/synchronize/README.md)

## 监控模块使用提示

### API 管理最佳实践
- **凭证安全**：使用 Ansible Vault 加密所有 API Key 和密码
- **权限最小化**：为不同监控平台创建专用的 API 用户，限制权限范围
- **定期轮换**：建立定期更新访问凭证的流程
- **环境隔离**：为不同环境（生产、测试、开发）使用独立的 API 凭证

### 安全注意事项
- 不要在代码中硬编码真实密码或 API Key
- 使用 `no_log: true` 保护敏感变量不被记录到日志
- 在运行前使用 `--check` 模式验证配置变更
- 限制 API 访问的源 IP 地址和网络范围

### 相关链接
- [Nagios 监控集成](monitoring/nagios/README.md) - 传统开源监控
- [Datadog 云监控](monitoring/datadog/README.md) - 云原生监控平台  
- [Zabbix 企业监控](monitoring/zabbix/README.md) - 企业级监控解决方案

## 云资源章节

### 覆盖范围
`cloud/` 目录聚焦多云与私有云资源交付，包含 AWS EC2、Azure VM、GCP Compute、OpenStack Server、阿里云 ECS 等模块，帮助团队在 Dry Run 状态下验证算力、网络、标签和配额策略。所有 playbook 默认引用 `vars/example_vars.yml` 并在任务中设置 `check_mode: true` 与 `no_log: true`，方便在无真实凭证时练习。

### 依赖安装与认证
本章节依赖的 Collections 和 Python 库已在根目录的 `collections/requirements.yml` 和 `requirements.txt` 中统一定义，可通过以下方式一键安装：

```bash
# 安装所有 Ansible Collections
ansible-galaxy collection install -r collections/requirements.yml

# 安装所有 Python 依赖库
pip install -r requirements.txt
```

云平台特定的认证方式：
- AWS 建议通过 `aws configure` 或 SSO profile，切勿把 Access Key 写入仓库。
- Azure 使用 Service Principal (`az ad sp create-for-rbac --sdk-auth`)，密钥应放入 Vault。
- GCP 采用 Service Account JSON，并结合 `env`/Vault 提供文件路径。
- OpenStack 使用 `clouds.yaml` + Application Credential，文件加密后再共享。
- 阿里云使用 RAM 临时凭证或最小权限 AccessKey，配合 `ansible-vault encrypt`。

### 模拟运行步骤
1. 进入对应模块目录并阅读 README，确认依赖与角色权限。
2. 按照中文注释修改 `vars/example_vars.yml`，保留 `REPLACE_` 或 `{{ vault_* }}` 占位。
3. 执行 `ansible-playbook playbook.yml --syntax-check`，再运行 `--check` 完成 Dry Run。
4. 若需真实执行，移除 `check_mode: true`、在 Vault 中加密变量文件，并在沙箱账号验证。

### 相关链接
- [cloud/aws_ec2](cloud/aws_ec2/README.md)
- [cloud/azure_vm](cloud/azure_vm/README.md)
- [cloud/gcp_compute](cloud/gcp_compute/README.md)
- [cloud/openstack_server](cloud/openstack_server/README.md)
- [cloud/aliyun_ecs](cloud/aliyun_ecs/README.md)

## 虚拟化章节

### 为什么独立
`virtualization/` 专注本地虚拟化（libvirt/qemu-img）与企业虚拟化（VMware vSphere）场景，既可在笔记本/实验室模拟，也能在生产级集群中 Dry Run 主机纳管流程。该章节强调“先在本地模板演练 → 再迁移到 cloud/ 章节”的混合云学习路径。

### 依赖安装
本章节依赖的 Collections 和 Python 库已在根目录的 `collections/requirements.yml` 和 `requirements.txt` 中统一定义，可通过以下方式安装相关依赖：

```bash
# 安装所有 Ansible Collections
ansible-galaxy collection install -r collections/requirements.yml

# 安装所有 Python 依赖库
pip install -r requirements.txt

# 同时需要在目标主机安装系统级虚拟化工具
sudo apt/yum install -y libvirt-daemon qemu-kvm qemu-img
```

虚拟化部署特定要求：
- libvirt 示例使用 `qemu:///system` 或 `qemu+ssh://` URI，需具备本地虚拟化权限。
- VMware 示例需 vCenter API 账号与可信证书，可通过环境变量注入。
- qemu-img 示例要求在非生产目录准备测试镜像，并在变量中写明占位路径。

### 本地/企业虚拟化安全准则
1. **凭证加密**：VMware 密码、libvirt 远程凭证须使用 Vault 或 Secret Manager。
2. **执行前备份**：在操作 qemu-img、libvirt 之前备份 XML/镜像；若只是快速演练，可持续保持 `check_mode: true`。
3. **环境隔离**：本地实验室建议使用独立用户与目录；企业集群需在维护窗口执行，并启用审计日志。
4. **结合 cloud/**：在 virtualization 中验证模板后，可直接把磁盘导出至 cloud/ 章节的镜像或实例定义，实现同构管理。

### 相关链接
- [virtualization/libvirt_domain](virtualization/libvirt_domain/README.md)
- [virtualization/vmware_host](virtualization/vmware_host/README.md)
- [virtualization/qemu_img](virtualization/qemu_img/README.md)

## Web 服务章节

### 服务概览
`web/` 目录提供 Nginx、Apache 以及通用 Web 配置的自动化管理示例，涵盖以下场景：
- **反向代理**：将外部请求代理到内网应用服务器（Django、Flask、Node.js 等）
- **静态站点发布**：部署 HTML/CSS/JS 静态资源
- **SSL/TLS 配置**：自动化管理 HTTPS 证书和安全加固
- **负载均衡**：配置多后端服务器的流量分发策略
- **虚拟主机管理**：多域名站点托管

### 模板说明
每个 Web 服务模块都包含完整的配置模板（`.j2` 文件），所有模板均包含中文注释说明关键配置项：
- **Nginx 模板**：`web/nginx/templates/` 包含主配置文件和虚拟主机模板
- **Apache 模板**：`web/apache2/templates/` 包含虚拟主机和安全配置模板
- **通用模板**：`web/web_config/templates/` 包含跨服务器的反向代理和静态站点模板

所有模板支持变量替换，可根据实际需求调整参数（域名、端口、路径、SSL 配置等）。

### 教学声明
⚠️ **重要提示**：本目录下的所有示例主要用于教学和学习目的，在生产环境使用前需要：
1. **安全加固**：根据实际需求调整安全配置（如禁用不必要的模块、配置 WAF、限流保护）
2. **性能调优**：根据服务器硬件资源调整并发参数、缓冲区大小、超时时间
3. **测试验证**：在预发布环境进行压力测试，验证配置正确性和性能表现
4. **监控告警**：建立完善的监控体系（结合 `monitoring/` 目录示例），及时发现异常
5. **备份恢复**：建立配置文件和证书的备份机制，确保可快速恢复

建议先在测试环境运行示例，理解每个配置项的作用后，再根据生产需求定制化。

### 与 system/applications 的配合
Web 服务层通常与应用层配合使用：
- **应用部署**：`system/applications/` 负责安装和启动应用（如 Django、Node.js）
- **Web 层代理**：`web/` 负责配置反向代理，将外部请求转发到应用端口
- **健康检查**：结合 `monitoring/` 监控应用和 Web 服务健康状态

典型工作流：先部署应用 → 配置 Web 服务 → 启用 HTTPS → 配置监控告警

### 快速开始
```bash
# 1. 语法检查
ansible-playbook web/nginx/playbook.yml --syntax-check

# 2. Dry-Run 预览变更
ansible-playbook web/nginx/playbook.yml -i hosts.ini --check

# 3. 执行部署
ansible-playbook web/nginx/playbook.yml -i hosts.ini

# 4. 验证服务状态
curl -I http://your-domain.com
```

### 相关链接
- [Nginx 配置管理](web/nginx/README.md) - 高性能 HTTP 服务器和反向代理
- [Apache2 配置管理](web/apache2/README.md) - 传统开源 Web 服务器
- [通用 Web 配置](web/web_config/README.md) - 跨服务器的通用配置场景

## 应用管理章节

### 管理概览
`applications/` 目录提供完整的应用生命周期管理解决方案，涵盖以下场景：
- **软件包管理**：通过 yum、apt、package 等模块实现跨平台软件部署
- **容器化部署**：使用 docker_container 模块管理 Docker 容器生命周期
- **源码部署**：通过 git 模块实现版本控制和持续部署

### 模块特性
每个应用管理模块都包含完整的部署示例：
- **docker_container**：容器化应用部署，支持网络、存储、健康检查配置
- **git**：源码仓库管理，支持版本控制、分支切换、子模块管理
- **package**：跨平台包管理，自动适配不同系统的包管理器
- **yum**：Red Hat 系统专用包管理，支持软件组和仓库管理
- **apt**：Debian 系统专用包管理，支持软件源和 GPG 验证

### 运行提示
- **容器示例**：建议在本地或 CI 环境仅做语法检查，避免在生产环境直接运行
- **包管理操作**：需要 root 权限，请确保适当的权限配置
- **Git 操作**：需要网络访问，请检查防火墙和代理设置

### 快速开始
```bash
# 1. 语法检查
ansible-playbook applications/[module]/playbook.yml --syntax-check

# 2. Dry-Run 预览
ansible-playbook applications/[module]/playbook.yml --check

# 3. 执行部署
ansible-playbook applications/[module]/playbook.yml

# 4. 验证结果
ansible-playbook applications/[module]/playbook.yml --check
```

### 相关链接
- [Docker 容器管理](applications/docker_container/README.md) - 容器化应用部署和管理
- [Git 仓库管理](applications/git/README.md) - 源码部署和版本控制
- [通用包管理](applications/package/README.md) - 跨平台软件包管理
- [YUM 包管理](applications/yum/README.md) - Red Hat 系统包管理
- [APT 包管理](applications/apt/README.md) - Debian 系统包管理

## 数据库管理章节

### 管理概览
`database/` 目录提供主流数据库系统（MySQL、PostgreSQL、MongoDB）的自动化管理解决方案，涵盖以下场景：
- **用户管理**：创建数据库用户、授予权限、密码管理
- **数据库管理**：创建/删除数据库、导入导出数据、字符集配置
- **权限控制**：精细化权限管理、最小权限原则实践
- **备份恢复**：自动化数据库备份和恢复流程

### 环境依赖
本章节依赖的 Collections 和 Python 库已在根目录的 `collections/requirements.yml` 和 `requirements.txt` 中统一定义，可通过以下方式安装：

```bash
# 安装所有 Ansible Collections
ansible-galaxy collection install -r collections/requirements.yml

# 安装所有 Python 依赖库
pip install -r requirements.txt
```

⚠️ **重要提示**：Python 库需要安装在**目标数据库主机**上，而非 Ansible 控制节点。特别是 MySQL 需要 PyMySQL 或 mysqlclient、PostgreSQL 需要 psycopg2-binary、MongoDB 需要 pymongo。

### 模块特性
每个数据库管理模块都包含完整的运维示例：
- **mysql_user**：MySQL 用户创建、权限授予、密码管理
- **mysql_db**：MySQL 数据库创建、导入导出、字符集配置
- **postgresql_db**：PostgreSQL 数据库管理、owner 配置、备份恢复
- **mongodb_user**：MongoDB 用户和角色管理、权限配置

### 安全注意事项
- **凭证加密**：所有示例使用占位符密码，生产环境务必使用 Ansible Vault 加密
- **最小权限**：为不同应用创建专用数据库用户，避免使用超级用户
- **check_mode 测试**：所有示例默认使用 `check_mode: true`，可在无真实数据库环境下运行
- **审计日志**：使用 `no_log: true` 防止敏感信息记录到日志

### 运行提示
- **本地测试**：所有 playbook 默认使用 `check_mode: true` 和 `delegate_to`，适合学习和测试
- **生产部署**：移除 `check_mode: true` 并配置正确的数据库连接信息
- **凭证管理**：使用 `ansible-vault encrypt` 加密 `vars/example_vars.yml` 文件

### 快速开始
```bash
# 1. 安装依赖
ansible-galaxy collection install community.mysql community.postgresql community.mongodb

# 2. 语法检查
ansible-playbook database/mysql_user/playbook.yml --syntax-check

# 3. Dry-Run 预览（默认 check_mode）
ansible-playbook database/mysql_user/playbook.yml

# 4. 实际执行（移除 playbook 中的 check_mode: true）
ansible-playbook database/mysql_user/playbook.yml -i hosts.ini
```

### 相关链接
- [MySQL 用户管理](database/mysql_user/README.md) - MySQL 用户创建和权限管理
- [MySQL 数据库管理](database/mysql_db/README.md) - MySQL 数据库生命周期管理
- [PostgreSQL 数据库管理](database/postgresql_db/README.md) - PostgreSQL 数据库和备份管理
- [MongoDB 用户管理](database/mongodb_user/README.md) - MongoDB 用户和角色管理

## 网络模块章节

### 模块概览
`network/` 目录提供完整的网络配置与防火墙管理解决方案，涵盖以下场景：
- **防火墙规则管理**：firewalld（RHEL 系统）、ufw（Debian 系统）、iptables（内核级防火墙）
- **网络监控与协调**：wait_for 模块用于端口监控、服务就绪验证、集群初始化协调
- **分层安全部署**：支持多层应用架构的网络隔离和安全加固
- **容器网络支持**：为 Kubernetes/Docker 等容器平台提供宿主机级网络配置

### 模块特性
每个网络管理模块都包含完整的配置和监控示例：
- **firewalld**：RHEL/CentOS 系统的动态防火墙，支持 zone、service、port 灵活配置
- **ufw**：Ubuntu/Debian 系统的简化防火墙，快速配置 allow/deny 规则
- **iptables**：内核级防火墙，支持 NAT、DNAT、SNAT 等高级功能
- **wait_for**：端口/服务可用性监控，支持延时重试和日志内容匹配

### 环境依赖

#### 必需的 Ansible Collections
本章节依赖的 Collections 已在根目录的 `collections/requirements.yml` 中统一定义，可通过以下方式安装：

```bash
# 安装所有 Ansible Collections
ansible-galaxy collection install -r collections/requirements.yml
```

注：wait_for 模块内置于 ansible.builtin，无需额外安装。

#### 系统工具安装
```bash
# 在目标主机上安装对应防火墙工具

# RHEL/CentOS/Fedora (firewalld)
sudo yum install -y firewalld
sudo systemctl enable firewalld
sudo systemctl start firewalld

# Ubuntu/Debian (ufw)
sudo apt-get install -y ufw
sudo ufw enable

# 通用 (iptables)
# 大多数系统已预装，如需安装：
sudo yum install -y iptables        # RHEL/CentOS
# 或
sudo apt-get install -y iptables    # Debian/Ubuntu
```

### 使用建议

#### 快速开始
```bash
# 1. 安装必要的集合和工具
ansible-galaxy collection install community.general
ansible-galaxy collection install ansible.posix
# 在目标主机上安装 firewalld、ufw、NetworkManager 等工具

# 2. 查看对应模块文档
cd network/firewalld  # 或 ufw/iptables/wait_for/port/route/interface
cat README.md

# 3. 配置变量
# 编辑 vars/example_vars.yml，根据实际需求调整参数

# 4. 测试执行
ansible-playbook playbook.yml --syntax-check
ansible-playbook playbook.yml -i hosts.ini --check

# 5. 实际部署
ansible-playbook playbook.yml -i hosts.ini
```

#### 分层部署示例
```yaml
# 1. Web 层防火墙配置
- hosts: web_servers
  tasks:
    - import_playbook: network/firewalld/playbook.yml
      vars:
        firewalld_web_services: [http, https]
        firewalld_web_zone: public

# 2. 应用层防火墙配置
- hosts: app_servers
  tasks:
    - import_playbook: network/firewalld/playbook.yml
      vars:
        firewalld_app_port: 8080
        firewalld_app_zone: internal

# 3. 验证服务可用性
- hosts: localhost
  tasks:
    - import_playbook: network/wait_for/playbook.yml
      vars:
        wait_for_web_host: "{{ web_server_ip }}"
        wait_for_web_port: 80
    - import_playbook: network/port/playbook.yml
      vars:
        port_web_host: "{{ web_server_ip }}"
        port_web_port: 80
        port_web_timeout: 30
```

#### 安全最佳实践
1. **测试环境验证**：先在测试环境验证防火墙规则，再部署到生产
2. **保持管理端口畅通**：避免意外阻断 SSH（通常 22 端口）
3. **规则备份**：修改前备份当前防火墙规则以便回滚
4. **使用 zone 隔离**：firewalld 的 zone 功能有效实现网络分段
5. **监控告警**：启用防火墙日志，配合监控系统及时发现异常

### 快速参考

| 场景 | 推荐模块 | 说明 |
|------|----------|------|
| RHEL/CentOS 防火墙管理 | firewalld | 支持动态更新、zone 隔离 |
| Ubuntu/Debian 防火墙管理 | ufw | 规则简单、易于维护 |
| 内核级防火墙 / NAT 配置 | iptables | 强大灵活，支持高级功能 |
| 服务启动等待 | wait_for | 监控端口/文件，协调依赖 |
| 端口健康探测 | port | 批量端口检查、delegate_to 安全检查 |
| 静态路由管理 | route | 多网卡路由、metric 优先级 |
| 网络接口管理 | interface | 以太网/网桥/绑定/VLAN 配置 |
| 检查日志消息 | wait_for + search_regex | 更精确的服务就绪判断 |

### 故障排查

#### 防火墙修改后 SSH 连接断开
```bash
# 在目标主机本地恢复访问
sudo systemctl stop firewalld         # 临时关闭
sudo iptables -I INPUT -p tcp --dport 22 -j ACCEPT  # 或添加 SSH 规则
```

#### wait_for 超时
```bash
# 检查目标端口是否真的开放
nc -zv <host> <port>
# 或
telnet <host> <port>
```

#### 防火墙规则查看
```bash
# firewalld
sudo firewall-cmd --list-all

# ufw
sudo ufw status verbose

# iptables
sudo iptables -L -n -v
```

### 相关链接
- [Firewalld 防火墙管理](network/firewalld/README.md) - RHEL 系统动态防火墙
- [UFW 防火墙管理](network/ufw/README.md) - Ubuntu/Debian 简化防火墙
- [iptables 防火墙与 NAT 规则](network/iptables/README.md) - 内核级防火墙管理
- [Wait For 端口/服务监控](network/wait_for/README.md) - 服务可用性监控
- [Port 端口健康探测](network/port/README.md) - 批量端口检查、安全探测
- [Route 静态路由管理](network/route/README.md) - 多网卡路由配置
- [Interface 网络接口管理](network/interface/README.md) - 网络接口配置管理
- [网络模块总览](network/README.md) - 网络模块完整指南