---
date: 2018-09-17
title: Newbe.Mahua 1.X 主要特性介绍与常见问题讲解
top: -1
tags:
  - Newbe.Mahua
  - QQ机器人
---

Newbe.Mahua 1.X 系列 LTS 版本已经发布。本篇就来介绍一下 1.X 版本中的主要特性以及常见问题的解答。

<!-- more -->

## 主要特性

### 依赖注入

框架本身采用 `Autofac` 作为依赖注入框架。进行插件开发时，必然会使用到该框架。建议开发者阅读官方文档熟悉其用法。https://autofac.readthedocs.io/en/latest/getting-started/index.html

### 日志

依赖于 `Liblog` 与 `NLog` 框架支持输出多种多样的日志数据，以便开发者进行开发调试。

[点击此处，学习如何调用日志接口。](./Release-Notes-1-6-0)

默认情况下，框架将会把日志输出在机器人平台根目录的 logs 文件夹中。

[点击此处，学习使用更加美观的日志查看器。](./Release-Notes-1-10-0)

### 调试

框架本身支持进行调试插件与调试框架源码。

[点击此处，学习如何进行调试插件与调试框架源码。](./Newbe-Mahua-Tests)

### Session 机制

Session 机制是框架基于 `Autofac` 采用的一套 API 生命周期管理方案。简要而言，框架将每次事件触发过程，当做一次 Session 进行控制。

开发者可以依赖这一生命周期特性，完成一些业务操作的连贯性。例如：保证整个事件的处理过程属于同一数据库事务。

详细的使用方法建议在了解 `Autofac` 相关的用法之后进行探究。

### 热更新

热更新机制为开发者提供了不需要重启机器人平台便能够更新插件的功能。

[点击此处，学习如何使用热更新功能](./Newbe-Mahua-Hot-Upgrade)

### 消息发送 Fluent API

依赖于 Session 机制，Fluent API 为开发者提供了能够通过链式调用的方式发送消息的功能。

通过 Fluent API 的操作方法，开发者可以类似于数据库事务一样，在多个对象中拼装消息内容，而在最终决定是否发送消息。

[点击此处，学习如何使用Fluent API](./Release-Notes-1-8-0)

### 设置中心

框架提供了一套基于 WPF 的统一设置中心，开发者可以使用此设置中心来制作自己的应用设置界面。

当然开发者可以完全扩展出自己的设置中心。

[点击此处，学习如何开发设置中心](./Newbe-Mahua-Administration)

### 扩展 API 与平台原生 API

开发者可以通过 `IMahuaApi` 调用框架提供的 API，通过这些 API 能够实现大部分的业务需求。

但由于不同平台的支持程度不同，因此实现上存在差异。但开发者可以通过扩展 `IMahuaApi` 的实现，进一步达到自己的需求。

[点击此处，学习如何扩展IMahuaApi](./Release-Notes-1-7-0)

并且，框架也提供了各平台原生的 API。

[点击此处，学习如何调用原生API](./Release-Notes-1-12-0)

## 常见问题

### 大佬，这里有个问题能帮我看一下吗？

不能。

### 框架免费吗？

免费。

### 哪里有框架的源码？

- https://github.com/newbe36524/Newbe.Mahua.Framework
- https://gitee.com/yks/Newbe.Mahua.Framework

### 无法将“Install-PackageProvider”项识别为 cmdlet、函数、脚本文件或可运行程序的名称...

升级到 Powershell 5。https://www.cnblogs.com/wenBlog/p/6198354.html

### 怎么异步发送消息？

由于 Session 机制的存在，直接调用注入事件的`IMahuaApi`执行是必然失败的。因此，需要在异步代码中能够开启新的 Session 才能够正常使用接口。

示例如下：

```csharp

// 异步发送消息，不能使用 _mahuaApi 实例，需要另外开启Session
Task.Factory.StartNew(() =>
{
    using (var robotSession = MahuaRobotManager.Instance.CreateSession())
    {
        var api = robotSession.MahuaApi;
        api.SendPrivateMessage(context.FromQq, "异步的嘤嘤嘤");
    }
});
```

### 怎么解析 API 中好像加密了的群列表？

`IMahuaApi`中提供了解析成模型的 API 接口。字符串本身如何解析可以参考对应平台的易语言 SDK。

### 怎么获取群列表？

看`IMahuaApi`。

### 怎么获取群成员列表？

看`IMahuaApi`。

### 怎么获取好友列表？

看`IMahuaApi`。

### 能不能发红包？

不能。

### 有没有微信 SDK？

没有。

### 为什么复制了启动之后，报错了？

- 重看教程，确认真的都看完了看准了
- 看日志，日志中记录了错误信息

### 能不能给项目捐款？

能。点击右侧链接，信仰充值：https://gitee.com/yks/Newbe.Mahua.Framework#project-donate-overview

<!-- md Nav-Newbe-Mahua-1.X.md -->
