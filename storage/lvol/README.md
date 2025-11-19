# lvol 模块演练指南

## 模块用途
`ansible.builtin.lvol` 用于在某个 VG 中创建或调整逻辑卷（LV），支持精确定义容量、条带数以及稀疏卷。示例通过 loopback 镜像 + 虚拟 VG 展示如何在教学环境中阅读返回值并验证参数组合。

## 主要参数
- `vg`: 目标卷组名称，例如 `vg_demo`，需提前由 `vgcreate` 初始化或在示例中以模拟命令展示。
- `lv`: 逻辑卷名称，如 `lv_logs`，配合 `state: present` 自动创建。
- `size`: 逻辑卷大小，支持 `m/g/t` 后缀（例：`32m`）。
- `pvs`: 物理卷列表，可绑定到 `losetup` 输出的设备；若在安全演练中仅需预览，可保留占位符。
- `thinpool`/`thinvolume`: 需要稀疏卷时可启用，示例保持默认。
- `force`: 设为 `yes` 可覆盖同名逻辑卷，真实环境建议搭配快照/备份后再启用。

## 返回值
- `changed`: 是否创建或调整了 LV。
- `lv`: 返回字典，包含 `name`、`size`, `vg`, `lv_path` 等关键字段。
- `stdout` / `stderr`: 捕获 lvm 命令输出，方便在 --check 模式下审阅计划动作。

## 安全注意事项
1. **备份 VG 元数据**：在生产环境运行前，使用 `vgcfgbackup` 备份卷组定义，并妥善保存到只读存储。
2. **只读验证**：通过 `ansible-playbook --check` 或将 `ansible.builtin.lvol` 与 `changed_when: false` 结合，先观察返回值再决定是否真实执行。
3. **数据隔离**：示例中的 VG/LV 名称、loop 设备仅供演示，务必替换为实验机专用值，禁止影响线上卷组。

## 测试步骤（受限环境）
1. 准备依赖：`ansible-galaxy collection install ansible.utils`（提供常用过滤器）、确保主机具备 `lvm2` 命令。
2. 运行 `dd if=/dev/zero of=$HOME/.ansible_storage_lvm/lvm-demo.img bs=1M count=64` 创建镜像文件。
3. 若拥有 sudo，可执行 `losetup --find --show lvm-demo.img && pvcreate /dev/loopX && vgcreate vg_demo /dev/loopX`，否则保持占位符并使用 `--check` 演练。
4. 执行 `ansible-playbook playbook.yml -i localhost, --connection=local --check`，playbook 会在首个任务断言 check 模式，并输出 `lvol` 模块的返回字典。
5. 需要真实变更时，请在沙箱主机中提前备份数据，并把 `lvm_pvs` 列表替换成实际物理卷。

## 受限环境技巧
- 配合 `ansible.builtin.command` + `loop` 展示 `pvcreate`、`vgcreate`、`lvremove` 等命令，即便因权限不足而跳过，也能记录计划。
- 将 `lvm_lv_size` 设为极小值（如 `16m`）以避免占用过多磁盘；测试完成后记得删除镜像与临时目录。
