# filesystem 模块演练指南

## 模块用途
`ansible.builtin.filesystem` 用于在块设备或镜像文件上创建文件系统，支持 ext4/xfs/btrfs 等格式，并可在 check 模式下预览格式化命令。本示例通过 loopback 设备展示如何在不具备 root 权限的环境中模拟格式化流程。

## 主要参数
- `fstype`: 目标文件系统类型，如 `xfs`、`ext4`，需要主机已安装对应 mkfs 工具。
- `dev`: 被格式化的块设备路径，可是 losetup 创建的设备或虚拟磁盘文件。
- `force`: 设为 `true` 时允许覆盖已有文件系统，演示环境默认 `false`。
- `opts`: 附加 mkfs 选项，例如 `-m 0`、`-n ftype=1`。
- `resizefs`: `yes` 时会尝试扩展已有文件系统。

## 返回值
- `device`: 实际处理的设备路径。
- `fstype`: 新建或已存在的文件系统类型。
- `cmd`: 底层执行的 `mkfs` 命令，便于在演示模式下确认安全性。
- `changed`: 表示是否真正执行了 mkfs；在演示示例中配合 `changed_when: false` 保持恒定。

## 安全注意事项
1. **永远确认设备路径**：真实环境格式化前请运行 `lsblk`/`blkid` 复核，防止误清空生产卷。
2. **只读测试**：先以 `ansible-playbook --check`、`changed_when: false` 检查命令，再决定是否执行。
3. **数据备份**：对于有价值的数据，需提前在对象存储或快照中备份多份，并做校验。

## 受限环境测试流程
1. 准备镜像：`dd if=/dev/zero of=$HOME/.ansible_storage_fs/fs-demo.img bs=1M count=16`。
2. 如需完整链路，可在具备 sudo 的环境执行 `losetup --find --show fs-demo.img`，否则保持 `fs_loop_device` 的占位符并使用 `--check` 观察输出。
3. 运行 `ansible-playbook playbook.yml -i localhost, --connection=local --check`，playbook 会断言当前处于 check 模式并打印 `filesystem` 模块的返回字段。
4. 若要验证 mkfs 选项，可在 vars 中调整 `fs_mkfs_options`，并在 README 所述的 loopback 设备上反复实验。

## 安装与依赖
- 只需 Ansible 自带的 `ansible.builtin.filesystem` 模块。
- 主机需要具备对应的 mkfs 命令，例如 `mkfs.xfs` 或 `mkfs.ext4`。
- pytest 校验要求 README 包含 loopback/`--check` 说明，请定期同步文档。
