# LVM 卷组（lvg）模块演练指南

## 模块用途

`community.general.lvg` 模块用于在 Linux 系统上创建、扩展和移除 LVM 卷组（Volume Group）。LVM 卷组是由一个或多个物理卷（PV）组成的存储池，在其之上可以创建逻辑卷（LV）。本示例通过 loopback 设备演示如何在非 root 或受限环境中学习 LVM 卷组的基本操作，包括卷组的创建、查询和安全删除。

## 主要参数

- `vg_name`：卷组名称，用于标识和管理 LVM 卷组。
- `pvs`：物理卷列表，即组成该卷组的块设备（如 `/dev/sda1`、loopback 设备等）。
- `state`：期望状态（`present` 创建或扩展、`absent` 删除）。
- `force`：强制删除非空卷组（谨慎使用，可能导致数据丢失）。
- `pesize`：物理范围大小（PE size），默认 4MB，用于粒度控制。

## 返回值

- `vg_name`：卷组名称。
- `pvs`：卷组包含的物理卷列表。
- `vg_size`：卷组总容量。
- `vg_free`：卷组可用容量。
- `vg_extent_size`：物理范围大小。
- `changed`：表示是否执行了更改。

## 使用情境

1. **初期部署**：创建新的 LVM 卷组，作为后续逻辑卷的容器。
2. **扩展存储**：向现有卷组添加新的物理卷。
3. **维护测试**：在测试环境使用 loopback 设备学习 LVM 操作，而不影响真实硬盘。
4. **持续集成**：在 CI 环境中通过 `ansible-playbook --check` 预览卷组操作。

## 安全注意事项

1. **只读测试**：先以 `ansible-playbook --check` 查看计划操作，再决定是否执行。
2. **数据备份**：对于包含重要数据的卷组，先做全量备份再进行修改。
3. **卷组删除**：删除卷组前需确认所有逻辑卷已删除，避免数据丢失。
4. **物理卷检查**：修改卷组前，先用 `pvs`/`vgs` 命令确认物理卷状态。

## 受限环境测试流程

1. **准备镜像**：
   ```bash
   dd if=/dev/zero of=$HOME/.storage_lab/pv-demo1.img bs=1M count=100
   dd if=/dev/zero of=$HOME/.storage_lab/pv-demo2.img bs=1M count=100
   ```

2. **绑定为 loopback 设备**（需 sudo）：
   ```bash
   sudo losetup --find --show $HOME/.storage_lab/pv-demo1.img  # /dev/loop0
   sudo losetup --find --show $HOME/.storage_lab/pv-demo2.img  # /dev/loop1
   ```

3. **运行 Playbook**（Check 模式）：
   ```bash
   ansible-playbook playbook.yml -i localhost, --connection=local --check
   ```

4. **Check 模式输出**：playbook 会输出计划创建的卷组信息（PV 列表、卷组名称等），不会实际修改系统。

5. **实际执行**（仅在拥有 sudo 权限时）：
   ```bash
   ansible-playbook playbook.yml -i localhost, --connection=local
   ```

## 安装与依赖

- `community.general` collection（包含 `lvg` 模块）。
- 主机需要安装 `lvm2` 软件包及其命令行工具（`pvcreate`、`vgcreate` 等）。
- pytest 校验要求 README 包含 loopback 说明、check 模式说明、安全提示等内容。

## 常见使用场景

### 场景 1：使用 loopback 演练卷组创建
```yaml
- name: 演练创建 LVM 卷组（loopback 环境）
  hosts: localhost
  connection: local
  gather_facts: no
  
  tasks:
    - name: 创建 LVM 卷组
      community.general.lvg:
        vg_name: demo_vg
        pvs:
          - /dev/loop0
          - /dev/loop1
        state: present
      register: vg_result
      changed_when: false  # 演练模式下不改变系统
    
    - name: 输出卷组信息
      debug:
        msg: "{{ vg_result }}"
```

### 场景 2：Check 模式验证卷组操作
```bash
# 只查看计划操作，不实际修改
ansible-playbook playbook.yml --check

# 查看详细信息
ansible-playbook playbook.yml -v --check
```

### 场景 3：扩展现有卷组
```yaml
- name: 向卷组添加新的物理卷
  community.general.lvg:
    vg_name: demo_vg
    pvs:
      - /dev/loop0
      - /dev/loop1
      - /dev/loop2  # 新增
    state: present
```

## 故障排查

### 问题 1：卷组创建失败
**症状**：`community.general.lvg` 返回错误

**排查**：
```bash
# 检查 lvm2 是否安装
sudo lvm version

# 检查物理卷状态
sudo pvs

# 检查是否为 loopback 设备
sudo losetup -a
```

### 问题 2：卷组删除失败（非空卷组）
**症状**：无法删除包含逻辑卷的卷组

**排查**：
```bash
# 查看卷组信息
sudo vgs

# 查看逻辑卷
sudo lvs

# 删除所有逻辑卷后再删除卷组
sudo lvremove -f /dev/demo_vg/*
```

## 相关资源

- [LVM 官方文档](https://sourceware.org/lvm2/wiki/index.php)
- [Ansible community.general.lvg 模块](https://docs.ansible.com/ansible/latest/collections/community/general/lvg_module.html)
- [Linux LVM 实战指南](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/logical_volume_manager_administration/)
