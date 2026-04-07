---
date: 2023-02-18
title: 如何使用 ArrayPool
tags: [C#, Docker, Kubernetes]

slag: 0x01F-how-to-use-arraypool
summary: 如果不停的 new 数组，可能会造成 GC 的压力，因此在 aspnetcore 中推荐使用 ArrayPool 来重用数组，本文将介绍如何使用 ArrayPool。
---

<!-- YamlFrontMatter -->

如果不停的 new 数组，可能会造成 GC 的压力，因此在 aspnetcore 中推荐使用 ArrayPool 来重用数组，本文将介绍如何使用 ArrayPool。

<!-- more -->

## 使用 ArrayPool

ArrayPool 是一个静态类，它提供了一个共享的数组池，可以用来重用数组。它可以用来避免频繁的分配和回收数组，从而减少 GC 的压力。

ArrayPool 的使用非常简单，只需要调用它的静态方法 `Rent` 即可。`Rent` 方法有两个参数，第一个参数是数组的长度，第二个参数是数组的最小长度。如果你不知道数组的最小长度，可以传递一个默认值，比如 16。下面是一个使用 ArrayPool 的 C# 示例：

```csharp
using System;
using System.Buffers;

class Program
{
    static void Main(string[] args)
    {
        // 创建一个数组池
        var pool = ArrayPool<int>.Shared;

        // 从池中获取一个长度为 10 的数组
        int[] array = pool.Rent(10);
        try
        {
            // 在数组中填充一些数据
            for (int i = 0; i < array.Length; i++)
            {
                array[i] = i;
            }

            // 使用数组中的数据
            foreach (int i in array)
            {
                Console.WriteLine(i);
            }
        }
        finally
        {
            // 将数组归还到池中
            pool.Return(array);
        }
    }
}
```

在上面的示例中，我们首先通过调用 `ArrayPool<int>.Shared` 来获取一个数组池的实例。接下来，我们通过调用 pool.Rent(10) 方法从池中获取一个长度为 10 的整数数组。在数组中填充数据后，我们遍历数组并输出其中的元素。最后，我们通过调用 pool.Return(array) 方法将数组归还到池中。

需要注意的是，在使用完数组后，必须将其归还到池中，否则该数组将一直占用池中的内存，导致内存泄漏。

## 使用场景

一个典型的场景是在高吞吐量的网络应用程序中，例如 Web 服务器或消息队列服务器中。这些服务器需要处理大量的网络请求或消息，这些请求或消息可能涉及到大量的内存分配和释放。如果在每个请求或消息处理期间都需要分配和释放内存，那么垃圾回收器将面临重大的压力，导致系统性能下降。

使用 ArrayPool 可以通过池化内存缓解这种情况。这样，当需要分配数组时，可以从池中获取可用的数组而不是分配新的数组，从而减少垃圾回收的压力。一旦使用完毕，将数组返回到池中，以便可以重复使用。

例如，一个 HTTP 服务器可能需要同时处理多个客户端请求，每个请求都需要读取和处理请求正文。在这种情况下，可以使用 ArrayPool 来池化内存，以便在每个请求处理期间重复使用相同的缓冲区。这将减少内存分配和垃圾回收的开销，从而提高服务器的性能和吞吐量。

## 总结

ArrayPool 是一个静态类，它提供了一个共享的数组池，可以用来重用数组。它可以用来避免频繁的分配和回收数组，从而减少 GC 的压力。

## 参考

- [ArrayPool](https://learn.microsoft.com/dotnet/api/system.buffers.arraypool-1?view=net-7.0&WT.mc_id=DT-MVP-5004283)[^1]

[^1]: https://learn.microsoft.com/dotnet/api/system.buffers.arraypool-1?view=net-7.0&WT.mc_id=DT-MVP-5004283

<!-- ending -->

<!-- ad -->

<!-- copyright-->