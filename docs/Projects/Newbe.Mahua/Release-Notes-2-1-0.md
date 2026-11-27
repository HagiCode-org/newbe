---
date: 2019-03-02
title: Newbe.Mahua 2.1 支持Websocket
tags:
    - Newbe.Mahua
    - QQ机器人
    - 更新说明

top: -999
---

Websocket 本框架支持的第一个双工通信方案。

<!-- more -->

## 版本亮点

### 支持 Websocket

HTTP 通信方案是本框架支持的第一个通信方案。而其需要客户端程序也运行一个 Web 服务才能够进行双向调用。

此次推出 Websocket 通信方案，客户端程序可以不必托管 Web 服务，也能够与框架进行双向调用。

读者可以通过运行在浏览器上的 javascript 与框架进行通信，此处提供了一个简单的 Demo 实现该功能。[点击此处跳转获取 Demo](https://github.com/newbe36524/Newbe.Mahua.Plugins.Parrot)

## 升级方法与要点

使用命令行在机器人 exe 根目录运行以下命令

```bash
mahua InstallMahua
```

注意：升级过程将会覆盖以下配置文件，若开发者有自行定制过这些配置项，需要先自行备份：

-   mahua.json
-   NLog.config

<!-- md Nav-Newbe-Mahua-2.X.md -->
