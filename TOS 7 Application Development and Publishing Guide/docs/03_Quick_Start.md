# 3. Quick Start

This chapter helps developers complete the development and publishing of their first TOS 7 application within 5 minutes.

### 3.1 Prerequisites

- A TNAS device running TOS 7.0 (current stable/beta version)

  > 💡 **No TNAS hardware?** You can use an Ubuntu 22.04 virtual machine, Open TOS local deployment, or apply for a remote trial machine as an alternative. See the "Alternative Testing Solutions for Developers Without TNAS Hardware" section in [6.2 Development Tools](#62-development-tools).

- Basic Linux command-line operation skills
- GitHub account (for code hosting and developer platform association)

### 3.2 Five-Step Publishing Workflow

**Step 1: Register a Developer Account**

Visit the [TNAS Developer Platform](https://developer.terra-master.com) (coming soon), register and complete developer certification.

**Step 2: Choose Application Type**

| Your Application Characteristics | Recommended Type |
|---|---|
| Native binary, Python/Node.js scripts, lightweight services | Deb Application |
| Requires isolated runtime environment, complex dependencies, multi-container architecture | Docker Application |

**Step 3: Choose Project Template**

Based on your application type, use the corresponding GitHub template repository:

| Template Repository | Applicable Scenario | Key Technical Points |
|---|---|---|
| [Deb App Template (Single Package)](https://github.com/terra-master/app-template-deb) | WebUI opens within TOS desktop (iframe) | Unix Socket + Platform Proxy + Cookie Authentication |
| [Deb App Template (Dual Package)](https://github.com/terra-master/app-template-deb-dual) | WebUI opens in a new tab | HTTP Port + Nginx Reverse Proxy + Dual Package Mechanism |
| [Docker App Template](https://github.com/terra-master/app-template-docker) | Docker containerized deployment | docker-compose.yml + Persistent Volumes + Non-Privileged Mode |

> Each template repository includes: complete directory structure, config.ini, multilingual files, systemd service,
> frontend and backend example code, lifecycle scripts, build script (build.sh), GitHub Actions CI/CD configuration.
> Click the **"Use this template"** button on the repository page to create your project.

**Step 4: Local Development and Testing**

```bash
# Deb Application: Build and test installation
dpkg-deb --build ./<app_root> ./<appid>_<version>_amd64.deb
sudo dpkg -i <appid>_<version>_amd64.deb
sudo systemctl status <system_id>

# Docker Application: Start testing
docker-compose up -d
curl http://localhost:<port>/health
```

**Step 5: Submit for Review**

1. Push code to a GitHub public repository
2. Create an application on the developer platform and associate the repository
3. Upload the application package (.deb or .tar.gz) and fill in version information
4. Submit for review, awaiting platform automated validation and manual review
5. After passing review, the application will be published to the TNAS App Center

### 3.3 Key Checklist

Please confirm the following items before submission:

- [ ] config.ini is valid JSON format (no comments, no trailing commas, double quotes)
- [ ] app.lang includes all 14 languages (untranslated languages filled with English)
- [ ] Icons are in SVG format, stored in `/images/icons/<appid>.svg`
- [ ] systemd service file `User` is not root
- [ ] Version number is strictly incremented and consistent across config.ini, DEBIAN/control, and app.lang
- [ ] Full-cycle testing (install/start/stop/uninstall) completed on a real TNAS device

  > 💡 **No TNAS hardware?** You can use alternative solutions for testing (Ubuntu 22.04 VM, Open TOS, remote trial machine). See the "Alternative Testing Solutions for Developers Without TNAS Hardware" section in [6.2 Development Tools](#62-development-tools).

---

### 3.4 Common Pitfalls to Avoid

Before starting formal development, pay special attention to the two most common cross-platform issues below to avoid rejection after submission:

#### Top 1: Line Ending Issues (CRLF → LF)

- **Symptom:** Scripts edited on Windows and uploaded to TOS report `bad interpreter: No such file or directory`
- **Root Cause:** Windows uses CRLF line endings by default, while Linux only recognizes LF
- **Solution:** Ensure all scripts/configuration files use LF line endings before submission (see Chapter 4 Cross-Platform Line Ending Specification)

```bash
# Quickly check for CRLF files in your project
grep -rl $'
' *.sh *.py *.ini *.lang *.service *.conf 2>/dev/null
# One-click conversion (Linux/macOS)
sed -i 's/
$//' *.sh *.py *.ini *.lang *.service *.conf
```

#### Top 2: Missing Node.js Dependency

- **Symptom:** Application reports `node: command not found` on startup
- **Root Cause:** TOS does not pre-install Node.js; Deb applications cannot directly depend on the node environment
- **Solution:** Use Go to compile a static binary, or use Python 3.10 (pre-installed on the system) (see Chapter 2 Non-Preinstalled Dependency Handling Specification)

---

← [Previous Chapter: Architecture Strategy](02_Architecture_Strategy.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next Chapter: Package Specification](04_Package_Specification.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Return to Contents](../README.md)
