---
date: 2018-01-07
title: Newbe.Mahua.Samples.ApiExtensions 对IMahuaApi进行扩展
tags:
  - Newbe.Mahua
  - QQ机器人
  - 教程

top: -999
---

本教程将通过对 CQP 进行 API 扩展为例，来实现以下功能：

- 扩展 CQP 原生不支持的获取好友列表接口
- 替换 CQP 原生的发送好友消息接口
- 通过`Newbe.Mahua.CQP.ApiExtensions`实现扩展 CQP 原生不支持的发送群公告接口

对于其他平台的扩展都可以参考此教程。

<!-- more -->

## 软硬条件

| 名           | 值        |
|-------------|----------|
| IDE         | VS2017.5 |
| Newbe.Mahua | 1.7      |

## 业务逻辑

当收到好友消息的时候，获取好友列表。

将好友列表的数据写入到群公告中。

替换发送好友消息接口，实际上将好友消息写入到日志文件中。

## 新建项目

使用`Newbe.Mahua.Plugins.Template`模板创建项目，项目名称为`Newbe.Mahua.Samples.ApiExtensions`。

新建项目的详细细节，可以参照右侧链接内容：[新建项目](./Begin-First-Plugin-With-Mahua-In-v1.4)

## 业务逻辑实现

本教程主要为了演示 API 的调用效果，因此只需要实现"好友消息接收事件"即可，具体代码如下：

在`MahuaEvents`下添加"好友消息接收事件"，并在事件内调用业务逻辑。实现代码如下：

> MahuaEvents 文件夹是本 SDK 建议将事件放置的文件夹位置。也可以不接受建议而添加在其他地方。

```csharp
using Newbe.Mahua.MahuaEvents;

namespace Newbe.Mahua.Samples.ApiExtensions.MahuaEvents
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
            // 获取好友列表
            var friends = _mahuaApi.GetFriends();

            // 测试好友消息发送
            _mahuaApi.SendPrivateMessage(context.FromQq, "这条消息将写入到日志当中");

            // 测试设置公告接口，需要本QQ在目标群具备管理员权限
            _mahuaApi.SetNotice("610394020", "测试公告", friends);
        }
    }
}
```

## 扩展 API

以下采用三种方式扩展 API。

### 自己实现原来不支持的

`IMahuaApi.GetFriends`在 CQP 平台下，原生是不支持的，本节可以通过添加实现类来进行扩展。

在`MahuaApis`下添加"获取好友列表"。并实现代码如下：

> MahuaApis 文件夹是本 SDK 建议将 API 扩展放置的文件夹位置。也可以不接受建议而添加在其他地方。

![添加获取好友列表](/images/20180107-001.png)

```csharp
using Newbe.Mahua.Apis;

namespace Newbe.Mahua.Samples.ApiExtensions.MahuaApis
{
    public class GetFriendsApiMahuaCommandHandler : IApiCommandHandler<GetFriendsApiMahuaCommand, GetFriendsApiMahuaCommandResult>
    {
        public GetFriendsApiMahuaCommandResult Handle(GetFriendsApiMahuaCommand message)
        {
            var re = new GetFriendsApiMahuaCommandResult
            {
                FriendsString = "这是一段测试好友消息，这段消息会被发送到公告中"
            };
            return re;
        }
    }
}
```

### 替换原来就支持的

`IMahuaApi.SendPrivateMessage`接口是 CQP 平台原生就支持的接口。

本节将通过扩展来覆盖原有的逻辑，将需要发送的消息写入到日志文件中。

在`MahuaApis`下添加"发送私聊消息"。并实现代码如下：

> MahuaApis 文件夹是本 SDK 建议将 API 扩展放置的文件夹位置。也可以不接受建议而添加在其他地方。

```csharp
using Newbe.Mahua.Apis;
using Newbe.Mahua.Logging;

namespace Newbe.Mahua.Samples.ApiExtensions.MahuaApis
{
    public class SendPrivateMessageApiMahuaCommandHandler : IApiCommandHandler<SendPrivateMessageApiMahuaCommand>
    {
        public void Handle(SendPrivateMessageApiMahuaCommand message)
        {
            var logger = LogProvider.For<SendPrivateMessageApiMahuaCommandHandler>();

            // 将好友消息写入到日志当中
            logger.Info(message.Message);
        }
    }
}
```

### 引入扩展包

`IMahuaApi.SetNotice`在 CQP 平台下，原生是不支持的。

为了给开发者提供更多便利的功能。本 SDK 提供了`Newbe.Mahua.*.ApiExtensions`系列 nuget 包。

插件使用者只需要引入这些 nuget 并恰当的注册，便可以实现对平台原生不支持的 API 进行扩展。

在项目源码下`Readme.md`的 MahuaApi 支持列表详细记录了平台原生支持的 API 和扩展包支持的 API。

`Newbe.Mahua.CQP.ApiExtensions` 1.7 版本实现了 CQP 平台下发送群公告的功能，因此，通过 nuget 直接安装此包即可。

## 模块注册

以上三种方式实现 API 的扩展都需要在模块中进行注册，具体的注册代码如下：

```csharp
using Autofac;
using Newbe.Mahua.Apis;
using Newbe.Mahua.CQP.ApiExtensions;
using Newbe.Mahua.MahuaEvents;
using Newbe.Mahua.Samples.ApiExtensions.MahuaApis;
using Newbe.Mahua.Samples.ApiExtensions.MahuaEvents;

namespace Newbe.Mahua.Samples.ApiExtensions
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
                new MyApiModule(),

                // 引入CQP的API扩展包的模块注册
                new CqpApiExtensionsModule(),
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

                //注册在“设置中心”中注册菜单，若想订阅菜单点击事件，可以查看教程。http://www.newbe.cf/docs/mahua/2017/12/24/Newbe-Mahua-Navigations.html
                builder.RegisterType<MyMenuProvider>()
                    .As<IMahuaMenuProvider>();
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

        private class MyApiModule : Module
        {
            protected override void Load(ContainerBuilder builder)
            {
                base.Load(builder);

                // 当前平台是CQP时才注册这些扩展API
                if (MahuaGlobal.CurrentPlatform == MahuaPlatform.Cqp)
                {
                    // 作者名称，既然是你实现了这个功能，那就填上你的名字吧
                    var authorName = "Newbe36524";

                    // 此方法没有CQP提供，此处将注册自己的实现
                    builder.RegisterMahuaApi<GetFriendsApiMahuaCommandHandler, GetFriendsApiMahuaCommand, GetFriendsApiMahuaCommandResult>(authorName);

                    // CQP原生也提供了此API的实现，这里注册时候将会覆盖原来的实现
                    builder.RegisterMahuaApi<SendPrivateMessageApiMahuaCommandHandler, SendPrivateMessageApiMahuaCommand>(authorName);
                }

            }
        }
    }
}
```

## 集成测试

万事具备，只欠生成。

生成解决方案，运行`build.bat`，复制相关的 DLL 到对应的平台，向机器人发送消息，效果达成！

以下是 CQP 平台的测试效果。~~其实其他的没测试~~

![API注册](/images/20180107-002.png)

![好友消息](/images/20180107-003.png)

## 总结

不同平台具备不同的 API 支持范围。通过自定义扩展和扩展包的引入，可以弥合各平台之间的不同。

`Newbe.Mahua.*.ApiExtensions`系列 nuget 包的实现需要依托社区发展方可进一步完善，欢迎您参与其中。

实例的项目代码，可以在源码仓库中的`Newbe.Mahua.Samples.ApiExtensions`解决方案下找到。

<!-- md Nav-Newbe-Mahua-1.X.md -->
