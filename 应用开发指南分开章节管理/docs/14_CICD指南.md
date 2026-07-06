# 14. CICD指南

### 14.1 GitHub Actions 模板


**必需的仓库 Secrets：**
在 GitHub 仓库 Settings → Secrets and Variables → Actions 中配置：

| Secret 名称 | 说明 | 是否必需 |
|---|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub 用户名（用于推送镜像） | Docker 应用需要 |
| `DOCKERHUB_TOKEN` | Docker Hub 访问令牌（非密码） | Docker 应用需要 |
| `GPG_PRIVATE_KEY` | GPG 私钥用于包签名（未来） | 可选 |
| `GPG_PASSPHRASE` | GPG 密钥密码 | 可选 |

> 切勿在工作流文件中硬编码凭据。始终使用 GitHub Secrets。

**Deb 应用**使用以下 GitHub Actions 工作流：

```yaml
# .github/workflows/build-deb.yml
name: 构建 Deb 包

on:
  push:
    tags:
      - 'v*'
  pull_request:
    branches: [main]

jobs:
  build:
    strategy:
      matrix:
        arch: [amd64, arm64]
        include:
          - arch: amd64
            runner: ubuntu-latest
          - arch: arm64
            runner: ubuntu-latest

    runs-on: ${{ matrix.runner }}

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 设置 QEMU（arm64）
        if: matrix.arch == 'arm64'
        uses: docker/setup-qemu-action@v3

      - name: 安装构建依赖
        run: |
          sudo apt-get update
          sudo apt-get install -y dpkg-dev debhelper lintian

      - name: 构建 deb 包
        run: |
          dpkg-deb --build ./app-root ./<appid>_${{ github.event.release.tag_name }}_${{ matrix.arch }}.deb

      - name: 校验包
        run: |
          dpkg-deb -c ./*.deb
          dpkg-deb -I ./*.deb
          lintian ./*.deb || true

      - name: 生成校验和
        run: |
          sha256sum ./*.deb > ./*.deb.sha256

      - name: 上传产物
        uses: actions/upload-artifact@v4
        with:
          name: deb-${{ matrix.arch }}
          path: |
            *.deb
            *.sha256

  release:
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')

    steps:
      - name: 下载产物
        uses: actions/download-artifact@v4

      - name: 创建 GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            deb-amd64/*.deb
            deb-amd64/*.sha256
            deb-arm64/*.deb
            deb-arm64/*.sha256
```

### 14.2 多架构构建

**Docker 应用**：

```yaml
# .github/workflows/build-docker.yml
name: 构建并推送 Docker 镜像

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 设置 QEMU
        uses: docker/setup-qemu-action@v3

      - name: 设置 Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: 登录 Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: 构建并推送
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/<appid>:latest
            ${{ secrets.DOCKERHUB_USERNAME }}/<appid>:${{ github.ref_name }}

      - name: 安全扫描
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: '${{ secrets.DOCKERHUB_USERNAME }}/<appid>:${{ github.ref_name }}'
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
```

### 14.3 自动化校验

添加校验工作流，每次推送时检查配置文件：

```yaml
# .github/workflows/validate.yml
name: 校验配置

on:
  push:
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 校验 config.ini（JSON格式）
        run: |
          python3 -c "import json; json.load(open('config.ini'))"
          echo "config.ini JSON 格式有效"

      - name: 校验必填字段
        run: |
          python3 -c "
          import json
          config = json.load(open('config.ini'))
          required = ['id', 'icon', 'publisher', 'exec', 'version', 'low_version',
                      'category', 'depend', 'platform', 'application_type', 'user',
                      'all_user_display', 'allow_open_in_mobile']
          for field in required:
              assert field in config, f'缺少必填字段: {field}'
          
          # 校验 Deb 专属字段
          if config['application_type'] == 'deb':
              assert config.get('system_id'), 'Deb 应用必须有 system_id'
              assert config.get('package'), 'Deb 应用必须有 package'
          
          # 校验分类数量
          assert len(config['category']) <= 3, '最多3个分类'
          
          print('所有校验通过！')
          "

      - name: 校验 app.lang（14种语言）
        run: |
          python3 -c "
          required_langs = ['zh-cn', 'zh-hk', 'en-us', 'fr-fr', 'de-de', 
                           'it-it', 'es-es', 'hu-hu', 'ja-jp', 'ko-kr',
                           'pl-pl', 'ru-ru', 'tr-tr', 'pt-pt']
          with open('app.lang', 'r') as f:
              content = f.read()
          for lang in required_langs:
              assert f'[{lang}]' in content, f'缺少语言: {lang}'
          print('14种语言全部存在！')
          "

      - name: 校验图标（SVG 格式）
        run: |
          python3 -c "
          import json, os
          config = json.load(open('config.ini'))
          icon_path = config['icon']
          icon_file = icon_path.lstrip('/')
          assert os.path.exists(icon_file), f'图标未找到: {icon_file}'
          with open(icon_file, 'r') as f:
              content = f.read()
          assert '<svg' in content and '</svg>' in content, '不是有效的 SVG 文件'
          assert 'viewBox' in content, 'SVG 缺少 viewBox 属性'
          print(f'图标校验通过: {icon_file}')
          "

```

> **Gitee Actions（中国开发者）：** 对于在 Gitee 上托管的开发者，请将 GitHub Actions 工作流适配为 Gitee CI/CD 格式。完整的 Gitee CI/CD 模板可在 TNAS 开发者平台上获取。Gitee 使用 `gitee-ci.yml` 配置格式。请参阅 Gitee 文档了解环境设置。

### 14.4 发布与上传

构建成功后：

1. 创建包含 deb 包和校验和的 GitHub Release
2. 如需要，更新仓库的 config.ini 和 app.lang
3. 通过 TNAS 开发者平台提交新版本
4. 将 Release 标签与版本提交关联

---

← [上一章：本地测试调试](13_本地测试调试.md) &nbsp;&nbsp;|&nbsp;&nbsp; [下一章：上架流程](15_上架流程.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 返回总目录](../README.md)
