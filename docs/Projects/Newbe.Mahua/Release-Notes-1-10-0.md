---
date: 2018-06-24
title: Newbe.Mahua 1.10 全新日志查看器
tags:
  - Newbe.Mahua
  - QQ机器人
  - 更新说明

top: -999
---

从此版本开始，全新的 Amanda 授权机制，全新的日志展示方案，全新的样例代码。

<!-- more -->

## 版本亮点

### 全新的 Amanda 授权机制

Amanda 平台 SDK 已经升级到版本 3，该版本采用了全新的授权码机制，实现了插件与主体框架的安全通信。

本 SDK 也全新升级，为开发者带来完整的 Amanda 平台开发体验。

### 全新日志展示方案

以往，开发者只能通过日志文件查看日志，不易查阅问题。

现在，开发者可以使用 Log4View 与本开发框架对接，实现日志在 Log4View 上的实时查看。

开发者可以进入 http://www.log4view.com/log4view/ 下载最新的 Log4View 并安装。

添加 Network Receiver 并按照如下图设置：

![Network Receiver基础配置](/images/20180624-001.png)

![Network Receiver编码设置](/images/20180624-002.png)

如此，便可以实时查看日志，效果如下：

![Log4View效果](/images/20180624-003.png)

### 全新样例代码

OkexRobot，与 OKEX 进行 API 对接，实现订单成交监控、资产变更跟踪、订单查询、资产查询功能。开发者可以按照此样例进行开发。

- 每 1 分钟定时获取当前资产状态，并记录在 App_Data/userAssets.db 中
- 每天 5/11/17/23 时，会定时汇报资产变更情况，并计算过去 6 小时增长量
- 每隔 5 分钟检测订单成交情况，汇报成交和撤销的订单。

详细实现代码，[点击此处链接进行查看](https://github.com/Newbe36524/Newbe.Mahua.Framework/tree/master/src/Newbe.Mahua.Samples.OkexRobot)

## 升级注意

从 1.9 版本直接更新全部的 Newbe.Mahua.\* nuget 包，重新生成便可以。

升级过程中出现需要覆盖文件的提示，请选择同意。

VS 插件更新只需要按照 VS 提示进行操作即可。

<!-- md Nav-Newbe-Mahua-1.X.md -->
