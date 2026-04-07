---
date: 2018-05-26
title: 免费构建自己的博客-Jekyll进阶
tags:
 - Jekyll
 - Web
 - 网站开发
 - 教程
---

Jekyll 是采用Ruby语言实现的将纯文本转换为静态博客网站的利器，也是本站点的关键技术。本文将对Jekyll中的进阶内容进行说明。

<!-- more -->

## 基本过程

> Jekyll 是一个简单的博客形态的静态站点生产机器。它有一个模版目录，其中包含原始文本格式的文档，通过一个转换器（如 Markdown）和我们的 Liquid 渲染器转化成一个完整的可发布的静态网站，你可以发布在任何你喜爱的服务器上。Jekyll 也可以运行在 GitHub Page 上，也就是说，你可以使用 GitHub 的服务来搭建你的项目页面、博客或者网站，而且是完全免费的。（引用自 http://jekyllcn.com/docs/home/）

由于本教程通过 Docker 技术直接在容器中运行 Jekyll 环境，因此读者不需要过多的研究 Jekyll 的运行环境要求。

Jekyll 的入门材料非常多，其中针对官网进行汉化翻译的 http://jekyllcn.com/docs/home/ 写的非常全面，因此本文就不全面介绍。以下只对主要的部分进行说明。

## 插件

Jekyll 插件可以扩展 Jekyll 原生没有的功能。

例如：自动生成RSS、生成TOC、生成SEO标记、压缩HTML等等功能，都可以通过插件来实现。

查看本站点`_config.yml`文件，便可以查看到本站所使用的插件。

### 引入插件

插件以 Ruby 代码或模块的方式存在，使用时通常引入相应的代码或模块即可。

值得注意的是，如果需要托管在 Github 或者其他提供 Pages 服务的站点，服务商不一定提供运行插件的环境。

因此，建议在本地运行插件，然后将生成结果发布到服务器上，这样就不需要依赖服务器的运行环境。

详细的引入方法，可以点击右侧链接进行了解：http://jekyllcn.com/docs/plugins/

### 寻找插件

可以通过 http://jekyllcn.com/docs/plugins/ 查看到一些主流的插件。

若需要寻找更多的插件，可以通过搜索引擎或 Github 进行搜索。

## 模板

模板是指将一个网页分割为多个部分，存放在不同的文件中，以实现尽可能复用代码的目的。

若要使用 Jekyll 布局，就必须了解 HTML 基本标签的用户，读者可以通过右侧链接进行学习：http://www.w3school.com.cn/html/index.asp 。

了解 HTML 基础之后，学习 Jekyll 则比较简单，详细可以通过右侧了解进行学习：http://jekyllcn.com/docs/templates/ 。

## 代码高亮

本站点模板默认开启了代码高亮，编写博客时只需要使用 markdown 的代码块方法编写即可。

本站点采用的代码高亮方案是通过 rouge 插件实现的，并直接生成的 Sublime Text 类似的展示效果。

若使用 rouge 生成其他风格代码高亮样式，可以通过右侧链接进行学习：http://gohom.win/2016/02/04/update-github-rouge/ 。

此部分操作较为困难，若读者对此部分要求不高，可以直接跳过。

## 主题

Jekyll 的主题功能也是通过 Ruby 实现的。

用户在编写自己的博文内容时，使用的是 markdown 进行编写，这样作者就可以专注于内容的编写，而效果上的调整，则可以直接借助于主题功能，进行切换，详细的内容，可以通过右侧链接进行了解：http://jekyllcn.com/docs/themes/ 。

本站点没有采用 Jekyll 的主题方案，而是采用 (amazeui)[http://amazeui.org/] 进行实现，实现了作者做移动端适配的需求。

更多的主题，通过 Github 所搜 Jekyll Theme 相关的关检测也可以找到。

<!-- md Nav-Build-Your-Own-Blog.md -->
