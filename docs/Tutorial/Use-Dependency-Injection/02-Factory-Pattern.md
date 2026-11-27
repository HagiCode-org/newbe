---
date: 2018-09-24
title: 工厂模式和工厂方法模式
tags:
 - 教程
 - C#
 - 依赖注入
 - Autofac
 - 工厂模式
---

工厂模式和工厂方法模式是设计模式中较为常见的两种模式，借助于依赖注入可以更好的发挥模式的特性。本文将通过一个业务需求的变化过程来阐述如何更好的使用设计模式与依赖注入。

<!-- more -->

## 业务需求

在用户登录之后，需要向用户发送一条短信，通知用户。

## 代码演练

### 公共内容

```csharp
namespace Use_Dependency_Injection_With_Factory_Pattern
{
    /// <summary>
    /// 发送短信
    /// </summary>
    public interface ISmsSender
    {
        /// <summary>
        /// 发送短信
        /// </summary>
        /// <param name="phone">手机</param>
        /// <param name="message">短信  </param>
        void Send(string phone, string message);
    }

    /// <summary>
    /// 用户业务
    /// </summary>
    public interface IUserBll
    {
        /// <summary>
        /// 登录
        /// </summary>
        /// <param name="phone"></param>
        /// <param name="password"></param>
        bool Login(string phone, string password);
    }

    public interface IUserDal
    {
        bool Exists(string phone, string password);
    }

    public class UserDal : IUserDal
    {
        private const string StaticPassword = "newbe";
        private const string StaticPhone = "yueluo";

        public bool Exists(string phone, string password)
        {
            // 使用固定的账号密码验证
            return phone == StaticPhone && password == StaticPassword;
        }
    }
}

```

公共内容中包含了业务需求中的主要接口`ISmsSender`和`IUserBll`，以及演示用的数据存储层接口与实现。

### 版本1，使用控制台“发送短信”

```csharp
using Autofac;
using System;

namespace Use_Dependency_Injection_With_Factory_Pattern
{
    public static class Demo1
    {
        public static void Run()
        {
            Console.WriteLine($"开始运行{nameof(Demo1)}");
            var cb = new ContainerBuilder();
            cb.RegisterType<UserDal>().As<IUserDal>();
            cb.RegisterType<UserBll>().As<IUserBll>();
            cb.RegisterType<ConsoleSmsSender>().As<ISmsSender>();
            var container = cb.Build();

            var userBll = container.Resolve<IUserBll>();
            var login = userBll.Login("yueluo", "newbe");
            Console.WriteLine(login);

            login = userBll.Login("newbe", "yueluo");
            Console.WriteLine(login);
            Console.WriteLine($"结束运行{nameof(Demo1)}");
        }

        public class UserBll : IUserBll
        {
            private readonly IUserDal _userDal;
            private readonly ISmsSender _smsSender;

            public UserBll(
                IUserDal userDal,
                ISmsSender smsSender)
            {
                _userDal = userDal;
                _smsSender = smsSender;
            }

            public bool Login(string phone, string password)
            {
                var re = _userDal.Exists(phone, password);
                if (re)
                {
                    _smsSender.Send(phone, "您已成功登录系统");
                }

                return re;
            }
        }

        public class ConsoleSmsSender : ISmsSender
        {
            public void Send(string phone, string message)
            {
                Console.WriteLine($"已给{phone}发送消息：{message}");
            }
        }
    }
}

```

简要分析。版本1使用构造函数注入实现了代码的解耦，使用Autofac作为容器管理，常规用法，没有问题。

由于没有正常的短信发送调用，所以使用`ConsoleSmsSender`在控制台中输出消息进行模拟发送。

### 版本2，线上版本“真发短信”，开发版本“假发短信”

```csharp
using Autofac;
using System;

namespace Use_Dependency_Injection_With_Factory_Pattern
{
    public static class Demo2
    {
        public static void Run()
        {
            Console.WriteLine($"开始运行{nameof(Demo2)}");
            var cb = new ContainerBuilder();
            cb.RegisterType<UserDal>().As<IUserDal>();
            cb.RegisterType<UserBll>().As<IUserBll>();
            // 使用预编译命令，使得 Release 和 Debug 版本注册的对象不同，从而实现调用的短信API不同
#if DEBUG
            cb.RegisterType<ConsoleSmsSender>().As<ISmsSender>();
#else
            cb.RegisterType<HttpApiSmsSender>().As<ISmsSender>();
#endif
            var container = cb.Build();

            var userBll = container.Resolve<IUserBll>();
            var login = userBll.Login("yueluo", "newbe");
            Console.WriteLine(login);

            login = userBll.Login("newbe", "yueluo");
            Console.WriteLine(login);
            Console.WriteLine($"结束运行{nameof(Demo2)}");
        }

        public class UserBll : IUserBll
        {
            private readonly IUserDal _userDal;
            private readonly ISmsSender _smsSender;

            public UserBll(
                IUserDal userDal,
                ISmsSender smsSender)
            {
                _userDal = userDal;
                _smsSender = smsSender;
            }

            public bool Login(string phone, string password)
            {
                var re = _userDal.Exists(phone, password);
                if (re)
                {
                    _smsSender.Send(phone, "您已成功登录系统");
                }

                return re;
            }
        }
        /// <summary>
        /// 调试·短信API
        /// </summary>
        public class ConsoleSmsSender : ISmsSender
        {
            public void Send(string phone, string message)
            {
                Console.WriteLine($"已给{phone}发送消息：{message}");
            }
        }

        /// <summary>
        /// 真·短信API
        /// </summary>
        public class HttpApiSmsSender : ISmsSender
        {
            public void Send(string phone, string message)
            {
                Console.WriteLine($"已调用API给{phone}发送消息：{message}");
            }
        }
    }
}

```

简要分析。与版本1相比，增加了真实调用短信API的实现类，并且通过预编译的方式，实现了Debug模式和Release模式下发布不同版本的效果。一定程度上已经完成了需求。

### 版本3，引入工厂模式，实现“短信API选择”逻辑的分类

```csharp
using Autofac;
using System;

namespace Use_Dependency_Injection_With_Factory_Pattern
{
    public static class Demo3
    {
        public static void Run()
        {
            Console.WriteLine($"开始运行{nameof(Demo3)}");
            var cb = new ContainerBuilder();
            cb.RegisterType<UserDal>().As<IUserDal>();
            cb.RegisterType<UserBll>().As<IUserBll>();
            cb.RegisterType<SmsSenderFactory>().As<ISmsSenderFactory>();
            cb.RegisterType<ConfigProvider>().As<IConfigProvider>();
            var container = cb.Build();

            var userBll = container.Resolve<IUserBll>();
            var login = userBll.Login("yueluo", "newbe");
            Console.WriteLine(login);

            login = userBll.Login("newbe", "yueluo");
            Console.WriteLine(login);
            Console.WriteLine($"结束运行{nameof(Demo3)}");
        }

        public class UserBll : IUserBll
        {
            private readonly IUserDal _userDal;
            private readonly ISmsSenderFactory _smsSenderFactory;

            public UserBll(
                IUserDal userDal,
                ISmsSenderFactory smsSenderFactory)
            {
                _userDal = userDal;
                _smsSenderFactory = smsSenderFactory;
            }

            public bool Login(string phone, string password)
            {
                var re = _userDal.Exists(phone, password);
                if (re)
                {
                    var smsSender = _smsSenderFactory.Create();
                    smsSender.Send(phone, "您已成功登录系统");
                }

                return re;
            }
        }

        /// <summary>
        /// 调试·短信API
        /// </summary>
        public class ConsoleSmsSender : ISmsSender
        {
            public void Send(string phone, string message)
            {
                Console.WriteLine($"已给{phone}发送消息：{message}");
            }
        }

        /// <summary>
        /// 真·短信API
        /// </summary>
        public class HttpApiSmsSender : ISmsSender
        {
            public void Send(string phone, string message)
            {
                Console.WriteLine($"已调用API给{phone}发送消息：{message}");
            }
        }

        public enum SmsSenderType
        {
            /// <summary>
            /// 控制台发送短信
            /// </summary>
            Console,

            /// <summary>
            /// 通过HttpApi进行发送短信
            /// </summary>
            HttpAPi
        }

        public interface ISmsSenderFactory
        {
            ISmsSender Create();
        }

        public class SmsSenderFactory : ISmsSenderFactory
        {
            private readonly IConfigProvider _configProvider;

            public SmsSenderFactory(
                IConfigProvider configProvider)
            {
                _configProvider = configProvider;
            }

            public ISmsSender Create()
            {
                // 短信发送者创建，从配置管理中读取当前的发送方式，并创建实例
                var smsConfig = _configProvider.GetSmsConfig();
                switch (smsConfig.SmsSenderType)
                {
                    case SmsSenderType.Console:
                        return new ConsoleSmsSender();
                    case SmsSenderType.HttpAPi:
                        return new HttpApiSmsSender();
                    default:
                        return new HttpApiSmsSender();
                }
            }
        }

        public class SmsConfig
        {
            public SmsSenderType SmsSenderType { get; set; }
        }

        public interface IConfigProvider
        {
            SmsConfig GetSmsConfig();
        }

        public class ConfigProvider : IConfigProvider
        {
            private readonly SmsConfig _smsConfig = new SmsConfig
            {
                SmsSenderType = SmsSenderType.Console
            };

            public SmsConfig GetSmsConfig()
            {
                // 此处直接使用了写死的短信发送配置，实际项目中往往是通过配置读取的方式，实现该配置的加载。
                return _smsConfig;
            }
        }
    }
}

```

简要分析。相较于版本2，引入的**工厂模式**，实现了“短信发送方式选择”逻辑的封装。这样改造之后，便可以不论是在生产环境还是开发环境，都能够通过配置项的修改，实现短信发送方式的切换。

当然，在增加了程序灵活性的同时，也引入了更多的类和配置。

### 版本4，工厂方法模式

```csharp
using Autofac;
using System;
using System.Linq;

namespace Use_Dependency_Injection_With_Factory_Pattern
{
    public static class Demo4
    {
        public static void Run()
        {
            Console.WriteLine($"开始运行{nameof(Demo4)}");
            var cb = new ContainerBuilder();
            cb.RegisterType<UserDal>().As<IUserDal>();
            cb.RegisterType<UserBll>().As<IUserBll>();
            cb.RegisterType<SmsSenderFactory>().As<ISmsSenderFactory>();
            cb.RegisterType<ConsoleSmsSenderFactoryHandler>()
                .As<ISmsSenderFactoryHandler>();
            cb.RegisterType<SmsSenderFactoryHandler>()
                .As<ISmsSenderFactoryHandler>();
            cb.RegisterType<ConfigProvider>().As<IConfigProvider>();
            var container = cb.Build();

            var userBll = container.Resolve<IUserBll>();
            var login = userBll.Login("yueluo", "newbe");
            Console.WriteLine(login);

            login = userBll.Login("newbe", "yueluo");
            Console.WriteLine(login);
            Console.WriteLine($"结束运行{nameof(Demo4)}");
        }

        public class UserBll : IUserBll
        {
            private readonly IUserDal _userDal;
            private readonly ISmsSenderFactory _smsSenderFactory;

            public UserBll(
                IUserDal userDal,
                ISmsSenderFactory smsSenderFactory)
            {
                _userDal = userDal;
                _smsSenderFactory = smsSenderFactory;
            }

            public bool Login(string phone, string password)
            {
                var re = _userDal.Exists(phone, password);
                if (re)
                {
                    var smsSender = _smsSenderFactory.Create();
                    smsSender.Send(phone, "您已成功登录系统");
                }

                return re;
            }
        }

        public enum SmsSenderType
        {
            /// <summary>
            /// 控制台发送短信
            /// </summary>
            Console,

            /// <summary>
            /// 通过HttpApi进行发送短信
            /// </summary>
            HttpAPi
        }

        public interface ISmsSenderFactory
        {
            ISmsSender Create();
        }

        public class SmsSenderFactory : ISmsSenderFactory
        {

            private readonly IConfigProvider _configProvider;
            private readonly ISmsSenderFactoryHandler[] _smsSenderFactoryHandlers;

            public SmsSenderFactory(
                IConfigProvider configProvider,
                ISmsSenderFactoryHandler[] smsSenderFactoryHandlers)
            {
                _configProvider = configProvider;
                _smsSenderFactoryHandlers = smsSenderFactoryHandlers;
            }

            public ISmsSender Create()
            {
                // 短信发送者创建，从配置管理中读取当前的发送方式，并创建实例
                var smsConfig = _configProvider.GetSmsConfig();
                // 通过工厂方法的方式，将如何创建具体短信发送者的逻辑从这里移走，实现了这个方法本身的稳定。
                var factoryHandler = _smsSenderFactoryHandlers.Single(x => x.SmsSenderType == smsConfig.SmsSenderType);
                var smsSender = factoryHandler.Create();
                return smsSender;
            }
        }

        /// <summary>
        /// 工厂方法接口
        /// </summary>
        public interface ISmsSenderFactoryHandler
        {
            SmsSenderType SmsSenderType { get; }
            ISmsSender Create();
        }

        #region 控制台发送短信接口实现

        public class ConsoleSmsSenderFactoryHandler : ISmsSenderFactoryHandler
        {
            public SmsSenderType SmsSenderType { get; } = SmsSenderType.Console;
            public ISmsSender Create()
            {
                return new ConsoleSmsSender();
            }
        }

        /// <summary>
        /// 调试·短信API
        /// </summary>
        public class ConsoleSmsSender : ISmsSender
        {
            public void Send(string phone, string message)
            {
                Console.WriteLine($"已给{phone}发送消息：{message}");
            }
        }

        #endregion

        #region API发送短信接口实现

        public class SmsSenderFactoryHandler : ISmsSenderFactoryHandler
        {
            public SmsSenderType SmsSenderType { get; } = SmsSenderType.HttpAPi;
            public ISmsSender Create()
            {
                return new HttpApiSmsSender();
            }
        }

        /// <summary>
        /// 真·短信API
        /// </summary>
        public class HttpApiSmsSender : ISmsSender
        {
            public void Send(string phone, string message)
            {
                Console.WriteLine($"已调用API给{phone}发送消息：{message}");
            }
        }

        #endregion

        public class SmsConfig
        {
            public SmsSenderType SmsSenderType { get; set; }
        }

        public interface IConfigProvider
        {
            SmsConfig GetSmsConfig();
        }

        public class ConfigProvider : IConfigProvider
        {
            private readonly SmsConfig _smsConfig = new SmsConfig
            {
                SmsSenderType = SmsSenderType.Console
            };

            public SmsConfig GetSmsConfig()
            {
                // 此处直接使用了写死的短信发送配置，实际项目中往往是通过配置读取的方式，实现该配置的加载。
                return _smsConfig;
            }
        }
    }
}

```

简要说明。相对于版本3，采用了**工厂方法模式**。本质上，就是将“不同的类型如何创建短信发送API”的逻辑转移到了`ISmsSenderFactory`的实现类中。实际项目中，往往可以将`ISmsSenderFactory`和`ISmsSender`的实现类放在不同的程序集中。而且后续如果要增加新的发送方式，只需要增加对应的实现类并且注册即可，进一步增加了可扩展性。

### 版本5，结合Autofac的最终版本

```csharp

using Autofac;
using Autofac.Features.Indexed;
using System;

namespace Use_Dependency_Injection_With_Factory_Pattern
{
    public static class Demo5
    {
        public static void Run()
        {
            Console.WriteLine($"开始运行{nameof(Demo5)}");
            var cb = new ContainerBuilder();

            cb.RegisterModule<CoreModule>();
            cb.RegisterModule<SmsCoreModule>();
            cb.RegisterModule<ConsoleSmsModule>();
            cb.RegisterModule<HttpApiSmsModule>();

            var container = cb.Build();

            var userBll = container.Resolve<IUserBll>();
            var login = userBll.Login("yueluo", "newbe");
            Console.WriteLine(login);

            login = userBll.Login("newbe", "yueluo");
            Console.WriteLine(login);
            Console.WriteLine($"结束运行{nameof(Demo5)}");
        }

        public class CoreModule : Module
        {
            protected override void Load(ContainerBuilder builder)
            {
                base.Load(builder);
                builder.RegisterType<UserDal>().As<IUserDal>();
                builder.RegisterType<UserBll>().As<IUserBll>();
                builder.RegisterType<ConfigProvider>().As<IConfigProvider>();
            }
        }

        public class SmsCoreModule : Module
        {
            protected override void Load(ContainerBuilder builder)
            {
                base.Load(builder);
                builder.RegisterType<SmsSenderFactory>()
                    .As<ISmsSenderFactory>();
            }
        }

        public class ConsoleSmsModule : Module
        {
            protected override void Load(ContainerBuilder builder)
            {
                base.Load(builder);
                builder.RegisterType<ConsoleSmsSender>().AsSelf();// 此注册将会使得 ConsoleSmsSender.Factory 能够被注入
                builder.RegisterType<ConsoleSmsSenderFactoryHandler>()
                    .Keyed<ISmsSenderFactoryHandler>(SmsSenderType.Console);
            }
        }

        public class HttpApiSmsModule : Module
        {
            protected override void Load(ContainerBuilder builder)
            {
                base.Load(builder);
                builder.RegisterType<HttpApiSmsSender>().AsSelf();
                builder.RegisterType<SmsSenderFactoryHandler>()
                    .Keyed<ISmsSenderFactoryHandler>(SmsSenderType.HttpAPi);
            }
        }

        public class UserBll : IUserBll
        {
            private readonly IUserDal _userDal;
            private readonly ISmsSenderFactory _smsSenderFactory;

            public UserBll(
                IUserDal userDal,
                ISmsSenderFactory smsSenderFactory)
            {
                _userDal = userDal;
                _smsSenderFactory = smsSenderFactory;
            }

            public bool Login(string phone, string password)
            {
                var re = _userDal.Exists(phone, password);
                if (re)
                {
                    var smsSender = _smsSenderFactory.Create();
                    smsSender.Send(phone, "您已成功登录系统");
                }

                return re;
            }
        }

        public enum SmsSenderType
        {
            /// <summary>
            /// 控制台发送短信
            /// </summary>
            Console,

            /// <summary>
            /// 通过HttpApi进行发送短信
            /// </summary>
            HttpAPi
        }

        public interface ISmsSenderFactory
        {
            ISmsSender Create();
        }

        public class SmsSenderFactory : ISmsSenderFactory
        {
            private readonly IConfigProvider _configProvider;
            private readonly IIndex<SmsSenderType, ISmsSenderFactoryHandler> _smsSenderFactoryHandlers;

            public SmsSenderFactory(
                IConfigProvider configProvider,
                IIndex<SmsSenderType, ISmsSenderFactoryHandler> smsSenderFactoryHandlers)
            {
                _configProvider = configProvider;
                _smsSenderFactoryHandlers = smsSenderFactoryHandlers;
            }

            public ISmsSender Create()
            {
                // 短信发送者创建，从配置管理中读取当前的发送方式，并创建实例
                var smsConfig = _configProvider.GetSmsConfig();
                // 通过工厂方法的方式，将如何创建具体短信发送者的逻辑从这里移走，实现了这个方法本身的稳定。
                var factoryHandler = _smsSenderFactoryHandlers[smsConfig.SmsSenderType];
                var smsSender = factoryHandler.Create();
                return smsSender;
            }
        }

        /// <summary>
        /// 工厂方法接口
        /// </summary>
        public interface ISmsSenderFactoryHandler
        {
            ISmsSender Create();
        }

        #region 控制台发送短信接口实现

        public class ConsoleSmsSenderFactoryHandler : ISmsSenderFactoryHandler
        {
            private readonly ConsoleSmsSender.Factory _factory;

            public ConsoleSmsSenderFactoryHandler(
                ConsoleSmsSender.Factory factory)
            {
                _factory = factory;
            }

            public ISmsSender Create()
            {
                return _factory();
            }
        }

        /// <summary>
        /// 调试·短信API
        /// </summary>
        public class ConsoleSmsSender : ISmsSender
        {
            public delegate ConsoleSmsSender Factory();
            public void Send(string phone, string message)
            {
                Console.WriteLine($"已给{phone}发送消息：{message}");
            }
        }

        #endregion

        #region API发送短信接口实现

        public class SmsSenderFactoryHandler : ISmsSenderFactoryHandler
        {
            private readonly HttpApiSmsSender.Factory _factory;

            public SmsSenderFactoryHandler(
                HttpApiSmsSender.Factory factory)
            {
                _factory = factory;
            }

            public ISmsSender Create()
            {
                return _factory();
            }
        }

        /// <summary>
        /// 真·短信API
        /// </summary>
        public class HttpApiSmsSender : ISmsSender
        {
            public delegate HttpApiSmsSender Factory();
            public void Send(string phone, string message)
            {
                Console.WriteLine($"已调用API给{phone}发送消息：{message}");
            }
        }

        #endregion

        public class SmsConfig
        {
            public SmsSenderType SmsSenderType { get; set; }
        }

        public interface IConfigProvider
        {
            SmsConfig GetSmsConfig();
        }

        public class ConfigProvider : IConfigProvider
        {
            private readonly SmsConfig _smsConfig = new SmsConfig
            {
                SmsSenderType = SmsSenderType.Console
            };

            public SmsConfig GetSmsConfig()
            {
                // 此处直接使用了写死的短信发送配置，实际项目中往往是通过配置读取的方式，实现该配置的加载。
                return _smsConfig;
            }
        }
    }
}

```

简要说明。相对于版本4，该版本结合了较多Autofac所提供的特性。

1. 使用了`Module`，使得相关的类更加聚合，往往可以通过这种方式将相关的逻辑独立在一个程序集中
2. 使用了`Index<,>`的方式进行注册。这是Autofac提供了一种服务注册方式，将相同接口的实现以不同的键进行注册和实例。[参考链接](https://autofac.readthedocs.io/en/latest/resolve/relationships.html#keyed-service-lookup-iindex-x-b)
3. 使用了Autofac提供了`Delegate Factories`特性。这样在操作`ConsoleSmsSender`这样的类时，便也可以使用依赖注入。[参考链接](https://autofac.readthedocs.io/en/latest/advanced/delegate-factories.html)

## 总结

通过上述代码的演变过程，简要介绍了工厂模式和工厂方法模式在项目当中的使用方法，也是对依赖注入方法使用的进一步熟悉。

在使用设计模式和依赖注入的过程当中，不可避免的增加了更多的接口和实现类。读者需要深入理解，各个版本之间的差异，已经后一个版本产生的原因。如果读者能够将每个版本的变化总结为**“隔离了什么变化，实现了什么解耦”**这样一句话，那么说明读者已经理解的其中的原因。

实际项目之中也并非始终都要套用最终的复杂模式，开发者需要根据实际项目可能的变化因素自行考评模式使用的力度。

[本文示例代码地址](https://github.com/newbe36524/Newbe.Demo/tree/master/src/BlogDemos/Use-Dependency-Injection-In-CSharp/Use-Dependency-Injection-With-Factory-Pattern)

<!-- md Nav-Use-Dependency-Injection.md -->
