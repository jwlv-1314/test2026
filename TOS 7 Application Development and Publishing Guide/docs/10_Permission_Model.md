# 10. Permission Model

### 10.0 SPC (System Permission Control) Overview

TOS7 introduces the **SPC (System Permission Control)** system, which follows the principle of least privilege to manage application system access behavior:

- Applications cannot directly modify system files or obtain root privileges; all permission requests must be submitted through the platform API
- Developers must clearly declare their application's permission requirements in the permission declaration; the platform will verify them, and only after approval can the application obtain the corresponding access permissions
- Any behavior that bypasses SPC permission checks is prohibited; such applications will not pass review or will be delisted

### 10.1 Overview

TOS7 follows the **principle of least privilege**. Applications can only request the minimum permissions necessary for their operation. TOS7 applications interact with the **SPC (System Permission Control)** system. Applications must:
- Declare permission requirements in the permission declaration (Section 10.7)
- Not bypass SPC permission checks
- Use platform APIs for permission requests instead of directly modifying system files

The platform provides a structured permission model for both Deb and Docker applications.

### 10.2 User and User Group Model

**⚠️ Application users are strictly prohibited from using root privileges.** All applications must run as a non-root dedicated user.

**Deb Applications:**

| Scenario | User | Description | Configuration Requirement |
|---|---|---|---|
| Dedicated User | `<appid>` | Must be used. Created by the preinst script. Minimal permissions. | **Mandatory** |

> **Mandatory Requirement:** All Deb applications must create a dedicated user (`<appid>`) and run the application as that user; root privileges are strictly prohibited. The dedicated user must be created in the `preinst` script to ensure minimal application runtime permissions. Application data directories (e.g., `/usr/local/<appid>`) must have their permissions set to the dedicated user to avoid insufficient permissions or unauthorized access.

**Creating a Dedicated User:**
```bash
# In preinst
useradd --system --no-create-home --shell /usr/sbin/nologin <appid>
```

**Docker Applications:**

| Scenario | User | Description |
|---|---|---|
| Non-root | `UID:GID` (e.g., `1000:1000`) | **Must be used**. Specified via the `user` field in compose. |

### 10.3 File System Permissions

**Standard Directory Permissions for Deb Applications:**

| Path | Ownership | Permissions | Description |
|---|---|---|---|
| `/usr/local/<appid>/` | `<appid>:<appid>` | `755` | Application directory (service read-only) |
| `/usr/local/<appid>/bin/` | `<appid>:<appid>` | `755` | Executables |
| `/usr/local/<appid>/config/` | `<appid>:<appid>` | `750` | Configuration files |
| `/usr/local/<appid>/site/` | `<appid>:<appid>` | `755` | Web UI files |
| `/var/lib/<appid>/` | `<appid>:<appid>` | `750` | Runtime data (read-write) |
| `/var/log/<appid>/` | `<appid>:<appid>` | `750` | Application logs |

> **Rule:** Application binaries and configuration should be read-only for the service user. Only data and log directories should be writable.

### 10.4 Network Permissions

| Permission | Deb Applications | Docker Applications | Description |
|---|---|---|---|
| Bind Ports | Bind specified ports in service config | Map ports in compose | Must not conflict with system ports |
| Access Local Services | Allowed by default | Use `network_mode: host` or explicit links | Minimize network exposure |
| Outbound Connections | Allowed | Allowed | Outbound is unrestricted |

### 10.5 Shared Folder Access

TNAS shared folders are the primary data access mechanism. Applications that need to access user data must:

1. **Create a shared folder** via `ter_share_add`:
```bash
ter_share_add -name <appid>-data -owner <appid>
```

2. **Or request access to existing shared folders** by joining the `allusers` group:
```bash
usermod -aG allusers <appid>
```

3. **Docker applications** mount shared folders through volumes:
```yaml
Volumes:
  - /Volume1/<shared_folder>:/data:rw    # Read-write access
  - /Volume1/<shared_folder>:/media:ro   # Read-only access
```

> **Important:** Applications must not directly modify shared folder permissions. Use the TOS shared folder management API or allow users to configure access permissions manually.


### 10.5.1 Permission Request Process

When an application needs to access shared folders:

1. **Dedicated Application Folder** (Recommended):
   - Created in postinst via `ter_share_add`
   - Application has full read-write permissions
   - No user authorization required

2. **User Shared Folders** (Authorization Required):
   - Application requests `allusers` group membership
   - User authorizes folder access through TOS shared folder settings
   - Application indicates read-only or read-write requirements in the permission declaration

3. **Permission Format**:
   ```yaml
   # Docker volumes
   - /Volume1/<shared_folder>:/data:rw   # Read-write access
   - /Volume1/<shared_folder>:/media:ro  # Read-only access
   ```

### 10.6 System Resource Limits


**Default Resource Quotas by Application Type:**

> Note: The following disk limits only apply to the **application's runtime usage on the system disk (/)**. Application business data must be stored on `/Volume*` (data disks), which have no storage capacity limits and can support TB-level data storage.

| Application Type | CPU Limit | Memory Limit | System Disk Limit | Example |
|---|---|---|---|---|
| Media Server | 200% (2 cores) | 2048M | 50GB | Jellyfin, Plex, Emby |
| Download Manager | 100% (1 core) | 512M | 20GB | Aria2, qBittorrent |
| Utility Tool | 50% | 256M | 10GB | File Manager, Text Editor |
| Web Service | 100% (1 core) | 512M | 30GB | CMS, Blog, Wiki |
| Database | 200% (2 cores) | 2048M | 30GB | MySQL, PostgreSQL, Redis |
| Security | 50% | 256M | 10GB | Firewall, Antivirus |

The above are platform defaults. Developers may apply for higher system disk limits in the permission declaration with reasonable justification; business data must be stored on data disks and is not subject to these limits.

**Deb Applications (via systemd):**
```ini
[Service]
# Memory limit
MemoryMax=512M
# CPU quota (200% = 2 cores)
CPUQuota=200%
# File descriptor limit
LimitNOFILE=65536
# Process count limit
LimitNPROC=256
```

**Docker Applications (via compose):**
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

### 10.7 Permission Declaration

For transparency, applications should document their permission requirements in README.md:

```markdown


| Permission | Reason |
|---|---|
| Network: Port 8686 | Web UI access |
| File System: /var/lib/tmrtimer | Runtime data storage |
| User: tmrtimer (system user) | Isolated service execution |
| Shared Folder: None | No user data access required |
```


### 10.8 Permission Red Lines (Automatic Rejection)

The following permission requests will result in **automatic rejection**:

| Violation | Description |
|---|---|
| Root Execution | Requesting `root` user to run the application |
| Privileged Mode | Requesting `--privileged` Docker mode |
| System Directory Write | Requesting write access to system directories such as `/etc/`, `/usr/`, `/boot/` |
| Cross-App Data Access | Requesting access to another application's data directories |
| Unrestricted Network Access | Applying for `network_mode: host` without written reasonable justification (only system-level network tools may apply) |
| Excessive Port Exposure | Requesting more ports than functionally necessary |

---

← [Previous: Docker Development](09_Docker_Development.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next: Package Signing Security](11_Package_Signing.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Table of Contents](../README.md)
