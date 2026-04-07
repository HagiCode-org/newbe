---
date: 2021-10-23
title: 产品说，我只需要一个有亿点复杂的查询界面
tags:
  - Newbe.ObjectVisitor
  - 表达式树
  - expression tree
  - 教程
  - dotnet
---

有的时候，你需要动态构建一个比较复杂的查询条件，传入数据库中进行查询。而条件本身可能来自前端请求或者配置文件。那么这个时候，表达式树，就可以帮助到你。本文我们将通过几个简短的示例来了解如何完成这些操作。

<!-- more -->

## 你也可能接到过这些需求

![从模型进行查询](/images/20211023-001.png)

![基于配置查询](/images/20211023-002.png)

今天我们看看表达式树如何实现这些需求。

## 一切都还要从盘古开天开始说起

以下是一个简单的单元测试用例。接下来，我们将这个测试用例改的面目全非。

```cs
[Test]
public void Normal()
{
    var re = Enumerable.Range(0, 10).AsQueryable() // 0-9
        .Where(x => x >= 1 && x < 5).ToList(); // 1 2 3 4
    var expectation = Enumerable.Range(1, 4); // 1 2 3 4
    re.Should().BeEquivalentTo(expectation);
}
```

## 很久很久以前天和地还没有分开

由于是 Queryable 的关系，所以Where当中的其实是一个表达式，那么我们把它单独定义出来，顺便水一下文章的长度。

```cs
[Test]
public void Expression00()
{
    Expression<Func<int, bool>> filter = x => x >= 1 && x < 5;
    var re = Enumerable.Range(0, 10).AsQueryable()
        .Where(filter).ToList();
    var expectation = Enumerable.Range(1, 4);
    re.Should().BeEquivalentTo(expectation);
}
```

## 有个叫盘古的巨人在这混沌之中

Expression 右侧是一个 Lambda ，所以可以捕获上下文中的变量。

这样你便可以把 minValue 和 maxValue 单独定义出来。

于是乎你可以从其他地方来获取 minValue 和 maxValue 来改变 filter。

```cs
[Test]
public void Expression01()
{
    var minValue = 1;
    var maxValue = 5;
    Expression<Func<int, bool>> filter = x => x >= minValue && x < maxValue;
    var re = Enumerable.Range(0, 10).AsQueryable()
        .Where(filter).ToList();
    var expectation = Enumerable.Range(1, 4);
    re.Should().BeEquivalentTo(expectation);
}
```

## 他睡了一万八千年也都不用上班

那既然这样，我们也可以使用一个方法来创建 Expression。

这个方法，实际上就可以认为是这个 Expression 的工厂方法。

```cs
[Test]
public void Expression02()
{
    var filter = CreateFilter(1, 5);
    var re = Enumerable.Range(0, 10).AsQueryable()
        .Where(filter).ToList();
    var expectation = Enumerable.Range(1, 4);
    re.Should().BeEquivalentTo(expectation);

    Expression<Func<int, bool>> CreateFilter(int minValue, int maxValue)
    {
        return x => x >= minValue && x < maxValue;
    }
}
```

## 有一天盘古突然醒了但天还没亮

那可以使用 minValue 和 maxValue 作为参数来制作工厂方法，那么用委托当然也可以。

于是，我们可以把左边和右边分别定义成两个 Func，从而由外部来决定左右具体的比较方式。

```cs
[Test]
public void Expression03()
{
    var filter = CreateFilter(x => x >= 1, x => x < 5);
    var re = Enumerable.Range(0, 10).AsQueryable()
        .Where(filter).ToList();
    var expectation = Enumerable.Range(1, 4);
    re.Should().BeEquivalentTo(expectation);

    Expression<Func<int, bool>> CreateFilter(Func<int, bool> leftFunc, Func<int, bool> rightFunc)
    {
        return x => leftFunc.Invoke(x) && rightFunc.Invoke(x);
    }
}
```

## 他就抡起大斧头朝前方猛劈过去

实际上，左右两个不仅仅是两个Func，其实也可以直接是两个表达式。

不过稍微有点不同的是，表达式的合并需要用 Expression 类型中的相关方法创建。

我们可以发现，调用的地方这次其实没有任何改变，因为 Lambda 既可以隐式转换为 Func 也可以隐式转换为 Expression。

每个方法的意思可以从注释中看出。

```cs
[Test]
public void Expression04()
{
    var filter = CreateFilter(x => x >= 1, x => x < 5);
    var re = Enumerable.Range(0, 10).AsQueryable()
        .Where(filter).ToList();
    var expectation = Enumerable.Range(1, 4);
    re.Should().BeEquivalentTo(expectation);

    Expression<Func<int, bool>> CreateFilter(Expression<Func<int, bool>> leftFunc,
        Expression<Func<int, bool>> rightFunc)
    {
        // x
        var pExp = Expression.Parameter(typeof(int), "x");
        // (a => leftFunc(a))(x)
        var leftExp = Expression.Invoke(leftFunc, pExp);
        // (a => rightFunc(a))(x)
        var rightExp = Expression.Invoke(rightFunc, pExp);
        // (a => leftFunc(a))(x) && (a => rightFunc(a))(x)
        var bodyExp = Expression.AndAlso(leftExp, rightExp);
        // x => (a => leftFunc(a))(x) && (a => rightFunc(a))(x)
        var resultExp = Expression.Lambda<Func<int, bool>>(bodyExp, pExp);
        return resultExp;
    }
}
```
## 只听枯叉一声黑暗渐渐地就分开

但是，上面的方法，其实可以在优化一下。避免对左右表达式的直接调用。

使用一个叫做 Unwrap 的方法，可以将 Lambda Expression 解构成只包含 Body 部分的表达式。

这是一个自定义的扩展方法，你可以通过 [ObjectVisitor](https://github.com/newbe36524/Newbe.ObjectVisitor) 来引入这个方法。

限于篇幅，我们此处不能展开谈 Unwrap 的实现。我们只需要关注和前一个示例中注释的不同即可。

```cs
[Test]
public void Expression05()
{
    var filter = CreateFilter(x => x >= 1, x => x < 5);
    var re = Enumerable.Range(0, 10).AsQueryable()
        .Where(filter).ToList();
    var expectation = Enumerable.Range(1, 4);
    re.Should().BeEquivalentTo(expectation);

    Expression<Func<int, bool>> CreateFilter(Expression<Func<int, bool>> leftFunc,
        Expression<Func<int, bool>> rightFunc)
    {
        // x
        var pExp = Expression.Parameter(typeof(int), "x");
        // leftFunc(x)
        var leftExp = leftFunc.Unwrap(pExp);
        // rightFunc(x)
        var rightExp = rightFunc.Unwrap(pExp);
        // leftFunc(x) && rightFunc(x)
        var bodyExp = Expression.AndAlso(leftExp, rightExp);
        // x => leftFunc(x) && rightFunc(x)
        var resultExp = Expression.Lambda<Func<int, bool>>(bodyExp, pExp);
        return resultExp;
    }
}
```
## 天和地分开后盘古怕它们还合并

我们可以再优化以下，把 CreateFilter 方法扩展为支持多个子表达式和可自定义子表达式的连接方式。

于是，我们就可以得到一个 JoinSubFilters 方法。

```cs
[Test]
public void Expression06()
{
    var filter = JoinSubFilters(Expression.AndAlso, x => x >= 1, x => x < 5);
    var re = Enumerable.Range(0, 10).AsQueryable()
        .Where(filter).ToList();
    var expectation = Enumerable.Range(1, 4);
    re.Should().BeEquivalentTo(expectation);

    Expression<Func<int, bool>> JoinSubFilters(Func<Expression, Expression, Expression> expJoiner,
        params Expression<Func<int, bool>>[] subFilters)
    {
        // x
        var pExp = Expression.Parameter(typeof(int), "x");
        var result = subFilters[0];
        foreach (var sub in subFilters[1..])
        {
            var leftExp = result.Unwrap(pExp);
            var rightExp = sub.Unwrap(pExp);
            var bodyExp = expJoiner(leftExp, rightExp);

            result = Expression.Lambda<Func<int, bool>>(bodyExp, pExp);
        }

        return result;
    }
}
```
## 他就头顶着天脚蹬着地不知多久

有了前面的经验，我们知道。其实`x => x >= 1`这个表达式可以通过一个工厂方法来创建。

所以，我们使用一个 CreateMinValueFilter 来创建这个表达式。

```cs
[Test]
public void Expression07()
{
    var filter = JoinSubFilters(Expression.AndAlso,
        CreateMinValueFilter(1),
        x => x < 5);
    var re = Enumerable.Range(0, 10).AsQueryable()
        .Where(filter).ToList();
    var expectation = Enumerable.Range(1, 4);
    re.Should().BeEquivalentTo(expectation);

    Expression<Func<int, bool>> CreateMinValueFilter(int minValue)
    {
        return x => x >= minValue;
    }

    Expression<Func<int, bool>> JoinSubFilters(Func<Expression, Expression, Expression> expJoiner,
        params Expression<Func<int, bool>>[] subFilters)
    {
        // x
        var pExp = Expression.Parameter(typeof(int), "x");
        var result = subFilters[0];
        foreach (var sub in subFilters[1..])
        {
            var leftExp = result.Unwrap(pExp);
            var rightExp = sub.Unwrap(pExp);
            var bodyExp = expJoiner(leftExp, rightExp);

            result = Expression.Lambda<Func<int, bool>>(bodyExp, pExp);
        }

        return result;
    }
}
```
## 盘古也累得倒下来变成山石河流

当然，可以只使用 Expression 相关的方法来创建`x => x >= 1`。

```cs
[Test]
public void Expression08()
{
    var filter = JoinSubFilters(Expression.AndAlso,
        CreateMinValueFilter(1),
        x => x < 5);
    var re = Enumerable.Range(0, 10).AsQueryable()
        .Where(filter).ToList();
    var expectation = Enumerable.Range(1, 4);
    re.Should().BeEquivalentTo(expectation);

    Expression<Func<int, bool>> CreateMinValueFilter(int minValue)
    {
        // x
        var pExp = Expression.Parameter(typeof(int), "x");
        // minValue
        var rightExp = Expression.Constant(minValue);
        // x >= minValue
        var bodyExp = Expression.GreaterThanOrEqual(pExp, rightExp);
        var result = Expression.Lambda<Func<int, bool>>(bodyExp, pExp);
        return result;
    }

    Expression<Func<int, bool>> JoinSubFilters(Func<Expression, Expression, Expression> expJoiner,
        params Expression<Func<int, bool>>[] subFilters)
    {
        // x
        var pExp = Expression.Parameter(typeof(int), "x");
        var result = subFilters[0];
        foreach (var sub in subFilters[1..])
        {
            var leftExp = result.Unwrap(pExp);
            var rightExp = sub.Unwrap(pExp);
            var bodyExp = expJoiner(leftExp, rightExp);

            result = Expression.Lambda<Func<int, bool>>(bodyExp, pExp);
        }

        return result;
    }
}
```
## 那么看来盘古也吃不了上班的苦

那既然都用了 Expression 来创建子表达式了，那就干脆再做一点点改进，把`x => x < 5`也做成从工厂方法获取。

```cs
[Test]
public void Expression09()
{
    var filter = JoinSubFilters(Expression.AndAlso,
        CreateValueCompareFilter(Expression.GreaterThanOrEqual, 1),
        CreateValueCompareFilter(Expression.LessThan, 5));
    var re = Enumerable.Range(0, 10).AsQueryable()
        .Where(filter).ToList();
    var expectation = Enumerable.Range(1, 4);
    re.Should().BeEquivalentTo(expectation);

    Expression<Func<int, bool>> CreateValueCompareFilter(Func<Expression, Expression, Expression> comparerFunc,
        int rightValue)
    {
        var pExp = Expression.Parameter(typeof(int), "x");
        var rightExp = Expression.Constant(rightValue);
        var bodyExp = comparerFunc(pExp, rightExp);
        var result = Expression.Lambda<Func<int, bool>>(bodyExp, pExp);
        return result;
    }

    Expression<Func<int, bool>> JoinSubFilters(Func<Expression, Expression, Expression> expJoiner,
        params Expression<Func<int, bool>>[] subFilters)
    {
        // x
        var pExp = Expression.Parameter(typeof(int), "x");
        var result = subFilters[0];
        foreach (var sub in subFilters[1..])
        {
            var leftExp = result.Unwrap(pExp);
            var rightExp = sub.Unwrap(pExp);
            var bodyExp = expJoiner(leftExp, rightExp);

            result = Expression.Lambda<Func<int, bool>>(bodyExp, pExp);
        }

        return result;
    }
}
```
## 所以如果可以不做这需求就别搞

最后，我们在把子表达式的创建通过一点点小技巧。通过外部参数来决定。就基本完成了一个多 And 的值比较查询条件的动态构建。

```cs
[Test]
public void Expression10()
{
    var config = new Dictionary<string, int>
    {
        { ">=", 1 },
        { "<", 5 }
    };
    var subFilters = config.Select(x => CreateValueCompareFilter(MapConfig(x.Key), x.Value)).ToArray();
    var filter = JoinSubFilters(Expression.AndAlso, subFilters);
    var re = Enumerable.Range(0, 10).AsQueryable()
        .Where(filter).ToList();
    var expectation = Enumerable.Range(1, 4);
    re.Should().BeEquivalentTo(expectation);

    Func<Expression, Expression, Expression> MapConfig(string op)
    {
        return op switch
        {
            ">=" => Expression.GreaterThanOrEqual,
            "<" => Expression.LessThan,
            _ => throw new ArgumentOutOfRangeException(nameof(op))
        };
    }

    Expression<Func<int, bool>> CreateValueCompareFilter(Func<Expression, Expression, Expression> comparerFunc,
        int rightValue)
    {
        var pExp = Expression.Parameter(typeof(int), "x");
        var rightExp = Expression.Constant(rightValue);
        var bodyExp = comparerFunc(pExp, rightExp);
        var result = Expression.Lambda<Func<int, bool>>(bodyExp, pExp);
        return result;
    }

    Expression<Func<int, bool>> JoinSubFilters(Func<Expression, Expression, Expression> expJoiner,
        params Expression<Func<int, bool>>[] subFilters)
    {
        // x
        var pExp = Expression.Parameter(typeof(int), "x");
        var result = subFilters[0];
        foreach (var sub in subFilters[1..])
        {
            var leftExp = result.Unwrap(pExp);
            var rightExp = sub.Unwrap(pExp);
            var bodyExp = expJoiner(leftExp, rightExp);

            result = Expression.Lambda<Func<int, bool>>(bodyExp, pExp);
        }

        return result;
    }
}
```


## 还要更多

如果逻辑关系更复杂，有多层嵌套像树形一样，比较方法也很多花样，甚至包含方法，怎么办？

可以参考以下示例：

https://github.com/newbe36524/Newbe.Demo/tree/main/src/BlogDemos/Newbe.ExpressionsTests/Newbe.ExpressionsTests/FilterFactory

如果你对此内容感兴趣，还可以浏览我之前录制的视频进行进一步了解：

- [戏精分享 C#表达式树，第一季 https://www.bilibili.com/video/BV15y4y1r7pK](https://www.bilibili.com/video/BV15y4y1r7pK)
- [戏精分享 C#表达式树，第二季 https://www.bilibili.com/video/BV1Mi4y1L7oR](https://www.bilibili.com/video/BV1Mi4y1L7oR)

你也可以参阅之前一篇入门：

[只要十步，你就可以应用表达式树来优化动态调用](./0017-Using-Expression-Tree-To-Build-Delegate)

或者看MSDN文档，我觉得你也可以有所收获:

https://docs.microsoft.com/dotnet/csharp/programming-guide/concepts/expression-trees/?WT.mc_id=DT-MVP-5004283

这篇相关的代码，可以通过以下地址得到：

https://github.com/newbe36524/Newbe.Demo/blob/main/src/BlogDemos/Newbe.ExpressionsTests/Newbe.ExpressionsTests/Examples/Z01SingleWhereTest.cs

如果你觉得本文不错，记得收藏、点赞、评论、转发。告诉我还想知道点什么哟。