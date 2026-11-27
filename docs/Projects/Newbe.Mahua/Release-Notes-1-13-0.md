---
date: 2018-10-02
title: Newbe.Mahua 1.13 支持撤回消息
tags:
    - Newbe.Mahua
    - QQ机器人
    - 更新说明

top: -999
---

感谢[kotoneme](https://github.com/kotoneme)开发者的 PR。为本框架添加了消息撤回的支持。

<!-- more -->

## 版本亮点

### 支持消息撤回

此版本添加了消息撤回的支持。详细的用法分为两类。

#### 撤回自己的消息

样例代码如下：

```csharp
using Newbe.Mahua.MahuaEvents;

namespace Newbe.Mahua.Plugins.Parrot.MahuaEvents
{
    /// <summary>
    ///     来自好友的私聊消息接收事件
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
            // 普通的 Fluent API 发送消息
            _mahuaApi.SendPrivateMessage(context.FromQq)
                .Text("嘤嘤嘤：")
                .Text(context.Message)
                .Done();

            // 支持撤回的 Fluent API 发送消息
            var token = _mahuaApi.SendPrivateMessage(context.FromQq)
                .Text("嘤嘤嘤：")
                .Text(context.Message)
                .DoneWithToken();

            // 撤回消息
            token.Cancel();

            // 普通 API 发送消息
            _mahuaApi.SendPrivateMessage(context.FromQq, context.Message);

            // 支持撤回的 API 发送消息
            var token2 = _mahuaApi.SendPrivateMessageWithCancelToken(context.FromQq, context.Message);

            // 撤回消息
            token2.Cancel();
        }
    }
}

```

#### 撤回群成员消息

样例代码如下：

```csharp
using Newbe.Mahua.MahuaEvents;

namespace Newbe.Mahua.Plugins.Parrot.MahuaEvents
{
    /// <summary>
    ///     处理群成员消息
    /// </summary>
    public class GroupMessageReceivedMahuaEvent
        : IGroupMessageReceivedMahuaEvent
    {
        public void ProcessGroupMessage(GroupMessageReceivedContext context)
        {
            // 获取用于撤回消息的 token
            var token = context.MessageCancelToken;

            // 撤回消息
            token.Cancel();
        }
    }
}
```

#### 各平台支持情况

消息撤回功能各平台的支持力度各不相同。[详情点击此处进行了解](https://github.com/newbe36524/Newbe.Mahua.Framework#消息撤回特别说明)。

## 升级注意

从 1.12 版本直接更新全部的 Newbe.Mahua.\* nuget 包，重新生成便可以。

升级过程中需要覆盖 build.bat 和 build.ps1 文件。若有自行定制的内容，请提前保留备份。

VS 插件更新只需要按照 VS 提示进行操作即可。

<!-- md Nav-Newbe-Mahua-1.X.md -->
