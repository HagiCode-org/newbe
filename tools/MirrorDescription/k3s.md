轻量级 Kubernetes。可用于生产环境，易于安装，占用内存减半，全部在一个小于 100MB 的二进制文件中。

K3s 是一个完全符合标准的、可投入生产的 Kubernetes 发行版，具有以下变化：
- 它被打包为单个二进制文件。
- 它增加了对 sqlite3 作为默认存储后端的支持。也支持 Etcd3、MariaDB、MySQL 和 Postgres。
- 它将 Kubernetes 和其他组件包装在一个单一、简单的启动器中。
- 在轻量级环境中，它默认是安全的，具有合理的默认设置。
- 它对操作系统的依赖最小甚至没有（只需要一个正常的内核和 cgroup 挂载）。
- 它通过在 WebSocket 隧道上将 kubelet API 暴露给 Kubernetes 控制平面节点，消除了在 Kubernetes 工作节点上为 kubelet API 暴露端口的需要。