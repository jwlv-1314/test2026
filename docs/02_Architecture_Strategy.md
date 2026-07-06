# 2. Architecture Strategy

### 2.1 Official Architecture Recommendation

TOS 7 adopts a **Container-first** strategy while maintaining full support for native Deb applications. The platform recommends the following decision framework:

```
                    ┌─────────────────────────────────┐
                    │ Does your application require    │
                    │ an isolated runtime environment? │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼─────────────────┐        
                    │  Yes                        No  │    
                    │                                │              
                    ▼                                ▼              
              ┌──────────┐           ┌────────────────────────────┐      
              │ Docker   │           │ Is it a TOS standard       │  
              │ App      │           │ service or lightweight     │      
              └──────────┘           │ tool?                      │      
                                     └─────────────┬──────────────┘      
                                           ┌───────▼───────┐         
                                           │  Yes          │  No      
                                           ▼               ▼         
                                     Deb App          Deb App      
                                     (TOS Std)        (Native)
```


### 2.2 Container-First Direction

The TOS 7 application ecosystem is evolving toward a **Container-first** model:

- **Docker applications** are the preferred path for most third-party services
- Provides better isolation, simpler dependency management, and cross-platform consistency
- TOS 7 supports Docker containerized deployment. Before use, install the DockerEngine application from the App Center, which provides a complete Docker Compose runtime environment for TOS 7.
- Future platform features (sandboxing, resource limits, automatic updates) will prioritize Docker applications

**Special Application Type Selection Rules:**

- **Headless backend services:** Use **Deb (No UI)** subtype for lightweight daemons; use **Docker** for services with complex runtime dependencies or requiring container isolation

**For Deb applications**, TOS 7 provides full support, but developers should:
- Minimize system-level dependencies
- Use systemd for lifecycle management
- Follow the principle of least privilege
- Prepare for future containerized deployment

**Scenarios where Docker is recommended:** The following scenarios must use Docker and Deb is prohibited:

- Applications requiring a specific OS environment or library versions conflicting with the host
- Applications requiring network isolation (separate namespaces)
- Multi-container architecture applications (e.g., web service + database)

> **Deb Application Roadmap:** Deb applications remain fully supported in TOS 7.x. The platform may gradually introduce transition paths toward a container-first architecture in future major TOS releases. Developers will receive at least 12 months' advance notice before any format deprecation.

---


---

### 2.3 TOS System Pre-installed Dependencies

TOS 7.0 is built on Ubuntu 22.04, and the system comes pre-installed with the following core dependencies:

- bash / dash
- Python 3.10
- systemd
- nginx
- curl / wget
- Docker runtime (Docker applications only)

> **Important Note:** Language runtimes such as Node.js, Java, and Go are **not pre-installed by default in TOS**. Do not directly depend on these environments in Deb applications.

### 2.4 Handling Non-Preinstalled Dependencies

If your application depends on an environment not pre-installed in TOS (such as Node.js), you must adopt one of the following compliant solutions. **Directly declaring dependencies or downloading at runtime is prohibited.**

#### Prohibited Approaches

- Declaring `Depends: nodejs` in `DEBIAN/control` (system does not have it pre-installed, causing installation failure)
- Installing dependencies via `apt install nodejs` in scripts (triggers permission issues and disrupts the system environment)
- Using Node.js scripts as the application entry point (results in `node: command not found`)

#### Recommended Alternatives (in order of priority)

##### Option 1: Compile Static Binary with Go (Recommended)

Rewrite core logic in Go and compile into a statically linked standalone binary with zero system dependencies:

```bash
# Compile x86_64 static binary
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o appname-x86_64 main.go

# Compile aarch64 static binary
GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build -o appname-aarch64 main.go
```

- Place the compiled binary in the `/usr/local/<appid>/` directory of the Deb package
- Launch directly via systemd service file, no additional dependencies needed

##### Option 2: Implement with Python (Leveraging System Pre-installed Dependencies)

Rewrite core logic in Python. TOS comes pre-installed with Python 3.10 and can be used directly:

- Declare dependency in `DEBIAN/control`: `Depends: python3`
- For third-party libraries, bundle them with the Deb package or use `pip install --target` to install into the application's private directory

##### Option 3: Package Static Dependencies (Special Scenarios Only)

If you must use an environment not pre-installed in TOS, such as Node.js, you can bundle the architecture-specific static binary with the Deb package:

- Place the Node.js static binary in the `/usr/local/<appid>/node/` directory
- Use absolute paths in scripts: `/usr/local/<appid>/node/bin/node /usr/local/<appid>/app.js`
- Note: This approach significantly increases package size and is only recommended for lightweight applications

---

← [Previous Chapter: Document Overview](01_Overview.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next Chapter: Quick Start](03_Quick_Start.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Return to Contents](../README.md)
