---
date: 2017-12-25
title: Newbe.Mahua 测试与调试
tags:
    - Newbe.Mahua
    - QQ机器人

top: -999
---

测试与调试是开发过程当中不可缺少的环节。本教程将通过对"鹦鹉学舌"插件对"如何测试与调试 Newbe.Mahua".

<!-- more -->

## 测试

测试分类多种多样，其中，"单元测试"是最开始的细粒度测试。

掌握单元测试的技能，将会在使用 Newbe.Mahua 进行开发时无往不利的成功秘诀。

本教程将使用 VS2017 作为开发 IDE 进行演示。

### 新建测试项目

![新建测试项目](/images/20171225-001.png)

### 引入测试框架

.Net 测试框架众多，主流的有 MSTest、NUnit 和 XUnit。本教程选择 XUnit 进行演示。

通过 nuget 安装以下包，全部安装最新版本即可：

-   xunit
-   xunit.runner.visualstudio
-   FluentAssertions
-   Autofac.Extras.Moq

可以不用先了解每个包时什么作用，看了代码，自然就会清楚。

### 添加单元测试代码

先看一下需要测试的"鹦鹉学舌"插件的核心逻辑，将消息回发给消息发送者。

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
            // 将好友信息会发给好友
            _mahuaApi.SendPrivateMessage(context.FromQq, context.Message);
        }
    }
}
```

通过项目引用，引用"Newbe.Mahua.Plugins.Parrot"项目。

在新建的测试项目"Newbe.Mahua.Plugins.Parrot.Tests"中新建一个类"ParrotTest"，并填写以下代码：

```csharp
using Autofac.Extras.Moq;
using FluentAssertions;
using Newbe.Mahua.MahuaEvents;
using Newbe.Mahua.Plugins.Parrot.MahuaEvents;
using System;
using Xunit;
using Xunit.Abstractions;

namespace Newbe.Mahua.Plugins.Parrot.Tests
{
    public class ParrotTest
    {
        private readonly ITestOutputHelper _testOutputHelper;

        public ParrotTest(ITestOutputHelper testOutputHelper)
        {
            // 这是xunit特有的信息输出方法，其他框架可以使用Console.Writeline
            _testOutputHelper = testOutputHelper;
        }

        [Fact(DisplayName = "将消息回发给消息发送者")]
        public void Test()
        {
            // 一般的单元测试都分为三个部分 Arrange(准备) Action(执行) 和 Assert(断言)
            // Arrange 对单元测试中需要测试的准备参数进行初始化
            // Action 执行需要测试的逻辑
            // Assert 对测试结果是否正确进行判断
            using (var mocker = AutoMock.GetStrict())
            {
                // Moq的参数，确定在整个单元测试结束之后，所有被模拟的方法都已经被执行。
                mocker.VerifyAll = true;

                #region Arrange

                // 生成一个IMahuaApi的实现，这个实现的所有方法都是没有实现的，需要进一步填充
                var mahuaApi = mocker.Mock<IMahuaApi>();

                // 用来记录消息是否已经发送的变量，为了在断言中使用
                var msgSend = false;

                // 对MahuaApi中的SendPrivateMessage方法进行模拟
                // 当调用参数是“472158246”和“呵呵哒”时，调用xunit帮助类在控制台输出消息
                // 并设置变量msgSend为true  表示，消息确实已经回发了
                mahuaApi
                    .Setup(x => x.SendPrivateMessage("472158246", "呵呵哒"))
                    .Callback<string, string>((qq, msg) =>
                    {
                        _testOutputHelper.WriteLine($"测试将消息发送给{qq},消息是{msg}");
                        msgSend = true;
                    });

                #endregion

                #region Action

                //创建需要测试的类，由于使用了Autofac.Extras.Moq，构造函数注入的过程会自动执行
                IPrivateMessageFromFriendReceivedMahuaEvent @event =
                    mocker.Create<PrivateMessageFromFriendReceivedMahuaEvent>();

                // 模拟某人向机器人发送了消息
                @event.ProcessFriendMessage(new PrivateMessageFromFriendReceivedContext
                {
                    FromQq = "472158246",
                    Message = "呵呵哒",
                    SendTime = DateTime.Now
                });

                #endregion

                #region Assert

                // 根据这个变量判断 机器人是否成功回发了消息
                msgSend.Should().BeTrue();

                #endregion
            }
        }
    }
}
```

通过阅读代码的注释，相信真正的勇士已经领会了其中的奥义。

### 运行测试代码

![运行测试](/images/20171225-002.png)

**来吧！真正的勇士，就绿了它们！**

### 需求变化

需求变了，只有消息当中有"收到回复"这个字符串，那么才需要回发，并且要删除其中的"收到回复"字符串。

在测试项目新加一个实现类，来实现上面的业务逻辑。

```csharp
using Newbe.Mahua.MahuaEvents;

namespace Newbe.Mahua.Plugins.Parrot.Tests
{
    /// <summary>
    /// 只有包含收到回复，才需要回复
    /// </summary>
    public class PrivateMessageFromFriendReceivedMahuaEventV2
        : IPrivateMessageFromFriendReceivedMahuaEvent
    {
        private readonly IMahuaApi _mahuaApi;

        public PrivateMessageFromFriendReceivedMahuaEventV2(
            IMahuaApi mahuaApi)
        {
            _mahuaApi = mahuaApi;
        }

        public void ProcessFriendMessage(PrivateMessageFromFriendReceivedContext context)
        {
            if (context.Message?.Contains("收到回复") == true)
            {
                var msg = context.Message.Replace("收到回复", string.Empty);
                _mahuaApi.SendPrivateMessage(context.FromQq, msg);
            }
        }
    }
}
```

显然，这个业务逻辑，至少需要两个单元测试。一个测试的消息中包含"收到回复"，另一个则不包含。

由此，新建"ParrotTestV2"类，并填写以下代码：

```csharp
using Autofac.Extras.Moq;
using FluentAssertions;
using Newbe.Mahua.MahuaEvents;
using System;
using Xunit;
using Xunit.Abstractions;

namespace Newbe.Mahua.Plugins.Parrot.Tests
{
    public class ParrotTestV2
    {
        private readonly ITestOutputHelper _testOutputHelper;

        public ParrotTestV2(ITestOutputHelper testOutputHelper)
        {
            _testOutputHelper = testOutputHelper;
        }

        [Fact(DisplayName = "消息包含“收到回复”")]
        public void Test1()
        {
            using (var mocker = AutoMock.GetStrict())
            {
                mocker.VerifyAll = true;
                var mahuaApi = mocker.Mock<IMahuaApi>();
                var msgSend = false;
                mahuaApi
                    .Setup(x => x.SendPrivateMessage("472158246", "请马上捐款"))
                    .Callback<string, string>((qq, msg) =>
                    {
                        _testOutputHelper.WriteLine($"测试将消息发送给{qq},消息是{msg}");
                        msgSend = true;
                    });

                // 这里使用的是V2
                IPrivateMessageFromFriendReceivedMahuaEvent @event =
                    mocker.Create<PrivateMessageFromFriendReceivedMahuaEventV2>();
                @event.ProcessFriendMessage(new PrivateMessageFromFriendReceivedContext
                {
                    FromQq = "472158246",
                    Message = "请马上捐款收到回复",
                    SendTime = DateTime.Now
                });

                // 注意，这里是true
                msgSend.Should().BeTrue();
            }
        }

        [Fact(DisplayName = "消息不包含“收到回复”")]
        public void Test2()
        {
            using (var mocker = AutoMock.GetStrict())
            {
                mocker.VerifyAll = true;

                // 因为我们确定不会调用IMahuaApi，所以不需要Mock

                // 这里使用的是V2
                IPrivateMessageFromFriendReceivedMahuaEvent @event =
                    mocker.Create<PrivateMessageFromFriendReceivedMahuaEventV2>();
                @event.ProcessFriendMessage(new PrivateMessageFromFriendReceivedContext
                {
                    FromQq = "472158246",
                    Message = "呵呵哒",
                    SendTime = DateTime.Now
                });
            }
        }
    }
}
```

自己手动尝试的过程中可能会出现，没出现"绿"的问题。不要放弃，要么测试错了，要么业务逻辑错误。电脑是不会错的。

其实上面的业务逻辑中是存在 BUG 的：QQ 无法发送空的消息，所以，如果对方的消息只包含"收到回复"四个字，那么真正运行的时候会报错。

因此，要增加额外的逻辑判断和单元测试，来确保这个 BUG 不会发生。**真正的勇士，自己就会动手。**

### 最后

单元测试就是为了确保代码逻辑在小范围内绝对正确的开发行为，很有必要。

**单元测试只要 Newbe.Mahua 提供的接口稳定，自己的业务逻辑没有变化，那么你的业务逻辑就永远能够通过单元测试。也就是说，这段代码就是为了确保你有底气说出："我的代码不可能出错！"**

以上演示代码，均可以在本项目代码仓库中找到。

## 调试

单元测试是开发阶段最初的测试，但事实是，绝大多数的人更喜欢"跑一下看看"。因此调试，也就很有必要。

### 构建

在构建脚本`build.ps1`中，将`$configuration`从`Release`改为`Debug`，然后运行`build.bat`完成构建。

![修改构建参数](/images/20171225-003.png)

### 复制

将生成的所有内容复制到对应机器人平台。

### 启动调试

修改项目属性中的调试选项卡配置，并且将插件项目设置为启动项目，F5 启动调试，下断点，命中，就这么简单。

<!-- ![修改调试启动项目](/i/20171225-004.png) -->

### 调试框架源码

从 1.6 版本开始，使用 VS 2017.5 及以上的版本，将可以实现无需下载源码，便可以调试源码的目的，只需要在 VS 中打开下图设置即可。

![开启源链接支持](/images/20171230-001.png)

至此，调试便可以正常进行了。

<!-- md Nav-Newbe-Mahua-1.X.md -->
