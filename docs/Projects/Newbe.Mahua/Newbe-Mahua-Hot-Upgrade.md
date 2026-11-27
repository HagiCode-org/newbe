---
date: 2018-08-02
title: Newbe.Mahua 插件热更新
tags:
  - Newbe.Mahua
  - QQ机器人
  - 教程

top: -999
---

本教程阐述如何在使用 Newbe.Mahua 开发插件时使用"插件热更新"技术。

<!-- more -->

## 软硬条件

| 名           | 值        |
|-------------|----------|
| IDE         | VS2017.5 |
| Newbe.Mahua | 1.11     |

## 项目基础

在阅读本教程之前，想必开发者已经学会了如何插件插件项目。因此本节只将本示例使用的关键参数和代码贴出。

本插件项目名称使用`Newbe.Mahua.Samples.HotUpdate`，使用`Newbe.Mahua.Plugins.Template`模板。

`PluginInfo.cs`文件内容：

```csharp
namespace Newbe.Mahua.Samples.HotUpdate
{
    /// <summary>
    /// 本插件的基本信息
    /// </summary>
    public class PluginInfo : IPluginInfo
    {
        /// <summary>
        /// 版本号，建议采用 主版本.次版本.修订号 的形式
        /// </summary>
        public string Version { get; set; } = "1.0.0";

        /// <summary>
        /// 插件名称
        /// </summary>

        public string Name { get; set; } = "Newbe.Mahua.Samples.HotUpdate";

        /// <summary>
        /// 作者名称
        /// </summary>
        public string Author { get; set; } = "Newbe";

        /// <summary>
        /// 插件Id，用于唯一标识插件产品的Id，至少包含 AAA.BBB.CCC 三个部分
        /// </summary>
        public string Id { get; set; } = "Newbe.Mahua.Samples.HotUpdate";

        /// <summary>
        /// 插件描述
        /// </summary>
        public string Description { get; set; } = "Newbe.Mahua.Samples.HotUpdate";
    }
}
```

新建一个好友消息处理事件（不要忘记注册）：

```csharp
using Newbe.Mahua.MahuaEvents;

namespace Newbe.Mahua.Samples.HotUpdate.MahuaEvents
{
    /// <summary>
    /// 来自好友的私聊消息接收事件
    /// </summary>
    public class PrivateMessageMahuaEventV1
        : IPrivateMessageReceivedMahuaEvent
    {
        private readonly IMahuaApi _mahuaApi;

        public PrivateMessageMahuaEventV1(
            IMahuaApi mahuaApi)
        {
            _mahuaApi = mahuaApi;
        }

        public void ProcessPrivateMessage(PrivateMessageReceivedContext context)
        {
            _mahuaApi.SendPrivateMessage(context.FromQq)
                .Text("嘤嘤嘤 v1")
                .Done();
        }
    }
}
```

运行`build.bat`生成插件文件，复制到机器人平台启动。

那么当向机器人发送任意消息时，将会得到 "嘤嘤嘤 v1" 的回复。

## 开始体验热更新

在上一节项目的基础上，我们再增加一个好友消息处理事件（不要忘记注册）:

```csharp
using Newbe.Mahua.MahuaEvents;

namespace Newbe.Mahua.Samples.HotUpdate.MahuaEvents
{
    /// <summary>
    /// 来自好友的私聊消息接收事件
    /// </summary>
    public class PrivateMessageMahuaEventV2
        : IPrivateMessageReceivedMahuaEvent
    {
        private readonly IMahuaApi _mahuaApi;

        public PrivateMessageMahuaEventV2(
            IMahuaApi mahuaApi)
        {
            _mahuaApi = mahuaApi;
        }
        public void ProcessPrivateMessage(PrivateMessageReceivedContext context)
        {
            _mahuaApi.SendPrivateMessage(context.FromQq)
                .Text("嘤嘤嘤 v2")
                .Done();
        }
    }
}
```

运行`build.bat`生成插件文件。

**注意！从这步开始之后不一样了。**

进入生成了对应平台的文件夹，文件夹中包含一个文件夹名称为**YUELUO**的文件夹。

该文件夹就是"插件热更新"的核心文件夹。

将 YUELUO 文件夹，**复制到对应的机器人平台根目录**。

通过 LogView 日志查看器，便可以看到热更新已经启动。

经过一段时间的等待后，热更新将会结束。

此时，向机器人发送任意消息时，将会得到 "嘤嘤嘤 v1" 和 "嘤嘤嘤 v2" 的两条回复即表示热更新已经成功。

> YUELUO 是 You unknow every lucky ubuntu owner 的缩写。摘自某论坛上 centos 使用者对 ubuntu 使用者的嘲讽。~~
> 绝对没有月落的意思~~

## 其他注意点

### 开始热更新事件 IPluginHotUpgradingMahuaEvent

开发者可以订阅"开始热更新事件"，在插件开始热更新时进行一些操作。并且能够通过参数控制是否取消热更新。

以下便是一个订阅的例子，该示例将允许在奇数秒进行热更新，偶数秒阻止热更新：

```csharp
using Newbe.Mahua.MahuaEvents;
using System;

namespace Newbe.Mahua.Samples.HotUpdate.MahuaEvents
{
    public class PluginHotUpgradingMahuaEvent : IPluginHotUpgradingMahuaEvent
    {
        public void HotUpgrading(
            PluginHotUpgradingContext context)
        {
            if (DateTime.Now.Second % 2 == 0)
            {
                context.Canceled = true;
                context.Reason = "月老板说，该时辰不利于更新！";
            }
        }
    }
}
```

### 热更新成功事件 IPluginHotUpgradedMahuaEvent

开发者可以订阅"热更新成功事件"，在插件热更新成功时进行一些操作。若在"开始热更新事件"中取消了热更新，将不会触发该事件。

以下便是一个订阅的例子，该示例将在热更新成功之后输出一条日志：

```csharp
using Newbe.Mahua.Logging;
using Newbe.Mahua.MahuaEvents;

namespace Newbe.Mahua.Samples.HotUpdate.MahuaEvents
{
    public class PluginHotUpgradedMahuaEvent : IPluginHotUpgradedMahuaEvent
    {
        private static readonly ILog Logger = LogProvider.For<PluginHotUpgradedMahuaEvent>();

        public void HotUpgraded(PluginHotUpgradedContext context)
        {
            Logger.Info("更新完毕，感谢月落大佬的奇妙点子");
        }
    }
}
```

### 插件初始化事件 IInitializationMahuaEvent

该事件原本在插件机器人初始化插件时，将会进行调用。

同时，在热更新成功之后，也将再次触发此事件。

### 热更新过程中的消息

热更新开始后，将会将后续接收的所有的消息进行暂存，在热更新成功之后发送后热更新之后的插件进行处理。

### 热回滚

其实只要将文件夹自行备份就能够自己实现热回滚功能。

## 示例代码

本教程中的所有示例代码，都可以在以下链接获取：

https://github.com/newbe36524/Newbe.Mahua.Framework/tree/master/src/Newbe.Mahua.Samples.HotUpdate

<!-- md Nav-Newbe-Mahua-1.X.md -->
