---
date: 2020-02-16
title: Newbe.Mahua 1.18.2 修复项目模板
tags:
    - Newbe.Mahua
    - QQ机器人
    - 更新说明

top: -999
---

对现有的项目模板进行修复。

<!-- more -->

## 版本亮点

### 修复项目模板错误

由于 Autofac 和 MessagePack 的最新版本已经不再支持 Net 4.5.2 ，因此项目模板构建时会出现错误。

通过限定最高版本号解决了该问题。[(#24)](https://github.com/newbe36524/Newbe.Mahua.Framework.V1/issues/24)

## 升级注意

已经创建过的项目，无论是否升级都没有影响，此次只对新建的项目产生影响。

只要控制台中运行以下命令即可升级至最新的项目模板：

```bash
dotnet new -i Newbe.Mahua.Template
```

<!-- md Nav-Newbe-Mahua-1.X.md -->
