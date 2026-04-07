---
date: 2022-12-17
title: 如何在 .Net 7 中将 Query 绑定到数组
tags:
  - aspnetcore
  - dotnet
  - dotnet7
  - chatOpenAI
---

在 .Net 7 中，我们可以通过绑定数组的方式来接收来自查询字符串的参数。这样就不需要再使用逗号分隔的字符串来获取参数了。

<!-- more -->

## 代码演示

假设我们需要从 query 上接受多个 id 并返回查询的结果。例如： id=1&id=2

在 .Net 7 中，我们可以这样实现：

```csharp
public ActionResult GetResults([FromQuery]int[] ids)
{
    // 使用 ids 数组查询结果
}
```

这样就可以直接将 id=1&id=2 这样的查询字符串绑定到 ids 数组上。

## 借助 IParsable 绑定更复杂的类型

如果我们需要绑定的类型比较复杂，例如：

```csharp
public ActionResult GetResults([FromQuery]MyDate[] dates)
{
    // 使用 dates 数组查询结果
}
```

我们可以通过实现 `IParsable<T>` 接口来实现自定义的绑定。

```csharp
public class MyDate : IParsable<MyDate>
{
    public int Month { get; set; }
    public int Day { get; set; }

    public void Parse(string input)
    {
        var parts = input.Split('-');
        Month = int.Parse(parts[0]);
        Day = int.Parse(parts[1]);
    }

    public static MyDate Parse(string s, IFormatProvider? provider)
    {
        var date = new MyDate();
        date.Parse(s);
        return date;
    }

    public static bool TryParse(string? s, IFormatProvider? provider, out MyDate result)
    {
        try
        {
            result = Parse(s, provider);
            return true;
        }
        catch
        {
            result = default;
            return false;
        }
    }
}
```

这样就可以通过 `dates=1-1&dates=2-2` 这样的查询字符串来绑定到 `MyDate[]` 数组上了。

## 参考资料

- [Bind arrays and string values from headers and query strings](https://learn.microsoft.com/aspnet/core/fundamentals/minimal-apis?preserve-view=true&view=aspnetcore-7.0&WT.mc_id=DT-MVP-5004283#bind-arrays-and-string-values-from-headers-and-query-strings)

<!-- md Chat-AI-Footer.md -->
