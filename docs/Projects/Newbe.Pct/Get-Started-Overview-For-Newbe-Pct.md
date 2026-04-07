---
date: 2018-12-05
title: Newbe.Pct 开始使用
tags:
  - Newbe.Pct
  - Web
  - 教程
  - 自动化测试
---

前篇介绍了，使用 Newbe.Pct 之前的准备工作。本篇将开始介绍如何使用本项目运行第一个测试用例。

<!-- more -->

## 阅前语

从本篇开始，读者将会接触到使用一些代码。希望读者不必纠结于语法本身。出现代码的地方都会伴有一定的解释，读者只需要关系代码起到的作用即可。

读者可以在查看过本篇的总体介绍，体验项目本身的所提供的功能，再来决定是否要学习语法。

## 下载模板

Web E2E 自动化测试实际上是通过编写脚本对浏览器进行自动控制实现的。因此编写代码是必不可少的。而在长久的代码实践中，使用代码版本管理软件对代码进行管理是非常必要且正确的实践。

因此，建议开发者在使用本项目前，先学会使用一种代码版本控制软件。

对于使用Git的用户，可以通过Git克隆本项目的代码。可用的地址有：

- https://github.com/newbe36524/Newbe.Pct
- https://gitee.com/yks/Newbe.Pct 国内地址，中国大陆速度更快

如果读者使用的是其他的代码版本管理软件，或者还没有打算使用代码版本管理软件。

可以通过以上链接页面上的下载按钮，实现源码的下载。

源码下载之后，解压到读者自己的工作目录当中即可。

## 测试用例说明

首先，描述一下测试用例：

在谷歌浏览器中，使用 `newbe` 这个关键词在 [必应搜索](https://cn.bing.com) 国内版中进行搜索时，获得的第一条结果就是本站点。

简要分析，该测试用例包含有三个部分：

- 给定条件：搜索引擎为 必应搜索， 搜索关键词为 `newbe`，谷歌浏览器
- 操作步骤：使用 必应搜索 的文本搜索功能
- 预期结果：搜索到的第一条结果能够说明是本站点。

测试用例的这三部分可以使用三个英文单词来表示 `Arrange` 、`Action` 和 `Assert`。

由于没有找到对这种分析方法的正式命名方法，因此我们不妨将此办法称为 `三A描述法`。

## 描述测试用例

本步骤，我们需要采用`Gherkin`关键字对我们的测试用例进行描述。

在项目模板的`features`文件夹下，新建文件`使用必应搜索Newbe相关的内容.feature`

在文件中填写以下内容

```cucumber
Feature: 使用必应搜索Newbe相关的内容

  Background:
    Given 打开必应首页 "https://cn.bing.com/"

  @NewbeDemo
  Scenario: 使用必应搜索 newbe
    When 搜索框输入内容 "newbe"
    When 点击搜索按钮
    Then 出现在必应搜索第一条的标题是 "主页 - Newbe便是新生，唯有不断蜕变才能焕然新生。"
```

文字内容无需过多解释。

这便是对测试用例的`代码性`描述。这种描述方式，没有损失过多可读性，甚至于增加了测试用例的条理性。另外结合以下步骤可以实现代码与这些步骤的绑定，从而
**执行**这个测试用例。

## 建立页面模型

本步骤，我们需要采用`Typescript`语言将测试过程中需要操作的页面元素进行定义。

简要分析，以上测试用例中需要用到三个页面元素：

- 搜索输入框
- 搜索按钮
- 搜索结果的第一条标题

由于搜索首页和搜索结果不在同一个页面。因而，我们定义两个页面。

在项目模板的`pages`文件夹下，新建文件`Bing首页.ts`。

在文件中填写以下内容：

```typescript
import {$, ElementFinder} from "protractor";

export class Bing首页 {
  public input搜索框: ElementFinder;
  public btn搜索按钮: ElementFinder;

  constructor() {
    this.input搜索框 = $("#sb_form_q");
    this.btn搜索按钮 = $("#sb_form_go");
  }
}
```

在项目模板的`pages`文件夹下，新建文件`Bing搜索结果页面.ts`。

在文件中填写以下内容：

```typescript
import {$, ElementFinder, $$} from "protractor";

export class Bing搜索结果页面 {

  public getlbl第一条搜索结果的标题(): ElementFinder {
    return $$("li.b_algo").get(0).$("h2");
  }
}
```

详细的语法细节这里并不做介绍，但即使没有学习过语法，相信读者也可以看出以上两个文件对应着两个主要的页面，其中的一些变量对应了需要操作的页面元素。

## 编写步骤

本步骤，我们需要采用 `Typescript` 语言编写测试步骤。

在项目模板的`stepdefinitions`文件夹下，新建文件`使用必应搜索Newbe相关的内容.ts`。

在文件中填写以下内容：

```typescript
import {Bing首页} from "../pages/Bing首页";
import {Bing搜索结果页面} from "../pages/Bing搜索结果页面";
import {Then, Given, When} from "cucumber";
import {should} from "chai";
import {browser} from "protractor";

should();

const bing首页 = new Bing首页();
const bing搜索结果页面 = new Bing搜索结果页面();

Given(/^打开必应首页 "(.+)"$/, async (url) => {
  await browser.get(url); // 打开URL
  await browser.sleep(1000); // 等待一秒，等待页面加载
});

When(/^搜索框输入内容 "(.+)"$/, async (keyword) => {
  await bing首页.input搜索框.sendKeys(keyword); // 输入关键词
});

When(/^点击搜索按钮$/, async () => {
  await bing首页.btn搜索按钮.click(); // 点击搜索按钮
  await browser.sleep(1000); // 等待一秒，等待页面处理
});

Then(/^出现在必应搜索第一条的标题是 "(.+)"$/, async (titlehtml) => {
  const title = await bing搜索结果页面.getlbl第一条搜索结果的标题().getText(); // 获取搜索结果第一条标题
  title.should.be.eq(title); // 判断第一条的标题和预期一样
});
```

读者可以按照以下几个要点来看上面这段代码：

1. 代码中出现了 `Given` 、 `When` 和 `Then`。读者可以参照上面的 `使用必应搜索Newbe相关的内容.feature` 文件，容易发现，这里的代码和`feature`是一一对应的。
1. 代码中出现了上节定义的 `Bing首页` 和 `Bing搜索结果页面` ，读者可以看到代码通过操作者两个变量，实现了对页面的操作。
1. 代码中通过 `//` 标注了一些注释，读者可以大致了解到每个步骤的作用。
1. 总的来说，这段代码，实现了 `feature` 文件所描述的步骤。

## 运行测试用例

以上，通过三节介绍，将执行测试用例所需要的代码都编写完成了。现在，便可以执行这个测试用例来查看效果。

### 启动 webdriver-manager

打开 控制台（或 Teminal ）, 在控制台中输入以下命令

```bash
webdriver-manager start
```

若控制台最后一句显示以下内容，则说明已经启动成功。

```bash
18:04:05.444 INFO [SeleniumServer.boot] - Selenium Server is up and running on port 4444
```

**启动成功后不要关闭控制台。**

### 执行测试用例

打开 控制台（或 Teminal ）, **注意，需要是新的控制台，与 webdriver-manager 控制台区别**。

将控制台目录切换到项目模板的根目录。

在控制台中输入以下命令

```bash
npm run testnow
```
等待所有操作完毕之后，控制台将输入如下内容：

```bash
PS D:\Repo\Newbe.Pct> npm run testnow

> newbe-pct@4.0.0 testnow D:\Repo\Newbe.Pct
> npm run clean && npm run build && protractor typeScript/config/config.js


> newbe-pct@4.0.0 clean D:\Repo\Newbe.Pct
> rimraf typeScript/


> newbe-pct@4.0.0 build D:\Repo\Newbe.Pct
> tsc

[18:45:52] I/launcher - Running 1 instances of WebDriver
[18:45:52] I/hosted - Using the selenium server at http://127.0.0.1:4444/wd/hub
(node:22948) [DEP0005] DeprecationWarning: Buffer() is deprecated due to security and usability issues. Please use the Buffer.alloc(), Buffer.allocUnsafe(), or Buffer.from() methods instead.
......

1 scenario (1 passed)
4 steps (4 passed)
0m04.255s
Cucumber HTML report D:\Repo\Newbe.Pct\reports\html/cucumber_reporter.html generated successfully.
[18:46:05] I/launcher - 0 instance(s) of WebDriver still running
[18:46:05] I/launcher - chrome #01 passed
```

从上面的报告中的 `1 scenario (1 passed)` 可以看出测试用例已经运行通过。

同时成功生成了 HTML 格式的测试报告。生成的位置为项目文件夹中的`reports\html\cucumber_reporter.html`。读者可以使用 Chrome 浏览器打开查看报告。

## 总结

至此，读者已经成功体验了如何使用本框架，以及本项目所提供的功能。下篇，将针对 feature 文件进行更加细致的说明。

<!-- md Nav-Newbe-Pct.md -->
