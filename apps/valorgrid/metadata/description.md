# ValorGrid

Private and auditable investment portfolio tracking

ValorGrid is a local-first portfolio tracker for recording, importing and analysing investment movements with SQLite persistence, local backups and a browser UI. Portfolio data stays on your Umbrel server; market price lookups are sent only to the configured market data provider for the requested symbol.

---

## Links

- Website: https://valorgrid.app
- Repository: https://github.com/aivm23/ValorGrid
- Support: https://github.com/aivm23/ValorGrid/issues

## Release notes

This release improves portfolio imports, charts, backups, and container security.
- Adds MyInvestor CSV as a known broker import adapter - Refreshes the portfolio history chart after editing a transaction - Improves backup filename uniqueness for rapid backup creation - Updates dependencies to address a security issue
