# 4. Package Specification

This section defines the formal specifications for TOS 7 application packages. All applications must comply with these specifications.


### 4.1 Application Lifecycle

TOS 7 applications follow a clearly defined lifecycle:

```
  Install ──► Configure ──► Start ──► Running
     │            │            │          │
     │            │            │          ├── Stop ──► Stopped ──► Start (Restart)
     │            │            │
     │            │            └── Crash ──► Auto-Restart (if configured)
     │            │
     │            └── Upgrade ──► Stop ──► Install New Version ──► Migrate ──► Start
     │
     └── Uninstall ──► Stop ──► Cleanup ──► Remove
```

**Deb Application Lifecycle Stages:**

| Stage | Trigger | Script/Action | Expected Behavior |
|---|---|---|---|
| Pre-Install | `dpkg -i` | `DEBIAN/preinst` | Create user, check prerequisites, create directories |
| Install | `dpkg -i` | Package extraction | Files deployed to `/usr/local/<appid>/` etc. |
| Post-Install | `dpkg -i` | `DEBIAN/postinst` | Set permissions, enable service, start service |
| Start | `systemctl start` | systemd / init.d | Application process starts |
| Stop | `systemctl stop` | systemd / init.d | Application process stops gracefully |
| Pre-Remove | `dpkg --remove` | `DEBIAN/prerm` | Stop service |
| Post-Remove | `dpkg --remove` | `DEBIAN/postrm` | Clean up user, data, residual files |
| Upgrade | `dpkg -i` (new version) | prerm → upgrade → postinst | Stop old version, install new version, migrate data, start |

**Docker Application Lifecycle Stages:**

| Stage | Trigger | Action | Expected Behavior | Additional Notes |
|---|---|---|---|---|
| Install | App Center (user clicks "Install" button) | Pull image, create volumes | Image available, data directories created | Platform automatically executes installation workflow; no additional developer intervention needed |
| Start | App Center (user clicks "Start" button) / `docker-compose up` | Start container | Service accessible | Supports manual command-line startup by user, consistent with platform operation logic |
| Stop | App Center (user clicks "Stop" button) / `docker-compose down` | Stop container | Service stopped, data preserved | Only stops container process; mounted data volumes are not deleted |
| Upgrade | App Center (user clicks "Update" button when new version exists) | Pull new image, rebuild container | Zero-downtime or brief downtime | Recommend application supports smooth upgrade to avoid data interruption |
| Uninstall | App Center (user clicks "Uninstall" button) | Remove container, optionally clean up volumes | All resources released | User can choose whether to retain data volumes to avoid accidental data deletion |

> Note: "App Center" refers to the built-in application management interface of the TNAS system. User-initiated install/start/stop/upgrade/uninstall operations through this interface will all trigger the corresponding lifecycle processes.


### 4.2 Version Number Specification

TOS 7 follows **Semantic Versioning (SemVer)**:

```
MAJOR.MINOR.PATCH

MAJOR: Incompatible API changes
MINOR: Backward-compatible new features
PATCH: Backward-compatible bug fixes
```

**Rules:**
1. Each submitted version number must be **strictly greater than** the previous version
2. Version downgrade is prohibited
3. Version number must be consistent across `version` in config.ini, `Version` in DEBIAN/control, and `version` in app.lang
4. The platform will verify version consistency during submission
5. Maximum version number length: **20 characters**. Exceeding this will result in rejection.
6. Allowed version number characters: only digits (`0-9`) and dots (`.`). Example: `"1.2.3"`
7. Pre-release/beta versions must use the `"beta": true` field in config.ini, not version number suffixes.

**Beta Version Management Notes:**
- The platform does not support version number suffixes (e.g., `-beta`, `-rc`, `-alpha`)
- Multiple beta versions are distinguished by incrementing the patch number:
  - First beta → `"version": "1.0.0"` + `"beta": true`
  - Second beta → `"version": "1.0.1"` + `"beta": true`
  - Third release → `"version": "1.0.2"` + `"beta": false`
- For official release: set `"beta": false` and increment the version number following normal rules
- Version rollback: The platform does not support version number "downgrade" rollbacks. For rollback needs, submit a rollback request on the developer platform, and the platform will roll back the application to the previous stable version
- See Appendix N Beta Application Management for details

### 4.3 Upgrades

**Deb Application Upgrades:**
- During upgrade, `preinst` receives the `$1 = "upgrade"` parameter
- `postinst` receives the `$1 = "configure"` parameter, with `$2` being the old version number
- Use `$2` to detect the old version and perform data migration
- Never delete user data during upgrades; only modify configuration formats or migrate data structures
- Users store data in the `/usr/local/<app_id>` directory, which is the application's dedicated data directory. The platform will not delete or overwrite user data in this directory during application upgrades or reinstallation
- It is recommended not to store data in system public directories such as `/etc`, `/var`, or `/usr/bin`, as these directories may be overwritten during system updates or application upgrades, leading to data loss

```bash
# Example: Migration logic in postinst
case "$1" in
    configure)
        if [ -n "$2" ]; then
            # Upgrading from version $2
            if dpkg --compare-versions "$2" lt "2.0.0"; then
                # Migrate v1.x config format to v2.x
                /usr/local/<appid>/bin/migrate.sh "$2"
            fi
        else
            # Fresh install
            echo "Fresh install"
        fi
        ;;
esac
```


**Docker Application Upgrades:**
- Pull new image tags
- Rebuild containers using existing volume mounts
- Preserve data across upgrades through persistent volumes
- Include migration logic in the application entry script if necessary

### 4.4 Compatibility Matrix

| TOS Version | Base System | glibc | Python3 | Docker | Node.js |
|---|---|---|---|---|---|
| TOS 7.0 | Ubuntu 22.04 | 2.35 | 3.10 | 20.10+ | 18.x |
| TOS 7.x (subsequent minor versions, compatible with TOS 7.0) | Ubuntu 22.04 | 2.35 | 3.10 | 24.x | 20.x |

> **Important:** Applications must declare the minimum TOS version requirement through the `low_version` field in config.ini. The platform will automatically filter out incompatible devices.

> **TOS 7.x Minor Version Compatibility:** TOS 7.x series minor versions (including 7.1 and above) will be based on Ubuntu 22.04 and maintain ABI/API compatibility for core dependencies (glibc/Python3/Docker/Node.js). Applications developed for TOS 7.0 will run without additional adaptation.

**TOS 7 Minor Version Compatibility:**
- The `low_version` field must specify the minimum required TOS version
- When submitting updates, test on the latest TOS 7 minor version


### 4.5 Case Sensitivity Specification

TOS is based on Ubuntu Linux, and the filesystem is strictly case-sensitive. All applications must follow these rules:

| Element | Rule |
|---|---|
| File names | Strict case matching. `config.ini` ≠ `Config.ini` ≠ `CONFIG.INI` |
| Directory names | Strict case matching. `/images/icons/` ≠ `/Images/Icons/` |
| config.ini key names | All key names lowercase. `"version"` correct, `"Version"` incorrect |
| Application ID (`id`) | Strict case matching. `MyApp` ≠ `myapp`. Cannot be modified after creation |
| Systemd service name | Must match exactly, case-sensitive |


**Prohibited:** Use of case variants of the same file or directory within a single application package. This causes "file not found" and "service startup failure" errors on Linux.

---

---

### 4.6 Cross-Platform Line Ending Specification (CRLF → LF)

All scripts and configuration files running on the TOS system (Linux environment) **must use LF (`\n`) as the line ending**, and must not use the Windows default CRLF (`\r\n`) line ending.

#### Impact of the Issue

- Script execution error: `bad interpreter: No such file or directory`
- Configuration file parsing failure (e.g., systemd service files, Nginx configs)
- Interpreter path incorrectly recognized as non-existent binaries like `/bin/bash\r`

#### Mandatory Requirements

1. All `.sh` / `.py` / `.ini` / `.lang` / `.service` / `.conf` files must be converted to LF line endings before submission
2. Deb package build scripts must include automatic conversion logic to prevent CRLF from being introduced during the build process

#### Recommended Fix Approaches

##### Approach 1: Automatic Conversion in Build Script (Recommended)

```python
import os

def convert_crlf_to_lf(file_path):
    with open(file_path, "rb") as f:
        content = f.read()
    content = content.replace(b"\r\n", b"\n")
    with open(file_path, "wb") as f:
        f.write(content)

# Before packaging, iterate over all files that need conversion
for root, _, files in os.walk("your_app_source/"):
    for name in files:
        if name.endswith((".sh", ".py", ".ini", ".lang", ".service", ".conf")):
            convert_crlf_to_lf(os.path.join(root, name))
```

##### Approach 2: Local Development Tool Configuration

- **VS Code**: Click `CRLF` in the bottom-right status bar, switch to `LF`, then save
- **Git global configuration** (to prevent future files from being automatically converted to CRLF):

```bash
git config --global core.autocrlf input
```

---

← [Previous Chapter: Quick Start](03_Quick_Start.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next Chapter: ABI Compatibility](05_ABI_Compatibility.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Return to Contents](../README.md)
