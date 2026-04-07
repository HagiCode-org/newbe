---
date: 2020-11-08
title: Newbe.ObjectVisitor 0.2.10 发布，更花里胡哨
tags:
  - Newbe.ObjectVisitor
  - 更新说明
---

Newbe.Claptrap 0.2.10 发布，更花里胡哨。

<!-- more -->

## 更新内容

现在，你可以通过上下文修改属性的值了：

```cs
//✔️ from 0.2
// 可以修改属性
o.V().ForEach((context) => ModifyData(context)).Run();

public static void ModifyData(IObjectVisitorContext<Yueluo,string> context)
{
    context.Value = context.Value.SubString(0,1)；
}
```

现在，支持多次 ForEach 操作：

```cs
// ✔️ from 0.2
// 多重 foreach
o.V().ForEach((context)=>{}).ForEach((context)=>{}).Run();
```

现在，支持更多花里胡哨的属性条件判断：

```cs
//✔️ from 0.2
// 遍历指定类型的属性
o.V().ForEach<Yueluo, string>((context) => {});
// 和上一条完全一样
o.V().ForEach<Yueluo, string>((context) => {}, x => x.PropertyType == typeof(string));
// 遍历被标记了 RequiredAttribute 的 string 属性
o.V().ForEach<Yueluo, string>((context) => {}, x => x.PropertyType == typeof(string) && x.GetCustomAttribute<RequiredAttribute>());
// 遍历“是”或者实现了 IEnumerable<int> 接口的属性, 例如 List<int>, int[], IEnumerable<int>, HashSet<int> 等等。
o.V().ForEach<Yueluo, IEnumerable<int>>((context) => {}, x => x.IsOrImplOf<IEnumerable<int>>());
// 指定属性类型，并包含一个扩展的参数
o.V().WithExtendObject<Yueluo, StringBuilder>().ForEach<Yueluo, StringBuilder, string>((context) => {});
```

## 基准测试

我们更新了两个基准测试：

1. FormatString 实现进行了优化，现在 Quick Style 和自己手写 ObjectVisitor 已经几乎没有区别。
2. 使用 ObjectVisitor 来修改属性值的代价约为 1-5 微秒(千分之一毫秒)。

详细的数据可以查看项目首页，此处仅给出图表说明。

![FormatString](/images/20201101-002.png)

![MOdifyData](/images/20201101-001.png)

## 文章

新增了一些相关的经验文章：

- [Newbe.ObjectVisitor/Better-Performance-Getter-Setter](./Better-Performance-Getter-Setter)
- [Newbe.ObjectVisitor/Better-Performance-Small-Map](./Better-Performance-Small-Map)

## 场景样例

我们增加了一些可以使用该库实现功能的场景和做法说明：

- 将数据库链接字符串转型为数据模型，或者将数据模型格式化为链接字符串。
- 将对象中满足手机号码格式的字段替换为密文，避免敏感信息输出。
- 将实现了 `IEnumerable<int>` 的所有属性求和。

可以参阅《[Newbe.ObjectVisitor/Example-1](./Example-1)》

<!-- md Footer-Newbe-ObjectVisitor.md -->
