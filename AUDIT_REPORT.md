# ansible_playbook 模块审计报告

## 1. 审计概览
- **审计范围**：仓库中 17 个一级目录、91 个 `playbook.yml`、所有 `README.md` 与 `vars/example_vars.yml`、`metadata/modules.yaml` 以及 `tests/` 下的 Pytest 套件。
- **方法**：使用 ripgrep / Python 脚本统计（如 `rg`, `pathlib` 扫描 `gather_facts`、`⚠️`、`no_log`）、逐个抽样阅读（web、applications、commands、monitoring、system 等目录）以及对 `metadata`、根 `README.md` 进行人工比对。
- **总体结论**：
  - 体系结构完整，所有模块均包含 README / playbook / vars，且元数据、根 README 的索引已覆盖最新的 timezone/locale/selinux 模块。
  - 仍存在多项需要统一的规范：36 个 playbook 未显式声明 `gather_facts`，14 个示例变量文件缺少统一的 `⚠️` 头部警示，部分 handler/notify 名称为英文，`check_mode` 覆盖率仅 34%（31/91），安全层面发现 1 个 Critical 问题。

## 2. 问题清单（按优先级）

### 2.1 Critical
| 编号 | 问题描述 | 位置 | 影响 | 改进建议 |
| --- | --- | --- | --- | --- |
| C1 | Docker 容器 playbook 未对密码/密钥使用 `no_log` | `applications/docker_container/playbook.yml`（第 39-86 行） | `redis_password`、`app_secret_key`、`DATABASE_URL` 等会直接出现在任务输出，存在凭证泄露风险。 | 将 `community.docker.docker_container` 涉及密码/密钥的任务包裹在 block 内设置 `no_log: true`，并在 vars 中统一使用 `vault_` 前缀变量。 |

### 2.2 High
| 编号 | 问题描述 | 位置 | 影响 | 改进建议 |
| --- | --- | --- | --- | --- |
| H1 | 36 个 playbook 未显式声明 `gather_facts` | `web/*`, `version_control/*`, `commands/{command,raw,shell,script}`, `network/{firewalld,ufw,iptables,wait_for}`, `applications/{pip,docker_container,package,docker_image,kubernetes,npm,apt,git,yum}`, `files/*` | 不同 Ansible 默认值可能导致执行环境不一致，也违反了项目“每个 play 设置 gather_facts”的要求。 | 在每个 Play 开头补充 `gather_facts: false`（或 true/yes/no 视需求），并在 README 中注明。 |
| H2 | 14 个 `vars/example_vars.yml` 缺少统一的 `# ⚠️` 头部警示 | `advanced/{loop_matrix,import_tasks,block_always,import_playbook}`, `monitoring/{prometheus,splunk,nagios,datadog,elk,zabbix}`, `commands/expect`, `message_queue/{rabbitmq_user,kafka_topic,rabbitmq_queue}`, `message_queue/rabbitmq_user` | 不符合“示例变量文件必须包含 ⚠️ 警告标识”的规范，难以及时提醒学员这些变量是占位符。 | 在文件开头插入 `# ⚠️ 示例警告…`，并强调需要 Vault/环境变量替换。 |
| H3 | 应用模块的 handler/notify 名称仍为英文 | `applications/package`、`applications/apt`、`applications/yum`、`applications/git`、`applications/docker_image` | 破坏“全中文任务名/处理器名”的一致性，也让 pytest 难以检查中文可读性。 | 将 handler 名称及 `notify/listen` 标签改写为中文，如“缓存已更新”“主应用需重启”等；若需兼容旧引用，可使用 `listen` 提供中英文别名。 |

**H1 文件清单**（共 36 个）：
web/ssl_certificate, web/haproxy, web/web_config, web/nginx, web/apache2, version_control/gitlab_project, version_control/git_workflow, version_control/hg, version_control/github_release, commands/script, commands/shell, commands/raw, commands/command, network/firewalld, network/ufw, network/iptables, network/wait_for, applications/pip, applications/docker_container, applications/package, applications/docker_image, applications/kubernetes, applications/npm, applications/apt, applications/git, applications/yum, files/copy, files/fetch, files/template, files/file, files/archive, files/find, files/unarchive, files/lineinfile, files/stat, files/synchronize。

**H2 文件清单**（共 14 个）：
advanced/loop_matrix, advanced/import_tasks, advanced/block_always, advanced/import_playbook, monitoring/prometheus, monitoring/splunk, monitoring/nagios, monitoring/datadog, monitoring/elk, monitoring/zabbix, commands/expect, message_queue/rabbitmq_user, message_queue/kafka_topic, message_queue/rabbitmq_queue。

### 2.3 Medium
| 编号 | 问题描述 | 位置 | 影响 | 改进建议 |
| --- | --- | --- | --- | --- |
| M1 | `check_mode` 覆盖率偏低，仅 31/91 个 playbook 展示了 dry-run 行为 | 全局 | 无法统一示范“安全预演”实践，亦与 README 中的最佳实践描述不符。 | 制定模板要求：关键改动任务需加 `check_mode: true` 示例；新增 pytest 统计确保每个目录至少存在一个 `check_mode` 示例。 |
| M2 | Pytest 未覆盖新的规范（gather_facts、⚠️、handler 中文化） | 例如 `tests/applications/test_applications.py` 仅检查 `vars_files`/FQCN/中文存在 | 规范违背时无法在 CI 中提前发现（此次 H1/H2/H3 即未被检测到）。 | 在各目录的测试中新增断言：`gather_facts` 必出现；`vars/example_vars.yml` 含 `⚠️`；`notify/listen` 文本包含中文。 |
| M3 | 示例依赖未集中维护 | 仓库缺少 `collections/requirements.yml`、`requirements.txt`，依赖只散落在 README/metadata | 学员需要手动逐页找依赖，且版本无法锁定。 | 新增顶层 `collections/requirements.yml` 与 `requirements.txt`，由 README 引用，并在 CI 中用于 `ansible-galaxy collection install -r collections/requirements.yml`。 |

### 2.4 Low
| 编号 | 问题描述 | 位置 | 影响 | 改进建议 |
| --- | --- | --- | --- | --- |
| L1 | 缺少自动化的模块索引生成脚本 | `metadata/modules.yaml` 需人工维护 | 随着模块数量增加，容易遗漏（虽然当前内容一致，但维护成本较高）。 | 编写 `tools/generate_metadata.py` 读取目录结构生成 YAML/README 索引，并在 CI 中校验。 |
| L2 | 根 README 尚未加入“审计报告/风格指南”引用 | `README.md` | 读者难以发现本报告及未来的规范更新。 | 在根 README 的“贡献指南”处添加指向 `AUDIT_REPORT.md` 与风格指南章节的链接。 |

## 3. 问题类别修复建议
1. **Playbook 规范**（覆盖 H1、M1）：
   - 为每个 Play 显式设置 `gather_facts`、`become`、`check_mode` 示例，并在模板中提供占位符。
   - 添加 lint/pytest 规则：解析 YAML，若缺少 `gather_facts` 或 `check_mode`，测试直接失败。
2. **中文文档/命名**（覆盖 H3）：
   - 统一 `- name`、`notify/listen`、handler 名称使用中文描述；若需保留英文代号，可使用 `listen` 提供别名。
   - README 中的章节必须为中文标题，可使用术语解释（如 “GitHub Release（发行版）”）。
3. **安全处理**（覆盖 C1、H2）：
   - 所有涉及密码/API Token 的任务默认放在 `block` 中统一 `no_log: true`。
   - `vars/example_vars.yml` 顶部统一模板：`# ⚠️ ...`，并要求敏感字段以 `vault_` 前缀命名。
4. **示例与依赖**（覆盖 M3）：
   - 在根目录新增 `collections/requirements.yml`、`requirements.txt`，每个 README 仅引用，不再重复命令。
   - 模块使用的模板/脚本需在 README 的 “相关示例” 列表中点明路径，测试也要检查文件是否存在。
5. **测试补强**（覆盖 M2）：
   - 扩展 `tests/<category>/test_*.py`：解析 playbook 断言 `gather_facts`、`no_log`、`⚠️`、`中文 handler` 等关键规则。
   - 在 `tests/system/test_system.py` 等文件中加入针对新模块（timezone/locale/selinux）的 check_mode/gather_facts 断言，避免回退。
6. **元数据与流程**（覆盖 L1）：
   - 编写生成脚本，CI 阶段比较脚本输出与 `metadata/modules.yaml`，防止漏记；同理也可生成根 README 的模块表格。
7. **根文档导航**（覆盖 L2）：
   - 在 README“学习路径 / 贡献指南”处放置《AUDIT_REPORT.md》及风格指南链接，并说明更新频率。
8. **冗余/冲突检查**：
   - 本次未发现重复模块或矛盾参数，但建议在 metadata 生成脚本中加入去重校验，确保未来扩展时自动检测冲突。

## 4. 统一代码风格指南（建议直接纳入贡献指南）
1. **Playbook 结构**
   - 文件以 `---` 开头，Play 级别字段顺序固定为：`- name` → `hosts` → `gather_facts` → `become` → `vars_files` → `tasks` → `handlers`。
   - 所有模块调用必须使用 FQCN（如 `ansible.builtin.copy`、`community.docker.docker_container`）。
   - 任务名、条件、循环说明统一使用中文，涉及外文术语时采用“中文（英文）”形式，例如“容器镜像（image）”。
   - 关键变更任务提供 `check_mode: true` 示例，并在注释里说明“此任务开启 check_mode 以便预演”。

2. **安全约定**
   - 凡是引用密码、Token、证书、密钥的任务都要加 `no_log: true`；如需调试，可通过变量开关 `enable_sensitive_logging` 控制。
   - 示例变量统一以 `vault_` 前缀指向 Vault，README 中给出 `ansible-vault encrypt_string` 示例。
   - `shell`/`command`/`raw` 任务写明 `set -e`、`warn: false` 等安全注释，并说明为何这样设置。

3. **变量文件 (`vars/example_vars.yml`)**
   - 第一行固定模板：`# ⚠️ 本文件仅为示例，占位符必须使用 Ansible Vault 或环境变量替换`。
   - 对每组变量加上中文注释，必要时列出“生产环境注意事项”。
   - 不允许出现真实值，所有凭证字段应指向 `vault_*` 或清晰的占位符。

4. **文档（README）**
   - 标准章节：模块用途、主要参数、返回值、使用情境、中文安全提示、环境依赖、常见问题、最佳实践、相关示例。
   - 内容必须以中文叙述，英文术语仅作为括号补充；引用命令时在下方提供中文注解。

5. **处理器 / Notify**
   - `notify` 与 `listen` 的值必须是中文短语；若需要兼容旧名字，可写成 `listen: ["缓存已更新", "cache updated"]`，但默认展示中文。
   - Handlers 应在结尾提供“总结”任务，对执行结果进行中文输出，保持学习体验一致。

6. **测试**
   - 每个目录的 pytest 至少校验：README 章节齐全、playbook 含 `gather_facts`/`check_mode`、vars 含 `⚠️`、FQCN 正确、任务/handler 中文化。
   - 编写通用辅助函数（如 `assert_has_warning(path)`）以减少重复代码。

7. **元数据/根文档**
   - 新增模块时同时更新 `metadata/modules.yaml` 与根 README，并运行生成脚本校验；提交 PR 时附上脚本输出 diff。

## 5. 其它观察
- 根 `README.md` 与 `metadata/modules.yaml` 已同步列出 system/timezone、system/locale、system/selinux 模块，结构正确。
- 各目录下的模板、脚本、示例数据文件齐全，未发现缺失引用。
- 当前未检测到重复模块或矛盾参数描述，但建议在下一轮迭代中把本报告纳入 README 以便团队随时查阅。
