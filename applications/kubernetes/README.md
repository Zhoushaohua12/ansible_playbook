# kubernetes 模块使用指南

## 模块简介
`kubernetes.core.k8s` 模块用于管理 Kubernetes 资源的创建、更新、删除和查询等操作。该模块提供了完整的 Kubernetes 资源管理功能，支持 Deployment、Service、ConfigMap、Secret、Ingress 等所有 Kubernetes 资源类型，是容器编排和应用部署的核心工具。

## 主要参数

### 基础配置
- `state`：资源状态，可选值：
  - `present`：确保资源存在（默认）
  - `absent`：删除资源
  - `patched`：部分更新资源
  - `restarted`：重启资源（适用于 Deployment、StatefulSet 等）

### 资源定义
- `definition`：YAML/JSON 格式的资源定义
- `src`：资源定义文件路径
- `template`：Jinja2 模板文件路径
- `kubeconfig`：kubeconfig 文件路径
- `context`：Kubernetes 上下文名称

### 应用控制
- `apply`：是否使用 kubectl apply 方式（默认：false）
- `force`：是否强制删除资源
- `wait`：是否等待资源就绪
- `wait_timeout`：等待超时时间（默认：120）
- `wait_condition`：等待条件配置

### 高级选项
- `namespace`：目标命名空间
- `validate`：是否验证资源定义（默认：true）
- `merge_type`：合并策略（strategic/merge/json）
- `continue_on_error`：是否在错误时继续执行

## 返回值
- `result`：操作结果详细信息
- `changed`：是否执行了变更操作
- `method`：使用的操作方法（create/patch/delete）
- `duration`：操作耗时
- `warnings`：警告信息列表

## 常见使用场景

### 1. 部署应用 Deployment
```yaml
- name: 部署 Web 应用 Deployment
  kubernetes.core.k8s:
    state: present
    definition:
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: webapp
        namespace: "{{ app_namespace }}"
        labels:
          app: webapp
      spec:
        replicas: 3
        selector:
          matchLabels:
            app: webapp
        template:
          metadata:
            labels:
              app: webapp
          spec:
            containers:
            - name: webapp
              image: "{{ app_image }}:{{ app_version }}"
              ports:
              - containerPort: 8080
```

### 2. 创建 Service
```yaml
- name: 创建应用 Service
  kubernetes.core.k8s:
    state: present
    definition:
      apiVersion: v1
      kind: Service
      metadata:
        name: webapp-service
        namespace: "{{ app_namespace }}"
      spec:
        selector:
          app: webapp
        ports:
        - protocol: TCP
          port: 80
          targetPort: 8080
        type: ClusterIP
```

### 3. 从文件部署资源
```yaml
- name: 从 YAML 文件部署应用
  kubernetes.core.k8s:
    state: present
    src: "{{ k8s_manifests_path }}/deployment.yaml"
    namespace: "{{ app_namespace }}"
    wait: true
    wait_timeout: 300
```

### 4. 使用模板部署
```yaml
- name: 使用 Jinja2 模板部署 ConfigMap
  kubernetes.core.k8s:
    state: present
    template: templates/configmap.j2
    namespace: "{{ app_namespace }}"
    vars:
      app_config: "{{ application_config }}"
```

### 5. 批量部署多个资源
```yaml
- name: 部署所有应用资源
  kubernetes.core.k8s:
    state: present
    src: "{{ item }}"
    namespace: "{{ app_namespace }}"
    wait: true
  loop: "{{ k8s_manifest_files }}"
  loop_control:
    label: "{{ item | basename }}"
```

### 6. 更新资源配置
```yaml
- name: 更新 Deployment 副本数
  kubernetes.core.k8s:
    state: patched
    definition:
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: webapp
        namespace: "{{ app_namespace }}"
      spec:
        replicas: "{{ new_replica_count }}"
```

### 7. 创建 Ingress
```yaml
- name: 创建应用 Ingress
  kubernetes.core.k8s:
    state: present
    definition:
      apiVersion: networking.k8s.io/v1
      kind: Ingress
      metadata:
        name: webapp-ingress
        namespace: "{{ app_namespace }}"
        annotations:
          nginx.ingress.kubernetes.io/rewrite-target: /
      spec:
        rules:
        - host: "{{ app_domain }}"
          http:
            paths:
            - path: /
              pathType: Prefix
              backend:
                service:
                  name: webapp-service
                  port:
                    number: 80
```

### 8. 管理密钥
```yaml
- name: 创建应用 Secret
  kubernetes.core.k8s:
    state: present
    definition:
      apiVersion: v1
      kind: Secret
      metadata:
        name: webapp-secrets
        namespace: "{{ app_namespace }}"
      type: Opaque
      data:
        database_url: "{{ database_url | b64encode }}"
        api_key: "{{ api_key | b64encode }}"
```

## 安全注意事项

### 集群安全
- 使用 RBAC 控制访问权限
- 定期轮换 Service Account Token
- 启用网络策略隔离应用
- 使用 Pod Security Policies

### 密钥管理
- 使用 Kubernetes Secret 存储敏感信息
- 启用 Secret 加密（Encryption at Rest）
- 避免在资源定义中硬编码密钥
- 定期更新和轮换密钥

### 网络安全
- 配置 NetworkPolicy 限制网络访问
- 使用 Ingress TLS 终止
- 启用 mTLS 服务间通信
- 限制 Pod 访问 API Server

## 最佳实践

### 资源管理
- 使用命名空间隔离不同环境
- 设置资源限制和请求
- 配置健康检查和就绪检查
- 使用标签和注解管理资源

### 部署策略
- 使用滚动更新减少服务中断
- 实施蓝绿部署或金丝雀发布
- 配置自动扩缩容策略
- 设置 Pod 中断预算

### 监控和日志
- 集成 Prometheus 监控
- 配置日志聚合和分析
- 设置告警规则和通知
- 定期备份集群配置

## 测试步骤
1. 确保 kubectl 已配置并可访问集群
2. 在 `vars/example_vars.yml` 中配置 K8s 参数
3. 准备应用资源定义文件
4. 使用 `--check` 模式预览资源变更
5. 验证资源部署和运行状态

## 常见问题
- **资源创建失败**：检查 YAML 语法和集群权限
- **镜像拉取失败**：检查 ImagePullSecrets 和镜像仓库访问
- **服务无法访问**：检查 Service 配置和网络策略
- **Pod 启动失败**：检查资源定义和事件日志

## 相关模块
- [k8s_info](https://docs.ansible.com/ansible/latest/collections/kubernetes/core/k8s_info_module.html) - Kubernetes 资源信息查询
- [k8s_scale](https://docs.ansible.com/ansible/latest/collections/kubernetes/core/k8s_scale_module.html) - Kubernetes 资源扩缩容
- [helm](https://docs.ansible.com/ansible/latest/collections/community/general/helm_module.html) - Helm Chart 管理