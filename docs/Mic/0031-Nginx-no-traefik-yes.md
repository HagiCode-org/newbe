---
date: 2023-08-19
title: Nginx No, Traefik Yes
tags: [ Nginx, Docker, Traefik ]

slag: 0x02A-Nginx-no-traefik-yes
summary: Why I choose Traefik instead of Nginx as a reverse proxy in test environment.
---

<!-- YamlFrontMatter -->

As we all know, Nginx is a very popular reverse proxy server. It is very stable and has a lot of features. But I choose Traefik instead of Nginx as a reverse proxy in test environment since it is more suitable for my use case. In this post, I will explain why I choose Traefik instead of Nginx.

<!-- more -->

## Background

I have a test environment which is running on a single server. It has a lot of services running on it. I want to expose these services to the internet. So I need a reverse proxy server to do this. I am used to using Swag as a reverse proxy for years, witch is based on Nginx. But it is a little bit hard to configure. So I want to find a better solution.

I want to find a reverse proxy server which meets the following requirements:

1. It should be containerized. I don't want to install it on the host machine.
2. It should be easy to configure.
3. It should support Let's Encrypt to generate SSL certificates automatically.
4. It should be easy to migrate to production environment if needed.

## Swag

[Swag](https://github.com/linuxserver/docker-swag)[^1] is a reverse proxy server based on Nginx, witch I used for years. It meets all the requirements above. Swag project provides a docker image to run it. And dozens of Nginx configuration template files for developers to use. If you are familiar with Nginx, you can easily configure it. But it is way too complex for beginners.

I choose Swag as my reverse proxy server instead of bare Nginx, because it supports Let's Encrypt to generate SSL automatically by adding a few lines of configuration. It is very convenient.

## Caddy

[Caddy](https://caddyserver.com/v2)[^2] is a web server written in Go. I tried this solution to solve my problem after doing some research.

For example, if you want to expose a service running on port 80, you just need to create a file named `Caddyfile`:

```Caddyfile
api.newbe.pro {
    reverse_proxy api:80
}

ws.newbe.pro {
    reverse_proxy ws:80
}
```

Then run Caddy with docker as following docker-compose file:

```yaml
version: "3.4"

services:
    caddy:
        image: caddy
        container_name: caddy
        restart: unless-stopped
        ports:
            - 80:80
            - 443:443
        volumes:
            - ./Caddyfile:/etc/caddy/Caddyfile
            - ./data/caddy:/data
            - ./data/caddy/config:/config
    api:
        image: newbe36524/newbe.api
        container_name: api
        restart: unless-stopped
        environment:
            - ASPNETCORE_ENVIRONMENT=Development
        volumes:
            - ./data/api:/app/data
    ws:
        image: newbe36524/newbe.ws
        container_name: ws
        restart: unless-stopped
        environment:
            - ASPNETCORE_ENVIRONMENT=Development
        volumes:
            - ./data/ws:/app/data
```

Then configure my DNS to point `api.newbe.pro` and `ws.newbe.pro` to my server with A record. Then I can access my api service and ws service with `https://api.newbe.pro` and `https://ws.newbe.pro` respectively.

I finally gave up this solution because Caddy does not support many build-in plugins as Traefik does. Of course, you can compile Caddy with plugins you need. But I don't want to do this.

## Traefik

[Traefik](https://doc.traefik.io/traefik/)[^3] is also a reverse proxy server written in Go. I can run it as following docker-compose file:

```yaml
version: '3.4'

secrets:
    azure_client_id:
        file: "./secrets/azure_client_id.secret"
    azure_client_secret:
        file: "./secrets/azure_client_secret.secret"
    azure_tenant_id:
        file: "./secrets/azure_tenant_id.secret"
    azure_subscription_id:
        file: "./secrets/azure_subscription_id.secret"
    azure_resource_group:
        file: "./secrets/azure_resource_group.secret"

services:
    reverse-proxy:
        # The official v2 Traefik docker image
        image: traefik:v2.10
        container_name: "traefik"
        # Enables the web UI and tells Traefik to listen to docker
        command:
            - "--api.insecure=true"
            - "--providers.docker=true"
            - "--entrypoints.web.address=:80"
            - "--entrypoints.websecure.address=:443"
            - "--certificatesresolvers.myresolver.acme.dnschallenge=true"
            - "--certificatesresolvers.myresolver.acme.dnschallenge.provider=azuredns"
            - "--certificatesresolvers.myresolver.acme.email=contact@newbe.pro"
            - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
        environment:
            - "AZURE_CLIENT_ID_FILE=/run/secrets/azure_client_id"
            - "AZURE_CLIENT_SECRET_FILE=/run/secrets/azure_client_secret"
            - "AZURE_TENANT_ID=/run/secrets/azure_tenant_id"
            - "AZURE_SUBSCRIPTION_ID=/run/secrets/azure_subscription_id"
            - "AZURE_RESOURCE_GROUP=/run/secrets/azure_resource_group"
        secrets:
            - "azure_client_id"
            - "azure_client_secret"
            - "azure_tenant_id"
            - "azure_subscription_id"
            - "azure_resource_group"
        ports:
            # The HTTP port
            - "80:80"
            - "443:443"
            - "443:443/udp"
            # The Web UI (enabled by --api.insecure=true)
            - "8080:8080"
        volumes:
            # So that Traefik can listen to the Docker events
            - "/var/run/docker.sock:/var/run/docker.sock:ro"
            - "./letsencrypt:/letsencrypt"
    api:
        image: newbe36524/newbe.api
        container_name: api
        restart: unless-stopped
        environment:
            - ASPNETCORE_ENVIRONMENT=Development
        labels:
            - "traefik.enable=true"
            - "traefik.http.routers.api.rule=Host(`api.newbe.pro`)"
            - "traefik.http.routers.api.entrypoints=websecure"
            - "traefik.http.routers.api.tls.certresolver=myresolver"
    ws:
        image: newbe36524/newbe.ws
        container_name: ws
        restart: unless-stopped
        environment:
            - ASPNETCORE_ENVIRONMENT=Development
        labels:
            - "traefik.enable=true"
            - "traefik.http.routers.ws.rule=Host(`ws.newbe.pro`)"
            - "traefik.http.routers.ws.entrypoints=websecure"
            - "traefik.http.routers.ws.tls.certresolver=myresolver"
```

You can notice that all the configuration is in docker-compose file. I don't need to create any other configuration file, it is very convenient. Traefik is not only support docker as a provider to automatically discover services, but also support Kubernetes if I want to migrate to Kubernetes in the future.

## Conclusion

I choose Traefik instead of Nginx as a reverse proxy in test environment because it is more suitable for my use case. It is cloud native and easy to configure. I don't need to create any other configuration file. I can configure everything in docker-compose file.

## References

- [Azure DNS Zone](https://learn.microsoft.com/azure/dns/dns-zones-records?WT.mc_id=DT-MVP-5004283)[^4]

[^1]: https://github.com/linuxserver/docker-swag

[^2]: https://caddyserver.com/v2

[^3]: https://doc.traefik.io/traefik/

[^4]: https://learn.microsoft.com/azure/dns/dns-zones-records?WT.mc_id=DT-MVP-5004283


<!-- ending -->

<!-- ad -->

<!-- copyright-->
