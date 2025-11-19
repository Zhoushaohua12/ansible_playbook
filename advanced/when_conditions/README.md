# 条件判断（when）

`when` 让任务只在满足条件时执行，可读取变量、主机 facts 或任意 Jinja2 表达式。通过组合 `and`、`or` 以及 `in` 等操作符，可以精准控制 Play 行为。

## 语法
```yaml
- name: 条件执行示例
  ansible.builtin.service:
    name: httpd
    state: started
  when:
    - ansible_facts['os_family'] == 'RedHat'
    - enable_httpd | default(false)
```

## 参数
- `when`：接受字符串或列表，列表模式表示“全部成立”才会执行。
- 表达式可引用 `vars`、`hostvars`、`ansible_facts` 以及 `group_names` 等内置变量。

## 返回值
任务一旦被 `when` 跳过，Ansible 会显示 `skipping`，并且不会产生 `register` 结果。若后续步骤需要该结果，务必提供默认值。

## 常见陷阱
1. **缩进错误**：在列表形式中确保 `- condition` 与任务同级，否则会被解析为新的任务。
2. **变量未定义**：使用 `| default()` 处理可能缺失的变量，避免 `undefined variable`。
3. **组合逻辑混乱**：复杂表达式可以拆成多条条件，让阅读和调试更直接。

## 如何调试/常见错误
- 启用 `-vv` 观察变量求值结果；必要时使用 `debug: var=变量名` 打印。
- 若多个任务共享同一条件，可将 `when` 写在 block 或 include 上，减少重复。

示例 Playbook 请查看 [playbook.yml](playbook.yml)。