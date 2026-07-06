# 9. Docker开发

### 9.1 概述

Docker 应用运行在 TOS7 内置 Docker 引擎管理的容器中。通过 `docker-compose.yml` 文件定义，需要在 TNAS 设备上安装 DockerEngine 应用。

**核心要求：**
- 必须提供兼容 Compose Spec 3.8+ 的 `docker-compose.yml`
- 数据必须通过卷挂载持久化到 NAS 可访问目录
- **严格禁止使用特权模式**
- **严格禁止占用系统核心端口（22、80、443、8181、5050）**

### 9.2 目录结构

```
<appid>-docker/                # 仓库根目录
├── config.ini                 # 应用元数据
├── app.lang                   # 多语言文件（14种语言）
├── docker-compose.yml         # 【必填】容器编排配置
├── .env.example               # 【可选】环境变量示例
├── README.md                  # 双语文档
└── images/
    └── icons/
        └── <appid>.svg        # 应用图标
```

### 9.3 docker-compose.yml 规范

```yaml
version: "3.8"
services:
  <appid>:
    image: <仓库>/<镜像>:<标签>  # 镜像仅限Docker Hub
    container_name: <appid>
    restart: unless-stopped
    Volumes:
      - /Volume1/docker/<appid>/config:/config
      - /Volume1/docker/<appid>/data:/data
    ports:
      - "<宿主端口>:<容器端口>"
    environment:
      - TZ=Asia/Shanghai
    user: "1000:1000"

x-app-meta:
  web:
    port: <宿主端口>
    protocol: http
```

**规则：**

1. **版本**：必须兼容 Compose Spec 3.8 及以上
2. **x-app-meta**：对于有 UI 的 Docker 应用，必须在 `docker-compose.yml` 文件末尾（services 块之后）追加 `x-app-meta` 标签，包含 `web.port`（Web UI 端口号）和 `web.protocol`（请求协议，通常为 `http`）。
   ```yaml
   x-app-meta:
     web:
       port: 8080
       protocol: http
   ```
3. **数据持久化**：所有数据目录必须挂载到宿主路径。仅存储在容器内的数据会在容器删除时丢失。
4. **端口映射**：
   - 禁用端口：22、80、443、8181、5050（系统服务）
   - 推荐范围：8000-19999
   - 提交前确认所选端口在 TNAS 上未被占用
5. **特权模式**：**严格禁止**。必须使用 `user` 字段指定 UID/GID。
6. **时区**：默认配置 `TZ=Asia/Shanghai`。用户可自行修改。
7. **容器名称**：必须与应用 `id` 一致
8. **重启策略**：普通服务使用 `unless-stopped`
9. **网络模式**：`network_mode: host` **严格禁止**，仅系统级网络工具除外。系统级网络工具需在提交时明确说明理由，经审核同意后方可使用。普通应用一律禁止。使用宿主机网络模式破坏容器隔离，存在安全风险。改用端口映射：
   ```yaml
   ports:
     - "8080:8080"
   ```
10. **时区**：容器时区必须显式配置：
   ```yaml
   environment:
     - TZ=Asia/Shanghai
     - TZ=${TZ:-Asia/Shanghai}  # 允许用户覆盖
   ```
   请勿将时区留空 — 时间戳不一致会导致时间敏感应用数据损坏。

### 9.4 镜像与安全要求

1. **镜像来源（仅限 Docker Hub）**：**所有 Docker 镜像必须来自 Docker Hub，非 Docker Hub 镜像直接驳回。** 镜像必须托管在 **Docker Hub**（hub.docker.com）。不支持其他镜像仓库（如 ghcr.io、quay.io、自建私有仓库等）。

   | 优先级 | 来源 | 示例 |
   |---|---|---|
   | 1（首选） | Docker Hub 官方项目镜像 | `nginx`、`postgres` |
   | 2 | Docker Hub 已验证发布者 | 带 Verified badge 的 Docker Hub 镜像 |
   | 3 | Docker Hub 知名社区镜像 | `linuxserver/jellyfin`（100M+ 拉取量、活跃维护） |
   | ❌ 驳回 | 非 Docker Hub 来源的镜像 | 私有仓库、ghcr.io、quay.io 等 |
   | ❌ 驳回 | Docker Hub 上未经验证的个人镜像 | 拉取量少、无文档的 Docker Hub 镜像 |

   > **强制要求：** 镜像必须托管在 Docker Hub 上。审核时将验证镜像来源。使用非 Docker Hub 镜像将被直接驳回。

   来自非 Docker Hub 来源或未经验证的 Docker Hub 镜像将在安全审核中被驳回。
2. **镜像体积**：使用多阶段构建或 Alpine 基础镜像以减小体积。
3. **敏感信息**：禁止在镜像或 compose 文件中硬编码密码、Token 或密钥。使用环境变量或 `.env` 文件。
4. **安全扫描**：提交前运行 `docker scan` 或 `trivy` 检查已知漏洞。
5. **用户权限**：**严格禁止使用 root 用户，严格禁止使用 `--privileged` 特权模式。**必须通过 `user` 字段指定非 root 用户。

### 9.5 完整示例

**应用概览：**
- ID：`myapp-docker`
- 类型：Docker 应用
- 镜像：`linuxserver/myapp:latest`
- 端口：8080
- 依赖：DockerEngine

#### config.ini

```json
{
  "id": "myapp-docker",
  "icon": "/images/icons/myapp-docker.svg",
  "publisher": "开发者名称",
  "path": "http://${ip}:8080",
  "exec": true,
  "open_path": true,
  "resize": true,
  "maxmin": true,
  "width": 0,
  "height": 0,
  "help": "https://github.com/example/myapp/wiki",
  "version": "1.0.0",
  "recommend": false,
  "beta": false,
  "low_version": "TOS7.0",
  "category": ["Utilities"],
  "depend": ["DockerEngine"],
  "relation": ["docker", "DockerEngine"],
  "platform": "x86_64",
  "official": "https://example.com",
  "application_type": "docker",
  "system_id": "",
  "package": "",
  "compose_project": "myapp-docker",
  "user": "myapp",
  "all_user_display": true,
  "allow_open_in_mobile": false
}
```

#### docker-compose.yml

```yaml
version: "3.8"
services:
  myapp-docker:
    image: linuxserver/myapp:1.0.0
    container_name: myapp-docker
    restart: unless-stopped
    Volumes:
      - /Volume1/docker/myapp-docker/config:/config
      - /Volume1/docker/myapp-docker/data:/data
    ports:
      - "8080:8080"
    environment:
      - TZ=Asia/Shanghai
      - PUID=1000
      - PGID=1000

x-app-meta:
  web:
    port: 8080
    protocol: http
```


> **说明：** 该应用为 WebUI 外部打开，因此 `path` 使用 `http://${ip}:<端口>` 格式。

**多容器服务启动顺序：**
对于具有多个服务的应用（如 Web + 数据库）：
```yaml
services:
  app-db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
  app-web:
    image: myapp:1.0.0
    depends_on:
      app-db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```
- 使用 `depends_on` 并设置 `condition: service_healthy` 确保正确的启动顺序
- 每个服务必须定义健康检查
- 平台验证：所有服务必须健康后应用才显示为"运行中"

**健康检查失败处理：**
- 连续 3 次健康检查失败后，容器标记为"不健康"
- 应用中心将应用显示为"异常"
- Docker 的重启策略（`unless-stopped`）将尝试重启不健康的容器
- 如果容器进入重启循环，平台将标记应用需要开发者关注

**数据备份、迁移和重置：**

| 操作 | 路径 | 方法 |
|---|---|---|
| 备份配置 | `/Volume1/docker/<appid>/config` | tar 或 rsync 备份 |
| 备份数据 | `/Volume1/docker/<appid>/data` | tar 或 rsync 备份 |
| 迁移 | 全部 `/Volume1/docker/<appid>/` | 复制到新设备，相同路径 |
| 重置为默认 | 停止容器 → 删除 `/Volume1/docker/<appid>/config` → 重启 | 容器创建全新配置 |
| 完全删除数据 | 停止容器 → 删除 `/Volume1/docker/<appid>/` | 所有数据永久删除 |

> 注意：配置和数据分开存储，支持独立备份/恢复。重大升级前务必备份。

---

← [上一章：Deb开发规范](08_Deb开发规范.md) &nbsp;&nbsp;|&nbsp;&nbsp; [下一章：权限模型](10_权限模型.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 返回总目录](../README.md)
