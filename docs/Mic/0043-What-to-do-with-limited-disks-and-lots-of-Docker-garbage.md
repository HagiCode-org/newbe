---
date: 2023-02-22
title: 磁盘有限，Docker 垃圾很多怎么办
tags: [C#, Docker, Kubernetes]

slag: 0x024-What-to-do-with-limited-disks-and-lots-of-Docker-garbage
summary: 你的电脑上可能 pull 或者 build 了很多 Docker 镜像，但是你不知道怎么清理，本文将介绍如何清理 Docker 垃圾的常见方法。
---

<!-- YamlFrontMatter -->

你的电脑上可能 pull 或者 build 了很多 Docker 镜像，但是你不知道怎么清理，本文将介绍如何清理 Docker 垃圾的常见方法。

<!-- more -->

## docker prune

你可以通过原生的多种 prune 命令来清理垃圾，比如

```bash
docker image prune # 清理镜像
docker container prune # 清理容器
docker volume prune # 清理卷
docker builder prune # 清理构建缓存
```

当然还有终极杀招

```bash
docker system prune # 清理所有
```

## 针对构建缓存还有更好的办法

那么可以尝试 builder 的 GC，这样就不会在本地保留构建太多缓存了。

你可以通过修改 docker deamon 的配置文件来开启这个功能

```json
{
  "builder": {
    "gc": {
      "enabled": true,
      "defaultKeepStorage": "10GB",
      "policy": [
        { "keepStorage": "10GB", "filter": ["unused-for=2200h"] },
        { "keepStorage": "50GB", "filter": ["unused-for=3300h"] },
        { "keepStorage": "100GB", "all": true }
      ]
    }
  }
}
```

## 总结

通过这些方法，你可以清理掉你的电脑上的大量 Docker 垃圾。

## 参考

- [Prune unused Docker objects](https://docs.docker.com/config/pruning/)[^1]
- [Garbage collection](https://docs.docker.com/build/cache/garbage-collection/)[^2]

[^1]: https://docs.docker.com/config/pruning/
[^2]: https://docs.docker.com/build/cache/garbage-collection/

<!-- ending -->

<!-- ad -->

<!-- copyright-->
