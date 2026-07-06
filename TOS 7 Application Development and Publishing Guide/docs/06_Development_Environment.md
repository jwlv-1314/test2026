# 6. Development Environment

### 6.1 Supported Target Architectures

| Architecture | Build Target | Deb Architecture Field |
|---|---|---|
| x86_64 | x86_64-pc-linux-gnu | amd64 |
| aarch64 | aarch64-linux-gnu | arm64 |

> Applications must provide separate builds for each target architecture. Multi-architecture support requires separate submissions.

### 6.2 Development Tools

**Deb Applications:**
- `dpkg-dev`, `debhelper` — Debian packaging tools
- `lintian` — Debian package compliance checker
- `systemd` — Service management testing

**Docker Applications:**
- `docker` (20.10+), `docker-compose` — Container toolchain
- `docker scan` / `trivy` — Vulnerability scanning

**Testing:**
- A TNAS device running **TOS 7.0 (current stable/testing version)** is required for local validation. Subsequent TOS 7.x versions will maintain compatibility, with no repeated verification needed
- An Ubuntu 22.04 virtual machine can be used for preliminary testing

**Alternative Testing Options for Developers Without TNAS Hardware:**

1. Use an Ubuntu 22.04 virtual machine for basic functional testing of Deb applications
2. Use Docker Desktop (Windows/macOS/Linux) to simulate the TOS 7.0 Docker environment and verify container application compatibility
3. **Local Deployment of Open TOS**: Open TOS is fully identical to the TNAS TOS 7.0 system and can be installed on a regular PC or virtual machine. Developers can download the Open TOS image from the TerraMaster official website and deploy their own testing environment
4. **Remote Test Machine**: Developers without hardware can apply for an official TerraMaster TOS 7.0 remote testing machine. Obtain the login credentials from the official forum — complete testing is possible without owning any hardware

---

← [Previous: ABI Compatibility](05_ABI_Compatibility.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next: Application Types](07_Application_Types.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Back to Contents](../README.md)
