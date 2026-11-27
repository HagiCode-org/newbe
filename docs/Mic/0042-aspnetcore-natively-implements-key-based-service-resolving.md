---
date: 2023-02-21
title: aspnetcore 原生 DI 实现基于 key 的服务获取
tags: [C#, Docker, Kubernetes]

slag: 0x023-aspnetcore-natively-implements-key-based-service-resolving
summary: 你可能想通过一个字符串或者其他的类型来获取一个具体的服务实现，那么在 aspnetcore 原生的 MSDI 中，如何实现呢？本文将介绍如何通过自定义工厂来实现。
---

<!-- YamlFrontMatter -->

你可能想通过一个字符串或者其他的类型来获取一个具体的服务实现，那么在 aspnetcore 原生的 MSDI 中，如何实现呢？本文将介绍如何通过自定义工厂来实现。

<!-- more -->

## 我们现在恰好有基于 Json 和 MessagePack 的两种序列化器

有一个接口是这样的

```csharp
public interface ISerializer
{
    byte[] Serialize<T>(T obj);
    T Deserialize<T>(ReadOnlySpan<byte> data);
}
```

并且由两个不同的实现

```csharp
// Json
public class MyJsonSerializer : ISerializer
{
    public byte[] Serialize<T>(T obj)
    {
        throw new NotImplementedException();
    }

    public T Deserialize<T>(ReadOnlySpan<byte> data)
    {
        throw new NotImplementedException();
    }
}

// MessagePack
public class MyMessagePackSerializer : ISerializer
{
    public byte[] Serialize<T>(T obj)
    {
        throw new NotImplementedException();
    }

    public T Deserialize<T>(ReadOnlySpan<byte> data)
    {
        throw new NotImplementedException();
    }
}
```

我有一个服务，需要使用这两种序列化器中的一种。

```csharp
public class MyService
{
    public object DoSomething(string dataType, ReadOnlySpan<byte> data)
    {
        // 根据 dataType 来决定使用哪种序列化器
    }
}
```

## 使用委托来定义获取服务的方法

我们可以通过委托来定义获取服务的方法，如下

```csharp
public delegate ISerializer SerializerFactory(string dataType);
```

然后在 `ConfigureServices` 方法中注册

```csharp
services.AddSingleton<MyJsonSerializer>();
services.AddSingleton<MyMessagePackSerializer>();
services.AddSingleton<SerializerFactory>(sp =>
{
    return dataType =>
    {
        switch (dataType)
        {
            case "json":
                return sp.GetRequiredService<MyJsonSerializer>();
            case "msgpack":
                return sp.GetRequiredService<MyMessagePackSerializer>();
            default:
                throw new NotSupportedException();
        }
    };
});
```

这样我们就可以在 `MyService` 中通过委托来获取服务了

```csharp
public class MyService
{
    private readonly SerializerFactory _serializerFactory;

    public MyService(SerializerFactory serializerFactory)
    {
        _serializerFactory = serializerFactory;
    }

    public object DoSomething(string dataType, ReadOnlySpan<byte> data)
    {
        var serializer = _serializerFactory(dataType);
        return serializer.Deserialize<object>(data);
    }
}
```

## 基于配置来改变工厂

因为本质是通过委托来获取服务，所以我们可以通过配置来改变委托的行为，如下

```csharp
public static class SerializerFactoryExtensions
{
    public static SerializerFactory CreateSerializerFactory(this IServiceProvider sp)
    {
        // get mapping from configuration
        var mapping = sp.GetRequiredService<IConfiguration>()
                      .GetSection("SerializerMapping")
                      .Get<Dictionary<string, string>>();
        return dataType =>
        {
            var serializerType = mapping[dataType];
            return (ISerializer)sp.GetRequiredService(Type.GetType(serializerType));
        };
    }
}
```

然后在 `appsettings.json` 中配置

```json
{
  "SerializerMapping": {
    "json": "WebApplication1.MyJsonSerializer",
    "msgpack": "WebApplication1.MyMessagePackSerializer"
  }
}
```

然后在 `ConfigureServices` 方法中注册

```csharp
services.AddSingleton<MyJsonSerializer>();
services.AddSingleton<MyMessagePackSerializer>();
services.AddSingleton(SerializerFactoryExtensions.CreateSerializerFactory);
```

## 总结

本篇文章介绍了如何通过自定义工厂来实现基于 key 的服务获取，这种方式在 aspnetcore 原生的 DI 中是原生支持的。

## 参考

- [Dependency injection guidelines](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines?WT.mc_id=DT-MVP-5004283)[^1]

[^1]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines?WT.mc_id=DT-MVP-5004283

<!-- ending -->

<!-- ad -->

<!-- copyright-->
