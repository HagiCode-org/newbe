---
date: 2023-02-08
title: ChatGPT集成之前，让我们复习一下即将过时的知识
tags: [C#, Docker, Kubernetes]

slag: 0x019-before-chatgpt-integration-let-us-review-the-soon-to-be-obsolete-knowledge
summary: 各大搜索引擎集成 ChatGPT 的步调已经在逐步加紧了。也许这将极大的改变搜索引擎的生态。那么就让我们在时代迎来巨变之前，复习一下即将过时的搜索引擎知识吧。
---

<!-- YamlFrontMatter -->

各大搜索引擎集成 ChatGPT 的步调已经在逐步加紧了。也许这将极大的改变搜索引擎的生态。那么就让我们在时代迎来巨变之前，复习一下即将过时的搜索引擎知识吧。

<!-- more -->

## 搜索引擎一般查询规则

在搜索引擎的时代，我们可以通过搜索引擎来快速的获取到我们想要的信息。但是，如果我们不知道如何高效的使用搜索引擎，那么我们就会浪费大量的时间在搜索引擎上。那么，如何高效的使用搜索引擎呢？下面，我们就来看一下如何使用特殊字符在搜索引擎中进行高效的搜索。

| 序号 | 语法        | 语法说明                                                                   | 示例                           | 示例说明                                   |
| ---- | ----------- | -------------------------------------------------------------------------- | ------------------------------ | ------------------------------------------|
| 1    | +           | 同 AND，搜索包含多个关键词的结果                                           | 搜索 + 引擎                    | 搜索包含【搜索】和【引擎】两个词的页面     |
| 2    | OR          | 或者                                                                       | 搜索 OR 引擎                   | 搜索包含【搜索】或【引擎】两个词的页面     |
| 3    | -           | 减号，不包含减号后面词的页面                                               | 搜索引擎 -百度                 | 搜索不包括【百度】的【搜索引擎】的页面     |
| 4    | ""          | 双引号，精确匹配                                                           | "搜索引擎"                     | 精确匹配【搜索引擎】这个关键词的页面       |
| 5    | \*          | 星号，通配符，模糊搜索，星号代替某个字                                     | 搜\*引擎                       | 星号可以为任何字                           |
| 6    | @           | 在用于搜索社交媒体的字词前加上@                                            | trump @twitter                 | 搜索 trump 的 twitter                      |
| 7    | $           | 在数字前加上$搜索特定价格                                                  | camera $400                    | 搜索 400$的 camera                         |
| 8    | #           | 搜索 # 标签                                                                | #throwbackthursday             | 搜索标签 throwbackthursday                 |
| 9    | ..          | 两个点，在两个数字之间加上.. 在数字范围内执行搜索                          | camera 500.. 500..1000         | 搜索 500−1000 − 1000 的 camera             |
| 10   | filetype    | 搜索某一种文件类型的资源                                                   | C++ filetype:pdf               | 搜索类型为 pdf 的 C++网页资源              |
| 11   | site        | 在指定站点搜索                                                             | C++ site:https://www.zhihu.com | 在知乎中搜索和 C++相关的网页               |
| 12   | cache       | 查看网站的 Google 缓存版本，会直接显示缓存页面                             | cache:weibo.com                | 查看微博的谷歌快照                         |
| 13   | info        | 在网址前加 info:，获取网站详情                                             | info:github.com                | 搜索 github 网站详情                       |
| 14   | related     | 搜索与某个网站有关联的页面                                                 | related:sina.com               | 和新浪网网站结构内容相似的一些其它网站     |
| 15   | link        | 返回所有链接到某个 URL 地址的网页                                          | link:www.csdn.net              | 搜索所有含指向【www.csdn.net】链接的网页   |
| 16   | inurl       | 搜索查询词出现在 url 中的页面                                              | inurl:搜索引擎                 | 搜索链接 url 中有【搜索引擎】的网页        |
| 17   | intitle     | 搜索查询词出现在页面标题(title)中的页面，支持中文和英文                    | intitle:搜索引擎               | 搜索页面标题中有【搜索引擎】的网页         |
| 18   | intext      | 搜索查询词出现在页面正文(title)中的页面，支持中文和英文                    | SEO intext:搜索引擎            | 在正文包含【搜索引擎】的网页中搜索【SEO】  |
| 19   | inanchor    | 搜索链接锚文字(即链接显示的文字)中包含搜索词的页面                         | inanchor:前端                  | 搜索链接锚文字中包含【前端】的页面         |
| 20   | allinurl    | 即 all+inurl 页面 url 中包含多个关键词的页面                               | allinurl:SEO 搜索引擎优化      | 相当于 ：inurl:SEO inurl:搜索引擎优化      |
| 21   | allintitle  | 即 all+intitle 页面标题中包含多个关键词的页面                              | allintitle:SEO 搜索引擎优化    | 相当于：intitle:SEO intitle:搜索引擎优化   |
| 22   | allintext   | 即 all+inanchor 页面正文包含多个关键词的页面                               | allintext:SEO 搜索引擎优化     | 相当于：intext:SEO intext:搜索引擎优化     |
| 23   | allinanchor | 即 all+inanchor 页面链接锚文字包含多个关键词的页面                         | allinanchor:SEO 搜索引擎优化   | 相当于：inanchor:SEO inanchor:搜索引擎优化 |
| 24   | weather     | weather/time/sunrise/sundown+城市名，返回城市的天气/时间/日出时间/日落时间 | weather:beijing                | 显示北京的天气                             |
| 25   | music       | 或者用 songs，歌手名字+music/songs                                         | 周杰伦 music                   | 返回周杰伦的各首歌曲                       |

> 表格引用自 https://evanli.github.io/blog/2019/01/26/advanced-google-search-engine-command/

## 随堂样例

### 搜搜 FastGithub 下载地址

fastgithub 下载 site:newbe.hagicode.com

### 搜索如何进行 C# sqlite 批量插入操作

sqlite bulk insert site:learn.microsoft.com

### C# 11 最新的语法

C# 11 site:learn.microsoft.com

### Rider 2023 最新更新内容

Rider 2023 site:blog.jetbrains.com

## 总结

未来也许结合了 ChatGPT 的搜索引擎将会越来越强大，也许这些知识再也用不到了呢？

## 参考资料

- [谷歌搜索引擎高级搜索、命令大全表格总结(完整示例说明)](https://evanli.github.io/blog/2019/01/26/advanced-google-search-engine-command/)[^1]

[^1]: https://evanli.github.io/blog/2019/01/26/advanced-google-search-engine-command/

<!-- ending -->

<!-- copyright-->
