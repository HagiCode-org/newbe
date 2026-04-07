---
date: 2020-11-11
title: Net5已经来临，让我来送你一个成功
tags:
  - 微信公众号文章
---

没错，那就是“下载成功”。

<!-- more -->

## 现在，已经可以急速下载.Net5 docker 镜像

.Net 5 进行今天已经正式发布，想必各位已经通过各种渠道了解到了此次发布的所有内容。

并且也都体会到了这次凑成三连的金 scott 是什么效果（啊哈，三连。

![scott](/images/20201111-001.jpg)

不过，目前在中国大陆地区拉取 MCR 上发布的 docker 镜像依旧是一件令人感到失望的事情。

为此，我们曾经在数月前发布了一款名为 docker-mcr 的 dotnet-tool 以便中国大陆地区的开发者可以快速拉取相应的镜像。

今天，我们也非常顺利的支持了最新发布的 .Net 5 一系列镜像。

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

## 还有一个好消息

更觉确凿的消息， MCR 中国大陆地区镜像 CDN 将会在 2020 年年底上线。因此，我们预计将会很快就能不使用其他工具，体会到急速下载的 MCR 的体验。

![github 消息](/images/20201111-002.png)

可以通过以下链接了解详情：

https://github.com/microsoft/containerregistry/issues/7

届时，原本作为 Newbe.Claptrap 项目附属产品的 Newbe.McrMirror 项目也将顺利完成它的使命。进入维护模式，并且将现有的文档翻译为英文，留给可能存在的其他国家和地区用户进行使用。
