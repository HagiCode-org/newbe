---
date: 2018-01-07
title: Newbe.Mahua 1.7.0 支持API扩展
tags:
    - Newbe.Mahua
    - QQ机器人
    - 更新说明
    - 更新说明

top: -999
---

从此版本开始，支持对`IMahuaApi`进行扩展实现。扩展性进一步提升。

<!-- more -->

## 版本亮点

### 支持对`IMahuaApi`进行扩展

允许 SDK 的使用者添加或者替换 IMahuaApi 的实现。从而实现一些原平台不具备或实现不佳的 API。

详细的使用方法可以参考教程：[教程链接](./Newbe-Mahua-ApiExtensions)

### 添加`Newbe.Mahua.*.ApiExtensions`对平台进行 API 扩展

进入了`Newbe.Mahua.*.ApiExtensions`包可以实现对平台原有 API 进行扩展。

详细的使用方法可以参考教程：[教程链接](./Newbe-Mahua-ApiExtensions)

### 支持在构建时修改`Newbe.Mahua.CQP.json`

新版本的构建脚本将支持在构建时自动，按照插件作者信息对`Newbe.Mahua.CQP.json`进行修改。

## 升级注意

从 1.6 版本直接更新全部的 Newbe.Mahua.\* nuget 包，重新生成便可以。

升级过程中若出现需要覆盖`Newbe.Mahua.CQP.json`的提示，允许即可。

VS 插件更新只需要按照 VS 提示进行操作即可。

<!-- md Nav-Newbe-Mahua-1.X.md -->
