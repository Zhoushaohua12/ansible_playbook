# pam_hardening PAM 安全加固模块使用指南

## 模块用途
`pam_hardening` 模块用于配置可插拔认证模块（PAM）的安全策略，通过调整 PAM 配置来增强系统认证安全性。支持密码复杂度策略、登录失败锁定、会话超时、警告横幅等安全加固措施。适用于安全基线加固、合规性配置、多用户环境安全管理等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `password_policies` | dict | 密码策略配置（复杂度、长度、历史） | 最小长度、复杂度要求、历史记录数 |
| `account_lockout` | dict | 账户锁定策略（失败次数、锁定时间） | 3次失败、15分钟锁定 |
| `session_limits` | dict | 会话限制（超时、并发连接数） | 10分钟超时、3个并发连接 |
| `login_banner` | str | 登录警告横幅内容 | 法律声明、安全提示 |
| `pam_modules` | list | PAM 模块配置列表 | pam_pwquality、pam_faillock、pam_limits |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `pam_configs_updated` | 是否更新了 PAM 配置 | true/false |
| `password_policy_applied` | 密码策略应用状态 | applied/failed |
| `account_lockout_configured` | 账户锁定配置状态 | configured/not_configured |
| `session_limits_set` | 会话限制设置状态 | set/not_set |
| `login_banner_deployed` | 登录横幅部署状态 | deployed/not_deployed |
| `changed` | 是否修改了 PAM 配置 | true/false |

## 使用情境

### 生产环境安全加固
**场景**：在生产服务器上配置严格的密码策略和账户锁定机制
- 设置密码最小长度和复杂度要求
- 配置登录失败自动锁定机制
- 部署法律合规的登录警告横幅
- 实施会话超时和并发连接限制

### 合规性配置
**场景**：满足 CIS Benchmarks、NIST 800-53、PCI DSS 等合规标准
- 配置符合合规要求的密码策略
- 实施账户生命周期管理
- 配置详细的登录审计日志
- 部署法律免责声明

### 多用户环境管理
**场景**：在多用户服务器环境中实施统一的安全策略
- 统一所有用户的密码复杂度要求
- 配置用户组权限限制
- 实施资源使用限制
- 配置用户登录时间窗口

### 高安全环境
**场景**：在需要高安全级别的环境中配置严格的认证策略
- 配置多因素认证集成
- 实施严格的密码历史记录
- 配置登录地理位置限制
- 实施实时异常登录检测

## 安全注意事项

1. **密码策略平衡**：
   - 过于严格的密码策略可能导致用户选择可预测的密码
   - 平衡安全性和可用性，避免用户绕过安全措施
   - 定期评估和调整密码策略的有效性

2. **账户锁定风险**：
   - 账户锁定可能被用于拒绝服务攻击
   - 配置合理的锁定阈值和解锁机制
   - 为管理员账户设置特殊的锁定策略

3. **PAM 配置风险**：
   - 错误的 PAM 配置可能导致无法登录系统
   - 在生产环境部署前必须充分测试
   - 保留配置备份和恢复机制

4. **合规性要求**：
   - 根据具体合规标准配置相应的安全策略
   - 确保所有安全措施都有文档记录
   - 定期审查和更新安全配置

## 环境依赖

### 必需
- 目标主机支持 PAM（Linux、Unix 系统）
- PAM 相关软件包（pam、pam-modules）
- 需要管理员权限修改 PAM 配置
- PAM 认证框架已正确安装

### 推荐
- libpwquality（密码质量检查）
- pam_faillock（账户锁定）
- pam_limits（资源限制）
- pam_unix（传统 Unix 认证）
- cracklib（密码强度检查）

### 系统支持
- RHEL/CentOS 6/7/8/9：全面支持
- Ubuntu 16.04+：支持
- Debian 8+：支持
- SUSE Linux Enterprise：支持
- 其他 Linux 发行版：基本支持

## 常见问题

### 1. PAM 配置错误导致无法登录
检查 PAM 配置文件语法：
```bash
# 验证 PAM 配置
pam-config --test

# 检查特定服务的 PAM 配置
pam-config --service sshd --test
```

### 2. 密码复杂度策略不生效
确认相关 PAM 模块已安装：
```bash
# 检查 pam_pwquality 模块
rpm -qa | grep pam_pwquality

# 验证密码质量配置
pam-config --service passwd --test
```

### 3. 账户锁定机制异常
检查 faillock 配置和状态：
```bash
# 查看失败登录记录
faillock --user username

# 清除用户锁定记录
faillock --user username --reset
```

### 4. 登录横幅不显示
检查显示管理器配置：
```bash
# 检查 SSH 配置
grep Banner /etc/ssh/sshd_config

# 检查本地登录配置
cat /etc/issue
```

## 最佳实践

### 分阶段安全加固
```yaml
- name: 分阶段 PAM 安全加固
  block:
    - name: 第一阶段：基础密码策略
      community.general.pamd:
        name: system-auth
        type: password
        control: requisite
        module_path: pam_pwquality.so
        module_arguments: "try_first_pass local_users_only retry=3 authtok_type="
      become: yes
    
    - name: 第二阶段：账户锁定机制
      community.general.pamd:
        name: system-auth
        type: auth
        control: required
        module_path: pam_faillock.so
        module_arguments: "preauth silent deny=3 unlock_time=900"
      become: yes
```

### 合规性配置示例
```yaml
- name: CIS Benchmarks 合规配置
  block:
    - name: 配置密码最小长度
      ansible.builtin.lineinfile:
        path: /etc/security/pwquality.conf
        regexp: '^minlen'
        line: 'minlen = 14'
      become: yes
    
    - name: 配置密码复杂度
      ansible.builtin.lineinfile:
        path: /etc/security/pwquality.conf
        regexp: '^dcredit'
        line: 'dcredit = -1'
      become: yes
```

### 用户资源限制
```yaml
- name: 配置用户资源限制
  community.general.pam_limits:
    domain: "*"
    limit_type: soft
    limit_item: nproc
    value: 1024
  become: yes
```

## 相关示例
- [user 模块](../user/README.md) - 用户账号管理
- [selinux 模块](../selinux/README.md) - SELinux 安全策略
- [authorized_key 模块](../authorized_key/README.md) - SSH 密钥管理
- [service 模块](../service/README.md) - 系统服务管理