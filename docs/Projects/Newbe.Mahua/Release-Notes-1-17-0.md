---
date: 2019-10-13
title: Newbe.Mahua 1.17 移除 CleverQQ
tags:
    - Newbe.Mahua
    - QQ机器人
    - 更新说明

top: -999
---

CleverQQ 由于众所周知的原因已经下线，现在我们移除了此平台的支持。

<!-- more -->

## 版本亮点

### 移除 CleverQQ

CleverQQ 由于众所周知的原因已经下线，现在我们移除了此平台的支持。

## 升级注意

从 1.16 版本直接更新全部的 Newbe.Mahua.\* nuget 包，重新生成便可以。

升级过程中需要覆盖 build.bat 和 build.ps1 文件。若有自行定制的内容，请提前保留备份。

VS 插件更新只需要按照 VS 提示进行操作即可。

Rider 用户更新项目模板，只需在控制台中运行以下命令即可：

```bash
dotnet new -i Newbe.Mahua.Template
```

<!-- md Nav-Newbe-Mahua-1.X.md -->
