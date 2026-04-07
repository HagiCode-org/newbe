---
date: 2020-08-01
title: Newbe.Claptrap 框架如何实现 Claptrap 的多样性？
tags:
  - Newbe.Claptrap
---

Newbe.Claptrap 框架如何实现 Claptrap 的多样性？最近整理了一下项目的术语表。今天就谈谈什么是 Claptrap Design 和 Claptrap Factory。

<!-- more -->

特别感谢 [kotone](https://github.com/kotoneme) 为本文提供的校对建议！

<!-- md Header-Newbe-Claptrap.md -->

## Claptrap Design 实现 Claptrap 的高可定制性

Claptrap 拥有较高的可定制性。开发者可以为 Claptrap 对象设置自定义的 Event Loader/ Event Saver/ State Loader / State Saver / EventNotification Method 等等一系列组件。而这一切的自定义，都可以具体反映到 Claptrap Design 对象上。

Claptrap Design 就像一个设计图，决定了 Claptrap 的每个细节，常见的包括：

1. 采用什么样的 Event Loader / Event Saver 来处理事件。
2. 多久保存一次 State 快照。
3. Minion ，如果是，那么 Master 是谁。
4. 有多少种事件，对应的 Event Handler 分别是什么。

这些细节都会在应用程序启动时，将会通过类型扫描、属性标记、连贯接口、配置文件等等多种方式进行配置。从而形成完整的 Claptrap Design。并且，启动时会对 Claptrap Design 进行合理性的验证，确保 Claptrap Design 都是基本可用的。从而不会出现类似于“忘记编写 Event 对应的 Handler”这样低级的错误。

所有的 Claptrap Design 都会被集中保存在 IClaptrapDesignStore 这样一个内存对象中，以便 Claptrap Factory 在构建 Claptrap 检索。

开发者也可以基于 IClaptrapDesignStore 中的所有数据，来构成可供人类阅读的文本或者图形，以便更容易地从高层面来了解当前系统中 Claptrap 之间的相互关系和配置细节，源于代码却高于代码。

---

以下是关于故事化描述，用于辅助理解。不必太过在意。

Claptrap Design 是 Claptrap Factory 进行 Claptrap 生产的重要依据。在 Design 中记录了对特定种类 Claptrap 所需要配备的定制化装置。例如：决定多功能任务处理器中的任务执行模组；决定手持型备忘录的设备型号；决定内存恢复控制器的恢复策略。

在决定 Claptrap 投产之前，设计好 Claptrap Design 是确保最终产物符合需求的重要一环。

---

## Claptrap Factory 组装 Claptrap

Claptrap 拥有较高的可定制性。开发者可以为 Claptrap 对象指定自定义的 Event Loader/ Event Saver/ State Loader / State Saver / EventNotification Method 等等一系列组件。为了适应这种可定制性，故而需要选用良好的方案来实现 Claptrap 对象的装配。

目前框架选用的是 Autofac 作为装配器来完成。主要原因是 Autofac 支持 Delegate Factory / Decorator / Generic Type / Module 等等一些相较于 System.DepenedencyInjection 更丰富的特性。

## Claptrap Factory 控制 Claptrap 生命周期

由于 Claptrap Factory 是 Claptrap 的生产者，因此一般也负责 Claptrap 级的生命周期控制功能。在基于 Autofac 实现的 Claptrap Factory，这种生命周期控制就体现在使用 Autofac 的 LifetimeScope 对象来控制整个装载、创建和卸载的过程。

---

以下是关于故事化描述，用于辅助理解。不必太过在意。

Claptrap Factory 是进行 Claptrap 进行生产的主要场所。它将依照给定的 Claptrap Design 对每一个出厂的 Claptrap 执行定制化装配，而它拥有着极高的产品合格率和工作效能。

---

<!-- md Footer-Newbe-Claptrap.md -->
