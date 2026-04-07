---
date: 2025-05-09
title: 好哥哥因为没有搞清楚同步完成和异步完成导致代码死循环了这档事
tags: [C#, Docker, Kubernetes]

slag: 0049-Dive-into-async-and-sync-completion
summary: 有个好哥哥说他遇到循环代码死循环的问题，所以仔细的研究了一下，于是发现了关于同步完成和异步完成的区别。
---

<!-- YamlFrontMatter -->

有个好哥哥说他遇到循环代码死循环的问题，所以仔细的研究了一下，于是发现了关于同步完成和异步完成的区别。

<!-- more -->

## 什么是死循环

比如，长这个样子

```csharp
[Test]
public void EndlessLoop()
{
    Yanjia_foRever_niCE();
    Console.WriteLine("nice end"); // it will never reach here
    return;

    void Yanjia_foRever_niCE()
    {
        do
        {
            Thread.Sleep(100); // some code running synchronously
            Console.WriteLine("严架 nice");
        } while (GetBool());

        return;

        bool GetBool()
        {
            return true;
        }
    }
}
```

❌ 这段代码一但开始运行，将不会结束，也不会打印 `nice end`。
因为 `Yanjia_foRever_niCE` 这个方法是一个死循环，永远不会结束。


## 那如果 `GetBool()` 返回 `Task<bool>` 呢

比如，长这个样子

```csharp
[Test]
public void EndlessLoopWithSyncCompletion()
{
    Yanjia_foRever_niCE();
    Console.WriteLine("nice end"); // it will never reach here
    return;

    async Task Yanjia_foRever_niCE()
    {
        do
        {
            Thread.Sleep(100); // some code running synchronously
            Console.WriteLine("严架 nice");
        } while (await GetBoolAsync());

        return;

        Task<bool> GetBoolAsync()
        {
            return Task.FromResult(true);
        }
    }
}
```

❌ 这个代码，看起来用了 Task 但是依然是一个死循环。因为 `GetBoolAsync` 返回的是一个 Task，但它是一个同步完成的 Task。所有的操作都会在当前线程完成，不会切换到其他线程。

## 聪明的宝宝已经想到了可以加上 async await

比如，长这个样子

```csharp
[Test]
public void EndlessLoopWithSyncCompletion2()
{
    Yanjia_foRever_niCE();
    Console.WriteLine("nice end"); // it will never reach here
    return;

    async Task Yanjia_foRever_niCE()
    {
        do
        {
            Thread.Sleep(100); // some code running synchronously
            Console.WriteLine("严架 nice");
        } while (await GetBoolAsync());

        return;

        async Task<bool> GetBoolAsync()
        {
            return true;
        }
    }
}
```

❌ 但实际上，没有任何卵用，因为 `GetBoolAsync` 本质依然是一个同步完成的 Task。所有的操作都会在当前线程完成，不会切换到其他线程。
并且实际上会触发编译器警告，乖宝宝可不要这样写哟。

## 但是我用 await Task.FromResult(true) 很开心

比如，长这个样子

```csharp
[Test]
public void EndlessLoopWithSyncCompletion3()
{
    Yanjia_foRever_niCE();
    Console.WriteLine("nice end"); // it will never reach here
    return;

    async Task Yanjia_foRever_niCE()
    {
        do
        {
            Thread.Sleep(100); // some code running synchronously
            Console.WriteLine("严架 nice");
        } while (await GetBoolAsync());

        return;

        async Task<bool> GetBoolAsync()
        {
            return await Task.FromResult(true);
        }
    }
}
```

❌ 确实曾经有好哥哥这么写过代码，但是实际上 `await Task.FromResult(true)` 依然是一个同步完成的 Task。 `async` 和 `await` 是不会改变 Task 的完成方式的。
它是同步完成，就一直都是同步完成。当然这样写还有一个好处就是可以略微增加代码量 XD。

## 真的异步才行

比如，长这个样子

```csharp
[Test]
public void EndlessLoopWithAsyncCompletion()
{
    Yanjia_foRever_niCE();
    Console.WriteLine("nice end"); // it will reach here
    return;

    async Task Yanjia_foRever_niCE()
    {
        do
        {
            Thread.Sleep(100); // some code running synchronously
            Console.WriteLine("严架 nice");
        } while (await GetBoolAsync());

        return;

        async Task<bool> GetBoolAsync()
        {
            await Task.Delay(100);
            return true;
        }
    }
}
```

✅ 这段代码就可以正常结束了，因为 `GetBoolAsync` 返回的是一个异步完成的 Task。其中的 `await Task.Delay(100)` 会真的触发异步完成。从而导致 `Yanjia_foRever_niCE` 由于没有 await 而直接推进到 `nice end` 这行代码。

## 有人好奇 ValueTask 会怎么样

实际上上面所有的 Task 换成 ValueTask 都是一样的。比如

```csharp
ValueTask<bool> GetBoolAsync() // ❌
{
    return ValueTask.FromResult(true);
}

async ValueTask<bool> GetBoolAsync() // ❌
{
    return true;
}

async ValueTask<bool> GetBoolAsync() // ❌
{
    return await ValueTask.FromResult(true);
}

async ValueTask<bool> GetBoolAsync() // ✅
{
    await Task.Delay(100);
    return true;
}
```

这些代码产生的效果和上面所有的 Task 代码是一样的。

也就是 ValueTask 也不会影响这段代码是同步完成还是异步完成。

## 其实一开始是因为一个 Timer

.NET6 中的 `PeriodicTimer` 是一个定时器，它的 `WaitForNextTickAsync` 方法是一个返回 `ValueTask<bool>` 的方法。

它有一个很合理但是可能有时候注意不到的地方，就是计时是从创建实例开始的，而不是从调用 `WaitForNextTickAsync` 开始的。

比如下面这段代码：

```csharp
[Test]
public void EndlessLoopWithSyncCompletion()
{
    var timer = new PeriodicTimer(TimeSpan.FromSeconds(0.01));
    Yanjia_foRever_niCE();
    Console.WriteLine("nice end"); // it will never reach here
    return;

    async Task Yanjia_foRever_niCE()
    {
        do
        {
            Thread.Sleep(TimeSpan.FromSeconds(0.5)); // some code running synchronously
            Console.WriteLine("严架 nice");
        } while (await GetBoolAsync());

        return;

        ValueTask<bool> GetBoolAsync()
        {
            return timer.WaitForNextTickAsync();
        }
    }
}
```

这段代码中， timer 的创建时间是 0.01 秒，而 `Thread.Sleep` 的时间是 0.5 秒。这也就意味者，在每次进入 `GetBoolAsync` 方法时， timer 早就已经到了下一个 tick 的时间了。

所以这个时候 `timer.WaitForNextTickAsync()` 返回的就是一个同步完成的 ValueTask。

因为它是一个同步完成的 ValueTask，所以 `await` 也不会切换到其他线程。从而就导致了死循环。

而，如果将 timer 的创建时间改成 1 秒，那么当 `Thread.Sleep` 结束时， timer 的 tick 还没有到达，所以 `timer.WaitForNextTickAsync()` 返回的就是一个异步完成的 ValueTask。

这时候 `await GetBoolAsync()` 就会切换到调度器上，从而导致 `Yanjia_foRever_niCE` 结束，打印 `nice end`。

这就是一开始好哥哥遇到的问题。

## 总结

代码是同步完成还是异步完成，和返回值是 Task 还是 ValueTask 没有关系，和有没有 async/await 也没有关系。

它只与实现的代码究竟有没有真异步操作有关。

测试代码在：[GitHub](https://github.com/newbe36524/Newbe.Demo/tree/main/src/BlogDemos/Newbe.NiceValueTasks)

<!-- ending -->

<!-- ad -->

<!-- copyright-->
