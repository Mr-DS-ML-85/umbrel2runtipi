# Nostr VPN

Admin-approved mesh VPN over Nostr

Nostr VPN turns your the server into a private mesh VPN node for your own devices and trusted groups. Approve signed join-request QRs, manage peers, and route traffic through trusted exit nodes without relying on a hosted VPN provider or a central control server.

To connect a device, choose Join on the device you want to add so it displays its signed QR code or link. On your the server, scan or paste that request, review it, and accept it. The joining device then receives the signed network roster and your devices can reach each other using their private Nostr VPN IPs.

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/nostr-vpn/1.webp)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/nostr-vpn/2.webp)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/nostr-vpn/3.webp)

## Links

- Website: https://github.com/mmalmi/nostr-vpn
- Repository: https://github.com/mmalmi/nostr-vpn
- Support: https://github.com/mmalmi/nostr-vpn/issues

## Release notes

Changes since v4.0.67:
  - Updates Umbrel to the signed join-request flow used by current clients: the joining device displays a QR code or link and the Umbrel admin scans or pastes it.
  - Improves VPN reliability, fallback recovery, and performance across platforms.
  - Fixes paid-exit discovery, provider links, connection status, pricing, and settlement.
