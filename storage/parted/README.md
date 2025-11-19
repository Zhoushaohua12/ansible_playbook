# Parted 磁盘分区模块演练指南

## 模块用途

`community.general.parted` 模块用于在 Linux 系统上使用 GNU Parted 进行磁盘分区操作。它支持创建、删除、修改分区，支持 MBR 和 GPT 分区表，是学习和自动化磁盘管理的强大工具。本示例通过 loopback 设备演示分区创建、查询和验证流程，在受限或非 root 环境中安全地学习磁盘分区操作。

## 主要参数

- `device`：目标磁盘设备路径（如 `/dev/sda`、loopback 设备等）
- `number`：分区号（1、2、3 等）
- `state`：分区状态（`present` 创建、`absent` 删除）
- `part_start`：分区起始位置（支持百分比或绝对位置）
- `part_end`：分区结束位置（支持百分比或绝对位置）
- `part_type`：分区类型（MBR 模式下为 `primary`/`extended`/`logical`；GPT 模式下为各种类型 UUID）
- `label`：分区表类型（`msdos` 对应 MBR，`gpt` 对应 GPT）
- `unit`：位置单位（`MiB`、`GiB`、`%` 等）
- `flags`：分区标志（如 `boot`、`lvm` 等）
- `align`：对齐方式（`minimal`、`optimal` 等）

## 返回值

- `partitions`：分区列表（包含分区号、大小、起始位置等信息）
- `disk`：磁盘设备信息
- `table`：分区表类型
- `unit`：使用的单位
- `changed`：是否执行了修改

## 使用情境

1. **初期部署**：为新磁盘创建分区表和初始分区
2. **测试验证**：在 CI/CD 环境中使用 loopback 设备验证分区脚本
3. **文档生成**：通过 `--check` 模式生成磁盘分区计划
4. **学习教学**：在教学环境中安全地演练 parted 命令

## 安全注意事项

1. **销毁警告**：parted 对磁盘的修改是破坏性的，务必确认目标设备
2. **备份分区表**：执行分区前保存分区表备份
3. **只读验证**：先用 `--check` 模式验证操作
4. **非生产测试**：仅在测试环境或虚拟磁盘上运行
5. **Loopback 使用**：建议使用 loopback 设备进行演练

## 受限环境测试流程

1. **准备镜像文件**：
   ```bash
   dd if=/dev/zero of=$HOME/.storage_lab/disk-demo.img bs=1M count=500
   ```

2. **绑定为 loopback 设备**（需 sudo）：
   ```bash
   sudo losetup --find --show $HOME/.storage_lab/disk-demo.img
   # 返回：/dev/loop0
   ```

3. **运行 Playbook**（Check 模式）：
   ```bash
   ansible-playbook playbook.yml -i localhost, --connection=local --check
   ```

4. **Check 模式预览**：显示计划创建的分区表和分区信息

5. **实际执行**（需 sudo）：
   ```bash
   ansible-playbook playbook.yml -i localhost, --connection=local
   ```

## 安装与依赖

- `community.general` collection（包含 `parted` 模块）
- 主机需要安装 `parted` 软件包及其命令行工具
- pytest 校验要求 README 包含 loopback 设备说明、分区表类型、check 模式说明等

## 常见使用场景

### 场景 1：使用 loopback 创建 MBR 分区表
```yaml
- name: 在 loopback 设备上创建 MBR 分区表
  community.general.parted:
    device: /dev/loop0
    label: msdos
    unit: MiB
    state: present

- name: 创建主分区
  community.general.parted:
    device: /dev/loop0
    number: 1
    state: present
    part_start: 0%
    part_end: 50%
    part_type: primary
```

### 场景 2：GPT 分区表和 LVM 分区
```yaml
- name: 创建 GPT 分区表
  community.general.parted:
    device: /dev/loop0
    label: gpt
    state: present

- name: 创建 LVM 分区
  community.general.parted:
    device: /dev/loop0
    number: 1
    state: present
    part_start: 0%
    part_end: 100%
    flags: [lvm]
```

### 场景 3：Check 模式验证分区计划
```bash
# 预览将要执行的分区操作
ansible-playbook playbook.yml --check

# 查看详细信息
ansible-playbook playbook.yml -v --check
```

### 场景 4：删除分区
```yaml
- name: 删除分区
  community.general.parted:
    device: /dev/loop0
    number: 1
    state: absent
```

## 故障排查

### 问题 1：分区创建失败
**症状**：parted 模块返回错误

**排查**：
```bash
# 检查 parted 是否安装
which parted

# 手动查看分区表
sudo parted -l /dev/loop0

# 查看详细错误
ansible-playbook playbook.yml -vvv
```

### 问题 2：分区表识别错误
**症状**：磁盘没有分区表或格式不正确

**排查**：
```bash
# 初始化新的分区表
sudo parted /dev/loop0 mklabel msdos

# 验证分区表
sudo parted /dev/loop0 print
```

### 问题 3：权限不足
**症状**：操作需要 root 权限

**排查**：
```bash
# 使用 become 提升权限
ansible-playbook playbook.yml --become

# 或在 playbook 中添加 become: yes
```

## 相关资源

- [GNU Parted 官方文档](https://www.gnu.org/software/parted/manual/parted.html)
- [Ansible community.general.parted 模块](https://docs.ansible.com/ansible/latest/collections/community/general/parted_module.html)
- [MBR vs GPT 分区表对比](https://wiki.archlinux.org/title/Partitioning)
