# TOS 7 应用开发与上架指南

**版本号：** v2.7  
**最后更新：** 2026-05-27  
**适用平台：** TOS 7.0 及以上版本  
**面向对象：** 全球第三方开发者、独立开发者、企业合作伙伴  

> 📢 本文档当前基于 TOS7.0  版编写，后续 TOS7.x 版本兼容性将保持一致。

---

## 🚀 快速入口

| 场景 | 推荐阅读 |
|------|---------|
| 第一次接触 TOS 应用开发 | [📘 第 3 章 · 快速开始](docs/03_快速开始.md) — 5 分钟跑通流程 |
| 了解整体架构 | [📘 第 2 章 · 应用架构策略](docs/02_应用架构策略.md) — 容器优先策略 |
| 开发 Deb 应用 | [📘 第 8 章 · Deb 开发规范](docs/08_Deb开发规范.md) — 完整规范 |
| 开发 Docker 应用 | [📘 第 9 章 · Docker 开发](docs/09_Docker开发.md) — Docker Compose 指南 |
| 准备上架 | [📘 第 15 章 · 上架流程](docs/15_上架流程.md) — 提交审核 |
| 遇到问题 | [📘 第 19 章 · FAQ](docs/19_FAQ常见问题.md) — 常见问题 |

---

## 📑 完整目录

| 01 | [文档概述](docs/01_文档概述.md) |
| 02 | [应用架构策略](docs/02_应用架构策略.md) |
| 03 | [快速开始](docs/03_快速开始.md) |
| 04 | [包规范](docs/04_包规范.md) |
| 05 | [ABI兼容性](docs/05_ABI兼容性.md) |
| 06 | [开发环境](docs/06_开发环境.md) |
| 07 | [应用类型](docs/07_应用类型.md) |
| 08 | [Deb开发规范](docs/08_Deb开发规范.md) |
| 09 | [Docker开发](docs/09_Docker开发.md) |
| 10 | [权限模型](docs/10_权限模型.md) |
| 11 | [包签名安全](docs/11_包签名安全.md) |
| 12 | [最佳实践](docs/12_最佳实践.md) |
| 13 | [本地测试调试](docs/13_本地测试调试.md) |
| 14 | [CICD指南](docs/14_CICD指南.md) |
| 15 | [上架流程](docs/15_上架流程.md) |
| 16 | [审核标准](docs/16_审核标准.md) |
| 17 | [运维下架](docs/17_运维下架.md) |
| 18 | [商业化捐赠](docs/18_商业化捐赠.md) |
| 19 | [FAQ常见问题](docs/19_FAQ常见问题.md) |
| 20 | [附录合集](docs/20_附录合集.md) |

---

## 📂 仓库结构

```
docs/
├── README.md            ← 你在这里
├── 01_文档概述.md
├── 02_应用架构策略.md
├── 03_快速开始.md
├── 04_包规范.md
├── 05_ABI兼容性.md
├── 06_开发环境.md
├── 07_应用类型.md
├── 08_Deb开发规范.md
├── 09_Docker开发.md
├── 10_权限模型.md
├── 11_包签名安全.md
├── 12_最佳实践.md
├── 13_本地测试调试.md
├── 14_CICD指南.md
├── 15_上架流程.md
├── 16_审核标准.md
├── 17_运维下架.md
├── 18_商业化捐赠.md
├── 19_FAQ常见问题.md
├── 20_附录合集.md
```

---

## 🔗 相关资源

- [TNAS 开发者平台](https://developer.terra-master.com)（即将上线）
- [Deb 应用模板（单包）](https://github.com/terra-master/app-template-deb)
- [Deb 应用模板（双包）](https://github.com/terra-master/app-template-deb-dual)
- [Docker 应用模板](https://github.com/terra-master/app-template-docker)
- [TOS 应用中心](https://terra-master.com)

---

*本文档由 [TOS 7 应用开发与上架指南] 拆分生成，各章节独立维护。*
