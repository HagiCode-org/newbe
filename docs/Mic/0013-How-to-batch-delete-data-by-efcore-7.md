---
date: 2022-12-17
title: 如何使用 EF Core 7 批量删除数据
tags:
  - efcore
  - dotnet
  - dotnet7
  - chatOpenAI
---

在 EF Core 7 中，我们可以使用批量操作来删除多条数据。这种方式与之前的版本有所不同，本文将对比 EFCore 7 和之前版本批量删除数据的不同方式。

<!-- more -->

## 删除给定 ID 的数据

在 EF Core 7 中，我们可以使用以下代码来删除给定 ID 的数据：

```csharp
await using var db = new MyContext();
await db.MyEntities.Where(static x => x.Id == 1).ExecuteDeleteAsync();
```

在之前的版本中，我们可以使用以下代码来删除给定 ID 的数据：

```csharp
await using var db = new MyDbContext();
// delete id == 1 by attaching it to the context
var myEntity = new MyEntity
{
    Id = 1
};
db.Attach(myEntity);
db.Remove(myEntity);
await db.SaveChangesAsync();
```

## 删除 Age 大于 10 的数据

在 EF Core 7 中，我们可以使用以下代码来删除 Age 大于 10 的数据：

```csharp
await using var db = new MyDbContext();
await db.MyEntities.Where(static x => x.Age > 10).ExecuteDeleteAsync();
```

在之前的版本中，我们可以使用以下代码来删除 Age 大于 10 的数据：

```csharp
await using var db = new MyDbContext();
// delete age > 10 
var entities = db.MyEntities.Where(static x => x.Age > 10).ToList();
db.MyEntities.RemoveRange(entities);
await db.SaveChangesAsync();
```

## 总结

在 EF Core 7 中，我们可以使用 ExecuteDeleteAsync 方法来批量删除数据，这个方法的用法与之前的版本不同。使用这种方法，我们可以方便地在数据库中删除多条数据，提升了删除数据的效率。

## 参考资料

- [EF Core 7 ExecuteUpdate 和 ExecuteDelete](https://learn.microsoft.com/ef/core/what-is-new/ef-core-7.0/whatsnew?source=recommendations&WT.mc_id=DT-MVP-5004283#executeupdate-and-executedelete-bulk-updates)

<!-- md Chat-AI-Footer.md -->
