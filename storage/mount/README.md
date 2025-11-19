# mount 模块演练指南

## 模块用途
`ansible.posix.mount` 用于声明挂载点与设备之间的关系，可同步更新 `/etc/fstab`，也能在 check 模式中验证挂载选项是否正确。本示例通过 loopback 镜像演示在受限环境下的安全操作流程。

## 主要参数
- `src`：需要挂载的设备或文件（示例中指向 `dd` 生成的 loopback 镜像）。
- `path`：挂载点目录，建议放在 `/tmp` 或工作目录，避免误写真实业务路径。
- `fstype`：文件系统类型，例如 `ext4`、`xfs`，应与 loopback 初始化时保持一致。
- `opts`：挂载参数，常见值有 `defaults`、`noatime`、`ro` 等，可在示例变量中自定义。
- `fstab`：可选，自定义模拟 fstab 文件，便于在无 root 权限环境中做 dry-run。
- `state`：`present` 写入 fstab / 保证挂载，`absent` 代表卸载；示例维持 `present` 用于展示。

## 返回值
- `changed`：指示是否需要写入 fstab 或调整挂载状态，配合 `changed_when: false` 可在教学中保持幂等。
- `mount`：返回当前挂载信息（mount point、src、fstype）。
- `diff`：在开启 diff 时显示 fstab 预计追加的条目，便于评审。

## 安全注意事项
1. **备份 fstab**：真实环境务必备份 `/etc/fstab`，并在 `state: present` 前先使用 `ro` 选项测试。
2. **只读演练**：搭配 `ansible-playbook --check` + `changed_when: false` 可确认条目是否期望被修改。
3. **loopback 隔离**：即便是演示环境，也应将镜像与挂载点放在工作目录下，避免覆盖系统目录。

## 测试步骤（受限环境）
1. 安装依赖：`ansible-galaxy collection install ansible.posix`。
2. 在 `vars/example_vars.yml` 中确认 `storage_loop_file` 与 `storage_mount_point` 指向可写目录。
3. 执行下列命令，生成镜像并模拟绑定：
   ```bash
   dd if=/dev/zero of=$HOME/.ansible_storage_demo/loop-mount.img bs=1M count=8
   losetup --find --show $HOME/.ansible_storage_demo/loop-mount.img  # 无 root 会失败但可配合 --check 观察
   ```
4. 运行 `ansible-playbook playbook.yml -i localhost, --connection=local --check`，所有任务会先 `assert` 检查 `ansible_check_mode`，再输出 mount 模块的计划更改。
5. 若需真实挂载，请切换到实验主机、备份 fstab，并取消变量中的占位 loop 设备。

## 附加提示
- 若想验证多条挂载记录，可以在 vars 中追加 `storage_additional_mounts`，再配合 `loop` 批量处理。
- 结合 `ansible.builtin.command` 与 `loop` 的示例任务可帮助你了解 `dd`、`losetup` 的执行顺序，即便在没有 sudo 的环境中也能看到完整计划。
