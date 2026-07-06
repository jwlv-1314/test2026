# 12. Best Practices

### 12.1 Application Directory Layout

Follow a consistent directory layout to ensure maintainability and compatibility:

```
/usr/local/<appid>/
├── <binary>        # Application executable
├── config.ini      # Application configuration file
├── <appid>.lang    # Language file
├── images/         # Icon resources
├── webui.bz2       # Frontend page archive (WebUI applications)
├── nginx/          # Nginx configuration (externally opened applications)
└── init.d/         # Systemd service file

/var/lib/<appid>/   # Runtime data (writable)
/var/log/<appid>/   # Application logs
/var/api/           # Unix Socket directory (internally opened WebUI)
```


**Directory Differences Between Official and Third-Party Applications:**

| Directory | Official Applications | Third-Party Applications |
|---|---|---|
| Install Base Path | `/usr/local/<appid>/` | `/usr/local/<appid>/` |
| Data Storage | `/home/<appid>/` or `/Volume*/` | `/var/lib/<appid>/` or `/Volume*/` |
| Log Storage | Managed by TOS | `/var/log/<appid>/` |
| Systemd Unit Path | `/etc/systemd/system/<appid>.service` | `/etc/systemd/system/<system_id>.service` |

**Data Storage Recommendations:**
- **It is recommended to store data within `/usr/local/<app_id>` or under `/Volume*`**
- Runtime mutable data is recommended to use `/var/lib/<appid>/`
- Log output should use `/var/log/<appid>/`

### 12.2 Data Persistence

**Deb Applications:**
1. Persistent data is recommended to be stored under `/usr/local/<appid>` or `/Volume*`
2. For NAS-accessible data, create a shared folder:
   ```bash
   ter_share_add -name <appid>-data -owner <appid>
   ```
3. Create symbolic links if needed:
   ```bash
   ln -s /Volume1/<appid>-data /usr/local/<appid>/data
   ```
4. Runtime data stored in `/var/lib/<appid>/`

**Docker Applications:**
1. Mount all persistent data directories through volumes:
   ```yaml
   Volumes:
     - /Volume1/docker/<appid>/config:/config
     - /Volume1/docker/<appid>/data:/data
   ```
2. Storing data in the container filesystem is prohibited
3. Use separate volumes for config and data to support independent backups

### 12.3 Logging

**Deb Applications:**
```bash
# Use systemd journal (recommended)
# All stdout/stderr from the service is automatically captured
# View logs: journalctl -u <appid>

# Or write to file
exec >> /var/log/<appid>/app.log 2>&1
```

**Docker Applications:**
```yaml
services:
  myapp:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

**Best Practices:**
- Use structured logging (JSON format recommended)
- Include timestamp, level, and context in every log entry
- Rotate logs to prevent disk exhaustion
- Do not log sensitive information (passwords, tokens, personal data)


**Log Retention and Cleanup:**

| Log Type | Maximum Retention | Cleanup Method |
|---|---|---|
| Application Logs (File) | 30 days | Logrotate: daily rotation, retain 30 files |
| Systemd Logs | Platform-managed | Automatically managed via journald limits |
| Docker Container Logs | 10MB per file, 3 files total | Docker logging driver configuration |

**Logrotate Configuration:**
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

### 12.4 Resource Limits

| Resource | Deb Applications (systemd) | Docker Applications (compose) |
|---|---|---|
| Memory | `MemoryMax=512M` | `memory: 512M` |
| CPU | `CPUQuota=200%` | `cpus: '2.0'` |
| File Descriptors | `LimitNOFILE=65536` | N/A (container level) |
| Process Count | `LimitNPROC=256` | N/A (container level) |
| Disk | N/A (use quotas) | Volume size limit |

**Guidelines:**
- Set resource limits based on expected workload, not maximum possible usage
- Reserve a 20-30% peak buffer on top of typical usage
- Document resource requirements in README.md

### 12.5 Health Checks

**Deb Applications:**
```ini
# In the systemd service file
[Service]
StartLimitBurst=3
StartLimitIntervalSec=60

# Watchdog (if the application supports it)
WatchdogSec=30
```

**Docker Applications:**
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

### 12.6 Upgrades and Migration

**Deb Applications:**
1. Always check for old versions in `postinst`:
   ```bash
   if [ -n "$2" ]; then
       # Upgrading from $2 — run migration
       /usr/local/<appid>/bin/migrate --from "$2"
   fi
   ```
2. Never delete user data during upgrades
3. Back up configuration before modifying config formats
4. Migration logic should be reversible to support rollback
5. **It is recommended that users store data within `/usr/local/<app_id>` or under `/Volume*`** to ensure data is not lost after upgrades

**Docker Applications:**
1. Use an entrypoint script to detect and migrate old data formats:
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
2. Test the upgrade path for at least the last 2 major versions

### 12.7 Security Hardening

**Deb Applications:**
```ini
[Service]
# Drop all capabilities, only add what's needed
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=true

# File system protection
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/<appid> /var/log/<appid>

# Network namespace (optional)
# PrivateNetwork=true  # Only when network is not needed

# User namespace
# PrivateUsers=true
```

**Docker Applications:**
```yaml
services:
  myapp:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Only when binding to ports below 1024
    read_only: true
    tmpfs:
      - /tmp
      - /run
```


> **Required (must be included in all submissions):**
> - `NoNewPrivileges=true`
> - `ProtectSystem=strict`
> - `ProtectHome=true`
> - `ReadWritePaths` (explicit paths only)
> - Non-root `User`/`Group`
>
> **Recommended (strongly encouraged):**
> - `AmbientCapabilities` (only needed capabilities)
> - `LimitNOFILE`, `LimitNPROC`
> - `PrivateTmp=true`
> - `PrivateDevices=true`
>
> **Optional (advanced hardening):**
> - `PrivateNetwork=true` (only when network is not needed)
> - `PrivateUsers=true`
> - `MemoryDenyWriteExecute=true`

### 12.8 Application Port Allocation

**Rules:**
1. Prioritize selecting ports within the recommended range of **8000-19999** (12,000 ports total, significantly reducing conflict probability)
2. If ports in the recommended range are occupied, the **49152-65535 (dynamic port range)** can be used, but must be explicitly declared in the configuration
3. Check for commonly used ports before selection to avoid conflicts, and make ports configurable via environment variables
4. Document port usage in README.md

**Port Range Description:**
- **8000-19999**: Recommended port range for TNAS applications, avoiding system core service ports (such as 22/80/443/8181) with sufficient capacity to meet the port needs of most applications
- **49152-65535**: IANA-defined dynamic/private port range, suitable for temporary or backup scenarios

**Common Port Reference (Avoid Using):**

| Port | Application |
|---|---|
| 22 | SSH |
| 80 | TOS Web (HTTP) |
| 443 | TOS Web (HTTPS) |
| 445 | SMB |
| 3306 | MySQL |
| 5050 | TOS Daemon |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 8096 | Jellyfin |
| 8181 | TOS Nginx |
| 8443 | TOS HTTPS |
| 9000 | Portainer |
| 9090 | Prometheus |

---

← [Previous: Package Signing Security](11_Package_Signing.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next: Local Testing & Debugging](13_Local_Testing.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Table of Contents](../README.md)
