# import_tasks 静态任务复用

`ansible.builtin.import_tasks` 在解析阶段加载任务文件，适用于需要在多个 Play 中复用同一批任务且希望拥有一致的执行顺序时。本示例展示如何利用 import_tasks 将配置和清理逻辑拆分为独立文件，并结合 `when` 与变量控制不同环境的执行路径。

## 何时使用 import_tasks
- 需要静态（非动态）引入任务，部署计划固定
- 希望任务在 Playbook 解析阶段即可展开，便于查找依赖
- 同一批任务会在多个 Play 中使用，且希望共用相同变量

## 示例要点
1. 主 Playbook 使用 `vars_files` 统一定义服务列表和环境参数
2. `tasks/configure.yml` 内部通过 `loop` 遍历服务并渲染配置
3. `tasks/cleanup.yml` 则只在 `import_tasks_cleanup_enabled` 为真时执行
4. 每个任务文件都包含中文注释，并在任务内部使用 `when` 控制

## 与 include_tasks 的差异
- `import_tasks`：静态解析，支持 `tags`、`when`、`vars`，但不支持 `loop`
- `include_tasks`：运行时解析，可与 `loop` 搭配生成多份任务实例

更多细节见 [playbook.yml](playbook.yml) 与 `tasks/` 目录。
