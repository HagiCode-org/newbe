---
date: 2018-04-21
title: Newbe.Mahua 1.8 消息发送Fluent API
tags:
    - Newbe.Mahua
    - QQ机器人

top: -999
---

从此版本开始，增加了"消息发送 Fluent API"，发送消息接口更加方便。

<!-- more -->

## 版本亮点

### 解决了消息发送兼容性问题

以往：想要发送图片消息，各个平台使用的发送机制各不相同。

现在：通过定义`IText`/`IImage`/`IAt`等一系列特殊消息接口，很好的解决的这个问题。

### 对`IMahuaApi`扩展了消息发送 Fluent API

以往：可以通过以下三个接口实现消息发送

```csharp
/// <summary>
/// 发送私聊消息
/// </summary>
/// <param name="toQq">目标QQ号</param>
/// <param name="message">消息内容</param>
void SendPrivateMessage(string toQq, string message);

/// <summary>
/// 发送群消息
/// </summary>
/// <param name="toGroup">目标群</param>
/// <param name="message">消息内容</param>
void SendGroupMessage(string toGroup, string message);

/// <summary>
/// 发送讨论组消息
/// </summary>
/// <param name="toDiscuss">目标讨论组</param>
/// <param name="message">消息内容</param>
void SendDiscussMessage(string toDiscuss, string message);
```

其中的`message`需要自行拼接。

现在：

扩展之后的消息发送 Fluent API，可以通过以下这种更加连贯的方式进行发送

```csharp
// 戳一戳
_mahuaApi.SendPrivateMessage("472158246")
    .Shake()
    .Done();

// 讨论组发送消息
_mahuaApi.SendDiscussMessage("472158246")
    .Text("嘤嘤嘤：")
    .Newline()
    .Text("文章无聊，不如来局游戏https://newbe.hagicode.com")
    .Image(@"D:\logo.png")
    .Done();

// 群内at发送消息
_mahuaApi.SendGroupMessage("610394020")
    .At("472158246")
    .Text("我想充钱")
    .Newline()
    .Done();
```

### 采用消息发送 Fluent API 重写了开发文档

初步教学文档"鹦鹉学舌插件教学"全面升级，新版的"嘤鹉学舌"更加详细。[马上点击学习](./Begin-First-Plugin-With-Mahua-In-v1.8)

## 升级注意

从 1.7 版本直接更新全部的 Newbe.Mahua.\* nuget 包，重新生成便可以。

升级过程中若出现需要覆盖`Newbe.Mahua.CQP.json`的提示，允许即可。

VS 插件更新只需要按照 VS 提示进行操作即可。

<!-- md Nav-Newbe-Mahua-1.X.md -->
