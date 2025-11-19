# 循环矩阵（Loop Matrix）

在需要对多维组合执行任务时，可使用 `product` 过滤器或 `subelements` 插件构建循环矩阵。本示例展示如何组合区域、环境、服务端口等多组变量，并通过 `loop_control.loop_var` 提升可读性。

## 适用场景
- 同时在多个区域和环境部署同一批服务
- 为每个服务配置多个监听端口或后端节点
- 进行跨组合的验证与告警（如 region × environment × feature flag）

## 技巧摘要
1. `regions | product(environments) | list`：快速生成笛卡尔积
2. `subelements`：遍历嵌套列表（如服务 → 端口）
3. `loop_control.label`：打印可读标签，便于调试
4. `when`：筛选特定组合，例如跳过生产环境中的实验功能

更多详情请参考 [playbook.yml](playbook.yml) 与变量文件。
