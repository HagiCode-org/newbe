---
date: 2018-06-10
title: Newbe.Mahua 1.9 引入 Session
tags:
    - Newbe.Mahua
    - QQ机器人
    - 更新说明

top: -999
---

从此版本开始，增加 MahuaRobotManager 和 RobotSession 机制，支持在 MahuaEvent 之外调用机器人 API。

<!-- more -->

## 版本亮点

### 解决无法在 MahuaEvent 线程之外调用 IMahuaApi 的问题

以往：只能在 MahuaEvent 中通过注入 IMahuaApi 来调用 API。

现在：通过 MahuaRobotManager 获得 Session 便可以在 Session 中实现对机器人 API 的调用。

```csharp
// 在 Task 中发送消息
Task.Factory.StartNew(() =>
{
    using (var robotSession = MahuaRobotManager.Instance.CreateSession())
    {
        var api = robotSession.MahuaApi;
        api.SendPrivateMessage("415206409", "异步的嘤嘤嘤");
    }
});
```

由此，配合 Timer 等方法便可以实现定时机器人控制。

## 升级注意

从 1.8 版本直接更新全部的 Newbe.Mahua.\* nuget 包，重新生成便可以。

升级过程中出现需要覆盖文件的提示，请选择同意。

VS 插件更新只需要按照 VS 提示进行操作即可。

框架不再依赖`NuGet.CommandLine`包，可以删除。

<!-- md Nav-Newbe-Mahua-1.X.md -->
