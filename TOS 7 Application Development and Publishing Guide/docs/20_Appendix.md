# 20. Appendix


| Category ID | Display Name |
|---|---|
| `Audio_Video_Entertainment` | Audio, Video & Entertainment |
| `Photography_Video` | Photography & Video |
| `Backup_Sync` | Backup & Sync |
| `Development_Tools` | Development Tools |
| `Utilities` | Utilities |
| `Web_Services` | Web Services |
| `Security` | Security |
| `Download` | Download |
| `Driver` | Driver |

**Requesting a New Category:**
If no existing category fits your application, you may request a new category:
1. Submit a category request through the Developer Platform support channel
2. Provide: a suggested Category ID, Display Name, and justification with at least 3 existing or planned applications
3. Review takes 5–10 business days
4. Custom/non-standard categories without prior approval will be rejected

### Appendix B: System Port Reference

The following ports are reserved by the TOS system and must not be used by applications:

| Port | Service |
|---|---|
| 22 | SSH |
| 80 | HTTP (TOS Web) |
| 443 | HTTPS |
| 445 | SMB |
| 3306 | MySQL |
| 5050 | TOS Daemon |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 8181 | TOS Nginx (Web UI) |
| 8443 | TOS HTTPS |

Recommended application port range: **8000–19999** (excluding ports already used by installed applications). If the recommended range ports are occupied, **49152–65535** (dynamic port range) may be used, but must be explicitly declared in the configuration.


### Appendix C: TOS System Directories

| Path | Description |
|---|---|
| `/usr/local/<appid>/` | Application main directory (Deb applications) |
| `/Volume1/@apps/<appid>/` | TOS application installation directory |
| `/var/lib/<appid>/` | Application runtime data |
| `/var/log/<appid>/` | Application logs |
| `/etc/init.d/<appid>` | TOS service script symlink |
| `/etc/systemd/system/<appid>.service` | Systemd service file |
| `/Volume1/docker/<appid>/` | Docker application data |

### Appendix D: TOS Systemd Targets

| Target | Description |
|---|---|
| `multi-user.target` | TOS application service target (**all application services must use this as `WantedBy`**) |
| `default.target` | System default boot target (do not use for application services; use `multi-user.target` instead) |

### Appendix E: Compatibility Matrix

| TOS Version | Base System | glibc | Python3 | Docker | systemd |
|---|---|---|---|---|---|
| TOS 7.0 | Ubuntu 22.04 | 2.35 | 3.10 | 20.10+ | 249 |
| TOS 7.x (subsequent minor versions, compatible with TOS7.0) | Ubuntu 22.04 | 2.35 | 3.10 | 24.x | 249 |

> Note: TOS7.x series minor versions (including 7.1 and above) will maintain ABI/API compatibility for core dependencies based on Ubuntu 22.04. Applications developed for TOS7.0 can run without additional adaptation.

### Appendix F: Language File Quick Template

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

### Appendix G: Shared Folder API

```bash
# Create a shared folder for your application
ter_share_add -name <folder_name> -owner <username>

# Example
ter_share_add -name myapp-data -owner myapp
```

### Appendix H: Upgrade Migration Checklist

Use this checklist when upgrading your application to a new major version:

- [ ] Data migration script handles previous version format
- [ ] Configuration files backed up before modification
- [ ] New dependencies declared in DEBIAN/control
- [ ] Service file updated (if needed)
- [ ] Version number incremented in config.ini, DEBIAN/control, and app.lang
- [ ] Changelog/release notes updated
- [ ] Upgrade path tested: install old version → add data → upgrade → verify data
- [ ] Rollback path tested: downgrade or restore from backup
- [ ] SHA-256 checksums regenerated

---



### Appendix J: README.md Template

```markdown
# <Application Name>

## Overview
A brief description of the application and its purpose.

## Features
- Feature 1
- Feature 2
- Feature 3

## Installation
1. Requirements: TOS 7.0+, [other dependencies]
2. Install from the TNAS App Center
3. Initial configuration steps

## Usage
How to access and use the application:

1. Access URL: `http://<your-nas-ip>:<port>`
2. Default credentials: [if applicable]
3. Key settings

## Permissions
| Permission | Justification |
|---|---|
| Network: Port XXXX | [Justification] |
| File System: /path/to/data | [Justification] |
| User: <appid> | Isolated service execution |

## Configuration
Key configuration options and their defaults.

## Ports
| Port | Protocol | Purpose |
|---|---|---|
| XXXX | TCP | [Purpose] |

## Support
- Documentation: [Link]
- Issue Tracker: [Link]
- Community: [Link]

## Changelog
### v1.0.0 (YYYY-MM-DD)
- Initial release

## License
[License Type]
```

### Appendix K: Complete Configuration File Templates

All complete downloadable configuration file templates for all application types are available on the TNAS Developer Platform:
- `config.ini` templates (Deb WebUI Internal, Deb WebUI External, Deb No-UI, Docker)
- `app.lang` template (14-language quick template, see Appendix F)
- Systemd unit file template (with security hardening)
- DEBIAN/control template (single-package, dual-package)
- Lifecycle script templates (preinst, postinst, prerm, postrm)
- Nginx configuration template
- docker-compose.yml template
- GitHub Actions CI/CD template

### Appendix L: Common Rejection Reasons and Fixes

| Rejection Reason | Incorrect Example | Correct Fix |
|---|---|---|
| Comments in config.ini | `// This is a comment` in JSON | Remove all comments; JSON does not support comments |
| Single quotes in JSON | `'version': '1.0.0'` | Use double quotes: `"version": "1.0.0"` |
| Trailing comma | `"beta": false,}` (comma after last field) | Remove comma after the last field |
| Hardcoded IP | `"path": "http://192.168.1.100:8080"` | Use placeholder: `"path": "http://${ip}:8080"` |
| Missing languages | app.lang has only 12 languages | Add all 14 required language nodes |
| root in systemd | `User=root` in service file | Use dedicated user: `User=<appid>` |
| Docker privileged mode | `privileged: true` in compose | Remove; use fine-grained permissions |
| Missing checksums | No .sha256 file submitted | Run `sha256sum <file> > <file>.sha256` |
| Version not incremented | v1.0.0 → v1.0.0 (same version) | Increment version: v1.0.0 → v1.0.1 |

### Appendix M: Terminology and Definitions

| Term | Definition | Also Known As |
|---|---|---|
| **Application ID** | Globally unique identifier for the application; set in `config.ini.id` | `app_id`, `appid`, `id` |
| **System ID** | Systemd service unit name; set in `config.ini.system_id` | `system_id`, Service Name |
| **Package Name** | Debian package name; set in the Package field of DEBIAN/control | `package`, deb package name |
| **Dual-Package Mode** | A tar.gz compressed archive containing two deb packages — one deb data package and one deb source package | Dual-package mechanism |
| **Data Package** | TOS system-recognizable application configuration data package, referred to as the deb data package | Application data package, metadata package |
| **Source Package** | The runnable application main deb package, referred to as the deb source package | Application install package, binary package |
| **Single-Package Mode** | Development directly following the TOS7.0 specification, integrating all files into a single deb package | Single-package mechanism |
| **WebUI Internal** | Application frontend opens within the TOS desktop as an iframe | iframe mode, embedded mode |
| **WebUI External** | Application frontend opens in a new browser tab | New tab mode, external mode |
| **No-UI Service** | Application without a graphical interface; a background daemon service | Headless service, daemon |
| **Minimum TOS Version** | Minimum TOS version required by the application; set in `config.ini.low_version` | Min TOS version, TOS version requirement |


### Appendix N: Beta Application Management

| Rule | Description |
|---|---|
| **Visibility Audience** | Beta applications are only visible to users who have opted into beta testing |
| **Visibility Control** | Set `"beta": true` in config.ini; the platform automatically restricts visibility |
| **Graduation Process** | To graduate from Beta: set `"beta": false` and increment the version number. The version string should follow standard SemVer (do not use beta suffixes) |
| **Prohibited Behavior** | Beta applications must not be distributed as stable releases; misleading users about beta status will result in rejection |
| **Expiry & Delisting** | Beta applications not updated for 90 days may be automatically delisted |
| **Version Number** | Use standard SemVer with the `"beta": true` field; do not use `-beta`, `-rc`, or other version number suffixes |

---


*This document is the official global specification for TOS7 application development and publishing. The specification will be continuously updated as TOS7 versions iterate. Developers should refer to the latest version on the Developer Platform.*

---

← [Previous: FAQ](19_FAQ.md) &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Return to TOC](../README.md)
