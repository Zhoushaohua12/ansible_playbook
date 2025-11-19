# 变量与 set_fact

`set_fact` 可在运行时创建或更新变量，常用于整理前一个任务的输出、生成派生值或跨任务复用的结构化数据。

## 语法
```yaml
- name: 计算派生变量
  ansible.builtin.set_fact:
    release_path: "/srv/app/releases/{{ build_id }}"
```

## 参数
- `set_fact`: 接受键值对，新变量可在后续任务中直接引用。
- `cacheable`: 可选布尔值，设为 true 时允许事实缓存插件保存结果。

## 返回值
该模块返回 `ansible_facts` 字段，包含你设置的所有变量。配合 `register` 时可查看 `ansible_facts` 与 `changed` 等元数据。

## 常见陷阱
1. **变量覆盖**：若名称与现有变量相同，会被立即覆盖；必要时添加前缀。
2. **循环中的累积**：需要基于 `ansible_facts` 旧值更新时，记得使用 `set_fact: var: "{{ var + [new_item] }}"`。
3. **缓存冲突**：启用 `cacheable` 后需确保 facts 缓存策略正确清理，否则旧值可能影响下次运行。

## 如何调试/常见错误
- 使用 `debug: var=ansible_facts.key` 验证新变量是否存在。
- 如果变量依赖前一个任务的 register 结果，在 set_fact 前先判断 `is defined`，避免 `undefined` 异常。

示例详见 [playbook.yml](playbook.yml)。