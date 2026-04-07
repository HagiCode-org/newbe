---
date: 2020-11-03
title: 究竟是什么可以比反射还快实现动态调用？
tags:
  - 微信公众号文章
---

究竟是什么可以比反射动态调用还快？

<!-- more -->

## 戏精分享 C#表达式树，第一季正式完稿

前不久，我们发布了[《只要十步，你就可以应用表达式树来优化动态调用》](https://newbe.hagicode.com/Newbe.Claptrap/Using-Expression-Tree-To-Build-Delegate/)。

观众们普遍反映文章的内容太多复杂不太容易理解。

因此，我们以此为契机发布了《戏精分享 C#表达式树》系列视频。现在，第一季的视频已经正式完稿，发布到了 B 站之上。

各位可以前往以下地址来查看内容：https://www.bilibili.com/video/BV15y4y1r7pK

## Newbe.ObjectVisitor 0.1.4 现已可用

Newbe.ObjectVisitor 帮助开发者可以用最简单的最高效的方式访问一个普通 class 的所有属性。从而实现：验证、映射、收集等等操作。

例如, 在你的代码中有这样一个简单的类。

```cs
var order = new OrderInfo();
```

你想要将这个类所有的属性和值都打印出来，那么你可以采用反射来完成：

```cs
for(var pInfo in typeof(OrderInfo).GetProperties())
{
    Console.Writeline($"{pInfo.Name}: {pInfo.GetValue(order)}");
}
```

如果你使用这个类库，则可以采用以下方式来实现一样的效果：

```cs
// call .V what is a static extension method
// you get a visitor object for order
var visitor = order.V();

visitor.ForEach(context=>{
    var name = context.Name;
    var value = context.Value;
    Console.Writeline($"{name}: {value}");
}).Run();

// you can also make it into one line
order.V().ForEach(c=> Console.Writeline($"{c.Name}: {c.Value}")).Run();

// or using quick style
order.FormatToString();
```

那我为什么要这样做?

- 因为这样更快！这个类库使用表达式树实现，因此它拥有比直接使用反射快上 10 倍的性能.
- 因为这样更可读！通过这个类库你可以使用链式 API 和命名方法来创建一个委托，这样可以让你的代码实现和硬编码同样的可读效果。
- 因为这样更具扩展性！如果使用了这个类库，你就拥有了一个简便的方法来访问一个类所有的属性。因此，你就做很多你想做的事情，比如：创建一个验证器来验证你的模型，修改一些可能包含敏感数据的属性从而避免输出到日志中，创建一个类似于 AutoMapper 的对象映射器但是拥有更好的性能，诸如此类。

我们发布了第一个版本。0.1 版本中我们完成了最基础的 ForEach API，并且实现了 FormatString 方法。

我们对初始版本进行了基准测试。得出了以下结论，详细的内容也可以前往仓库首页查看：

1. 该类库可以实现和硬编码一样快速的性能。
2. 该类库比直接使用反射更快。
3. 对于非代码热点路径，即使使用非缓存方式调用也仍然在可接受范围内容。

![Cache](/images/20201031-001.png)

![NoCache](/images/20201031-002.png)

## 目前，我们还有很多计划中的 API

| icon | remark                                                      |
| ---- | ----------------------------------------------------------- |
| ✔️   | it is already avaliable in latest version                   |
| 🚧   | still in plan or development and will be changed or removed |
| ❌   | it is removed form the latest version                       |

```cs
var o = new Yueluo();

using Newbe.ObjectVisitor;

//✔️ from 0.1
// V is a static extension method
var visitor = o.V();

//✔️ from 0.1
// create visitor from factory method
var visitor = typeof(Yueluo).V();

//✔️ from 0.1
// create and fire way.
// this is the most simple structure about this lib
// there are Name, Value, PropertyInfo, SourceObj, SourceObjType and etc in the context
o.V().ForEach((context)=>{}).Run();
o.V().ForEach((name,value)=>{}).Run();

//✔️ from 0.1
// create a visitor with extend object as parameter
o.V().WithExtendObject<Yueluo, StringBuilder>()
    .ForEach((context)=>{var _ = context.ExtendObject})
    .Run(new StringBuilder());
o.V().WithExtendObject<Yueluo, StringBuilder>()
    .ForEach((name,value,stringBuilder)=>{})
    .Run(new StringBuilder());

//✔️ from 0.1
// create and cache way. This is suggested way to use.
// cache object visitor to run it with anothor object
var cachedVisitor = deafult(Yueluo).V().ForEach((context)=>{}).Cache();
cachedVisitor.Run(new Yueluo());

//✔️ from 0.1
// cache object visitor with extend object
var cachedVisitor = deafult(Yueluo).V()
    .WithExtendObject<Yueluo, StringBuilder>()
    .ForEach((context)=>{var _ = context.ExtendObject})
    .Cache();
cachedVisitor.Run(new Yueluo(), new StringBuilder());


//🚧 you can modify value if return a new value
o.V().ForEach((context)=>context.Value.SubString(0,1)).Run();

//✔️ from 0.1
// get debug info about expression now
var debugInfo = o.V().ForEach((context)=>{}).GetDebugInfo();

//🚧 generate code in C# as a string about expression now
var code = o.V().ForEach((context)=>{}).GenerateCode();

//✔️ from 0.1
// generate a lambda func
var func = o.V().ForEach((context)=>{}).GetLambda();


//🚧 foreach properties with specified type
o.V().ForEach<string>((context)=>{}).Run();

//🚧  using linq to filter
o.V().AsEnumerable().Where((context)=>context.Name == "YueLuo").ForEach((context)=>{}).Run();

//🚧  suppending visiting sub object
o.V().SuppendSubObject().ForEach((context)=>{}).Run();

//🚧  suppending visiting enumerable object
o.V().SuppendEnumerable().ForEach((context)=>{}).Run();


/**
 ✔️ from 0.1
 sample to join all properties to string
*/
var sb = new StringBuilder();
o.V().ForEach((context)=>{
    sb.Append(context.Name);
    sb.Append(context.Value);
    sb.Append(Enviroment.Newline);
}).Run();
var s = sb.ToString();

//✔️ from 0.1
// quick style for above
var s = o.FormatString();

//🚧 Deconstruct as C# 7 but more flexible
var destructor1 = Destructor<Yueluo>
    .Property(x=>x.Name)
    .Property(x=>x.Age)

var destructor2 = Destructor<Yueluo>
    .Property(x=>x.Name)
    .Property(x=>(long)x.Age)

var destructor3 = Destructor<Yueluo>
    .Property(x=>x.Name)
    .Property(x=>x.NickName)
    .Property(x=>x.Age)

var (name, age) = o.V().Destruct(destructor1).Run();
var (name, ageInLong) = o.V().Destruct(destructor2).Run();
var (name, nickName, age) = o.V().Destruct(destructor3).Run();

// namespace for operation with collections
using Newbe.ObjectVisitor.Collections;

/**
 🚧collect properties into a dictionary
*/

var dic1 = o.V().CollectAsDictionary().Run();
// quick style for above
var dic1 = o.V().ToDictionary();

/**
 🚧apply value from a dictionary to object
*/
o.V().ApplyFromDictionary(dic).Run();
// quick style for above
o.V().FromDictionary(dic);


// namespace for data validation
using Newbe.ObjectVisitor.Validation;

// 🚧create rule to validation
var rule = ValidateRule<Yueluo>
    .GetBuilder()
    .Property(x=>x.Name).Required().Length(2,10)
    .Property(x=>x.Age).Range(0, int.MaxValue)
    .Property(x=>x.Password).Validate(value=>ValidatePassword(value))
    .Property(x=>x.Level).Validate(value=>value + 1 >= 0)
    .Build();

o.V().Validate(rule).Run();
o.Validate(rule);


// 🚧validate data in flunet api
// attribute-based enabled by default
o.V().Validate(v=>
    v
     .Property(x=>x.Name).Required().Length(2,10)
     .Property(x=>x.Age).Range(0, int.MaxValue)
     .Property(x=>x.Password).Validate(value=>ValidatePassword(value))
     .Property(x=>x.Level).Validate(value=>value + 1 >= 0)
).Run();

// 🚧suppending attribute-based validation
o.V().SuppendAttributeValidation()
    .Validate(v=>
        v
        .Property(x=>x.Name).Required().Length(2,10)
        .Property(x=>x.Age).Range(0, int.MaxValue)
        .Property(x=>x.Password).Validate(value=>ValidatePassword(value))
        .Property(x=>x.Level).Validate(value=>value + 1 >= 0)
).Run();

// 🚧suppending sub-object validation
// validate whole object
o.V().SuppendSubObject()
    .SuppendAttributeValidation()
    .Validate(v=>
        v
        .Validate(x=>x.NewPassword == x.OldPassword)
        .Validate(x=>ValidateFormDb(x))
        .Property(x=>x.Name).Required().Length(2,10)
        .Property(x=>x.Age).Range(0, int.MaxValue)
        .Property(x=>x.Age).If(x=>x.Name == "123").Range(0, int.MaxValue)
        .Property(x=>x.Password).Validate(value=>ValidatePassword(value))
        .Property(x=>x.Level).Validate(value=>value + 1 >= 0)
).Run();

// namespace for Task
using Newbe.ObjectVisitor.Task;

// 🚧async way
await o.V().ForEachAsync((context)=>{}).RunAsync();

// 🚧controlling concurrency
await o.V().ForEachAsync((context)=>{}).WhenAsync(tasks=>Task.WhenAll(tasks)).RunAsync();

// namespace for Microsoft.Extensions.DependencyInjection
using Newbe.ObjectVistory.DepencyInjection;

// 🚧inject services to the properties of this object
this.V().ForEach(context=>this.ServiceProvider.GetService(context.PropertyInfo.PorpertyType)).Run();

// 🚧quick style for above
this.V().PropertyInject(this.ServiceProvider);

```
