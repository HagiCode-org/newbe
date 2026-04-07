---
date: 2018-09-25
title: 生命周期控制
tags:
 - 教程
 - C#
 - 依赖注入
 - Autofac
 - 生命周期控制
 - LifetimeScope
---

在使用依赖注入的过程当中，除了应用设计模式注意代码的变化隔离之外，另外一个重要的内容就是**生命周期控制**。

<!-- more -->

## 每次获取都是新的实例

前文中用到的方式都是这样的效果。在容器中每次获取同一个接口的实现，每次获取到的都是不同的实例。读者可以翻阅一下先前的示例代码回顾一下。

## 单例模式

**单例模式**也是一种常见的设计模式，这种设计模式。主要是为了解决某些特定需求时不希望特定的实例过多，而采用单个实例的设计模式。

在C#之中，最为容易理解的一种单例模式的应用便是**静态成员**，这点显而易见，以下获取系统时间的代码。便是一种单例模式。

```csharp
using System;
using System.Threading;

namespace Use_Dependency_Injection_With_Lifetime_Scope_Control
{
    public static class Demo1
    {
        public static void Run()
        {
            Console.WriteLine($"第一次获取时间：{DateTime.Now}");
            Thread.Sleep(1000);
            Console.WriteLine($"第二次获取时间：{DateTime.Now}");
            Thread.Sleep(1000);
            Console.WriteLine($"第三次获取时间：{DateTime.Now}");
        }
    }
}

```

每隔一秒钟获取一次系统时间。`DateTime.Now`是DateTime类型提供的静态属性。在C#语言之中这可以被看做一种单例模式。

但是，存在一个问题，那就是单元测试的可行性。简单来说，这段代码的运行结果会随着时间的变化而变化，每次运行的结果都不相同，这样通常来说是**不可测的**。因此，应用依赖注入进行一下改造。

```csharp
using Autofac;
using System;
using System.Threading;

namespace Use_Dependency_Injection_With_Lifetime_Scope_Control
{
    public static class Demo2
    {
        public static void Run()
        {
            var cb = new ContainerBuilder();
            cb.RegisterType<StaticClockByOneTime>()
                .As<IClock>()
                .SingleInstance();
            var container = cb.Build();
            var clock = container.Resolve<IClock>();
            Console.WriteLine($"第一次获取时间：{clock.Now}");
            Thread.Sleep(1000);
            clock = container.Resolve<IClock>();
            Console.WriteLine($"第二次获取时间：{clock.Now}");
            Thread.Sleep(1000);
            clock = container.Resolve<IClock>();
            Console.WriteLine($"第三次获取时间：{clock.Now}");
        }

        public interface IClock
        {
            /// <summary>
            /// 获取当前系统时间
            /// </summary>
            DateTime Now { get; }
        }

        public class StaticClockByOneTime : IClock
        {
            private DateTime _firstTime = DateTime.MinValue;
            public DateTime Now
            {
                get
                {
                    if (_firstTime == DateTime.MinValue)
                    {
                        _firstTime = DateTime.Now;
                    }

                    return _firstTime;
                }
            }
        }
    }
}


```

简要分析。通过改造之后引入了新的接口获取当前系统时间。由于接口的存在，我们可以替换接口的实现。

此处使用了一个有趣的实现`StaticClockByOneTime`。简单来说，这个实例如果获取过一次时间之后，时间就不会变化。

为这个特性作支撑的，便是`SingleInstance`这个方法。此方法将`StaticClockByOneTime`注册时标记为了“单例”。因此，从容器中获取`IClock`实例时始终得到的是同一个实例。就这样，便即实现了单例，又实现了可以自主控制时间的需求。

> 读者可以将上文代码中的`SingleInstance`代码去掉来体验单例和非单例运行结果的区别。

## 生命周期内单例

上文的单例是一种全局性的单例配置。只要容器建立起来，在容器内就是完全单例的。但在实际的应用场景中可能需要在某个特定生命周期内的单例，也可以成为局部单例。

### 业务需求

以下实例代码都将完成如下定义的一个业务场景：从A账号转账给B账号，转账数额为C，则A账号减少数额C，B账号增加数额C。

### 有关联的输出日志

转账影响了两个账号余额，现在考虑输出两条余额更新的日志，并且在日志中需要包含相同的转账流水号。

```csharp
using Autofac;
using System;
using System.Collections.Generic;

namespace Use_Dependency_Injection_With_Lifetime_Scope_Control
{
    public static class Demo3
    {
        public static void Run()
        {
            var cb = new ContainerBuilder();
            cb.RegisterType<AccountBll>().As<IAccountBll>();
            cb.RegisterType<AccountDal>().As<IAccountDal>();
            cb.RegisterType<ConsoleLogger>().As<ILogger>()
                .InstancePerLifetimeScope();
            var container = cb.Build();

            using (var beginLifetimeScope = container.BeginLifetimeScope())
            {
                var accountBll = beginLifetimeScope.Resolve<IAccountBll>();
                accountBll.Transfer("yueluo", "newbe", 333);
                accountBll.Transfer("yueluo", "newbe", 333);
            }
        }

        public interface ILogger
        {
            void BeginScope(string scopeTag);
            void Log(string message);
        }

        public class ConsoleLogger : ILogger
        {
            private string _currenctScopeTag;

            public void BeginScope(string scopeTag)
            {
                _currenctScopeTag = scopeTag;
            }

            public void Log(string message)
            {
                Console.WriteLine(string.IsNullOrEmpty(_currenctScopeTag)
                    ? $"输出日志：{message}"
                    : $"输出日志：{message}[scope:{_currenctScopeTag}]");
            }
        }

        public interface IAccountBll
        {
            /// <summary>
            /// 转账
            /// </summary>
            /// <param name="fromAccountId">来源账号Id</param>
            /// <param name="toAccountId">目标账号Id</param>
            /// <param name="amount">转账数额</param>
            void Transfer(string fromAccountId, string toAccountId, decimal amount);
        }

        public class AccountBll : IAccountBll
        {
            private readonly ILogger _logger;
            private readonly IAccountDal _accountDal;

            public AccountBll(
                ILogger logger,
                IAccountDal accountDal)
            {
                _logger = logger;
                _accountDal = accountDal;
            }

            public void Transfer(string fromAccountId, string toAccountId, decimal amount)
            {
                _logger.BeginScope(Guid.NewGuid().ToString());
                var fromAmount = _accountDal.GetBalance(fromAccountId);
                var toAmount = _accountDal.GetBalance(toAccountId);
                fromAmount -= amount;
                toAmount += amount;
                _accountDal.UpdateBalance(fromAccountId, fromAmount);
                _accountDal.UpdateBalance(toAccountId, toAmount);
            }
        }

        public interface IAccountDal
        {
            /// <summary>
            /// 获取账户的余额
            /// </summary>
            /// <param name="id"></param>
            /// <returns></returns>
            decimal GetBalance(string id);

            /// <summary>
            /// 更新账户的余额
            /// </summary>
            /// <param name="id"></param>
            /// <param name="balance"></param>
            void UpdateBalance(string id, decimal balance);
        }

        public class AccountDal : IAccountDal
        {
            private readonly ILogger _logger;

            public AccountDal(
                ILogger logger)
            {
                _logger = logger;
            }

            private readonly Dictionary<string, decimal> _accounts = new Dictionary<string, decimal>
            {
                {"newbe",1000},
                {"yueluo",666},
            };

            public decimal GetBalance(string id)
            {
                return _accounts.TryGetValue(id, out var balance) ? balance : 0;
            }

            public void UpdateBalance(string id, decimal balance)
            {
                _logger.Log($"更新了 {id} 的余额为 {balance}");
                _accounts[id] = balance;
            }
        }
    }
}

```

简要分析。以上代码的关键点：

1. 在注册`ILogger`时，注册为了生命周期内单例。
2. 在获取`IAccountBll`时，开启了一个生命周期，那么在这个生命周期内获取的`ILogger`实例都是同一个。
3. 在`IAccountBll`内使用`ILogger`记录了转账流水号。

读者可以尝试将`InstancePerLifetimeScope`去除，观察运行效果的不同。

### 使用相同的数据库事务

转账从现有的代码结构而言，需要开启数据库事务才能够确保在数据入库时是无误的。从**三层结构**的角度来说，通常需要调用多个具有修改数据库数据功能的DAL方法时，将会开启事务从而确保这些DAL方法的执行是正确的。

为了实现这个特性，首先准备一些基础的类。

```csharp
using System;
using System.Data;

namespace Use_Dependency_Injection_With_Lifetime_Scope_Control
{
    /// <summary>
    /// 能够直接执行语句的数据库链接
    /// </summary>
    public interface IExecuteSqlDbConnection : IDbConnection
    {
        /// <summary>
        /// 执行数据库语句
        /// </summary>
        /// <param name="sql"></param>
        /// <param name="ps"></param>
        /// <param name="dbTransaction"></param>
        void ExecuteSql(string sql, object[] ps, IDbTransaction dbTransaction = null);
    }

    /// <summary>
    /// 只会向控制台输出内容的数据库连接
    /// </summary>
    public class ConsoleDbConnection : IExecuteSqlDbConnection
    {
        public delegate ConsoleDbConnection Factory();

        public void Dispose()
        {
            Console.WriteLine("数据库连接：释放");
        }

        public IDbTransaction BeginTransaction()
        {
            return new ConsoleOutDbTransaction(this, IsolationLevel.Unspecified);
        }

        public IDbTransaction BeginTransaction(IsolationLevel il)
        {
            return new ConsoleOutDbTransaction(this, il);
        }

        public void Close()
        {
            Console.WriteLine("数据库连接：关闭");
        }

        public void ChangeDatabase(string databaseName)
        {
            throw new NotSupportedException();
        }

        public IDbCommand CreateCommand()
        {
            throw new NotSupportedException();
        }

        public void Open()
        {
            throw new NotSupportedException();
        }

        public string ConnectionString { get; set; }

        public int ConnectionTimeout
        {
            get { throw new NotSupportedException(); }
        }

        public string Database
        {
            get { throw new NotSupportedException(); }
        }

        public ConnectionState State
        {
            get { throw new NotSupportedException(); }
        }

        public void ExecuteSql(string sql, object[] ps, IDbTransaction dbTransaction = null)
        {
            if (dbTransaction == null)
            {
                Console.WriteLine($"无事务执行：{string.Format(sql, ps)}");
            }
            else
            {
                Console.WriteLine($"有事务执行：{string.Format(sql, ps)}");
            }
        }
    }

    /// <summary>
    /// 只会向控制台输出内容的事务
    /// </summary>
    public class ConsoleOutDbTransaction : IDbTransaction
    {
        public ConsoleOutDbTransaction(IDbConnection connection, IsolationLevel isolationLevel)
        {
            Connection = connection;
            IsolationLevel = isolationLevel;
        }

        public void Dispose()
        {
            Console.WriteLine("事务：释放");
        }

        public void Commit()
        {
            Console.WriteLine("事务：提交");
        }

        public void Rollback()
        {
            Console.WriteLine("事务：回滚");
        }

        public IDbConnection Connection { get; }
        public IsolationLevel IsolationLevel { get; }
    }
}

```

具备了数据库链接和事务的基础类后，假设我们不采用生命周期控制的方案。那么一种实现方案如下

```csharp
using Autofac;
using System;
using System.Collections.Generic;
using System.Data;

namespace Use_Dependency_Injection_With_Lifetime_Scope_Control
{
    public static class Demo4
    {
        public static void Run()
        {
            var cb = new ContainerBuilder();
            cb.RegisterType<AccountBll>().As<IAccountBll>();
            cb.RegisterType<AccountDal>().As<IAccountDal>();
            cb.RegisterType<DbFactory>().As<IDbFactory>();
            cb.RegisterType<ConsoleDbConnection>().AsSelf();
            var container = cb.Build();

            using (var beginLifetimeScope = container.BeginLifetimeScope())
            {
                var accountBll = beginLifetimeScope.Resolve<IAccountBll>();
                accountBll.Transfer("yueluo", "newbe", 333);
            }
        }

        public interface IDbFactory
        {
            IExecuteSqlDbConnection CreateDbConnection();
        }

        public class DbFactory : IDbFactory
        {
            private readonly ConsoleDbConnection.Factory _factory;

            public DbFactory(
                ConsoleDbConnection.Factory factory)
            {
                this._factory = factory;
            }

            public IExecuteSqlDbConnection CreateDbConnection()
            {
                return _factory();
            }
        }

        public interface IAccountBll
        {
            void Transfer(string fromAccountId, string toAccountId, decimal amount);
        }

        public class AccountBll : IAccountBll
        {
            private readonly IDbFactory _dbFactory;
            private readonly IAccountDal _accountDal;

            public AccountBll(
                IDbFactory dbFactory,
                IAccountDal accountDal)
            {
                _dbFactory = dbFactory;
                _accountDal = accountDal;
            }

            public void Transfer(string fromAccountId, string toAccountId, decimal amount)
            {
                using (var dbConnection = _dbFactory.CreateDbConnection())
                {
                    using (var transaction = dbConnection.BeginTransaction())
                    {
                        try
                        {
                            var fromAmount = _accountDal.GetBalance(fromAccountId);
                            var toAmount = _accountDal.GetBalance(toAccountId);
                            fromAmount -= amount;
                            toAmount += amount;
                            _accountDal.UpdateBalance(fromAccountId, fromAmount, dbConnection, transaction);
                            _accountDal.UpdateBalance(toAccountId, toAmount, dbConnection, transaction);
                            transaction.Commit();
                        }
                        catch (Exception)
                        {
                            transaction.Rollback();
                            throw;
                        }
                    }
                }
            }
        }

        public interface IAccountDal
        {
            /// <summary>
            /// 获取账户的余额
            /// </summary>
            /// <param name="id"></param>
            /// <returns></returns>
            decimal GetBalance(string id);

            /// <summary>
            /// 更新账户的余额
            /// </summary>
            /// <param name="id"></param>
            /// <param name="balance"></param>
            /// <param name="dbConnection"></param>
            /// <param name="dbTransaction"></param>
            void UpdateBalance(string id, decimal balance, IExecuteSqlDbConnection dbConnection = null, IDbTransaction dbTransaction = null);
        }

        public class AccountDal : IAccountDal
        {
            private readonly IDbFactory _dbFactory;

            public AccountDal(
                IDbFactory dbFactory)
            {
                _dbFactory = dbFactory;
            }

            private readonly Dictionary<string, decimal> _accounts = new Dictionary<string, decimal>
            {
                {"newbe",1000},
                {"yueluo",666},
            };

            public decimal GetBalance(string id)
            {
                return _accounts.TryGetValue(id, out var balance) ? balance : 0;
            }

            public void UpdateBalance(string id, decimal balance, IExecuteSqlDbConnection dbConnection = null, IDbTransaction dbTransaction = null)
            {
                if (dbConnection == null)
                {
                    dbConnection = _dbFactory.CreateDbConnection();
                    dbConnection.ExecuteSql("更新语句：更新 {0} 余额为 {1}", new object[] { id, balance });
                    _accounts[id] = balance;

                }
                else
                {
                    dbConnection.ExecuteSql("更新语句：更新 {0} 余额为 {1}", new object[] { id, balance }, dbTransaction);
                    _accounts[id] = balance;
                }

            }
        }
    }
}

```

简要分析，上例代码中关键点：

`IAccountDal.UpdateBalance`支持传入数据库链接和事务对象，这样在`IAccountBll`既可以开启事务确保方法在一个事务内执行，也可以不开启事务，进行分事务执行。

这样做的缺点也比较明显。DAL层实现比较麻烦。

假如参照上文中“日志”的处理方案，将数据库链接和事务作为**生命周期内单例**来控制，实现起来将更加方便。

```csharp
using Autofac;
using System;
using System.Collections.Generic;
using System.Data;

namespace Use_Dependency_Injection_With_Lifetime_Scope_Control
{
    public static class Demo5
    {
        public static void Run()
        {
            var cb = new ContainerBuilder();
            cb.RegisterType<AccountBll>().As<IAccountBll>();
            cb.RegisterType<AccountDal>().As<IAccountDal>();
            cb.RegisterType<DbFactory>().As<IDbFactory>()
                .InstancePerLifetimeScope();
            cb.RegisterType<ConsoleDbConnection>().AsSelf();
            var container = cb.Build();

            using (var beginLifetimeScope = container.BeginLifetimeScope())
            {
                var accountBll = beginLifetimeScope.Resolve<IAccountBll>();
                accountBll.Transfer("yueluo", "newbe", 333);
            }
        }

        public interface IDbFactory
        {
            IExecuteSqlDbConnection CreateDbConnection();
        }

        public class DbFactory : IDbFactory
        {
            private readonly ConsoleDbConnection.Factory _factory;

            public DbFactory(
                ConsoleDbConnection.Factory factory)
            {
                this._factory = factory;
            }

            private IExecuteSqlDbConnection _connection;
            public IExecuteSqlDbConnection CreateDbConnection()
            {
                return _connection ?? (_connection = new TransactionOnceDbConnection(_factory()));
            }
        }

        /// <summary>
        /// 除非上次事务结束，否则只会开启一次事务的链接
        /// </summary>
        public class TransactionOnceDbConnection : IExecuteSqlDbConnection
        {
            private readonly IExecuteSqlDbConnection _innerConnection;
            private IDbTransaction _innerDbTransaction;
            public TransactionOnceDbConnection(
                IExecuteSqlDbConnection innerConnection)
            {
                _innerConnection = innerConnection;
            }

            public void Dispose()
            {
                _innerConnection.Dispose();
            }

            public IDbTransaction BeginTransaction()
            {
                if (_innerDbTransaction != null)
                {
                    return _innerDbTransaction;
                }
                return _innerDbTransaction = _innerConnection.BeginTransaction();
            }

            public IDbTransaction BeginTransaction(IsolationLevel il)
            {
                if (_innerDbTransaction != null)
                {
                    return _innerDbTransaction;
                }
                return _innerDbTransaction = _innerConnection.BeginTransaction(il);
            }

            public void Close()
            {
                _innerConnection.Close();
            }

            public void ChangeDatabase(string databaseName)
            {
                _innerConnection.ChangeDatabase(databaseName);
            }

            public IDbCommand CreateCommand()
            {
                return _innerConnection.CreateCommand();
            }

            public void Open()
            {
                _innerConnection.Open();
            }

            public string ConnectionString
            {
                get => _innerConnection.ConnectionString;
                set => _innerConnection.ConnectionString = value;
            }

            public int ConnectionTimeout => _innerConnection.ConnectionTimeout;

            public string Database => _innerConnection.Database;

            public ConnectionState State => _innerConnection.State;
            public void ExecuteSql(string sql, object[] ps, IDbTransaction dbTransaction = null)
            {
                _innerConnection.ExecuteSql(sql, ps, _innerDbTransaction ?? dbTransaction);
            }
        }

        public interface IAccountBll
        {
            void Transfer(string fromAccountId, string toAccountId, decimal amount);
        }

        public class AccountBll : IAccountBll
        {
            private readonly IDbFactory _dbFactory;
            private readonly IAccountDal _accountDal;

            public AccountBll(
                IDbFactory dbFactory,
                IAccountDal accountDal)
            {
                _dbFactory = dbFactory;
                _accountDal = accountDal;
            }

            public void Transfer(string fromAccountId, string toAccountId, decimal amount)
            {
                using (var dbConnection = _dbFactory.CreateDbConnection())
                {
                    using (var transaction = dbConnection.BeginTransaction())
                    {
                        try
                        {
                            var fromAmount = _accountDal.GetBalance(fromAccountId);
                            var toAmount = _accountDal.GetBalance(toAccountId);
                            fromAmount -= amount;
                            toAmount += amount;
                            _accountDal.UpdateBalance(fromAccountId, fromAmount);
                            _accountDal.UpdateBalance(toAccountId, toAmount);
                            transaction.Commit();
                        }
                        catch (Exception)
                        {
                            transaction.Rollback();
                            throw;
                        }
                    }
                }
            }
        }

        public interface IAccountDal
        {
            /// <summary>
            /// 获取账户的余额
            /// </summary>
            /// <param name="id"></param>
            /// <returns></returns>
            decimal GetBalance(string id);

            /// <summary>
            /// 更新账户的余额
            /// </summary>
            /// <param name="id"></param>
            /// <param name="balance"></param>
            void UpdateBalance(string id, decimal balance);
        }

        public class AccountDal : IAccountDal
        {
            private readonly IDbFactory _dbFactory;

            public AccountDal(
                IDbFactory dbFactory)
            {
                this._dbFactory = dbFactory;
            }

            private readonly Dictionary<string, decimal> _accounts = new Dictionary<string, decimal>
            {
                {"newbe",1000},
                {"yueluo",666},
            };

            public decimal GetBalance(string id)
            {
                return _accounts.TryGetValue(id, out var balance) ? balance : 0;
            }

            public void UpdateBalance(string id, decimal balance)
            {
                var dbConnection = _dbFactory.CreateDbConnection();
                dbConnection.ExecuteSql("更新语句：更新 {0} 余额为 {1}", new object[] { id, balance });
                _accounts[id] = balance;
            }
        }
    }
}

```

简要分析，上例代码关键点：

1. 通过[装饰模式](https://baike.baidu.com/item/%E8%A3%85%E9%A5%B0%E6%A8%A1%E5%BC%8F/10158540?fr=aladdin)实现了`TransactionOnceDbConnection`，支持一次开启事务之后，后续操作都使用相同事务。
2. 修改了`DbFactory`，实现一次开启链接之后，就是用相同链接的特性。
3. 将`IDbFactory`标记为生命周期内单例。
4. 在使用`IAccountBll`时，开启了一个生命周期。

这样改造之后，DAL实现时，就不需要关系事务到底是否开启没有，只需要直接执行相关操作即可。

## 总结

在使用依赖注入的时候，生命周期控制是一个相当重要的课题。读者需要在实践中注意分析。

以上示例代码都是基于较为简单的业务场景与基础代码实现，实际操作中不一定是如此，读者需要在实践中注意分析。

本文由于采用了Autofac作为主要的依赖注入框架，因此生命周期控制方式也采用了框架相关的函数。实际上，绝大多数框都提供了以上提及的生命周期控制方式。在实践中，读者可以找寻相关框架的文档，了解如何应用框架进行生命周期控制。

关于Autofac更加深入的生命周期控制：[参考链接](https://autofac.readthedocs.io/en/latest/lifetime/index.html)。

至此，该系列文章也已完结，希望读者能够从中获益。

[本文示例代码地址](https://github.com/newbe36524/Newbe.Demo/tree/master/src/BlogDemos/Use-Dependency-Injection-In-CSharp/Use-Dependency-Injection-With-Lifetime-Scope-Control)

<!-- md Nav-Use-Dependency-Injection.md -->
