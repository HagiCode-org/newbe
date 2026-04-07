---
date: 2020-06-16
title: docker-mcr 助您全速下载 dotnet 镜像
tags:
  - C#
  - Docker
  - Newbe.Claptrap
top: 80
---

2018 年五月之后，微软将后续发布的所有 docker image 都推送到了 MCR （Miscrosoft Container Registry），但在中国大陆，它的速度实在是令人发指，本文将介绍一种方法来解决这个问题。

<!-- more -->

## 使用方法

![下载方式](/images/20200616-001.png)

存在至少三种方法进行加速：

- 使用 docker-mcr （推荐）
- 拉取国内服务器上的镜像
- 使用 DockerHub 加速器

注意，无论采用什么方式，请先确保本地的 docker 已经正常可用。

### 使用 docker-mcr

docker-mcr 是一个 dotnet core global tool，简单几步，便可以进行安装和使用。

[进入 dotnet 页面，下载并安装 netcore 3.1 或 5 SDK](https://dotnet.microsoft.com/download)。

安装完毕后打开控制台运行以下命令:

```bash
dotnet tool install newbe.mcrmirror -g
```

现在，假如需要拉取 mcr.microsoft.com/dotnet/aspnet:5.0-buster-slim ，则运行以下命令：

```bash
docker-mcr -i mcr.microsoft.com/dotnet/aspnet:5.0-buster-slim
```

等待完成之后，便可以在本地看到已经拉取完毕的镜像。

如果您曾经安装过 newbe.mcrmirror ,您需要使用以下命令来进行升级，确保最佳的体验。

```bash
dotnet tool update newbe.mcrmirror -g
```

### 拉取国内服务器上的镜像

加速的本质是因为我将镜像推送到了国内的服务器，目前在以下服务器均存在镜像:

- 阿里云 registry.cn-hangzhou.aliyuncs.com/newbe36524

假设需要拉取 aspnet:5.0-buster-slim

[点击此处打开配置文件](https://gitee.com/yks/Newbe.McrMirror/raw/master/src/GithubActionGeneration/config-v2.json)，搜索 mcr.microsoft.com/dotnet/core/aspnet:5.0-buster-slim 会找到以下节点

```json
{
  "tag": "aspnet:5.0-buster-slim",
  "source": "mcr.microsoft.com/dotnet/aspnet:5.0-buster-slim"
}
```

则说明在国内镜像的 tag 为 aspnet:5.0-buster-slim。

则拼接上面的前缀，则得到地址 registry.cn-hangzhou.aliyuncs.com/newbe36524/aspnet:5.0-buster-slim

然后，为了不修改默认的 Dockerfile 您可以运行以下命令:

```bash
docker pull registry.cn-hangzhou.aliyuncs.com/newbe36524/aspnet:5.0-buster-slim
docker tag registry.cn-hangzhou.aliyuncs.com/newbe36524/aspnet:5.0-buster-slim mcr.microsoft.com/dotnet/aspnet:5.0-buster-slim
```

这样你就成功的在本地得到了 mcr.microsoft.com/dotnet/aspnet:5.0-buster-slim 镜像。

当然，你也可以直接把 registry.cn-hangzhou.aliyuncs.com/newbe36524/aspnet:5.0-buster-slim 写入到你的 Docker file 中。

### 使用 DockerHub 加速器

我也将镜像推送到了 dockerhub ，所以正常来说，在中国大陆使用 dockerhub 加速器也可以达到加速的效果。

规则，`mcr.microsoft.com/dotnet/{name}:{tag}` -> `newbe36524/{name}:{tag}`

例如，您可以运行以下命令:

```bash
docker pull newbe36524/aspnet:5.0-buster-slim
docker tag newbe36524/aspnet:5.0-buster-slim mcr.microsoft.com/dotnet/aspnet:5.0-buster-slim
```

这样你就成功的在本地得到了 mcr.microsoft.com/dotnet/aspnet:5.0-buster-slim 镜像。

当然，你也可以直接把 newbe36524/aspnet:5.0-buster-slim 写入到你的 Docker file 中。

在此之前，请确保你正确配置了本地的加速器。

## 起因经过

将微软发布在 MCR 上的镜像同步到 DockerHub 上，以加速中国大陆的下载速度。

正如我们所知，微软在 2018 年五月之后，只会将相关镜像打包发布到 MCR 上。

但是，在中国大陆从 MCR 上拉取镜像简直慢得让人发指。

MCR 团队已经决定尝试一些方案为此提速，相关的讨论罗列在[这个 issue 中](https://github.com/microsoft/containerregistry/issues/7)。我也将会持续跟踪这个 issue。

## 代码仓库

docker-mcr 以及 Github Action 相关的代码都在以下仓库中，如果您在使用中遇到了任何问题，可以通过 issue 进行反馈：

- Github: https://github.com/newbe36524/Newbe.McrMirror
- Gitee: https://gitee.com/yks/Newbe.McrMirror

## 最后，但是最重要

最近作者正在构建以`反应式`、`Actor模式`和`事件溯源`为理论基础的一套服务端开发框架。希望为开发者提供能够便于开发出“分布式”、“可水平扩展”、“可测试性高”的应用系统——Newbe.Claptrap

此次的加速工具实际上是笔者在编写样例时遇到下载困难时编写的工具。

本篇文章是该框架的一篇技术选文，属于技术构成的一部分。如果读者对该内容感兴趣，欢迎转发、评论、收藏文章以及项目。您的支持是促进项目成功的关键。

当前项目已经快要发布 0.2 alpha 版本，欢迎参与讨论。

GitHub 项目地址：https://github.com/newbe36524/Newbe.Claptrap

Gitee 项目地址：https://gitee.com/yks/Newbe.Claptrap
