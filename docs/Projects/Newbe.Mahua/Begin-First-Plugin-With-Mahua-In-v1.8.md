---
date: 2018-04-21
title: 开始第一个QQ机器人【适用于v1.8】
tags:
  - Newbe.Mahua
  - QQ机器人
  - CQP
  - Amanda
  - MPQ
  - 教程
top: -999
---

本示例将会使用"嘤鹉学舌"这个小插件的实现来演示如何使用`Newbe.Mahua`实现第一个机器人插件。

<!-- more -->

## 插件功能

自动将发送者的消息回发给发送人，嘤鹉（Parrot，其实是说嘤嘤嘤怪）学舌。

## 开发环境要求

- .Net Framework 4.5.2 及以上
- Visual Studio 2017（VS2015 update 3 理论上也能够开发，但开发遇到的问题，需自行解决）
- powershell 3.0 及以上

## 设置 Powershell 执行策略限制

参考链接：http://www.pstips.net/powershell-create-and-start-scripts.html

简单来说，使用管理员权限在 cmd 中运行以下命令:

```bash
powershell -command "Set-ExecutionPolicy RemoteSigned -Force"
```

## 安装 VS 扩展

从 VS 扩展商店下载最新的 VS 扩展，下载地址为：https://marketplace.visualstudio.com/items?itemName=Newbe36524.NewbeMahuaVsExtensions

若出现下载不畅通，也可以通过加入技术交流群，在群文件中进行下载。[点击加入 Newbe.Mahua 群【610394020】](https://jq.qq.com/?_wv=1027&k=4AMMCTx)

**安装过程可能需要花费若干分钟，需耐心等待。**

**安装完毕，需要重启所有 VS 方可生效。**

## 新建项目

项目名称**至少**需要包含三部分，形如 AAA.BBB.CCC 的形式。

新建项目时，可以根据"希望支持的插件平台"来选择特定后缀的项目模板来安装。

`Newbe.Mahua.Plugins.Template`是安装了所有平台支持包的项目模板。本示例将使用此项目模板进行演示。

本插件项目名称使用`Newbe.Mahua.Plugins.Parrot`。

![新建项目](/images/20171216-001.png)

## 修改插件基本信息

打开`PluginInfo.cs`文件，按照实际需求和注释内容进行修改。

```csharp
namespace Newbe.Mahua.Plugins.Parrot
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

        public string Name { get; set; } = "嘤鹉学舌";

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
        public string Description { get; set; } = "嘤鹉学舌，是一个使用Mahua框架开发的第一个插件。该插件实现将好友的私聊消息回发给好友的功能。";
    }
}
```

## 添加"接收好友消息事件"代码实现

在`MahuaEvents`处右键，选择"添加->新建项"。

> MahuaEvents 文件夹是本 SDK 建议将事件放置的文件夹位置。也可以不接受建议而添加在其他地方。

![添加->新建项](/images/20171216-002.png)

如下图所示，选择"来自好友的私聊消息接收事件"。

![新建好友消息处理事件](/images/20171217-001.png)

在`PrivateMessageFromFriendReceivedMahuaEvent.cs`中，调用`IMahuaApi`，将好友消息回发给好友，实现嘤鹉学舌的效果。

```csharp
using Newbe.Mahua.MahuaEvents;

namespace Newbe.Mahua.Plugins.Parrot.MahuaEvents
{
    /// <summary>
    /// 来自好友的私聊消息接收事件
    /// </summary>
    public class PrivateMessageFromFriendReceivedMahuaEvent
        : IPrivateMessageFromFriendReceivedMahuaEvent
    {
        private readonly IMahuaApi _mahuaApi;

        public PrivateMessageFromFriendReceivedMahuaEvent(
            IMahuaApi mahuaApi)
        {
            _mahuaApi = mahuaApi;
        }

        public void ProcessFriendMessage(PrivateMessageFromFriendReceivedContext context)
        {
          // 戳一戳
          _mahuaApi.SendPrivateMessage(context.FromQq)
              .Shake()
              .Done();

          // 嘤嘤嘤，换行，重复消息
          _mahuaApi.SendPrivateMessage(context.FromQq)
              .Text("嘤嘤嘤：")
              .Newline()
              .Text(context.Message)
              .Done();
        }
    }
}
```

## 在模块中注册事件

打开`MahuaModule.cs`文件，在`MahuaEventsModule`中注册刚刚添加的`PrivateMessageFromFriendReceivedMahuaEvent`。

```csharp
using Autofac;
using Newbe.Mahua.MahuaEvents;
using Newbe.Mahua.Plugins.Parrot.MahuaEvents;

namespace Newbe.Mahua.Plugins.Parrot
{
    /// <summary>
    /// Ioc容器注册
    /// </summary>
    public class MahuaModule : IMahuaModule
    {
        public Module[] GetModules()
        {
            // 可以按照功能模块进行划分，此处可以改造为基于文件配置进行构造。实现模块化编程。
            return new Module[]
            {
                new PluginModule(),
                new MahuaEventsModule(),
            };
        }

        /// <summary>
        /// 基本模块
        /// </summary>
        private class PluginModule : Module
        {
            protected override void Load(ContainerBuilder builder)
            {
                base.Load(builder);
                // 将实现类与接口的关系注入到Autofac的Ioc容器中。如果此处缺少注册将无法启动插件。
                // 注意！！！PluginInfo是插件运行必须注册的，其他内容则不是必要的！！！
                builder.RegisterType<PluginInfo>()
                    .As<IPluginInfo>();

            }
        }

        /// <summary>
        /// <see cref="IMahuaEvent"/> 事件处理模块
        /// </summary>
        private class MahuaEventsModule : Module
        {
            protected override void Load(ContainerBuilder builder)
            {
                base.Load(builder);
                // 将需要监听的事件注册，若缺少此注册，则不会调用相关的实现类
                builder.RegisterType<PrivateMessageFromFriendReceivedMahuaEvent>()
                    .As<IPrivateMessageFromFriendReceivedMahuaEvent>();
            }
        }
    }
}
```

## 生成与打包

生成项目，然后双击位于项目根目录的`build.bat`文件。

![build.bat执行成功](/images/20171217-002.png)

## 复制文件到机器人平台

在`bin`目录下会按照当前安装的平台生成相应的目录。本示例将会生成 CQP、Amanda 和 MPQ 三个目录。

**分别将三个文件夹下的所有文件和文件夹都复制到对应的机器人平台根目录**。

各机器人软件下载地址：

| 名称     | 地址                                       |
|--------|------------------------------------------|
| CQP    | https://cqp.cc/                          |
| MPQ    | https://f.mypcqq.cc/thread-2327-1-1.html |
| Amanda | http://www.52chat.cc/                    |

## 启用插件

各个机器人平台的启用方式各不相同。

### CQP

按照下图所示，开启开发者模式。

![开启开发者模式](/images/20171218-001.jpg)

打开插件管理将插件启用。

### MPQ

打开插件管理将插件启用。

### Amanda

打开插件管理将插件启用。

## 成功！

发送消息给机器人，你就会收到机器人回发的信息。

> 机器人插件启动可能需要一段时间，并且大多数平台都会丢弃离线信息，可能需要等待一会儿在发送。

<!-- md Nav-Newbe-Mahua-1.X.md -->
