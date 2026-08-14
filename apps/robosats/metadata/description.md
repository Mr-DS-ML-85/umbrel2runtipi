# RoboSats

Simple and Private Bitcoin P2P Exchange

RoboSats is a simple and private app to exchange bitcoin for national currencies.  Robosats simplifies the P2P user experience and uses lightning hold invoices to  minimize custody and trust requirements. The deterministically generated robot  avatars help users stick to best privacy practices.

Features:

- Privacy focused: your robot avatar is deterministically generated, no need for registration.
- More than 10 languages available and over 60 fiat currencies
- Safe: simply lock a lightning hodl invoice and show you are real and committed.
- No data collection. Your communication with your peer is PGP encrypted, only you can read it.
- Lightning fast: the average sovereign trade finishes in ~ 8 minutes. Faster than a single block confirmation!
- Fully collateralized escrow: your peer is always committed and cannot run away with the funds.
- Strong incentives system: attempts of cheating are penalized with the slashing of the Sats in the fidelity bond.
- Guides and video tutorials available at https://learn.robosats.org/watch/en

You can join other cool Robots and get community support at https://t.me/robosats telegram group.

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/robosats/1.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/robosats/2.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/robosats/3.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/robosats/4.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/robosats/5.jpg)

## Links

- Website: https://learn.robosats.org
- Repository: https://github.com/RoboSats/robosats
- Support: https://t.me/robosats

## Release notes

Note for users who already updated to v0.8.5-alpha: v0.8.5-alpha was a pre-release, so this update returns RoboSats to v0.8.4-alpha, the latest regular release. It is safe to click update. This only changes the RoboSats app version that opens on Umbrel and does not reset your RoboSats data or require you to set up RoboSats again.

Highlights:

  - Multiple UI improvements and bug fixes.
  - Payment methods input clears when switching to Swap.
  - API errors are now displayed globally in toast messages.
  - Orders are automatically sorted by premium when filtering by SELL / BUY type.
  - Bond amount in sats is now estimated before order creation.
  - Also includes v0.8.3-alpha additions such as new coordinators, Tor Browser configuration warning, and better order-form errors.


New payment methods:

  - Binance Pay
  - DANA


Bugs:

  - Fixed typo in federation table.
  - Fixed swap and range-order "You receive..." calculations.
  - Fixed coordinator node app and Nostr values for WhiteEyeSats and Alice.
  - Pin colors are now static in map view.


Full release notes are available at https://github.com/RoboSats/robosats/releases/tag/v0.8.4-alpha
