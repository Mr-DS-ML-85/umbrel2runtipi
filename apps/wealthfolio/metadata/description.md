# Wealthfolio

Private investment portfolio tracking

Wealthfolio is an open source investment portfolio tracker for monitoring holdings, accounts, performance, and market activity from your own server. It is designed for private wealth tracking, with a browser-based dashboard and local SQLite storage for portfolio data.

Use Wealthfolio to keep a self-hosted view of your investments without sending portfolio details to a third-party tracking service. It supports portfolio and account management, performance views, market data workflows, and a focused web interface for personal finance monitoring.

---

## Links

- Website: https://wealthfolio.app/
- Repository: https://github.com/wealthfolio/wealthfolio
- Support: https://github.com/wealthfolio/wealthfolio/issues

## Release notes

Wealthfolio 3.6.3 is a stability release focused on faster, lighter portfolio calculations for large histories.

First launch after updating may take longer than usual while Wealthfolio rebuilds derived data and rewrites the SQLite database to reclaim disk space. Let it finish before closing the app.

Valuation now uses a sparse keyframe timeline with batched quotes to avoid memory spikes, and performance statistics avoid repeated cold calculations that could time out.

Database snapshots no longer duplicate full lot data, SQLite tuning was improved, imports are validated before they are applied, and unsupported dates or skipped accounts are handled more safely.

This release also fixes holdings-mode gains, quote-gap dashboards, rebalance target sizing, CSV currency backfills, bulk activity validation, cash dividend/interest edits, TWR edge cases, BRL custom provider prices, add-on navigation layout issues, and clears most open Dependabot advisories.

Full release notes can be found at https://github.com/wealthfolio/wealthfolio/releases/tag/v3.6.3
