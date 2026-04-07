---
date: 2020-11-08
title: 寻找性能更优秀的动态 Getter 和 Setter 方案
tags:
  - Newbe.ObjectVisitor
---

反射获取 PropertyInfo 可以对对象的属性值进行读取或者写入，但是这样性能不好。所以，我们需要更快的方案。

<!-- more -->

## 方案说明

就是用表达式编译一个`Action<TObj,TValue>`作为 Setter，编译一个`Func<TObj,TValue>`作为 Getter。

然后把这些编译好的委托放在一个**泛型类的静态字段**中保存起来，需要使用的时候从这里面查找就可以了。

## 知识要点

1. 使用表达式创建委托
2. 泛型类的静态字段是每个闭合类型独立的，因此用于存储和类型相关的内容非常方便

## 实现代码

由于代码中混合的使用 Switch 作为字典的阴招，所以代码很长，此处不再罗列，仅给出链接：

- [Github ValueGetter](https://github.com/newbe36524/Newbe.ObjectVisitor/blob/main/src/Newbe.ObjectVisitor/Newbe.ObjectVisitor/Core/ValueGetter.cs)
- [Github ValueSetter](https://github.com/newbe36524/Newbe.ObjectVisitor/blob/main/src/Newbe.ObjectVisitor/Newbe.ObjectVisitor/Core/ValueSetter.cs)
- [Gitee ValueGetter](https://gitee.com/yks/Newbe.ObjectVisitor/blob/main/src/Newbe.ObjectVisitor/Newbe.ObjectVisitor/Core/ValueGetter.cs)
- [Gitee ValueSetter](https://gitee.com/yks/Newbe.ObjectVisitor/blob/main/src/Newbe.ObjectVisitor/Newbe.ObjectVisitor/Core/ValueSetter.cs)

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

1. 使用委托明显比使用 PropertyInfo 要快，这个方案可以。
2. Framework 真拉胯，Net 5 简直太强了。
3. 如果属性是明确的，建议把字典中取出来的委托保存在自己的上下文，这可以明显的省去查找的消耗。

### 图表

从左往右分别是：直接读取属性、缓存委托、不缓存委托和使用 PropertyInfo。

![Getter](/images/20201101-003.png)
![Setter](/images/20201101-004.png)

### 数据

Getter

| Method         | Job          | Runtime       |        Mean |     Error |    StdDev |      Median |   Ratio | RatioSD | Rank |
| -------------- | ------------ | ------------- | ----------: | --------: | --------: | ----------: | ------: | ------: | ---: |
| DirectlyString | net461       | .NET 4.6.1    |   0.1636 ns | 0.0822 ns | 0.1126 ns |   0.1472 ns |       ? |       ? |    2 |
| DirectlyInt    | net461       | .NET 4.6.1    |   0.0318 ns | 0.0348 ns | 0.0342 ns |   0.0217 ns |       ? |       ? |    1 |
| ReflectString  | net461       | .NET 4.6.1    | 145.8375 ns | 2.2790 ns | 2.1317 ns | 145.6522 ns |       ? |       ? |    7 |
| ReflectInt     | net461       | .NET 4.6.1    | 172.5066 ns | 1.3206 ns | 1.1028 ns | 172.6804 ns |       ? |       ? |    8 |
| GetterString   | net461       | .NET 4.6.1    |  31.4379 ns | 0.6017 ns | 0.5334 ns |  31.6316 ns |       ? |       ? |    4 |
| GetterInt      | net461       | .NET 4.6.1    |  33.0642 ns | 0.4940 ns | 0.4380 ns |  33.0557 ns |       ? |       ? |    5 |
| GetterObject   | net461       | .NET 4.6.1    |  33.9174 ns | 0.5587 ns | 0.5226 ns |  33.7326 ns |       ? |       ? |    6 |
| GetterCached   | net461       | .NET 4.6.1    |   7.5878 ns | 0.1223 ns | 0.1144 ns |   7.5765 ns |       ? |       ? |    3 |
|                |              |               |             |           |           |             |         |         |      |
| DirectlyString | net48        | .NET 4.8      |   0.0181 ns | 0.0353 ns | 0.0313 ns |   0.0043 ns |       ? |       ? |    1 |
| DirectlyInt    | net48        | .NET 4.8      |   0.0050 ns | 0.0089 ns | 0.0079 ns |   0.0000 ns |       ? |       ? |    1 |
| ReflectString  | net48        | .NET 4.8      | 143.8313 ns | 2.2501 ns | 2.1047 ns | 143.5568 ns |       ? |       ? |    5 |
| ReflectInt     | net48        | .NET 4.8      | 172.1714 ns | 1.9819 ns | 1.7569 ns | 172.3142 ns |       ? |       ? |    6 |
| GetterString   | net48        | .NET 4.8      |  31.5887 ns | 0.6310 ns | 0.5902 ns |  31.5385 ns |       ? |       ? |    3 |
| GetterInt      | net48        | .NET 4.8      |  32.7140 ns | 0.3992 ns | 0.3734 ns |  32.7343 ns |       ? |       ? |    4 |
| GetterObject   | net48        | .NET 4.8      |  33.3063 ns | 0.2069 ns | 0.1834 ns |  33.3053 ns |       ? |       ? |    4 |
| GetterCached   | net48        | .NET 4.8      |   7.5540 ns | 0.2201 ns | 0.1951 ns |   7.5069 ns |       ? |       ? |    2 |
|                |              |               |             |           |           |             |         |         |      |
| DirectlyString | netcoreapp21 | .NET Core 2.1 |   0.0000 ns | 0.0000 ns | 0.0000 ns |   0.0000 ns |       ? |       ? |    1 |
| DirectlyInt    | netcoreapp21 | .NET Core 2.1 |   0.0193 ns | 0.0111 ns | 0.0104 ns |   0.0177 ns |       ? |       ? |    2 |
| ReflectString  | netcoreapp21 | .NET Core 2.1 | 110.4180 ns | 2.2159 ns | 1.8503 ns | 110.8038 ns |       ? |       ? |    7 |
| ReflectInt     | netcoreapp21 | .NET Core 2.1 | 138.9612 ns | 0.9694 ns | 0.8594 ns | 138.8217 ns |       ? |       ? |    8 |
| GetterString   | netcoreapp21 | .NET Core 2.1 |  16.8958 ns | 0.2384 ns | 0.2230 ns |  16.8103 ns |       ? |       ? |    4 |
| GetterInt      | netcoreapp21 | .NET Core 2.1 |  19.4407 ns | 0.2041 ns | 0.1809 ns |  19.4539 ns |       ? |       ? |    6 |
| GetterObject   | netcoreapp21 | .NET Core 2.1 |  18.6922 ns | 0.2700 ns | 0.2255 ns |  18.6582 ns |       ? |       ? |    5 |
| GetterCached   | netcoreapp21 | .NET Core 2.1 |   0.9299 ns | 0.0457 ns | 0.0427 ns |   0.9308 ns |       ? |       ? |    3 |
|                |              |               |             |           |           |             |         |         |      |
| DirectlyString | netcoreapp31 | .NET Core 3.1 |   0.0000 ns | 0.0000 ns | 0.0000 ns |   0.0000 ns |       ? |       ? |    1 |
| DirectlyInt    | netcoreapp31 | .NET Core 3.1 |   0.0693 ns | 0.0102 ns | 0.0091 ns |   0.0709 ns |       ? |       ? |    2 |
| ReflectString  | netcoreapp31 | .NET Core 3.1 |  98.6735 ns | 0.8335 ns | 0.7389 ns |  98.5319 ns |       ? |       ? |    7 |
| ReflectInt     | netcoreapp31 | .NET Core 3.1 | 130.6941 ns | 0.9332 ns | 0.8730 ns | 130.5376 ns |       ? |       ? |    8 |
| GetterString   | netcoreapp31 | .NET Core 3.1 |  14.8915 ns | 0.2025 ns | 0.1795 ns |  14.8911 ns |       ? |       ? |    4 |
| GetterInt      | netcoreapp31 | .NET Core 3.1 |  16.2874 ns | 0.0789 ns | 0.0700 ns |  16.2753 ns |       ? |       ? |    5 |
| GetterObject   | netcoreapp31 | .NET Core 3.1 |  17.6202 ns | 0.1130 ns | 0.1057 ns |  17.6092 ns |       ? |       ? |    6 |
| GetterCached   | netcoreapp31 | .NET Core 3.1 |   0.6351 ns | 0.0244 ns | 0.0217 ns |   0.6393 ns |       ? |       ? |    3 |
|                |              |               |             |           |           |             |         |         |      |
| DirectlyString | netcoreapp5  | .NET Core 5.0 |   0.5098 ns | 0.0328 ns | 0.0291 ns |   0.5131 ns |   1.000 |    0.00 |    2 |
| DirectlyInt    | netcoreapp5  | .NET Core 5.0 |   0.0000 ns | 0.0000 ns | 0.0000 ns |   0.0000 ns |   0.000 |    0.00 |    1 |
| ReflectString  | netcoreapp5  | .NET Core 5.0 |  88.8937 ns | 0.9697 ns | 0.8596 ns |  88.7457 ns | 174.838 |    9.26 |    7 |
| ReflectInt     | netcoreapp5  | .NET Core 5.0 | 123.4464 ns | 1.0582 ns | 0.9898 ns | 123.3193 ns | 242.996 |   14.00 |    8 |
| GetterString   | netcoreapp5  | .NET Core 5.0 |   7.6628 ns | 0.0931 ns | 0.0777 ns |   7.6703 ns |  15.031 |    0.95 |    5 |
| GetterInt      | netcoreapp5  | .NET Core 5.0 |   6.6645 ns | 0.0825 ns | 0.0772 ns |   6.6497 ns |  13.085 |    0.69 |    4 |
| GetterObject   | netcoreapp5  | .NET Core 5.0 |   8.3090 ns | 0.1685 ns | 0.1576 ns |   8.2865 ns |  16.344 |    0.83 |    6 |
| GetterCached   | netcoreapp5  | .NET Core 5.0 |   0.9791 ns | 0.0293 ns | 0.0245 ns |   0.9764 ns |   1.920 |    0.13 |    3 |

Setter

| Method         | Job          | Runtime       |        Mean |     Error |    StdDev |      Median |   Ratio | RatioSD | Rank |
| -------------- | ------------ | ------------- | ----------: | --------: | --------: | ----------: | ------: | ------: | ---: |
| DirectlyString | net461       | .NET 4.6.1    |   2.0161 ns | 0.0300 ns | 0.0266 ns |   2.0045 ns |   1.000 |    0.00 |    2 |
| DirectlyInt    | net461       | .NET 4.6.1    |   0.0076 ns | 0.0094 ns | 0.0083 ns |   0.0081 ns |   0.004 |    0.00 |    1 |
| ReflectString  | net461       | .NET 4.6.1    | 237.5006 ns | 4.5706 ns | 4.4890 ns | 236.5912 ns | 117.871 |    3.40 |    5 |
| ReflectInt     | net461       | .NET 4.6.1    | 249.3627 ns | 2.1717 ns | 2.0314 ns | 249.0283 ns | 123.681 |    1.94 |    6 |
| GetterString   | net461       | .NET 4.6.1    |  32.8621 ns | 0.2855 ns | 0.2229 ns |  32.9189 ns |  16.335 |    0.22 |    4 |
| GetterInt      | net461       | .NET 4.6.1    |  33.6103 ns | 0.4245 ns | 0.3544 ns |  33.5499 ns |  16.695 |    0.26 |    4 |
| GetterObject   | net461       | .NET 4.6.1    |  33.2561 ns | 0.2966 ns | 0.2629 ns |  33.1795 ns |  16.497 |    0.17 |    4 |
| GetterCached   | net461       | .NET 4.6.1    |   9.1805 ns | 0.0761 ns | 0.0674 ns |   9.1802 ns |   4.554 |    0.08 |    3 |
|                |              |               |             |           |           |             |         |         |      |
| DirectlyString | net48        | .NET 4.8      |   1.9272 ns | 0.0298 ns | 0.0264 ns |   1.9245 ns |   1.000 |    0.00 |    2 |
| DirectlyInt    | net48        | .NET 4.8      |   0.0000 ns | 0.0000 ns | 0.0000 ns |   0.0000 ns |   0.000 |    0.00 |    1 |
| ReflectString  | net48        | .NET 4.8      | 237.7686 ns | 4.6597 ns | 5.3661 ns | 235.8445 ns | 123.908 |    3.57 |    5 |
| ReflectInt     | net48        | .NET 4.8      | 249.6291 ns | 4.5333 ns | 4.2404 ns | 249.5459 ns | 129.689 |    3.13 |    6 |
| GetterString   | net48        | .NET 4.8      |  32.2366 ns | 0.1941 ns | 0.1721 ns |  32.1780 ns |  16.731 |    0.29 |    4 |
| GetterInt      | net48        | .NET 4.8      |  32.0081 ns | 0.1488 ns | 0.1162 ns |  32.0270 ns |  16.572 |    0.23 |    4 |
| GetterObject   | net48        | .NET 4.8      |  32.6413 ns | 0.1417 ns | 0.1183 ns |  32.6260 ns |  16.907 |    0.24 |    4 |
| GetterCached   | net48        | .NET 4.8      |   9.2589 ns | 0.0928 ns | 0.0868 ns |   9.2564 ns |   4.799 |    0.07 |    3 |
|                |              |               |             |           |           |             |         |         |      |
| DirectlyString | netcoreapp21 | .NET Core 2.1 |   2.4107 ns | 0.0507 ns | 0.0475 ns |   2.3936 ns |   1.000 |    0.00 |    2 |
| DirectlyInt    | netcoreapp21 | .NET Core 2.1 |   0.0007 ns | 0.0028 ns | 0.0025 ns |   0.0000 ns |   0.000 |    0.00 |    1 |
| ReflectString  | netcoreapp21 | .NET Core 2.1 | 203.6637 ns | 3.6109 ns | 3.3777 ns | 203.4793 ns |  84.517 |    2.31 |    7 |
| ReflectInt     | netcoreapp21 | .NET Core 2.1 | 213.8619 ns | 2.1882 ns | 1.9398 ns | 213.7367 ns |  88.757 |    1.71 |    8 |
| GetterString   | netcoreapp21 | .NET Core 2.1 |  19.5240 ns | 0.0811 ns | 0.0758 ns |  19.5149 ns |   8.102 |    0.15 |    5 |
| GetterInt      | netcoreapp21 | .NET Core 2.1 |  18.8794 ns | 0.1193 ns | 0.1058 ns |  18.8837 ns |   7.836 |    0.18 |    4 |
| GetterObject   | netcoreapp21 | .NET Core 2.1 |  20.6765 ns | 0.2709 ns | 0.2115 ns |  20.6419 ns |   8.584 |    0.14 |    6 |
| GetterCached   | netcoreapp21 | .NET Core 2.1 |   2.7606 ns | 0.0613 ns | 0.0512 ns |   2.7590 ns |   1.148 |    0.02 |    3 |
|                |              |               |             |           |           |             |         |         |      |
| DirectlyString | netcoreapp31 | .NET Core 3.1 |   2.2625 ns | 0.0647 ns | 0.0605 ns |   2.2555 ns |   1.000 |    0.00 |    2 |
| DirectlyInt    | netcoreapp31 | .NET Core 3.1 |   0.0072 ns | 0.0165 ns | 0.0146 ns |   0.0000 ns |   0.003 |    0.01 |    1 |
| ReflectString  | netcoreapp31 | .NET Core 3.1 | 182.7306 ns | 3.3249 ns | 3.1101 ns | 182.3062 ns |  80.804 |    1.99 |    7 |
| ReflectInt     | netcoreapp31 | .NET Core 3.1 | 192.2510 ns | 2.3691 ns | 2.1002 ns | 191.4821 ns |  85.061 |    2.88 |    8 |
| GetterString   | netcoreapp31 | .NET Core 3.1 |  16.9918 ns | 0.2115 ns | 0.1979 ns |  16.9651 ns |   7.516 |    0.25 |    5 |
| GetterInt      | netcoreapp31 | .NET Core 3.1 |  16.1168 ns | 0.3558 ns | 0.3654 ns |  15.9822 ns |   7.138 |    0.19 |    4 |
| GetterObject   | netcoreapp31 | .NET Core 3.1 |  19.3060 ns | 0.4173 ns | 0.5571 ns |  19.4856 ns |   8.480 |    0.45 |    6 |
| GetterCached   | netcoreapp31 | .NET Core 3.1 |   2.9276 ns | 0.0156 ns | 0.0146 ns |   2.9313 ns |   1.295 |    0.03 |    3 |
|                |              |               |             |           |           |             |         |         |      |
| DirectlyString | netcoreapp5  | .NET Core 5.0 |   2.2455 ns | 0.0084 ns | 0.0078 ns |   2.2460 ns |   1.000 |    0.00 |    2 |
| DirectlyInt    | netcoreapp5  | .NET Core 5.0 |   0.0000 ns | 0.0000 ns | 0.0000 ns |   0.0000 ns |   0.000 |    0.00 |    1 |
| ReflectString  | netcoreapp5  | .NET Core 5.0 | 162.8780 ns | 0.7135 ns | 0.6674 ns | 162.8741 ns |  72.538 |    0.45 |    7 |
| ReflectInt     | netcoreapp5  | .NET Core 5.0 | 171.1380 ns | 0.4173 ns | 0.3699 ns | 171.1414 ns |  76.217 |    0.31 |    8 |
| GetterString   | netcoreapp5  | .NET Core 5.0 |   8.6244 ns | 0.1891 ns | 0.1769 ns |   8.5469 ns |   3.841 |    0.08 |    5 |
| GetterInt      | netcoreapp5  | .NET Core 5.0 |   6.5511 ns | 0.0347 ns | 0.0325 ns |   6.5634 ns |   2.917 |    0.02 |    4 |
| GetterObject   | netcoreapp5  | .NET Core 5.0 |   9.0732 ns | 0.0306 ns | 0.0272 ns |   9.0735 ns |   4.041 |    0.02 |    6 |
| GetterCached   | netcoreapp5  | .NET Core 5.0 |   2.8223 ns | 0.0728 ns | 0.0681 ns |   2.8190 ns |   1.257 |    0.03 |    3 |

## 总结

使用表达式创建委托来取代 PropertyInfo 读取和写入属性效果很好。

开发者也可以直接引用 Newbe.ObjectVisitor 包来使用已经封装好的 ValueGetter 和 ValueSetter。

## 我只是知识的搬运工

- [晚绑定场景下对象属性赋值和取值可以不需要 PropertyInfo](https://www.cnblogs.com/artech/archive/2011/03/24/PropertyAccessor.html)
- [三种属性操作性能比较：PropertyInfo + Expression Tree + Delegate.CreateDelegate](https://www.cnblogs.com/artech/archive/2011/03/26/Propertyaccesstest.html)
- [关于 Expression Tree 和 IL Emit 的所谓的"性能差别"](https://www.cnblogs.com/artech/archive/2011/03/27/ExpressTreeVsIlEmit.html)

<!-- md Footer-Newbe-ObjectVisitor.md -->
