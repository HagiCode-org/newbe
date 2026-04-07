---
date: 2023-02-20
title: 不同程序集，名称空间类名和方法签名都一样的方法，如何调用
tags: [C#, Docker, Kubernetes]

slag: 0x022-how-to-call-a-method-with-the-same-method-signature-in-different-assemblies
summary: 有时候，你可能会遇到这样的问题，不同程序集，名称空间类名和方法签名都一样的方法，如何调用。本文将介绍如何通过别名的方式来解决这个问题。
---

<!-- YamlFrontMatter -->

有时候，你可能会遇到这样的问题，不同程序集，名称空间类名和方法签名都一样的方法，如何调用。本文将介绍如何通过别名的方式来解决这个问题。

<!-- more -->

## 创建两个不同的程序集

我们来创建两个不同的程序集，但是他们的名称空间一样：

```bash
dotnet new classlib -o ClassLibrary1 -n ClassLibrary1
dotnet new classlib -o ClassLibrary2 -n ClassLibrary2
```

修改他们的 RootNamespace 为 Example：

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net7.0</TargetFramework>
    <RootNamespace>Example</RootNamespace>
  </PropertyGroup>

</Project>
```

然后，我们在两个程序集中都创建一个类，类名也一样，并且添加一个自定义 Where 扩展方法：

```csharp
namespace Example
{
    public static class LinqExtensions
    {
        public static void Where(IEnumerable<int> source)
        {
            // 在这里添加代码
            Console.WriteLine("ClassLibrary1.Class1.Where");
        }
    }
}
```

## 创建一个控制台应用

然后，我们创建一个控制台应用，来调用这两个程序集中的 Where 方法：

```bash
dotnet new console -o ConsoleAppShi -n ConsoleAppShi
dotnet add ConsoleAppShi reference ClassLibrary1
dotnet add ConsoleAppShi reference ClassLibrary2
```

然后，我们在控制台应用中调用这两个程序集中的 Where 方法：

```csharp
using Example;
var list = new int[]{1,2,3};
LinqExtensions.Where(list);
```

如果是这样的话，我们会得到这个错误：

```bash
Ambiguous reference: Example.LinqExtensions Example.LinqExtensions match
```

## 通过别名的方式来解决

我们可以通过别名的方式来解决这个问题，首先修改项目文件，设置两个程序集的别名：

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <ItemGroup>
    <ProjectReference Include="..\ClassLibrary1\ClassLibrary1.csproj">
      <Aliases>ClassLibrary1</Aliases>
    </ProjectReference>
    <ProjectReference Include="..\ClassLibrary2\ClassLibrary2.csproj">
      <Aliases>ClassLibrary2</Aliases>
    </ProjectReference>
  </ItemGroup>
</Project>
```

然后，我们在控制台应用中调用这两个程序集中的 Where 方法：

```csharp
extern alias ClassLibrary1;
extern alias ClassLibrary2;

var list = new[] { 1, 2, 3 };

ClassLibrary1::Example.LinqExtensions.Where(list);
ClassLibrary2::Example.LinqExtensions.Where(list);
```

运行就会得到这样的结果：

```bash
ClassLibrary1.Class1.Where
ClassLibrary2.Class1.Where
```

## 为什么会有这种问题

一般来说你会在三种情况下遇到这个问题：

1. 某个开源项目使用 ILmerge 把多个程序集合并成一个程序集。其中一个依赖项 A 恰好也是你的依赖项，但是 A 的版本和开源项目的依赖项 A 的版本不一样，这时候你就会遇到这个问题。
2. 很早之前 Rx.net 正对 System.Linq.Async 进行了支持，而后来系统也内置了 System.Linq.Async。你会在使用 Rx.net 的时候遇到这个问题。
3. 你的同事想考验你一下，估计把自己写的 Sqlite 扩展和 MSSQL 扩展中加入了同样的方法签名，然后你就会遇到这个问题。

## 总结

通过别名的方式，我们可以解决不同程序集，名称空间类名和方法签名都一样的方法，如何调用的问题。

## 参考

- [extern alias (C# Reference)](https://learn.microsoft.com/dotnet/csharp/language-reference/keywords/extern-alias?WT.mc_id=DT-MVP-5004283)[^1]

[^1]: https://learn.microsoft.com/dotnet/csharp/language-reference/keywords/extern-alias?WT.mc_id=DT-MVP-5004283

<!-- ending -->

<!-- ad -->

<!-- copyright-->
