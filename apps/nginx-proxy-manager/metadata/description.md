# Nginx Proxy Manager

Expose your services easily and securely

Expose your apps to the internet easily and securely.

⚠️ Be cautious when exposing apps to the public internet. Ensure they have proper security, such as login protection, and avoid exposing sensitive apps without adequate safeguards.

🔧 Nginx Proxy Manager uses port 40080 for HTTP (unsecured) traffic and port 40443 for HTTPS (secured) traffic. To make your apps accessible from the public internet, you will need to set up port forwarding on your router. Forward external port 80 (HTTP) to internal port 40080 and external port 443 (HTTPS) to internal port 40443.

🔍 Features:

  - Beautiful and Secure Admin Interface based on Tabler
  - Easily create forwarding domains, redirections, streams and 404 hosts without knowing anything about Nginx
  - Free SSL using Let's Encrypt or provide your own custom SSL certificates
  - Access Lists and basic HTTP Authentication for your hosts
  - Advanced Nginx configuration available for super users
  - User management, permissions and audit log

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/nginx-proxy-manager/1.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/nginx-proxy-manager/2.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/nginx-proxy-manager/3.jpg)

## Links

- Website: https://nginxproxymanager.com/
- Repository: https://github.com/NginxProxyManager/nginx-proxy-manager
- Support: https://github.com/NginxProxyManager/nginx-proxy-manager/issues

## Release notes

This release reverts the base image to Lua 5.1.5 and fixes an issue that could occur when internal Nginx configuration files are mounted.

Full release notes can be found at https://github.com/NginxProxyManager/nginx-proxy-manager/releases/tag/v2.15.1
