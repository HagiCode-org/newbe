---
date: 2018-04-30
title: 免费构建自己的博客-管理博客代码与发布到Github
tags:
  - Jekyll
  - Web
  - 网站开发
  - 教程
---

阅读完前面几节，读者想必已经能够在本地开发环境上正常运行自己的博客。那么本节内容，就说明以下，如何把博客发布的互联网上。

<!-- more -->

## Github Pages

Github是全球流行的~~同性交友~~代码托管平台以及开源项目聚集地。

我们可以将博客通过Github进行代码管理以及博客发布。这一切都是免费的。

### 注册

在这之前，读者需要到Github上注册自己的专属的~~交友~~账号：https://github.com/join?source=header-home

注册之后，登录Github。

**为了说明方便，我们假设新注册的账号名称为traceless**。

**为了说明方便，我们假设新注册的账号名称为traceless**。

**为了说明方便，我们假设新注册的账号名称为traceless**。

### 获得下载权限

点击右侧链接：https://github.com/Newbe36524/Newbe.Docs。

在界面的右上角点击 Star 获取下载权限。

![点击Star获取下载权限](/images/20180429-002.png)

### 下载文件到自己的账号中

点击下图中的`Fork`，将源代码下载到自己的账号中。

![下载文件到自己的账号中](/images/20180430-001.png)

经过一段时间的等待之后，浏览器会自动刷新，并打开下载成功的项目。

从右侧便可以看出，名称已经变更为：`traceless/Newbe.Docs` forked from `Newbe36524/Newbe.Docs`。

这就表明，已经成功下载了项目到自己的账号中。

### 发布博客到互联网中

在项目的页面上，选择`Settings`.

![点击Settings](/images/20180430-002.png)

滚动到下方，在`Github Pages`这个选项上，按照下图所示选择。

![Github Pages 选择](/images/20180430-003.png)

选择完毕后，点击右侧的`Save`按钮。

页面刷新之后，在此滚动到这个设置，便可以看到自动生成的博客地址。

![生成的博客地址](/images/20180430-004.png)

点击生成的博客地址，便可以查看到发布好的博客内容。

## 注册域名

由于文件路径的问题，上节发布的博客中，内容显示是不正常的。

可以通过添加域名，来解决此问题。

### 免费域名

点击右侧链接，进入免费域名注册页面：http://www.freenom.com/zh/index.html?lang=zh，按照提示进行域名注册。

通过这种方式注册的域名，可以使用一年，**次年快要到期的时候，可以免费续费**。

### 付费域名

付费域名的提供商很多，我推荐使用阿里云。

首先，点击链接获取最新的阿里云优惠券：https://promotion.aliyun.com/ntms/act/ambassador/sharetouser.html?userCode=vmx5szbq&utm_source=vmx5szbq

点击下图中的一键领取，获得优惠券，购买更便宜。

![领取优惠券](/images/20180430-005.png)

按照网站提示，注册并领取成功之后，在浏览器中输入链接地址，进行域名注册。https://wanwang.aliyun.com/

## 配置域名

域名注册成功之后，回到 Github Pages 的配置页面，将注册好的域名，填入 Custom domain 中。

![生成的博客地址](/images/20180430-006.png)

保存成功之后，在域名管理商中配置你的域名`CNAME`记录到`traceless.github.io`。

等待DNS刷新之后，便可以使用刚刚注册的域名，访问你的个人博客了。

## 推送自己的内容

前文中，通过修改本博客的源代码，实现了在本地修改博客的目的。

结合本节内容，读者便可以通过下载自己账号中的Fork的项目，来实现对自己博客的更新。

<!-- md Nav-Build-Your-Own-Blog.md -->
