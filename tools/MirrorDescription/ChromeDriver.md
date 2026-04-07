ChromeDriver 是一个独立的服务器，它实现了W3C WebDriver 标准。WebDriver 是一个为跨多个浏览器的 Web 应用程序自动化测试而构建的开源工具。它的接口允许使用功能在本地或远程控制和内省用户代理。

功能是一组与语言无关的键值对，用于定义 WebDriver 会话所需的特性和行为。在创建 WebDriver 实例时，功能通常作为参数传递，并且可用于指定浏览器设置，例如浏览器名称、版本和页面加载策略。

ChromeDriver 通过添加特定于 Chromium 的功能来扩展 WebDriver。它使用ChromeOptions对象从 WebDriver API 将功能传递给 ChromeDriver。一些特定于 Chromium 的功能包括安装扩展、更改窗口类型以及在启动时传递命令行参数的能力。

ChromeDriver 可用于 Android 上的 Chrome 和桌面版 Chrome（Mac、Linux、Windows 和 ChromeOS）。