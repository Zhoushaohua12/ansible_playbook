# 循环（loop）

Loop 用于批量执行任务，比 `with_items` 更直观，并支持 `loop_control` 自定义迭代变量，提高可读性。

## 语法
```yaml
- name: 批量创建用户
  ansible.builtin.user:
    name: "{{ user_item.name }}"
    state: present
  loop: "{{ users }}"
  loop_control:
    loop_var: user_item
```

## 参数
- `loop`：接受列表、字典（使用 `dict2items`）或查询插件返回值。
- `loop_control`：可设置 `loop_var`、`label`、`pause` 等。

## 返回值
每次迭代都会覆盖 `register` 的结果，使用 `results` 聚合字段查看所有迭代详情。

## 常见陷阱
1. **变量名冲突**：默认 `item` 容易与已有变量冲突，推荐显式指定 `loop_var`。
2. **嵌套循环**：组合 `subelements` 或 `product` 插件前，确认数据结构，避免层级混淆。
3. **错误引用**：在 Jinja 中引用循环变量时，记得使用 `{{ user_item }}` 而不是 `{{ item }}`。

## 如何调试/常见错误
- 在循环任务后追加 `debug: var=registered_var.results` 观察每次执行结果。
- 若某次迭代失败，可配合 `loop_control.label` 打印更友好的提示。

示例 Playbook 见 [playbook.yml](playbook.yml)，其中通过循环遍历主机与端口组合并在注释中解释了 `loop_var` 的作用。