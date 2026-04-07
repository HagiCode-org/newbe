---
date: 2020-10-31
title: Newbe.ObjectVisitor 0.1.4 发布，初始版本
tags:
  - Newbe.ObjectVisitor
  - 更新说明
---

Newbe.Claptrap 0.1.4 发布，初始版本。

<!-- more -->

## 更新内容

我们发布了第一个版本。0.1 版本中我们完成了最基础的 ForEach API，并且实现了 FormatString 方法。

## 视频

与此类库相关的视频截至目前已经更新了 22 个。开发者可以前往以下地址查看相关概念和用法。

https://www.bilibili.com/video/BV15y4y1r7pK

## 基准测试

我们对初始版本进行了基准测试。得出了以下结论，详细的内容也可以前往仓库首页查看：

1. 该类库可以实现和硬编码一样快速的性能。
2. 该类库比直接使用反射更快。
3. 对于非代码热点路径，即使使用非缓存方式调用也仍然在可接受范围内容。

![Cache](/images/20201031-001.png)

![NoCache](/images/20201031-002.png)

<!-- md Footer-Newbe-ObjectVisitor.md -->
