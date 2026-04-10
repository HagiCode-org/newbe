## 1. Catalog Updates

- [ ] 1.1 审核 `tools/mirrorsDef.json` 中现有 `PowerToys`、`PowerShell` 条目，确认本次变更按“保留并复核”处理而不是重复新增。
- [ ] 1.2 在 `tools/mirrorsDef.json` 中补充缺失的 12 个 A 档 GitHub 仓库定义，并为每个条目设置一致的 `softwareName`、`officialSite`、`markdownFilename` 与生成元数据。
- [ ] 1.3 为新增 A 档仓库建立清晰的文件命名映射，确保定义项、描述文件和生成页面之间一一对应。

## 2. Content Sources

- [ ] 2.1 为每个新增 A 档仓库创建对应的 `tools/MirrorDescription/*.md` 文案文件。
- [ ] 2.2 为 `OpenAgentPlatform/Dive` 写入可用的临时业务说明，并在文案中标记后续可继续优化。
- [ ] 2.3 复核新增文案是否与仓库定位、目标用户和大体积 Release 分发价值保持一致。

## 3. Generation And Compatibility

- [ ] 3.1 使用现有 Mirror 生成流程为新增仓库生成 `docs/Mirrors/*.md` 页面。
- [ ] 3.2 验证现有 `PowerToys`、`PowerShell` 页面在本次目录更新后仍可正常生成且未出现重复内容。
- [ ] 3.3 如果新增仓库暴露出 `tools/tasks.py` 的兼容性问题，仅针对必要点修正 GitHub Mirror 生成逻辑。

## 4. Verification

- [ ] 4.1 为镜像目录覆盖、页面生成路径或重复定义检查补充自动化测试。
- [ ] 4.2 校验新增 A 档仓库都具备“定义项 + 描述文件 + 生成页面”三件套。
- [ ] 4.3 运行相关验证，确认变更达到 `mirror-tier-a-catalog` spec 中的全部验收场景。
