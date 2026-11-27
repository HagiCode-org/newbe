---
date: 2018-09-22
title: 在C#中使用依赖注入
top: -1
cover: true
slug: /Use-Dependency-Injection
tags:
  - 教程
  - C#
  - 依赖注入
  - Autofac
---

依赖注入（Dependency Injection，缩写为DI）是一种实现（Inversion of Control，缩写为IoC）的方法。在编写C#代码时，使用这种方法能够解决一些场景的需求。本系列将通过若干个实际问题，向读者介绍如何在C#中使用依赖注入。

<!-- more -->

## 阅读说明

### 软件要求

本系列文章将基于以下基本的软件运行环境

| 项目   | 内容                                  |
|------|-------------------------------------|
| 操作系统 | Microsoft Windows 10 专业版 10.0.17134 |
| IDE  | Visual Studio 2017 15.8.3           |

### DI框架选择

C#开发中可选的DI框架众多。本系列文章将使用`Autofac`作为DI框架。

本系列文章也会对 Autofac 的基本用法进行介绍。对于更加深入的内容，读者可以前往 Autofac 官网进行了解。https://autofac.org/

### 项目结构

该系列文章均采用目标框架为`Framework 4.6.1`的`控制台项目`作为演练项目。

### 注意实践

本系列文章采用代码为主的方式进行编写，因此理论介绍较少。希望读者能够在样例代码的区别和实践中体验**使用依赖注入带来的区别
**。

<!-- md Nav-Use-Dependency-Injection.md -->
