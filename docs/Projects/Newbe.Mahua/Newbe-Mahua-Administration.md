---
date: 2017-12-24
title: Newbe.Mahua 扩展设置中心
tags:
  - Newbe.Mahua
  - QQ机器人
  - 教程

top: -999
---

本教程将描述，如何使用和扩展`Newbe.Mahua`中的`设置中心`。

<!-- more -->

## 设置中心

设置中心是 SDK 提供的，可以进行挂载菜单和界面的管理中心。使用者可以通过实现特定的接口来实现一个跨平台的统一管理界面。

![设置中心](/images/20171224-001.png)

## 扩展菜单

### 引入 nuget 包

https://www.nuget.org/packages/Newbe.Mahua.Administration/ WPF 版设置中心界面。

此 nuget 包是实现 WPF 版本的设置中心的必要组件。

最新的 VS 插件中的项目模板已经包含有此组件，无需特别安装。

### 定义菜单

在项目中实现`Newbe.Mahua.IMahuaMenuProvider`接口中定义的方法，返回菜单项。

> 不要忘记在 MahuaModule 中注册这个实现类

```csharp
using System.Collections.Generic;

namespace Newbe.Mahua.Plugins.Template
{
    public class MyMenuProvider : IMahuaMenuProvider
    {
        public IEnumerable<MahuaMenu> GetMenus()
        {
            return new[]
            {
                new MahuaMenu
                {
                    Id = "menu1",
                    Text = "测试菜单1"
                },
                new MahuaMenu
                {
                    Id = "menu2",
                    Text = "测试菜单2"
                },
            };
        }
    }
}
```

### 菜单处理事件

右键点击`MahuaEvents`文件夹，选择 添加->新建项 。 从`Newbe.Mahua`中选取`菜单处理事件`

![新建菜单处理事件](/images/20171224-005.png)

实现相关的业务逻辑。

```csharp
using Newbe.Mahua.MahuaEvents;
using System.Diagnostics;

namespace Newbe.Mahua.Plugins.Parrot.MahuaEvents
{
    /// <summary>
    /// 菜单点击事件
    /// </summary>
    public class MahuaMenuClickedMahuaEvent
        : IMahuaMenuClickedMahuaEvent
    {
        private readonly IMahuaApi _mahuaApi;

        public MahuaMenuClickedMahuaEvent(
            IMahuaApi mahuaApi)
        {
            _mahuaApi = mahuaApi;
        }

        public void ProcessManhuaMenuClicked(MahuaMenuClickedContext context)
        {
            // context.Menu 被选中到底菜单
            ShowNewbe();
        }

        private static void ShowNewbe()
        {
            Process.Start("https://newbe.hagicode.com");
        }
    }
}
```

### 启动设置中心

不同的平台点击不同的按钮来启动设置中心。

#### CQP

![新建菜单处理事件](/images/20171224-003.png)

#### Amanda

![新建菜单处理事件](/images/20171224-002.png)

#### MPQ

![新建菜单处理事件](/images/20171224-004.png)

### 完成

至此，就完成了对`设置中心`菜单的扩展。

## 自定义设置中心 UI

WPF 版设置中心是本 SDK 提供的基本界面。若在项目中不满足需求，可以通过本节内容实现彻底的自定义。

只要实现`Newbe.Mahua.IMahuaAdministration`，那么在点击平台中的`设置`或`设置中心`按钮，便会调用此接口。

> 若需要采用自定义设置中心 UI，需要移除`Newbe.Mahua.Administration`包。

<!-- md Nav-Newbe-Mahua-1.X.md -->
