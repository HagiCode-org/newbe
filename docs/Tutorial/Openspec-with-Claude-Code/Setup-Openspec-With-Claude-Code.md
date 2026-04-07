---
date: 2025-12-03
title: 为什么我还需要 Openspec 和 Claude Code？
tags:
 - Openspec
 - Claude Code

---

AI 辅助编程工具已经成为现代开发者工作流程中不可或缺的一部分。Openspec 和 Claude Code 是两款强大的工具，能够显著提升开发效率和代码质量。那么，为什么我们还需要它们呢？

<!-- more -->

## Openspec

### 我们遇到了什么问题？

AI不擅长猜测开发者的心思。虽然 AI 可以生成代码，但它往往无法准确理解开发者的具体需求和意图，导致生成的代码不符合预期。
所以 AI 需要上下文。 但是通常来说上下文是零散的，比如来自用户的输入的提示词、项目的 README 文件、代码注释等。AI 需要将这些零散的信息整合起来，才能更好地理解开发者的需求。
为了更好的构建良好的上下文，我们需要一个结构化的方式来描述需求和设计。
而这种方式就是规范（specification）。

现在有很多现成的 AI 工具或者 IDE 都带有类似的功能。比如 Github Copilot、Cursor 等 IDE 的 Plan 功能，比如类似 Kiro 的 spec 模式。实际上他们都是为了做一件事情，就是在开始编码之前，让AI输出一个结构化的需求描述，从而更好地指导后续的代码生成。让开发者和 AI 之间有一个共同的理解基础。

而在众多的规范化工具中，笔者认为 Openspec 是一个非常有潜力的工具。它非常适合于有丰富经验的开发者使用，因为它允许开发者以一种结构化的方式来描述需求和设计，从而更好地指导 AI 生成代码。

### 为什么是 Openspec？

笔者认为 Openspec 有以下几个优势。

- 他能工作而又不会太重。Openspec 采用轻量级的 Markdown 文件来描述规范和变更，易于阅读和维护。它不会给项目增加过多的复杂性。
- 他可以和 AI 工具无缝集成。Openspec 支持多种 AI 工具，包括 Claude Code，这使得开发者可以方便地使用 AI 来生成代码和文档。
- 他可以越来越智能，因为归档。Openspec 支持归档已完成的变更，这样 AI 可以学习过去的决策和实现，从而在未来提供更好的建议。

### 如何安装 Openspec？

#### 前置条件

- **Node.js >= 20.19.0** - 使用 `node --version` 检查你的版本

#### 步骤 1: 全局安装 CLI

```bash
npm install -g @fission-ai/openspec@latest
```

验证安装：
```bash
openspec --version
```

#### 步骤 2: 在项目中初始化 Openspec

导航到你的项目目录：
```bash
cd my-project
```

运行初始化：
```bash
openspec init
```

**初始化过程中会发生什么：**
- 系统会提示你选择原生支持的 AI 工具，**请选择 Claude Code**
- OpenSpec 会自动为 Claude Code 配置专用的斜杠命令（`/openspec:proposal`、`/openspec:apply`、`/openspec:archive`）
- 在项目根目录创建 `AGENTS.md` 文件，同时在项目中创建 `openspec/` 目录结构

**设置完成后：**
- 在 Claude Code 中可以直接使用 `/openspec:*` 斜杠命令触发工作流
- 运行 `openspec list` 验证设置并查看任何活跃的变更
- 如果 Claude Code 没有立即显示斜杠命令，请重启 VS Code。斜杠命令在启动时加载

### 如何使用 Openspec？

#### 工作流程概览

```
┌────────────────────┐
│ 起草变更提案        │
│ (Draft Proposal)   │
└────────┬───────────┘
         │ 与 AI 共享意图
         ▼
┌────────────────────┐
│ 审查与对齐          │◀──── 反馈循环 ────┐
│ (Review & Align)   │                   │
└────────┬───────────┘                   │
         │ 批准的计划                    │
         ▼                               │
┌────────────────────┐                   │
│ 实现任务            │───────────────────┘
│ (Implement Tasks)  │
└────────┬───────────┘
         │ 发布变更
         ▼
┌────────────────────┐
│ 归档并更新规范      │
│ (Archive & Update) │
└────────────────────┘
```

#### 创建你的第一个变更

##### 1. 起草提案

在 Claude Code 中使用斜杠命令创建变更提案：

```text
你：/openspec:proposal 添加按角色和团队的个人资料搜索过滤器

Claude Code：我将为个人资料过滤器创建一个 OpenSpec 变更提案。
    *在 openspec/changes/add-profile-filters/ 中创建 proposal.md、tasks.md 和规范增量。*
```

> **提示：** 你也可以用自然语言描述："创建一个 OpenSpec 变更提案，添加按角色和团队的个人资料搜索过滤器"，但使用斜杠命令更加简洁直接。

##### 2. 验证和审查

检查变更是否正确创建并审查提案：

```bash
$ openspec list                            # 确认变更文件夹存在
$ openspec validate add-profile-filters    # 验证规范格式
$ openspec show add-profile-filters        # 审查提案、任务和规范增量
```

##### 3. 完善规范

在 Claude Code 中迭代规范直到它们符合你的需求：

```text
你：你能为角色和团队过滤器添加验收标准吗？

Claude Code：我将使用角色和团队过滤器的场景更新规范增量。
    *编辑 openspec/changes/add-profile-filters/specs/profile/spec.md 和 tasks.md。*
```

##### 4. 实现变更

一旦规范看起来不错，在 Claude Code 中开始实现：

```text
你：/openspec:apply add-profile-filters

Claude Code：我将处理 add-profile-filters 变更中的任务。
    *从 openspec/changes/add-profile-filters/tasks.md 实现任务*
    *标记任务完成：任务 1.1 ✓，任务 1.2 ✓，任务 2.1 ✓...*
```

> **提示：** Claude Code 会自动读取 tasks.md 中的任务列表，并逐个实现它们。你可以随时查看进度，也可以要求它暂停或跳过某些任务。

##### 5. 归档已完成的变更

实现完成后，在 Claude Code 中归档变更：

```text
Claude Code：所有任务已完成。实现已准备就绪。

你：/openspec:archive add-profile-filters

Claude Code：我将归档 add-profile-filters 变更。
    *运行：openspec archive add-profile-filters --yes*
    ✓ 变更已成功归档。规范已更新。准备好下一个功能！
```

或者在终端中自己运行命令：
```bash
$ openspec archive add-profile-filters --yes  # 无提示归档已完成的变更
```

### Openspec 的实际示例

当你要求 AI 助手"添加双因素认证"时，它会创建：

```
openspec/
├── specs/
│   └── auth/
│       └── spec.md           # 当前认证规范（如果存在）
└── changes/
    └── add-2fa/              # AI 创建整个结构
        ├── proposal.md       # 为什么以及改变什么
        ├── tasks.md          # 实现清单
        ├── design.md         # 技术决策（可选）
        └── specs/
            └── auth/
                └── spec.md   # 显示添加内容的增量
```

#### AI 生成的规范（在 `openspec/specs/auth/spec.md` 中创建）：

```markdown
# 认证规范

## 目的
认证和会话管理。

## 需求
### 需求：用户认证
系统应在成功登录时颁发 JWT。

#### 场景：有效凭证
- 当用户提交有效凭证时
- 则返回 JWT
```

#### AI 生成的变更增量（在 `openspec/changes/add-2fa/specs/auth/spec.md` 中创建）：

```markdown
# 认证增量

## 添加的需求
### 需求：双因素认证
系统必须在登录期间要求第二因素。

#### 场景：需要 OTP
- 当用户提交有效凭证时
- 则需要 OTP 挑战
```

#### AI 生成的任务（在 `openspec/changes/add-2fa/tasks.md` 中创建）：

```markdown
## 1. 数据库设置
- [ ] 1.1 向用户表添加 OTP 密钥列
- [ ] 1.2 创建 OTP 验证日志表

## 2. 后端实现
- [ ] 2.1 添加 OTP 生成端点
- [ ] 2.2 修改登录流程以要求 OTP
- [ ] 2.3 添加 OTP 验证端点

## 3. 前端更新
- [ ] 3.1 创建 OTP 输入组件
- [ ] 3.2 更新登录流程 UI
```

**重要提示：** 你不需要手动创建这些文件。Claude Code 会根据你的需求和现有代码库自动生成它们。
