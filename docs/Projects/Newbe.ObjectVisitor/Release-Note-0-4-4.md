---
date: 2020-12-08
title: Newbe.ObjectVisitor 0.4.4 发布，模型验证器上线
tags:
  - Newbe.ObjectVisitor
  - 更新说明
---

Newbe.Claptrap 0.4.4 发布，模型验证器上线。

<!-- more -->

## 更新内容

### 完全基于表达式树的模型验证器

本版本，我们带来了基于表达式树实现的模型验证器。并实现了很多内置的验证方法。

我们罗列了与 FluentValidation 比较的情况：

| Build in Validators   | FluentValidation 9.X | Newbe.ObjectVistor                  |
|-----------------------|----------------------|-------------------------------------|
| NotNull               | ✔️                   | ✔️ NotNull; class                   |
| NotEmpty              | ✔️                   | ✔️ NotEmpty; string,enumerable      |
| NotEqual              | ✔️                   | ✔️ NotEqual; all                    |
| Equal                 | ✔️                   | ✔️ Equal; all                       |
| Length                | ✔️                   | ✔️ Length; string,enumerable        |
| MaxLength             | ✔️                   | ✔️ MaxLength; string,enumerable     |
| MinLength             | ✔️                   | ✔️ MinLength; string,enumerable     |
| Less Than             | ✔️                   | ✔️ LessThan; number                 |
| Less Than Or Equal    | ✔️                   | ✔️ LessThanOrEqual; number          |
| Greater Than          | ✔️                   | ✔️ GreaterThan; number              |
| Greater Than Or Equal | ✔️                   | ✔️ GreaterThanOrEqual; number       |
| Predicate             | ✔️                   | ✔️ Validate; all                    |
| Regular Expression    | ✔️                   | ✔️ MatchRegex,NotMatchRegex; string |
| Email                 | ✔️                   | 💭 MatchRegex; string               |
| Credit Card           | ✔️                   | 💭 MatchRegex; string               |
| Enum                  | ✔️                   | ✔️ IsInEnum; number,string,enum     |
| Enum Name             | ✔️                   | ✔️ IsEnumName; string               |
| Empty                 | ✔️                   | ✔️ Empty; string,enumerable         |
| Null                  | ✔️                   | ✔️ Null; class                      |
| ExclusiveBetween      | ✔️                   | ✔️ IsInRange; number,enum           |
| InclusiveBetween      | ✔️                   | ✔️ IsInRange; number,enum           |
| ScalePrecision        | ✔️                   | ✔️ ScalePrecision; number           |
| Or                    | ❌                    | ✔️ Or; all                          |
| IsInSet               | ❌                    | ✔️ IsInSet; all                     |
| IsNotInSet            | ❌                    | ✔️ IsNotInSet; all                  |
| CanParse              | ❌                    | 🚧 CanParse; all                    |

### FluentAPI 生成器重构的代码

我们基于 0.3 已经发布的 FluentAPI 进行了核心代码重构，现在一些特定场景下需要您指定的泛型参数更少了，但是功能没有减少，更有利您进行开发。

类似的，例如下面这个变更：

```cs
  // create a data visitor to cover sensitive data
  _visitor = default(UserModel).V()
-     .ForEach<UserModel, string>(x => CoverSensitiveData(x))
+     .ForEach<string>(x => CoverSensitiveData(x))
      .Cache();
```

### 同时支持英文与简体中文方法注释

在热心网友 [EventHorizon1024](https://github.com/EventHorizon1024) 的帮助下，我们在保留英文作为原始注释的情况下，对使用简体中文 IDE 的开发者们提供了全简中的方法说明。

开发者无需特殊操作，便可以在 IDE 中直接查看到简体中文的方法注释。

如何实现的详细操作方法，开发者也可以通过以下链接借鉴使用：

https://github.com/dotnet/roslyn/issues/3371#issuecomment-737623706

### 开发文章站点正式上线

我们非常顺利的上线了开发文档站点：

- http://ov.newbe.pro
- http://cn.ov.newbe.pro 中国大陆访问更快
- https://github.com/newbe36524/Newbe.ObjectVisitor.Docs

后续所有关于本工具包相关的文章除了在博客 https://newbe.hagicode.com 及相关博客公布之外，我们将会更新以上站点，丰富其中的文档。

目前，我们已经上线了几篇简单的文档：

- [我的第一个 Object Visitor](http://cn.ov.newbe.pro/zh/001-quick-started/001-my-fisrt-object-visitor)
- [创建并缓存 Object Visitor](http://cn.ov.newbe.pro/zh/001-quick-started/002-create-and-cache-your-object-visitor)

<!-- md Footer-Newbe-ObjectVisitor.md -->
