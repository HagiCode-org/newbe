---
date: 2019-05-05
title: Newbe.Mahua CQP 紧急故障修复
tags:
    - Newbe.Mahua
    - QQ机器人

top: -999
---

此次版本发布主要围绕"CQP 紧急故障修复"。

<!-- more -->

## 版本亮点

### CQP 紧急故障修复

由于 CQP 进行了命名规则改换，导致 SDK 全部失效，因此特别紧急修复发布版本。

此次修复版本包括最新的 1.X 、 2.X 和 LTS 版本。更新后的版本号如下所示：

-   1.12.1
-   1.15.1
-   2.1.1

## 手动修复

CQP 此次变更后要求 AppID 为全小写字母组成。因此，本 SDK 需要对构建脚本进行修改，既可以修复该问题。

若开发者使用的不是上述罗列的主要版本，也可以不升级最新 SDK。使用以下链接中所示的修改，对 build.ps1 脚本进行调整即可：

[点击查看修改 build.ps1 的详细方法](https://github.com/newbe36524/Newbe.Mahua.Framework/pull/65/commits/955e210ee0ec0f4ed93e7f8799dbaaff64cad0d9)

## 升级注意

### 1.X

从 1.X 版本直接更新全部的 Newbe.Mahua.\* nuget 包，重新生成便可以。

升级过程中若出现需要覆盖 build.ps1 的提示，允许即可。

### 2.X

使用命令行在机器人 exe 根目录运行以下命令

```bash
mahua InstallMahua
```

注意：升级过程将会覆盖以下配置文件，若开发者有自行定制过这些配置项，需要先自行备份：

-   mahua.json
-   NLog.config

<!-- md Nav-Newbe-Mahua-1.X.md -->
