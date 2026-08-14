# Urbit

Run Urbit on your the server

Urbit is a personal server for self-sovereign personal & networked computing. Nock, a functional combinator, is built into Hoon, a system programming language, used to implement Arvo, a deterministic operating system, that communicates over Ames, a decentralized, encrypted P2P network.

This app helps you boot and manage Urbit instances on your the server. It provides a simple management GUI, start and stop operations, and passes your +code through the interface.

If you are interested in purchasing an L2 planet checkout: subject.network/buy

Credit to ~timluc-miptev, ~master-forwex, ~sipsen-pilser & ~rivpyl-sidfyl

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/urbit/1.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/urbit/2.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/urbit/3.jpg)

## Links

- Website: https://github.com/mopfel-winrux/urbit-umbrel
- Repository: https://github.com/mopfel-winrux/urbit-umbrel
- Support: https://github.com/mopfel-winrux/urbit-umbrel/issues

## Default credentials

- Username: `the server`

## Release notes

vere-v4.6 is a minor release aimed at fixing several issues that were discovered during the 408k pre-release testing process:
-   A directed messaging driver bug caused sporadic crashes, mainly on
    busy distribution ships.
-   The spin hint kubernetes fix in vere-v4.6 caused the spin hint to be
    unavailable on macos.
-   The directed messaging packet queue was uncapped, causing
    bufferbloat on heavy traffic.
-   Each directed messaging flow in the driver had nine retries once
    every second until the first response packet was heard, this caused
    unnecessary amplification on the receiver. We have reduced the retry
    count to two.


Full release notes here: https://github.com/urbit/vere/releases/tag/vere-v4.6
