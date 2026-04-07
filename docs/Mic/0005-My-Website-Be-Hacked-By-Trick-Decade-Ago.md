---
date: 2019-07-11
title: 我的网站被十年前的套路给黑了
tags:
 - Newbe.Pct
 - Web
 - 网站开发
---

某天，网站被黑。出现了不和谐的内容。查了一下，其实这个套路十年前就有了。

<!-- more -->

## 基础环境

Windows Server 2012R2，不知道什么时候装的，从未打过补丁。

IIS 除了 FTP 和 IIS6 兼容，其他全勾。

Asp.net MVC 5 。

Framework 4.5。

没有安装任何防黑防毒软件。

## 被黑表现

如果用户从百度搜索到网站，并点击链接跳转到网站内的一个原本不存在的页面（也就是原本应该404的页面）。那么浏览器就会被重定向到一个不和谐网站。

因此得知触发这个问题必须，HTTP请求必须具备两个条件：

1. 这个页面对应地址原本是 404 页面
2. 求请求中表明了上一页来自搜索引擎，即 Referrer 来自搜索引擎

## 作案手法

1. 篡改 Global.asax 内容，加入 runat="server" 代码。
2. 使用 Easy File Locker 隐藏 Global.asax 文件，使得管理员无法修改或覆盖该文件。

## 应对方法

1. 安装 Easy File Locker ，解除 Global.asax 文件的隐藏和写保护。

    需要接触 Easy File Locker 的密码限制，[参考链接](https://www.ahaoyw.com/article/245.html)。

2. 删除 Global.asax 中的恶意代码。

3. 完毕。

## 后续

1. 压根不知道黑客如何入侵，删服务器！
2. 新服务器装点防黑防毒软件吧。

## 参考链接

- https://www.zhihu.com/question/308025422
- http://www.dtcms.net/news/show-99.html
- http://www.bluece.com/newsread.asp?u=102w316w4073t0
