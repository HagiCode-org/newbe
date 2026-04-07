---
date: 2019-11-17
title: 总结一下 IEnumerable 的例子
top: -1
cover: true
tags:
 - 教程
 - C#
 - IEnumerable
---

本篇将围绕 《[试试 IEnumerable 的10个小例子](./01-Try-More-On-IEnumerable.md)》和《[试试 IEnumerable 的另外6个小例子](./02-Try-More-On-IEnumerable-2.md)》给出的例子，总结一下对于`IEnumerable`接口的一些使用方法，希望读者能够从中获得一些启发。

<!-- more -->

## 框架类型的迭代

对于一个实现了`IEnumerable`接口的类型来说，开发中最常用的，就是把这个类型的对象放入到`foreach`等循环关键词中进行迭代，遍历其中的元素进行处理。

这种遍历通常分为两种目的：遍历和查找。

`IEnumerable`及其泛型版本`IEnumerable<T>`定义了一个类型的“可迭代性”。这点很容易理解，系统中的很多集合类型都实现了该接口。

因此这些集合类型均可以采用`foreach`进行迭代遍历。但是每个集合类型的迭代方式和结果是不完全相同的，这取决于集合本身的特性。例如：

- `List<>`、`Stack<>`和`Queue<>`的迭代的顺序不相同，因为数据结构本身要求是不同的
- `ConcurrentDictionary<,>`和``Dictionary<,>``在迭代时的线程安全性是不同的，因为针对线程安全的设计是不同的
- `BlockingCollection.GetConsumingEnumerable`方法返回一个会产生阻塞的消费者对象，

所以，即使都是丢进`foreach`，但是效果也是不完全一样的。使用这些，需要读者对这些类型本身需要增进了解。

建议读者在使用框架中实现了`IEnumerable`的类型时，一定要注意迭代的细节，可以通过MSDN上的文档了解其特殊性。

## Linq

Linq是一个说小不小的话题，这里只是说其中的 Linq To Object 部分内容。

通过Linq中提供的一些扩展方法，可以方便的控制对于一个`IEnumerable`对象的迭代方式。通过这些方法的应用，可以在很多时候避免复杂的条件和循环嵌套。

同时，Linq中抽象的Func和Action，也要求开发人员在平时的编写过程中注意对于迭代本身的归类和整理。`Where(IsLeapYear)`会比`Where(x=>(x % 4 == 0 && x % 100 != 0) || x % 400 == 0)`来的更加容易阅读。

## 设计复杂的数据结构及其迭代算法

除了基础的数据结构，开发过程中有时需要自定义一些集合类型。这些集合类型需要自己实现一个迭代过程。例如：二叉树及其遍历，对列表进行分页等等。

这些数据结构的迭代通常需要特定算法的支持。

在《[试试 IEnumerable 的另外6个小例子](./02-Try-More-On-IEnumerable-2.md)》中关于树的几个例子便数据此类中。

## 本地函数

在C#7.0引入了[本地函数](https://docs.microsoft.com/zh-cn/dotnet/csharp/whats-new/csharp-7#local-functions)之后， `IEnumerable`结合本地函数，快速实现自定义迭代过程的奇怪操作也就跟着出现。

通过这种操作可以在一个函数内采用一些以前不容易实现的方式实现一些操作：

- 将多重循环拉平
- 将多级条件判断变为循环判断
- 无需创建新的类就能快速生成一个上下文需要的特殊迭代算法

这相关的例子在《[试试 IEnumerable 的10个小例子](./01-Try-More-On-IEnumerable.md)》中较多。

按照月老板的名言：“业务复杂度是不会因为系统设计变化而减少的，它只是从一个地方转移到了另外的地方。”，我们可以知道，这种写法其实没有使得原来就有的判断和循环变少。只是改变了语法结构。

读者可以将这种操作作为一种“语法糖”进行使用。如果是在团队项目中，则需要尊重团队成员的共同意见，因为这种操作并非所有人都愿意接受。

当然，这种做法在一些地方会产生好处。例如在将本地函数、IEnumerable和Task相结合的 T10测试网络连接 中。这种写法就减少了传统写法中需要创建一个`List`或者`Array`的开销。

总之，这种写法，提供了一种新的思路。是否一定要使用，将取决于读者团队的接受程度。

## 异步迭代器

在 C# 8 和 .netcore 3.0 到来的版本中，我们迎接到了`IAsyncEnumerable`接口来实现异步迭代器的功能。

`IEnumerable`是同步方法的迭代器，`IAsyncEnumerable`可以看做是其异步版本。有了这个接口，那么在迭代的过程中也可以充分利用async/await带来的编程快感。

本系列中没有添加这部分的示例，但是主体思路是一致的。

她的出现，只会使得开发者更容易应用以上总结的几种主要场景。

详细的例子，可以[参见相关文章进行了解](https://www.cnblogs.com/yanxiaodi/p/Support-IAsyncEnumerable-with-LINQ.html)。

## 总结

本系列到此便结束了，希望读者多在实践中体会以上总结的几种使用场景。

本系列中的例子已经全部使用[dotnetfiddle.net](https://dotnetfiddle.net)进行了重写，读者可以直接在本博客的页面上运行这些示例。

如果无法正常的展示示例，读者也可以[通过本仓库下载示例相关的代码](https://github.com/newbe36524/Newbe.Demo/tree/master/src/BlogDemos/Try-More-On-IEnumerable)。
