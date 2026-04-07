---
date: 2017-06-03
title: 开始第一个插件【适用于v1.0-1.1】
tags:
  - Newbe.Mahua
  - QQ机器人
  - CQP
  - Amanda
  - 教程
top: -999
---

本示例将会使用"鹦鹉学舌"这个小插件的实现来演示如何使用`Newbe.Mahua`实现第一个机器人插件。

**Newbe.Mahua.Framework 已于 2020 年 8 月 2 日 正式归档，源码将不再更新。**

<!-- more -->

## 插件功能

自动将发送者的消息回发给发送人，鹦鹉（英文：Parrot）学舌。

## 环境要求

- .Net Framework 4.5.2 及以上
- Visual Studio 2015 update 3 及以上(推荐 2017)

> 以下内容均采用 vs2017 作为演示 IDE

## 新建项目

项目名称**至少**需要包含三部分，形如 AAA.BBB.CCC 的形式。

![新建项目](/images/20170613-d51f6524.png)

## 安装 nuget 包

![安装nuget包](/images/20170613-f51fc24f.png)

打开 nuget 包管理器，搜索`Mahua`。根据你希望运行的机器人平台安装`Newbe.Mahua.*`的 nuget 包。

本示例希望运行在多个平台上，因此安装以下 nuget 包：

- Newbe.Mahua.CQP
- Newbe.Mahua.Amanda

> 若想要安装最新的开发版，可以勾选"包含预发行版"。 由于框架在不断演进，因此尽可能早的升级到最新的版本。

## 修改`Newbe.Mahua.props`文件

```xml
<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup>
      <!--修改插件名称-->
    <MahuaPluginName>Newbe.Mahua.Plugins.Parrot</MahuaPluginName>
  </PropertyGroup>
</Project>
```

## 实现插件

新建`MahuaModule.cs`文件，将以下代码复制进去：

```csharp
using System;
using Autofac;
using Newbe.Mahua.MahuaEvents;

namespace Newbe.Mahua.Plugins.Parrot
{
    /**
     * 此文件为了演示方便，将所有的类合并在同一个文件中，实际项目中可以根据要求分开放置
     */

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

        public string Name { get; set; } = "鹦鹉学舌";

        /// <summary>
        /// 作者名称
        /// </summary>
        public string Author { get; set; } = "Newbe";

        /// <summary>
        /// 插件Id，用于唯一标识插件产品的Id，至少包含 AAA.BBB.CCC 三个部分
        /// </summary>
        public string Id { get; set; } = "Newbe.Mahua.Plugins.Parrot";

        /// <summary>
        /// 插件描述
        /// </summary>
        public string Description { get; set; } = "鹦鹉学舌，是一个使用Mahua框架开发的第一个插件。该插件实现将好友的私聊消息回发给好友的功能。";
    }

    /// <summary>
    /// 监听来自好友的私聊消息事件
    /// </summary>
    public class PrivateMessageFromFriendReceivedMahuaEvent : IPrivateMessageFromFriendReceivedMahuaEvent
    {
        private readonly IMahuaApi _mahuaApi;

        /// <summary>
        /// 采用构造函数注入<see cref="IMahuaApi"/>，以便后续调用
        /// </summary>
        /// <param name="mahuaApi"></param>
        public PrivateMessageFromFriendReceivedMahuaEvent(IMahuaApi mahuaApi)
        {
            _mahuaApi = mahuaApi;
        }

        /// <summary>
        /// 处理事件
        /// </summary>
        /// <param name="context"></param>
        public void ProcessFriendMessage(PrivateMessageFromFriendReceivedContext context)
        {
            //调用_mahuaApi实现将消息回发给好友的功能
            _mahuaApi.SendPrivateMessage(context.FromQq, context.Message);
        }
    }

    /// <summary>
    /// Ioc容器注册
    /// </summary>
    public class MahuaModule : IMahuaModule
    {
        public Module[] GetModules()
        {
            return new Module[] {new PluginModule(),};
        }

        private class PluginModule : Module
        {
            protected override void Load(ContainerBuilder builder)
            {
                //将相关的实现类注册到，此处可以根据自定义的配置文件进行按需加载，可以自行发挥想象力。
                base.Load(builder);
                //将实现类与接口的关系注入到Autofac的Ioc容器中。如果此处缺少注册将无法启动插件。注意！！！PluginInfo是插件运行必须注册的，其他内容则不是必要的！！！
                builder.RegisterType<PluginInfo>().AsImplementedInterfaces();
                //将需要监听的事件注册，若缺少此注册，则不会调用相关的实现类
                builder.RegisterType<PrivateMessageFromFriendReceivedMahuaEvent>().AsImplementedInterfaces();
            }
        }
    }
}
```

## 生成解决方案

若出现生成失败请多次重试，多次重试失败请认栽。

## 复制文件到机器人平台

在`bin`目录下会按照当前安装的平台生成相应的目录。本示例将会生成 CQP 和 Amanda 两个目录。

分别将两个目录中的文件复制到对应的**机器人平台根目录**。

## 启用插件

### CQP

打开酷 Q 文件夹下的 `conf\CQP.cfg` 文件，并在文件末尾插入以下两行，即可开启开发者模式。

```ini
[Debug]
DeveloperMode=1
```

打开插件管理将插件启用。

### Amanda

打开插件管理将插件启用。

## 成功！

发送消息给机器人，你就会收到机器人回发的信息。

> 机器人插件启动可能需要一段时间，并且大多数平台都会丢弃离线信息，可能需要等待一会儿在发送。
