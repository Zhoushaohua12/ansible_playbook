# 存储模块实践指南

## 章节概览
本章节聚焦磁盘与文件系统的基础操作，涵盖从创建模拟磁盘、构建逻辑卷到格式化与挂载的完整流程。示例全部以中文注释编写，并通过 `ansible-playbook --check`、`changed_when: false` 等手段，将潜在破坏性操作限制在安全的演练环境中。

## 涉及模块

### 基础模块
- [mount 模块](mount/README.md)：管理 fstab 条目与挂载点，示范如何在 loopback 设备上编写受控挂载。
- [lvol 模块](lvol/README.md)：创建与调整 LVM 逻辑卷，配合临时 VG/LV 展示参数含义与返回值。
- [filesystem 模块](filesystem/README.md)：在模拟块设备上格式化文件系统，并解释只读验证与元数据检查。

### 高级模块
- [lvg 模块](lvg/README.md)：管理 LVM 卷组，学习如何创建、扩展和删除卷组。
- [parted 模块](parted/README.md)：使用 GNU Parted 进行磁盘分区操作，支持 MBR 和 GPT 分区表。
- [disk_facts 模块](disk_facts/README.md)：采集和分析系统磁盘信息，用于容量规划与系统审计。

## 测试与验证策略
1. **Loopback 设备**：先用 `dd`/`truncate` 生成小型镜像，再通过 `losetup --find --show` 绑定至临时设备，整个过程在 `check` 模式下仅输出计划操作。
2. **受限环境执行**：所有 playbook 第一任务都会 `assert` 当前处于 `ansible_check_mode`，防止在生产或无权限环境中误写磁盘。
3. **重复可回放**：每个任务都显式声明 `changed_when: false` 或仅用于说明，从而可以在 CI、教学环境中多次运行且不会污染宿主机。
4. **pytest 校验**：`tests/storage/test_storage.py` 会检查 README 章节、loopback 说明、中文注释与安全提示，确保文档与示例持续符合规范。

## 文件结构
```
storage/
├── README.md                # 本说明文档
├── mount/                   # mount 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── lvol/                    # lvol 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── filesystem/              # filesystem 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── lvg/                     # lvg 模块示例（LVM 卷组）
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── parted/                  # parted 模块示例（磁盘分区）
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
└── disk_facts/              # disk_facts 模块示例（磁盘信息采集）
    ├── README.md
    ├── playbook.yml
    ├── vars/example_vars.yml
    └── templates/disk_report.j2
```

## 安全注意事项
- **不要在生产环境直接运行本章节 playbook**，它们默认写入假的设备路径，仅用于教学。若需真实演练，请在沙箱或离线主机中启用，并提前做好全量数据备份。
- 对真实磁盘或 LVM 进行操作前，应先复制 fstab/VG metadata 并执行只读挂载或 `--check` 演练以确认任务顺序。
- 敏感参数（如 VG 名称、挂载点路径、模拟设备文件）统一存放在 `vars/example_vars.yml`，实际项目请使用 Vault 或环境变量覆盖。

## 快速开始
1. 进入目标模块目录，例如 `storage/mount/`。
2. 按需修改 `vars/example_vars.yml`，保持占位符或自定义 loopback 路径。
3. 使用 `ansible-galaxy collection install ansible.posix`、`ansible-galaxy collection install ansible.utils` 等命令准备依赖。
4. 执行：
   ```bash
   ansible-playbook playbook.yml -i localhost, --connection=local --check
   ```
5. 阅读任务输出，确认 `command` 模拟步骤、loop 设备规划与 `mount/lvol/filesystem` 的返回值，再对照 README 的测试tips 调整至自己的实验环境。

## 常见问题
- **为什么任务强制要求 --check？** 防止无 root 权限时命令失败或误改真实磁盘，可视作“干跑”模式。
- **如何在 CI 中测试？** 结合 `pytest` + `ansible-playbook --check`，并将 loopback 文件放在工作目录（例如 `/tmp/.storage_lab`）。
- **需要真实 losetup 吗？** 非必需。示例默认只打印命令，如需真实绑定请在拥有 sudo 的实验机上运行并更新变量 `*_loop_device`。
