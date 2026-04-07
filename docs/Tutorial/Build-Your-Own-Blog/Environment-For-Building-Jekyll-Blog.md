---
date: 2018-04-28
title: 免费构建自己的博客-开发环境安装
tags:
  - Jekyll
  - Web
  - 网站开发
  - 教程
---

本文将对本系列涉及到的主要软件安装过程进行统一说明。

<!-- more -->

## 开发环境

操作系统：Windows 10 Pro 版本作为演示版本，其他能够支持运行 Docker 的操作系统同样可行，但需要自行探究如何使用。

本系列教程将以 **Windows 10 Pro** 作为开发环境进行演示。

## Atom

Atom 是 Github 发布的开源跨平台文本编辑器。

作为本系列编写博客的主要文本编辑器，其中的若干插件对于编写博客较为便利。

以下便是安装的主要过程。

### 下载

通过官网链接，下载适合当前操作系统的版本。链接：https://atom.io/

### 安装

Atom 安装过程非常简单，不断的下一步即可。

### 插件

为了编写博客，需要安装一些便利插件，提升编写体验。

建议安装的插件有以下几个：

| 名称              | 说明                  |
|-----------------|---------------------|
| language-docker | 支持对Dockerfile进行高亮处理 |
| jekyll          | 支持jekyll中的一些模板标签提示  |
| tidy-markdown   | 支持markdown文档自动格式化   |

#### 安装过程

以下以安装 tidy-markdown 为例进行说明。

首先，关闭Atom。

按下`Win+X`，然后按下`A`，从而以管理员身份启动控制台或PowerShell。

输入以下命令，并回车：

```bash
apm install tidy-markdown
```

经过一段时间的等待之后，控制台输出`done`，则表明安装成功。

#### 不可告人的技巧

如果打开的是powershell，运行以下命令，可实现批量安装：

```bash
"language-docker","jekyll","tidy-markdown" | foreach { apm install $_ }
```

### 设置Atom

为方便在资源浏览器中打开Atom，可以通过在Atom中进行以下设置：

![设置Atom](/images/20180428-001.gif)

设置之后，便可以在文件夹中通过右键，快速打开Atom。

![打开Atom](/images/20180428-002.png)

## Docker for Windows

Docker 可以让你在一个隔离的环境中安装你需要的软件，而不会产生过大的开销。

本系列教程主要通过Docker来安装Jekyll环境，避免在Windows上进行太多复杂的环境安装。

### 启用Hyper-v

Hyper-v 是 Windows 操作系统原生提供的虚拟化软件。

该软件在 Windows 10 Pro 和 Enterprise ，以及 Windows Server 2016 上都可以开启。~~是的，家庭版还是别折腾了~~

以下是在 Windows 10 Pro 上的操作步骤：

按下`Win+X`，然后按下`A`，从而以管理员身份启动控制台或PowerShell。

输入以下命令，并回车：

```bash
dism.exe /Online /Enable-Feature:Microsoft-Hyper-V /All
```

经过一段时间的等待之后，要求重新启动计算机，选择Y。

**如果你是一步一步看教程做的，记得要先把本站点加入收藏夹，防止重启之后找不到哟。**

### 安装Docker For Windows

#### 下载

Docker For Windows 是在 Windows 10 上运行 Docker 的必要组件。

可以通过官网链接下载最新的版本：https://store.docker.com/editions/community/docker-ce-desktop-windows

#### 安装

双击下载完成的安装程序，不断下一步即可。不需要特殊处理。

安装完毕后，可以通过开始菜单，启动 Docker For Windows。

![开始菜单启动Docker](/images/20180428-025.png)

启动完成之后，可以在任务栏中看到相应的小鲸鱼。

![神秘小鲸鱼](/images/20180428-026.png)

### 设置国内Docker加速器

由于国内网络的特殊性，在使用 Docker 的时候需要配置一下国内的加速器。

有以下几种：

- daocloud https://www.daocloud.io/mirror#accelerator-doc
- 阿里云 https://cr.console.aliyun.com/#/accelerator

根据相关的网站说明，获取你专属的加速器地址。然后便可以配置在刚刚安装好的Docker中。

进入 Docker 的设置界面。

![点击Docker的设置按钮](/images/20180428-027.png)

在下图位置，设置你的加速器地址。

![配置加速器](/images/20180428-028.png)

点击确认，稍等一下，便完成了设置。

### 尝试启动

Docker 安装成功之后，可以采用以下方式启动第一个 Docker 应用。

nginx 是常见的一种Web软件。官方提供了linux版本和Windows版本，今天，我们则可以使用Docker，快速的安装一个nginx。

按下`Win+X`，然后按下`A`，从而以管理员身份启动控制台或PowerShell。

输入以下命令，并回车：

```bash
docker run  -d -p 8656:80 --name nginx nginx
```

等待一段时间之后，将会nginx就下载完了，并且启动运行，过程图示如下：

![配置加速器](/images/20180428-029.png)

接下在，继续运行以下命令，便可以成功看到刚刚启动的nginx界面。

```bash
start http://127.0.0.1:8656
```

![配置加速器](/images/20180428-030.png)

就此，Docker就已经能够在开发环境上正常运行了。

## Git Extensions

通过Git可以对你的博客内容进行版本管理，确保博客不会因为本计算机的奔溃而导致巨大的损失。

Git Extensions 是 Git 的一个图形化操作工具，可以更加方便的进行Git操作。

类似软件还有Git GUI/SourceTree/Tortoise Git等，读者可以根据自己的习惯选用。

### 下载

Git Extensions 是一个开源项目，软件本体发布在Github上，可以通过项目Release页面，下载最新的**SetupComplete
**版本：https://github.com/gitextensions/gitextensions/releases

### 安装

开始安装GitExtensions

![安装GitExtensions03](/images/20180428-003.png)

![安装GitExtensions04](/images/20180428-004.png)

![安装GitExtensions05](/images/20180428-005.png)

![安装GitExtensions06](/images/20180428-006.png)

![安装GitExtensions07](/images/20180428-007.png)

![安装GitExtensions08](/images/20180428-008.png)

![安装GitExtensions09](/images/20180428-009.png)

![安装GitExtensions10](/images/20180428-010.png)

中间~~强势~~插入安装Git For Windows

![安装GitExtensions11](/images/20180428-011.png)

![安装GitExtensions12](/images/20180428-012.png)

![安装GitExtensions13](/images/20180428-013.png)

![安装GitExtensions14](/images/20180428-014.png)

![安装GitExtensions15](/images/20180428-015.png)

![安装GitExtensions16](/images/20180428-016.png)

![安装GitExtensions17](/images/20180428-017.png)

![安装GitExtensions18](/images/20180428-018.png)

中间~~强势~~插入安装KDiff3

![安装GitExtensions19](/images/20180428-019.png)

![安装GitExtensions20](/images/20180428-020.png)

![安装GitExtensions21](/images/20180428-021.png)

![安装GitExtensions22](/images/20180428-022.png)

![安装GitExtensions23](/images/20180428-023.png)

![安装GitExtensions24](/images/20180428-024.png)

## 总结

就此，本系列需要用的主要软件就已经安装完毕了。

<!-- md Nav-Build-Your-Own-Blog.md -->
