# 1. Document Overview

TOS 7 is built on Ubuntu 22.04 and uses a standard Linux runtime environment. Starting from TOS 7, the platform supports the following two types for newly submitted applications:

- **Deb Applications**: Native applications running directly on the host system, packaged in standard Debian package format
- **Docker Applications**: Containerized applications deployed via Docker Compose

> **Note:** The legacy `.tpk` format submission channel has been closed for new applications. Already-published tpk format applications will continue to be maintained, but all new application submissions must follow the Deb or Docker specifications defined in this document.

All applications submitted to the TNAS App Center must strictly adhere to this guide in order to pass the platform's automated validation and manual review.

---

[Next Chapter: Architecture Strategy](02_Architecture_Strategy.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Return to Contents](../README.md)
