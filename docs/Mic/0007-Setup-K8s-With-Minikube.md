---
date: 2021-09-05
title: 简单三分钟，本地搭建k8s
slug: /Mic/0007-Setup-K8s-With-Minikube
tags:
  - Newbe.Claptrap
  - k8s
  - kubenates
---

使用 minikube 在本地搭建 k8s 已经比以前要简单很多了。本文，我们通过简短的三分钟来重现一下在本地搭建 k8s 实验环境的步骤。

<!-- more -->

<!-- md Header-Newbe-Claptrap.md -->

## 下载 Minikube

首先，你可能会考虑从官网下载 minikube 然后进行安装，但是这样实际上可以预知的是，在后续的使用中你可能会到由于网络的特殊性，无法正常地启动。

因此，需要使用一些特殊的办法来解决这个问题。

这里，我们直接使用由阿里云团队针对中国大陆网络环境进行优化的版本。

Mac OSX

```bash
curl -Lo minikube https://kubernetes.oss-cn-hangzhou.aliyuncs.com/minikube/releases/v1.20.0/minikube-darwin-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/
```

Linux

```bash
curl -Lo minikube https://kubernetes.oss-cn-hangzhou.aliyuncs.com/minikube/releases/v1.20.0/minikube-linux-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/
```

Windows

https://kubernetes.oss-cn-hangzhou.aliyuncs.com/minikube/releases/v1.20.0/minikube-windows-amd64.exe

下载 minikube-windows-amd64.exe 文件，并重命名为 minikube.exe

下面我们都将围绕 windows 版本进行说明和演示。

> 虽然官方版本已经支持中国区的镜像加速，但是截至笔者自己发文的时候，还是存在各种问题。本着人的生命是有限的基本原则，我们可以先跳过这些恼人的问题。

## 安装 Minikube

windows 版本只要下载到特定文件夹，然后将这个文件夹，加入到 PATH 当中即可。这样以后无论在那个路径下都可以正常运行 minikube 命令。

## 启动 Hyper-v

虽然最新的 minikube 对于 Docker 和 Hyper-v 都是首选驱动，但是 Docker 无法使用 ingress 插件，因此考虑使用 Hyper-v。

使用管理员权限运行以下脚本来启用 Hyper-v:

```bash
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

启用后需要重新启动操作系统才能生效。

## 配置 Minikube

使用管理员权限打开一个控制台，并运行以下命令，来设置驱动、CPU 和内存：

```bash
minikube config set driver hyperv
minikube config set cpus 8
minikube config set memory 12288
```

CPU 和内存可以按照你的实际情况进行设置。其中内存的单位为 MB，12288 即表示 12G。

在 Hyper-v 中，这实际上就是虚拟机的 CPU 和内存。

## 启动 k8s

使用管理员权限打开一个控制台，并运行以下命令，来启动一个 k8s 节点：

```bash
minikube start
```

运行这段命令后，经过一段时间的等待，你应该会得到如下所示的输出内容，这就表示你已经正确启动了一个 k8s 节点：

```bash
PS C:/Users/Administrator> minikube start
😄  Microsoft Windows 10 Enterprise 10.0.19042 Build 19042 上的 minikube v1.20.0
✨  根据用户配置使用 hyperv 驱动程序
👍  Starting control plane node minikube in cluster minikube
🔥  Creating hyperv VM (CPUs=8, Memory=12288MB, Disk=20000MB) ...
🐳  正在 Docker 20.10.6 中准备 Kubernetes v1.20.2…
    ▪ Generating certificates and keys ...
    ▪ Booting up control plane ...
    ▪ Configuring RBAC rules ...
🔎  Verifying Kubernetes components...
    ▪ Using image registry.cn-hangzhou.aliyuncs.com/google_containers/storage-provisioner:v5 (global image repository)
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

## 启用 dashboard 看看集群

运行以下命令：

```bash
minikube dashboard
```

稍等片刻，浏览器便会打开 dashboard，你就可以看到集群的基本情况。

![dashboard](/images/20210905-001.png)

## 使用 lens 查看集群

除了使用原生的 dashboard，你也可以使用 lens 来查看这个集群的情况。

通过 https://k8slens.dev/ 下载和安装最新的 lens 版本。

然后打开之后，便可以通过 lens 来查看集群的基本情况。

![lens1](/images/20210905-002.png)

![lens2](/images/20210905-003.png)

![lens3](/images/20210905-004.png)

## 安装 helm

为了验证这个集群的基础功能，我们尝试使用 helm 来安装一个简单的应用

首先，需要安装 helm。 helm 和 minikube 一样，是一个单文件的命令行程序。可以直接从 Github 上下载。

或者也可以通过以下地址加速下载：

[下载 helm](/docs/Mirrors/Mirrors-Helm.md )

下载，设置好 PATH 之后，我们就可以在控制台中调用 helm：

```bash
PS C:/Users/Administrator> helm version
version.BuildInfo{Version:"v3.6.3", GitCommit:"d506314abfb5d21419df8c7e7e68012379db2354", GitTreeState:"clean", GoVersion:"go1.16.5"}
```

## 添加 bitnami 为 helm 包源

helm 实际上是一个包安装器，这个包被称为 charts，每个 chart 实质上就是一组 k8s 资源的定义。

因此，和软件安装一样，想要安装一个软件，首先需要选择一个软件包源来下载这个软件包。

bitnami 是 VMware 提供的一个包源，其中包含了一些已经被用于产线的常用中间件包，比如 mysql，elasticsearch，mongodb，wordpress 等等。

通过以下命令，便可以添加这个包源。

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
```

添加好之后，可以使用以下命令来查看已经添加的所有包源：

```bash
PS C:/Users/Administrator> helm repo list
NAME    URL
bitnami https://charts.bitnami.com/bitnami
dapr    https://dapr.github.io/helm-charts/
```

## 使用 helm 安装一个 nginx

这里我们以安装一个简单的 nginx 为例，演示一下如何安装 helm chart 包。

通过运行以下命令，便可以从 bitnami 上安装一个 nginx 到集群中：

```bash
helm install my-release bitnami/nginx
```

同时，如果你前面安装了 lens， 那么也可以通过左侧的 APP/Charts 来安装：

![nginx](/images/20210905-005.png)

安装好之后，便可以使用 k8s 的 port-forward 功能来查看安装结果。当然，在 lens 上，只需要一次鼠标点击可以：

![nginx-port-forward](/images/20210905-006.png)

![view nginx](/images/20210905-007.png)

## 移除安装的 helm chart

通过 lens app/release 菜单，你可以非常简单的移除刚刚安装的 chart。

![remove release](/images/20210905-008.png)

## 停止和移除 minikube 节点

如果你想停止当前 minikube 节点以节约资源，可以运行以下命令：

```bash
minikube stop
```

如果你想移除安装的 minikube 节点（hyper-v 虚拟机），可以运行以下命令：

```
minikube delete --all
```

## 本篇小结

通过简单的 minikube 、 helm 和 lens， 你便可以拥有一个非常简单的 k8s 测试环境。

一切就是这样的轻松愉快。

## 相关链接

af 开头的链接为 af code，你可以通过 https://af.newbe.pro/ 来了解如何使用此链接进行快速收藏。

### 阿里云版本 minikub

https://github.com/AliyunContainerService/minikube

af://1eyJ1IjoiaHR0cHM6Ly9naXRodWIuY29tL0FsaXl1bkNvbnRhaW5lclNlcnZpY2UvbWluaWt1YmUiLCJ0IjoiQWxpeXVuQ29udGFpbmVyU2VydmljZS9taW5pa3ViZSIsInRzIjpbIms4cyIsIm1pbmlrdWJlIiwiXHU5NjNGXHU5MUNDXHU0RTkxIl19

### Github minikub

https://github.com/kubernetes/minikube

af://1eyJ1IjoiaHR0cHM6Ly9naXRodWIuY29tL2t1YmVybmV0ZXMvbWluaWt1YmUiLCJ0Ijoia3ViZXJuZXRlcy9taW5pa3ViZTogUnVuIEt1YmVybmV0ZXMgbG9jYWxseSIsInRzIjpbImdpdGh1YiIsIm1pbmlrdWJlIl19

### Github minikub

https://github.com/kubernetes/minikube

af://1eyJ1IjoiaHR0cHM6Ly9naXRodWIuY29tL2t1YmVybmV0ZXMvbWluaWt1YmUiLCJ0Ijoia3ViZXJuZXRlcy9taW5pa3ViZTogUnVuIEt1YmVybmV0ZXMgbG9jYWxseSIsInRzIjpbImdpdGh1YiIsIm1pbmlrdWJlIl19

### Github helm

https://github.com/helm/helm

af://1eyJ1IjoiaHR0cHM6Ly9naXRodWIuY29tL2hlbG0vaGVsbSIsInQiOiJoZWxtL2hlbG06IFRoZSBLdWJlcm5ldGVzIFBhY2thZ2UgTWFuYWdlciIsInRzIjpbImdpdGh1YiIsImhlbG0iXX0=

### Github helm 加速下载

https://newbe.hagicode.com/Mirrors/Mirrors-Helm/

af://1eyJ1IjoiaHR0cHM6Ly93d3cubmV3YmUucHJvL01pcnJvcnMvTWlycm9ycy1IZWxtLyIsInQiOiJIZWxtIFx1NTZGRFx1NTE4NVx1NTJBMFx1OTAxRlx1NEUwQlx1OEY3RCB8IG5ld2JlIiwidHMiOlsiaGVsbSIsIm1pcnJvciJdfQ==

### Github bitnami charts

https://github.com/bitnami/charts

af://1eyJ1IjoiaHR0cHM6Ly9naXRodWIuY29tL2JpdG5hbWkvY2hhcnRzIiwidCI6ImJpdG5hbWkvY2hhcnRzOiBIZWxtIENoYXJ0cyIsInRzIjpbImJpdG5hbWkiLCJjaGFydHMiLCJoZWxtIl19

<!-- md Footer-Newbe-Claptrap.md -->
