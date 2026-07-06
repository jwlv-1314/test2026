# 5. ABI兼容性


### 5.1 ABI 稳定性规则

1. **系统库 ABI**：小版本更新不会破坏 glibc ABI。针对 glibc 2.35 编译的应用将继续正常工作。
2. **Systemd 服务约定**：`multi-user.target` 和服务管理接口将保持稳定。
3. **Docker 引擎**：Docker API 兼容性遵循 Docker 上游的稳定性保证。
4. **TOS 应用中心 API**：安装/启动/停止/卸载接口已版本化且向后兼容。

### 5.2 声明运行时依赖

应用应显式声明运行时依赖：

**在 DEBIAN/control 中（Deb 应用）：**
```
Depends: libc6 (>= 2.35), python3 (>= 3.10), systemd
```

**在 docker-compose.yml 中（Docker 应用）：**
```yaml
services:
  myapp:
    image: myapp:1.0.0  # 锁定特定版本，避免 :latest
```



### 5.3 测试建议

为确保前向兼容性：
- 提交前在最新 TOS7 版本上测试你的应用
- 在 Deb 包中使用版本锁定的依赖
- Docker 应用应锁定镜像标签为特定版本（而非 `:latest`）
- 在开发者平台订阅 TOS 发行说明

---

← [上一章：包规范](04_包规范.md) &nbsp;&nbsp;|&nbsp;&nbsp; [下一章：开发环境](06_开发环境.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 返回总目录](../README.md)
