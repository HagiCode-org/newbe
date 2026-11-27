---
date: 2023-02-15
title: 我不想再传递 nameof 了
tags: [C#, Docker, Kubernetes]
 
slag: 0x01D-I-don-t-want-to-pass-nameof-anymore
summary: 有的时候抛出一个异常，我们需要知道是哪个方法抛出的异常。那么，我们可以通过传递 nameof 来获取调用者的方法名。但是，感觉很烦，每次都要传递 nameof。那么，有没有更好的方法呢？
---

<!-- YamlFrontMatter -->

有的时候抛出一个异常，我们需要知道是哪个方法抛出的异常。那么，我们可以通过传递 nameof 来获取调用者的方法名。但是，感觉很烦，每次都要传递 nameof。那么，有没有更好的方法呢？

<!-- more -->

## CallerLineNumberAttribute

获取调用者的行号。

```csharp
using System;
using System.Runtime.CompilerServices;

public static class Program
{
   public static void Main()
   {
      TraceMessage("Something happened.");
   }

   public static void TraceMessage(string message,
                        [CallerLineNumber] int sourceLineNumber = 0)
   {
      Console.WriteLine("Line: {0} - {1}", sourceLineNumber, message);
   }
}
// The example displays the following output:
//    Line: 10 - Something happened.
```

## CallerFilePathAttribute

获取调用者的文件路径。

```csharp
using System;
using System.IO;
using System.Runtime.CompilerServices;

public static class Program
{
   public static void Main()
   {
      TraceMessage("Something happened.");
   }

   public static void TraceMessage(string message,
                        [CallerFilePath] string sourceFilePath = "")
   {
      Console.WriteLine("File: {0} - {1}", Path.GetFileName(sourceFilePath), message);
   }
}
// The example displays the following output:
//    File: Program.cs - Something happened.
```

<!-- ad -->

## CallerMemberNameAttribute

获取调用者的方法名。

```csharp
using System;
using System.Runtime.CompilerServices;

public static class Program
{
   public static void Main()
   {
      DoProcessing();
   }

   public static void DoProcessing()
   {
      TraceMessage("Something happened.");
   }

   public static void TraceMessage(string message,
                        [CallerMemberName] string memberName = "")
   {
      Console.WriteLine("Member: {0} - {1}", memberName, message);
   }
}
// The example displays the following output:
//    Member: DoProcessing - Something happened.
```

## CallerArgumentExpressionAttribute

获取调用者的参数表达式。C# 10.0 新增。

这个其实很好用，以后再也不用担心 ArgumentException 还需要写一个 nameof 了。

```csharp
using System;
using System.Runtime.CompilerServices;

public static class Program
{
   public static void Main()
   {
      int x = 10;
      int y = 20;
      Assert(x > y, "x > y");
   }

   public static void Assert(bool condition, [CallerArgumentExpression("condition")] string message = null)
   {
      Console.WriteLine("Condition: {0} - {1}", condition, message);
   }
}
// The example displays the following output:
//    Condition: False - x > y
```

## 总结

通过上面的几个例子，我们可以看到，借助在编译时获取调用者的行号、文件路劲和调用者方法名的特性，我们可以在开发中更加方便的进行日志记录。

## 参考

- [CallerLineNumberAttribute Class](https://learn.microsoft.com/dotnet/api/system.runtime.compilerservices.callerlinenumberattribute?view=net-7.0&WT.mc_id=DT-MVP-5004283)[^1]
- [CallerFilePathAttribute Class](https://learn.microsoft.com/dotnet/api/system.runtime.compilerservices.callerfilepathattribute?view=net-7.0&WT.mc_id=DT-MVP-5004283)[^2]
- [CallerMemberNameAttribute Class](https://learn.microsoft.com/dotnet/api/system.runtime.compilerservices.callermembernameattribute?view=net-7.0&WT.mc_id=DT-MVP-5004283)[^3]
- [CallerArgumentExpressionAttribute Class](https://learn.microsoft.com/dotnet/api/system.runtime.compilerservices.callerargumentexpressionattribute?view=net-7.0&WT.mc_id=DT-MVP-5004283)[^4]

[^1]: https://learn.microsoft.com/dotnet/api/system.runtime.compilerservices.callerlinenumberattribute?view=net-7.0&WT.mc_id=DT-MVP-5004283
[^2]: https://learn.microsoft.com/dotnet/api/system.runtime.compilerservices.callerfilepathattribute?view=net-7.0&WT.mc_id=DT-MVP-5004283
[^3]: https://learn.microsoft.com/dotnet/api/system.runtime.compilerservices.callermembernameattribute?view=net-7.0&WT.mc_id=DT-MVP-5004283
[^4]: https://learn.microsoft.com/dotnet/api/system.runtime.compilerservices.callerargumentexpressionattribute?view=net-7.0&WT.mc_id=DT-MVP-5004283

<!-- ending -->

<!-- ad -->

<!-- copyright-->