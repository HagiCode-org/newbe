---
date: 2019-01-25
title: 开始第一个QQ机器人【适用于v2.0及以上】
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

**Newbe.Mahua.Framework 已于 2020 年 8 月 2 日 正式归档，源码将不再更新。**

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
- .Net Framework 4.6.1 及以上
- Powershell 5.0 及以上，仅开发环境要求

## 设置 Powershell 执行策略限制

参考链接：http://www.pstips.net/powershell-create-and-start-scripts.html

简单来说，使用管理员权限在 cmd 中运行以下命令:

```bash
powershell -command "Set-ExecutionPolicy RemoteSigned -Force"
```

## 下载机器人平台

需要从各机器人平台下载最新的软件，各平台官网地址：

| 名称      | 地址                                       | 费用            |
|---------|------------------------------------------|---------------|
| CQP     | https://cqp.cc/                          | Air 免费，Pro 收费 |
| MPQ     | https://f.mypcqq.cc/thread-2327-1-1.html | 免费            |
| QQLight | http://www.52chat.cc/                    | Air 免费，Pro 收费 |

选择开发者喜欢的平台，下载完毕后，将压缩包解压备用。

本教程将采用 CQP 作为主要演示平台。

## 安装 Newbe.Mahua

[点击此处 Newbe.Mahua.Installer](https://github.com/newbe36524/Newbe.Mahua.Framework/tree/master/src/Newbe.Mahua.Installer)，
**下载这个文件夹下所有的文件**。

或者，可以[点击此处](https://gitee.com/yks/Newbe.Mahua.Framework/releases/v2.2)下载其中的`Newbe.Mahua.Installer.zip`压缩包。压缩包中的内容与以上链接一致。

将下载的文件放置到**机器人软件的 exe 所在的文件夹**。

使用控制台打开**机器人软件的 exe 所在的文件夹**，然后执行以下命令

```bash
mahua.bat InstallMahua
```

**计算机第一次安装 Newbe.Mahua 时将会花费较多的时间，需要下载约 50M 左右的软件包，需要耐心等待。**

以下便是一次安装的效果图：

![mahua.bat 安装效果图](/images/20190125-001.gif)

## 启用 Newbe.Mahua.Agent 插件

各个机器人平台的启用方式各不相同。

### CQP

按照下图所示，开启开发者模式。

![开启开发者模式](/images/20171218-001.jpg)

打开插件管理将插件启用。

### MPQ、QQLight

打开插件管理将插件启用。

## 尝试调用 HTTP API

Newbe.Mahua 默认将启动 HTTP API 以便外部进行调用。API 文档的地址默认是 http://127.0.0.1:36524/apiDoc

以下便是一个调用 CQP 发送好友消息的示例：

**注意：以下 API 调用需要根据实际的 API 文档界面的参数提示进行调用。此处文档可能和真实的调用不同，请以文档为准。**

```http request
POST http://127.0.0.1:36524/api/v1/Cqp/CQ_sendPrivateMsg
Content-Type: application/json

{
  "account": 472158246,
  "msg": "月落大佬永远都是唯一的大佬！"
}

```

实际效果如下：

![测试发送消息](/images/20190125-002.gif)

## 实现回调订阅与处理

除了调用 API，框架本身还提供了回调的实现，也就是在机器人触发了“收到好友消息”等事件时，通过一些方式回调开发者的程序。

本示例利用 HTTP 方式来实现需求。

默认情况下，安装完 Newbe.Mahua 之后，机器人的所有事件会通过 HTTP 的方式进行回调。

例如，CQP 平台收到好友消息时，将产生如下请求：

```http request
POST http://localhost:65321/api/ReceiveMahuaOutput
Content-Type: application/json

{
    "TypeCode": "ProcessPrivateMessage",
    "SubType": 11,
    "FromQQ": 472158246,
    "Msg": "YUELUO ： You unknow every lucky ubuntu owner",
    "MsgId": 1408,
    "Font": 147911064,
    "Platform": 0,
    "CreateTime": "2019-01-26T07:36:11.006313+00:00"
}
```

## 实现功能

基于“调用”和“回调”两个内容的处理，我们便可以实现以上需求。

这里给出一些常用编程语言的对应实现，其中包含有`C#`/`Java`/`Javascript`/`Typescript`等开发语言。调用与回调方式包含有`HTTP`/`Websocket`等。

[开发者可以点击此处查看一些技术实现](https://github.com/newbe36524/Newbe.Mahua.Plugins.Parrot)

## 成功！

发送消息给机器人，你就会收到机器人回发的信息。

> 机器人插件启动可能需要一段时间，并且大多数平台都会丢弃离线信息，可能需要等待一会儿在发送。

<!-- md Nav-Newbe-Mahua-2.X.md -->
