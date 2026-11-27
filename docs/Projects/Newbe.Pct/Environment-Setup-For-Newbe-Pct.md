---
date: 2018-12-04
title: Newbe.Pct-开发环境准备
tags:
  - Newbe.Pct
  - Web
  - 教程
  - 自动化测试
---

本文将介绍使用Newbe.Pct项目所需要的环境准备工作。本篇作为启动项目的基本篇是必不可少的。但是，假如读者希望先了解本项目的功能效果，读者可以先阅读《[Newbe.Pct 开始使用](./Get-Started-Overview-For-Newbe-Pct.md))》

<!-- more -->

## 操作系统

本项目基于Java与NodeJs运行。因此，正常在能够正常运行Java与NodeJs的操作系统，都可以作为开发或运行用的操作系统。

本系列文章采用 `Windows 10 专业版 Build 17134`作为演示操作系统。

正常，在Mac和Linux操作系统上也同样能够实现本系列文章所述内容。需要读者自行尝试。

以下所有步骤均要按顺序执行安装，若前一步没有成功，则下一步通常也不会成功。

## 浏览器

本项目原理上支持 Chrome、Firefox 和 IE 浏览器。本系列文章主要围绕 Chrome 浏览器相关的内容进行描述。

因此，读者需要从以下链接下载和安装 Chrome 浏览器：

https://www.google.cn/chrome/

## Java

关于Java的版本，本项目要求 Java7+ 。

Java环境的安装，可以参考以下文章：

http://www.runoob.com/java/java-environment-setup.html

对于初学者需要特别注意的是：以上链接中提到了Java的开发环境和IDE的安装。

其中IDE的安装是本项目所不需要的，注意甄别。

作者编写此文章时，所使用的Java版本为 `x64 1.8.0_112`。建议至少安装同版本或更高版本以便能够正常运行示例中的内容。

## NodeJs

关于Java的版本，本项目要求 NodeJs 8+ 。

NodeJs环境的安装，可以参考以下文章：

http://www.runoob.com/nodejs/nodejs-install-setup.html

作者编写此文章时，所使用的NodeJs版本为 `x64 10.13.0`。建议至少安装同版本或更高版本以便能够正常运行示例中的内容。

## 安装与设置 webdriver-manager

webdriver-manager 作为本项目的浏览器驱动引擎，是非常关键的一项内容。

以下，详细叙述一下安装步骤。

### 安装 webdriver-manager

打开 控制台（或 Teminal ）, 在控制台中输入以下命令

```bash
npm install -g webdriver-manager
```

若安装之后，界面上没有任何明显的错误提示，则说明安装成功。

### 在线初始化 webdriver-manager

打开 控制台（或 Teminal ）, 在控制台中输入以下命令

```bash
webdriver-manager status
```

将会输出类似以下内容

```bash
C:\Users\newbe36524>webdriver-manager status
webdriver-manager: using global installed version 12.1.0
[18:19:53] W/status - the out_dir path C:\Users\newbe36524\AppData\Roaming\npm\node_modules\webdriver-manager\selenium does not exist
```

此内容表示当前 webdriver-manager 还未安装任何浏览器自动化驱动。

在控制台中输入以下命令

```bash
webdriver-manager update
```

值得注意的是，该步骤需要从`googleapis.com`网站下载文件。由于众所周知的原因，在大陆访问该站点时，会出现无法下载的情况，导致这一步失败。因此，通过以下命令设置网络代理，以实现加速下载

```bash
webdriver-manager update --proxy=http://127.0.0.1:1080
```

### 离线初始化 webdriver-manager

若读者在无法正常使用在线方案实现初始化 webdriver-manager ，这里同样提供离线方案。

通过下面链接下载已经下载好的压缩包

https://pan.baidu.com/s/1tSI3MzbhNxaEmk0DtYXRuw

运行以下命令获取npm包安装位置

```bash
npm root -g
```

假设，获取到的路径是 `C:\Users\newbe\AppData\Roaming\npm\node_modules`，则将压缩包的内容解压到 `C:\Users\newbe\AppData\Roaming\npm\node_modules\webdriver-manager\selenium` 文件夹。注意，如果 `selenium` 文件夹不存在，可以手动创建。

### 确认 webdriver-manager 安装效果

运行以下命令获取npm包安装位置

```bash
webdriver-manager status
```

若得到类似以下结果，则说明安装成功。

```bash
webdriver-manager: using global installed version 12.1.0
[19:58:24] I/status - selenium standalone version available: 3.141.59
[19:58:24] I/status - chromedriver version available: 2.44
[19:58:24] I/status - geckodriver version available: v0.23.0
[19:58:24] I/status - IEDriverServer is not present
[19:58:24] I/status - android-sdk is not present
[19:58:24] I/status - appium is not present
```

可以通过以下命令启动 webdriver-manager

```bash
webdriver-manager start
```

若得到以下信息，则说明以上安装的内容全部已经成功。

```bash
webdriver-manager: using global installed version 12.1.0
[20:00:19] I/start - java -Dwebdriver.chrome.driver=C:\Users\newbe\AppData\Roaming\npm\node_modules\webdriver-manager\selenium\chromedriver_2.44.exe -Dwebdriver.gecko.driver=C:\Users\newbe\AppData\Roaming\npm\node_modules\webdriver-manager\selenium\geckodriver-v0.23.0.exe -jar C:\Users\newbe\AppData\Roaming\npm\node_modules\webdriver-manager\selenium\selenium-server-standalone-3.141.59.jar -port 4444
[20:00:19] I/start - seleniumProcess.pid: 7936
20:00:19.750 INFO [GridLauncherV3.parse] - Selenium server version: 3.141.59, revision: e82be7d358
20:00:19.829 INFO [GridLauncherV3.lambda$buildLaunchers$3] - Launching a standalone Selenium Server on port 4444
2018-12-04 20:00:19.867:INFO::main: Logging initialized @330ms to org.seleniumhq.jetty9.util.log.StdErrLog
20:00:20.035 INFO [WebDriverServlet.<init>] - Initialising WebDriverServlet
20:00:20.541 INFO [SeleniumServer.boot] - Selenium Server is up and running on port 4444
```

至此，安装 webdriver-manager 的步骤就完毕了。详细的使用方法，在后续的文章中将会介绍。

读者可以直接关闭以上运行的 webdriver-manager 。

## 安装 typescript

打开 控制台（或 Teminal ）, 在控制台中输入以下命令

```bash
npm install typescript -g
```

等待成功安装完毕即可。

## IDE

本项目涉及 `protractor`、`cucumber`和`typescript`。作者更加偏向于使用`WebStorm`作为开发IDE。

可以点击以下链接下载安装 WebStorm :

https://www.jetbrains.com/webstorm/

开发者也可以根据自己的习惯选用相应的IDE并配合相应的插件实现相应的效果。

## 完成

至此关于 `Newbe.Pct` 相关的环境初始化内容都说明完毕了。

<!-- md Nav-Newbe-Pct.md -->
