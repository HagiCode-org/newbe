---
date: 2021-04-21
title: Newbe.Claptrap 0.10.2 发布，Blazor 演示
tags:
  - Newbe.Claptrap
  - 更新说明
---

Newbe.Claptrap 0.10.2 发布，我们为项目模板引入了 Minion 以及 Blazor 制作的交互界面。

<!-- more -->

<!-- md Header-Newbe-Claptrap.md -->

## 更新内容

### 类库常规升级

升级了相关的所有类库至最新版本。包括 Dapr SDK 1.1 等等。

### 项目模板增强

现在，我们为最新的项目模板引入了 Minion 以演示如何使用 Minion 处理旁路业务逻辑。

另外我们也引入了一个使用 [ant-design-blazor](https://ant-design-blazor.gitee.io/) 制作的的模拟演示界面，用于展示拍卖竞价样例中的数据情况。

### 可自定义 Event 和 State 的序列化过程

现在，开发者可以自定义 Event 和 State 的序列化过程，从而定义更加自由的保存和加载过程。

例如，在拍卖竞价示例中，我们使用到了 SortDictionary 作为 State 的一部分。但是，如果直接采用原生的 Json 序列化，将会导致 SortDictionary 的比较器丢失。因此，此时开发者可以使用自定义的 State Loader 来解决该问题。

详细的使用方案可以常见最新的项目模板。

<!-- md Footer-Newbe-Claptrap.md -->
