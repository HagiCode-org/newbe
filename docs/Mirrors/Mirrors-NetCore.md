---
date: 2019-12-22
title: NetCore 国内加速下载
tags:
  - NetCore
  - Mirrors
  - 加速下载
  - 镜像加速
  - 国内加速
---

NetCore docker 镜像. 国内直接从官网（https://mcr.microsoft.com）下载比较困难，需要一些技术手段。这里提供一个国内的镜像下载地址列表，方便网友下载。

<!-- more -->

存在至少三种方法进行加速：

- 使用 docker-mcr （推荐）
- 拉取国内服务器上的镜像
- 使用 DockerHub 加速器

注意，无论采用什么方式，请先确保本地的 docker 已经正常可用。

### 使用 docker-mcr （推荐）

docker-mcr 是一个 dotnet core global tool，简单几步，便可以进行安装和使用。

[进入dotnet页面，下载并安装 netcore 3.1 SDK](https://dotnet.microsoft.com/download)。

安装完毕后打开控制台运行以下命令:

```bash
dotnet tool install newbe.mcrmirror -g 
```

现在，假如需要拉取 mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim ，则运行以下命令：

```bash
docker-mcr -i mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim
```

等待完成之后，便可以在本地看到已经拉取完毕的镜像。

您可以运行 `docker-mcr --help` 来查看更多的参数配置方式。

如果您曾经安装过 newbe.mcrmirror ,您需要使用`dotnet tool update newbe.mcrmirror -g`命令来进行升级，确保最佳的体验。

### 拉取国内服务器上的镜像

加速的本质是因为我将镜像推送到了国内的服务器，目前在以下服务器均存在镜像:

- 阿里云 registry.cn-hangzhou.aliyuncs.com/newbe36524
- 腾讯云 ccr.ccs.tencentyun.com/mcr_newbe36524

以下以阿里云为例进行说明，假设需要拉取 aspnet:3.1-buster-slim

则拼接上面的前缀，则得到地址 registry.cn-hangzhou.aliyuncs.com/newbe36524/aspnet:3.1-buster-slim

然后，为了不修改默认的 Dockerfile 您可以运行以下命令:

```bash
docker pull registry.cn-hangzhou.aliyuncs.com/newbe36524/aspnet:3.1-buster-slim
docker tag newbe36524/aspnet:3.1-buster-slim mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim
```

这样你就成功的在本地得到了 mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim 镜像。

当然，你也可以直接把 registry.cn-hangzhou.aliyuncs.com/newbe36524/aspnet:3.1-buster-slim 写入到你的 Docker file 中。

### 使用 DockerHub 加速器

我也将镜像推送到了 dockerhub ，所以正常来说，在中国大陆使用 dockerhub 加速器也可以达到加速的效果。

规则，`mcr.microsoft.com/dotnet/core/{name}:{tag}` -> `newbe36524/{name}:{tag}`

例如，您可以运行以下命令:

```bash
docker pull newbe36524/aspnet:3.1-buster-slim
docker tag newbe36524/aspnet:3.1-buster-slim mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim
```

这样你就成功的在本地得到了 `mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim` 镜像。

当然，你也可以直接把 `newbe36524/aspnet:3.1-buster-slim` 写入到你的 Docker file 中。

在此之前，请确保你正确配置了本地的加速器。

<!-- more -->
<!-- md Mirrors.md -->
