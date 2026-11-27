---
date: 2023-01-01
title: 如何指定多个项目的 InternalsVisibleTo
tags:
  - aspnetcore
  - chatOpenAI
---

InternalsVisibleTo 属性允许你指定一个或多个程序集，这些程序集可以访问当前程序集中的内部类型。经常在进行单元测试时使用，例如，你可以在一个项目中定义一个内部类型，然后在另一个项目中进行单元测试。本文将介绍如何指定多个项目的 InternalsVisibleTo，从而不需要在每个项目中都指定一遍。

<!-- more -->

## 代码演示

假如我们有一个项目，名称为 TestProject1。则我们需要在 TestProject1 中指定 InternalsVisibleTo 属性，如下所示：

```csharp
[assembly: InternalsVisibleTo("TestProject1.Tests")]
```

但其实，我们也可以在 TestProject1.csproj 中指定 InternalsVisibleTo 属性，如下所示：

```xml
<Project>
    <ItemGroup>
        <AssemblyAttribute Include="System.Runtime.CompilerServices.InternalsVisibleToAttribute">
            <_Parameter1>TestProject1.Tests</_Parameter1> <!-- We use the value of AssemblyName to declare the value of the attribute -->
        </AssemblyAttribute>
    </ItemGroup>
</Project>
```

既然如此，我们便可以使用 Directory.Build.props 文件来指定多个项目的 InternalsVisibleTo 属性，如下所示：

```xml
<Project>
    <ItemGroup>
        <AssemblyAttribute Include="System.Runtime.CompilerServices.InternalsVisibleToAttribute">
            <_Parameter1>$(AssemblyName).Tests</_Parameter1> <!-- We use the value of AssemblyName to declare the value of the attribute -->
        </AssemblyAttribute>
    </ItemGroup>
</Project>
```

这样，所有的项目都会自动指定 InternalsVisibleTo 属性，而不需要在每个项目中都指定一遍。

## 总结

本文介绍了如何指定多个项目的 InternalsVisibleTo 属性，从而不需要在每个项目中都指定一遍。

## 参考资料

- [directory.build.props](https://learn.microsoft.com/visualstudio/msbuild/customize-your-build?view=vs-2019&WT.mc_id=DT-MVP-5004283#directorybuildprops-and-directorybuildtargets)
- [Adding AssemblyMetadataAttribute using new SDK project, with MSBuild](https://stu.dev/adding-assemblymetadataattribute-using-new-sdk-project-with-msbuild/)

<!-- md Chat-AI-Footer.md -->
