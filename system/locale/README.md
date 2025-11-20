# locale 模块使用指南

## 模块用途
`community.general.locale_gen` 模块用于生成和管理系统支持的区域设置（Locale），支持设置字符编码、时间格式、货币符号等。在多语言环境、国际化应用部署、系统本地化配置中提供支持。确保应用程序能够正确处理不同语言的输入、输出和显示。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `name` | str | Locale 名称（必需），格式为 `language_COUNTRY.encoding` | zh_CN.UTF-8、en_US.UTF-8、ja_JP.UTF-8 等 |
| `state` | str | Locale 状态（present 生成，absent 移除） | present、absent |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `name` | Locale 名称 | zh_CN.UTF-8 |
| `state` | Locale 当前状态 | present、absent |
| `changed` | 是否修改了系统 Locale | true/false |
| `rc` | 命令返回码 | 0（成功）、非 0（失败） |

## 使用情境

### 中文应用部署
**场景**：在服务器上安装中文语言支持，确保中文显示、输入正常
- 应用程序输出中文文本
- 文件系统支持中文文件名
- 数据库中存储中文字符
- 日志输出中文错误信息

### 多语言 Web 应用
**场景**：支持多种语言环境，适配不同地区用户
- 英文界面：en_US.UTF-8
- 中文界面：zh_CN.UTF-8
- 日本语界面：ja_JP.UTF-8
- 欧洲用户：de_DE.UTF-8、fr_FR.UTF-8 等

### 容器与虚拟机初始化
**场景**：容器镜像或虚拟机模板的初始化配置
- Docker 容器中添加特定语言支持
- Kubernetes Pod 中正确显示本地化文本
- 虚拟机克隆后的快速本地化配置

### 开发与测试环境
**场景**：为开发团队配置本地化环境
- 国际化应用的多语言测试
- 本地化文本处理的验证
- 字符编码兼容性测试

## 安全注意事项

1. **字符编码一致性**：
   - 推荐使用 UTF-8 编码以支持全球语言
   - 避免混用 UTF-8 和 GB2312 等遗留编码
   - 确保数据库、应用程序与系统 Locale 编码一致
2. **Locale 生成性能**：
   - 生成大量 Locale 会占用磁盘空间和启动时间
   - 仅生成必需的 Locale，避免过度配置
3. **应用兼容性**：
   - 某些遗留应用可能只支持特定 Locale
   - 修改系统 Locale 前验证应用兼容性
4. **GLIBC Locale 缓存**：
   - 大规模 Locale 生成后可能需要清空缓存
   - 在 Docker 等最小化环境中，仅预装必需 Locale

## 环境依赖

### 必需
- glibc-langpack 包（RHEL/CentOS）或 language-pack-* 包（Ubuntu/Debian）
- locale 命令行工具
- 需要 root 或 sudo 权限生成 Locale

### 推荐
- locales 包（Debian/Ubuntu）
- glibc-i18n 包（提供国际化支持）

### 系统支持
- CentOS/RHEL 7/8/9：glibc-langpack、glibc-common
- Ubuntu/Debian：locales、language-pack-zh-hans 等
- Alpine Linux：musl-locales（部分支持）

## 常见问题

### 1. 运行 locale 命令时显示 "locale: Cannot set LC_COLLATE to default locale"
Locale 数据库可能损坏，需要重新生成：
```yaml
- name: 重新生成 Locale 数据库
  ansible.builtin.shell: |
    locale-gen zh_CN.UTF-8 2>&1 || localedef -i zh_CN -f UTF-8 zh_CN.UTF-8
  become: yes
```

### 2. 中文文件名显示为乱码
检查系统 Locale 设置是否正确：
```yaml
- name: 验证系统 Locale
  ansible.builtin.shell: |
    locale
  register: current_locale
```

### 3. Docker 容器中 Locale 生成失败
最小化容器镜像可能缺少必要的 Locale 文件，可以手动添加或使用多阶段构建：
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y locales
RUN locale-gen zh_CN.UTF-8
```

### 4. Locale 切换后应用仍使用旧 Locale
某些应用缓存了 Locale 信息，需要重启应用或清空环境变量：
```yaml
- name: 重启应用以应用新 Locale
  ansible.builtin.systemd:
    name: myapp
    state: restarted
  become: yes
  environment:
    LC_ALL: zh_CN.UTF-8
```

## 最佳实践

### 生产环境 Locale 配置
```yaml
- name: 配置生产环境 Locale
  community.general.locale_gen:
    name: "{{ item }}"
    state: present
  with_items:
    - en_US.UTF-8
    - zh_CN.UTF-8
  become: yes
  check_mode: true  # 先预览
```

### 仅安装必需的 Locale
```yaml
- name: 安装特定区域的 Locale
  community.general.locale_gen:
    name: "{{ system_locale }}"
    state: present
  become: yes
  vars:
    system_locale: "{{ locale_by_region[deployment_region] }}"
```

### 与系统初始化协同
```yaml
- name: 新主机初始化 - 生成 Locale
  block:
    - name: 更新包管理器
      ansible.builtin.package:
        name: locales
        state: present
      become: yes
    
    - name: 生成必需 Locale
      community.general.locale_gen:
        name: "{{ item }}"
        state: present
      with_items: "{{ required_locales }}"
      become: yes
      check_mode: true
    
    - name: 设置系统默认 Locale（仅演示）
      ansible.builtin.debug:
        msg: "系统 Locale 已生成，可通过 /etc/locale.conf 或 /etc/default/locale 设置默认值"
```

## 相关示例
- [timezone 模块](../timezone/README.md) - 时区配置
- [hostname 模块](../hostname/README.md) - 主机名配置
- [service 模块](../service/README.md) - 系统服务管理
