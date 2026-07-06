# 17. Operations & Delisting


### 17.3 Version Rollback

If severe issues arise after publishing:

1. Submit a rollback request through the Developer Platform with the reason
2. The platform can roll back the application to the previous stable version
3. Users who installed the problematic version will receive a prompt to upgrade to the rolled-back version
4. A post-mortem analysis report must be submitted to the Developer Platform

### 17.4 Application Delisting

#### Developer-Initiated Delisting:
1. Submit a delisting application through the Developer Platform
2. Specify the reason (discontinued, replaced, merged, etc.)
3. Existing users retain the installed application but will no longer receive updates
4. New users can no longer find/install the application
5. Repository resources should be retained for 60 days after delisting for existing users

#### Platform-Enforced Delisting (Violations):
1. The platform issues a violation notice via email
2. Developers have 7 days to respond and rectify
3. If no response is received within 7 days, the application will be forcibly delisted
4. Severe violations (malware, data theft, TOS violations) result in immediate delisting without a grace period

#### Archived (Discontinued):
- Mark the application as "Discontinued" on the Developer Platform
- Users see a "Discontinued — No Longer Maintained" label
- New installations are not permitted
- Existing installations continue to work but no longer receive updates
- Discontinued applications are archived after 12 months

### 17.5 Ongoing Operations

1. **Version Updates**: Each new submission must increment the version number and provide update notes.
2. **Security Patches**: Promptly fix security vulnerabilities and compatibility issues.
3. **Review Feedback**: Respond to platform rectification notices within the specified timeframe and complete fixes.
4. **TOS Compatibility**: Continuously adapt to TOS system updates. Test on new TOS versions before user-version releases.
5. **Repository Maintenance**: Keep public repository resources available long-term. Do not delete published resources.
6. **ABI Monitoring**: Subscribe to TOS release notes and deprecation notices. Plan migrations for announced breaking changes in advance.
7. **Image Updates**: Regularly update base images for Docker applications to include security patches.

---

← [Previous: Review Standards](16_Review_Standards.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next: Commercialization & Donations](18_Commercialization_Donations.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Return to TOC](../README.md)
