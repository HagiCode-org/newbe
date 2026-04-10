## 1. Manifest Ingestion

- [x] 1.1 在 `tools/mirrorsDef.json` 为 `ollama` 增加 Azure manifest 来源、仓库标识和推荐 provider 顺序等配置字段，并保持其他镜像仓库向后兼容。
- [x] 1.2 在 `tools/tasks.py` 中实现 Azure manifest 的拉取、解析和缓存入口，支持把远程 JSON 归一化为仓库 / 版本 / 资产 / provider / share URL 记录。
- [x] 1.3 补充 Python 测试，覆盖 manifest 获取成功、请求失败、JSON 非法和仓库未启用 manifest 的路径。

## 2. Asset Matching And Page Generation

- [x] 2.1 扩展 GitHub mirror 生成流程，按仓库、版本和资产名称把 manifest 记录匹配到 GitHub release 资产，并只为准确命中的资产附加 provider 直链。
- [x] 2.2 修改 `tools/mirror/github/__init__.py` 和相关生成逻辑，让 `GithubMirrorLink` 调用可携带按资产解析后的镜像连接列表，而不是只传原始 GitHub 链接。
- [x] 2.3 重新生成并复核 `docs/Mirrors/Mirrors-ollama.md`，确认有同步记录的资产会输出 123pan 推荐项，未同步资产继续输出默认代理。

## 3. Frontend Mirror Strategy

- [x] 3.1 在 `src/components/GithubMirrorLink/types.ts` 和 `config.ts` 中定义统一的已解析镜像连接类型，兼容 provider 直链、默认代理和官方源。
- [x] 3.2 更新 `src/components/GithubMirrorLink/index.tsx` 的分组与排序逻辑，使其按仓库策略把 123pan 放到 Ollama 的推荐区首位，同时保留默认推荐代理、备用代理和官方源。
- [x] 3.3 复核 `MirrorCard`、`MirrorSection` 与现有样式，确保新增 provider 卡片不破坏现有弹窗布局、复制逻辑和键盘交互。

## 4. Verification And Documentation

- [x] 4.1 新增或更新 Python 回归测试，验证 Ollama 页面生成时的推荐排序、资产级错配防护和降级行为。
- [x] 4.2 运行 `python -m unittest tools.tests.test_ollama_123pan_manifest` 以及相关 mirror 回归测试，确认生成逻辑满足 `github-mirror-share-manifest` 和 `github-mirror-connection-strategy` 的场景。
- [x] 4.3 运行 `npm run typecheck`，必要时补充实现注释或文档说明，明确 Azure manifest 契约和 provider 扩展约束。
