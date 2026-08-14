# Pterodactyl

Open-source game server management panel

Pterodactyl is an open-source game server management panel. It provides a web UI to deploy, manage and monitor game servers (Minecraft, Terraria, CS2, ...) across multiple nodes, with an integrated account system, server resource limits and a REST API.

**After install**, the panel needs one manual step before you can log in: create the admin user by running inside the panel container:

```bash
docker exec -it pterodactyl-panel php artisan p:user:make
```

This package runs the control *panel* plus its MariaDB and Redis services. The *wings* daemon that actually hosts game servers is a separate component that runs on each node, requires a generated config and direct Docker access, and is not included here -- see https://pterodactyl.io for setting up wings and connecting nodes.

---


## Preview

![Preview](https://cdn.pterodactyl.io/site-assets/carousel/screenshot-1.png)

## Links

- Website: https://pterodactyl.io
- Repository: https://github.com/pterodactyl/panel
