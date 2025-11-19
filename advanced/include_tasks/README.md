# Include Tasks

`include_tasks` 按需加载外部任务文件，使 Playbook 得到模块化拆分。相比 `import_tasks`，它在运行时动态决定是否加载，适合带条件的场景。

## 语法
```yaml
- name: 根据系统类型加载对应任务
  ansible.builtin.include_tasks:
    file: "tasks/{{ ansible_facts['os_family'] }}.yml"
  apply:
    vars:
      pkg_state: latest
```

## 参数
- `file`：必填，指向待引入的任务文件，路径相对于当前 Playbook。
- `apply`：可为被包含的任务批量添加 `vars`、`tags`、`become` 等。
- `vars`：也可通过普通变量传递，类似调用函数时的实参。

## 返回值
`include_tasks` 自身不会产生结果，真正的返回值来自被包含的任务，必要时在子任务中 `register`。

## 常见陷阱
1. **路径解析**：路径基于运行 include 的文件，而非 `playbook_dir`，请保持结构清晰。
2. **变量作用域**：子任务可访问父 Play 的变量，也能接收 `apply.vars`；但子任务中定义的 `vars` 不会自动回写。
3. **循环中的 include**：在循环里 include 时，Ansible 会为每次迭代单独解析文件，注意控制开销。

## 如何调试/常见错误
- 运行时加上 `-vvv` 可看到具体引入的文件；若报找不到文件，使用 `debug: msg={{ playbook_dir }}` 检查路径。
- 子任务抛错时，回溯中会展示包含关系，可依据 `included: ...` 提示快速定位。

完整示例见 [playbook.yml](playbook.yml) 与配套的 [child_task.yml](child_task.yml)。