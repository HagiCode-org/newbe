---
date: 2023-03-18
title: 实现常驻任务除了避免昙花线程，还需要避免重返线程池
tags: [C#, Docker, Kubernetes]

slag: 0x028-avoid-return-to-threadpool-in-longrunning-task
summary: 前面我们使用简单的例子演示了 Task 和 Thread 的两种制造昙花线程的方式。那么除了避免昙花线程，在实现常驻任务的时候，还需要避免重返线程池。本文将介绍如何避免重返线程池。
---

<!-- YamlFrontMatter -->

前面我们使用简单的例子演示了 Task 和 Thread 的两种制造昙花线程的方式。那么除了避免昙花线程，在实现常驻任务的时候，还需要避免重返线程池。本文将介绍如何避免重返线程池。

<!-- more -->

## 常驻任务

常驻任务非常常见，比如：

1. 我们正在编写一个日志文件库，我们希望在后台不断的将日志写入文件，尽可能不影响业务线程的执行。因此，需要一个写文件的常驻任务。
2. 我们对接了一个远程 TCP 服务，对方要求我们每隔一段时间发送一个心跳包，以保持连接。因此，需要一个发送心跳包的常驻任务。
3. 我们编写了一个简单的内存缓存，通过一个后台任务来定期清理过期的缓存。因此，需要一个清理缓存的常驻任务。

类似的场景还有很多。因此，我们需要一个能够实现常驻任务的方法。

而实现常驻任务的主要要点是：

1. 常驻任务必须避免影响业务线程的执行，因此需要在后台执行。
2. 常驻任务不能被业务线程影响，无论当前业务多么繁忙，常驻任务都必须能够正常执行。否则会出现日志不落盘，心跳包不发送，缓存不清理等问题。

实现常驻任务的手段有很多。本文将围绕如何使用常驻单一线程来实现常驻任务。

所谓常驻单一线程，就是指始终使用一个线程来执行常驻任务。从而达到：

1. 避免频繁的创建和销毁线程，从而避免频繁的线程切换。
2. 更容易的处理背压问题。
3. 更容易的处理线程安全问题。

## 评测主体

我们将采用如下情况来评测如何编写常驻任务的正确性。

```csharp yanjia.cs
private int _count = 0;

private void ProcessTest(Action<CancellationToken> action, [CallerMemberName] string methodName = "")
{
    var cts = new CancellationTokenSource();
    // 启动常驻线程
    action.Invoke(cts.Token);
    // 严架给压力
    YanjiaIsComing(cts.Token);

    // 等待一段时间
    Thread.Sleep(TimeSpan.FromSeconds(5));
    cts.Cancel();

    // 输出结果
    Console.WriteLine($"{methodName}: count = {_count}");
}

private void YanjiaIsComing(CancellationToken token)
{
    Parallel.ForEachAsync(Enumerable.Range(0, 1_000_000), token, (i, c) =>
    {
        while (true)
        {
            // do something
            c.ThrowIfCancellationRequested();
        }
    });
}
```

这里我们定义了一个 ProcessTest 方法，用于评测常驻任务的正确性。我们将在这个方法中启动常驻任务，然后执行一个严架给压力的方法，来模拟非常繁忙的业务操作。最后我们将输出常驻任务中的计数器的值。

可以初步看一下严架带来的压力有多大：

![CPU 100](/images/20230318-001.png)

然后我们不妨假设，我们的常驻任务是希望每秒进行一次计数。那么最终在控制台输出的结果应该是 5 或者 6。但如果小于 5，那么就说明我们的常驻任务有问题。

比如下面这样：

```csharp
[Test]
public void TestTaskRun_Error()
{
    ProcessTest(token =>
    {
        Task.Run(async () =>
        {
            while (true)
            {
                _count++;
                await Task.Delay(TimeSpan.FromSeconds(1), token);
            }
        }, token);
    });
    // TestTaskRun_Error: count = 1
}
```

在该测试中，我们希望使用 Task.Run 来执行我们期待的循环，进行每秒加一的操作。但是，我们发现，最终输出的结果是 1。这是因为：

1. Task.Run 会将我们的任务放入 Task Default Scheduler 线程池中执行。
2. 但是由于迫于严架给压力，我们的业务线程会一直处于繁忙状态，因此线程池中的线程也会一直处于繁忙状态。
3. 从而日导致我们的常驻任务无法正常执行。

这里我们可以看到，Task.Run 并不是一种正确的实现常驻任务的方法。当然实际上这也不是常驻单一线程，因为这样本质是使用了线程池。

<!-- ad -->

## 全同步过程

结合我们之前提到的 TaskCreationOptions.LongRunning 以及 Thread 很容易在全同步的情况下实现常驻单一线程。

```csharp
[Test]
public void TestSyncTaskLongRunning_Success()
{
    ProcessTest(token =>
    {
        Task.Factory.StartNew(() =>
        {
            while (true)
            {
                _count++;
                Thread.Sleep(TimeSpan.FromSeconds(1));
            }
        }, token, TaskCreationOptions.LongRunning, TaskScheduler.Current);
    });
    // TestSyncTaskLongRunning_Success: count = 6
}


[Test]
public void TestThread_Success()
{
    ProcessTest(token =>
    {
        new Thread(() =>
        {
            while (true)
            {
                _count++;
                Thread.Sleep(TimeSpan.FromSeconds(1));
                if (token.IsCancellationRequested)
                {
                    return;
                }
            }
        })
        {
            IsBackground = true,
        }.Start();
    });
    // TestThread_Success: count = 6
}
```

这两种正确的写法都实现了常驻单一线程，因此我们可以看到，最终输出的结果都是 6。

## 昙花线程

那么自然，我们也可以知道，如果混合了昙花线程，那么就会出现问题。

```csharp
[Test]
public void TestAsyncTaskLongRunning_Error()
{
    ProcessTest(token =>
    {
        Task.Factory.StartNew(async () =>
        {
            while (true)
            {
                _count++;
                await Task.Delay(TimeSpan.FromSeconds(1), token);
            }
        }, token, TaskCreationOptions.LongRunning, TaskScheduler.Current);
    });
    // TestAsyncTaskLongRunning_Error: count = 1
}

[Test]
public void TestThreadWithAsync_Error()
{
    ProcessTest(token =>
    {
        Task CountUp(CancellationToken c)
        {
            _count++;
            return Task.CompletedTask;
        }

        new Thread(async () =>
        {
            while (true)
            {
                try
                {
                    await CountUp(token);
                    await Task.Delay(TimeSpan.FromSeconds(1), token);
                    token.ThrowIfCancellationRequested();
                }
                catch (OperationCanceledException e)
                {
                    return;
                }
            }
        })
        {
            IsBackground = true,
        }.Start();
    });
    // TestThreadWithAsync_Error: count = 1
}
```

这两种错误的写法都无法实现常驻单一线程，因此我们可以看到，最终输出的结果都是 1。

## 不是有 Task 就是异步的

虽然不是本篇的关键内容，但是还是额外补充两个 case 作为对比：

```csharp
[Test]
public void TestThreadWithTask_Success()
{
    ProcessTest(token =>
    {
        Task CountUp(CancellationToken c)
        {
            _count++;
            return Task.CompletedTask;
        }

        new Thread(() =>
        {
            while (true)
            {
                try
                {
                    CountUp(token).Wait(token);
                    Thread.Sleep(TimeSpan.FromSeconds(1));
                }
                catch (OperationCanceledException e)
                {
                    return;
                }
            }
        })
        {
            IsBackground = true,
        }.Start();
    });
    // TestThreadWithTask_Success: count = 6
}

[Test]
public void TestThreadWithDelayTask_Error()
{
    ProcessTest(token =>
    {
        Task CountUp(CancellationToken c)
        {
            _count++;
            return Task.Delay(TimeSpan.FromSeconds(1), c);
        }

        new Thread(() =>
        {
            while (true)
            {
                try
                {
                    CountUp(token).Wait(token);
                    token.ThrowIfCancellationRequested();
                }
                catch (OperationCanceledException e)
                {
                    return;
                }
            }
        })
        {
            IsBackground = true,
        }.Start();
    });
    // TestThreadWithDelayTask_Error: count = 1
}
```

在这两个 case 但中，虽然在 while 中包含了 wait Task，但是由于 Task.CompletedTask 实际上是一种同步代码，所以并不会进入到线程池当中。因此也就不会出现错误的情况。

但是这种错误的原因不是因为昙花线程，是由于我们在 Thread 中进行了 Wait，但是被调用的 Task 如果确实是一个异步的 Task，那么由于线程池繁忙，我们的 Task 就会被延迟执行，因此就会出现错误的情况。

## 总结

1. 在全同步的情况下，我们可以使用 TaskCreationOptions.LongRunning 或者 Thread 来实现常驻单一线程。从而实现稳定的常驻任务。
2. 注意 async/await 可能会导致线程池的使用，从而避免常驻单一线程被破坏。
3. 我们暂未给出带有异步代码的情况下如何实现稳定的常驻任务，我们将在后续讨论。

测试代码：https://github.com/newbe36524/Newbe.Demo/tree/main/src/BlogDemos/Newbe.LongRunningJob

## 参考

- [.NET Task 揭秘（2）：Task 的回调执行与 await](https://www.cnblogs.com/eventhorizon/p/15912383.html)[^1]
- [Task](https://threads.whuanle.cn/3.task/)[^2]
- [TaskCreationOptions](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.taskcreationoptions?view=net-7.0&WT.mc_id=DT-MVP-5004283)[^3]
- [这样在 C# 使用 LongRunningTask 是错的](https://newbe.hagicode.com/Others/0x026-This-is-the-wrong-way-to-use-LongRunnigTask-in-csharp/)[^4]
- [async 与 Thread 的错误结合](https://newbe.hagicode.com/Others/0x027-error-when-using-async-with-thread/)[^5]

[^1]: https://www.cnblogs.com/eventhorizon/p/15912383.html
[^2]: https://threads.whuanle.cn/3.task/
[^3]: https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.taskcreationoptions?view=net-7.0&WT.mc_id=DT-MVP-5004283
[^4]: https://newbe.hagicode.com/Others/0x026-This-is-the-wrong-way-to-use-LongRunnigTask-in-csharp/
[^5]: https://newbe.hagicode.com/Others/0x027-error-when-using-async-with-thread/

<!-- ending -->

<!-- ad -->

<!-- copyright-->
