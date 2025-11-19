# Handler 与 Notify

Handler 是在任务检测到变更时才执行的收尾动作，例如重启服务或刷新缓存。通过 `notify` 将多个 handler 组合，可以构建清晰的回调链。

## 语法
```yaml
- name: 更新配置
  ansible.builtin.template:
    src: app.conf.j2
    dest: /etc/app/app.conf
  notify:
    - 重启应用

handlers:
  - name: 重启应用
    ansible.builtin.service:
      name: app
      state: restarted
```

## 参数
- `notify`：支持字符串或列表，列出需要触发的 handler 名称。
- Handler 任务与普通任务写法相同，可使用 `listen` 聚合多个名称。

## 返回值
Handler 只有在被通知且第一次执行时才会运行，`changed` 标志表示 handler 自身是否修改了系统状态。

## 常见陷阱
1. **没有变更就不会触发**：如需强制执行，可在任务中设置 `changed_when: true` 或使用 `meta: flush_handlers`。
2. **命名重复**：handler 名称是唯一标识，保持清晰命名以免被错误复用。
3. **通知链过长**：注意区分真正需要串联的动作，可在 handler 里调用 include_tasks 拆分逻辑。

## 如何调试/常见错误
- 查看 Play 末尾输出确认 handler 是否被触发；必要时添加 `debug` handler 记录上下文。
- 如果多个任务通知同一 handler，Ansible 只执行一次，可通过日志确认是否满足需求。

详见 [playbook.yml](playbook.yml)，示例展示了配置变更后依次触发重启与审计 handler 的链路。