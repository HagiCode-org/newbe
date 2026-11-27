---
date: 2020-11-08
title: Newbe.ObjectVisitor 样例1
tags:
  - Newbe.ObjectVisitor
---

我们增加了一些可以使用该库实现功能的场景和做法说明。

<!-- more -->

## 将数据库链接字符串转型为数据模型，或者将数据模型格式化为链接字符串。

```cs
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using FluentAssertions;
using NUnit.Framework;

namespace Newbe.ObjectVisitor.Tests
{
    public class DataConnectionModelTest
    {
        public const string ConnectionStringValue =
            "Host=www.newbe.pro;Port=36524;Username=newbe36524;Password=newbe.pro;";

        [Test]
        public void JoinToString()
        {
            var model = new DataConnectionModel
            {
                Host = "www.newbe.pro",
                Port = 36524,
                Username = "newbe36524",
                Password = "newbe.pro",
            };
            var connectionString = model.ToString();

            connectionString.Should().Be(ConnectionStringValue);
        }

        [Test]
        public void BuildFromString()
        {
            var model = DataConnectionModel.FromString(ConnectionStringValue);
            var expected = new DataConnectionModel
            {
                Host = "www.newbe.pro",
                Port = 36524,
                Username = "newbe36524",
                Password = "newbe.pro",
            };
            model.Should().BeEquivalentTo(expected);
        }


        public class DataConnectionModel
        {
            public string Host { get; set; } = null!;
            public ushort? Port { get; set; } = null!;
            public string Username { get; set; } = null!;
            public string Password { get; set; } = null!;
            public int? MaxPoolSize { get; set; } = null!;

            private static readonly ICachedObjectVisitor<DataConnectionModel, StringBuilder> ConnectionStringBuilder =
                default(DataConnectionModel)!
                    .V()
                    .WithExtendObject<DataConnectionModel, StringBuilder>()
                    .ForEach((name, value, sb) => AppendValueIfNotNull(name, value, sb))
                    .Cache();

            private static void AppendValueIfNotNull(string name, object? value, StringBuilder sb)
            {
                if (value != null)
                {
                    sb.Append($"{name}={value};");
                }
            }

            public override string ToString()
            {
                var sb = new StringBuilder();
                ConnectionStringBuilder.Run(this, sb);
                return sb.ToString();
            }

            private static readonly ICachedObjectVisitor<DataConnectionModel, Dictionary<string, string>>
                ConnectionStringConstructor
                    =
                    default(DataConnectionModel)!
                        .V()
                        .WithExtendObject<DataConnectionModel, Dictionary<string, string>>()
                        .ForEach(context => SetValueIfFound(context))
                        .Cache();

            private static void SetValueIfFound(
                IObjectVisitorContext<DataConnectionModel, Dictionary<string, string>, object> c)
            {
                if (c.ExtendObject.TryGetValue(c.Name, out var stringValue))
                {
                    TypeConverter conv = TypeDescriptor.GetConverter(c.PropertyInfo.PropertyType);
                    c.Value = conv.ConvertFrom(stringValue)!;
                }
            }

            public static DataConnectionModel FromString(string connectionString)
            {
                var dic = connectionString.Split(';')
                    .Where(x => !string.IsNullOrEmpty(x))
                    .Select(x => x.Split('='))
                    .ToDictionary(x => x[0], x => x[1]);
                var re = new DataConnectionModel();
                ConnectionStringConstructor.Run(re, dic);
                return re;
            }
        }
    }
}
```

## 将对象中满足手机号码格式的字段替换为密文，避免敏感信息输出。

```cs
using System.Text.RegularExpressions;
using FluentAssertions;
using NUnit.Framework;

namespace Newbe.ObjectVisitor.Tests
{
    public class ChangePasswordTest
    {
        [Test]
        public void CoverSensitiveDataTest()
        {
            // here is a model
            var userModel = new UserModel
            {
                Username = "newbe36524",
                Password = "newbe.pro",
                Phone = "12345678901"
            };

            // create a data visitor to cover sensitive data
            var visitor = userModel.V()
                .ForEach<UserModel, string>(x => CoverSensitiveData(x))
                .Cache();

            visitor.Run(userModel);

            var expected = new UserModel
            {
                Username = "newbe36524",
                Password = "***",
                Phone = "123****8901",
            };
            userModel.Should().BeEquivalentTo(expected);
        }

        private void CoverSensitiveData(IObjectVisitorContext<UserModel, string> c)
        {
            var value = c.Value;
            if (!string.IsNullOrEmpty(value))
            {
                c.Value = Regex.Replace(value, "(\\d{3})\\d{4}(\\d{4})", "$1****$2");
            }

            if (c.Name == nameof(UserModel.Password))
            {
                c.Value = "***";
            }
        }

        public class UserModel
        {
            public string Username { get; set; } = null!;
            public string Phone { get; set; } = null!;
            public string Password { get; set; } = null!;
        }
    }
}
```

## 将实现了 `IEnumerable<int>` 的所有属性求和。

```cs
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using NUnit.Framework;

namespace Newbe.ObjectVisitor.Tests
{
    public class EnumerableTest
    {
        [Test]
        public void NameAndValue()
        {
            var model = new TestModel
            {
                List1 = new[] {1},
                List2 = new[] {2},
                List3 = new List<int> {3},
                List4 = new HashSet<int> {4}
            };
            var sumBag = new SumBag();
            var visitor = model.V()
                .WithExtendObject(sumBag)
                .ForEach<TestModel, SumBag, IEnumerable<int>>((name, value, bag) => Sum(bag, value),
                    x => x.IsOrImplOf<IEnumerable<int>>())
                .Cache();
            visitor.Run(model, sumBag);
            sumBag.Sum.Should().Be(10);
        }

        private static void Sum(SumBag bag, IEnumerable<int> data)
        {
            bag.Sum += data.Sum();
        }

        public class SumBag
        {
            public int Sum { get; set; }
        }

        public class TestModel
        {
            public int[] List1 { get; set; } = null!;
            public IEnumerable<int> List2 { get; set; } = null!;
            public List<int> List3 { get; set; } = null!;
            public HashSet<int> List4 { get; set; } = null!;
        }
    }
}
```

<!-- md Footer-Newbe-ObjectVisitor.md -->
