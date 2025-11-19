# 磁盘信息采集（disk_facts）模块演练指南

## 模块用途

本示例展示如何使用 `ansible.builtin.setup` 模块（gather_facts）采集系统磁盘和块设备信息，获取关于硬件配置、块设备、LVM、分区等的详细数据。通过使用 `filter` 参数，可以选择性地采集特定的硬件信息（如磁盘列表、分区信息、LVM 卷等）。这对于自动化部署、系统审计和容量规划非常有用。

## 主要模块

### ansible.builtin.setup
**用途**：收集目标主机的系统信息（facts）

**常用参数**：
- `filter`：使用通配符模式过滤 facts（如 `ansible_*disk*`、`ansible_*lvm*`）
- `gather_subset`：指定采集的信息子集（如 `hardware`、`network`、`all`）
- `gather_timeout`：采集超时时间（秒）

**常用 facts 变量**：
- `ansible_mounts`：挂载点列表（包含设备、挂载路径、文件系统类型等）
- `ansible_devices`：块设备列表（如 sda、sdb 等）
- `ansible_lvm`：LVM 卷组和逻辑卷信息（如果系统已安装 LVM）
- `ansible_memtotal_mb`：总内存容量
- `ansible_processor_vcpus`：CPU 逻辑核心数

**示例**：
```yaml
- name: 采集全部系统信息
  ansible.builtin.setup:
    gather_subset: all
  register: system_facts

- name: 采集硬件信息
  ansible.builtin.setup:
    gather_subset: hardware
  register: hardware_facts

- name: 采集磁盘相关信息
  ansible.builtin.setup:
    filter: ansible_*disk*
  register: disk_info
```

## 主要参数说明

### Gather Subset 选项
- `all`：采集所有信息（可能较慢）
- `hardware`：CPU、内存、磁盘等硬件信息
- `network`：网络接口和配置信息
- `virtual`：虚拟化相关信息
- `ohai`：通过 Ohai 采集信息（需要安装 Ohai）
- `facter`：通过 Facter 采集信息（需要安装 Facter）

### 重要 Facts 字段
- `ansible_mounts`：系统挂载点信息
  - `device`：块设备名称
  - `mount`：挂载点路径
  - `fstype`：文件系统类型
  - `size_total`：总容量（字节）
  - `size_available`：可用容量（字节）
  - `size_used`：已用容量（字节）

- `ansible_devices`：块设备信息
  - `device_name`（如 `sda`）：设备名称
  - `model`：设备型号
  - `size`：设备大小
  - `partitions`：分区列表

- `ansible_lvm`：LVM 信息
  - `lvs`：逻辑卷列表
  - `pvs`：物理卷列表
  - `vgs`：卷组列表

## 使用情境

1. **系统审计**：自动采集和报告系统硬件配置
2. **容量规划**：评估磁盘利用率和可用空间
3. **自动化部署**：根据系统磁盘配置动态调整部署策略
4. **监控告警**：定期采集磁盘信息，生成容量报告
5. **灾备管理**：记录系统硬件配置用于灾难恢复规划

## 返回值

采集到的 facts 包括：
- `ansible_mounts`：挂载点列表
- `ansible_devices`：块设备列表
- `ansible_processor_count`：物理 CPU 数
- `ansible_processor_vcpus`：逻辑 CPU 数
- `ansible_memtotal_mb`：总内存
- `ansible_lvm`：LVM 信息（如果已安装）

## 常见部署场景

### 场景 1：采集所有磁盘和挂载信息
```yaml
- name: 采集硬件信息
  ansible.builtin.setup:
    gather_subset: hardware
  register: hardware_info

- name: 输出磁盘信息
  ansible.builtin.debug:
    msg: "{{ hardware_info.ansible_facts.ansible_mounts }}"

- name: 输出块设备信息
  ansible.builtin.debug:
    msg: "{{ hardware_info.ansible_facts.ansible_devices }}"
```

### 场景 2：检查磁盘可用空间
```yaml
- name: 采集挂载点信息
  ansible.builtin.setup:
    filter: ansible_mounts
  register: mounts_info

- name: 检查根分区可用空间
  ansible.builtin.set_fact:
    root_available: "{{ item.size_available | int / 1024 / 1024 / 1024 }}"
  loop: "{{ mounts_info.ansible_facts.ansible_mounts }}"
  when: item.mount == '/'
  register: root_space

- name: 输出根分区可用空间
  ansible.builtin.debug:
    msg: "根分区可用空间: {{ root_space.ansible_facts.root_available | round(2) }} GB"
```

### 场景 3：采集 LVM 信息
```yaml
- name: 采集 LVM 信息
  ansible.builtin.setup:
    filter: ansible_lvm
  register: lvm_info

- name: 输出 LVM 卷组
  ansible.builtin.debug:
    msg: "{{ lvm_info.ansible_facts.ansible_lvm }}"
  when: lvm_info.ansible_facts.ansible_lvm is defined
```

### 场景 4：生成系统硬件报告
```yaml
- name: 采集全部硬件信息
  ansible.builtin.setup:
    gather_subset: hardware
  register: hw_facts

- name: 生成硬件报告
  ansible.builtin.template:
    src: hardware_report.j2
    dest: /tmp/hardware_report.txt
  vars:
    facts: "{{ hw_facts.ansible_facts }}"
```

## 如何在本地测试

### 1. 语法检查
```bash
ansible-playbook playbook.yml --syntax-check
```

### 2. Check 模式（模拟运行）
```bash
ansible-playbook playbook.yml -i localhost, --connection=local --check
```

### 3. 采集本地信息
```bash
# 采集所有 facts
ansible-playbook playbook.yml -i localhost, --connection=local

# 采集硬件信息
ansible-playbook playbook.yml -i localhost, --connection=local --tags facts_hardware
```

### 4. 手动采集 facts
```bash
# 采集所有信息
ansible localhost -m setup -a "gather_subset=all"

# 采集硬件信息
ansible localhost -m setup -a "gather_subset=hardware"

# 采集磁盘相关信息
ansible localhost -m setup -a "filter=ansible_*disk*"

# 采集挂载点信息
ansible localhost -m setup -a "filter=ansible_mounts"
```

### 5. 过滤输出
```bash
# 仅输出特定 facts
ansible localhost -m setup -a "filter=ansible_mounts" -v

# 输出为 JSON 格式
ansible localhost -m setup -a "gather_subset=hardware" --verbose > facts.json
```

## 磁盘信息解析

### Mounts 信息字段
```yaml
ansible_mounts:
  - mount: /
    device: /dev/sda1
    fstype: ext4
    size_total: 107374182400  # 字节
    size_available: 53687091200  # 字节
    size_used: 53687091200
    inode_total: 6553600
    inode_available: 6400000
    inode_used: 153600
```

### Devices 信息字段
```yaml
ansible_devices:
  sda:
    model: QEMU HARDDISK
    size: 100 GB
    host: SCSI storage controller
    vendor: ATA
    serial: serial_number
    partitions:
      sda1:
        start: 2048
        sectors: 209717248
        sectorsize: 512
```

### LVM 信息字段
```yaml
ansible_lvm:
  lvs:
    - name: root
      vg: vg0
      size_g: 20
  pvs:
    - name: /dev/sda2
      vg: vg0
      free_g: 5
      used_g: 15
  vgs:
    - name: vg0
      size_g: 20
      free_g: 5
      pvs: ['/dev/sda2']
```

## 安全注意事项

1. **只读操作**：`setup` 模块仅采集信息，不修改系统，是安全的
2. **权限需求**：某些 facts 采集可能需要 root 权限（如 LVM 信息）
3. **信息保护**：采集的系统信息可能包含敏感数据，请妥善处理生成的报告
4. **隐私考虑**：避免在公开渠道分享包含真实磁盘路径和容量的报告
5. **定期审计**：定期采集信息用于系统审计和监控

## 故障排查

### 问题 1：采集信息超时
**症状**：`gather_facts` 命令执行缓慢或超时

**排查**：
```bash
# 增加超时时间
ansible-playbook playbook.yml --timeout 60

# 或在 playbook 中设置
- name: 采集信息（增加超时）
  ansible.builtin.setup:
    gather_timeout: 60
    gather_subset: hardware
```

### 问题 2：缺少 LVM 信息
**症状**：`ansible_lvm` 为空或未定义

**排查**：
```bash
# 检查系统是否安装了 LVM
sudo lvs
sudo pvs
sudo vgs

# 检查 lvm2 软件包
dpkg -l | grep lvm2
```

### 问题 3：权限不足
**症状**：某些硬件信息无法采集

**排查**：
```bash
# 使用提升权限的方式采集
ansible-playbook playbook.yml --become

# 或在 playbook 中添加 become: yes
```

## 相关资源

- [Ansible Setup 模块文档](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/setup_module.html)
- [Ansible Facts 参考](https://docs.ansible.com/ansible/latest/user_guide/playbooks_vars_facts.html)
- [Linux 块设备管理](https://wiki.archlinux.org/title/Block_device)
- [LVM 管理指南](https://sourceware.org/lvm2/wiki/index.php)
