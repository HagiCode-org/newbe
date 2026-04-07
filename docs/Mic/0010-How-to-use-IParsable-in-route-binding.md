---
date: 2022-12-17
title: 如何在路由绑定中使用 IParsable
tags:
  - aspnetcore
  - dotnet
  - dotnet7
  - chatOpenAI
---

IParsable 是 .Net 7 中新增的接口，它可以将字符串转换为对应的实体。在 Controller 的 Route 绑定中可以使用 IParsable 来绑定复杂的实体。

<!-- more -->

## 实验背景

假设有一个需要将 route `report/{month}-{day}` 绑定到 MyDate 对象上的场景。

在 .Net 7 之前，通常是使用两个参数来接收绑定的 month 和 day，然后在代码中实例化 MyDate 对象。例如：

```csharp
[Route("report/{month}-{day}")]
public ActionResult GetReport(int month, int day)
{
    var myDate = new MyDate { Month = month, Day = day };
    // 使用 myDate
}
```

## 使用 IParsable

在 .Net 7 中，可以直接让 MyDate 实现 IParsable 接口，然后在 route 中绑定 `report/{myDate}`。这样 MyDate 就能直接从 route 上绑定，省去了手动实例化的步骤。

下面是一个示例代码：

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

[HttpGet("report/{myDate}")]
public ActionResult GetReport(MyDate myDate)
{
    // myDate 已经被正确地绑定
}

```

## 参考资料

- [IParsable](https://learn.microsoft.com/en-us/dotnet/api/system.iparsable-1?view=net-7.0&WT.mc_id=DT-MVP-5004283)
- [5 new MVC features in .NET 7](https://andrewlock.net/5-new-mvc-features-in-dotnet-7/)

<!-- md Chat-AI-Footer.md -->
