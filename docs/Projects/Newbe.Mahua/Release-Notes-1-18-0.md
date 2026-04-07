---
date: 2019-12-17
title: Newbe.Mahua 1.18 恢复 QQLight
tags:
    - Newbe.Mahua
    - QQ机器人
    - 更新说明

top: -999
---

QQLight 由于众所周知的原因已经升级到了 3.X 的 SDK，旧版本全部失效，现在我们更新了版本以重新支持。

<!-- more -->

## 版本亮点

### 恢复 QQLight

QQLight 由于众所周知的原因已经升级到了 3.X 的 SDK，旧版本全部失效，现在我们更新了版本以重新支持。

### 更新其他平台的 API

由于其他平台的 API 也发生了若干变更，因此，我们也按照当前最新的情况更新了 API 。

## 升级注意

从 1.17 版本直接更新全部的 Newbe.Mahua.\* nuget 包，重新生成便可以。

升级过程中需要覆盖 build.bat 和 build.ps1 文件。若有自行定制的内容，请提前保留备份。

Rider 用户更新项目模板，只需在控制台中运行以下命令即可：

```bash
dotnet new -i Newbe.Mahua.Template
```

<!-- md Nav-Newbe-Mahua-1.X.md -->
