---
date: 2023-03-12
title: async 与 Thread 的错误结合
tags: [C#, Docker, Kubernetes]

slag: 0x027-error-when-using-async-with-thread
summary: 在 TAP 出现之前，我们可以通过 Thread 来完成一些线程操作，从而实现多线程和异步操作。在 TAP 出现之后，有时候为了更高精度的控制线程，我们还是会使用到 Thread 。文本讲介绍一种错误的使用方式，作为读者的一个参考。
alias: /Others/0x027-This-is-the-wrong-way-to-use-LongRunnigTask-in-csharp/
---

<!-- YamlFrontMatter -->

在 TAP 出现之前，我们可以通过 Thread 来完成一些线程操作，从而实现多线程和异步操作。在 TAP 出现之后，有时候为了更高精度的控制线程，我们还是会使用到 Thread 。文本讲介绍一种错误的使用方式，作为读者的一个参考。

<!-- more -->

## 和 TaskCreateOptions.LongRunning 类似

不应该尝试使用 Thread 执行类似的异步操作。因为这浪费了开启线程的花销。

有的时候，你可能会这么写：

```csharp
var thread = new Thread(async () =>
{
    while (true)
    {
        // do something
        await Task.Delay(1000);
    }
}){
    IsBackground = true
};
thread.Start();
```

但其实，这是个错误的写法。

## IDE 提示

和 TaskCreateOptions.LongRunning 略有不同，采用这种写法，IDE 会给出一个提示，表明希望取消 async 关键字。因为实际上

1. Thread 的所有重载中并没有支持 Task 相关的重载。
2. async void 除了在 event handler 中使用，其他地方都是不推荐的。

所以这种做法实际上并不推荐。

而 TaskFactory.StartNew() 的重载中，由于存在一个 `Func<T>` 的重载，所以导致虽然这种这种使用方式错误，却被 IDE 所接受。

所以这里其实就可以总结一个简单的规则：**当考察一组 API 是否原生支持 TAP 操作的时候，应该查看这组 API 中是否存在 Task 相关的重载。如果没有，那么说明原生并不能良好支持，如果使用则可能会出现意外的情况**

同样的，当我们自己在设计 API 的时候也应该参考该原则，对于自己希望支持 TAP 的 API，应该提供 Task 相关的重载。

## 昙花线程

在 thread async void 其实上只是一个很小的问题。这个错误的关键还是造成了一个昙花线程。

我们通过以下代码来验证：

```csharp
var thread = new Thread(async () =>
{
    while (true)
    {
        // do something
        await Task.Delay(1000);
    }
}){
    IsBackground = true
};
thread.Start();

Thread.Sleep(3000);

Console.WriteLine("thread is alive: " + thread.IsAlive);
// thread is alive: False
```

这里我们可以看到，thread.IsAlive 的值为 False。这是因为，我们在 thread 中使用了 await 关键字，在 await 之后的代码，实际上是在另一个 ThreadPool 中的线程中执行的。而我们的 thread 本身在 await 之后就已经结束了。于是我们就得到了一个昙花一现的线程。

而这种昙花线程无疑就是一种浪费。

## 如何观测线程的生命周期

其实大体的内容我们已经讲完了。但为了凑一下篇幅，我们着重演示一下如何使用 Rider 来观测线程的生命周期。

首先我们在 Rider 中创建一个单元测试项目，然后在其中创建一个单元测试：

```csharp
[Test]
public void Test1()
{
    var t1 = new Thread(async () =>
    {
        while (true)
        {
            // do something
            await Task.Delay(1000);
        }
    })
    {
        IsBackground = true,
        Name = "t1"
    };
    t1.Start();

    var t2 = new Thread(() =>
    {
        while (true)
        {
            // do something
            Thread.Sleep(1000);
        }
    })
    {
        IsBackground = true,
        Name = "t2"
    };
    t2.Start();

    Thread.Sleep(3000);
}
```

然后我们在 Rider 中按照下图选择 Profile 选项：

![profile1](/images/20230312-001.png)

然后选择 Profile Unit Tests 选项：

![profile2](/images/20230312-002.png)

稍等片刻之后，我们就可以双击下图中的报告，来查看线程的生命周期：

![profile3](/images/20230312-003.png)

在查看界面中，我们可以通过线程下来框来查看线程运行所花费的时间：

![profile4](/images/20230312-004.png)

如果上图，我们可以很直接的看到，t1 线程的生命周期可以说是瞬间就结束了，因为第一次 await 之后，线程就结束了。

## 总结

在本文中，我们演示了一种错误的使用方式，以及如何使用 Rider 来观测线程的生命周期。

## 参考

- [.NET Task 揭秘（2）：Task 的回调执行与 await](https://www.cnblogs.com/eventhorizon/p/15912383.html)[^1]
- [Task](https://threads.whuanle.cn/3.task/)[^2]
- [TaskCreationOptions](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.taskcreationoptions?view=net-7.0&WT.mc_id=DT-MVP-5004283)[^3]

[^1]: https://www.cnblogs.com/eventhorizon/p/15912383.html
[^2]: https://threads.whuanle.cn/3.task/
[^3]: https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.taskcreationoptions?view=net-7.0&WT.mc_id=DT-MVP-5004283

<!-- ending -->

<!-- ad -->

<!-- copyright-->
