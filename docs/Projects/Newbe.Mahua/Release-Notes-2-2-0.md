---
date: 2019-09-22
title: Newbe.Mahua 2.2 可用性修复
tags:
    - Newbe.Mahua
    - QQ机器人
    - 更新说明

top: -999
---

修复了 CQP 和 CleverQQ 不可用的问题。加快模板安装速度。

<!-- more -->

## 版本亮点

### 可用性修复

修复了以下平台近期由于平台更新导致 SDK 不可用的问题：

-   CQP
-   CleverQQ

**虽说该版本是一个次要更新版本，但实际上现在版本在这两个平台上已经完全失效，必须升级为最新版本。**

下载了源码的开发者，可以根据最新提交的代码 diff 来修正自己项目

### 优化 Installer 安装速度

在国内仍然有开发者反映依赖于 nuget 的模板下载安装速度不快。

因此，我们将最新的项目模板所需要的文件都进行了“离线化”处理，使得下载过程更加流畅。

由于有初学开发者无法区别“下载 HTML”和“下载脚本”的区别，因此，我们制作了打包下载的方式托管于码云上。[点击此处查看 Installer 压缩包](https://gitee.com/yks/Newbe.Mahua.Framework/releases/v2.2)

## 升级方法与要点

使用命令行在机器人 exe 根目录运行以下命令

```bash
mahua InstallMahua
```

注意：升级过程将会覆盖以下配置文件，若开发者有自行定制过这些配置项，需要先自行备份：

-   mahua.json
-   NLog.config

<!-- md Nav-Newbe-Mahua-2.X.md -->
