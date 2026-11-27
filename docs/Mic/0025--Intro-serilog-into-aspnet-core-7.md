---
date: 2023-01-01
title: 为 ASPNETCORE 7 项目添加 Serilog
tags:
  - dotnet
  - dotnet7
  - aspnetcore
  - chatOpenAI
---

本文将介绍如何为 ASP.NET Core 项目添加 Serilog。

<!-- more -->

## 添加 Serilog

首先，我们需要在项目中添加 Serilog 的 NuGet 包。

```powershell
dotnet add package Serilog.AspNetCore
```

## 修改 Program.cs

在 Program.cs 中，添加 Serilog 的配置。

```csharp
using Serilog;

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .CreateLogger();

try
{
    Log.Information("Starting web application");

    var builder = WebApplication.CreateBuilder(args);

    builder.Host.UseSerilog(); // <-- Add this line

    var app = builder.Build();

    app.MapGet("/", () => "Hello World!");

    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Application terminated unexpectedly");
}
finally
{
    Log.CloseAndFlush();
}
```

这段代码中，我们使用 `Log.Logger` 创建了一个 Serilog 的日志记录器。然后，我们使用 `Log.Information` 记录了一条日志。在 `CreateHostBuilder` 方法中，我们使用 `builder.Host.UseSerilog()` 将 Serilog 配置到主机中。

这里的 Try/Catch 语句是为了确保在应用程序退出时，日志记录器能够正确关闭。

## 移除默认的日志记录器

我们可以移除 appsetting.json 中的日志记录器配置，仅仅保留 Serilog 的配置。

```json
{
  "Serilog": {
    "Using": ["Serilog.Sinks.Console", "Serilog.Sinks.File"],
    "MinimumLevel": "Debug",
    "WriteTo": [{ "Name": "Console" }],
    "Enrich": ["FromLogContext", "WithMachineName", "WithThreadId"]
  }
}
```

## 运行应用程序

运行应用程序，我们可以看到控制台中输出了日志。

```powershell
[22:14:44.646 DBG] RouteCollection.RouteAsync
    Routes:
        Microsoft.AspNet.Mvc.Routing.AttributeRoute
        {controller=Home}/{action=Index}/{id?}
    Handled? True
[22:14:44.647 DBG] RouterMiddleware.Invoke
    Handled? True
[22:14:45.706 DBG] /lib/jquery/jquery.js not modified
[22:14:45.706 DBG] /css/site.css not modified
[22:14:45.741 DBG] Handled. Status code: 304 File: /css/site.css
```

## 记录日志

记录日志和之前的 ASP.NET Core 项目一样，我们可以使用 `ILogger` 接口。

```csharp
public class HomeController : Controller
{
    private readonly ILogger<HomeController> _logger;

    public HomeController(ILogger<HomeController> logger)
    {
        _logger = logger;
    }

    public IActionResult Index()
    {
        _logger.LogInformation("Hello World!");

        return View();
    }
}
```

## 总结

在本文中，我们介绍了如何为 ASP.NET Core 项目添加 Serilog。

## 参考资料

- [Serilog.AspNetCore](https://www.nuget.org/packages/Serilog.AspNetCore/)
- [Serilog.Settings.Configuration](https://github.com/serilog/serilog-settings-configuration)

<!-- md Chat-AI-Footer.md -->
