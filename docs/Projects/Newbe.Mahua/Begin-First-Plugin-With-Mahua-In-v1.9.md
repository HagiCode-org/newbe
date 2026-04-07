---
date: 2018-06-10
title: 开始第一个QQ机器人【适用于v1.9-v1.X】
tags:
  - Newbe.Mahua
  - QQ机器人
  - CQP
  - QQLight
  - MPQ
  - 教程
top: -999
---

本示例将会使用"嘤鹉学舌"这个小插件的实现来演示如何使用`Newbe.Mahua`实现第一个机器人插件。

<!-- more -->

## 入坑提示

建议开发者先根据自身需求结合表格，选择属于自己的专属开发框架，避免浪费时间。

1. 编写一套代码就能在多个平台运行
2. 支持使用除了 C#之外的开发语言来开发
3. 我希望他足够简单，不用学习太多就能掌握，通常只需要半个小时就能掌握所有内容
4. 我希望社区的反馈足够快，有问题都可以帮我解决

| SDK 名称                                                                      | （1） | （2） | （3） | （4） |
|-----------------------------------------------------------------------------|-----|-----|-----|-----|
| 论坛中的其他 SDK                                                                  | ✔   | ✔   | ✔   | ✔   |
| [Jie2GG.Native.Csharp.Frame](https://github.com/Jie2GG/Native.Csharp.Frame) | ✔   | ✘   | ✔   | ✔   |
| [Newbe.Mahua V2](https://github.com/newbe36524/Newbe.Mahua.Framework/)      | ✔   | ✔   | ✘   | ✘   |
| [Newbe.Mahua V1](https://github.com/newbe36524/Newbe.Mahua.Framework.V1)    | ✔   | ✘   | ✘   | ✘   |

### 论坛其他 SDK 的链接

- [CQP](https://d.oo14.com/b7oy?target=cqp)
- [MPQ](https://d.oo14.com/b7oy?target=mpq)
- [QQLight](https://d.oo14.com/b7oy?target=qqlight)

## 插件功能

自动将发送者的消息回发给发送人，嘤鹉（Parrot，其实是说嘤嘤嘤怪）学舌。

## 基础环境要求

- Windows 操作系统
- .Net Framework 4.5.2 及以上
- Powershell 5.0 及以上，仅开发环境要求
- [.Net Core SDK 2.2 及以上](https://dotnet.microsoft.com/download)，仅开发环境要求

## IDE

开发者可以任选以下任意一款 IDE

- Visual Studio 2017（VS2015 update 3 理论上也能够开发，但开发遇到的问题，需自行解决）
- Visual Studio Code
- [Rider（Newbe 更加推荐）](https://www.jetbrains.com/rider/)

## 设置 Powershell 执行策略限制

简单来说，使用管理员权限在 cmd 中运行以下命令:

```bash
powershell -command "Set-ExecutionPolicy RemoteSigned -Force"
```

> 参考资料：http://www.pstips.net/powershell-create-and-start-scripts.html

## 安装项目模板

在安装好 `.Net Core SDK` 之后，启动控制台运行以下命令：

```bash
dotnet new -i Newbe.Mahua.Template
```

出现以下内容，则说明项目模板已经安装成功。

![项目模板安装结果](/images/20181216-001.png)

## 新建项目

项目模板包含有五个，包含四个对应平台的模板和一个全平台的模板。

| 名称                  | 说明      |
|---------------------|---------|
| newbe.mahua.all     | 全平台     |
| newbe.mahua.cqp     | 酷 Q     |
| newbe.mahua.mpq     | MyPcQQ  |
| newbe.mahua.qqlight | QQLight |

本示例使用全平台模板 newbe.mahua.all 进行演示。

**特别注意：为了确保新建的项目的能够在所有平台运行，项目名称至少需要包含 AAA.BBB.CCC 三段。**

本次实例使用名称 Newbe.Mahua.Plugins.Parrot 进行演示。

### 使用 Rider

直接使用 Rider 创建项目，可以在 Other 模板分组中找到该框架相关的模板。

![使用Rider创建项目](/images/20181220-001.png)

等待 Rider 创建完毕后，进入新建的项目文件夹中。使用控制台执行更新命令，更新相应的组件包到最新：

```bash
build.bat UpdateMahuaPackages
```

### 使用其他 IDE

新建一个空的文件夹，启动控制台，cd 进入该文件夹，运行以下命令：

```bash
REM 创建解决方案
dotnet new sln -n Newbe.Mahua.Plugins.Parrot

REM 创建项目文件夹
mkdir Newbe.Mahua.Plugins.Parrot

REM 切换目录
cd Newbe.Mahua.Plugins.Parrot

REM 使用模板创建项目
dotnet new newbe.mahua.all -n Newbe.Mahua.Plugins.Parrot
y

REM 切换目录
cd ../

REM 将项目添加到解决方案中
dotnet sln Newbe.Mahua.Plugins.Parrot.sln add Newbe.Mahua.Plugins.Parrot/Newbe.Mahua.Plugins.Parrot.csproj
echo finished
```

**初次执行这些命令需要 1-2 分钟时间。**

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

新建出来的项目中包含一个 `ItemTemplate` 文件夹，里面包含了所有需要的项模板。

**注意，这个文件夹默认没有包含到项目中，需要使用资源管理器进行查看。**

将 `ItemTemplate/MahuaEvent/PrivateMessageReceivedMahuaEvent.cs`

文件复制到 `MahuaEvents/PrivateMessageReceivedMahuaEvent.cs`，并使用 IDE 将复制后的文件包含在项目中。

### 处理事件

在`PrivateMessageFromFriendReceivedMahuaEvent.cs`中，调用`IMahuaApi`，将好友消息回发给好友，实现嘤鹉学舌的效果。

```csharp
using Newbe.Mahua.MahuaEvents;
using System.Threading.Tasks;

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

          // 异步发送消息，不能使用 _mahuaApi 实例，需要另外开启Session
         Task.Factory.StartNew(() =>
         {
             using (var robotSession = MahuaRobotManager.Instance.CreateSession())
             {
                 var api = robotSession.MahuaApi;
                 api.SendPrivateMessage(context.FromQq, "异步的嘤嘤嘤");
             }
         });
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

以 CQP 为例，进行一次复制过程如下图所示：

![CQP复制插件](/images/20180916-001.gif)

各机器人软件下载地址：

| 名称      | 地址                                       |
|---------|------------------------------------------|
| CQP     | https://cqp.cc/                          |
| MPQ     | https://f.mypcqq.cc/thread-2327-1-1.html |
| QQLight | http://www.52chat.cc/                    |

## 启用插件

各个机器人平台的启用方式各不相同。

### CQP

按照下图所示，开启开发者模式。

![开启开发者模式](/images/20171218-001.jpg)

打开插件管理将插件启用。

### MPQ、QQLight

打开插件管理将插件启用。

## 成功！

发送消息给机器人，你就会收到机器人回发的信息。

> 机器人插件启动可能需要一段时间，并且大多数平台都会丢弃离线信息，可能需要等待一会儿在发送。

## 继续了解

[Newbe.Mahua/Feature-And-FAQ-Of-Mahua-With-Version-1-X 'Newbe.Mahua 1.X 主要特性介绍与常见问题讲解'](./Feature-And-FAQ-Of-Mahua-With-Version-1-X 'Newbe.Mahua 1.X 主要特性介绍与常见问题讲解')

<!-- md Nav-Newbe-Mahua-1.X.md -->
