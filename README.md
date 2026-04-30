# newbe

`newbe` 是一个基于 Docusaurus 的静态站点，生产地址为 [newbe.hagicode.com](https://newbe.hagicode.com)。

## 本地启动

```bash
cd repos/newbe
npm install
npm run dev
```

## 构建与校验

```bash
npm run build
```

当前生产发布不再使用 `docusaurus deploy`。权威发布路径由 GitHub Actions 接管。

## 生产部署

- 权威工作流：`.github/workflows/newbe-deploy-gh-pages.yml`
- 生产 source of truth：`gh-pages` 分支，只允许 CI 发布经过验证的快照
- 发布 payload 契约：分支根目录保留 `esa.jsonc`，Docusaurus `build/` 输出会在发布前归一化复制到 `dist/`
- 所需 GitHub 权限：deploy job 需要 `contents: write`
- 所需托管设置：托管层应读取 `gh-pages/esa.jsonc`，并把 `gh-pages/dist/` 作为站点目录
- 首次部署检查：确认工作流上传了 `esa.jsonc` 与 `dist/`，确认 `dist/` 内含 Docusaurus 站点资源，然后验证 `https://newbe.hagicode.com`
- 回滚方式：回退 source 提交，或从旧提交重新运行工作流，让 CI 重新发布之前的分支快照
