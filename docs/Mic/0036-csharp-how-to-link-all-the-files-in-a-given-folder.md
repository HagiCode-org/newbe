---
date: 2023-02-06
title: 如何在 C# 项目中链接一个文件夹下的所有文件
tags: [C#, Docker, Kubernetes]

slag: 0x017-csharp-how-to-link-all-the-files-in-a-given-folder
summary: 在 C# 项目中通过链接方式引入文件可以让我们在项目中使用这些文件中的代码。常见的比如链接 AssemblyInfo.cs 文件，这样我们就可以在项目中使用这个文件中的版本号等信息。但是如果我们想要链接一个文件夹下的所有文件，该怎么做呢？今天我们就来看看如何在 C# 项目中链接一个文件夹下的所有文件。
---

在 C# 项目中通过链接方式引入文件可以让我们在项目中使用这些文件中的代码。常见的比如链接 AssemblyInfo.cs 文件，这样我们就可以在项目中使用这个文件中的版本号等信息。但是如果我们想要链接一个文件夹下的所有文件，该怎么做呢？今天我们就来看看如何在 C# 项目中链接一个文件夹下的所有文件。

<!-- more -->

## 编辑项目文件引入单个文件

在项目文件中，我们可以通过 `Compile` 标签来引入单个文件。比如我们想要引入 `AssemblyInfo.cs` 文件，我们可以这样做：

```xml
<Project>
    <ItemGroup>
        <Compile Include="../Shared/AssemblyInfo.cs">
            <Link>Properties/AssemblyInfo.cs</Link>
        </Compile>
    </ItemGroup>
</Project>
```

这样我们就可以在项目中使用 `AssemblyInfo.cs` 文件中的代码了。

## 编辑项目文件引入文件夹下的所有文件

那如果想要引入多个文件，我们可以使用通配符来引入文件夹下的所有文件。比如我们想要引入 `Shared` 文件夹下的所有文件，我们可以这样做：

```xml
<Project>
    <ItemGroup>
        <Compile Include="..\Shared\**\*.cs">
            <Link>Properties/%(Filename)%(Extension)</Link>
        </Compile>
    </ItemGroup>
</Project>
```

这样我们就可以在项目中使用 `Shared` 文件夹下的所有文件中的代码了。

不过这样会使得所有的文件在项目中都会显示在 `Properties` 文件夹下，这样会让项目文件看起来很乱。我们可以通过修改 `Link` 标签来修改文件在项目中的显示位置。比如我们想要把 `Shared` 文件夹下的所有文件都显示在项目的根目录下，我们可以这样做：

```xml
<Project>
    <ItemGroup>
        <Compile Include="..\Shared\**\*.cs">
            <Link>%(RecursiveDir)%(Filename)%(Extension)</Link>
        </Compile>
    </ItemGroup>
</Project>
```

## 别忘了使用 Directory.Build.props 文件

上面的方法都是在项目文件中引入文件的，但是如果我们有很多项目，那么我们就需要在每个项目文件中都引入这些文件。这样会让我们的项目文件变得很乱。我们可以通过使用 `Directory.Build.props` 文件来解决这个问题。我们可以在解决文件夹下创建一个 `Directory.Build.props` 文件，然后在这个文件中引入文件夹下的所有文件。比如我们想要引入 `Shared` 文件夹下的所有文件，我们可以这样做：

```xml
<Project>
    <ItemGroup>
        <Compile Include="..\Shared\**\*.cs">
            <Link>%(RecursiveDir)%(Filename)%(Extension)</Link>
        </Compile>
    </ItemGroup>
</Project>
```

## 总结

通过上面的方法，我们可以在 C# 项目中引入文件夹下的所有文件。这样我们就可以在项目中使用这些文件中的代码了。

## 参考资料

- [Linking files in a project](https://learn.microsoft.com/en-us/visualstudio/msbuild/common-msbuild-project-items?view=vs-2022&WT.mc_id=DT-MVP-5004283#compile)[^1]
- [Directory.Build.props](https://learn.microsoft.com/visualstudio/msbuild/customize-your-build?view=vs-2022&WT.mc_id=DT-MVP-5004283#directorybuildprops-and-directorybuildtargets)[^2]

[^1]: https://learn.microsoft.com/en-us/visualstudio/msbuild/common-msbuild-project-items?view=vs-2022&WT.mc_id=DT-MVP-5004283#compile
[^2]: https://learn.microsoft.com/visualstudio/msbuild/customize-your-build?view=vs-2022&WT.mc_id=DT-MVP-5004283#directorybuildprops-and-directorybuildtargets

<!-- ending -->

<!-- copyright-->
