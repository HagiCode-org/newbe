---
date: 2023-02-23
title: 使用一个文件集中管理你的 Nuget 依赖版本号
tags: [C#, Docker, Kubernetes]

slag: 0x025-Use-one-file-to-centrally-manage-your-Nuget-dependency-version-numbers
summary: 在 .net 7 以前，项目对于 nuget 依赖项的版本依赖散落与解决方案的各个角落。这导致升级维护和查看的时候都比较麻烦。在 .net 7 中，你可以使用一个文件来集中管理你的 Nuget 依赖版本号。本篇文章将介绍如何使用这个功能。
---

<!-- YamlFrontMatter -->

在 .net 7 以前，项目对于 nuget 依赖项的版本依赖散落与解决方案的各个角落。这导致升级维护和查看的时候都比较麻烦。在 .net 7 中，你可以使用一个文件来集中管理你的 Nuget 依赖版本号。本篇文章将介绍如何使用这个功能。

<!-- more -->

## 为什么需要这个功能

通过单文件控制 Nuget 依赖版本号。那么你就可以：

1. 统一查看
2. 升级的时候只要该这一个地方
3. 统一版本号，至少不会忘记升级某个项目

## 怎么操作呢

### 修改 Directory.Build.props

在你的项目根目录下创建一个 `Directory.Build.props` 文件，然后添加以下内容：

```xml
<Project>
    <PropertyGroup>
        <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
    </PropertyGroup>
</Project>
```

这样就启用了这个功能。

### 创建一个 Directory.Packages.props 文件

在你的项目根目录下创建一个 `Directory.Packages.props` 文件，然后添加以下内容：

```xml
<Project>
    <ItemGroup>
        <PackageVersion Include="xunit" Version="2.4.2"/>
        <PackageVersion Include="xunit.runner.visualstudio" Version="2.4.5">
            <PrivateAssets>all</PrivateAssets>
            <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
        </PackageVersion>
        <PackageVersion Include="coverlet.collector" Version="3.2.0">
            <PrivateAssets>all</PrivateAssets>
            <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
        </PackageVersion>
    </ItemGroup>
</Project>
```

这个文件就是你的 Nuget 依赖版本号的集中管理文件。其中的写法除了 `PackageVersion` 元素外，其他的都是 Nuget 的写法。你可以在这个文件中添加你的 Nuget 依赖版本号。

再次注意，这里是 `PackageVersion` 而不是 `PackageReference`。

### 修改你的项目文件

在你的项目文件中，你可以通过以下方式来引用 Nuget 依赖：

```xml
<Project>
    <ItemGroup>
        <PackageReference Include="xunit" />
        <PackageReference Include="unit.runner.visualstudio" />
    </ItemGroup>
</Project>
```

该文件和以前的写法是一样的。但是你不需要再指定版本号了。

这样你就可以通过 `Directory.Packages.props` 来集中管理你的 Nuget 依赖版本号了。

## 如果我是 .net 7 以前的版本那怎么办

实际上在 .net 7 之前，你也可以通过因为额外的 Sdk 来实现这个功能。

[Microsoft.Build.CentralPackageVersions](https://github.com/microsoft/MSBuildSdks/tree/main/src/CentralPackageVersions)[^1]

[^1]: https://github.com/microsoft/MSBuildSdks/tree/main/src/CentralPackageVersions

## 总结

通过这个功能，你可以集中管理你的 Nuget 依赖版本号。这样你就可以统一查看，升级的时候只要该这一个地方，统一版本号，至少不会忘记升级某个项目。

## 参考

- [Central Package Management (CPM)](https://learn.microsoft.com/nuget/consume-packages/central-package-management?WT.mc_id=DT-MVP-5004283)[^2]
- [Directory.Build.props](https://learn.microsoft.com/visualstudio/msbuild/customize-your-build?view=vs-2022&WT.mc_id=DT-MVP-5004283#directorybuildprops-and-directorybuildtargets)[^3]

[^2]: https://learn.microsoft.com/nuget/consume-packages/central-package-management?WT.mc_id=DT-MVP-5004283
[^3]: https://learn.microsoft.com/visualstudio/msbuild/customize-your-build?view=vs-2022&WT.mc_id=DT-MVP-5004283#directorybuildprops-and-directorybuildtargets

<!-- ending -->

<!-- ad -->

<!-- copyright-->
