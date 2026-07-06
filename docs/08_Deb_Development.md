# 8. Deb Development Specification

### 8.1 Overview

Deb applications are native packages that run directly on the TOS7 host system. They follow standard Debian packaging specifications with adaptations for TOS service management and platform integration.

TOS7 Deb applications are divided into **three subtypes** based on whether they have a frontend page and how it is opened:

| Subtype | Use Case | Opening Method | Backend Communication Method |
|---|---|---|---|
| **WebUI Internal (Inline)** | Backend is a local executable service, frontend is a static WebUI | TOS desktop embedded iframe | Unix Socket + Platform Proxy |
| **WebUI External (New Tab)** | Backend is a local executable service, frontend is a static WebUI | Browser new tab | Nginx Reverse Proxy + HTTP Port |
| **No UI Service** | Background service without an operation page | No frontend page | As needed (no mandatory requirement) |


**Subtype Selection Mandatory Constraints:**

| Application Characteristics | Required Subtype |
|---|---|
| Has Web UI and must open within TOS desktop | WebUI Internal (Inline/iframe) |
| Has Web UI and must open in a browser tab | WebUI External (New Tab) |
| No frontend / background daemon service | No UI Service |
| Needs to access device filesystem via TOS File Manager | WebUI Internal or External |

TOS7 Deb applications support **two packaging methods**:

| Packaging Method | Use Case | Description |
|---|---|---|
| **Method 1: Single Package** | New applications developed from scratch | Developer develops directly following TOS 7.0 specifications, integrating all files into a single deb package |
| **Method 2: Dual Package (Tarball Mode)** | Applications that already have a standard general-purpose deb package | The original application package (deb source package) remains unchanged, with an additional TOS 7.0-compliant data package (<appid>.deb) provided. Both are packaged as a tar.gz tarball for submission |


**Dual Package Mode Applicability Rules:**

| Scenario | Must Use | Must Not Use |
|---|---|---|
| Existing standard general-purpose deb package, complex build | Dual Package Mode | — |
| New application developed from scratch | — | Dual Package Mode (use Single Package) |
| Simple binary program, no existing packaging | — | Dual Package Mode (use Single Package) |
| Third-party upstream Debian package | Dual Package Mode | — |

**Dual Package Mode Mandatory Constraints:**

- **Version Consistency:** The `Version` field of the data package and source package must be exactly identical. Mismatches result in immediate rejection.
- **Content Restrictions:** The data package (`<appid>.deb`) **must not contain any binary files**, otherwise immediate rejection.
- **Installation Order:** Automatically guaranteed by the APT repository dependency mechanism (data package `Depends` on source package), no additional configuration needed.
- **Source Package Independence:** The deb source package must be independently installable on the TOS 7.0 system using the `dpkg -i` command.
- **Dependency Declaration:** The deb data package's metadata `Depends` field must include the deb source package, preferably with the version specified, to maintain a healthy dependency relationship.

### 8.2 General Directory Structure

All Deb application files are installed under the `/usr/local/<app_id>/` directory:

```
/usr/local/<app_id>/
├── config.ini                    # [Required] Application core configuration file
├── bin/
│   └── <binary_name>             # [Required] Backend executable
├── <app_id>.lang                 # [Required] Multi-language configuration file
├── images/
│   └── icons/
│       └── <icon_file>.svg       # [Required] Application icon
├── init.d/
│   └── <system_id>.service       # [Required] Systemd service unit file
├── webui.bz2                     # [Required for WebUI apps] Frontend page archive
├── nginx/                        # [Required only for External Open]
│   └── <app_id>.conf             # Nginx configuration file
├── <app_id>.env                  # [Optional] Environment variable configuration file
└── depends/                      # [Optional] Dependency file directory
    ├── bin/                      # Executable files
    ├── lib/                      # Dynamic libraries (.so)
    ├── etc/                      # Configuration files
    ├── data/                     # Runtime data (database/cache/state)
    └── logs/                     # Logs
```

**Mandatory Correspondences:**

```text
config.ini.id              == <app_id>
config.ini.package         == Package in DEBIAN/control
config.ini.system_id       == systemd service unit ID (without .service suffix)
config.ini.icon            == "/images/icons/<icon_file>.svg"
config.ini.path            == "/<app_id>/" (WebUI Internal)
```

**Requirements:**
1. Application files installed to `/usr/local/<app_id>/`.
2. `<app_id>.lang` filename must correspond to `config.ini.id`.
3. Icon file path must correspond to `config.ini.icon`.
4. systemd service unit ID must match `system_id` in `config.ini`.
5. The binary package name `Package` in deb metadata must match `package` in `config.ini`.
6. The service must be able to start, stop, and query status via `<system_id>.service`.

### 8.3 Three Subtypes in Detail

**The three subtypes are mutually exclusive — each application can only belong to one:**

| Subtype | Required config.ini Fields | Key Identifiers |
|---|---|---|
| **iframe (Internal)** | `type`, `path` | `"type": "iframe"`, `"open_path": false` |
| **External Open (New Tab)** | `path` | `"open_path": true` (do not set `type` field) |
| **No UI Service** | No page-related fields | Do not set `path`, `open_path`, `type` fields |

> **Mutual Exclusion Rule:** `type` and `open_path` cannot coexist — iframe uses `"type": "iframe"`; external open uses `"open_path": true`; No UI sets neither. Mixing leads to undefined behavior and rejection during review.

#### 8.3.1 WebUI Internal (iframe Embedding)

For applications where the backend is a local executable service and the frontend is a static WebUI, opened in an embedded iframe within the TOS desktop.

**Directory Structure:**

```
/usr/local/<app_id>/
├── config.ini
├── bin/
│   └── <binary_name>
├── <app_id>.lang
├── webui.bz2                     # [Required] Frontend page archive
├── images/
│   └── icons/
│       └── <icon_file>.svg
├── init.d/
│   └── <system_id>.service
├── <app_id>.env                  # [Optional] Environment variable configuration file
└── depends/                      # [Optional] Dependency file directory
    ├── bin/                      # Executable files
    ├── lib/                      # Dynamic libraries (.so)
    ├── etc/                      # Configuration files
    ├── data/                     # Runtime data (database/cache/state)
    └── logs/                     # Logs
```

**config.ini Minimal Configuration:**

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

**Core Requirements:**

1. The `type` field must be `"iframe"`.
2. The `path` field format is `"/<app_id>/"`.
3. `webui.bz2` is a fixed filename and cannot be written as any other name.
4. The deb package must contain an executable program, stored at `/usr/local/<app_id>/bin/<binary_name>`.
5. The `config.ini.package` field specification must strictly comply with the Debian package `package` specification.
6. The backend service provides HTTP interface via Unix Socket and must listen on `/var/api/<app_id>.sock` at startup.
7. `/var/api` must be auto-created if it does not exist; old socket files must be cleaned up before startup.
8. Socket file permissions must allow platform proxy access.
9. Frontend requests to the backend must go through the platform proxy path, with the fixed format `/v2/proxy/<app_id>`.
10. Frontend requests must carry the authentication headers required by the platform, including `X-Csrf-Token` and `Cookie` in the request headers.


**Socket File Specification:**
- Permission mode: `0660` (owner and group read/write)
- Owner: `<appid>:<appid>` (matching the service user)
- Support HTTP keep-alive connections
- Support at least 100 concurrent connections
- Idle connection timeout: 30 seconds

7. Frontend requests to the backend must use the platform proxy path: `/v2/proxy/<app_id>/<api_name>`.
8. Frontend requests must carry platform authentication headers.


**CORS and Preflight Request Configuration:**
The backend must handle CORS preflight requests (OPTIONS method) for the platform proxy. Allow the following:
- Origin: TOS Web origin
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type, X-Csrf-Token, Cookie
- Credentials: true

#### 8.3.2 WebUI External (New Tab)

For applications where the backend is a local executable service and the frontend is a static WebUI, opened in a new browser tab.

**Directory Structure:**

```
/usr/local/<app_id>/
├── config.ini
├── bin/
│   └── <binary_name>
├── <app_id>.lang
├── webui.bz2                     # [Required] Frontend page archive
├── images/
│   └── icons/
│       └── <icon_file>.svg
├── nginx/
│   └── <app_id>.conf             # [Required] Nginx configuration file
├── init.d/
│   └── <system_id>.service
├── <app_id>.env                  # [Optional] Environment variable configuration file
└── depends/                      # [Optional] Dependency file directory
    ├── bin/                      # Executable files
    ├── lib/                      # Dynamic libraries (.so)
    ├── etc/                      # Configuration files
    ├── data/                     # Runtime data (database/cache/state)
    └── logs/                     # Logs
```

**config.ini Minimal Configuration:**

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

**Core Requirements:**

1. `open_path` must be `true`.
2. The `path` field must correspond to the route in the nginx configuration file and must resolve to the externally provided HTTP interface.
3. The application package must carry the nginx configuration file `<app_id>.conf`, and the filename must correspond to `config.ini.id`.
4. The backend directly listens on `<listen_port>` to provide the HTTP interface.
5. The deb package must contain an executable program, stored at `/usr/local/<app_id>/bin/<binary_name>`.
6. The `config.ini.package` field specification must strictly comply with the Debian package `package` specification.


**Port Listening Rules:**
- **Must** listen on `0.0.0.0` (all network interfaces); listening only on `127.0.0.1` is prohibited. Listening only on the local loopback address will prevent external access.
- **Must not** occupy system reserved ports (22, 80, 443, 8181, 5050)
- Recommended port range: 8000-19999

**Nginx Configuration File Template:**

Create at `/usr/local/<app_id>/nginx/<app_id>.conf`:

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


**Nginx Configuration Management Requirements:**
- Configuration file permissions: `644` (owner read/write, group and others read-only)
- Configuration file must be placed at `/usr/local/<app_id>/nginx/<app_id>.conf`
- The platform Nginx `include` directive loads configurations alphabetically; port conflicts between applications are resolved through unique ports — two applications cannot share the same port
- Log rotation: Nginx access/error logs are managed by the platform; do not write your own nginx logs
- Do not include `server {}` blocks; only use `location /<app_id>/ {}` blocks

#### 8.3.3 No UI Service

For background service applications without an operation page.

**Directory Structure:**

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
├── <app_id>.env                  # [Optional] Environment variable configuration file
└── depends/                      # [Optional] Dependency file directory
    ├── bin/                      # Executable files
    ├── lib/                      # Dynamic libraries (.so)
    ├── etc/                      # Configuration files
    ├── data/                     # Runtime data (database/cache/state)
    └── logs/                     # Logs
```

**config.ini Minimal Configuration:**

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

**Core Requirements:**

1. No UI applications do not need frontend-related fields such as `path`, `type`, `open_path`, `resize`, `maxmin`, `width`, `height`.
2. No `webui.bz2` frontend archive required.
3. No `nginx/` directory required.
4. The deb package must contain an executable program, stored at `/usr/local/<app_id>/bin/<binary_name>`.
5. The `config.ini.package` field specification must strictly comply with the Debian package `package` specification.


**Status Reporting Requirements:**
No UI applications must report their running status so that the platform can detect failures:
- The systemd service unit's `Type` should be `simple` or `forking`
- Use systemd's `ExecStartPost` to confirm successful startup
- The App Center displays "Running"/"Stopped"/"Abnormal" based on the systemd service status
- On failure, systemd automatic restart (configured in the service file) handles recovery


### 8.4 Core Configuration File — config.ini

config.ini is the core metadata file, defining the application's identity information, display information, runtime properties, and dependency relationships. It is the key basis for platform validation and App Center display.

> **Important:** The file extension is `.ini`, but the content must be in **strict JSON format**. Comments, single quotes, trailing commas, or any syntax errors are prohibited.

> **Format Note:** The `.ini` file extension is a company historical convention (maintaining file naming consistency with legacy configuration systems), but the parser processes it as JSON. Developers must write using JSON syntax, otherwise automatic validation will fail.

#### 8.4.1 Standard Template

Below is the standard template containing all available config.ini fields. Developers should keep the relevant fields and remove those that don't apply.

```json
{
  "id": "dev-myapp",
  "icon": "/images/icons/dev-myapp.svg",
  "publisher": "Developer Name",
  "exec": true,

  // ===== Application Type Mutually Exclusive Fields (choose one, cannot coexist) =====
  // Method 1: WebUI Internal (iframe Embedding)
  "type": "iframe",
  "path": "/dev-myapp/",

  // Method 2: WebUI External (New Tab) — mutually exclusive with type
  // "open_path": true,
  // "path": "http://${ip}:8686",

  // Method 3: No UI Service — do not set type/open_path/path

  // ===== iframe Mode Window Control (only effective when open_path=false) =====
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

> **Required Reading: Field Mutual Exclusion Relationships**
>
> | Application Type | Required Fields | Prohibited Fields |
> |---|---|---|
> | WebUI Internal (iframe) | `type: "iframe"` + `path: "/<id>/"` | `open_path` |
> | WebUI External (New Tab) | `open_path: true` + `path: "http://${ip}:<port>"` | `type` |
> | No UI Service | — | `type`, `open_path`, `path` |

#### 8.4.2 Field Reference

| Field | Type | Required | Description | Detailed Description |
|---|---|---|---|---|
| `id` | string | ✅ Yes | Application unique identifier | Globally unique across the platform, must not duplicate any published application. Character set: lowercase letters (a-z), digits (0-9), and hyphens (-). Must start with a letter. Maximum length: 50 characters. Recommended format: developer-account-identifier-app-business-name or reversed-domain-business-app-name. Examples: dev-admin-monitor, com-douyin-service. Prohibited generic system keywords: docker, bin, var, api, usr, root, admin, system, service, etc. Cannot be modified after creation. |
| `icon` | string | ✅ Yes | Icon path | Relative path within the repository. Must follow `/images/icons/<id>.svg` format. The icon file must exist at this path. |
| `publisher` | string | ✅ Yes | Publisher name | The developer or organization name displayed in the App Center. Examples: `"Kevin"`, `"LinuxServer.io"`. |
| `path` | string | Conditional | Application access URL | **The `path` field is mutually exclusive by scenario: iframe uses `/<app_id>/`; external open uses `http://${ip}:<port>`; No UI leaves empty.** Must use the `${ip}` placeholder (e.g., `http://${ip}:8686`). The system automatically replaces `${ip}` with the TNAS LAN IP. **Hardcoding a fixed IP or domain is prohibited.** Non-80/443 ports: `http://${ip}:<port>`. WebUI Internal (iframe): `/<app_id>/`. No UI applications: set to `""` or omit this field. Required when `exec=true`. |
| `exec` | bool | ✅ Yes | Whether there is an executable service | Whether the application supports start/stop operations. `true`: App Center displays Start/Stop buttons; `false`: Display only, no lifecycle control. |
| `open_path` | bool | Conditional | Whether to open in a new tab | Controls how the application is opened: `true` = browser new tab; `false` or omitted = TOS desktop embedded iframe. External open applications must set to `true`. **Mutually exclusive with `type`, cannot be set simultaneously.** |
| `type` | string | Conditional | Application open type | Set to `"iframe"` for WebUI Internal (iframe embedding). **Mutually exclusive with `open_path`, cannot be set simultaneously.** Do not set this field for external open or No UI applications. |
| `resize` | bool | No | Whether the window is resizable | Only effective when `open_path=false`. Controls whether the application window can be resized. Default `false`. |
| `maxmin` | bool | No | Whether the window supports maximize/minimize | Only effective when `open_path=false`. Controls whether the application window supports maximize/minimize. Default `false`. |
| `width` | int | No | Default window width | Only effective when `open_path=false`. The width of the application page when opened, default 1180. |
| `height` | int | No | Default window height | Only effective when `open_path=false`. The height of the application page when opened, default 680. |
| `help` | string | No | Help documentation URL | Link to help documentation, wiki, or community tutorial. Leave empty if none. |
| `version` | string | ✅ Yes | Application version number | Follows semantic versioning. Each submission must be unique and incremental. Examples: `"1.0.0"`, `"2.3.1"`. |
| `recommend` | bool | ✅ Yes | Whether the app is recommended | Platform-specific field. Developers must set to `false`. The platform may adjust based on quality after review. |
| `beta` | bool | ✅ Yes | Whether it is a beta version | `true` = beta, only visible to test users; `false` = stable, visible to all users. |
| `low_version` | string | ✅ Yes | Minimum supported TOS version | The minimum TOS version on which the application can run normally. Must be `TOS7.0` or higher. Format: `"TOS7.0"`, `"TOS7.1"`. |
| `category` | []string | ✅ Yes | Application category | Maximum 3 categories, selected from the official category list (see [Appendix A](#appendix-a-category-list)). **The first category is the primary category** — determines the default display section of the application. Arrange from most specific to most general. Excess categories will result in rejection. |
| `depend` | []string | ✅ Yes | Dependency application list | Application IDs that must be installed before this application. Must be existing application IDs in the App Center. Dependencies are installed in list order. Example: `["DockerEngine"]`. No dependencies: `[]`. **Circular dependencies will be rejected.** |
| `relation` | []string | No | Related application list | Application IDs displayed in the "Related Applications" module on the application details page. No mandatory dependency, display only. None: `[]`. |
| `platform` | string | ✅ Yes | Target architecture | `"x86_64"` or `"aarch64"`. Multi-architecture requires separate submissions. |
| `official` | string | No | Official website | Link to the application's official website. Leave empty if none. |
| `application_type` | string | ✅ Yes | Application package type | For Deb single-package applications, fill in `"deb"`; for dual-package/tarball applications, fill in `"deb-TarGz"`; for Docker applications, fill in `"docker"`. |
| `system_id` | string | Conditional | Systemd service name | **Required for Deb applications.** Must match the systemd service filename. Leave empty for Docker applications. |
| `package` | string | Conditional | Deb package name | **Required for Deb applications.** Must match the `Package` field in DEBIAN/control. Leave empty for Docker applications. |
| `compose_project` | string | Conditional | Docker Compose project name | **Required for Docker applications.** Specifies the name when creating the docker-compose project; must comply with Docker Compose project naming conventions (only lowercase letters, digits, hyphens, and underscores). Leave empty for Deb applications. Example: `"myapp-docker"`. |
| `user` | string | ✅ Yes | Runtime user | The system user under which the application runs. After specification, a dedicated user (e.g., `"jellyfin"`) is automatically created. Deb applications must match the systemd service `User` field. **Using the root user is strictly prohibited.** |
| `all_user_display` | bool | ✅ Yes | Whether to display for all users | `true` = visible to all TNAS users; `false` = visible only to administrators. When `false`, the application only appears in the administrator's App Center view. Non-admin users cannot see or interact with this application. The application is still installed system-wide and runs for all users; this setting only controls visibility. |
| `allow_open_in_mobile` | bool | No | Whether mobile opening is supported | `true` = the application supports opening on mobile; `false` = the application does not support opening on mobile. Default `false`. |
| `share_folders` | []string | No | Create shared folders on install | Configures shared folders to be created for the application during installation; folder permissions are managed via ACL. **Using this field requires that the `user` field is not empty.** Example: `["data", "config"]`. |

#### 8.4.3 Key Rules

**JSON Format Validation:**

Validate config.ini before submission:

```bash
# Using python3
python3 -c "import json; json.load(open('config.ini'))" && echo "JSON format valid"

# Using jq
jq empty config.ini
```

**Common JSON Errors That Cause Rejection:**
```json
{
  "id": "myapp",       // ❌ Trailing comma after last field
  "version": '1.0.0',  // ❌ Single quotes (must use double quotes)
  // ❌ JSON does not allow comments
  "beta": false,
}
```
Correct:
```json
{
  "id": "myapp",
  "version": "1.0.0",
  "beta": false
}
```


1. **IP Placeholder**: The `path` field must use `${ip}` (e.g., `http://${ip}:8686`). Hardcoding a fixed IP or domain is prohibited.
2. **JSON Syntax**: Must be valid JSON. Comments (`//` or `/* */`), single quotes, or trailing commas are prohibited.
3. **ID Uniqueness**: `id` must be globally unique. Duplicate IDs will be rejected.
4. **Version Increment**: Each new submission's version number must be greater than the previous version. Duplicate or downgraded versions are prohibited.
5. **Category Limit**: Maximum 3 categories per application.
6. **TOS Version**: `low_version` must be TOS 7.0 or higher.
7. **Field Consistency**: `version` must be consistent across config.ini, DEBIAN/control, and app.lang. `system_id` must match the systemd service filename. `package` must match the `Package` field in DEBIAN/control.


**`path` Field Value Quick Reference Table:**

| Application Type | Opening Method | `path` Value | Example |
|---|---|---|---|
| Deb WebUI Internal | iframe embedding | `/<app_id>/` | `"/tmrtimer/"` |
| Deb WebUI External | New tab | `/<app_id>/` | `"/weather/"` |
| Docker Application | New tab | `http://${ip}:<port>` | `"http://${ip}:8080"` |
| No UI Service | No frontend | Omit or `""` | — |

> **Note:** The `path` format for iframe mode (internal) and external open is the same (both `/<app_id>/`), the difference lies in the `open_path` field: internal `open_path=false` (default), external `open_path=true`. Docker applications' `path` uses the `http://${ip}:<port>` format.


> **Reserved Fields:** The following field names are reserved for future platform use. Do not use them in custom config.ini: `host_network`, `container_runtime`, `sandbox`, `auto_update`, `upstream_url`, `license`, `min_memory`, `min_cpu`, `min_disk`. Using reserved fields may cause future compatibility issues and rejection.

---

### 8.5 Language File — app.lang

The language file provides multi-language display support for the App Center. The system automatically loads the corresponding language based on the user's device language.

#### 8.5.1 Supported Languages (14 required)

| Tag | Language |
|---|---|
| `zh-cn` | Simplified Chinese |
| `zh-hk` | Traditional Chinese |
| `en-us` | English |
| `fr-fr` | French |
| `de-de` | German |
| `it-it` | Italian |
| `es-es` | Spanish |
| `hu-hu` | Hungarian |
| `ja-jp` | Japanese |
| `ko-kr` | Korean |
| `pl-pl` | Polish |
| `ru-ru` | Russian |
| `tr-tr` | Turkish |
| `pt-pt` | Portuguese |

#### 8.5.2 File Format

```ini
[en-us]
name = "Application Name"
auth = "Developer Name"
descript = "Detailed description of application features and characteristics."
release_note = "1. New feature. 2. Fixed issue."
important = "Important notes that users need to be aware of."

[zh-cn]
name = "应用名称"
auth = "开发者名称"
descript = "应用功能和特性的详细描述。"
release_note = "1. 新增功能。2. 修复问题。"
important = "用户需要注意的重要事项。"
```

#### 8.5.3 Field Descriptions

| Field | Required | Description |
|---|---|---|
| `name` | ✅ Yes | Application display name. If the application name is a unified language name (not translated), the same name can be used across all languages. |
| `auth` | ✅ Yes | Developer/organization name. |
| `descript` | ✅ Yes | Application feature description. The semantics must be consistent across all languages. |
| `release_note` | No | Version update content. Multiple items use `</br>` for line breaks. Can be left empty for the initial release. |
| `important` | No | Important notice information (e.g., permission requirements, port conflicts, configuration steps, etc.). |

#### 8.5.4 Rules

1. All 14 language nodes must be present. For untranslated languages, fill with English content — **leaving blank is prohibited**.
2. File encoding must be **UTF-8 without BOM**.
3. The `descript` field semantics must be consistent across all language versions.
4. If the application name is a unified language name (not translated), the same `name` can be used across all languages.
5. File naming convention: `<appid>.lang` (e.g., `aria2.lang`).


#### 8.5.5 File Encoding & Format

- File encoding must be **UTF-8 without BOM**
- Line endings must be **LF** (Unix style, `\n`). CRLF (Windows style, `\r\n`) will cause parsing errors
- File naming convention: `<appid>.lang` (e.g., `aria2.lang`)

#### 8.5.6 Text Length Limits

| Field | Maximum Length | Description |
|---|---|---|
| `name` | 64 characters | Display name; exceeding will be truncated |
| `auth` | 64 characters | Developer/organization name |
| `descript` | 512 characters | Feature description |
| `release_note` | 2048 characters | Separate multiple lines with `</br>` |
| `important` | 512 characters | Important notice |

#### 8.5.7 release_note Format

- Multiple items use `</br>` as the line break separator
- **Do not** use other HTML tags (`<b>`, `<p>`, `<div>`, etc.) — may cause page rendering anomalies
- Plain text only, except for `</br>` line breaks

#### 8.5.8 Translation Consistency

- The `descript` field semantics must be consistent across all 14 languages
- Reviewers will verify the translation accuracy of at least the core languages (zh-cn, en-us); for other languages, developers will be asked to correct obvious errors

---

### 8.6 Application Icon

| Requirement | Specification |
|---|---|
| Format | SVG (vector graphics, transparent background) |
| Filename | Must exactly match `id` in config.ini (e.g., `Example-latest.svg`) |
| Storage path | Under the repository `/images/icons/` directory |
| ViewBox | Recommended: `0 0 512 512` |
| Design requirement | Clearly identifiable, no prohibited content |

Icon display scenarios: Application list, application details page, installed applications panel.

---

### 8.7 Backend Service Specification

#### 8.7.1 WebUI Internal (Unix Socket Mode)

The backend executable is installed to:

```text
/usr/local/<app_id>/bin/<binary_name>
```

The backend must create and listen on a Unix Socket:

```text
/var/api/<app_id>.sock
```

**Requirements:**
1. `/var/api` must be auto-created if it does not exist.
2. Old socket files must be cleaned up before startup.
3. Socket file permissions must allow platform proxy access.
4. The backend interface protocol is HTTP-over-Unix-Socket.
5. The backend should gracefully handle `SIGTERM` for systemd service stopping.


**Standard Logging Specification:**

| Log Level | Purpose |
|---|---|
| ERROR | Service failure, startup errors, data corruption |
| WARN | Deprecated features, recoverable errors, configuration issues |
| INFO | Service lifecycle events (start/stop), version info, configuration loaded |
| DEBUG | Detailed diagnostic information (should be disabled in production) |

**Standard Output Format:**
```
[YYYY-MM-DD HH:MM:SS] [LEVEL] [component] message
```
Example:
```
[2026-05-11 16:30:00] [INFO] [main] Service started on port 8686
```

For systemd-managed services, prefer outputting logs to stdout/stderr — systemd journal automatically captures both.

**Service Crash Auto-Restart Limits:**
- Maximum restart attempts: **5 times within 60 seconds**
- After exceeding the limit, the service enters a failed state
- The App Center displays the service as "Abnormal" after the restart limit is exceeded
- Configure in systemd: `StartLimitBurst=5`, `StartLimitIntervalSec=60`

#### 8.7.2 WebUI External (HTTP Port Mode)

The backend executable is installed to:

```text
/usr/local/<app_id>/bin/<binary_name>
```

The backend directly listens on `<listen_port>` to provide HTTP interface.

**Requirements:**
1. Directly listen on `<listen_port>`.
2. Provide a static WebUI home page.
3. Provide a health check endpoint.
4. Provide business API routes, with specific business logic defined by the application.
5. Gracefully handle `SIGTERM` and `SIGINT`.

**Recommended Fixed Routes:**

```text
GET /
GET /health
```

**Recommended Business API Naming:**

```text
/api/<resource>
```

If compatibility with system entry points is needed, also support:

```text
/<app_id>/api/<resource>
/v2/proxy/<app_id>/<resource>
/v2/proxy/<app_id>/api/<resource>
```

### 8.8 Frontend File Specification

Applies to WebUI applications (internal and external).

The frontend source code can be placed in the project source directory:

```text
webui/
├── index.html
├── app.js
└── styles.css
```

When packaging, it must be compressed into `webui.bz2`, with the post-installation path:

```text
/usr/local/<app_id>/webui.bz2
```

**Requirements:**
1. After decompression, `webui.bz2` must contain a properly openable `.html` file.
2. At minimum, `index.html`, `app.js`, and `styles.css` are recommended.
3. Each time the frontend page is opened, it should initialize to an empty state and should not reuse the temporary input state from the previous run.
4. Frontend resource references should carry version parameters to avoid continued loading of old caches after application upgrades.

```html
<link rel="stylesheet" href="./styles.css?v=<version>">
<script src="./app.js?v=<version>"></script>
```

### 8.9 Frontend-Backend Request Specification (WebUI Internal)

The frontend **cannot directly access the socket file** when communicating with the backend. Requests must go through the platform HTTP proxy path:

```text
/v2/proxy/<app_id>/<api_name>
```

If the application has only one main interface, it is recommended:

```text
/v2/proxy/<app_id>
```

**Frontend Request Example:**

```js
fetch("/v2/proxy/<app_id>/<api_name>", {
  method: "POST",
  credentials: "include",
  headers,
  body: JSON.stringify(payload)
});
```

The backend is recommended to be compatible with the following routes to avoid path inconsistencies across different proxy modes:

```text
/<app_id>
/<app_id>/<api_name>
<config.ini.path>/<api_name>
<config.ini.path>/<app_id>
```

### 8.10 Frontend Authentication Header Specification (WebUI Internal)

When the frontend sends backend requests, it must read the current site cookies.

**Cookies that must be read:**

```text
TMSESSNAME
X-Csrf-Token
```

**Request headers must include:**

```text
X-Csrf-Token: <X-Csrf-Token value read from cookie>
Cookie: TMSESSNAME=<TMSESSNAME value read from cookie>; X-Csrf-Token=<X-Csrf-Token value read from cookie>;
```

**Example:**

```text
X-Csrf-Token: ltRoTGSICC68drxbvljhBeD2DZ7LPcge
Cookie: TMSESSNAME=46958db9-1f8a-4686-b340-34fd8ccf62e8; X-Csrf-Token=ltRoTGSICC68drxbvljhBeD2DZ7LPcge;
```

**Frontend Implementation Example:**

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

**Notes:**
1. Browsers do not allow frontend code to manually set the standard `Cookie` header.
2. This specification uses the custom header `Cookie` to pass the concatenated cookie string.
3. `Cookie` is a fixed key name and must be spelled as required by the platform.
4. Requests should retain `credentials: "include"`.

The backend should allow the following headers if browser preflight requests need to be supported:

```text
Content-Type
X-Csrf-Token
Cookie
```


**`Cookie` Header Naming Note:** The custom header name `Cookie` is a platform internal naming convention. It bypasses the browser's restriction on setting the standard `Set-Cookie` header in JavaScript fetch/XHR requests. This name is fixed and must not be modified — any deviation will break authentication.

**Backend Authentication Verification Example (Python):**
```python
def validate_auth(headers):
    '''Validate the Cookie authentication header from frontend requests.'''
    ciikie = headers.get('Cookie', '')
    csrf_token = headers.get('X-Csrf-Token', '')
    
    # Parse Cookie header (format: key1=val1; key2=val2)
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
    # Verify session via TOS platform
    return True
```

**Backend Authentication Verification Example (Go):**
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

**Token Expiration and Session Invalidation Handling:**
- When the authentication token expires or the session becomes invalid, the backend must return HTTP `401 Unauthorized`
- The frontend must detect the 401 response and redirect to the TOS login page
- Do not attempt to automatically refresh tokens; redirect to `/` to trigger TOS re-authentication

```javascript
fetch('/v2/proxy/myapp/api', { credentials: 'include' })
  .then(res => {
    if (res.status === 401) {
      window.location.href = '/';  // Redirect to TOS login
    }
    return res.json();
  });
```

---
### 8.11 Nginx Configuration Specification (WebUI External)

An nginx configuration directory must be created at the same level as `config.ini`:

```text
/usr/local/<app_id>/nginx/<app_id>.conf
```

**Content Template:**

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

**Example (weather application, port 16688):**

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

### 8.12 Systemd Service Specification

The service unit ID comes from `config.ini.system_id`:

```json
{
  "system_id": "<system_id>"
}
```

The final system service must be:

```text
<system_id>.service
```

Retained within the application installation directory:

```text
/usr/local/<app_id>/init.d/<system_id>.service
```

**Standard Service File:**

**Standard Service File (with security hardening):**

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

**Systemd Directive Reference:**

| Directive | Value | Required | Description |
|---|---|---|---|
| `User` | `<appid>` | ✅ Yes | Run the service with a dedicated non-root user |
| `Group` | `<appid>` | ✅ Yes | Run the service with a dedicated group |
| `WorkingDirectory` | `/usr/local/<appid>` | ✅ Yes | Working directory of the service |
| `NoNewPrivileges` | `true` | ✅ Yes | Prevent privilege escalation |
| `ProtectSystem` | `strict` | ✅ Yes | Mount /usr, /boot, /etc as read-only |
| `ProtectHome` | `true` | ✅ Yes | Hide the /home directory |
| `TimeoutStartSec` | `30` | ✅ Yes | Service startup timeout (seconds) |
| `TimeoutStopSec` | `10` | ✅ Yes | Graceful stop timeout (seconds) |
| `AmbientCapabilities` | `CAP_NET_BIND_SERVICE` | Conditional | Only required when binding to ports below 1024 |
| `ReadWritePaths` | `/var/lib/<appid> /var/log/<appid>` | ✅ Yes | Explicitly declare writable paths |
| `LimitNOFILE` | `65536` | Recommended | File descriptor limit |
| `StartLimitBurst` | `5` | Recommended | Maximum restart count within the interval |
| `StartLimitIntervalSec` | `60` | Recommended | Restart limit interval (seconds) |

> **⚠️ Important:** Service unit configuration files **must not configure `Restart` and `RestartSec` parameters**. The application's start, stop, and restart lifecycle is uniformly managed by the TOS App Center. Developer-configured auto-restart policies may conflict with platform management logic, causing inconsistent application state. `StartLimitBurst` and `StartLimitIntervalSec` are retained and unaffected.

### 8.13 DEBIAN/control File

#### 8.13.1 Single Package Mode

In single package mode, all content is integrated into one deb package:

```
Package: <appid>
Version: <version>
Architecture: amd64
Section: utils
Priority: optional
Maintainer: Developer Name <your.email@example.com>
Depends: libc6 (>= 2.34), systemd
Description: Short description
 Detailed description of application functionality.
```

**Field Reference:**

| Field | Required | Description |
|---|---|---|
| `Package` | ✅ Yes | Package name. Must match the `package` field in config.ini. |
| `Version` | ✅ Yes | Package version. Must match the `version` field in config.ini. |
| `Architecture` | ✅ Yes | Use `amd64` for x86_64, `arm64` for aarch64. |
| `Section` | Yes | Package classification (e.g., `utils`, `web`, `net`). |
| `Priority` | Yes | Usually `optional`. |
| `Maintainer` | ✅ Yes | Developer name and email. |
| `Depends` | Recommended | Runtime dependencies. Declare all required system libraries and packages. |
| `Description` | ✅ Yes | The first line is a short description, subsequent lines are detailed description. See format rules below. |

**Architecture Field Reference:**

| TOS Platform | DEBIAN/control `Architecture` | Build Target |
|---|---|---|
| x86_64 / amd64 | `amd64` | `x86_64-pc-linux-gnu` |
| aarch64 / arm64 | `arm64` | `aarch64-linux-gnu` |

**Common Errors:**
- Using `x86_64` in DEBIAN/control → must use `amd64`
- Using `arm64` for 32-bit ARM → must use `armhf` (not supported by TOS7)

**Description Field Format:**
- Line 1: Short description (max 80 characters, no leading space)
- Subsequent lines: Detailed description (each line must begin with a single space, max 80 characters per line)
- Blank lines in the description must contain a single space and a period: ` .`

Example:
```
Description: Short summary of the package
 This is the detailed description.
 It can span multiple lines,
 with each line starting with a space.
 .
 This is a new paragraph.
```

#### 8.13.2 Dual Package Mode

Dual package mode is for applications that already have a standard general-purpose deb package. The source package remains unchanged, with an additional application data package provided.

**Application Data Package DEBIAN/control:**

```
Package: <appid>
Version: <version>
Architecture: all
Section: utils
Priority: optional
Maintainer: Developer Name <your.email@example.com>
Depends: <package> (>= <version>)
Description: Application data package - <Application Name>
 TerraMaster App Center metadata package for <Application Name>.
```

> **Naming Note:** The data package name uses `<appid>` (recommended to match config.ini.id), while the source package name uses `<package>` (the original application's default package name). The data package declares its dependency on the source package through the `Depends` field.

**Dual Package Field Association Rules:**

| Field | Data Package | Source Package | Association Requirement |
|---|---|---|---|
| `Package` | `<appid>` | `<package>` | Data package name recommended to match config.ini.id |
| `Version` | `<version>` | `<version>` | Must be exactly identical |
| `Architecture` | `all` | `amd64`/`arm64` | Data package is usually `all`, source package is the actual architecture |

**config.ini Field Associations:**

| Field | Association Description |
|---|---|
| `config.ini.package` | Must match the **data package** metadata `package` |
| `config.ini.version` | Must match the **data package** metadata `version` |
| `config.ini.system_id` | Must match the **source package** systemd service id |
| `config.ini.path` (when external open) | Must correspond to the nginx configuration route, resolving to the `<listen_port>` provided by the source package |

**Data Package Internal File Structure:**

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
            └── nginx/                    # Only needed for external open
                └── <appid>.conf
```

**Source Package Internal File Structure:**

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

### 8.14 Lifecycle Scripts

**Script Requirements:**
- All lifecycle scripts must begin with a `#!/bin/bash` shebang
- File encoding: UTF-8
- File permissions: `755` (executable by all, writable by owner)
- All scripts must exit with exit code `0` to indicate success
- Use `set -e` to fail on any error

#### preinst — Before Installation

```bash
#!/bin/bash
set -e

# Create dedicated user (if not exists)
if ! id -u <appid> > /dev/null 2>&1; then
    useradd --system --no-create-home --shell /usr/sbin/nologin <appid> 2>/dev/null || true
fi

# Create data directory
mkdir -p /var/lib/<appid>
chown <appid>:<appid> /var/lib/<appid> 2>/dev/null || true

# Create Unix Socket directory (WebUI Internal)
mkdir -p /var/api

exit 0
```

#### postinst — After Installation

```bash
#!/bin/bash
set -e

# Set file permissions
chown -R <appid>:<appid> /usr/local/<appid> 2>/dev/null || true
chown -R <appid>:<appid> /var/lib/<appid> 2>/dev/null || true

# Ensure webui.bz2 is decompressed if present (WebUI applications)
if [ -f /usr/local/<appid>/webui.bz2 ]; then
    cd /usr/local/<appid> && tar -xjf webui.bz2 2>/dev/null || true
fi

# Enable and start service
systemctl daemon-reload
systemctl enable <system_id>.service
systemctl start <system_id>.service

exit 0
```

#### prerm — Before Uninstallation

```bash
#!/bin/bash
set -e

# Kill all residual processes of the application user (upgrade safety)
pkill -u <appid> 2>/dev/null || true
sleep 1

# Stop and disable service
systemctl stop <system_id>.service 2>/dev/null || true
systemctl disable <system_id>.service 2>/dev/null || true

exit 0
```

#### postrm — After Uninstallation

```bash
#!/bin/bash
set -e

# Reload systemd
systemctl daemon-reload

# Remove user and data on purge
if [ "$1" = "purge" ]; then
    if id -u <appid> > /dev/null 2>&1; then
        userdel <appid> 2>/dev/null || true
    fi
    rm -rf /var/lib/<appid>
    rm -f /var/api/<appid>.sock
    # Remove nginx configuration
    rm -f /etc/nginx/conf.d/<appid>.conf 2>/dev/null || true
    # Remove systemd service file
    rm -f /etc/systemd/system/<system_id>.service 2>/dev/null || true
    # Reload systemd
    systemctl daemon-reload 2>/dev/null || true
fi

exit 0
```

### 8.15 Packaging and Verification


**Deb Package Filename Naming Convention:**
- Single package mode: `<appid>_<version>_<arch>.deb`
  - Example: `myapp_1.0.0_amd64.deb`
- Data package: `<appid>_<version>_all.deb`
  - Example: `myapp_1.0.0_all.deb`
- Tarball: `<appid>_<platform>.tar.gz` (dual package mode containing two .deb files)
  - Example: `weather_x86_64.tar.gz`
  - Naming rule: `config.ini.id_config.ini.platform.tar.gz`

**Lintian Verification Requirements:**
- All `Error` (E) level issues must be fixed before submission
- `Warning` (W) level issues should be reviewed; platform-critical warnings must be fixed
- `Info` (I) level issues are informational, optional to address
- Only use `lintian --suppress-tags=<tag>` for documented, intentional deviations

**Dual Package Tarball Structure:**
The `.tar.gz` tarball must have the following structure:
```
<appid>_<platform>.tar.gz
├── <appid>.deb              # Application data package (recommended to match config.ini.id)
└── <package>.deb            # deb source package (use the default name, no modification needed)
```
The tarball root directory must not contain subdirectories — `.deb` files must be at the tarball root level.

**Description:**
- `<appid>.deb`: deb data package, through which the application can be displayed and operated in the App Center
- `<package>.deb`: deb source package, used to implement the deb service functionality

#### Method 1: Single Package Mode

**Step 1: Build the Deb Package**

```bash
dpkg-deb --build ./<application-root-dir> ./<appid>_<version>_amd64.deb
```

**Step 2: Verify the Package**

```bash
dpkg-deb -c <appid>_<version>_amd64.deb
dpkg-deb -I <appid>_<version>_amd64.deb
lintian <appid>_<version>_amd64.deb  # if lintian is available
```

**Step 3: Generate Checksum**

```bash
sha256sum <appid>_<version>_amd64.deb > <appid>_<version>_amd64.deb.sha256
```

**Step 4: Test Installation**

```bash
sudo dpkg -i <appid>_<version>_amd64.deb
sudo systemctl status <system_id>
sudo dpkg --purge <appid>    # Uninstall
```

---

#### Method 2: Dual Package Mode

**Step 1: Build deb Source Package**

```bash
dpkg-deb --build ./<application-root-dir> ./<package>.deb
```

**Step 2: Build deb Data Package**

```bash
mkdir -p /tmp/<appid>/DEBIAN
mkdir -p /tmp/<appid>/usr/local/<appid>

# Copy TOS 7.0 configuration files to the data package
cp config.ini /tmp/<appid>/usr/local/<appid>/
cp <appid>.lang /tmp/<appid>/usr/local/<appid>/
cp -r images /tmp/<appid>/usr/local/<appid>/
# If external open, also copy nginx configuration
cp -r nginx /tmp/<appid>/usr/local/<appid>/ 2>/dev/null || true

# Create DEBIAN/control (see 8.13.2)
# ...

# Build data package
dpkg-deb --build /tmp/<appid> ./<appid>.deb
```

**Step 3: Package and Submit the Tarball**

```bash
tar -czf <appid>_<platform>.tar.gz <appid>.deb <package>.deb
```

**Step 4: Verify, Checksum, and Test Installation**

```bash
# Verify
dpkg-deb -c <package>.deb && dpkg-deb -I <package>.deb
dpkg-deb -c <appid>.deb && dpkg-deb -I <appid>.deb

# Checksum
sha256sum <appid>_<platform>.tar.gz > <appid>_<platform>.tar.gz.sha256

# Test installation
sudo dpkg -i <package>.deb
sudo dpkg -i <appid>.deb
sudo systemctl status <system_id>
```

### 8.16 Complete Examples

#### Example 1: WebUI Internal — Timer Application

**Application Overview:**
- ID: `tmrtimer`
- Type: Deb Application / WebUI Internal (iframe)
- Runtime: Python3 HTTP service (Unix Socket mode)
- Frontend: Static HTML timer page

**Directory Structure:**

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

**config.ini:**

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

**DEBIAN/control:**

```
Package: tmrtimer
Version: 1.0.0
Architecture: amd64
Section: utils
Priority: optional
Maintainer: ljw <ljw@example.com>
Depends: python3 (>= 3.10), systemd
Description: Timer Application
 A simple timer tool supporting start, pause, and reset functionality.
```

---

#### Example 2: WebUI External — Weather Application

**Application Overview:**
- ID: `weather`
- Type: Deb Application / WebUI External (New Tab)
- Runtime: Go backend service, port 16688
- Frontend: Static weather page

**Directory Structure:**

```
/usr/local/weather/
├── config.ini
├── bin/
│   └── weather                  # Go binary
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

**config.ini:**

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

**nginx/weather.conf:**

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

#### Example 3: No UI Service — Data Sync Service

**Application Overview:**
- ID: `datasync`
- Type: Deb Application / No UI Service
- Runtime: Python3 background service

**Directory Structure:**

```
/usr/local/datasync/
├── config.ini
├── bin/
│   └── datasync                  # Executable
├── datasync.lang
├── images/
│   └── icons/
│       └── datasync.svg
└── init.d/
    └── datasync.service
```

**config.ini:**

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

### 8.17 Dual Package Mode Specification

In dual package mode, the original application package (deb source package) remains unchanged, and an additional application data package (deb data package) is provided. The deb data package contains the TOS 7.0 required configuration files. Both are packaged as a tar.gz tarball for submission.

**Data Package Naming Rule:** `<appid>.deb` (recommended to match config.ini.id, all lowercase)

**Data Package Internal File Structure:**

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
            ├── webui.bz2             # Required for WebUI applications
            └── nginx/                # Only needed for external open
                └── <appid>.conf
```

**Data Package DEBIAN/postinst:**

```bash
#!/bin/bash
set -e

# Ensure configuration file permissions are correct
chmod 644 /usr/local/<appid>/config.ini 2>/dev/null || true
chmod 644 /usr/local/<appid>/<appid>.lang 2>/dev/null || true
chmod 644 /usr/local/<appid>/images/icons/<appid>.svg 2>/dev/null || true

exit 0
```

**Data Package config.ini Notes:**
- The `icon` path is fixed to `/images/icons/<appid>.svg` (consistent with the data package icon filename)

- `id` must exactly match the `id` field in config.ini
- `version` must exactly match the source package metadata `Version`
- `application_type` must be set to `deb-TarGz`
- `package` must match the `Package` field in the data package DEBIAN/control

**Source Package Internal File Structure:**

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
            ├── depends/             # If there are dependencies
            │   ├── bin/
            │   ├── lib/
            │   └── ...
            └── init.d/
                └── <system_id>.service
```

**Submission Tarball Structure:**

```
<appid>_<platform>.tar.gz
├── <appid>.deb              # deb data package
└── <package>.deb            # deb source package
```

**GitHub Repository Data Structure (Dual Package Mode):**

```
<appid>_<platform>.tar.gz
├── <appid>.deb              # Application data package
└── <package>.deb            # deb source package (original application package)
```


**Dual Package Mode Mandatory Constraints:**

| Constraint | Description | Violation Consequence |
|---|---|---|
| **Installation Order** | Must install the source package (`<package>.deb`) first, then the data package (`<appid>.deb`). The data package depends on the source package. | Installation failure |
| **Strict Version Consistency** | The `Version` of both packages must be exactly identical. Any version mismatch triggers automatic rejection. | Automatic rejection |
| **Data Package No Binaries** | The data package (`<appid>.deb`) **must not contain any executable binary files**, compiled code, or system-specific libraries. Only configuration files, icons, language files, nginx configs, and other static resources are allowed. | Automatic rejection |
| **Data Package Architecture** | The data package `Architecture` must be `all`, not `amd64` or `arm64`. Configuration files are architecture-independent. | Automatic rejection |
| **Source Package Independence** | The deb source package must be independently installable on the TOS 7.0 system using the `dpkg -i` command. | Installation failure |
| **Dependency Declaration** | The data package's `Depends` field must include the source package name, preferably with the version specified. | Rejection |
| **Systemd Service File Ownership** | The systemd service file (`.service`) must be placed in the source package; the data package must not contain it. The data package is only responsible for TOS platform configuration and display. | Rejection |
| **Uninstallation Order** | When uninstalling, remove the data package first, then the source package. Uninstalling the data package does not affect the source package's runtime data. | — |

**Installation and Uninstallation Flow:**
```bash
# Installation order
sudo dpkg -i <package>.deb                    # 1. Install deb source package first
sudo dpkg -i <appid>.deb                      # 2. Then install deb data package

# Uninstallation order
sudo dpkg --remove <appid>                    # 1. Remove data package first
sudo dpkg --purge <package>                   # 2. Then remove source package
```

---

← [Previous: Application Types](07_Application_Types.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next: Docker Development](09_Docker_Development.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Back to Contents](../README.md)
