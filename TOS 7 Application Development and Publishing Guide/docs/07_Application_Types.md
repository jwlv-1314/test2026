# 7. Application Types

| Type | Use Case | Package Format | Submission Format |
|---|---|---|---|
| Deb Application | Binary programs/scripts running directly on the host | Standard `.deb` package | Deb package + config file |
| Docker Application | Services requiring an isolated runtime environment | Docker image + docker-compose.yml | Compose file + config file |

Choose the appropriate type based on application characteristics:

- **Choose Deb** — If your application is a native binary, Python/Node.js script, or lightweight service
- **Choose Docker** — If your application requires a specific runtime environment, has complex dependencies, or already has a containerized version

> **Hybrid Applications:** When a native launcher manages Docker containers, the application package may contain both Deb and Docker components. In this case, use `"application_type": "deb"` and declare `["DockerEngine"]` in `depend`. The Deb component serves as the launcher/manager for the Docker service.

---

← [Previous: Development Environment](06_Development_Environment.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next: Deb Development](08_Deb_Development.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Back to Contents](../README.md)
