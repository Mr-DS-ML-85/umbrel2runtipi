# Snort

Fast Nostr UI

Snort is a client for Nostr that is built using React, designed to be fast and lightweight while still offering a wide range of features.  Our focus is on providing users with an easy-to-use interface to interact with the Nostr network, making it accessible to all types of users.  With its clean and intuitive design, Snort makes it simple to navigate the Nostr network and access its features, allowing users to efficiently manage their data.

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/snort/1.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/snort/2.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/snort/3.jpg)

## Links

- Website: https://snort.social
- Repository: https://git.v0l.io/Kieran/snort
- Support: https://t.me/snort_social

## Release notes

# Highlights
- **Security Hardening**: Comprehensive audit fixes including Schnorr signature verification, NIP-46 relay message forgery protection, PIN encryption improvements, and NIP-26 delegation trust removal
- **Performance**: Batched Schnorr verification in WASM, lazy-loaded routes, pre-compiled translations, worker-relay batch optimizations, and eliminated double verification per event
- **Stability**: Fixed multiple React render loops, hook dependency arrays, stale closures, and lifecycle/memory leaks across the app

# Added
- Comprehensive request processing path tests
- Priority profile loader with batch loading, priority tiers, and chunking
- DVM kind:7000 payment-required invoice display
- Default relays fallback when pool is empty
- Zapstore manifest migration (nap.yaml → zapstore.yaml)

# Fixed
- Real Schnorr signature verification in isValid
- PIN encryption security issues
- NIP-46 hardened against forged relay messages and secret leakage
- Removed unverified NIP-26 delegation trust in getRootPubKey
- Wrapped all dangerous JSON.parse calls in try/catch
- Added timeouts to all hanging promises
- Added lifecycle management and fixed timer/memory leaks
- Render loops in NoteReaction, profile page pinned notes, notifications, and NoteContext
- React hook dependency arrays and stale closures across components
- NoteStore lazy snapshot and OutboxModel input mutation
- Queue traces for connecting relays with query system edge-case tests

https://github.com/v0l/snort/compare/v0.4.0...v0.5.0
