# 15. Publishing Process

### 15.1 Detailed Procedure

#### Step 1: Register a Developer Account

1. Visit the TNAS Developer Platform: https://developer.terra-master.com
2. Click the [Register] button to enter the registration information page
3. Use a valid email address as your login account, and fill in your developer name (recommended to match the publisher in the config file)
4. Read and agree to the Service Agreement, then click [Confirm] to complete registration
5. No review wait is required after registration; your account is activated immediately

> **Note:** Your account email is used to receive review result notifications, password resets, and other important information. Please keep your email address valid.

#### Step 2: Obtain Configuration Templates and Develop Your Application

1. Refer to the standard templates in Chapter 8 (Deb Application Development and Configuration Specification) of this document to write config.ini, app.lang, systemd service files, etc., or use the recommended project template repository from the TNAS Developer Platform for quick initialization
2. Complete application development and packaging according to the specifications in this document
3. Perform local testing and verification (see Chapter 13)

#### Step 3: Create a Public Repository

1. Create a public repository on GitHub or Gitee
2. Upload all required files (config files, application packages, icons, README.md, etc.)
3. **Deb Applications** — Upload the `<appid>_<platform>.tar.gz` archive (containing the `<appid>.deb` data package and `<package>.deb` source package)
4. **Docker Applications** — Upload `docker-compose.yml`, `config.ini`, `app.lang`, and icon files
5. Include SHA-256 checksum files

#### Step 4: Create an Application on the Developer Platform

1. Log in to the Developer Platform and click [My Applications] → [Add Application]
2. Fill in application information:
   - **Application ID**: Must exactly match the `id` field in config.ini
   - **Application Package Type**: Select Docker type or deb package type
   - **Repository URL**: Enter the public repository URL (must be public, or review cannot proceed)
3. Confirm and submit

#### Step 5: Add a New Application Version

1. Find the target application in [My Applications] and click [Version Management]
2. Click [Add Version] and fill in the version number
   - Version number format: strictly follow `xx.yy.zzz` (major.minor.revision)
   - Historical version numbers cannot be reused
   - Must match the `version` field in config.ini
3. After submitting the version, the publishing application process begins

#### Step 6: Platform Automatic Validation

After submission, the platform automatically performs the following checks:
- File format validation (config.ini JSON syntax, app.lang format)
- Field completeness validation (no missing required fields)
- Language coverage validation (all 14 language nodes present)
- Icon validation (SVG format, path matching)
- Checksum verification (SHA-256 matches uploaded file)
- Version consistency validation (config.ini / DEBIAN/control / app.lang versions match)

**Common reasons for automatic validation failure:**
- config.ini contains comments or syntax errors
- app.lang is missing language nodes
- Icon not found or format error
- Checksum mismatch

#### Step 7: Manual Review

The review team evaluates from four dimensions (see Chapter 16 for details):
1. **Configuration Completeness** (Weight 30%): All required files complete, formats correct
2. **Functional Availability** (Weight 35%): Install, start, run, uninstall all work without errors
3. **Security** (Weight 25%): No malicious code, no excessive authorization, no sensitive hardcoding
4. **Compliance** (Weight 10%): Content compliant, description matches functionality

Review process: Initial Review (information consistency, repository compliance) → Security Review (technical support staff) → Functional Compatibility Testing (testing support staff) → Comprehensive Review (dedicated review staff)

#### Step 8: Review Result Notification

Review results are notified to developers through two channels:
- **Platform Messages**: Log in to the Developer Platform to check review status
- **Registered Email**: Review results sent to the email used during registration

Review status descriptions:
- **Under Review**: Application is in the review queue
- **Approved**: Application has passed review and is entering the publishing process
- **Rejected**: Application has issues requiring correction; must be fixed and resubmitted within 30 days
- **Withdrawn**: Developer has voluntarily withdrawn the review application

#### Step 9: Official Publishing

After passing review, the application will be listed on the TNAS Application Center within 1-2 business days:
- Users can search for and install the application from the Application Center
- Developers can check the application status changed to "Published" in [My Applications]

> **Statistics:** The developer dashboard displays core metrics such as the number of published applications, total application downloads, and cumulative application submissions. The progress of the latest 3 publishing applications is updated in real time.

### 15.2 Repository Requirements

- Must be a **public repository** (GitHub or Gitee). Private repositories are not supported.
- Must include all required configuration files and application resources.
- Deb applications must submit a `tar.gz` archive containing the `<appid>.deb` data package and `<package>.deb` source package.
- Docker applications must submit `docker-compose.yml`, `config.ini`, `app.lang`, and icon files.
- Repository resources must remain available long-term. Do not delete published resources.
- Repository structure must conform to the specified directory layout.
- All binary artifacts must include SHA-256 checksum files.

**Application Renaming and ID Change Policy:**
- The application `id` (in config.ini) **cannot be changed** once published
- The application display name (in app.lang) can be updated in new versions
- To change the application `id`, you must submit it as a completely new application (new listing, new review)
- The old application must go through the application delisting process (see Section 17.4)

---

← [Previous: CICD Guide](14_CICD_Guide.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next: Review Standards](16_Review_Standards.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Return to Contents](../README.md)
