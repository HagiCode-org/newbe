---
date: 2017-12-30
title: Newbe.Mahua.Samples.Sqlite SQLite操作实例
tags:
    - Newbe.Mahua
    - QQ机器人
    - 教程

top: -999
---

文本将通过实现一个记录"收到消息数量"的功能，来演示如何在本 SDK 中操作数据库的 SQLite 数据库。

<!-- more -->

## 软硬条件

| 名          | 值       |
| ----------- | -------- |
| IDE         | VS2017.5 |
| Newbe.Mahua | 1.6      |

## 业务逻辑

当收到好友消息时，将消息记录在数据库中。

同时将当前数据库中已经存储的消息数目，发送给消息发送者。

实测效果图：

![最终效果](/images/20171230-003.png)

## 新建项目

使用`Newbe.Mahua.Plugins.Template`模板创建项目，项目名称为`Newbe.Mahua.Samples.Sqlite`。

新建项目的详细细节，可以参照右侧链接内容：[新建项目](./Begin-First-Plugin-With-Mahua-In-v1.4)

## 业务逻辑实现

业务逻辑比较简单，主要实现两个方法："保存好友消息"和"获取消息数量"。

为了提升多核 CPU 的利用率，相关接口都采用异步的方式进行定义。~~实际上时为了让新手看不懂~~

业务接口代码如下：

```csharp
using System;
using System.Threading.Tasks;

namespace Newbe.Mahua.Samples.Sqlite.Services
{
    /// <summary>
    /// 好友消息存储
    /// </summary>
    public interface IFriendMessageStore
    {
        /// <summary>
        /// 获取消息数量
        /// </summary>
        /// <returns></returns>
        Task<int> GetCountAsync();

        /// <summary>
        /// 保存好友消息
        /// </summary>
        /// <param name="input"></param>
        /// <returns></returns>
        Task InsertAsync(InsertFriendMessageInput input);
    }

    public class InsertFriendMessageInput
    {
        /// <summary>
        /// QQ
        /// </summary>
        public string Qq { get; set; }

        /// <summary>
        /// 消息内容
        /// </summary>
        public string Message { get; set; }

        /// <summary>
        /// 收到消息的事件
        /// </summary>
        public DateTimeOffset ReceivedTime { get; set; }
    }
}
```

在`MahuaEvents`下添加"好友消息接收事件"，并在事件内调用业务逻辑。实现代码如下：

> MahuaEvents 文件夹是本 SDK 建议将事件放置的文件夹位置。也可以不接受建议而添加在其他地方。

```csharp
using Newbe.Mahua.MahuaEvents;
using Newbe.Mahua.Samples.Sqlite.Services;

namespace Newbe.Mahua.Samples.Sqlite.MahuaEvents
{
    /// <summary>
    /// 来自好友的私聊消息接收事件
    /// </summary>
    public class PrivateMessageFromFriendReceivedMahuaEvent
        : IPrivateMessageFromFriendReceivedMahuaEvent
    {
        private readonly IMahuaApi _mahuaApi;
        private readonly IFriendMessageStore _friendMessageStore;

        public PrivateMessageFromFriendReceivedMahuaEvent(
            IMahuaApi mahuaApi,
            IFriendMessageStore friendMessageStore)
        {
            _mahuaApi = mahuaApi;
            _friendMessageStore = friendMessageStore;
        }

        public void ProcessFriendMessage(PrivateMessageFromFriendReceivedContext context)
        {
            _friendMessageStore.InsertAsync(new InsertFriendMessageInput
            {
                Message = context.Message,
                Qq = context.FromQq,
                ReceivedTime = context.SendTime
            }).GetAwaiter().GetResult();
            var count = _friendMessageStore.GetCountAsync().GetAwaiter().GetResult();
            _mahuaApi.SendPrivateMessage(context.FromQq, $"存储中已经存在{count}条好友信息。");
        }
    }
}
```

至此业务逻辑便实现完毕。

## 单元测试

业务逻辑已经实现完毕，接下来对业务逻辑编写单元测试进行验证。~~其实这么简单的逻辑，看一眼就知道没错~~

单元测试项目相关的内容可以参看右侧的教程：[单元测试](./Newbe-Mahua-Tests)

此处只将业务逻辑的关键测试代码展示出来：

```csharp
using Autofac.Extras.Moq;
using FluentAssertions;
using Moq;
using Newbe.Mahua.MahuaEvents;
using Newbe.Mahua.Samples.Sqlite.MahuaEvents;
using Newbe.Mahua.Samples.Sqlite.Services;
using System;
using System.Threading.Tasks;
using Xunit;

namespace Newbe.Mahua.Samples.Sqlite.Tests
{
    public class PrivateMessageFromFriendReceivedMahuaEventTests
    {
        [Fact]
        public void Test()
        {
            using (var mocker = AutoMock.GetStrict())
            {
                mocker.VerifyAll = true;

                var now = DateTime.Now;
                var msg = string.Empty;

                mocker.Mock<IMahuaApi>()
                    .Setup(x => x.SendPrivateMessage("472158246", It.IsAny<string>()))
                    .Callback<string, string>((qq, inputmsg) => msg = inputmsg);

                mocker.Mock<IFriendMessageStore>()
                    .Setup(x => x.InsertAsync(It.IsAny<InsertFriendMessageInput>()))
                    .Returns(Task.FromResult(0));

                mocker.Mock<IFriendMessageStore>()
                    .Setup(x => x.GetCountAsync())
                    .Returns(Task.FromResult(200));

                var service = mocker.Create<PrivateMessageFromFriendReceivedMahuaEvent>();
                service.ProcessFriendMessage(new PrivateMessageFromFriendReceivedContext
                {
                    FromQq = "472158246",
                    Message = "MSG",
                    SendTime = now
                });

                msg.Should().Be("存储中已经存在200条好友信息。");
            }
        }
    }
}
```

## 数据库操作实现

### 定义数据库操作接口

单元测试通过之后便表明当前业务逻辑都已经正确实现了。

接下来进一步就可以实现业务接口的实现类了。

为了完成业务逻辑，本实例至少需要"初始化数据库"、"查询数据库"和"向数据库插入数据"三个数据库操作方法。

其中的"查询数据库"和"向数据库插入数据"可以简单定义为"创建数据库链接即可"。

为了提升多核 CPU 的利用率，相关接口都采用异步的方式进行定义。~~实际上时为了让新手看不懂~~

数据库操作接口定义如下：

```csharp
using System.Data.Common;
using System.Threading.Tasks;

namespace Newbe.Mahua.Samples.Sqlite.Services
{
    public interface IDbHelper
    {
        /// <summary>
        /// 初始化数据库
        /// </summary>
        Task InitDbAsync();

        /// <summary>
        /// 获取数据库链接
        /// </summary>
        /// <returns></returns>
        Task<DbConnection> CreateDbConnectionAsync();
    }
}
```

### 使用 SQLite 实现数据库操作

SQLite 数据库操作，通过官方提供的类库便可以完成。

通过 nuget 安装以下 nuget 包：

-   System.Data.SQLite.Core
-   Dapper
-   Dapper.Contrib

其中`System.Data.SQLite.Core`是数据库驱动，`Dapper`则是对`ADO.NET`操作的扩展包。

新建`应用程序配置文件`。

![应用程序配置文件](/images/20171230-002.png)

在应用程序配置文件中配置以下内容：

```xml
<?xml version="1.0" encoding="utf-8"?>

<configuration>
  <connectionStrings>
    <!--
    数据库链接字符串
    DataDirectory需要从当前的应用程序域上下文中获取，可以通过以下代码进行设置：
    AppDomain.CurrentDomain.SetData("DataDirectory",Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "App_Data"))
    -->
    <add name="Default" connectionString="Data Source=|DataDirectory|\mydb.db;Pooling=true;FailIfMissing=false" />
  </connectionStrings>
  <system.data>
    <DbProviderFactories>
      <!--配置ado.net数据工厂-->
      <remove invariant="System.Data.SQLite" />
      <add name="SQLite Data Provider" invariant="System.Data.SQLite"
           description=".NET Framework Data Provider for SQLite"
           type="System.Data.SQLite.SQLiteFactory, System.Data.SQLite" />
    </DbProviderFactories>
  </system.data>
</configuration>
```

添加数据库操作实现类`SqliteDbHelper`,详细代码如下：

```csharp
using Dapper;
using System;
using System.Configuration;
using System.Data.Common;
using System.Data.SQLite;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;

namespace Newbe.Mahua.Samples.Sqlite.Services.Impl
{
    internal class SqliteDbHelper : IDbHelper
    {
        public Task InitDbAsync()
        {
            return Task.Run(() => CreateDbIfnotExists());
        }

        public Task<DbConnection> CreateDbConnectionAsync()
        {
            return Task.Run(() => CreateDbConnectionCore());
        }

        private static DbConnection CreateDbConnectionCore()
        {
            var dbf = DbProviderFactories.GetFactory("System.Data.SQLite");
            var conn = dbf.CreateConnection();
            Debug.Assert(conn != null, nameof(conn) + " != null");
            conn.ConnectionString = ConfigurationManager.ConnectionStrings["Default"].ConnectionString;
            return conn;
        }

        private static void CreateDbIfnotExists()
        {
            var dbDirectory = (string)AppDomain.CurrentDomain.GetData("DataDirectory");
            if (!Directory.Exists(dbDirectory))
            {
                Directory.CreateDirectory(dbDirectory);
            }

            var dbfile = Path.Combine(dbDirectory, "mydb.db");
            if (!File.Exists(dbfile))
            {
                SQLiteConnection.CreateFile(dbfile);
                using (var conn = CreateDbConnectionCore())
                {
                    conn.Execute(@" CREATE TABLE MSG(
                        Id TEXT PRIMARY KEY  ,
                        Qq           TEXT    NOT NULL,
                        Message            TEXT     NOT NULL,
                        ReceivedTime       TEXT NOT NULL
                        )");
                }
            }
        }
    }
}
```

### 编写业务实现类

完成了业务接口的定义和数据操作的定义，接下来只要将两者结合起来，便可以实现业务实现类。

添加`FriendMessageStore`类，详细代码如下：

```csharp
using Dapper;
using Dapper.Contrib.Extensions;
using System;
using System.Threading.Tasks;

namespace Newbe.Mahua.Samples.Sqlite.Services.Impl
{
    /// <inheritdoc />
    /// <summary>
    /// 通过数据库实现好友信息存储
    /// </summary>
    internal class FriendMessageStore : IFriendMessageStore
    {
        private readonly IDbHelper _dbHelper;

        public FriendMessageStore(IDbHelper dbHelper)
        {
            _dbHelper = dbHelper;
        }

        public async Task<int> GetCountAsync()
        {
            using (var conn = await _dbHelper.CreateDbConnectionAsync())
            {
                var count = await conn.ExecuteScalarAsync<int>("select count(1) from MSG");
                return count;
            }
        }

        public async Task InsertAsync(InsertFriendMessageInput input)
        {
            using (var conn = await _dbHelper.CreateDbConnectionAsync())
            {
                await conn.InsertAsync(new MessageEntity
                {
                    Id = Guid.NewGuid().ToString(),
                    Message = input.Message,
                    Qq = input.Qq,
                    ReceivedTime = input.ReceivedTime.ToString("s")
                });
            }
        }

        [Table("MSG")]
        public class MessageEntity
        {
            [Key] public string Id { get; set; }
            public string Qq { get; set; }
            public string Message { get; set; }
            public string ReceivedTime { get; set; }
        }
    }
}
```

### 在插件启动时初始化数据库

数据库的初始化，需要在插件启动时进行调用。

在`MahuaEvents`下添加"插件初始化事件"，并在事件内调用业务逻辑。实现代码如下：

> MahuaEvents 文件夹是本 SDK 建议将事件放置的文件夹位置。也可以不接受建议而添加在其他地方。

```csharp
using Newbe.Mahua.MahuaEvents;
using Newbe.Mahua.Samples.Sqlite.Services;

namespace Newbe.Mahua.Samples.Sqlite.MahuaEvents
{
    /// <summary>
    /// 插件初始化事件
    /// </summary>
    public class InitializationMahuaEvent
        : IInitializationMahuaEvent
    {
        private readonly IDbHelper _dbHelper;

        public InitializationMahuaEvent(
            IDbHelper dbHelper)
        {
            _dbHelper = dbHelper;
        }

        public void Initialized(InitializedContext context)
        {
            // 插件初始化时，初始化数据库
            // 此处采用异步操作，可以避免插件初始化超时的问题
            _dbHelper.InitDbAsync();
        }
    }
}
```

## 模块注册

以上所有的接口与实现类与接口，都不要忘记在模块中进行注册，以下是`MahuaModule`的完整代码：

```csharp
using Autofac;
using Newbe.Mahua.MahuaEvents;
using Newbe.Mahua.Samples.Sqlite.MahuaEvents;
using Newbe.Mahua.Samples.Sqlite.Services;
using Newbe.Mahua.Samples.Sqlite.Services.Impl;
using System;
using System.IO;

namespace Newbe.Mahua.Samples.Sqlite
{
    /// <summary>
    /// Ioc容器注册
    /// </summary>
    public class MahuaModule : IMahuaModule
    {
        public Module[] GetModules()
        {
            AppDomain.CurrentDomain.SetData("DataDirectory",
                Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "App_Data"));

            // 可以按照功能模块进行划分，此处可以改造为基于文件配置进行构造。实现模块化编程。
            return new Module[]
            {
                new PluginModule(),
                new MahuaEventsModule(),
                new MyServiceModule()
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
                builder.RegisterType<InitializationMahuaEvent>()
                    .As<IInitializationMahuaEvent>();
            }
        }

        private class MyServiceModule : Module
        {
            protected override void Load(ContainerBuilder builder)
            {
                base.Load(builder);
                builder.RegisterType<FriendMessageStore>()
                    .As<IFriendMessageStore>();
                builder.RegisterType<SqliteDbHelper>()
                    .As<IDbHelper>();
            }
        }
    }
}
```

## 集成测试

万事具备，只欠生成。

生成解决方案，运行`build.bat`，复制相关的 DLL 到对应的平台，向机器人发送消息，效果达成！

以下是 CQP 平台的测试效果。~~其实其他的没测试~~

![最终效果](/images/20171230-003.png)

## 总结

数据库操作本身并不困难。

开发过程中采用基于接口开发的基本思想，结合单元测试，不论是开发简单的插件还是复杂的项目，都是可靠的方法。

若 SQLite 无法满足项目要求，只要将多实现一个`IDbHelper`便可以完成了，开发者可以动手体验。

实例的项目代码，可以在源码仓库中的`Newbe.Mahua.Samples`解决方案下找到。

<!-- md Nav-Newbe-Mahua-1.X.md -->
