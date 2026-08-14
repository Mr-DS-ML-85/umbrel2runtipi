# Gupt

Encrypted chat, secure vault, and ephemeral sharing

Encrypted chat, secure vault, and ephemeral sharing — with no phone number, no email, no account, and no central server.

Key features include:
  - Anonymous — no phone number, no email, no account required
  - End-to-end encrypted direct messages
  - WebRTC voice & video calls
  - Encrypted media uploads via decentralized file storage
  - Group rooms via Nostr relays
  - Local-first with offline cache (IndexedDB)
  - Vault for passwords, bookmarks, and notes
  - Anonymous file sharing

Gupt is fully client-side with no backend — it connects directly to public or private Nostr relays. Your keys, your messages, your privacy.

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/gupt/1.webp)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/gupt/2.webp)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/gupt/3.webp)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/gupt/4.webp)

## Links

- Website: https://github.com/besoeasy/gupt
- Repository: https://github.com/besoeasy/gupt
- Support: https://github.com/besoeasy/gupt/issues

## Release notes

Gupt 2.x is backwards-incompatible with Gupt v1. If you're updating from a pre-v2 version, your Gupt identity will remain, but conversations, Vault entries, and groups created in Gupt v1 will not be available in Gupt v2. Gupt v2 also cannot communicate with Gupt v1 clients, so your contacts will need to update as well.

Before updating from a pre-v2 version, open Gupt v1 and copy anything you need from your chats, Vault, and groups, and back up your private key.

This update makes Vault items easier to manage with a dedicated add page, a cleaner table layout, and templates for credit cards, crypto wallets, API keys, and Wi-Fi credentials.

Vault storage changes in this release. Before updating, open Vault and back up any important entries, especially entries that may not have synced to relays.

Vault items are now saved as readable notes with encrypted payload tags while keeping legacy Vault items visible, and Gupt adds a gupt-mark bookmarklet for saving pages to Vault more quickly.

The notification banner is now more compact and the bookmarklet redirect timer is shorter.

Encrypted chats, groups, Vault, and Share work on current Umbrel LAN URLs. Voice and video calls, screen sharing, and offline notifications require HTTPS and will become available once built-in HTTPS support lands.

Full release notes can be found at https://github.com/besoeasy/gupt/releases/tag/2.80.4
