---
date: 2020-11-08
title: 寻找性能更优秀的不可变小字典
tags:
  - Newbe.ObjectVisitor
---

Dictionary 是一个很常用的键值对管理数据结构。但是在性能要求严苛的情况下，字典的查找速度并不高。所以，我们需要更快的方案。

<!-- more -->

## 需求说明

这里，我们需要一个 PropertyInfo 和委托对应的映射关系，这样我们就可以存储《[Newbe.ObjectVisitor/Better-Performance-Getter-Setter](./Better-Performance-Getter-Setter)》提到的委托。

因此，这个字典有这些特点：

1. 这个字典一旦创建就不需要修改。
2. 字典项目并不多，因为通常一个 class 不会有太多属性。

## 方案说明

方案 1，Switch 表达式法。使用表达式生成一个包含 switch case 语句的委托。

方案 2，数组跳表。我们知道，switch case 之所以比连续的 if else 要快的原因是因为其生成的 IL 中包含一个跳表算法。因此，如果我们有办法使用连续数字作为下标，以及一个数组。就可以在 C#中自己实现跳表。

## 知识要点

1. 使用表达式创建委托
2. PropertyInfo 有一个 int MetadataToken 属性，根据目前的观察，可以知道在一个类型中的属性其 MetadataToken 似乎是连续的，因此可以取模后作为跳表的 key。
3. 所谓的跳表，可以简单理解为，使用数组的下标来定位数组中的特定元素。

## 实现代码

这里，我们直接给出基准测试中使用的代码。

其中：

- Directly 直接读，没有任何查找
- ArrayIndex 数组跳表
- SwitchExp 表达式生成 Switch 方案
- Dic 传统字典方案

```cs
using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using BenchmarkDotNet.Attributes;

namespace Newbe.ObjectVisitor.BenchmarkTest
{
    [Config(typeof(Config))]
    public class FuncSearchTest
    {
        private Func<Yueluo, object>[] _target;
        private readonly Yueluo _yueluo;
        private readonly Func<Yueluo, string> _func;
        private readonly PropertyInfo _nameP;
        private readonly Func<PropertyInfo, Func<Yueluo, object>> _switcher;
        private readonly Dictionary<PropertyInfo, Func<Yueluo, object>> _dic;

        public FuncSearchTest()
        {
            _yueluo = Yueluo.Create();
            var propertyInfos = typeof(Yueluo).GetProperties().ToArray();

            CreateCacheArrayD(propertyInfos);

            _switcher = ValueGetter.CreateGetter<Yueluo, object>(propertyInfos,
                info => Expression.SwitchCase(Expression.Constant(CreateFunc(info)), Expression.Constant(info)));
            _dic = propertyInfos.ToDictionary(x => x, CreateFunc);

            _nameP = typeof(Yueluo).GetProperty(nameof(Yueluo.Name));
            _func = x => x.Name;
        }

        private void CreateCacheArrayD(IReadOnlyCollection<PropertyInfo> propertyInfos)
        {
            _target = new Func<Yueluo, object>[propertyInfos.Count];
            foreach (var info in propertyInfos)
            {
                var key = GetKey(info);
                var index = key % propertyInfos.Count;
                _target[index] = CreateFunc(info);
            }
        }

        private static Func<Yueluo, object> CreateFunc(PropertyInfo info)
        {
            var pExp = Expression.Parameter(typeof(Yueluo), "x");
            var bodyExp = Expression.Property(pExp, info);
            var finalExp =
                Expression.Lambda<Func<Yueluo, object>>(Expression.Convert(bodyExp, typeof(object)), pExp);
            return finalExp.Compile();
        }

        private static int GetKey(MemberInfo info)
        {
            var token = info.MetadataToken;
            return token;
        }

        [Benchmark(Baseline = true)]
        public string Directly() => _func(_yueluo);

        [Benchmark]
        public string ArrayIndex() => (string) _target[_nameP.MetadataToken % _target.Length](_yueluo);

        [Benchmark]
        public string SwitchExp() => (string) _switcher(_nameP)(_yueluo);

        [Benchmark]
        public string Dic() => (string) _dic[_nameP](_yueluo);
    }
}
```

## 基准测试

```ini

BenchmarkDotNet=v0.12.1, OS=Windows 10.0.19041.572 (2004/?/20H1)
Intel Xeon CPU E5-2678 v3 2.50GHz, 1 CPU, 24 logical and 12 physical cores
.NET Core SDK=5.0.100-rc.2.20479.15
  [Host]       : .NET Core 2.1.23 (CoreCLR 4.6.29321.03, CoreFX 4.6.29321.01), X64 RyuJIT
  net461       : .NET Framework 4.8 (4.8.4250.0), X64 RyuJIT
  net48        : .NET Framework 4.8 (4.8.4250.0), X64 RyuJIT
  netcoreapp21 : .NET Core 2.1.23 (CoreCLR 4.6.29321.03, CoreFX 4.6.29321.01), X64 RyuJIT
  netcoreapp31 : .NET Core 3.1.9 (CoreCLR 4.700.20.47201, CoreFX 4.700.20.47203), X64 RyuJIT
  netcoreapp5  : .NET Core 5.0.0 (CoreCLR 5.0.20.47505, CoreFX 5.0.20.47505), X64 RyuJIT
```

### 结论

1. 字典真拉胯。
2. Framework 真拉胯。
3. Net 5 简直太强了。
4. 数组跳表是非直接方案中最快的。

### 图表

![FuncSearch](/images/20201101-005.png)

### 数据

| Method     | Job          | Runtime       |       Mean |     Error |    StdDev | Ratio | RatioSD | Rank |
| ---------- | ------------ | ------------- | ---------: | --------: | --------: | ----: | ------: | ---: |
| Directly   | net461       | .NET 4.6.1    |  0.9347 ns | 0.0363 ns | 0.0321 ns |  1.00 |    0.00 |    1 |
| ArrayIndex | net461       | .NET 4.6.1    | 15.0904 ns | 0.3820 ns | 0.3752 ns | 16.13 |    0.64 |    2 |
| SwitchExp  | net461       | .NET 4.6.1    | 17.1585 ns | 0.0624 ns | 0.0521 ns | 18.30 |    0.56 |    3 |
| Dic        | net461       | .NET 4.6.1    | 34.3348 ns | 0.2447 ns | 0.2169 ns | 36.77 |    1.18 |    4 |
|            |              |               |            |           |           |       |         |      |
| Directly   | net48        | .NET 4.8      |  0.6338 ns | 0.0233 ns | 0.0218 ns |  1.00 |    0.00 |    1 |
| ArrayIndex | net48        | .NET 4.8      | 15.3098 ns | 0.2794 ns | 0.2613 ns | 24.17 |    0.69 |    2 |
| SwitchExp  | net48        | .NET 4.8      | 17.8113 ns | 0.0740 ns | 0.0656 ns | 28.20 |    0.98 |    3 |
| Dic        | net48        | .NET 4.8      | 33.7930 ns | 0.4538 ns | 0.4245 ns | 53.36 |    1.64 |    4 |
|            |              |               |            |           |           |       |         |      |
| Directly   | netcoreapp21 | .NET Core 2.1 |  1.2153 ns | 0.1168 ns | 0.1434 ns |  1.00 |    0.00 |    1 |
| ArrayIndex | netcoreapp21 | .NET Core 2.1 |  4.6545 ns | 0.1044 ns | 0.0871 ns |  4.01 |    0.51 |    2 |
| SwitchExp  | netcoreapp21 | .NET Core 2.1 |  8.1995 ns | 0.2567 ns | 0.2747 ns |  6.81 |    0.90 |    3 |
| Dic        | netcoreapp21 | .NET Core 2.1 | 24.2669 ns | 0.5440 ns | 0.5586 ns | 20.07 |    2.51 |    4 |
|            |              |               |            |           |           |       |         |      |
| Directly   | netcoreapp31 | .NET Core 3.1 |  0.7382 ns | 0.1148 ns | 0.1074 ns |  1.00 |    0.00 |    1 |
| ArrayIndex | netcoreapp31 | .NET Core 3.1 |  4.3580 ns | 0.1299 ns | 0.1085 ns |  6.10 |    0.77 |    2 |
| SwitchExp  | netcoreapp31 | .NET Core 3.1 |  7.5985 ns | 0.1310 ns | 0.1161 ns | 10.45 |    1.41 |    3 |
| Dic        | netcoreapp31 | .NET Core 3.1 | 22.2433 ns | 0.2756 ns | 0.2443 ns | 30.61 |    4.20 |    4 |
|            |              |               |            |           |           |       |         |      |
| Directly   | netcoreapp5  | .NET Core 5.0 |  1.3323 ns | 0.0527 ns | 0.0493 ns |  1.00 |    0.00 |    1 |
| ArrayIndex | netcoreapp5  | .NET Core 5.0 |  5.0058 ns | 0.1361 ns | 0.1206 ns |  3.77 |    0.15 |    2 |
| SwitchExp  | netcoreapp5  | .NET Core 5.0 |  9.0576 ns | 0.0985 ns | 0.0921 ns |  6.81 |    0.26 |    3 |
| Dic        | netcoreapp5  | .NET Core 5.0 | 20.4052 ns | 0.2724 ns | 0.2275 ns | 15.44 |    0.59 |    4 |

## 总结

不论是数组跳表还是表达式 Switch 方案都可以解决这个问题，而且都要比使用字典要快。

但是这里有一个问题，就是目前作者还没有找到任何有关 MetadataToken 是否真的具备同 class 连续的性质。

因此建议还是使用 Switch 方案实现。

## 我只是知识的搬运工

- [Working with Expression Trees in C#](https://tyrrrz.me/blog/expression-trees)

<!-- md Footer-Newbe-ObjectVisitor.md -->
