---
date: 2019-09-10
title: 试试IEnumerable的另外6个小例子
tags:
 - 教程
 - C#
 - IEnumerable
---

IEnumerable 接口是 C# 开发过程中非常重要的接口，对于其特性和用法的了解是十分必要的。本文将通过6个小例子，来熟悉一下其简单的用法。

<!-- more -->

## 阅读建议

- 在阅读本篇时，建议先阅读前篇《[试试IEnumerable的10个小例子](./01-Try-More-On-IEnumerable.md)》，更加助于读者理解。
- 阅读并理解本篇需要花费5-10分钟左右的时间，而且其中包含一些实践建议。建议先收藏本文，闲时阅读并实践。

## 全是源码

以下便是这6个小例子，相应的说明均标记在注释中。

### T11分组合并

`{% dotnetfiddle KbtqSi https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T11分组合并.cs 1200 %}`

### T12拉平三重循环

`{% dotnetfiddle SgRu1z https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T12拉平三重循环.cs 1200 %}`

### T13遍历树

`{% dotnetfiddle bOlMuO https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T13遍历树.cs 1200 %}`

### T14搜索树

`{% dotnetfiddle 2SpQsM https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T14搜索树.cs 1200 %}`

### T15分页

`{% dotnetfiddle dK8l6Y https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T15分页.cs 1200 %}`

### T16分页与多级缓存

`{% dotnetfiddle RPWoSA https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T16分页与多级缓存.cs 1200 %}`

## 源码说明

以上示例的源代码放置于[博客示例代码库](https://github.com/newbe36524/Newbe.Demo/tree/master/src/BlogDemos/Try-More-On-IEnumerable)中。

项目采用 netcore 2.2 作为目标框架，因此需要安装 netcore 2.2 SDK 才能运行。
