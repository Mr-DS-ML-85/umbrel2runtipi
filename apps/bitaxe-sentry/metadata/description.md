# Bitaxe Sentry

Bitaxe stats and alerts, all in one

Bitaxe Sentry is a monitoring and management solution for Bitaxe ASIC miners. Track the performance, temperature, and status of your miners from a single dashboard. Get alerts when your miners hit a new best difficulty, or when temperature or voltage thresholds are exceeded.

Features included: 
  - 📊 Centralized dashboard for all Bitaxe miners
  - 🌡️ Temperature and hashrate monitoring
  - 🚨 Discord and ntfy notifications for critical events

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/bitaxe-sentry/1.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/bitaxe-sentry/2.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/bitaxe-sentry/3.jpg)

## Links

- Website: https://github.com/zachchan105/bitaxe-sentry
- Repository: https://github.com/zachchan105/bitaxe-sentry
- Support: https://github.com/zachchan105/bitaxe-sentry/issues

## Release notes

This release adds VR temperature monitoring, fan/pool telemetry, ntfy push notifications, pool latency monitoring, and per-miner notification muting, plus several bug fixes:
  - Added VR temperature tracking and alerting (default threshold 90°C, configurable in settings)
  - Added fan RPM/%, active pool URL, and session best difficulty to the dashboard
  - Added ntfy push notification support alongside existing notifiers
  - Added pool failover alerts when a miner switches between primary and fallback stratum
  - Added pool latency monitoring with a graph and configurable alert threshold
  - Added a consecutive-failure counter for miner status
  - Changed miner polling to run in parallel threads for faster, non-blocking refresh
  - Changed offline alerts to require 2 consecutive failed checks, reducing false-positive spam
  - Fixed dark mode flash on page load
  - Fixed history chart timeframes being shared instead of independent per chart
  - Fixed a fatal crash on fresh installs caused by an outdated Starlette TemplateResponse call
