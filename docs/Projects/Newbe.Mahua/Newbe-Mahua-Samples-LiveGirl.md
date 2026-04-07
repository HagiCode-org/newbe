---
date: 2017-12-31
title: Newbe.Mahua.Samples.LiveGirl 操作定时任务
tags:
    - Newbe.Mahua
    - QQ机器人
    - 教程

top: -999
---

B 站直播姬！定时向群友通知群主何时进行女装直播的消息。

<!-- more -->

## 软硬条件

| 名          | 值       |
| ----------- | -------- |
| IDE         | VS2017.5 |
| Newbe.Mahua | 1.6      |

## 业务逻辑

收到 "直播姬起飞" 的消息后，启动定时任务，每个整点时，检测 B 站直播间当前是否正在直播。

如果正在直播，就向群发送 "群主正在女装" 的消息。

收到 "直播姬降落" 的消息后，取消所有定时任务。

![最终效果](/images/20171231-001.png)

## 新建项目

使用`Newbe.Mahua.Plugins.Template`模板创建项目，项目名称为`Newbe.Mahua.Samples.LiveGirl`。

新建项目的详细细节，可以参照右侧链接内容：[新建项目](./Begin-First-Plugin-With-Mahua-In-v1.4)

## 业务逻辑实现

定义直播姬接口`ILiveGirl`，包含 "启动" 和 "停止" 两个基础方法。以便收到消息命令后对定时任务进行启停。

为了提升多核 CPU 的利用率，相关接口都采用异步的方式进行定义。~~实际上时为了让新手看不懂~~

业务接口代码如下：

```csharp
using System.Threading.Tasks;

namespace Newbe.Mahua.Samples.LiveGirl.Services
{
    /// <summary>
    /// B站直播姬
    /// </summary>
    public interface ILivegirl
    {
        /// <summary>
        /// 启动
        /// </summary>
        /// <returns></returns>
        Task StartAsync();

        /// <summary>
        /// 停止
        /// </summary>
        /// <returns></returns>
        Task StopAsnyc();
    }
}
```

在`MahuaEvents`下添加"好友消息接收事件"，并在事件内调用业务逻辑。实现代码如下：

> MahuaEvents 文件夹是本 SDK 建议将事件放置的文件夹位置。也可以不接受建议而添加在其他地方。

```csharp
using Newbe.Mahua.MahuaEvents;
using Newbe.Mahua.Samples.LiveGirl.Services;

namespace Newbe.Mahua.Samples.LiveGirl.MahuaEvents
{
    /// <summary>
    /// 来自好友的私聊消息接收事件
    /// </summary>
    public class PrivateMessageFromFriendReceivedMahuaEvent
        : IPrivateMessageFromFriendReceivedMahuaEvent
    {
        private readonly ILivegirl _livegirl;

        public PrivateMessageFromFriendReceivedMahuaEvent(
            ILivegirl livegirl)
        {
            _livegirl = livegirl;
        }

        public void ProcessFriendMessage(PrivateMessageFromFriendReceivedContext context)
        {
            if (context.FromQq == "472158246")
            {
                switch (context.Message)
                {
                    case "直播姬起飞":
                        _livegirl.StartAsync().GetAwaiter().GetResult();
                        break;
                    case "直播姬降落":
                        _livegirl.StopAsnyc().GetAwaiter().GetResult();
                        break;
                }
            }
        }
    }
}
```

至此直播姬的启停便实现完毕。

## 定时任务

定时任务的实现方式多种多样，可以利用`Timer`进行简单实现，也可以使用一些定时任务的类库进行实现。

比较流行的有：~~其实我也就知道两个~~

-   Quartz.net
-   Hangfire

本例程将使用`Hangfire`来实现这一个功能。

### 安装 nuget 包

安装以下 nuget 包：

-   Hangfire.Core
-   Hangfire.MemoryStorage
-   Hangfire.Autofac
-   Microsoft.Owin.Hosting
-   Microsoft.Owin.Host.HttpListener

`Hangfire`相关内容是实现定时任务功能。

`Microsoft.Owin.*`则实现了在非 IIS 进程中托管 Web 服务的功能。

### 插件启动时初始化 Web 服务

Hangfire 需要通过 Web 服务来展示当前的任务状态情况。

添加 `IWebHost` 接口，以便在插件初始化时，初始化 Web 服务。

```csharp
using Autofac;
using System.Threading.Tasks;

namespace Newbe.Mahua.Samples.LiveGirl.Services
{
    public interface IWebHost
    {
        /// <summary>
        /// 启动Web服务
        /// </summary>
        /// <param name="baseUrl"></param>
        /// <param name="lifetimeScope"></param>
        Task StartAsync(string baseUrl, ILifetimeScope lifetimeScope);

        /// <summary>
        /// 停止
        /// </summary>
        Task StopAsync();
    }
}
```

Web 服务的初始化，需要在插件启动时进行调用。

在`MahuaEvents`下添加"插件初始化事件"，并在事件内调用初始化。实现代码如下：

> MahuaEvents 文件夹是本 SDK 建议将事件放置的文件夹位置。也可以不接受建议而添加在其他地方。

```csharp
using Newbe.Mahua.MahuaEvents;
using Newbe.Mahua.Samples.LiveGirl.Services;

namespace Newbe.Mahua.Samples.LiveGirl.MahuaEvents
{
    /// <summary>
    /// 插件初始化事件
    /// </summary>
    public class InitializationMahuaEvent
        : IInitializationMahuaEvent
    {
        private readonly IMahuaApi _mahuaApi;
        private readonly IWebHost _webHost;

        public InitializationMahuaEvent(
            IMahuaApi mahuaApi,
            IWebHost webHost)
        {
            _mahuaApi = mahuaApi;
            _webHost = webHost;
        }

        public void Initialized(InitializedContext context)
        {
            // 在本地地址上启动Web服务，可以根据需求改变端口
            _webHost.StartAsync("http://localhost:65238", _mahuaApi.GetSourceContainer());
        }
    }
}
```

### 添加 Hangfire 初始化代码

Owin 的启动入口是一个名为`Startup`的启动类，为了初始化`Hangfire`，则需要创建启动类，并初始化`Hangfire`。

代码如下：

```csharp
using Autofac;
using Hangfire;
using Hangfire.MemoryStorage;
using Microsoft.Owin;
using Owin;

// 这是Startup的入口标记
[assembly: OwinStartup(typeof(Newbe.Mahua.Samples.LiveGirl.Startup))]

namespace Newbe.Mahua.Samples.LiveGirl
{
    public class Startup
    {
        public void Configuration(IAppBuilder app, ILifetimeScope lifetimeScope)
        {
            // 初始化Hangfire
            var config = GlobalConfiguration.Configuration;

            // 使用内存存储任务，若有持久化任务的需求，可以根据Hangfire的文档使用数据库方式存储
            config.UseMemoryStorage();

            // 通过Autofac容器来实现任务的构建
            config.UseAutofacActivator(lifetimeScope);

            // 启用Hangfire的web界面
            app.UseHangfireDashboard();

            // 初始化Hangfire服务
            app.UseHangfireServer();
        }
    }
}
```

### 实现 IWebHost

上代码：

```csharp
using Autofac;
using Microsoft.Owin.Hosting;
using System;
using System.Threading.Tasks;

namespace Newbe.Mahua.Samples.LiveGirl.Services.Impl
{
    public class OwinWebHost : IWebHost
    {
        // 保存Web服务的实例
        private IDisposable _webhost;

        public Task StartAsync(string baseUrl, ILifetimeScope lifetimeScope)
        {
            _webhost = WebApp.Start(baseUrl, app => new Startup().Configuration(app, lifetimeScope));
            return Task.FromResult(0);
        }

        public Task StopAsync()
        {
            _webhost.Dispose();
            return Task.FromResult(0);
        }
    }
}
```

## 实现直播姬

基础设施已经在上一节完成，接下来就要实现直播姬和定时任务之间的调度代码。

### 获取直播间状态

直播间状态可以通过捕捉 HTTP 请求，看出如何实现。

本例程，将引入 `RestSharp` nuget 包来实现 HTTP 请求。

定义直播间接口`ILiveRoom`并添加实现类。

```csharp
namespace Newbe.Mahua.Samples.LiveGirl.Services
{
    public interface ILiveRoom
    {
        /// <summary>
        /// 获取直播间状态
        /// </summary>
        /// <returns></returns>
        bool IsOnLive();
    }
}
```

```csharp
using RestSharp;

namespace Newbe.Mahua.Samples.LiveGirl.Services.Impl
{
    public class LiveRoom : ILiveRoom
    {
        public bool IsOnLive()
        {
            var client = new RestClient("https://api.live.bilibili.com");
            var req = new RestRequest("room/v1/Room/get_info?room_id=7834872&from=room");
            var resp = client.Get<Rootobject>(req);
            if (resp.IsSuccessful)
            {
                return resp.Data.data.live_status == 1;
            }

            return false;
        }

        // 可以使用VS中的 编辑->选择性粘贴->将JSON粘贴为类
        // 莫非不知道么ლ(′◉❥◉｀ლ)
        public class Rootobject
        {
            public int code { get; set; }
            public string msg { get; set; }
            public string message { get; set; }
            public Data data { get; set; }
        }

        public class Data
        {
            public int uid { get; set; }
            public string description { get; set; }
            public int live_status { get; set; }
            public int area_id { get; set; }
            public int parent_area_id { get; set; }
            public string parent_area_name { get; set; }
            public int old_area_id { get; set; }
            public string background { get; set; }
            public string title { get; set; }
            public string user_cover { get; set; }
            public string live_time { get; set; }
            public string tags { get; set; }
            public int is_anchor { get; set; }
            public string room_silent_type { get; set; }
            public int room_silent_level { get; set; }
            public int room_silent_second { get; set; }
            public string area_name { get; set; }
            public string pendants { get; set; }
            public string area_pendants { get; set; }
            public string verify { get; set; }
        }
    }
}
```

### Livegirl

来吧，终于可以实现直播姬了。

```csharp
using Hangfire;
using System.Diagnostics;
using System.Threading.Tasks;

namespace Newbe.Mahua.Samples.LiveGirl.Services.Impl
{
    public class Livegirl : ILivegirl
    {
        private static readonly string JobId = "jobid";

        private readonly IMahuaApi _mahuaApi;
        private readonly ILiveRoom _liveRoom;

        public Livegirl(
            IMahuaApi mahuaApi,
            ILiveRoom liveRoom)
        {
            _mahuaApi = mahuaApi;
            _liveRoom = liveRoom;
        }

        public Task StartAsync()
        {
            // 添加定时任务
            // 每个整点触发
            RecurringJob.AddOrUpdate(JobId, () => SendMessage(), () => Cron.HourInterval(1));

            // 使用浏览器打开定时任务的地址
            Process.Start("http://localhost:65238/hangfire/recurring");
            return Task.FromResult(0);
        }

        public Task StopAsnyc()
        {
            // 移除定时任务
            RecurringJob.RemoveIfExists(JobId);
            return Task.FromResult(0);
        }

        public void SendMessage()
        {
            // 如果直播间状态为正在直播，则发送消息
            if (_liveRoom.IsOnLive())
            {
                _mahuaApi.SendGroupMessage("610394020", "群主正在女装，前往观望？https://live.bilibili.com/7834872");
            }
        }
    }
}
```

## 模块注册

以上所有的接口与实现类与接口，都不要忘记在模块中进行注册，以下是`MahuaModule`的完整代码：

```csharp
using Autofac;
using Newbe.Mahua.MahuaEvents;
using Newbe.Mahua.Samples.LiveGirl.MahuaEvents;
using Newbe.Mahua.Samples.LiveGirl.Services;
using Newbe.Mahua.Samples.LiveGirl.Services.Impl;

namespace Newbe.Mahua.Samples.LiveGirl
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
                new MyServiceModule(),
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
                builder.RegisterType<InitializationMahuaEvent>()
                    .As<IInitializationMahuaEvent>();
                builder.RegisterType<PrivateMessageFromFriendReceivedMahuaEvent>()
                    .As<IPrivateMessageFromFriendReceivedMahuaEvent>();
            }
        }

        private class MyServiceModule : Module
        {
            protected override void Load(ContainerBuilder builder)
            {
                base.Load(builder);
                // 确保Web服务是单例
                builder.RegisterType<OwinWebHost>()
                    .As<IWebHost>()
                    .SingleInstance();

                // AsSelf是为了Hangfire能够初始化这个类
                builder.RegisterType<Livegirl>()
                    .As<ILivegirl>()
                    .AsSelf();
                builder.RegisterType<LiveRoom>()
                    .As<ILiveRoom>();
            }
        }
    }
}
```

## 集成测试

万事具备，只欠生成。

生成解决方案，运行`build.bat`，复制相关的 DLL 到对应的平台，向机器人发送消息，效果达成！

以下是 CQP 平台的测试效果。~~其实其他的没测试~~

![最终效果](/images/20171231-001.png)

## 总结

一般的定时任务只需要使用`Timer`就能够实现了，引入`Hangfire`主要是为了体现框架本身的可扩展性。~~分明是为了装逼~~

HTTP 的捕捉，可以使用`Fiddler`等 Web 调试工具实现。~~又要自己学~~

例程中写死的字符串，应当通过文件配置进行保存，可以自行改造。

实例的项目代码，可以在源码仓库中的`Newbe.Mahua.Samples`解决方案下找到。

<!-- md Nav-Newbe-Mahua-1.X.md -->
