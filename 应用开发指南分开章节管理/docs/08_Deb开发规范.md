# 8. Deb开发规范

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
├── nginx/                        # 【仅外部打开需要】
│   └── <app_id>.conf             # Nginx 配置文件
├── <app_id>.env                  # 【可选】环境变量配置文件
└── depends/                      # 【可选】依赖文件目录
    ├── bin/                      # 可执行文件
    ├── lib/                      # 动态库 (.so)
    ├── etc/                      # 配置文件
    ├── data/                     # 运行数据（数据库/缓存/状态）
    └── logs/                     # 日志
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
├── init.d/
│   └── <system_id>.service
├── <app_id>.env                  # 【可选】环境变量配置文件
└── depends/                      # 【可选】依赖文件目录
    ├── bin/                      # 可执行文件
    ├── lib/                      # 动态库 (.so)
    ├── etc/                      # 配置文件
    ├── data/                     # 运行数据（数据库/缓存/状态）
    └── logs/                     # 日志
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
├── init.d/
│   └── <system_id>.service
├── <app_id>.env                  # 【可选】环境变量配置文件
└── depends/                      # 【可选】依赖文件目录
    ├── bin/                      # 可执行文件
    ├── lib/                      # 动态库 (.so)
    ├── etc/                      # 配置文件
    ├── data/                     # 运行数据（数据库/缓存/状态）
    └── logs/                     # 日志
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
  "path": "http://${ip}:8686",
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
├── init.d/
│   └── <system_id>.service
├── <app_id>.env                  # 【可选】环境变量配置文件
└── depends/                      # 【可选】依赖文件目录
    ├── bin/                      # 可执行文件
    ├── lib/                      # 动态库 (.so)
    ├── etc/                      # 配置文件
    ├── data/                     # 运行数据（数据库/缓存/状态）
    └── logs/                     # 日志
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

> **格式说明：** 文件扩展名 `.ini` 是公司历史使用习惯（与传统配置系统保持文件命名一致），但解析器按 JSON 格式处理。开发者务必使用 JSON 语法编写，否则将导致自动校验失败。

#### 8.4.1 标准模板

以下为标准模板，包含 config.ini 所有可用字段。开发者按需保留对应字段、删去不适用的即可。

```json
{
  "id": "dev-myapp",
  "icon": "/images/icons/dev-myapp.svg",
  "publisher": "开发者名称",
  "exec": true,

  // ===== 应用类型互斥字段（三选一，不可共存）=====
  // 方式一：WebUI 内部打开（iframe 嵌入）
  "type": "iframe",
  "path": "/dev-myapp/",

  // 方式二：WebUI 外部打开（新标签页）— 与 type 互斥
  // "open_path": true,
  // "path": "http://${ip}:8686",

  // 方式三：无 UI 服务 — 不设置 type/open_path/path

  // ===== iframe 模式窗口控制（仅 open_path=false 时生效）=====
  "resize": true,
  "maxmin": true,
  "width": 1180,
  "height": 680,

  "help": "https://example.com/docs",
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
  "system_id": "dev-myapp",
  "package": "dev-myapp",
  "user": "dev-myapp",
  "all_user_display": true,
  "allow_open_in_mobile": false
}
```

> **必读：字段互斥关系**
>
> | 应用类型 | 必设字段 | 禁止设置 |
> |---|---|---|
> | WebUI 内部打开（iframe） | `type: "iframe"` + `path: "/<id>/"` | `open_path` |
> | WebUI 外部打开（新标签页） | `open_path: true` + `path: "http://${ip}:<端口>"` | `type` |
> | 无 UI 服务 | — | `type`、`open_path`、`path` |

#### 8.4.2 字段参考

| 字段 | 类型 | 必填 | 说明 | 详细描述 |
|---|---|---|---|---|
| `id` | string | ✅ 是 | 应用唯一标识符 | 平台全局唯一，不可与已上架应用重复。字符集：小写字母（a-z）、数字（0-9）和连字符（-）。必须以字母开头。最大长度：50 字符。推荐格式：开发者账号标识-应用业务名称 或 域名倒装-业务应用名。示例：dev-admin-monitor     com-douyin-service。禁止纯通用系统关键词：docker、bin、var、api、usr、root、admin、system、service等。创建后不可修改。 |
| `icon` | string | ✅ 是 | 图标路径 | 仓库中的相对路径。必须遵循 `/images/icons/<id>.svg` 格式。图标文件必须存在于该路径。 |
| `publisher` | string | ✅ 是 | 发布者名称 | 在应用中心展示的开发者或组织名称。示例：`"Kevin"`、`"LinuxServer.io"`。 |
| `path` | string | 条件必填 | 应用访问地址 | **`path` 字段按场景互斥：iframe 用 `/<app_id>/`；外部打开用 `http://${ip}:<端口>`；无 UI 留空。** 必须使用 `${ip}` 占位符（如 `http://${ip}:8686`）。系统自动替换 `${ip}` 为 TNAS 局域网 IP。**禁止写死固定 IP 或域名。** 非 80/443 端口：`http://${ip}:<端口>`。WebUI 内部打开（iframe）：`/<app_id>/`。无 UI 应用：设为 `""` 或省略该字段。`exec=true` 时必填。 |
| `exec` | bool | ✅ 是 | 是否有可执行服务 | 应用是否支持启停操作。`true`：应用中心显示启动/停止按钮；`false`：仅展示，无生命周期控制。 |
| `open_path` | bool | 条件必填 | 是否在新标签页打开 | 控制应用打开方式：`true` = 浏览器新标签页；`false` 或省略 = TOS 桌面内嵌 iframe。外部打开应用必须设为 `true`。**与 `type` 互斥，不可同时设置。** |
| `type` | string | 条件必填 | 应用打开类型 | WebUI 内部打开（iframe 嵌入）时设为 `"iframe"`。**与 `open_path` 互斥，不可同时设置。** 外部打开或无 UI 应用不设置此字段。 |
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
| `compose_project` | string | 条件必填 | Docker Compose 项目名 | **Docker 应用必填。** 指定 docker-compose 项目创建时的名称，必须符合 Docker Compose 项目命名规范（仅小写字母、数字、连字符和下划线）。Deb 应用留空。示例：`"myapp-docker"`。 |
| `user` | string | ✅ 是 | 运行用户 | 应用运行的系统用户。指定后自动创建专属用户（如 `"jellyfin"`）。Deb 应用需与 systemd 服务 `User` 字段匹配。**严禁使用 root 用户。** |
| `all_user_display` | bool | ✅ 是 | 是否对所有用户展示 | `true` = 所有 TNAS 用户可见；`false` = 仅管理员可见。当为 `false` 时，应用仅在管理员的应用程序中心视图中出现。非管理员用户无法看到或与该应用交互。应用仍在系统范围内安装并为所有用户运行；此设置仅控制可见性。 |
| `allow_open_in_mobile` | bool | 否 | 是否支持手机端打开 | `true` = 该应用支持手机端打开；`false` = 该应用不支持手机端打开。默认 `false`。 |
| `share_folders` | []string | 否 | 安装时创建共享文件夹 | 配置在安装时为应用创建共享文件夹，文件夹权限采用 ACL 管理。**使用此字段必须保证 `user` 字段不为空。** 示例：`["data", "config"]`。 |

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
  "id": "myapp",       // ❌ 对象最后一个字段末尾多余逗号
  "version": '1.0.0',  // ❌ 单引号（必须用双引号）
  // ❌ JSON 不允许注释
  "beta": false,
}
```
正确写法：
```json
{
  "id": "myapp",
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
EnvironmentFile=/usr/local/<appid>/<appid>.env
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
| `LimitNOFILE` | `65536` | 建议 | 文件描述符限制 |
| `StartLimitBurst` | `5` | 建议 | 间隔内最大重启次数 |
| `StartLimitIntervalSec` | `60` | 建议 | 重启限制间隔（秒） |

> **⚠️ 重要：** 服务单元配置文件**禁止配置 `Restart` 和 `RestartSec` 参数**。应用的启动、停止和重启生命周期由 TOS 应用中心统一管理，开发者配置的自动重启策略可能与平台管理逻辑冲突，导致应用状态不一致。`StartLimitBurst` 和 `StartLimitIntervalSec` 保留不受影响。

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
| **版本强一致** | 两个包的 `Version` 必须完全相同。任何版本不匹配将触发自动驳回。 | 自动驳回 |
| **数据包禁止二进制** | 数据包（`<appid>.deb`）**严禁包含任何可执行二进制文件**、编译代码或系统特定库。仅允许配置文件、图标、语言文件、nginx配置等静态资源。 | 自动驳回 |
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

---

← [上一章：应用类型](07_应用类型.md) &nbsp;&nbsp;|&nbsp;&nbsp; [下一章：Docker开发](09_Docker开发.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 返回总目录](../README.md)
