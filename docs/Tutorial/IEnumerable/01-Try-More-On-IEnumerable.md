---
date: 2019-09-01
title: 试试IEnumerable的10个小例子
tags:
  - 教程
  - C#
  - IEnumerable
---

IEnumerable 接口是 C# 开发过程中非常重要的接口，对于其特性和用法的了解是十分必要的。本文将通过10个小例子，来熟悉一下其简单的用法。

<!-- more -->

## 全是源码

以下便是这10个小例子，响应的说明均标记在注释中。

### T01普通的循环获取偶数

`{% dotnetfiddle elXUjA https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T01普通的循环获取偶数.cs 1200 %}`

### T02普通Enumerable

`{% dotnetfiddle Qp10IH https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T02普通Enumerable.cs 1200 %}`

### T02本地函数

`{% dotnetfiddle MQ1TSg https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T02本地函数.cs 1200 %}`

### T03分离条件

`{% dotnetfiddle c7NMNI https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T03分离条件.cs 1200 %}`

### T04Linq产生数值

`{% dotnetfiddle bMtGG3 https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T04Linq产生数值.cs 1200 %}`

### T05输出233

`{% dotnetfiddle fuPPbW https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T05输出233.cs 1200 %}`

### T06获取10个小于50的随机数

`{% dotnetfiddle iqFoq3 https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T06获取10个小于50的随机数.cs 1200 %}`

### T07自动补足随机数

`{% dotnetfiddle HG0kd6 https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T07自动补足随机数.cs 1200 %}`

### T08条件转循环

`{% dotnetfiddle ftbRfN https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T08条件转循环.cs 1200 %}`

### T09获取一个链接字符串

`{% dotnetfiddle vShbOW https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T09获取一个链接字符串.cs 1200 %}`

### T10测试网络连接

`{% dotnetfiddle IBHOxI https://github.com/newbe36524/Newbe.Demo/blob/master/src/BlogDemos/Try-More-On-IEnumerable/Try-More-On-IEnumerable/T10测试网络连接.cs 1200 %}`

## 源码说明

以上示例的源代码放置于[博客示例代码库](https://github.com/newbe36524/Newbe.Demo/tree/master/src/BlogDemos/Try-More-On-IEnumerable)中。

项目采用 netcore 2.2 作为目标框架，因此需要安装 netcore 2.2 SDK 才能运行。
