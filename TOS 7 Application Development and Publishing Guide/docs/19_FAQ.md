# 19. FAQ

### 19.1 Review Related

**Q: What should I do if my review is rejected?**  
Review the rejection reason, make corrections, and resubmit. Common rejection reasons include: JSON format errors, version number not incremented, missing language files, port conflicts. See the Review Standards chapter for details.

**Q: How long does the review take?**  
Typically 3–5 business days. Initial submissions may take longer (full manual review of all content). Version update reviews are usually faster (typically 1–3 business days).

**Q: Can the application ID be modified?**  
Once created, it cannot be modified. Please carefully confirm the application ID before publishing.

### 19.2 Technical Issues

**Q: What should I do about port conflicts?**  
- System-reserved ports are prohibited: 22, 80, 443, 8181, 5050
- Recommended range: 8000–19999
- Check port occupancy in the preinst script before installation
- Different applications use different ports; the platform does not auto-assign ports

**Q: What are the version number rules?**  
- Follow Semantic Versioning (SemVer): `MAJOR.MINOR.PATCH`
- Each submission must be strictly greater than the previous version; downgrades are prohibited
- Beta versions use the `"beta": true` field; version number suffixes (-beta/-rc) are not supported
- Maximum version number length: 20 characters

**Q: Single-package or dual-package?**  
- Starting from scratch → Single-package mode (all files integrated into a single deb package)
- Already have a generic standard deb package, complex build → Dual-package mode (source package + data package)
- Simple binary program → Single-package mode

**Q: The config.ini file has a .ini extension but its content is JSON — why?**  
This is a company historical convention. The file extension remains `.ini`, but the parser processes it as JSON format.

### 19.3 Installation & Runtime

**Q: What should I do if application installation fails?**  
1. Check `systemctl status <system_id>` to view service status
2. Check `journalctl -u <system_id> -n 50` to view service logs
3. Confirm all required fields in config.ini are correctly filled
4. Confirm systemd service file paths and permissions are correct
5. Confirm ports are not occupied: `ss -tlnp | grep <port>`

**Q: How do I debug a WebUI-internal application?**  
1. Check if `/var/api/<app_id>.sock` exists
2. Use `curl --unix-socket /var/api/<app_id>.sock http://localhost/` to test the backend directly
3. In the browser DevTools Network panel, check `/v2/proxy/<app_id>/` requests
4. Confirm the frontend correctly sends the `Cookie` and `X-Csrf-Token` headers

**Q: How do I debug a WebUI-external application?**  
1. Check if the backend listens on `0.0.0.0:<port>` (not 127.0.0.1)
2. Check the nginx configuration file path and syntax: `nginx -t`
3. Access `http://<TNAS_IP>:<port>` directly to confirm the backend responds correctly
4. Confirm the nginx location block's proxy_pass port matches the backend listening port

### Appendix A: Category List

---

← [Previous: Commercialization & Donations](18_Commercialization_Donations.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next: Appendix](20_Appendix.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Return to TOC](../README.md)
