# Dokploy

Self-hosted Platform as a Service (PaaS)

Dokploy is a free, self-hostable Platform as a Service (PaaS) that simplifies deployment and management of applications, databases and Docker Compose stacks. It uses Traefik for automatic HTTPS routing.

It manages Docker directly through the host socket and runs its control plane in Docker Swarm mode, so the host Docker engine must be reachable and able to run Swarm services. Dokploy also brings up its own Traefik on ports 80/443, which will conflict with Runtipi's Traefik -- expose Dokploy on a host with those ports free, or stop Runtipi's proxy while using it.

---


## Preview

![Preview](https://dokploy.com/banner.png)

## Links

- Website: https://dokploy.com
- Repository: https://github.com/Dokploy/dokploy
