# import_playbook 模块复用

`import_playbook` 在 Play 级别引入其他 Playbook，适用于将大型部署拆分成多个阶段或重用通用 Playbook。与 `include_*` 不同，`import_playbook` 在解析阶段就完成合并，无法通过 `when` 动态控制。

## 使用场景
- **多阶段部署**：按准备、部署、验证拆分，每个阶段有独立 Playbook
- **团队协作**：不同职能（网络、存储、应用）维护各自 Playbook，主 Playbook 统一调用
- **环境复用**：将通用操作（如准备系统用户、安装依赖）封装为独立 Playbook

## 语法
```yaml
---
- import_playbook: prepare_infrastructure.yml
- import_playbook: deploy_applications.yml
- import_playbook: verify_services.yml
```

## 重要特性
- **静态引入**：Ansible 在解析阶段（而非执行阶段）就合并 Playbook，不支持条件判断
- **独立变量作用域**：每个被引入的 Playbook 有独立的 `vars`、`vars_files`、`hosts` 定义
- **执行顺序固定**：按 `import_playbook` 出现顺序依次执行

## 与 include_tasks 区别
- `import_playbook`：在顶层引入整个 Playbook，包含 hosts、vars 等 Play 元素
- `include_tasks`：在任务内部引入任务列表，只包含任务

## 常见陷阱
1. **误用 when 条件**：`import_playbook` 不支持条件，需要在被引入的 Play 内部写条件
2. **变量覆盖**：多个 Playbook 定义同名变量时，后引入的会覆盖先引入的
3. **循环依赖**：避免 A 引入 B，B 又引入 A 的情况

完整示例见 [playbook.yml](playbook.yml)。
