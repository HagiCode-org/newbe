---
date: 2020-01-14
title: Newbe.Mahua 1.18.1 缺陷修复
tags:
    - Newbe.Mahua
    - QQ机器人
    - 更新说明

top: -999
---

对现有的缺陷进行了修复。

<!-- more -->

## 版本亮点

### 修复 CQP 打包错误

若当前打包的类库中引用了非.Net 的类库，可能在打包时出现错误。因此进行了修复。[(#15)](https://github.com/newbe36524/Newbe.Mahua.Framework.V1/issues/15)

## 升级注意

从 1.18 版本直接更新全部的 Newbe.Mahua.\* nuget 包，重新生成便可以。

升级过程中需要覆盖 build.bat 和 build.ps1 文件。若有自行定制的内容，请提前保留备份。

Rider 用户更新项目模板，只需在控制台中运行以下命令即可：

```bash
dotnet new -i Newbe.Mahua.Template
```

<!-- md Nav-Newbe-Mahua-1.X.md -->
