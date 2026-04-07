---
date: 2020-06-10
title: 朋友，您可能是MCR的受害者
tags:
  - C#
  - Docker
  - Newbe.Claptrap
---

2018 年五月之后，微软将后续发布的所有 docker image 都推送到了 MCR （Miscrosoft Container Registry），但在中国大陆，它的速度实在是令人发指，本文将介绍一种方法来解决这个问题。

<!-- more -->

## 基本思路

MCR 团队已经决定尝试一些方案为此提速，相关的讨论罗列在[这个issue中](https://github.com/microsoft/containerregistry/issues/7)。我也将会持续跟踪这个issue，但谁也不知道什么时候会完成。

因此，笔者决定在 Github 上运用 Github Action 来自动将 MCR 上的镜像推送到国内阿里云的杭州节点。这样便可以实现中国大陆快速下载的目的。

## 如何使用

假如现在，你想要 pull mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim

那么只需要将其中的 mcr.microsoft.com/dotnet/core 替换为 registry.cn-hangzhou.aliyuncs.com/newbe36524

那么你就可以得到 registry.cn-hangzhou.aliyuncs.com/newbe36524/aspnet:3.1-buster-slim

另外，由于 Dockerfile 当中一般使用的是 mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim

因此，我们可以使用 docker tag 命令进行重新标记。

那么，总体的脚本就如下所示:

```bash
docker pull registry.cn-hangzhou.aliyuncs.com/newbe36524/aspnet:3.1-buster-slim
docker tag newbe36524/aspnet:3.1-buster-slim mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim
```

这样你就成功的在本地得到了 mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim 镜像。

## 为什么有一些还是 pull 不了

笔者并不知道所有人的需求，因此，如果有一些镜像未进行同步，您可以在以下任一仓库中提交 issue。笔者将进行调整：

- Github: https://github.com/newbe36524/Newbe.McrMirror
- Gitee: https://gitee.com/yks/Newbe.McrMirror

## 说点代码吧

其实真没啥好说的，要做到同步，只需要做到以下几点：

- 了解一下如何使用 Github Action 进行自动化构建
- 了解一下 docker 的 login/tag/pull/push 命令
- 为了避免编写 Github Action 定义文件的重复劳动，编写一个脚本来自动生成

那么就可以完成这项工作了。整个代码库只有6K。

## 最后，但是最重要

最近作者正在构建以`反应式`、`Actor模式`和`事件溯源`为理论基础的一套服务端开发框架。希望为开发者提供能够便于开发出“分布式”、“可水平扩展”、“可测试性高”的应用系统——Newbe.Claptrap

本篇文章是该框架的一篇技术选文，属于技术构成的一部分。如果读者对该内容感兴趣，欢迎转发、评论、收藏文章以及项目。您的支持是促进项目成功的关键。

当前项目已经快要发布 0.2 alpha 版本，欢迎参与讨论。

GitHub 项目地址：https://github.com/newbe36524/Newbe.Claptrap

Gitee 项目地址：https://gitee.com/yks/Newbe.Claptrap