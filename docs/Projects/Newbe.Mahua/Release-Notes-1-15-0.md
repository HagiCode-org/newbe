---
date: 2018-12-25
title: Newbe.Mahua 1.15 支持发送语音
tags:
    - Newbe.Mahua
    - QQ机器人

top: -999
---

很遗憾，我们带来了一个没有彩蛋的版本更新。该版本增加了发送语音的接口，并改进了项目模板，修复了一些 Bug。在此感谢[LollipopGeneral](https://github.com/LollipopGeneral) 的 PR。

<!-- more -->

## 版本亮点

### 支持 Rider 创建项目

更新后的`Newbe.Mahua.Template`项目模板，将支持在 Rider IDE 中直接使用。

![使用Rider创建项目](/images/20181220-001.png)

开发者可以通过右侧链接了解详细的使用方法：[开始第一个QQ机器人【适用于v1.9-1.14】](./Begin-First-Plugin-With-Mahua-In-v1.9)

### 添加了语音发送接口

感谢[LollipopGeneral](https://github.com/LollipopGeneral) 的 PR。

现在，开发者可以使用 FluentApi 进行语音消息的发送。示例代码如下

```csharp
_mahuaApi.SendPrivateMessage("10086").Record("D:\666.mp3").Done();
```

### 移除了对 Newbe.Build.Psake 的依赖

从版本开始，移除了对 Newbe.Mahua.Psake 的依赖。避免用户在升级过程中容易出现构建脚本被覆盖的问题。

在已有项目上进行升级时，需要开发者手动按照以下操作移除相关的包：

1. 卸载 Newbe.Mahua.Tools.Psake
1. 卸载 Newbe.Build.Psake
1. 安装 Newbe.Mahua.Tools.Psake

## 升级注意

从 1.14 版本直接更新全部的 Newbe.Mahua.\* nuget 包，重新生成便可以。

升级过程中需要覆盖 build.bat 和 build.ps1 文件。若有自行定制的内容，请提前保留备份。

VS 插件更新只需要按照 VS 提示进行操作即可。

更新项目模板，只需在控制台中运行以下命令即可：

```bash
dotnet new -i Newbe.Mahua.Template
```

<!-- md Nav-Newbe-Mahua-1.X.md -->
