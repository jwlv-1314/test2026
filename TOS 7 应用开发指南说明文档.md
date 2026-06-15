# TOS 7 应用开发与上架指南

**最后更新：** 2026-05-27  
**适用平台：** TOS 7.0 及以上版本  
**当前文档版本：** TOS7.0 Beta 版，后续 TOS7.x 版本兼容性将保持一致  
**面向对象：** 全球第三方开发者、独立开发者、企业合作伙伴  

---

## 目录
1. [文档概述](#1-文档概述)
2. [应用架构策略](#2-应用架构策略)
3. [快速开始](#3-快速开始)
4. [包规范](#4-包规范)
5. [ABI/API 兼容性与稳定性策略](#5-abiapi-兼容性与稳定性策略)
6. [开发环境](#6-开发环境)
7. [应用类型](#7-应用类型)
8. [Deb 应用开发与配置规范](#8-deb-应用开发与配置规范)
9. [Docker 应用开发](#9-docker-应用开发)
10. [权限模型](#10-权限模型)
11. [包签名与安全](#11-包签名与安全)
12. [最佳实践](#12-最佳实践)
13. [本地测试与调试](#13-本地测试与调试)
14. [CI/CD 指南](#14-cicd-指南)
15. [上架流程](#15-上架流程)
16. [审核标准](#16-审核标准)
17. [上架后运维与下架](#17-上架后运维与下架)
18. [开发者捐赠与商业化支持](#18-开发者捐赠与商业化支持)
19. [常见问题 FAQ](#19-常见问题-faq)
20. [附录](#20-附录)

## 1. 文档概述

TOS7 基于 Ubuntu 22.04 构建，采用标准 Linux 运行环境。从 TOS7 开始，平台对新提交的应用支持以下两种类型：

- **Deb 应用**：直接运行在宿主机的原生应用，以标准 Debian 包格式封装
- **Docker 应用**：通过 Docker Compose 部署的容器化应用

> **说明：** 历史版本 `.tpk` 格式已对新应用开放提交通道关闭。已上架的 tpk 格式应用将继续维护，但所有新上架应用必须遵循本文档定义的 Deb 或 Docker 规范。


所有提交至 TNAS 应用中心的应用，必须严格遵循本指南，以通过平台自动校验与人工审核。


---
## 2. 应用架构策略

### 2.1 官方架构推荐

TOS7 采用 **容器优先（Container-first）** 策略，同时保持对原生 Deb 应用的完整支持。平台推荐以下决策框架：

```
                    ┌─────────────────────┐
                    │ 你的应用是否需要     │
                    │ 独立的运行环境？     │
                    └──────┬──────────────┘
                           │
                    ┌──────▼──────┐        ┌──────────────┐
                    │     是      │        │     否       │
                    │             │        │              │
                    ▼             │        ▼              │
              ┌──────────┐       │  ┌──────────────┐    │
              │ Docker   │       │  │ 是否为TOS标准服务 │    │
              │ 应用     │       │  │ 或轻量工具？  │    │
              └──────────┘       │  └──────┬───────┘    │
                                 │    ┌────▼────┐       │
                                 │    │ 是      │ 否    │
                                 │    ▼         ▼       │
                                 │  Deb应用  Deb应用    │
                                 │  (tos标准)   (原生)     │
                                 └──────────────────────┘
```


### 2.2 容器优先方向

TOS7 应用生态正在向 **容器优先** 模型演进：

- **Docker 应用** 是大多数第三方服务的首选路径
- 提供更好的隔离性、更简单的依赖管理、跨平台一致性
- TOS7 存在Docker 引擎（DockerEngine应用，需要安装）提供完整的 Docker Compose 支持
- 未来平台功能（沙箱、资源限制、自动更新）将优先支持 Docker 应用

**特殊应用类型选择规则：**

- **无 UI 后台服务：** 轻量级守护进程使用 **Deb（无 UI）** 子类型；具有复杂运行时依赖或需要容器隔离的服务使用 **Docker**

**对于 Deb 应用**，TOS7 提供完整支持，但开发者应：
- 尽量减少系统级依赖
- 使用 systemd 管理生命周期
- 遵循最小权限原则
- 为未来容器化部署做好准备

**建议使用 Docker 的场景：** 以下场景必须使用 Docker，禁止使用 Deb：

- 需要特定操作系统环境或与宿主机冲突的库版本
- 需要网络隔离（独立命名空间）的应用
- 多容器架构应用（如 Web 服务 + 数据库）

> **Deb 应用路线图：** Deb 应用在 TOS7.x 中保持完整支持。平台可能在未来的 TOS 主版本中逐步引入向容器优先架构的过渡路径。开发者将在任何格式弃用前收到至少 12 个月的提前通知。

---


---

### 2.3 TOS 系统预装依赖说明

TOS 7.0 基于 Ubuntu 22.04 构建，系统默认预装以下核心依赖：

- bash / dash
- Python 3.10
- systemd
- nginx
- curl / wget
- Docker 运行时（Docker 应用专用）

> **重要提示：** Node.js、Java、Go 等语言运行时，**TOS 系统默认不预装**，请勿在 Deb 应用中直接依赖这些环境。

### 2.4 非预装依赖处理规范

若你的应用依赖 TOS 未预装的环境（如 Node.js），必须采用以下合规方案，**禁止直接声明依赖或运行时下载**。

#### 禁止方案

- 在 `DEBIAN/control` 中声明 `Depends: nodejs`（系统无预装，会导致安装失败）
- 在脚本中通过 `apt install nodejs` 安装依赖（会触发权限问题，且破坏系统环境）
- 使用 Node.js 编写的脚本作为应用入口（会报 `node: command not found`）

#### 推荐替代方案（按优先级排序）

##### 方案 1：使用 Go 编译静态二进制（推荐）

将核心逻辑用 Go 重写，编译为静态链接的独立二进制文件，无任何系统依赖：

```bash
# 编译 x86_64 架构静态二进制
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o appname-x86_64 main.go

# 编译 aarch64 架构静态二进制
GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build -o appname-aarch64 main.go
```

- 将编译好的二进制放入 Deb 包的 `/usr/local/<appid>/` 目录
- 通过 systemd 服务文件直接启动，无需额外依赖

##### 方案 2：使用 Python 实现（利用系统预装依赖）

将核心逻辑改用 Python 实现，TOS 已预装 Python 3.10，可直接使用：

- 在 `DEBIAN/control` 中声明依赖：`Depends: python3`
- 如需第三方库，需将依赖包随 Deb 包一起打包，或使用 `pip install --target` 安装到应用私有目录

##### 方案 3：打包静态依赖（仅特殊场景）

若必须使用 Node.js 等非预装环境，可将对应架构的静态二进制随 Deb 包一起打包：

- 将 Node.js 静态二进制放入 `/usr/local/<appid>/node/` 目录
- 脚本中使用绝对路径调用：`/usr/local/<appid>/node/bin/node /usr/local/<appid>/app.js`
- 注意：此方案会显著增大包体积，仅推荐轻量应用使用

## 3. 快速开始

本章节帮助开发者在 5 分钟内完成第一个 TOS7 应用的开发与上架。

### 3.1 前置准备

- 一台运行 TOS 7.0（当前稳定版/测试版）的 TNAS 设备

  > 💡 **无 TNAS 硬件设备？** 可使用 Ubuntu 22.04 虚拟机、Open TOS 本地部署或申请远程体验机替代，详见 [6.2 开发工具](#62-开发工具) 中的「开发者无 TNAS 硬件时的替代测试方案」。

- 基础的 Linux 命令行操作能力
- GitHub 账号（用于代码托管与开发者平台关联）

### 3.2 五步上架流程

**第 1 步：注册开发者账号**

访问 <a href="https://developer.terra-master.com" target="_blank" rel="noopener noreferrer">TNAS 开发者平台</a>（即将上线），注册并完成开发者认证。

**第 2 步：选择应用类型**

| 你的应用特征 | 推荐类型 |
|---|---|
| 原生二进制、Python/Node.js 脚本、轻量级服务 | Deb 应用 |
| 需要独立运行环境、复杂依赖、多容器架构 | Docker 应用 |

**第 3 步：选择项目模板**

根据你的应用类型，使用对应的 GitHub 模板仓库：

| 模板仓库 | 适用场景 | 技术要点 |
|---|---|---|
| [Deb 应用模板（单包）](https://github.com/terra-master/app-template-deb) | WebUI 在 TOS 桌面内打开（iframe） | Unix Socket + 平台代理 + Cookie 鉴权 |
| [Deb 应用模板（双包）](https://github.com/terra-master/app-template-deb-dual) | WebUI 在新标签页打开 | HTTP 端口 + Nginx 反向代理 + 双包机制 |
| [Docker 应用模板](https://github.com/terra-master/app-template-docker) | Docker 容器化部署 | docker-compose.yml + 持久化卷 + 非特权模式 |

> 每个模板仓库均包含：完整目录结构、config.ini、多语言文件、systemd 服务、
> 前后端示例代码、生命周期脚本、构建脚本（build.sh）、GitHub Actions CI/CD 配置。
> 点击仓库页面的 **"Use this template"** 按钮即可创建你的项目。

**第 4 步：本地开发与测试**

```bash
# Deb 应用：构建并测试安装
dpkg-deb --build ./<应用根目录> ./<appid>_<version>_amd64.deb
sudo dpkg -i <appid>_<version>_amd64.deb
sudo systemctl status <system_id>

# Docker 应用：启动测试
docker-compose up -d
curl http://localhost:<端口>/health
```

**第 5 步：提交审核**

1. 将代码推送至 GitHub 公开仓库
2. 在开发者平台创建应用，关联仓库
3. 上传应用包（.deb 或 .tar.gz），填写版本信息
4. 提交审核，等待平台自动校验与人工审核
5. 审核通过后，应用将发布至 TNAS 应用中心

### 3.3 关键检查清单

提交前请确认以下事项：

- [ ] config.ini 是合法 JSON 格式（无注释、无尾随逗号、双引号）
- [ ] app.lang 包含全部 14 种语言（未翻译语种用英语填充）
- [ ] 图标为 SVG 格式，存放于 `/images/icons/<appid>.svg`
- [ ] systemd 服务文件 `User` 非 root
- [ ] 版本号严格递增，config.ini、DEBIAN/control、app.lang 中一致
- [ ] 在真实 TNAS 设备上完成安装/启动/停止/卸载全流程测试

  > 💡 **无 TNAS 硬件设备？** 可使用替代方案完成测试（Ubuntu 22.04 虚拟机、Open TOS、远程体验机），详见 [6.2 开发工具](#62-开发工具) 中的「开发者无 TNAS 硬件时的替代测试方案」。

---

### 3.4 常见踩坑避坑清单

在正式开发前，请特别注意以下两个最常见的跨平台问题，避免提交后被驳回：

#### Top 1：换行符问题（CRLF to LF）

- **现象：** 在 Windows 上编辑的脚本上传到 TOS 后，报 `bad interpreter: No such file or directory`
- **根因：** Windows 默认使用 CRLF 换行，Linux 只认 LF
- **解决：** 提交前确保所有脚本/配置文件使用 LF 换行（详见第 4 章跨平台换行符规范）

```bash
# 快速检查项目中的 CRLF 文件
grep -rl $'
' *.sh *.py *.ini *.lang *.service *.conf 2>/dev/null
# 一键转换（Linux/macOS）
sed -i 's/
$//' *.sh *.py *.ini *.lang *.service *.conf
```

#### Top 2：Node.js 依赖缺失

- **现象：** 应用启动时报 `node: command not found`
- **根因：** TOS 系统不预装 Node.js，不能在 Deb 应用中直接依赖 node 环境
- **解决：** 改用 Go 编译静态二进制，或使用 Python 3.10（系统已预装）（详见第 2 章非预装依赖处理规范）

---

## 4. 包规范

本节定义 TOS7 应用包的正式规范。所有应用必须符合本规范。


### 4.1 应用生命周期

TOS7 应用遵循明确定义的生命周期：

```
  安装 ──► 配置 ──► 启动 ──► 运行中
     │        │         │         │
     │        │         │         ├── 停止 ──► 已停止 ──► 启动（重启）
     │        │         │
     │        │         └── 崩溃 ──► 自动重启（如已配置）
     │        │
     │        └── 升级 ──► 停止 ──► 安装新版 ──► 迁移 ──► 启动
     │
     └── 卸载 ──► 停止 ──► 清理 ──► 移除
```

**Deb 应用的生命周期阶段：**

| 阶段 | 触发条件 | 脚本/操作 | 预期行为 |
|---|---|---|---|
| 安装前 | `dpkg -i` | `DEBIAN/preinst` | 创建用户、检查前置条件、创建目录 |
| 安装 | `dpkg -i` | 包解压 | 文件部署到 `/usr/local/<appid>/` 等 |
| 安装后 | `dpkg -i` | `DEBIAN/postinst` | 设置权限、启用服务、启动服务 |
| 启动 | `systemctl start` | systemd / init.d | 应用进程启动 |
| 停止 | `systemctl stop` | systemd / init.d | 应用进程优雅停止 |
| 卸载前 | `dpkg --remove` | `DEBIAN/prerm` | 停止服务 |
| 卸载后 | `dpkg --remove` | `DEBIAN/postrm` | 清理用户、数据、残留文件 |
| 升级 | `dpkg -i`（新版本） | prerm → 升级 → postinst | 停止旧版、安装新版、迁移数据、启动 |

**Docker 应用的生命周期阶段：**

| 阶段 | 触发条件 | 操作 | 预期行为 | 补充说明 |
|---|---|---|---|---|
| 安装 | 应用中心（用户点击「安装」按钮） | 拉取镜像、创建卷 | 镜像可用、数据目录已创建 | 平台自动执行安装流程，开发者无需额外干预 |
| 启动 | 应用中心（用户点击「启动」按钮）/ `docker-compose up` | 启动容器 | 服务可访问 | 支持用户手动在命令行启动，与平台操作逻辑一致 |
| 停止 | 应用中心（用户点击「停止」按钮）/ `docker-compose down` | 停止容器 | 服务已停止，数据保留 | 仅停止容器进程，不会删除挂载的数据卷 |
| 升级 | 应用中心（用户点击「更新」按钮，存在新版本） | 拉取新镜像、重建容器 | 零停机或短暂停机 | 建议应用支持平滑升级，避免数据中断 |
| 卸载 | 应用中心（用户点击「卸载」按钮） | 移除容器、可选清理卷 | 所有资源释放 | 用户可选择是否保留数据卷，避免误删数据 |

> 说明："应用中心"指TNAS系统内置的应用管理界面，用户通过该界面执行的安装/启动/停止/升级/卸载操作，均会触发对应生命周期流程。


### 4.2 版本号规范

TOS7 遵循 **语义化版本号（SemVer）**：

```
主版本号.次版本号.修订号

主版本号：不兼容的 API 变更
次版本号：向后兼容的新功能
修订号：向后兼容的问题修复
```

**规则：**
1. 每次提交的版本号必须**严格大于**前一版本
2. 禁止版本降级
3. 版本号必须在 config.ini 的 `version`、DEBIAN/control 的 `Version`、app.lang 的 `version` 之间保持一致
4. 平台在提交时会校验版本一致性
5. 版本号最大长度：**20 个字符**。超出将被驳回。
6. 版本号允许字符：仅限数字（`0-9`）、点（`.`）和连字符（`-`）。示例：`"1.2.3-beta1"` → `"1.2.3"`（SemVer 预发布标签不支持；使用 `beta` 字段替代）。
7. 预发布/测试版必须使用 config.ini 中的 `"beta": true` 字段，而非版本号后缀。

**Beta 版本管理说明：**
- 平台不支持版本号后缀（如 `-beta`、`-rc`、`-alpha`）
- 多个测试版通过递增修订号区分：
  - 第一个测试版 → `"version": "1.0.0"` + `"beta": true`
  - 第二个测试版 → `"version": "1.0.1"` + `"beta": true`
- 正式版发布：设置 `"beta": false`，版本号按正常规则递增
- 版本回滚：平台不支持版本号"变小"的回滚。如需回滚，需在开发者平台提交回滚申请，由平台操作将应用回滚至上一个稳定版本
- 详见附录 N Beta 版应用管理

### 4.3 升级

**Deb 应用升级：**
- 升级时 `preinst` 收到 `$1 = "upgrade"` 参数
- `postinst` 收到 `$1 = "configure"` 参数，`$2` 为旧版本号
- 使用 `$2` 检测旧版本并执行数据迁移
- 升级过程中绝不删除用户数据，仅修改配置格式或迁移数据结构
- 用户将数据存储在 `/usr/local/<app_id>` 目录内，该目录为应用专属数据目录，平台在升级/重装应用时不会删除或覆盖此目录下的用户数据
- 建议不要将数据存储在 `/etc`、`/var`、`/usr/bin` 等系统公共目录，此类目录可能因系统更新或应用升级被覆盖，导致数据丢失

```bash
# 示例：postinst 中包含迁移逻辑
case "$1" in
    configure)
        if [ -n "$2" ]; then
            # 从版本 $2 升级
            if dpkg --compare-versions "$2" lt "2.0.0"; then
                # 将 v1.x 配置格式迁移到 v2.x
                /usr/local/<appid>/bin/migrate.sh "$2"
            fi
        else
            # 全新安装
            echo "全新安装"
        fi
        ;;
esac
```


**Docker 应用升级：**
- 拉取新的镜像标签
- 使用现有卷挂载重建容器
- 通过持久化卷在升级间保留数据
- 如有需要，在应用入口脚本中包含迁移逻辑

### 4.4 兼容性矩阵

| TOS 版本 | 基础系统 | glibc | Python3 | Docker | Node.js |
|---|---|---|---|---|---|
| TOS 7.0 | Ubuntu 22.04 | 2.35 | 3.10 | 20.10+ | 18.x |
| TOS 7.x（后续小版本，兼容TOS7.0） | Ubuntu 22.04 | 2.35 | 3.10 | 24.x | 20.x |

> **重要：** 应用必须通过 config.ini 中的 `low_version` 声明最低 TOS 版本要求。平台将自动过滤不兼容的设备。

> **TOS7.x 小版本兼容性：** TOS7.x 系列小版本（含7.1及以上）将基于 Ubuntu 22.04 保持核心依赖（glibc/Python3/Docker/Node.js）的 ABI/API 兼容性，为 TOS7.0 开发的应用无需额外适配即可运行。

**TOS7 小版本兼容性：**
- `low_version` 字段必须指定所需的最低 TOS 版本
- 提交更新时，请在最新的 TOS7 小版本上测试


### 4.5 大小写敏感规范

TOS 基于 Ubuntu Linux，文件系统严格区分大小写。所有应用必须遵循以下规则：

| 要素 | 规则 |
|---|---|
| 文件名 | 严格匹配大小写。`config.ini` ≠ `Config.ini` ≠ `CONFIG.INI` |
| 目录名 | 严格匹配大小写。`/images/icons/` ≠ `/Images/Icons/` |
| config.ini 键名 | 所有键名小写。`"version"` 正确，`"Version"` 错误 |
| 应用 ID（`id`） | 严格匹配大小写。`MyApp` ≠ `myapp` 。创建后不可修改 |
| Systemd 服务名 | 必须严格匹配，区分大小写 |


**禁止：** 在单个应用包中使用同一文件或目录的大小写变体。这会导致 Linux 上出现"找不到文件"和"服务启动失败"错误。

---

---

### 4.6 跨平台换行符规范（CRLF to LF）

所有在 TOS 系统（Linux 环境）中运行的脚本和配置文件，**必须使用 LF（`\n`）作为换行符**，禁止使用 Windows 默认的 CRLF（`\r\n`）换行符。

#### 问题影响

- 脚本执行报错 `bad interpreter: No such file or directory`
- 配置文件解析失败（如 systemd 服务文件、Nginx 配置）
- 解释器路径被错误识别为 `/bin/bash\r` 等不存在的二进制

#### 强制要求

1. 所有 `.sh` / `.py` / `.ini` / `.lang` / `.service` / `.conf` 文件，提交前必须转为 LF 换行
2. Deb 包构建脚本中，必须加入自动转换逻辑，避免构建过程中引入 CRLF

#### 推荐修复方案

##### 方案 1：在构建脚本中自动转换（推荐）

```python
import os

def convert_crlf_to_lf(file_path):
    with open(file_path, "rb") as f:
        content = f.read()
    content = content.replace(b"\r\n", b"\n")
    with open(file_path, "wb") as f:
        f.write(content)

# 打包前，遍历所有需要转换的文件
for root, _, files in os.walk("your_app_source/"):
    for name in files:
        if name.endswith((".sh", ".py", ".ini", ".lang", ".service", ".conf")):
            convert_crlf_to_lf(os.path.join(root, name))
```

##### 方案 2：本地开发工具配置

- **VS Code**：右下角状态栏点击 `CRLF` ，切换为 `LF` 后保存
- **Git 全局配置**（避免后续文件自动转为 CRLF）：

```bash
git config --global core.autocrlf input
```

## 5. ABI/API 兼容性与稳定性策略


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


### 5.3 TOS 平台 API

TOS7 对外提供以下官方 API 供应用使用。应用必须使用这些 API，而不是直接操作系统文件。

| API | 方法 | 说明 | 版本 |
|---|---|---|---|
| `/v2/proxy/<app_id>/` | ANY | WebUI 内部打开应用的平台代理入口 | v2 |
| 共享文件夹管理 | `ter_share_add` | 创建共享文件夹 | TOS7.0+ |
| 应用中心状态 | 平台内部 | 应用安装/启动/停止/卸载生命周期 | TOS7.0+ |

**API 鉴权：**
- WebUI 内部打开应用：使用 `Cookie` 自定义 Header 携带会话 Cookie（参见 8.10 节）
- WebUI 外部打开应用：HTTP 标准鉴权
- 系统级 API 调用：使用 TOS 系统用户上下文


### 5.4 测试建议

为确保前向兼容性：
- 提交前在最新 TOS7 版本上测试你的应用
- 在 Deb 包中使用版本锁定的依赖
- Docker 应用应锁定镜像标签为特定版本（而非 `:latest`）
- 在开发者平台订阅 TOS 发行说明

---

## 6. 开发环境

### 6.1 支持的目标架构

| 架构 | 构建目标 | Deb 架构字段 |
|---|---|---|
| x86_64 | x86_64-pc-linux-gnu | amd64 |
| aarch64 | aarch64-linux-gnu | arm64 |

> 应用需为每个目标架构单独提供构建。多架构支持需分别提交。

### 6.2 开发工具

**Deb 应用：**
- `dpkg-dev`、`debhelper` — Debian 打包工具
- `lintian` — Debian 包合规检查器
- `systemd` — 服务管理测试

**Docker 应用：**
- `docker`（20.10+）、`docker-compose` — 容器工具链
- `docker scan` / `trivy` — 漏洞扫描

**测试：**
- 需要一台运行 **TOS 7.0（当前稳定版/测试版）** 的 TNAS 设备进行本地验证，后续TOS7.x版本将保持兼容性，无需重复验证
- 可使用 Ubuntu 22.04 虚拟机进行初步测试

**开发者无TNAS硬件时的替代测试方案：**

1. 使用 Ubuntu 22.04 虚拟机进行 Deb 应用的基础功能测试
2. 使用 Docker Desktop（Windows/macOS/Linux）模拟 TOS7.0 的 Docker 环境，验证容器应用的兼容性
3. **本地部署 Open TOS**：Open TOS 与 TNAS TOS7.0 系统完全一致，可安装在普通电脑或虚拟机上。开发者可从铁威马官网下载 Open TOS 镜像，自行部署测试环境
4. **远程体验机测试**：开发者若无硬件设备，可申请铁威马官方提供的 TOS7.0 远程体验机，在官方论坛获取体验机的登录信息，无需自备硬件即可完成完整测试

---

## 7. 应用类型

| 类型 | 适用场景 | 包格式 | 提交格式 |
|---|---|---|---|
| Deb 应用 | 直接运行在宿主机的二进制程序/脚本 | 标准 `.deb` 包 | Deb 包 + 配置文件 |
| Docker 应用 | 需要独立运行环境的服务 | Docker 镜像 + docker-compose.yml | Compose 文件 + 配置文件 |

根据应用特性选择合适类型：

- **选择 Deb** — 如果你的应用是原生二进制、Python/Node.js 脚本或轻量级服务
- **选择 Docker** — 如果你的应用需要特定运行环境、依赖复杂或已有容器化版本

> **混合类型应用：** 当原生启动器管理 Docker 容器时，应用包可同时包含 Deb 和 Docker 组件。此时使用 `"application_type": "deb"` 并在 `depend` 中声明 `["DockerEngine"]`。Deb 组件作为 Docker 服务的启动器/管理器。

---

## 8. Deb 应用开发与配置规范

### 8.1 概述

Deb 应用是直接运行在 TOS7 宿主系统上的原生包。遵循标准 Debian 打包规范，并针对 TOS 服务管理和平台集成进行了适配。

TOS7 的 Deb 应用根据是否有前端页面以及打开方式，分为 **三种子类型**：

| 子类型 | 适用场景 | 打开方式 | 后端通信方式 |
|---|---|---|---|
| **WebUI 内部打开** | 后端为本地可执行服务、前端为静态 WebUI | TOS 桌面内嵌 iframe | Unix Socket + 平台代理 |
| **WebUI 外部打开** | 后端为本地可执行服务、前端为静态 WebUI | 浏览器新标签页 | Nginx 反向代理 + HTTP 端口 |
| **无 UI 服务** | 没有操作页面的后台服务 | 无前端页面 | 按需（无强制要求） |


**子类型选择强制约束：**

| 应用特性 | 必须使用的子类型 |
|---|---|
| 有 Web UI 且必须在 TOS 桌面内打开 | WebUI 内部打开（iframe） |
| 有 Web UI 且必须在浏览器标签页打开 | WebUI 外部打开（新标签页） |
| 无前端/后台守护服务 | 无 UI 服务 |
| 需要通过 TOS 文件管理器访问设备文件系统 | WebUI 内部或外部打开 |

TOS7 的 Deb 应用支持 **两种打包方式**：

| 打包方式 | 适用场景 | 说明 |
|---|---|---|
| **方式一：单包模式** | 从零开发的新应用 | 开发者按照 TOS7.0 规范直接开发，将所有文件集成到单个 deb 包中 |
| **方式二：双包模式（压缩包模式）** | 已有通用标准 deb 包的应用 | 原应用安装包（deb源包）保持不变，额外提供一个符合 TOS7.0 规范的数据包（<appid>.deb），两者打包为 tar.gz 压缩包提交 |


**双包模式适用规则：**

| 场景 | 必须使用 | 禁止使用 |
|---|---|---|
| 已有通用标准 deb 包、构建复杂 | 双包模式 | — |
| 从零开发的新应用 | — | 双包模式（应使用单包模式） |
| 简单二进制程序、无已有的打包 | — | 双包模式（应使用单包模式） |
| 第三方上游 Debian 包 | 双包模式 | — |

**双包模式强制约束：**

- **版本一致性：** 数据包与源包的 `Version` 字段必须完全一致，不一致直接驳回。
- **内容限制：** 数据包（`<appid>.deb`）**严禁包含任何二进制文件**，否则直接驳回。
- **安装顺序：** 由 APT 仓库依赖机制自动保证（数据包 `Depends` 源包），无需额外配置。
- **源包独立性：** deb源包必须可以独立在TOS7.0系统上使用`dpkg -i`命令进行安装。
- **依赖声明：** deb数据包的元数据 `Depends` 字段，必须要写上 deb源包，最好和版本一起指定，保持健康的依赖关系。

### 8.2 通用目录结构

所有 Deb 应用的文件安装到 `/usr/local/<app_id>/` 目录下：

```
/usr/local/<app_id>/
├── config.ini                    # 【必填】应用核心配置文件
├── bin/
│   └── <binary_name>             # 【必填】后端可执行文件
├── <app_id>.lang                 # 【必填】多语言配置文件
├── images/
│   └── icons/
│       └── <icon_file>.svg       # 【必填】应用图标
├── init.d/
│   └── <system_id>.service       # 【必填】Systemd 服务单元文件
├── webui.bz2                     # 【WebUI 应用必填】前端页面压缩包
└── nginx/                        # 【仅外部打开需要】
    └── <app_id>.conf             # Nginx 配置文件
```

**强制对应关系：**

```text
config.ini.id              == <app_id>
config.ini.package         == DEBIAN/control 中的 Package
config.ini.system_id       == systemd 服务单元 ID（不含 .service 后缀）
config.ini.icon            == "/images/icons/<icon_file>.svg"
config.ini.path            == "/<app_id>/"（WebUI 内部打开）
```

**要求：**
1. 应用文件安装到 `/usr/local/<app_id>/`。
2. `<app_id>.lang` 文件名必须与 `config.ini.id` 对应。
3. 图标文件路径必须与 `config.ini.icon` 对应。
4. systemd 服务单元 ID 必须与 `config.ini` 中的 `system_id` 一致。
5. deb 元数据中的二进制包名 `Package` 必须与 `config.ini` 中的 `package` 一致。
6. 服务必须能通过 `<system_id>.service` 启动、停止和查询状态。

### 8.3 三种子类型详解

**三种子类型互斥 — 每个应用只能属于其中一种：**

| 子类型 | config.ini 必填字段 | 关键标识 |
|---|---|---|
| **iframe（内部打开）** | `type`、`path` | `"type": "iframe"`、`"open_path": false` |
| **外部打开（新标签页）** | `path` | `"open_path": true`（不写 `type` 字段） |
| **无 UI 服务** | 无页面相关字段 | 不写 `path`、`open_path`、`type` 字段 |

> **互斥规则：** `type` 和 `open_path` 不可同时出现 — iframe 用 `"type": "iframe"`；外部打开用 `"open_path": true`；无 UI 两者皆不写。混用将导致行为未定义，审核时驳回。

#### 8.3.1 WebUI 内部打开（iframe 嵌入）

适用于后端为本地可执行服务、前端为静态 WebUI，在 TOS 桌面内嵌 iframe 打开的应用。

**目录结构：**

```
/usr/local/<app_id>/
├── config.ini
├── bin/
│   └── <binary_name>
├── <app_id>.lang
├── webui.bz2                     # 【必填】前端页面压缩包
├── images/
│   └── icons/
│       └── <icon_file>.svg
└── init.d/
    └── <system_id>.service
```

**config.ini 最小配置：**

```json
{
  "id": "<app_id>",
  "icon": "/images/icons/<icon_file>.svg",
  "exec": true,
  "version": "<app_version>",
  "category": ["Utilities"],
  "platform": "x86_64",
  "system_id": "<system_id>",
  "package": "<deb_package_name>",
  "application_type": "deb",
  "path": "/<app_id>/",
  "type": "iframe"
}
```

**核心要求：**

1. `type` 字段必须为 `"iframe"`。
2. `path` 字段格式为 `"/<app_id>/"`。
3. `webui.bz2` 是固定文件名，不能写成其他名称。
4. deb包必须包含可执行程序，可执行程序存放地址 `/usr/local/<app_id>/bin/<binary_name>`。
5. `config.ini.package` 字段规范必须严格符合Debian包的 `package` 规范。
6. 后端服务通过 Unix Socket 对外提供 HTTP 接口，启动时必须在 `/var/api/<app_id>.sock` 监听。
7. `/var/api` 不存在时必须自动创建；启动前必须清理旧 socket 文件。
8. socket 文件权限必须允许平台代理访问。
9. 前端请求后端接口时必须走平台代理路径，固定格式为 `/v2/proxy/<app_id>`。
10. 前端请求必须携带平台鉴权所需 header，请求header中携带 `X-Csrf-Token` 和 `Cookie`。


**Socket 文件规范：**
- 权限模式：`0660`（属主和属组读写）
- 属主：`<appid>:<appid>`（与服务用户匹配）
- 支持 HTTP keep-alive 连接
- 至少支持 100 个并发连接
- 空闲连接超时时间：30 秒

7. 前端请求后端接口时必须走平台代理路径：`/v2/proxy/<app_id>/<api_name>`。
8. 前端请求必须携带平台鉴权 header。


**跨域和预检请求配置：**
后端必须为平台代理处理 CORS 预检请求（OPTIONS 方法）。允许以下内容：
- Origin：TOS Web 源
- Methods：GET, POST, PUT, DELETE, OPTIONS
- Headers：Content-Type, X-Csrf-Token, Cookie
- Credentials：true

#### 8.3.2 WebUI 外部打开（新标签页）

适用于后端为本地可执行服务、前端为静态 WebUI，在浏览器新标签页打开的应用。

**目录结构：**

```
/usr/local/<app_id>/
├── config.ini
├── bin/
│   └── <binary_name>
├── <app_id>.lang
├── webui.bz2                     # 【必填】前端页面压缩包
├── images/
│   └── icons/
│       └── <icon_file>.svg
├── nginx/
│   └── <app_id>.conf             # 【必填】Nginx 配置文件
└── init.d/
    └── <system_id>.service
```

**config.ini 最小配置：**

```json
{
  "id": "<app_id>",
  "icon": "/images/icons/<icon_file>.svg",
  "exec": true,
  "version": "<app_version>",
  "category": ["Utilities"],
  "platform": "x86_64",
  "system_id": "<system_id>",
  "package": "<deb_package_name>",
  "application_type": "deb",
  "path": "/<app_id>/",
  "open_path": true
}
```

**核心要求：**

1. `open_path` 必须为 `true`。
2. `path` 字段必须对应 nginx 配置文件的路由，并且可以解析到对外提供的 HTTP 接口。
3. 应用包必须携带 nginx 配置文件 `<app_id>.conf`，文件名必须与 `config.ini.id` 对应。
4. 后端直接监听 `<listen_port>` 提供 HTTP 接口。
5. deb包必须包含可执行程序，可执行程序存放地址 `/usr/local/<app_id>/bin/<binary_name>`。
6. `config.ini.package` 字段规范必须严格符合Debian包的 `package` 规范。


**端口监听规则：**
- **必须**监听 `0.0.0.0`（所有网络接口），禁止仅监听 `127.0.0.1`。仅监听本地回环地址会阻止外部访问。
- **禁止**占用系统保留端口（22、80、443、8181、5050）
- 推荐端口范围：8000-19999

**nginx 配置文件模板：**

在 `/usr/local/<app_id>/nginx/<app_id>.conf` 创建：

```nginx
location /<app_id>/ {
    proxy_pass http://127.0.0.1:<listen_port>/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```


**Nginx 配置管理要求：**
- 配置文件权限：`644`（属主读写，属组和其他只读）
- 配置文件必须放置在 `/usr/local/<app_id>/nginx/<app_id>.conf`
- 平台 Nginx 的 `include` 指令按字母顺序加载配置；应用间端口冲突通过唯一端口解决 — 两个应用不能共享同一端口
- 日志轮转：Nginx 访问/错误日志由平台管理；请勿写入自己的 nginx 日志
- 禁止包含 `server {}` 块；仅使用 `location /<app_id>/ {}` 块

#### 8.3.3 无 UI 服务

适用于没有操作页面的后台服务应用。

**目录结构：**

```
/usr/local/<app_id>/
├── config.ini
├── bin/
│   └── <binary_name>
├── <app_id>.lang
├── images/
│   └── icons/
│       └── <icon_file>.svg
└── init.d/
    └── <system_id>.service
```

**config.ini 最小配置：**

```json
{
  "id": "<app_id>",
  "icon": "/images/icons/<icon_file>.svg",
  "exec": true,
  "version": "<app_version>",
  "category": ["Utilities"],
  "platform": "x86_64",
  "system_id": "<system_id>",
  "package": "<deb_package_name>",
  "application_type": "deb"
}
```

**核心要求：**

1. 无 UI 应用不需要 `path`、`type`、`open_path`、`resize`、`maxmin`、`width`、`height` 等前端相关字段。
2. 不需要 `webui.bz2` 前端压缩包。
3. 不需要 `nginx/` 目录。
4. deb包必须包含可执行程序，可执行程序存放地址 `/usr/local/<app_id>/bin/<binary_name>`。
5. `config.ini.package` 字段规范必须严格符合Debian包的 `package` 规范。


**状态上报要求：**
无 UI 应用必须上报其运行状态，以便平台检测故障：
- systemd 服务单元的 `Type` 应为 `simple` 或 `forking`
- 使用 systemd 的 `ExecStartPost` 确认成功启动
- 应用中心基于 systemd 服务状态显示"运行中"/"已停止"/"异常"
- 故障时，systemd 自动重启（在服务文件中配置）处理恢复


### 8.4 核心配置文件 — config.ini

config.ini 是核心元数据文件，定义应用的身份信息、展示信息、运行属性和依赖关系。是平台校验和应用中心展示的关键依据。

> **重要：** 文件扩展名为 `.ini`，但内容必须为 **严格 JSON 格式**。禁止添加注释、使用单引号、多余逗号或任何语法错误。

> **格式说明：** 文件扩展名 `.ini` 是公司历史使用习惯（与传统配置系统保持文件命名一致），但解析器按 JSON 格式处理。开发者务必使用 JSON 语法编写，否则将导致自动校验失败（错误码 E002）。

#### 8.4.1 标准模板

```json
{
  "id": "Example-latest",
  "icon": "/images/icons/Example-latest.svg",
  "publisher": "开发者名称",
  // "path": "/myapp/",              // iframe（内部打开）
  // "path": "http://${ip}:8686",   // 外部打开
  "exec": true,
  "open_path": true,
  "resize": true,
  "maxmin": true,
  "width": 0,
  "height": 0,
  "help": "https://github.com/example/docs",
  "version": "1.0.0",
  "recommend": false,
  "beta": false,
  "low_version": "TOS7.0",
  "category": ["Utilities"],
  "depend": [],
  "relation": [],
  "platform": "x86_64",
  "official": "https://example.com",
  "application_type": "deb",
  "system_id": "example",
  "package": "example-app",
  "user": "example",
  "all_user_display": true
}
```

#### 8.4.2 字段参考

| 字段 | 类型 | 必填 | 说明 | 详细描述 |
|---|---|---|---|---|
| `id` | string | ✅ 是 | 应用唯一标识符 | 平台全局唯一，不可与已上架应用重复。字符集：小写字母（`a-z`）、数字（`0-9`）和连字符（`-`）。必须以字母开头。最大长度：50 字符。示例：`my-app-latest`。创建后不可修改。 |
| `icon` | string | ✅ 是 | 图标路径 | 仓库中的相对路径。必须遵循 `/images/icons/<id>.svg` 格式。图标文件必须存在于该路径。 |
| `publisher` | string | ✅ 是 | 发布者名称 | 在应用中心展示的开发者或组织名称。示例：`"Kevin"`、`"LinuxServer.io"`。 |
| `path` | string | 条件必填 | 应用访问地址 | **`path` 字段按场景互斥：iframe 用 `/<app_id>/`；外部打开用 `http://${ip}:<端口>`；无 UI 留空。** 必须使用 `${ip}` 占位符（如 `http://${ip}:8686`）。系统自动替换 `${ip}` 为 TNAS 局域网 IP。**禁止写死固定 IP 或域名。** 非 80/443 端口：`http://${ip}:<端口>`。WebUI 内部打开（iframe）：`/<app_id>/`。无 UI 应用：设为 `""` 或省略该字段。`exec=true` 时必填。 |
| `exec` | bool | ✅ 是 | 是否有可执行服务 | 应用是否支持启停操作。`true`：应用中心显示启动/停止按钮；`false`：仅展示，无生命周期控制。 |
| `open_path` | bool | 条件必填 | 是否在新标签页打开 | 控制应用打开方式：`true` = 浏览器新标签页；`false` 或省略 = TOS 桌面内嵌 iframe。外部打开应用必须设为 `true`。 |
| `resize` | bool | 否 | 窗口是否可拉伸 | 仅 `open_path=false` 时生效。控制应用弹窗是否可调整大小。默认 `false`。 |
| `maxmin` | bool | 否 | 窗口是否可最大化/最小化 | 仅 `open_path=false` 时生效。控制应用弹窗是否支持最大化/最小化。默认 `false`。 |
| `width` | int | 否 | 默认窗口宽度 | 仅 `open_path=false` 时生效。应用打开页面的宽度，默认值 1180。 |
| `height` | int | 否 | 默认窗口高度 | 仅 `open_path=false` 时生效。应用打开页面的高度，默认值 680。 |
| `help` | string | 否 | 帮助文档网址 | 指向帮助文档、Wiki 或社区教程的链接。无则留空。 |
| `version` | string | ✅ 是 | 应用版本号 | 遵循语义化版本号。每次提交必须唯一且递增。示例：`"1.0.0"`、`"2.3.1"`。 |
| `recommend` | bool | ✅ 是 | 是否推荐应用 | 平台专用字段。开发者必须设为 `false`。审核后平台可根据质量调整。 |
| `beta` | bool | ✅ 是 | 是否测试版 | `true` = 测试版，仅对测试用户展示；`false` = 正式版，全量用户展示。 |
| `low_version` | string | ✅ 是 | 支持的最低TOS版本 | 应用可正常运行的最低 TOS 版本。必须为 `TOS7.0` 及以上。格式：`"TOS7.0"`、`"TOS7.1"`。 |
| `category` | []string | ✅ 是 | 应用分类 | 最多3个分类，从官方分类列表中选择（见[附录A](#附录a分类列表)）。**第一个分类为主要分类** — 决定应用的默认展示分区。按从最具体到最通用的顺序排列。超量分类将导致驳回。 |
| `depend` | []string | ✅ 是 | 依赖应用列表 | 安装前必须先安装的应用 ID。必须为应用中心已有的应用 ID。依赖按列表顺序安装。示例：`["DockerEngine"]`。无依赖：`[]`。**循环依赖将被驳回。** |
| `relation` | []string | 否 | 关联应用列表 | 应用详情页"关联应用"模块展示的应用 ID。无强制依赖，仅展示关联。无关联：`[]`。 |
| `platform` | string | ✅ 是 | 目标架构 | `"x86_64"` 或 `"aarch64"`。多架构需分别提交。 |
| `official` | string | 否 | 官方网站 | 应用官方网站链接。无则留空。 |
| `application_type` | string | ✅ 是 | 应用包类型 | Deb 单包应用填 `"deb"`，双包/压缩包应用填 `"deb-TarGz"`，Docker 应用填 `"docker"`。 |
| `system_id` | string | 条件必填 | Systemd 服务名 | **Deb 应用必填。** 必须与 systemd 服务文件名一致。Docker 应用留空。 |
| `package` | string | 条件必填 | Deb 包名 | **Deb 应用必填。** 必须与 DEBIAN/control 中的 `Package` 字段一致。Docker 应用留空。 |
| `user` | string | ✅ 是 | 运行用户 | 应用运行的系统用户。指定后自动创建专属用户（如 `"jellyfin"`）。Deb 应用需与 systemd 服务 `User` 字段匹配。**严禁使用 root 用户。** |
| `all_user_display` | bool | ✅ 是 | 是否对所有用户展示 | `true` = 所有 TNAS 用户可见；`false` = 仅管理员可见。当为 `false` 时，应用仅在管理员的应用程序中心视图中出现。非管理员用户无法看到或与该应用交互。应用仍在系统范围内安装并为所有用户运行；此设置仅控制可见性。 |

#### 8.4.3 关键规则

**JSON 格式校验：**

提交前校验 config.ini：

```bash
# 使用 python3
python3 -c "import json; json.load(open('config.ini'))" && echo "JSON 格式有效"

# 使用 jq
jq empty config.ini
```

**常见导致驳回的 JSON 错误：**
```json
{
  "id": "MyApp",       // ❌ 对象最后一个字段末尾多余逗号
  "version": '1.0.0',  // ❌ 单引号（必须用双引号）
  // ❌ JSON 不允许注释
  "beta": false,
}
```
正确写法：
```json
{
  "id": "MyApp",
  "version": "1.0.0",
  "beta": false
}
```


1. **IP 占位符**：`path` 字段必须使用 `${ip}`（如 `http://${ip}:8686`）。禁止写死固定 IP 或域名。
2. **JSON 语法**：必须是有效 JSON。禁止注释（`//` 或 `/* */`）、单引号或末尾多余逗号。
3. **ID 唯一性**：`id` 必须全局唯一。重复 ID 将被驳回。
4. **版本递增**：每次新提交的版本号必须大于前一版本。禁止重复或降级。
5. **分类限制**：每个应用最多3个分类。
6. **TOS 版本**：`low_version` 必须为 TOS7.0 及以上。
7. **字段一致性**：`version` 在 config.ini、DEBIAN/control 和 app.lang 之间必须一致。`system_id` 必须与 systemd 服务文件名匹配。`package` 必须与 DEBIAN/control 的 `Package` 字段匹配。


**`path` 字段取值速查表：**

| 应用类型 | 打开方式 | `path` 填写值 | 示例 |
|---|---|---|---|
| Deb WebUI 内部打开 | iframe 嵌入 | `/<app_id>/` | `"/tmrtimer/"` |
| Deb WebUI 外部打开 | 新标签页 | `/<app_id>/` | `"/weather/"` |
| Docker 应用 | 新标签页 | `http://${ip}:<端口>` | `"http://${ip}:8080"` |
| 无 UI 服务 | 无前端 | 省略或 `""` | — |

> **注意：** iframe 模式（内部打开）和外部打开的 `path` 格式相同（均为 `/<app_id>/`），区别在于 `open_path` 字段：内部打开 `open_path=false`（默认），外部打开 `open_path=true`。Docker 应用的 `path` 使用 `http://${ip}:<端口>` 格式。


> **保留字段：** 以下字段名保留供未来平台使用。请勿在自定义 config.ini 中使用：`host_network`、`container_runtime`、`sandbox`、`auto_update`、`upstream_url`、`license`、`min_memory`、`min_cpu`、`min_disk`。使用保留字段可能导致未来兼容性问题和驳回。

---

### 8.5 语言文件 — app.lang

语言文件为应用中心提供多语言展示支持。系统根据用户设备语言自动加载对应语种。

#### 8.5.1 支持语种（14种必填）

| 标签 | 语言 |
|---|---|
| `zh-cn` | 简体中文 |
| `zh-hk` | 繁体中文 |
| `en-us` | 英语 |
| `fr-fr` | 法语 |
| `de-de` | 德语 |
| `it-it` | 意大利语 |
| `es-es` | 西班牙语 |
| `hu-hu` | 匈牙利语 |
| `ja-jp` | 日语 |
| `ko-kr` | 韩语 |
| `pl-pl` | 波兰语 |
| `ru-ru` | 俄语 |
| `tr-tr` | 土耳其语 |
| `pt-pt` | 葡萄牙语 |

#### 8.5.2 File Format

```ini
[en-us]
name = "应用名称"
auth = "开发者名称"
descript = "应用功能和特性的详细描述。"
release_note = "1. 新增功能。2. 修复问题。"
important = "用户需要注意的重要事项。"

[zh-cn]
name = "应用名称"
auth = "开发者名称"
descript = "应用功能和特性的详细描述。"
release_note = "1. 新增功能。2. 修复问题。"
important = "用户需要注意的重要事项。"
```

#### 8.5.3 Field Descriptions

| 字段 | 必填 | 说明 |
|---|---|---|
| `name` | ✅ 是 | 应用展示名称。若应用名称为统一语言名称（不翻译），各语种可使用相同名称。 |
| `auth` | ✅ 是 | 开发者/组织名称。 |
| `descript` | ✅ 是 | 应用功能描述。各语种语义必须一致。 |
| `release_note` | 否 | 版本更新内容。多条内容使用 `</br>` 换行。首次发布可留空。 |
| `important` | 否 | 重要提示信息（如权限要求、端口冲突、配置步骤等）。 |

#### 8.5.4 Rules

1. 14种语言节点必须全部存在。未完成翻译的语种，使用英语内容填充——**禁止留空**。
2. 文件编码必须为 **UTF-8 无 BOM**。
3. `descript` 字段各语种功能描述语义必须一致。
4. 若应用名称为统一语言名称（不翻译），各语种的 `name` 可使用相同名称。
5. 文件命名规范：`<appid>.lang`（如 `aria2.lang`）。


#### 8.5.5 File Encoding & Format

- 文件编码必须为 **UTF-8 无 BOM**
- 换行符必须为 **LF**（Unix 风格，`\n`）。CRLF（Windows 风格，`\r\n`）将导致解析错误
- 文件命名规范：`<appid>.lang`（如 `aria2.lang`）

#### 8.5.6 Text Length Limits

| 字段 | 最大长度 | 说明 |
|---|---|---|
| `name` | 64 字符 | 展示名称，超出将被截断 |
| `auth` | 64 字符 | 开发者/组织名称 |
| `descript` | 512 字符 | 功能描述 |
| `release_note` | 2048 字符 | 多行用 `</br>` 分隔 |
| `important` | 512 字符 | 重要提示 |

#### 8.5.7 release_note Format

- 多条内容使用 `</br>` 作为换行分隔符
- **禁止**使用其他 HTML 标签（`<b>`、`<p>`、`<div>` 等）—— 可能导致页面渲染异常
- 仅限纯文本，`</br>` 换行除外

#### 8.5.8 Translation Consistency

- 所有 14 种语言的 `descript` 字段语义必须一致
- 审核人员至少验证核心语言（zh-cn、en-us）的翻译准确性，其他语言若存在明显错误，将要求开发者修正

---

### 8.6 应用图标

| 要求 | 规范 |
|---|---|
| 格式 | SVG（矢量图形，透明背景） |
| 文件名 | 必须与 config.ini 中的 `id` 完全一致（如 `Example-latest.svg`） |
| 存放路径 | 仓库 `/images/icons/` 目录下 |
| ViewBox | 建议：`0 0 512 512` |
| 设计要求 | 清晰可识别，无违规内容 |

图标展示场景：应用列表、应用详情页、已安装应用面板。

---

### 8.7 后端服务规范

#### 8.7.1 WebUI 内部打开（Unix Socket 模式）

后端可执行文件安装到：

```text
/usr/local/<app_id>/bin/<binary_name>
```

后端必须创建并监听 Unix Socket：

```text
/var/api/<app_id>.sock
```

**要求：**
1. `/var/api` 不存在时必须自动创建。
2. 启动前必须清理旧 socket 文件。
3. socket 文件权限必须允许平台代理访问。
4. 后端接口协议为 HTTP-over-Unix-Socket。
5. 后端应优雅处理 `SIGTERM`，便于 systemd 停止服务。


**标准日志规范：**

| 日志级别 | 用途 |
|---|---|
| ERROR | 服务故障、启动错误、数据损坏 |
| WARN | 弃用功能、可恢复错误、配置问题 |
| INFO | 服务生命周期事件（启动/停止）、版本信息、配置已加载 |
| DEBUG | 详细诊断信息（生产环境应禁用） |

**标准输出格式：**
```
[YYYY-MM-DD HH:MM:SS] [LEVEL] [component] message
```
示例：
```
[2026-05-11 16:30:00] [INFO] [main] 服务已在端口 8686 上启动
```

对于 systemd 管理的服务，优先使用 stdout/stderr 输出日志 — systemd journal 会自动捕获两者。

**服务崩溃自动重启限制：**
- 最大重启尝试次数：**60 秒内 5 次**
- 超出限制后，服务进入失败状态
- 应用中心在重启限制超出后显示服务为"异常"
- 在 systemd 中配置：`StartLimitBurst=5`，`StartLimitIntervalSec=60`

#### 8.7.2 WebUI 外部打开（HTTP 端口模式）

后端可执行文件安装到：

```text
/usr/local/<app_id>/bin/<binary_name>
```

后端直接监听 `<listen_port>` 提供 HTTP 接口。

**要求：**
1. 直接监听 `<listen_port>`。
2. 提供静态 WebUI 首页。
3. 提供健康检查接口。
4. 提供业务 API 路由，具体业务由应用自行定义。
5. 优雅处理 `SIGTERM` 和 `SIGINT`。

**推荐固定路由：**

```text
GET /
GET /health
```

**业务 API 推荐命名：**

```text
/api/<resource>
```

如需兼容系统入口，可同时支持：

```text
/<app_id>/api/<resource>
/v2/proxy/<app_id>/<resource>
/v2/proxy/<app_id>/api/<resource>
```

### 8.8 前端文件规范

适用于 WebUI 应用（内部打开和外部打开）。

前端源码可以放在项目源码目录中：

```text
webui/
├── index.html
├── app.js
└── styles.css
```

打包时必须压缩为 `webui.bz2`，安装后路径：

```text
/usr/local/<app_id>/webui.bz2
```

**要求：**
1. `webui.bz2` 解压后必须包含可正常打开的 `.html` 文件。
2. 推荐至少包含 `index.html`、`app.js`、`styles.css`。
3. 前端页面每次新打开时应初始化为空状态，不应复用上一次运行的临时输入状态。
4. 前端资源引用应带版本参数，避免应用升级后继续加载旧缓存。

```html
<link rel="stylesheet" href="./styles.css?v=<version>">
<script src="./app.js?v=<version>"></script>
```

### 8.9 前后端请求规范（WebUI 内部打开）

前端访问后端时**不能直接访问 socket 文件**。请求必须走平台 HTTP 代理路径：

```text
/v2/proxy/<app_id>/<api_name>
```

如果应用只有一个主接口，建议：

```text
/v2/proxy/<app_id>
```

**前端发送请求示例：**

```js
fetch("/v2/proxy/<app_id>/<api_name>", {
  method: "POST",
  credentials: "include",
  headers,
  body: JSON.stringify(payload)
});
```

后端建议兼容以下路由，避免不同代理模式下路径不一致：

```text
/<app_id>
/<app_id>/<api_name>
<config.ini.path>/<api_name>
<config.ini.path>/<app_id>
```

### 8.10 前端鉴权 Header 规范（WebUI 内部打开）

前端发送后端请求时，必须读取当前网站 cookie。

**必须读取的 cookie：**

```text
TMSESSNAME
X-Csrf-Token
```

**请求 header 必须包含：**

```text
X-Csrf-Token: <从 cookie 读取到的 X-Csrf-Token 值>
Cookie: TMSESSNAME=<从 cookie 读取到的 TMSESSNAME 值>; X-Csrf-Token=<从 cookie 读取到的 X-Csrf-Token 值>;
```

**示例：**

```text
X-Csrf-Token: ltRoTGSICC68drxbvljhBeD2DZ7LPcge
Cookie: TMSESSNAME=46958db9-1f8a-4686-b340-34fd8ccf62e8; X-Csrf-Token=ltRoTGSICC68drxbvljhBeD2DZ7LPcge;
```

**前端实现示例：**

```js
function getCookie(name) {
  const prefix = encodeURIComponent(name) + "=";
  return document.cookie
    .split(";")
    .map((item) => item.trim())
    .find((item) => item.startsWith(prefix))
    ?.slice(prefix.length) || "";
}

const sessionName = getCookie("TMSESSNAME");
const csrfToken = getCookie("X-Csrf-Token");

const headers = {
  "Content-Type": "application/json",
  "X-Csrf-Token": csrfToken,
  "Cookie": `TMSESSNAME=${sessionName}; X-Csrf-Token=${csrfToken};`
};
```

**注意事项：**
1. 浏览器不允许前端手动设置标准 `Cookie` header。
2. 本规范使用自定义 header `Cookie` 传递拼接后的 cookie 字符串。
3. `Cookie` 为固定 key 名称，必须按平台要求拼写。
4. 请求应保留 `credentials: "include"`。

后端如需支持浏览器预检请求，应允许以下 header：

```text
Content-Type
X-Csrf-Token
Cookie
```


**`Cookie` Header 命名说明：** 自定义 header 名称 `Cookie` 是平台内部命名约定。它绕过了浏览器在 JavaScript fetch/XHR 请求中设置标准 `Set-Cookie` header 的限制。此名称固定，不得修改 — 任何偏差都会破坏鉴权。

**后端鉴权校验示例（Python）：**
```python
def validate_auth(headers):
    '''校验来自前端请求的 Cookie 鉴权 header。'''
    ciikie = headers.get('Cookie', '')
    csrf_token = headers.get('X-Csrf-Token', '')
    
    # 解析 Cookie header（格式：key1=val1; key2=val2）
    parts = {}
    for part in ciikie.split(';'):
        if '=' in part:
            k, v = part.strip().split('=', 1)
            parts[k.strip()] = v.strip()
    
    session_name = parts.get('TMSESSNAME', '')
    ciikie_csrf = parts.get('X-Csrf-Token', '')
    
    if not session_name or not csrf_token:
        return False
    if csrf_token != ciikie_csrf:
        return False
    # 通过 TOS 平台验证会话
    return True
```

**后端鉴权校验示例（Go）：**
```go
func validateAuth(r *http.Request) bool {
    ciikie := r.Header.Get("Cookie")
    csrfToken := r.Header.Get("X-Csrf-Token")
    if ciikie == "" || csrfToken == "" {
        return false
    }
    for _, part := range strings.Split(ciikie, ";") {
        kv := strings.SplitN(strings.TrimSpace(part), "=", 2)
        if len(kv) == 2 && kv[0] == "X-Csrf-Token" {
            if kv[1] != csrfToken {
                return false
            }
        }
    }
    return true
}
```

**Token 过期与会话失效处理：**
- 鉴权 token 过期或会话失效时，后端必须返回 HTTP `401 Unauthorized`
- 前端必须检测 401 响应并重定向到 TOS 登录页面
- 请勿尝试自动刷新 token；重定向到 `/` 触发 TOS 重新鉴权

```javascript
fetch('/v2/proxy/myapp/api', { credentials: 'include' })
  .then(res => {
    if (res.status === 401) {
      window.location.href = '/';  // 重定向到 TOS 登录
    }
    return res.json();
  });
```

---
### 8.11 Nginx 配置规范（WebUI 外部打开）

必须在 `config.ini` 同级创建 nginx 配置目录：

```text
/usr/local/<app_id>/nginx/<app_id>.conf
```

**内容模板：**

```nginx
location /<app_id>/ {
    proxy_pass http://127.0.0.1:<listen_port>/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**示例（weather 应用，端口 16688）：**

```nginx
location /weather/ {
    proxy_pass http://127.0.0.1:16688/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 8.12 Systemd 服务规范

服务单元 ID 来自 `config.ini.system_id`：

```json
{
  "system_id": "<system_id>"
}
```

最终系统服务必须是：

```text
<system_id>.service
```

应用安装目录内保留：

```text
/usr/local/<app_id>/init.d/<system_id>.service
```

**标准服务文件：**

**标准服务文件（含安全加固）：**

```ini
[Unit]
Description=<service_description>
After=network.target
StartLimitBurst=5
StartLimitIntervalSec=60

[Service]
Type=simple
User=<appid>
Group=<appid>
WorkingDirectory=/usr/local/<appid>
ExecStart=/usr/local/<appid>/bin/<binary_name>
Restart=always
RestartSec=3
TimeoutStartSec=30
TimeoutStopSec=10
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/<appid> /var/log/<appid>
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

**Systemd 指令参考：**

| 指令 | 值 | 是否必填 | 说明 |
|---|---|---|---|
| `User` | `<appid>` | ✅ 是 | 以专用非 root 用户运行服务 |
| `Group` | `<appid>` | ✅ 是 | 以专用组运行服务 |
| `WorkingDirectory` | `/usr/local/<appid>` | ✅ 是 | 服务的工作目录 |
| `NoNewPrivileges` | `true` | ✅ 是 | 阻止权限提升 |
| `ProtectSystem` | `strict` | ✅ 是 | 将 /usr、/boot、/etc 挂载为只读 |
| `ProtectHome` | `true` | ✅ 是 | 隐藏 /home 目录 |
| `TimeoutStartSec` | `30` | ✅ 是 | 服务启动超时（秒） |
| `TimeoutStopSec` | `10` | ✅ 是 | 优雅停止超时（秒） |
| `AmbientCapabilities` | `CAP_NET_BIND_SERVICE` | 条件 | 仅在绑定 1024 以下端口时需要 |
| `ReadWritePaths` | `/var/lib/<appid> /var/log/<appid>` | ✅ 是 | 显式声明可写路径 |
| `RestartSec` | `3` | 建议 | 重启前延迟（秒） |
| `Restart` | `always` | 建议 | 自动重启策略 |
| `LimitNOFILE` | `65536` | 建议 | 文件描述符限制 |
| `StartLimitBurst` | `5` | 建议 | 间隔内最大重启次数 |
| `StartLimitIntervalSec` | `60` | 建议 | 重启限制间隔（秒） |

### 8.13 DEBIAN/control 文件

#### 8.13.1 单包模式

单包模式下，所有内容集成在一个 deb 包中：

```
Package: <appid>
Version: <version>
Architecture: amd64
Section: utils
Priority: optional
Maintainer: 开发者名称 <your.email@example.com>
Depends: libc6 (>= 2.34), systemd
Description: 简短描述
 应用功能的详细描述。
```

**字段参考：**

| 字段 | 必填 | 说明 |
|---|---|---|
| `Package` | ✅ 是 | 包名。必须与 config.ini 的 `package` 字段一致。 |
| `Version` | ✅ 是 | 包版本。必须与 config.ini 的 `version` 字段一致。 |
| `Architecture` | ✅ 是 | x86_64 填 `amd64`，aarch64 填 `arm64`。 |
| `Section` | 是 | 包分类（如 `utils`、`web`、`net`）。 |
| `Priority` | 是 | 通常为 `optional`。 |
| `Maintainer` | ✅ 是 | 开发者名称和邮箱。 |
| `Depends` | 建议 | 运行时依赖。声明所有必需的系统库和包。 |
| `Description` | ✅ 是 | 第一行为简短描述，后续行为详细描述。见下方格式规则。 |

**架构字段参考：**

| TOS 平台 | DEBIAN/control `Architecture` | 构建目标 |
|---|---|---|
| x86_64 / amd64 | `amd64` | `x86_64-pc-linux-gnu` |
| aarch64 / arm64 | `arm64` | `aarch64-linux-gnu` |

**常见错误：**
- 在 DEBIAN/control 中使用 `x86_64` → 必须使用 `amd64`
- 将 `arm64` 用于 32 位 ARM → 必须使用 `armhf`（TOS7 不支持）

**Description 字段格式：**
- 第 1 行：简短描述（最多 80 字符，无前导空格）
- 后续行：详细描述（每行必须以一个空格开头，每行最多 80 字符）
- 描述中的空行必须包含一个空格和一个句点：` .`

示例：
```
Description: 软件包的简短摘要
 这是详细描述。
 可以跨多行，
 每行以一个空格开头。
 .
 这是一个新段落。
```

#### 8.13.2 双包模式

双包模式适用于已有通用标准 deb 包的应用，源包保持不变，额外提供应用数据包。

**应用数据包 DEBIAN/control：**

```
Package: <appid>
Version: <version>
Architecture: all
Section: utils
Priority: optional
Maintainer: 开发者名称 <your.email@example.com>
Depends: <package> (>= <version>)
Description: 应用数据包 - <应用名称>
 TerraMaster App Center metadata package for <应用名称>.
```

> **命名说明：** 数据包包名使用 `<appid>`（建议与 config.ini.id 保持一致），源包包名使用 `<package>`（即原应用默认包名）。数据包通过 `Depends` 字段声明对源包的依赖。

**双包字段关联规则：**

| 字段 | 数据包 | 源包 | 关联要求 |
|---|---|---|---|
| `Package` | `<appid>` | `<package>` | 数据包包名建议与 config.ini.id 保持一致 |
| `Version` | `<version>` | `<version>` | 必须完全一致 |
| `Architecture` | `all` | `amd64`/`arm64` | 数据包通常为 `all`，源包为实际架构 |

**config.ini字段关联：**

| 字段 | 关联说明 |
|---|---|
| `config.ini.package` | 必须和**数据包**的元数据 `package` 对应 |
| `config.ini.version` | 必须和**数据包**的元数据 `version` 对应 |
| `config.ini.system_id` | 必须和**源包**的 systemd 服务 id 对应 |
| `config.ini.path`（外部打开时） | 必须对应 nginx 配置文件的路由，解析到源包对外提供的 `<listen_port>` |

**数据包内部文件结构：**

```
<appid>.deb
├── DEBIAN/
│   └── control
└── usr/
    └── local/
        └── <appid>/
            ├── config.ini
            ├── <appid>.lang
            ├── images/
            │   └── icons/
            │       └── <appid>.svg
            └── nginx/                    # 仅外部打开需要
                └── <appid>.conf
```

**源包内部文件结构：**

```
<package>.deb
├── DEBIAN/
│   ├── control
│   ├── preinst
│   ├── postinst
│   ├── prerm
│   └── postrm
└── usr/
    └── local/
        └── <appid>/
            ├── bin/
            │   └── <binary_name>
            └── init.d/
                └── <system_id>.service
```

### 8.14 生命周期脚本

**脚本要求：**
- 所有生命周期脚本必须以 `#!/bin/bash` shebang 开头
- 文件编码：UTF-8
- 文件权限：`755`（所有人可执行，属主可写）
- 所有脚本必须以 `0` 退出码表示成功
- 使用 `set -e` 在任何错误时失败退出

#### preinst — 安装前

```bash
#!/bin/bash
set -e

# 创建专属用户（如不存在）
if ! id -u <appid> > /dev/null 2>&1; then
    useradd --system --no-create-home --shell /usr/sbin/nologin <appid> 2>/dev/null || true
fi

# 创建数据目录
mkdir -p /var/lib/<appid>
chown <appid>:<appid> /var/lib/<appid> 2>/dev/null || true

# 创建 Unix Socket 目录（WebUI 内部打开）
mkdir -p /var/api

exit 0
```

#### postinst — 安装后

```bash
#!/bin/bash
set -e

# 设置文件权限
chown -R <appid>:<appid> /usr/local/<appid> 2>/dev/null || true
chown -R <appid>:<appid> /var/lib/<appid> 2>/dev/null || true

# 确保 webui.bz2 存在时解压（WebUI 应用）
if [ -f /usr/local/<appid>/webui.bz2 ]; then
    cd /usr/local/<appid> && tar -xjf webui.bz2 2>/dev/null || true
fi

# 启用并启动服务
systemctl daemon-reload
systemctl enable <system_id>.service
systemctl start <system_id>.service

exit 0
```

#### prerm — 卸载前

```bash
#!/bin/bash
set -e

# 杀死应用用户的所有残留进程（升级安全性）
pkill -u <appid> 2>/dev/null || true
sleep 1

# 停止并停用服务
systemctl stop <system_id>.service 2>/dev/null || true
systemctl disable <system_id>.service 2>/dev/null || true

exit 0
```

#### postrm — 卸载后

```bash
#!/bin/bash
set -e

# 重载 systemd
systemctl daemon-reload

# purge 时移除用户和数据
if [ "$1" = "purge" ]; then
    if id -u <appid> > /dev/null 2>&1; then
        userdel <appid> 2>/dev/null || true
    fi
    rm -rf /var/lib/<appid>
    rm -f /var/api/<appid>.sock
    # 移除 nginx 配置
    rm -f /etc/nginx/conf.d/<appid>.conf 2>/dev/null || true
    # 移除 systemd 服务文件
    rm -f /etc/systemd/system/<system_id>.service 2>/dev/null || true
    # 重载 systemd
    systemctl daemon-reload 2>/dev/null || true
fi

exit 0
```

### 8.15 打包与校验


**Deb 包文件名命名规范：**
- 单包模式：`<appid>_<version>_<arch>.deb`
  - 示例：`myapp_1.0.0_amd64.deb`
- 数据包：`<appid>_<version>_all.deb`
  - 示例：`myapp_1.0.0_all.deb`
- 压缩包：`<appid>_<platform>.tar.gz`（双包模式包含两个 .deb 文件）
  - 示例：`weather_x86_64.tar.gz`
  - 命名规则：`config.ini.id_config.ini.platform.tar.gz`

**Lintian 校验要求：**
- 所有 `Error` (E) 级别问题必须在提交前修复
- `Warning` (W) 级别问题应审查；平台关键警告必须修复
- `Info` (I) 级别问题为信息性，可选处理
- 仅对已记录、有意的偏差使用 `lintian --suppress-tags=<tag>`

**双包压缩包结构：**
`.tar.gz` 压缩包必须具有以下结构：
```
<appid>_<platform>.tar.gz
├── <appid>.deb              # 应用数据包（建议 config.ini.id 保持一致）
└── <package>.deb            # deb源包（名称默认即可，无需修改）
```
压缩包根目录不得包含子目录 — `.deb` 文件必须位于压缩包根级别。

**说明：**
- `<appid>.deb`：deb数据包，通过当前包可以在应用中心对包进行展示操作等
- `<package>.deb`：deb源包，用于完成deb服务功能

#### 方式一：单包模式

**步骤1：构建 Deb 包**

```bash
dpkg-deb --build ./<应用根目录> ./<appid>_<version>_amd64.deb
```

**步骤2：校验包**

```bash
dpkg-deb -c <appid>_<version>_amd64.deb
dpkg-deb -I <appid>_<version>_amd64.deb
lintian <appid>_<version>_amd64.deb  # 如有 lintian
```

**步骤3：生成校验和**

```bash
sha256sum <appid>_<version>_amd64.deb > <appid>_<version>_amd64.deb.sha256
```

**步骤4：测试安装**

```bash
sudo dpkg -i <appid>_<version>_amd64.deb
sudo systemctl status <system_id>
sudo dpkg --purge <appid>    # 卸载
```

---

#### 方式二：双包模式

**步骤1：构建deb源包**

```bash
dpkg-deb --build ./<应用根目录> ./<package>.deb
```

**步骤2：构建deb数据包**

```bash
mkdir -p /tmp/<appid>/DEBIAN
mkdir -p /tmp/<appid>/usr/local/<appid>

# 复制 TOS7.0 配置文件到数据包
cp config.ini /tmp/<appid>/usr/local/<appid>/
cp <appid>.lang /tmp/<appid>/usr/local/<appid>/
cp -r images /tmp/<appid>/usr/local/<appid>/
# 如果是外部打开，还需复制 nginx 配置
cp -r nginx /tmp/<appid>/usr/local/<appid>/ 2>/dev/null || true

# 创建 DEBIAN/control（参见 8.13.2）
# ...

# 构建数据包
dpkg-deb --build /tmp/<appid> ./<appid>.deb
```

**步骤3：打包提交压缩文件**

```bash
tar -czf <appid>_<platform>.tar.gz <appid>.deb <package>.deb
```

**步骤4：校验、校验和、测试安装**

```bash
# 校验
dpkg-deb -c <package>.deb && dpkg-deb -I <package>.deb
dpkg-deb -c <appid>.deb && dpkg-deb -I <appid>.deb

# 校验和
sha256sum <appid>_<platform>.tar.gz > <appid>_<platform>.tar.gz.sha256

# 测试安装
sudo dpkg -i <package>.deb
sudo dpkg -i <appid>.deb
sudo systemctl status <system_id>
```

### 8.16 完整示例

#### 示例1：WebUI 内部打开 — 计时器应用

**应用概览：**
- ID：`tmrtimer`
- 类型：Deb 应用 / WebUI 内部打开（iframe）
- 运行时：Python3 HTTP 服务（Unix Socket 模式）
- 前端：静态 HTML 计时器页面

**目录结构：**

```
/usr/local/tmrtimer/
├── config.ini
├── tmrtimer.lang
├── webui.bz2
├── images/
│   └── icons/
│       └── tmrtimer.svg
└── init.d/
    └── tmrtimer.service
```

**config.ini：**

```json
{
  "id": "tmrtimer",
  "icon": "/images/icons/tmrtimer.svg",
  "exec": true,
  "version": "1.0.0",
  "category": ["Utilities"],
  "platform": "x86_64",
  "system_id": "tmrtimer",
  "package": "tmrtimer",
  "application_type": "deb",
  "path": "/tmrtimer/",
  "type": "iframe",
  "resize": true,
  "maxmin": true
}
```

**DEBIAN/control：**

```
Package: tmrtimer
Version: 1.0.0
Architecture: amd64
Section: utils
Priority: optional
Maintainer: ljw <ljw@example.com>
Depends: python3 (>= 3.10), systemd
Description: 计时器应用
 一个简单的定时器工具，支持启动、暂停和重置功能。
```

---

#### 示例2：WebUI 外部打开 — 天气应用

**应用概览：**
- ID：`weather`
- 类型：Deb 应用 / WebUI 外部打开（新标签页）
- 运行时：Go 后端服务，端口 16688
- 前端：静态天气页面

**目录结构：**

```
/usr/local/weather/
├── config.ini
├── bin/
│   └── weather                  # Go 二进制
├── weather.lang
├── webui.bz2
├── images/
│   └── icons/
│       └── weather.svg
├── nginx/
│   └── weather.conf
└── init.d/
    └── weather-system.service
```

**config.ini：**

```json
{
  "id": "weather",
  "icon": "/images/icons/weather.svg",
  "exec": true,
  "version": "1.0.001",
  "category": ["Utilities"],
  "platform": "x86_64",
  "system_id": "weather-system",
  "package": "weather-package",
  "application_type": "deb",
  "path": "/weather/",
  "open_path": true
}
```

**nginx/weather.conf：**

```nginx
location /weather/ {
    proxy_pass http://127.0.0.1:16688/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

#### 示例3：无 UI 服务 — 数据同步服务

**应用概览：**
- ID：`datasync`
- 类型：Deb 应用 / 无 UI 服务
- 运行时：Python3 后台服务

**目录结构：**

```
/usr/local/datasync/
├── config.ini
├── bin/
│   └── datasync                  # 可执行文件
├── datasync.lang
├── images/
│   └── icons/
│       └── datasync.svg
└── init.d/
    └── datasync.service
```

**config.ini：**

```json
{
  "id": "datasync",
  "icon": "/images/icons/datasync.svg",
  "exec": true,
  "version": "1.0.0",
  "category": ["Utilities"],
  "platform": "x86_64",
  "system_id": "datasync",
  "package": "datasync",
  "application_type": "deb"
}
```

### 8.17 双包模式规范

双包模式下，原应用安装包（deb源包）保持不变，额外提供一个应用数据包（deb数据包）。deb数据包包含 TOS7.0 所需的配置文件，两者打包为 tar.gz 压缩包提交。

**数据包命名规则：** `<appid>.deb`（建议与 config.ini.id 保持一致，全小写）

**数据包内部文件结构：**

```
<appid>.deb
├── DEBIAN/
│   ├── control
│   └── postinst
└── usr/
    └── local/
        └── <appid>/
            ├── config.ini
            ├── <appid>.lang
            ├── images/
            │   └── icons/
            │       └── <appid>.svg
            ├── webui.bz2             # WebUI 应用需要
            └── nginx/                # 仅外部打开需要
                └── <appid>.conf
```

**数据包 DEBIAN/postinst：**

```bash
#!/bin/bash
set -e

# 确保配置文件权限正确
chmod 644 /usr/local/<appid>/config.ini 2>/dev/null || true
chmod 644 /usr/local/<appid>/<appid>.lang 2>/dev/null || true
chmod 644 /usr/local/<appid>/images/icons/<appid>.svg 2>/dev/null || true

exit 0
```

**数据包 config.ini 注意事项：**
- `icon` 路径固定为 `/images/icons/<appid>.svg`（与数据包图标文件名一致）
- `id` 与 config.ini 中的 `id` 字段完全一致
- `version` 与源包元数据的 `Version` 完全一致
- `application_type` 必须填写 `deb-TarGz`
- `package` 必须与数据包 DEBIAN/control 中的 `Package` 字段一致

**源包内部文件结构：**

```
<package>.deb
├── DEBIAN/
│   ├── control
│   ├── preinst
│   ├── postinst
│   ├── prerm
│   └── postrm
└── usr/
    └── local/
        └── <appid>/
            ├── bin/
            │   └── <binary_name>
            ├── depends/             # 如有依赖
            │   ├── bin/
            │   ├── lib/
            │   └── ...
            └── init.d/
                └── <system_id>.service
```

**提交压缩包结构：**

```
<appid>_<platform>.tar.gz
├── <appid>.deb              # deb数据包
└── <package>.deb            # deb源包
```

**GitHub 仓库数据结构（双包模式）：**

```
<appid>_<platform>.tar.gz
├── <appid>.deb              # 应用数据包
└── <package>.deb            # deb源包（原应用安装包）
```


**双包模式强制约束：**

| 约束 | 说明 | 违规后果 |
|---|---|---|
| **安装顺序** | 必须先安装源包（`<package>.deb`），再安装数据包（`<appid>.deb`）。数据包依赖源包。 | 安装失败 |
| **版本强一致** | 两个包的 `Version` 必须完全相同。任何版本不匹配将触发自动驳回。 | 自动驳回（E006） |
| **数据包禁止二进制** | 数据包（`<appid>.deb`）**严禁包含任何可执行二进制文件**、编译代码或系统特定库。仅允许配置文件、图标、语言文件、nginx配置等静态资源。 | 自动驳回（E019） |
| **数据包架构** | 数据包 `Architecture` 必须为 `all`，不可写为 `amd64` 或 `arm64`。配置文件与架构无关。 | 自动驳回 |
| **源包独立性** | deb源包必须可以独立在TOS7.0系统上使用 `dpkg -i` 命令进行安装。 | 安装失败 |
| **依赖声明** | 数据包的 `Depends` 字段必须写上源包包名，建议和版本一起指定。 | 驳回 |
| **Systemd 服务文件归属** | systemd 服务文件（`.service`）必须放在源包中，数据包不可包含。数据包仅负责 TOS 平台配置与展示。 | 驳回 |
| **卸载顺序** | 卸载时先卸载数据包，再卸载源包。数据包卸载不影响源包的运行数据。 | — |

**安装与卸载流程：**
```bash
# 安装顺序
sudo dpkg -i <package>.deb                    # 1. 先安装deb源包
sudo dpkg -i <appid>.deb                      # 2. 再安装deb数据包

# 卸载顺序  
sudo dpkg --remove <appid>                    # 1. 先卸载数据包
sudo dpkg --purge <package>                   # 2. 再卸载源包
```


## 9. Docker 应用开发

### 9.1 概述

Docker 应用运行在 TOS7 内置 Docker 引擎管理的容器中。通过 `docker-compose.yml` 文件定义，需要在 TNAS 设备上安装 DockerEngine 应用。

**核心要求：**
- 必须提供兼容 Compose Spec 3.8+ 的 `docker-compose.yml`
- 数据必须通过卷挂载持久化到 NAS 可访问目录
- 严禁使用特权模式
- 禁止占用系统核心端口（22、80、443、8181、5050）

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
    volumes:
      - /volume1/docker/<appid>/config:/config
      - /volume1/docker/<appid>/data:/data
    ports:
      - "<宿主端口>:<容器端口>"
    environment:
      - TZ=Asia/Shanghai
    user: "1000:1000"
```

**规则：**

1. **版本**：必须兼容 Compose Spec 3.8 及以上
2. **数据持久化**：所有数据目录必须挂载到宿主路径。仅存储在容器内的数据会在容器删除时丢失。
3. **端口映射**：
   - 禁用端口：22、80、443、8181、5050（系统服务）
   - 推荐范围：8000-19999
   - 提交前确认所选端口在 TNAS 上未被占用
4. **特权模式**：**严禁使用**。必须使用 `user` 字段指定 UID/GID。
5. **时区**：默认配置 `TZ=Asia/Shanghai`。用户可自行修改。
6. **容器名称**：必须与应用 `id` 一致
7. **重启策略**：普通服务使用 `unless-stopped`
8. **网络模式**：`network_mode: host` **严格禁止**，仅系统级网络工具除外。使用宿主机网络模式破坏容器隔离，存在安全风险。改用端口映射：
   ```yaml
   ports:
     - "8080:8080"
   ```
9. **时区**：容器时区必须显式配置：
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
   | 1（首选） | Docker Hub 官方项目镜像 | `linuxserver/jellyfin`、`plexinc/pms-docker` |
   | 2 | Docker Hub 已验证发布者 | 带 Verified badge 的 Docker Hub 镜像 |
   | 3 | Docker Hub 知名社区镜像 | Docker Hub 上 100M+ 拉取量、活跃维护的镜像 |
   | ❌ 驳回 | 非 Docker Hub 来源的镜像 | 私有仓库、ghcr.io、quay.io 等 |
   | ❌ 驳回 | Docker Hub 上未经验证的个人镜像 | 拉取量少、无文档的 Docker Hub 镜像 |

   > **强制要求：** 镜像必须托管在 Docker Hub 上。审核时将验证镜像来源。使用非 Docker Hub 镜像将被直接驳回。

   来自非 Docker Hub 来源或未经验证的 Docker Hub 镜像将在安全审核中被驳回。
2. **镜像体积**：使用多阶段构建或 Alpine 基础镜像以减小体积。
3. **敏感信息**：禁止在镜像或 compose 文件中硬编码密码、Token 或密钥。使用环境变量或 `.env` 文件。
4. **安全扫描**：提交前运行 `docker scan` 或 `trivy` 检查已知漏洞。
5. **用户权限**：**严禁使用 root 用户**。必须通过 `user` 字段指定非 root 用户。**严禁** `--privileged` 模式。

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
  "relation": [],
  "platform": "x86_64",
  "official": "https://example.com",
  "application_type": "docker",
  "system_id": "",
  "package": "",
  "user": "myapp",
  "all_user_display": true
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
    volumes:
      - /volume1/docker/myapp-docker/config:/config
      - /volume1/docker/myapp-docker/data:/data
    ports:
      - "8080:8080"
    environment:
      - TZ=Asia/Shanghai
      - PUID=1000
      - PGID=1000
```


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
| 备份配置 | `/volume1/docker/<appid>/config` | tar 或 rsync 备份 |
| 备份数据 | `/volume1/docker/<appid>/data` | tar 或 rsync 备份 |
| 迁移 | 全部 `/volume1/docker/<appid>/` | 复制到新设备，相同路径 |
| 重置为默认 | 停止容器 → 删除 `/volume1/docker/<appid>/config` → 重启 | 容器创建全新配置 |
| 完全删除数据 | 停止容器 → 删除 `/volume1/docker/<appid>/` | 所有数据永久删除 |

> 注意：配置和数据分开存储，支持独立备份/恢复。重大升级前务必备份。

---

## 10. 权限模型

### 10.0 SPC（系统权限控制）概述

TOS7 引入 **SPC（System Permission Control，系统权限控制）** 系统，遵循最小权限原则，对应用的系统访问行为进行管控：

- 应用无法直接修改系统文件或获取 root 权限，所有权限请求需通过平台 API 提交
- 开发者需在权限声明中明确应用的权限需求，平台审核通过后，应用才能获得对应访问权限
- 禁止任何绕过 SPC 权限检查的行为，此类应用将无法通过审核或被下架

### 10.1 概述

TOS7 遵循 **最小权限原则**。应用只能请求运行所必需的最小权限。TOS7 应用与 **SPC（系统权限控制）**系统交互。应用必须：
- 在权限声明（10.7 节）中声明权限需求
- 不得绕过 SPC 权限检查
- 使用平台 API 进行权限请求，而不是直接修改系统文件

平台为 Deb 和 Docker 应用提供结构化的权限模型。

### 10.2 用户与用户组模型

**⚠️ 严禁应用用户使用 root 权限。** 所有应用必须以非 root 专属用户运行。

**Deb 应用：**

| 场景 | 用户 | 说明 | 配置要求 |
|---|---|---|---|
| 专属用户 | `<appid>` | 必须使用。由 preinst 脚本创建。权限最小。 | **强制** |

> **强制要求：** 所有 Deb 应用必须创建专属用户（`<appid>`），并以该用户运行应用，严禁使用 root 权限。专属用户需在 `preinst` 脚本中创建，确保应用运行时权限最小化。应用数据目录（如 `/usr/local/<appid>`）的权限需设置为专属用户所有，避免权限不足或越权访问。

**创建专属用户：**
```bash
# 在 preinst 中
useradd --system --no-create-home --shell /usr/sbin/nologin <appid>
```

**Docker 应用：**

| 场景 | 用户 | 说明 |
|---|---|---|
| 非 root | `UID:GID`（如 `1000:1000`） | **必须使用**。在 compose 中通过 `user` 字段指定。 |

### 10.3 文件系统权限

**Deb 应用的标准目录权限：**

| 路径 | 归属 | 权限 | 说明 |
|---|---|---|---|
| `/usr/local/<appid>/` | `<appid>:<appid>` | `755` | 应用目录（服务只读） |
| `/usr/local/<appid>/bin/` | `<appid>:<appid>` | `755` | 可执行文件 |
| `/usr/local/<appid>/config/` | `<appid>:<appid>` | `750` | 配置文件 |
| `/usr/local/<appid>/site/` | `<appid>:<appid>` | `755` | Web UI 文件 |
| `/var/lib/<appid>/` | `<appid>:<appid>` | `750` | 运行时数据（读写） |
| `/var/log/<appid>/` | `<appid>:<appid>` | `750` | 应用日志 |

> **规则：** 应用二进制和配置对服务用户应为只读。只有数据和日志目录应为可写。

### 10.4 网络权限

| 权限 | Deb 应用 | Docker 应用 | 说明 |
|---|---|---|---|
| 绑定端口 | 在服务配置中绑定指定端口 | 在 compose 中映射端口 | 不得与系统端口冲突 |
| 访问本地服务 | 默认允许 | 使用 `network_mode: host` 或显式链接 | 尽量减少网络暴露 |
| 出站连接 | 允许 | 允许 | 出站无限制 |

### 10.5 共享文件夹访问

TNAS 共享文件夹是主要的数据访问机制。需要访问用户数据的应用必须：

1. **创建共享文件夹**，通过 `ter_share_add`：
```bash
ter_share_add -name <appid>-data -owner <appid>
```

2. **或请求访问现有共享文件夹**，通过加入 `allusers` 组：
```bash
usermod -aG allusers <appid>
```

3. **Docker 应用**通过卷挂载共享文件夹：
```yaml
volumes:
  - /volume1/<共享文件夹>:/data:rw    # 读写访问
  - /volume1/<共享文件夹>:/media:ro   # 只读访问
```

> **重要：** 应用不得直接修改共享文件夹权限。使用 TOS 共享文件夹管理 API 或让用户手动配置访问权限。


### 10.5.1 权限请求流程

当应用需要访问共享文件夹时：

1. **专用应用文件夹**（推荐）：
   - 在 postinst 中通过 `ter_share_add` 创建
   - 应用拥有完整的读写权限
   - 无需用户授权

2. **用户共享文件夹**（需要授权）：
   - 应用请求 `allusers` 组成员资格
   - 用户通过 TOS 共享文件夹设置授权文件夹访问
   - 应用在权限声明中注明只读或读写需求

3. **权限格式**：
   ```yaml
   # Docker 卷
   - /volume1/<共享文件夹>:/data:rw   # 读写访问
   - /volume1/<共享文件夹>:/media:ro  # 只读访问
   ```

### 10.6 系统资源限制


**按应用类型的默认资源配额：**

> 说明：以下磁盘限制仅针对**应用在系统盘（/）的运行时占用**，应用的业务数据需存储在 `/Volume*`（数据盘）中，数据盘无存储容量限制，可支持 TB 级数据存储。

| 应用类型 | CPU 限制 | 内存限制 | 系统盘限制 | 示例 |
|---|---|---|---|---|
| 媒体服务器 | 200% (2 核) | 2048M | 50GB | Jellyfin, Plex, Emby |
| 下载管理器 | 100% (1 核) | 512M | 20GB | Aria2, qBittorrent |
| 实用工具 | 50% | 256M | 10GB | 文件管理器, 文本编辑器 |
| Web 服务 | 100% (1 核) | 512M | 30GB | CMS, 博客, Wiki |
| 数据库 | 200% (2 核) | 2048M | 30GB | MySQL, PostgreSQL, Redis |
| 安全类 | 50% | 256M | 10GB | 防火墙, 杀毒软件 |

以上为平台默认值。开发者可在权限声明中附合理理由申请更高的系统盘限制；业务数据请务必存储在数据盘，不受此限制影响。

**Deb 应用（通过 systemd）：**
```ini
[Service]
# 内存限制
MemoryMax=512M
# CPU 配额（200% = 2核）
CPUQuota=200%
# 文件描述符限制
LimitNOFILE=65536
# 进程数限制
LimitNPROC=256
```

**Docker 应用（通过 compose）：**
```yaml
services:
  myapp:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 128M
```

### 10.7 权限声明

为保持透明，应用应在 README.md 中记录其权限需求：

```markdown


| 权限 | 理由 |
|---|---|
| 网络：端口 8686 | Web UI 访问 |
| 文件系统：/var/lib/tmrtimer | 运行时数据存储 |
| 用户：tmrtimer（系统用户） | 隔离的服务执行 |
| 共享文件夹：无 | 不需要用户数据访问 |
```


### 10.8 权限红线（自动驳回）

以下权限请求将导致 **自动驳回**：

| 违规行为 | 说明 |
|---|---|
| Root 执行 | 请求 `root` 用户运行应用 |
| 特权模式 | 请求 `--privileged` Docker 模式 |
| 系统目录写入 | 请求写入 `/etc/`、`/usr/`、`/boot/` 等系统目录 |
| 跨应用数据访问 | 请求访问其他应用的数据目录 |
| 无限制网络访问 | 无书面合理理由申请 `network_mode: host`（仅系统级网络工具可申请） |
| 过多端口暴露 | 请求超过功能所需的端口数量 |

---

## 11. 包签名与安全

### 11.1 包完整性

**Deb 包：**
- 所有 deb 包必须包含 MD5 校验和文件（由 dpkg-deb 自动生成）：
  ```
  DEBIAN/md5sums
  ```
- 开发者应在 deb 包旁提供 SHA-256 校验和：
  ```bash
  sha256sum <appid>_<version>_amd64.deb > <appid>_<version>_amd64.deb.sha256
  ```

**Docker 应用：**
- Docker 镜像应使用签名/摘要锁定引用：
  ```yaml
  image: myapp@sha256:<摘要>  # 优先于 :latest
  ```
- 使用 Docker Content Trust（DOCKER_CONTENT_TRUST=1）进行验证拉取

### 11.2 发布者信任

TNAS 开发者平台通过以下方式建立发布者信任：

1. **开发者账号验证**：注册需邮箱验证
2. **应用审核**：所有提交均经过人工安全审核
3. **发布者身份**：config.ini 中的 `publisher` 字段会展示给用户
4. **版本审计追踪**：所有版本提交均有日志记录且可追溯

> **未来计划：** 铁威马计划为 Deb 应用引入基于 GPG 密钥的包签名，并为容器镜像集成 Docker Content Trust。

**过渡期安全措施（GPG/DCT 实施前）：**
在完整的 GPG 签名和 Docker Content Trust 实施之前，以下过渡期措施适用：
1. 所有提交必须为每个二进制产物附带 SHA-256 校验和文件
2. 平台对比上传包验证校验和
3. 校验和不匹配将导致自动驳回
4. 维护者必须在其仓库账户（GitHub/Gitee）上启用双重认证（2FA）

### 11.3 安全审计要求

所有应用在审核期间均需通过安全审计：

| 检查项 | Deb 应用 | Docker 应用 |
|---|---|---|
| 无硬编码凭据 | ✅ | ✅ |
| 严禁 root 权限 | ✅ | ✅ |
| 无特权模式（严禁） | N/A | ✅ |
| 无全局可写文件 | ✅ | N/A |
| 仅声明所需依赖 | ✅ | ✅ |
| 无过度资源消耗 | ✅ | ✅ |
| 漏洞扫描 | 可选 | 推荐 `docker scan` / `trivy` |
| 无脚本注入漏洞 | ✅ | ✅ |
| 无路径遍历漏洞 | ✅ | ✅ |
| 日志中无敏感信息 | ✅ | ✅ |
| 校验和与上传产物匹配 | ✅ | ✅ |

### 11.4 供应链安全

**Deb 应用：**
- 在 DEBIAN/control 中声明精确的依赖版本
- 尽可能使用可复现的构建过程
- 不要捆绑不必要的文件或库

**Docker 应用：**
- 镜像标签锁定为特定版本或摘要（避免 `:latest`）
- 使用多阶段构建以减小攻击面
- 定期更新基础镜像以包含安全补丁
- 不在生产镜像中包含开发工具

---

## 12. 最佳实践

### 12.1 应用目录布局

遵循一致的目录布局以确保可维护性和兼容性：

```
/usr/local/<appid>/
├── <binary>        # 应用可执行文件
├── config.ini      # 应用配置文件
├── <appid>.lang    # 语言文件
├── images/         # 图标资源
├── webui.bz2       # 前端页面压缩包（WebUI 应用）
├── nginx/          # Nginx 配置（外部打开应用）
└── init.d/         # Systemd 服务文件

/var/lib/<appid>/   # 运行时数据（可写）
/var/log/<appid>/   # 应用日志
/var/api/           # Unix Socket 目录（WebUI 内部打开）
```


**官方应用与第三方应用目录差异：**

| 目录 | 官方应用 | 第三方应用 |
|---|---|---|
| 安装基础路径 | `/usr/local/<appid>/` | `/usr/local/<appid>/` |
| 数据存储 | `/home/<appid>/` 或 `/Volume*/` | `/var/lib/<appid>/` 或 `/Volume*/` |
| 日志存储 | TOS 管理 | `/var/log/<appid>/` |
| Systemd 单元路径 | `/etc/systemd/system/<appid>.service` | `/etc/systemd/system/<system_id>.service` |

**数据存储建议：**
- **建议将数据存储在 `/usr/local/<app_id>` 内，或者 `/Volume*` 内**
- 运行时可变数据建议使用 `/var/lib/<appid>/`
- 日志输出使用 `/var/log/<appid>/`

### 12.2 数据持久化

**Deb 应用：**
1. 持久化数据建议存储在 `/usr/local/<appid>` 或 `/Volume*` 下
2. 需要NAS可访问的数据，创建共享文件夹：
   ```bash
   ter_share_add -name <appid>-data -owner <appid>
   ```
3. 如需要可创建符号链接：
   ```bash
   ln -s /volume1/<appid>-data /usr/local/<appid>/data
   ```
4. 运行时数据存储在 `/var/lib/<appid>/`

**Docker 应用：**
1. 通过卷挂载所有持久化数据目录：
   ```yaml
   volumes:
     - /volume1/docker/<appid>/config:/config
     - /volume1/docker/<appid>/data:/data
   ```
2. 禁止在容器文件系统中存储数据
3. 配置和数据使用独立卷，以支持独立备份

### 12.3 日志

**Deb 应用：**
```bash
# 使用 systemd 日志（推荐）
# 服务的所有 stdout/stderr 自动被捕获
# 查看日志：journalctl -u <appid>

# 或写入文件
exec >> /var/log/<appid>/app.log 2>&1
```

**Docker 应用：**
```yaml
services:
  myapp:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

**最佳实践：**
- 使用结构化日志（推荐 JSON 格式）
- 每条日志包含时间戳、级别和上下文
- 轮转日志防止磁盘耗尽
- 禁止在日志中记录敏感信息（密码、Token、个人数据）


**日志保留与清理：**

| 日志类型 | 最长保留时间 | 清理方式 |
|---|---|---|
| 应用日志（文件） | 30 天 | Logrotate：每日轮转，保留 30 个文件 |
| Systemd 日志 | 平台管理 | 通过 journald 限制自动管理 |
| Docker 容器日志 | 每文件 10MB，共 3 文件 | Docker 日志驱动配置 |

**Logrotate 配置：**
```
/var/log/<appid>/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

### 12.4 资源限制

| 资源 | Deb 应用（systemd） | Docker 应用（compose） |
|---|---|---|
| 内存 | `MemoryMax=512M` | `memory: 512M` |
| CPU | `CPUQuota=200%` | `cpus: '2.0'` |
| 文件描述符 | `LimitNOFILE=65536` | N/A（容器级别） |
| 进程数 | `LimitNPROC=256` | N/A（容器级别） |
| 磁盘 | N/A（使用配额） | 卷大小限制 |

**指导原则：**
- 根据预期工作负载设置资源限制，而非最大可能用量
- 在典型用量基础上预留 20-30% 的峰值缓冲
- 在 README.md 中记录资源需求

### 12.5 健康检查

**Deb 应用：**
```ini
# 在 systemd 服务文件中
[Service]
# 故障自动重启
Restart=on-failure
RestartSec=5
StartLimitBurst=3
StartLimitIntervalSec=60

# 看门狗（如应用支持）
WatchdogSec=30
```

**Docker 应用：**
```yaml
services:
  myapp:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

### 12.6 升级与迁移

**Deb 应用：**
1. 在 `postinst` 中始终检查旧版本：
   ```bash
   if [ -n "$2" ]; then
       # 从 $2 升级 — 运行迁移
       /usr/local/<appid>/bin/migrate --from "$2"
   fi
   ```
2. 升级过程中绝不删除用户数据
3. 修改配置格式前先备份
4. 迁移逻辑应可逆以支持回滚
5. **建议用户将数据存储在 `/usr/local/<app_id>` 内，或者 `/Volume*` 内**，确保升级后数据不丢失

**Docker 应用：**
1. 使用入口脚本检测和迁移旧数据格式：
   ```bash
   #!/bin/bash
   if [ -f /config/version ]; then
       OLD_VERSION=$(cat /config/version)
       if [ "$OLD_VERSION" != "$NEW_VERSION" ]; then
           /app/migrate.sh "$OLD_VERSION" "$NEW_VERSION"
       fi
   fi
   echo "$NEW_VERSION" > /config/version
   ```
2. 至少测试最近2个大版本的升级路径

### 12.7 安全加固

**Deb 应用：**
```ini
[Service]
# 丢弃所有能力，仅添加所需
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=true

# 文件系统保护
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/<appid> /var/log/<appid>

# 网络命名空间（可选）
# PrivateNetwork=true  # 仅当不需要网络时

# 用户命名空间
# PrivateUsers=true
```

**Docker 应用：**
```yaml
services:
  myapp:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # 仅当需要绑定1024以下端口时
    read_only: true
    tmpfs:
      - /tmp
      - /run
```


> **必须（所有提交必须包含）：**
> - `NoNewPrivileges=true`
> - `ProtectSystem=strict`
> - `ProtectHome=true`
> - `ReadWritePaths`（仅显式路径）
> - 非 root `User`/`Group`
>
> **建议（强烈建议）：**
> - `AmbientCapabilities`（仅需的能力）
> - `LimitNOFILE`、`LimitNPROC`
> - `PrivateTmp=true`
> - `PrivateDevices=true`
>
> **可选（高级加固）：**
> - `PrivateNetwork=true`（仅在不需要网络时）
> - `PrivateUsers=true`
> - `MemoryDenyWriteExecute=true`

### 12.8 应用端口分配

**规则：**
1. 优先在推荐范围 **8000-19999** 内选择端口（共 12000 个端口，大幅降低冲突概率）
2. 若推荐范围端口被占用，可使用 **49152-65535（动态端口范围）**，但需在配置中明确声明
3. 选择前检查常用端口避免冲突，通过环境变量使端口可配置
4. 在 README.md 中文档化端口使用

**端口范围说明：**
- **8000-19999**：为 TNAS 应用推荐端口段，避开系统核心服务端口（如22/80/443/8181），且数量充足，可满足绝大多数应用的端口需求
- **49152-65535**：为 IANA 定义的动态/私有端口段，适合临时或备用场景使用

**常用端口参考（避免使用）：**

| 端口 | 应用 |
|---|---|
| 22 | SSH |
| 80 | TOS Web（HTTP） |
| 443 | TOS Web（HTTPS） |
| 445 | SMB |
| 3306 | MySQL |
| 5050 | TOS 守护进程 |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 8096 | Jellyfin |
| 8181 | TOS Nginx |
| 8443 | TOS HTTPS |
| 9000 | Portainer |
| 9090 | Prometheus |


---

## 13. 本地测试与调试

提交应用前，必须在 TNAS 设备上全面测试完整生命周期。


**TOS7 开发环境快速搭建：**

1. **选项 A：Ubuntu 22.04 虚拟机（推荐）**
   - 下载 VirtualBox 或 VMware
   - 从 TNAS 开发者平台导入官方 TOS7 开发者虚拟机
   - 虚拟机包含预配置的 TOS7 工具和模拟服务

2. **选项 B：基于 Docker 的开发容器**
   ```bash
   docker run -it --name tos7-dev      -v $(pwd):/workspace      ubuntu:22.04 /bin/bash
   apt-get update && apt-get install -y dpkg-dev lintian systemd
   ```

3. **选项 C：物理 TNAS 设备（用于最终测试）**
   - 提交前必须在实际设备上进行最终验证
   - 必须运行 TOS 7.0 或更高版本
   - 开启 SSH 访问以进行调试

### 13.1 Deb 应用测试

```bash
# 1. 安装 deb 包
sudo dpkg -i <appid>_<version>_amd64.deb

# 2. 检查服务是否运行
sudo systemctl status <appid>

# 3. 查看服务日志（实时）
sudo journalctl -u <appid> -f

# 4. 查看近期日志
sudo journalctl -u <appid> --since "1 hour ago"

# 5. 检查 Web UI 是否可访问（Web 应用）
curl http://localhost:<端口>

# 6. 测试启停
sudo systemctl stop <appid>
sudo systemctl start <appid>
sudo systemctl restart <appid>

# 7. 测试卸载
sudo dpkg --remove <appid>       # 保留配置
sudo dpkg --purge <appid>        # 完全删除

# 9. 验证清理（无残留文件/服务）
systemctl list-unit-files | grep <appid>
ls /usr/local/<appid> 2>/dev/null
ls /var/lib/<appid> 2>/dev/null
id <appid> 2>/dev/null

# 10. 测试升级路径
sudo dpkg -i <appid>_0.9.0_amd64.deb   # 安装旧版本
# ... 添加一些数据 ...
sudo dpkg -i <appid>_1.0.0_amd64.deb   # 升级到新版本
# 验证数据已保留并迁移
```

### 13.2 Docker 应用测试

```bash
# 1. 确保 DockerEngine 已安装并运行
sudo systemctl status docker

# 2. 启动应用
docker-compose -f docker-compose.yml up -d

# 3. 检查容器状态
docker ps | grep <appid>

# 4. 查看容器日志（实时）
docker logs -f <appid>

# 5. 检查资源使用
docker stats <appid>

# 6. 检查 Web UI 是否可访问
curl http://localhost:<端口>

# 7. 测试停止/重启
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml up -d

# 8. 测试数据持久化
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml up -d
# 验证数据仍然存在

# 9. 测试健康检查
docker inspect --format='{{.State.Health.Status}}' <appid>

# 10. 清理
docker-compose -f docker-compose.yml down -v
```

### 13.3 开发者调试工具包


**一键调试脚本：**
保存为 `debug.sh` 并运行以验证你的应用：
```bash
#!/bin/bash
APPID="$1"
echo "=== TOS7 应用调试: $APPID ==="

echo "--- 服务状态 ---"
systemctl status "$APPID" 2>/dev/null || echo "未找到服务"

echo "--- 进程 ---"
ps aux | grep "$APPID" | grep -v grep

echo "--- 端口 ---"
ss -tlnp | grep "$APPID"

echo "--- 文件归属 ---"
ls -laR "/usr/local/$APPID/" 2>/dev/null

echo "--- 近期错误 ---"
journalctl -u "$APPID" -p err --since "10 minutes ago" --no-pager

echo "--- 磁盘使用 ---"
du -sh "/usr/local/$APPID/" "/var/lib/$APPID/" "/var/log/$APPID/" 2>/dev/null

echo "=== 调试完成 ==="
```

#### 服务调试

```bash
# 检查服务文件是否有效
systemd-analyze verify /etc/systemd/system/<appid>.service

# 检查服务依赖
systemd-analyze dump | grep -A5 <appid>

# 检查端口监听
ss -tlnp | grep <端口>

# 检查进程详情
ps aux | grep <appid>

# 检查文件归属
ls -laR /usr/local/<appid>/
ls -laR /var/lib/<appid>/

# 查看 systemd 错误日志
journalctl -u <appid> -p err

# 查看系统日志
grep <appid> /var/log/syslog
```

#### Docker 调试

```bash
# 进入运行中的容器
docker exec -it <appid> /bin/sh

# 检查容器详情
docker inspect <appid>

# 检查资源限制
docker stats --no-stream <appid>

# 检查网络
docker network ls
docker network inspect <网络名>

# 查看容器文件系统变更
docker diff <appid>

# 查看镜像层
docker history <镜像>
```

#### 快速开发循环

开发过程中快速迭代：

```bash
# Deb 应用：快速重装
sudo dpkg --purge <appid> && sudo dpkg -i <appid>_<version>_amd64.deb

# Docker 应用：快速重建
docker-compose down && docker-compose up -d --build

# 测试时同时查看日志
journalctl -u <appid> -f &   # Deb
docker logs -f <appid> &     # Docker
```

### 13.4 常见问题与解决方案

| 问题 | 可能原因 | 解决方案 |
|---|---|---|
| 服务启动失败 | 缺少依赖或路径错误 | 检查 `journalctl -u <appid>`，验证 `ExecStart` 路径 |
| 端口冲突 | 其他服务占用同一端口 | `ss -tlnp | grep <端口>`，更换可用端口 |
| 权限拒绝 | 文件归属或权限不正确 | 验证服务文件中的 `User`/`Group`，检查文件归属 |
| Web UI 不可访问 | 服务未监听或防火墙 | 检查服务是否运行，验证端口绑定（`0.0.0.0` 而非 `127.0.0.1`） |
| 容器立即退出 | 容器内应用错误 | `docker logs <appid>`，检查 entrypoint/command |
| 重启后数据丢失 | 未配置卷挂载 | 在 docker-compose.yml 中添加卷映射 |
| TOS 更新后应用异常 | ABI 变更或服务冲突 | 检查 `low_version`，在新 TOS 版本上测试 |
| 配置未加载 | 配置路径或权限错误 | 验证 WorkingDirectory 和配置文件路径 |
| 升级后配置权限丢失 | postinst 中未重新设置 chown/chmod | 在 postinst 脚本中添加 `chown -R <appid>:<appid>` |
| Socket 文件残留导致启动失败 | 上次运行未清理的 socket | 启动服务前添加 `rm -f /var/api/<appid>.sock` |
| Nginx 重载失败 | Nginx 配置语法无效 | 重载前用 `nginx -t` 验证 |
| Docker 卷权限不正确 | 宿主机与容器 UID/GID 不匹配 | 使用与宿主机用户匹配的 `PUID`/`PGID` 环境变量 |
| 网络就绪前服务启动 | systemd 单元缺少 `After=network.target` | 添加 `After=network.target` 和 `Wants=network.target` |
| Deb 因未满足依赖而无法安装 | DEBIAN/control 缺少 Depends | 在 `Depends` 字段中声明所有必需的软件包 |

---

---

## 14. CI/CD 指南

### 14.1 GitHub Actions 模板


**必需的仓库 Secrets：**
在 GitHub 仓库 Settings → Secrets and Variables → Actions 中配置：

| Secret 名称 | 说明 | 是否必需 |
|---|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub 用户名（用于推送镜像） | Docker 应用需要 |
| `DOCKERHUB_TOKEN` | Docker Hub 访问令牌（非密码） | Docker 应用需要 |
| `GPG_PRIVATE_KEY` | GPG 私钥用于包签名（未来） | 可选 |
| `GPG_PASSPHRASE` | GPG 密钥密码 | 可选 |

> 切勿在工作流文件中硬编码凭据。始终使用 GitHub Secrets。

**Deb 应用**使用以下 GitHub Actions 工作流：

```yaml
# .github/workflows/build-deb.yml
name: 构建 Deb 包

on:
  push:
    tags:
      - 'v*'
  pull_request:
    branches: [main]

jobs:
  build:
    strategy:
      matrix:
        arch: [amd64, arm64]
        include:
          - arch: amd64
            runner: ubuntu-latest
          - arch: arm64
            runner: ubuntu-latest

    runs-on: ${{ matrix.runner }}

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 设置 QEMU（arm64）
        if: matrix.arch == 'arm64'
        uses: docker/setup-qemu-action@v3

      - name: 安装构建依赖
        run: |
          sudo apt-get update
          sudo apt-get install -y dpkg-dev debhelper lintian

      - name: 构建 deb 包
        run: |
          dpkg-deb --build ./app-root ./<appid>_${{ github.event.release.tag_name }}_${{ matrix.arch }}.deb

      - name: 校验包
        run: |
          dpkg-deb -c ./*.deb
          dpkg-deb -I ./*.deb
          lintian ./*.deb || true

      - name: 生成校验和
        run: |
          sha256sum ./*.deb > ./*.deb.sha256

      - name: 上传产物
        uses: actions/upload-artifact@v4
        with:
          name: deb-${{ matrix.arch }}
          path: |
            *.deb
            *.sha256

  release:
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')

    steps:
      - name: 下载产物
        uses: actions/download-artifact@v4

      - name: 创建 GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            deb-amd64/*.deb
            deb-amd64/*.sha256
            deb-arm64/*.deb
            deb-arm64/*.sha256
```

### 14.2 多架构构建

**Docker 应用**：

```yaml
# .github/workflows/build-docker.yml
name: 构建并推送 Docker 镜像

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 设置 QEMU
        uses: docker/setup-qemu-action@v3

      - name: 设置 Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: 登录 Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: 构建并推送
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/<appid>:latest
            ${{ secrets.DOCKERHUB_USERNAME }}/<appid>:${{ github.ref_name }}

      - name: 安全扫描
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: '${{ secrets.DOCKERHUB_USERNAME }}/<appid>:${{ github.ref_name }}'
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
```

### 14.3 自动化校验

添加校验工作流，每次推送时检查配置文件：

```yaml
# .github/workflows/validate.yml
name: 校验配置

on:
  push:
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 校验 config.ini（JSON格式）
        run: |
          python3 -c "import json; json.load(open('config.ini'))"
          echo "config.ini JSON 格式有效"

      - name: 校验必填字段
        run: |
          python3 -c "
          import json
          config = json.load(open('config.ini'))
          required = ['id', 'icon', 'publisher', 'exec', 'version', 'low_version',
                      'category', 'depend', 'platform', 'application_type', 'user',
                      'all_user_display']
          for field in required:
              assert field in config, f'缺少必填字段: {field}'
          
          # 校验 Deb 专属字段
          if config['application_type'] == 'deb':
              assert config.get('system_id'), 'Deb 应用必须有 system_id'
              assert config.get('package'), 'Deb 应用必须有 package'
          
          # 校验分类数量
          assert len(config['category']) <= 3, '最多3个分类'
          
          print('所有校验通过！')
          "

      - name: 校验 app.lang（14种语言）
        run: |
          python3 -c "
          required_langs = ['zh-cn', 'zh-hk', 'en-us', 'fr-fr', 'de-de', 
                           'it-it', 'es-es', 'hu-hu', 'ja-jp', 'ko-kr',
                           'pl-pl', 'ru-ru', 'tr-tr', 'pt-pt']
          with open('app.lang', 'r') as f:
              content = f.read()
          for lang in required_langs:
              assert f'[{lang}]' in content, f'缺少语言: {lang}'
          print('14种语言全部存在！')
          "

      - name: 校验图标（SVG 格式）
        run: |
          python3 -c "
          import json, os
          config = json.load(open('config.ini'))
          icon_path = config['icon']
          icon_file = icon_path.lstrip('/')
          assert os.path.exists(icon_file), f'图标未找到: {icon_file}'
          with open(icon_file, 'r') as f:
              content = f.read()
          assert '<svg' in content and '</svg>' in content, '不是有效的 SVG 文件'
          assert 'viewBox' in content, 'SVG 缺少 viewBox 属性'
          print(f'图标校验通过: {icon_file}')
          "

```

> **Gitee Actions（中国开发者）：** 对于在 Gitee 上托管的开发者，请将 GitHub Actions 工作流适配为 Gitee CI/CD 格式。完整的 Gitee CI/CD 模板可在 TNAS 开发者平台上获取。Gitee 使用 `gitee-ci.yml` 配置格式。请参阅 Gitee 文档了解环境设置。

### 14.4 发布与上传

构建成功后：

1. 创建包含 deb 包和校验和的 GitHub Release
2. 如需要，更新仓库的 config.ini 和 app.lang
3. 通过 TNAS 开发者平台提交新版本
4. 将 Release 标签与版本提交关联

---

## 15. 上架流程

### 15.1 详细操作流程

#### 第一步：注册开发者账号

1. 访问 TNAS 开发者平台：https://developer.terra-master.com
2. 点击【注册】按钮，进入注册信息填写页面
3. 使用有效电子邮箱作为登录账号，填写开发者姓名（建议与配置文件中的 publisher 保持一致）
4. 阅读并同意服务协议，点击【确定】完成注册
5. 注册后无需等待审核，账号即时生效

> **注意：** 账号邮箱用于接收审核结果通知、密码重置等重要信息，请保持邮箱有效。

#### 第二步：下载配置模板与开发应用

1. 从 TNAS 开发者平台下载官方配置模板（config.ini、app.lang、systemd 服务文件等）
2. 按照本文档规范完成应用开发与封装
3. 本地测试验证（参见第13章）

#### 第三步：创建公开仓库

1. 在 GitHub 或 Gitee 上创建公开仓库
2. 上传所有必需文件（配置文件、应用包、图标、README.md 等）
3. **Deb 应用** — 上传 `<appid>_<platform>.tar.gz` 压缩包（内含 `<appid>.deb` 数据包和 `<package>.deb` 源包）
4. **Docker 应用** — 上传 `docker-compose.yml`、`config.ini`、`app.lang` 和图标文件
5. 附带 SHA-256 校验和文件

#### 第四步：在开发者平台创建应用

1. 登录开发者平台，点击【我的应用】→【新增应用】
2. 填写应用信息：
   - **应用 ID**：与 config.ini 中的 `id` 字段完全一致
   - **应用包类型**：选择 Docker 类或 deb 包类
   - **仓库地址**：填写公开仓库地址（必须公开，否则审核无法进行）
3. 确认无误后提交创建

#### 第五步：新增应用版本

1. 在【我的应用】中找到目标应用，点击【版本管理】
2. 点击【新增版本】，填写版本号
   - 版本号格式：严格遵循 `xx.yy.zzz`（主版本号.次版本号.修订号）
   - 不可重复使用历史版本号
   - 必须与 config.ini 中的 `version` 字段一致
3. 提交版本后进入上架申请流程

#### 第六步：平台自动校验

提交后平台自动执行以下检查：
- 文件格式校验（config.ini JSON 语法、app.lang 格式）
- 字段完整性校验（必填字段无缺失）
- 语言覆盖校验（14 种语言节点全部存在）
- 图标校验（SVG 格式、路径匹配）
- 校验和验证（SHA-256 与上传文件匹配）
- 版本一致性校验（config.ini / DEBIAN/control / app.lang 版本匹配）

**自动校验失败的常见原因：**
- config.ini 包含注释或语法错误（E002）
- app.lang 缺少语言节点（E007）
- 图标未找到或格式错误（E009）
- 校验和不匹配（E013）

#### 第七步：人工审核

审核团队从四个维度进行审核（详见第16章）：
1. **配置完整性**（权重 30%）：所有必需文件齐全，格式正确
2. **功能可用性**（权重 35%）：安装、启动、运行、卸载完整无异常
3. **安全性**（权重 25%）：无恶意代码、无过度授权、无敏感硬编码
4. **合规性**（权重 10%）：内容合规，描述与功能一致

审核流程：初审（信息一致性、仓库规范性）→ 安全性审核（技术支持人员）→ 功能兼容性测试（测试支持人员）→ 综合审核（专职审核人员）

#### 第八步：审核结果通知

审核结果通过两种渠道通知开发者：
- **平台消息**：登录开发者平台可查看审核状态
- **注册邮箱**：审核结果发送至注册时使用的邮箱

审核状态说明：
- **审核中**：应用正在审核队列中
- **审核通过**：应用已通过审核，进入上架流程
- **审核驳回**：应用存在问题需整改，需在 30 天内修正并重新提交
- **自主撤回**：开发者主动撤回审核申请

#### 第九步：正式上架

审核通过后，应用将在 1-2 个工作日内上线至 TNAS 应用中心：
- 用户可在应用中心搜索并安装应用
- 开发者可在【我的应用】中查看应用状态变更为"已上架"

> **统计信息：** 开发者主页展示已发布应用数、应用总下载量、累计提交应用数等核心数据。最近 3 条上架申请进展情况实时更新。

### 15.2 仓库要求

- 必须为 **公开仓库**（GitHub 或 Gitee）。私有仓库不予支持。
- 必须包含所有必需的配置文件和应用资源。
- Deb 应用需提交 `tar.gz` 压缩包，内含 `<appid>.deb` 数据包和 `<package>.deb` 源包。
- Docker 应用需提交 `docker-compose.yml`、`config.ini`、`app.lang` 和图标文件。
- 仓库资源需长期保持可用。不可删除已上架的资源。
- 仓库结构必须符合指定的目录布局。
- 所有二进制产物需附带 SHA-256 校验和文件。

**应用更名和 ID 变更政策：**
- 应用 `id`（config.ini 中）一旦发布**不可更改**
- 应用展示名称（app.lang 中）可在新版本中更新
- 如需更改应用 `id`，必须作为全新应用提交（新上架、新审核）
- 旧应用必须走应用下架流程（参见 17.4 节）

---

## 16. 审核标准

### 16.1 四大审核维度

| 维度 | 审核内容 | 审核人 |
|---|---|---|
| **配置完整性** | config.ini JSON 格式正确、app.lang 14 种语言齐全、图标 SVG 规范、必填字段无缺失、systemd 服务文件有效 | 专职审核人员 |
| **功能可用性** | 安装/启动/停止/卸载完整无异常、架构适配正确、功能与描述一致、端口可用无冲突 | 测试支持人员 |
| **安全性** | 无硬编码凭据、非 root 运行、无特权模式、无恶意代码、无漏洞、无违规脚本、哈希值校验通过 | 技术支持人员 |
| **合规性** | 内容合法合规、不侵犯知识产权、描述与功能相符、仓库为公开状态、目录结构规范 | 专职审核人员 |

### 16.2 审核流程

#### 16.2.1 初审阶段
1. 专职审核人员登录应用管理平台（https://mgmt.terra-master.com），领取"待初审"任务
2. 下载待审核的应用包，获取基准 SHA-256 哈希值并记录
3. 验证信息一致性：开发者提交的应用信息与 GitHub/Gitee 仓库内容一致
4. 验证仓库规范性：仓库为公开状态、目录结构完整、无冗余违规文件
5. 知识产权合规检查：不侵犯 TerraMaster 或第三方知识产权

**初审结果：**
- ✅ 通过 → 应用状态更新为"待人工审核"，进入人工审核阶段
- ❌ 驳回 → 详细填写驳回原因，双渠道通知开发者整改

#### 16.2.2 哈希值流转验证
所有审核岗位人员在接收应用包后，必须先验证哈希值与基准哈希值一致，方可开展审核工作。哈希值异常立即暂停并排查。

#### 16.2.3 人工审核阶段
按以下顺序进行：
1. **技术支持人员** → 安全性审核（安全扫描、代码安全、网络安全、数据合规）
2. **测试支持人员** → 功能与兼容性审核（安装/启停/卸载测试、架构适配、功能完整性）
3. **专职审核人员** → 合规性与内容审核、用户体验与文档质量审核

各岗位出具明确的审核意见（通过/驳回及具体原因），由专职审核人员汇总形成综合审核结果。

### 16.3 评分标准

| 维度 | 权重 | 满分 | 最低通过分 | 一票否决条件 |
|---|---|---|---|---|
| 配置完整性 | 30% | 30 | 27 | 必填字段缺失、JSON 语法错误 |
| 功能可用性 | 35% | 35 | 28 | 无法安装/启动/停止 |
| 安全性 | 25% | 25 | 20 | Root 运行、特权模式、恶意代码 |
| 合规性 | 10% | 10 | 8 | 知识产权侵权、违法内容 |

**一票否决项（出现任意一项直接驳回，无需继续审核）：**
- 应用以 root 用户运行
- Docker 应用使用特权模式（`--privileged`）
- 检测到恶意代码或数据窃取行为
- 应用 ID 与已有应用重复
- 数据包包含二进制可执行文件
- 校验和不匹配

### 16.4 常见驳回原因（按频次排序）

| 排名 | 驳回原因 | 错误码 | 整改建议 |
|---|---|---|---|
| 1 | config.ini 包含注释、语法错误或字段缺失 | E002/E003 | 移除所有注释，用 python3 校验 JSON 格式 |
| 2 | app.lang 缺少语言节点或字段为空 | E007/E008 | 补充全部 14 种语言，未翻译的用英文填充 |
| 3 | Docker compose 镜像来源非 Docker Hub | — | 将镜像托管到 Docker Hub |
| 4 | 仓库非公开或资源缺失 | — | 设为公开仓库，上传完整资源 |
| 5 | 应用功能描述与实际功能不符 | — | 修正 app.lang 中的 descript 字段 |
| 6 | id 字段重复 | E004 | 使用全局唯一的应用 ID |
| 7 | 图标格式不符合要求或路径不匹配 | E009 | 使用 SVG 格式，确保路径与 config.ini 一致 |
| 8 | Deb 包服务无法启停或卸载残留 | E016/E017 | 完善 systemd 服务文件和生命周期脚本 |
| 9 | Docker 端口冲突、无数据持久化 | E015 | 确认端口可用，添加卷挂载 |
| 10 | 版本号未递增 | E005 | 新版本号必须严格大于前一版本 |
| 11 | Deb 包以 root 运行 | E011 | 改用非 root 专属用户 |
| E012 | 脚本执行失败，报 `bad interpreter` | 检查文件换行符，确保所有 `.sh` 文件使用 LF 换行，参考第 4 章跨平台换行符规范 |
| E013 | 依赖未预装，报 `command not found` | 参考第 2 章系统预装依赖说明，改用 Go/Python 实现或打包静态依赖，禁止依赖系统未预装的 Node.js/Java 等环境 |
| 12 | Docker 应用使用特权模式 | E012 | 移除 privileged，使用细粒度权限 |
| 13 | 校验和不匹配或缺少校验和文件 | E013 | 重新生成 SHA-256 校验和 |
| 14 | config.ini/DEBIAN/control/app.lang 版本号不一致 | E006 | 统一三处版本号 |

### 16.5 驳回整改流程

1. 审核不通过 → 系统通过「平台消息 + 注册邮箱」双渠道通知开发者
2. 开发者登录开发者平台查看驳回原因和整改建议
3. 开发者须在 **30 天内** 修正问题并重新提交
4. 超过 30 天未重新提交 → 提交自动关闭
5. 连续 **3 次驳回** → 触发强制开发者咨询，审核团队与开发者直接沟通
6. 整改后重新提交 → 更新版本号，以新版本名义重新进入审核流程

### 16.6 审核时效

| 阶段 | 预计耗时 | 说明 |
|---|---|---|
| 自动校验 | 实时 | 提交后即时完成 |
| 初审 | 1-2 个工作日 | 信息一致性与仓库规范验证 |
| 人工审核 | 3-5 个工作日 | 安全/功能/合规全面审核 |
| 上架发布 | 1-2 个工作日 | 审核通过后上架至应用中心 |

> 总审核周期通常为 5-8 个工作日。高峰期可能延长，请提前规划提交时间。

---

## 17. 上架后运维与下架


### 17.3 版本回滚

上架后如出现严重问题：

1. 通过开发者平台提交回滚申请并附原因
2. 平台可将应用回滚至上一个稳定版本
3. 安装了问题版本的用户将收到升级到回滚版本的提示
4. 需向开发者平台提交事后分析报告

### 17.4 应用下架

#### 开发者主动下架：
1. 通过开发者平台提交下架申请
2. 注明原因（停更、替代、合并等）
3. 现有用户保留已安装的应用，但不再接收更新
4. 新用户无法再找到/安装该应用
5. 仓库资源在下架后应保留 60 天，供现有用户使用

#### 平台强制下架（违规）：
1. 平台通过邮件发出违规通知
2. 开发者有 7 天时间回复和整改
3. 逾期 7 天未回复的，应用将被强制下架
4. 严重违规行为（恶意软件、数据窃取、违反 TOS）立即下架，无需等待期

#### 停更归档：
- 在开发者平台将应用标记为"已停更"
- 用户看到"已停更 — 不再维护"标记
- 不允许新安装
- 现有安装继续工作但不再接收更新
- 停更应用在 12 个月后归档

### 17.5 持续运维

1. **版本更新**：每次新提交必须递增版本号并提供更新说明。
2. **安全补丁**：及时修复安全漏洞和兼容性问题。
3. **审核反馈**：在规定时限内响应平台整改通知并完成修复。
4. **TOS 兼容**：持续适配 TOS 系统更新。在用户版本发布前在新 TOS 版本上测试。
5. **仓库维护**：保持公开仓库资源长期可用。不可删除已上架资源。
6. **ABI 监控**：订阅 TOS 发行说明和弃用通知。对已公布的破坏性变更提前规划迁移。
7. **镜像更新**：Docker 应用定期更新基础镜像以包含安全补丁。

---



## 18. 开发者捐赠与商业化支持

### 18.1 捐赠功能说明

#### 18.1.1 功能概述

为支持开发者持续维护与开发优质应用，TNAS 开发者平台提供捐赠链接配置能力。开发者可在个人信息中添加捐赠链接，所有已上架应用的详情页将自动展示捐赠按钮，用户点击后直接跳转至该链接，自愿为开发者提供资金支持。

#### 18.1.2 捐赠链接配置规则

**配置入口：** 登录 TNAS 开发者平台 → 进入「Personal information（个人信息）」页面 → 找到「Donation Link（捐赠链接）」模块，点击右侧「Edit（编辑）」按钮进行修改。

**格式要求：**

- 类型：字符串格式，需为有效的 HTTPS 链接（推荐）；
- 长度限制：10–255 字符；
- 非必填项：开发者可选择不配置捐赠链接，不影响应用上架；
- 可编辑性：支持随时修改、删除链接，修改后即时生效（应用详情页同步更新）。

**展示逻辑：**

- 仅当开发者配置了有效的捐赠链接时，应用详情页才会显示「捐赠」按钮；无配置则按钮隐藏；
- 平台不介入资金流转、结算与纠纷处理，仅提供链接跳转通道，不收取任何费用或分成。

#### 18.1.3 合规提示

- 捐赠链接需遵守所在地区法律法规，不得包含赌博、色情、非法金融、诈骗等违规内容；
- 禁止将捐赠与应用核心功能绑定（如"不捐赠则无法使用基础功能"），需保持捐赠的自愿性；
- 开发者需自行承担链接的可访问性、合规性及相关税务、法律责任。

### 18.2 未来付费应用功能说明（规划中）

#### 18.2.1 功能愿景

为帮助开发者获得合理的开发回报，TNAS 应用生态未来将推出付费应用商业化方案，为优质应用提供合规、透明的付费分发渠道，让开发者的创新与投入获得对应收益，同时为用户提供更多高质量的专业应用选择。

#### 18.2.2 核心方案框架（规划方向）

| 模块 | 规划细节 |
|------|----------|
| **付费模式** | 支持多种商业化模式，包括：<br>1. 一次性买断：用户支付固定费用后永久使用应用；<br>2. 订阅制：按月/按年付费，获取持续更新与技术支持；<br>3. 增值功能解锁：基础功能免费，高级功能需付费解锁。 |
| **定价与分成** | 1. 开发者自主定价，平台提供定价建议区间参考；<br>2. 透明分成机制：开发者获得绝大部分收益，平台收取少量技术服务费（具体比例后续公示）；<br>3. 结算周期：支持按自然月/季度结算，提供清晰的订单与对账数据。 |
| **审核与上架** | 1. 付费应用需通过额外的质量与合规审核（含功能完整性、用户协议、隐私政策等）；<br>2. 需提供明确的功能说明、更新日志及售后支持承诺；<br>3. 支持免费试用/限时体验，降低用户决策门槛。 |
| **权益与保障** | 1. 开发者后台提供付费数据看板（下载量、付费转化率、用户评价等）；<br>2. 平台提供用户投诉处理与纠纷调解通道；<br>3. 为优质付费应用提供推荐位、流量倾斜等扶持资源。 |

#### 18.2.3 开发者准备建议

为迎接付费应用功能上线，建议开发者提前做好以下准备：

- **打磨应用质量：** 聚焦解决用户真实痛点，优化功能稳定性、性能与用户体验，形成差异化竞争力；
- **完善配套服务：** 准备清晰的用户说明文档、更新计划与技术支持渠道，提升用户付费意愿；
- **合规性前置准备：** 梳理应用数据处理逻辑，准备隐私政策、用户协议等合规文件，为付费上架审核做好准备；
- **明确商业化路径：** 结合应用定位，提前规划付费模式（如买断/订阅）与定价策略，匹配目标用户群体的消费习惯。

### 18.3 补充说明

- 本章中"付费应用功能"为未来规划方向，具体上线时间、规则细节将以平台后续公告为准；
- 平台将在功能上线前开放开发者预约通道，优先为优质应用提供测试与上架支持；
- 若开发者对商业化方案有建议或疑问，可通过开发者平台工单通道反馈。

---


## 19. 常见问题 FAQ

### 19.1 审核相关

**Q: 审核被驳回怎么办？**  
审查驳回原因（平台会反馈具体错误码和说明），修正后重新提交。常见驳回原因包括：JSON 格式错误、版本号不递增、缺少语言文件、端口冲突。详见审核标准章节。

**Q: 审核需要多长时间？**  
通常 3-5 个工作日。首次提交可能更长（需人工审核全部内容）。更新版本审核较快（通常 1-3 个工作日）。

**Q: 应用 ID 可以修改吗？**  
创建后不可修改。请在上架前仔细确认应用 ID。

### 19.2 技术问题

**Q: 端口冲突怎么办？**  
- 禁止使用系统保留端口：22、80、443、8181、5050
- 推荐使用 8000-19999 范围
- 安装前在 preinst 脚本中检测端口占用
- 不同应用使用不同端口，平台不自动分配

**Q: 版本号规则是什么？**  
- 遵循语义化版本号（SemVer）：`主版本.次版本.修订号`
- 每次提交必须严格大于前一版本，禁止降级
- 测试版使用 `"beta": true` 字段，版本号后缀（-beta/-rc）不被支持
- 版本号最大长度 20 字符

**Q: 单包还是双包？**  
- 从零开发 → 单包模式（所有文件集成在一个 deb 包中）
- 已有通用标准 deb 包、构建复杂 → 双包模式（源包 + 数据包）
- 简单二进制程序 → 单包模式

**Q: config.ini 文件后缀是 .ini 但内容是 JSON，为什么？**  
公司历史使用习惯。文件扩展名保持 `.ini`，但解析器按 JSON 格式处理。

### 19.3 安装与运行

**Q: 应用安装失败怎么办？**  
1. 检查 `systemctl status <system_id>` 查看服务状态
2. 检查 `journalctl -u <system_id> -n 50` 查看服务日志
3. 确认 config.ini 中所有必填字段已正确填写
4. 确认 systemd 服务文件路径和权限正确
5. 确认端口未被占用：`ss -tlnp | grep <端口>`

**Q: 如何调试 WebUI 内部打开的应用？**  
1. 检查 `/var/api/<app_id>.sock` 是否存在
2. 使用 `curl --unix-socket /var/api/<app_id>.sock http://localhost/` 直接测试后端
3. 在浏览器 DevTools Network 面板检查 `/v2/proxy/<app_id>/` 请求
4. 确认前端正确携带了 `Cookie` 和 `X-Csrf-Token` header

**Q: 如何调试 WebUI 外部打开的应用？**  
1. 检查后端是否监听 `0.0.0.0:<端口>`（非 127.0.0.1）
2. 检查 nginx 配置文件路径和语法：`nginx -t`
3. 直接访问 `http://<TNAS_IP>:<端口>` 确认后端响应正常
4. 确认 nginx location 块的 proxy_pass 端口与后端监听端口一致

---

## 20. 附录
### 附录A：分类列表

| 分类 ID | 显示名称 |
|---|---|
| `Audio_Video_Entertainment` | 音视频娱乐 |
| `Photography_Video` | 摄影与视频 |
| `Backup_Sync` | 备份与同步 |
| `Development_Tools` | 开发工具 |
| `Utilities` | 实用工具 |
| `Web_Services` | Web 服务 |
| `Security` | 安全 |
| `Download` | 下载 |
| `Driver` | 驱动 |

**申请新分类：**
如果没有现有分类适合你的应用，可以申请新分类：
1. 通过开发者平台支持渠道提交分类申请
2. 提供：建议的分类 ID、展示名称、至少 3 个现有或计划应用的合理性说明
3. 审核需 5-10 个工作日
4. 未经事先批准的自定义/非标准分类将被驳回

### 附录B：系统端口参考

以下端口为 TOS 系统保留，应用不得使用：

| 端口 | 服务 |
|---|---|
| 22 | SSH |
| 80 | HTTP（TOS Web） |
| 443 | HTTPS |
| 445 | SMB |
| 3306 | MySQL |
| 5050 | TOS 守护进程 |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 8181 | TOS Nginx（Web UI） |
| 8443 | TOS HTTPS |

推荐应用端口范围：**8000-19999**（排除已被已安装应用占用的端口）。若推荐范围端口被占用，可使用 **49152-65535**（动态端口范围），但需在配置中明确声明。



### 附录C：TOS Systemd 目标

| 目标 | 说明 |
|---|---|
| `multi-user.target` | TOS 应用服务目标（**所有应用服务必须将此用作 `WantedBy`**） |
| `default.target` | 系统默认启动目标（应用服务请勿使用；应使用 `multi-user.target`） |

### 附录D：兼容性矩阵

| TOS 版本 | 基础系统 | glibc | Python3 | Docker | systemd |
|---|---|---|---|---|---|
| TOS 7.0 | Ubuntu 22.04 | 2.35 | 3.10 | 20.10+ | 249 |
| TOS 7.x（后续小版本，兼容TOS7.0） | Ubuntu 22.04 | 2.35 | 3.10 | 24.x | 249 |

> 说明：TOS7.x 系列小版本（含7.1及以上）将基于 Ubuntu 22.04 保持核心依赖的 ABI/API 兼容性，为 TOS7.0 开发的应用无需额外适配即可运行。

### 附录E：语言文件快速模板

```ini
[zh-cn]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[zh-hk]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[en-us]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[fr-fr]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[de-de]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[it-it]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[es-es]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[hu-hu]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[ja-jp]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[ko-kr]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[pl-pl]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[ru-ru]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[tr-tr]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""

[pt-pt]
name = ""
auth = ""
descript = ""
release_note = ""
important = ""
```



---




### 附录F：README.md 模板

```markdown
# <应用名称>

## 概述
应用的简要描述和用途。

## 功能特点
- 功能 1
- 功能 2
- 功能 3

## 安装
1. 要求：TOS 7.0+，[其他依赖]
2. 从 TNAS 应用中心安装
3. 初始配置步骤

## 使用方法
如何访问和使用应用：

1. 访问地址：`http://<你的-nas-ip>:<端口>`
2. 默认凭据：[如适用]
3. 关键设置

## 权限
| 权限 | 理由 |
|---|---|
| 网络：端口 XXXX | [理由] |
| 文件系统：/path/to/data | [理由] |
| 用户：<appid> | 隔离的服务执行 |

## 配置
关键配置选项及其默认值。

## 端口
| 端口 | 协议 | 用途 |
|---|---|---|
| XXXX | TCP | [用途] |

## 支持
- 文档：[链接]
- 问题追踪：[链接]
- 社区：[链接]

## 更新日志
### v1.0.0 (YYYY-MM-DD)
- 首次发布

## 许可证
[许可证类型]
```

### 附录G：配置文件模板全集

所有应用类型的完整可下载配置文件模板可在 TNAS 开发者平台获取：
- `config.ini` 模板（Deb WebUI 内部、Deb WebUI 外部、Deb 无 UI、Docker）
- `app.lang` 模板（14 语言快速模板，参见附录F）
- Systemd 单元文件模板（含安全加固）
- DEBIAN/control 模板（单包、双包）
- 生命周期脚本模板（preinst、postinst、prerm、postrm）
- Nginx 配置模板
- docker-compose.yml 模板
- GitHub Actions CI/CD 模板

### 附录H：常见驳回原因与整改示例

| 驳回原因 | 错误示例 | 正确修复 |
|---|---|---|
| config.ini 有注释 | JSON 中的 `// 这是注释` | 移除所有注释；JSON 不支持注释 |
| JSON 单引号 | `'version': '1.0.0'` | 使用双引号：`"version": "1.0.0"` |
| 尾随逗号 | `"beta": false,}`（最后字段逗号） | 移除最后一个字段后的逗号 |
| 硬编码 IP | `"path": "http://192.168.1.100:8080"` | 使用占位符：`"path": "http://${ip}:8080"` |
| 缺少语言 | app.lang 只有 12 种语言 | 添加全部 14 种必需语言节点 |
| systemd 中使用 root | 服务文件中 `User=root` | 使用专用用户：`User=<appid>` |
| Docker 特权模式 | compose 中 `privileged: true` | 移除；使用细粒度权限 |
| 缺少校验和 | 未提交 .sha256 文件 | 运行 `sha256sum <文件> > <文件>.sha256` |
| 版本号未递增 | v1.0.0 → v1.0.0（相同版本） | 递增版本号：v1.0.0 → v1.0.1 |

### 附录I：术语与名词定义

| 术语 | 定义 | 也称 |
|---|---|---|
| **应用 ID** | 应用的全局唯一标识符；在 `config.ini.id` 中设置 | `app_id`、`appid`、`id` |
| **系统 ID** | Systemd 服务单元名称；在 `config.ini.system_id` 中设置 | `system_id`、服务名 |
| **包名** | Debian 包名称；在 `DEBIAN/control` 的 `Package` 字段设置 | `package`、deb 包名 |
| **双包模式** |是在一个 tar.gz 格式的压缩包中，包含两个 deb 包 ，一个`deb数据包`，另一个是`deb源包`| 双包机制 |
| **数据包** | TOS 系统可识别的应用配置数据包，简称`deb数据包` | 应用数据包、元数据包 |
| **源包** | 可运行的应用主体deb包，简称`deb源包` | 应用安装包、二进制包 |
| **单包模式** | 按照 TOS7.0 规范直接开发，将所有文件集成到单个 deb 包 | 单包机制 |
| **WebUI 内部打开** | 应用前端在 TOS 桌面内以 iframe 方式打开 | iframe 模式、内嵌模式 |
| **WebUI 外部打开** | 应用前端在浏览器新标签页打开 | 新标签页模式、外部模式 |
| **无 UI 服务** | 没有图形界面的应用；后台守护服务 | 无头服务、守护进程 |
| **低版本兼容** | 应用所需的最低 TOS 版本；在 `config.ini.low_version` 中设置 | 最低TOS版本、TOS版本要求 |
| **ABI** | 应用程序二进制接口 — 应用与系统库之间的编译接口 | 二进制兼容性 |
| **SPC** | 系统权限控制 — TOS 的核心权限管理系统 | 权限系统 |

### 附录J：Beta 版应用管理

| 规则 | 说明 |
|---|---|
| **可见人群** | Beta 应用仅对已选择加入 Beta 测试的用户可见 |
| **可见性控制** | 在 config.ini 中设置 `"beta": true`；平台自动限制可见范围 |
| **转正流程** | 从 Beta 毕业：设置 `"beta": false` 并递增版本号。版本号字符串应遵循标准 SemVer（不使用 beta 后缀） |
| **禁止行为** | Beta 应用不得作为正式版分发；误导用户 Beta 状态将导致驳回 |
| **过期下架** | 90 天未更新的 Beta 应用可能被自动下架 |
| **版本号** | 使用标准 SemVer 配合 `"beta": true` 字段；请勿使用 `-beta`、`-rc` 或其他版本号后缀 |

---


*本文档为 TOS7 应用开发与上架的官方全球通用规范。规范将随 TOS7 版本迭代持续更新。开发者应以开发者平台上的最新版本为准。*
