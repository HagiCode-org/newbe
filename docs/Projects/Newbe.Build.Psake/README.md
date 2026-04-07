---
date: 2019-05-18
title: Newbe.Build.Psake 编写自动化构建脚本
tags:
 - Newbe.Build.Psake
 - Web
 - 网站开发
 - 自动化构建
 - powershell
 - 教程
---

编写脚本可以将很多繁琐重复的工作进行简化。本篇将介绍一种基于 powershell 的脚本框架。基于该框架，开发者可以方便的编写和维护自己的自动化脚本。

<!-- more -->

## 抄起脚本一把梭

对项目进行持续集成和持续发布是现在项目开发中非常基础的要求。现在可选的自动化构建引擎很多。Jenkins、Gitlab、TFS、TeamCity等都是很好的选择。很多项目都基于这些自动化构建引擎实现了项目的持续集成和持续发布。

一般，自动化引擎都提供了简单的构建步骤，开发者可以直接使用内置的步骤，便可以实现自动化需求。不过，为了更强的自定义需求，开发者往往需要自己编写一些脚本，然后使用自动化引擎进行构建。例如：发送钉钉通知，这样的需求，自动化引擎没有提供专门的插件实现这些需求。

自动化引擎一般都提供了“直接执行脚本”的步骤。直接使用这样的步骤，开发者可以直接填入脚本实现需求。但是，本文将介绍一种更为合理的方案来解决这样的需求。

## Powershell

Powershell 是微软提供的一种脚本语言。在最新的 Powershell 6 中，由于基于 Netcore 2.0 作为运行时，Powershell 6 具备了跨平台运行的特性。因此，使用这种脚本语言编写的脚本可以在不同的操作系统平台上运行。

## Psake

Psake 是一个基于 Powershell 的脚本语言框架。通过这种框架，可以结构化的管理自己的脚本。使得自己的脚本更加易读，便于管理。

以下便是采用 Psake 框架编写的构建脚本，这段脚本展示了编译一个解决方案的基础过程。

```powershell
properties {
    # 定义一个变量，指向当前文件夹所在的位置
    $rootNow = Resolve-Path .
}

# 默认任务。调用该脚本时，如果没有指定执行的任务，那么将会执行这个任务
# 通过 -depends 指定该任务所依赖的上级任务
Task Default -depends Build

# 调用 dotnet 来执行 nuget 还原的操作。
Task Nuget -Description "nuget restore" {
    Exec {
        dotnet restore
    }
}

# 调用 dotnet 执行编译操作。
Task Build -depends Nuget -Description "build sln" {
    Exec {
        dotnet build -c "Release"
    }
}
```

TODO 还没写完
