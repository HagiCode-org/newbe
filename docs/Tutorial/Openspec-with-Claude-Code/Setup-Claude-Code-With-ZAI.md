---
date: 2025-12-03
title: 安装和设置 Claude Code 与 ZAI
tags:
 - Claude Code
 - ZAI

---

Claude Code 是一个强大的 AI 辅助编程工具，能够显著提升开发效率和代码质量。智谱 AI (ZAI) 是国内供应商提供的一款据说智能度较高的 AI 模型。笔者在实际使用的过程中发现，确实还不错。因此本文将指导你如何在 Claude Code 中配置和使用 ZAI 模型。

<!-- more -->

## 安装 Claude Code

通过 NPM 可以以非常方便地安装 Claude Code 插件。请确保你已经安装了 Node.js 环境。

```bash
npm install -g @anthropic-ai/claude-code
```
安装完毕之后，可以通过以下命令验证安装是否成功：

```bash
claude --version
```

## 购买 ZAI 订阅

使用 ZAI 你需要先购买订阅并获得 API Key。对于写代码来说，一般要购买 Coding Plan 作为日常使用，这样才会更加节约成本。

可以通过以下链接购买获得 10% 优惠：[https://www.bigmodel.cn/claude-code?ic=14BY54APZA](https://www.bigmodel.cn/claude-code?ic=14BY54APZA)

初次体验可以购买 lite 版本，价格更低。

购买成功之后通过这个地址可以创建 API Key：[https://bigmodel.cn/usercenter/proj-mgmt/apikeys](https://bigmodel.cn/usercenter/proj-mgmt/apikeys)

## 在 Claude Code 中配置 ZAI

官方提供了文档来说明如何在 Claude Code 中配置 ZAI 模型：[https://docs.bigmodel.cn/cn/coding-plan/tool/claude](https://docs.bigmodel.cn/cn/coding-plan/tool/claude)
这里也进行一次说明，如果官网有变化请以官网为准。

ZAI 现在提供了一个简单的命令行工具 `coding-helper` 来帮助你配置 Claude Code。

```bash
# 进入命令行界面，执行如下运行 Coding Tool Helper
npx @z_ai/coding-helper
```

运行之后会进入一个交互式的命令行界面，按照提示输入你的 API Key 和选择 Claude Code 即可完成配置。

## 初次体验

完成配置之后，你就可以在 Claude Code 中使用 ZAI 模型了。在命令行中输入

```bash
claude
```

即可进入 Claude Code 的交互界面。在交互界面中, 进行围绕当前文件夹的上下文进行代码生成和修改。

如果第一次呼出的时候要求填写一个 API Key，你可以随便输入一个字符串，因为这不是我们需要的 Key，真正的 Key 已经通过 `coding-helper` 工具配置好了。

## IDE 插件

Claude Code 也提供了 VSCode 和 JetBrains 系列 IDE 的插件，可以让你在熟悉的开发环境中使用 Claude Code 和 ZAI 模型。

- VSCode 插件市场链接：[https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)
- JetBrains 插件市场链接：[https://plugins.jetbrains.com/plugin/27310-claude-code-beta-](https://plugins.jetbrains.com/plugin/27310-claude-code-beta-)

使用 IDE 插件比起命令行工具来说，体验会更好一些，因为它可以识别到你鼠标选中的代码片段，以及你当前打开的文件，从而提供更精准的代码生成和修改建议。

## 总结

通过本文的介绍，你应该已经能够在 Claude Code 中配置和使用 ZAI 模型了。下面可以进一步了解如何配合 openspec 来进一步改进 ai 编写代码的质量。

👉 [下一步：结合 Openspec 使用 Claude Code](./Setup-Openspec-With-Claude-Code.md)