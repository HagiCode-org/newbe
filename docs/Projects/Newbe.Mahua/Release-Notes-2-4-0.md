---
date: 2019-12-17
title: Newbe.Mahua 2.4 恢复 QQLight
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

## 升级方法与要点

使用命令行在机器人 exe 根目录运行以下命令

```bash
mahua InstallMahua
```

注意：升级过程将会覆盖以下配置文件，若开发者有自行定制过这些配置项，需要先自行备份：

-   mahua.json
-   NLog.config

<!-- md Nav-Newbe-Mahua-2.X.md -->
