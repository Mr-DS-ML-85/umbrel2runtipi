# umbrel2runtipi

A Runtipi-compatible app store built by converting apps from the [Umbrel App Store](https://apps.umbrel.com) that are **not** already available in the [official Runtipi appstore](https://github.com/runtipi/runtipi-appstore).

## Usage

Add this repository as a custom app store in your Runtipi instance:

1. Settings → App Stores → **Add App Store**
2. Paste this repository's URL (or clone it and point Runtipi at the local folder)
3. Click **Update App Stores**

## Stats

- **191 apps** converted from Umbrel
- 123 Umbrel apps skipped because they already exist in the official Runtipi store (deduped by id / normalized id / normalized name / verified image alias)
- 77 apps skipped because they depend on Umbrel-only infrastructure (Bitcoin/Lightning/Electrs/Monero system nodes, Tor)
- See `conversion-report.md` for the full breakdown.

## Image tags

Images are pinned to **`latest`** where the registry publishes a `latest` tag
(Docker Hub, GHCR, Quay). For images whose registries do **not** maintain a
`latest` tag (e.g. `seafileltd/sdoc-server`, `secondark/bark-web`,
`toshimoto821/toshi-moto`, GHCR images that only publish `main`/version tags),
the newest available version tag is resolved at conversion time by querying the
registry APIs, and that tag is pinned instead. Pinned digests (`@sha256:…`)
are stripped so images always resolve to the tag at install time.

## Layout

```
apps/
  <app-id>/
    config.json          # Runtipi app manifest
    docker-compose.yml   # dynamic compose (x-runtipi schema v2)
    metadata/
      description.md
      logo.jpg
app-info-schema.json     # official Runtipi app schema
scripts/validate.py      # local validation
tools/
  convert.py             # Umbrel -> Runtipi converter
  update_tags.py         # image tag resolver (latest / registry API)
```

## Converting / regenerating

```bash
git clone https://github.com/getumbrel/umbrel-apps.git      # or refresh your clone
git clone https://github.com/runtipi/runtipi-appstore.git   # clone as runtipi-official/
python3 tools/convert.py      # regenerates apps/ + conversion-report.md
python3 tools/update_tags.py  # resolves image tags to latest / newest
python3 scripts/validate.py   # sanity-check the result
```

The converter reads the local clones of `umbrel-apps/` and `runtipi-official/`,
dedupes against the Runtipi registry, and rewrites `umbrel-app.yml` +
`docker-compose.yml` into the Runtipi dynamic-compose format.

### Port handling

Host ports assigned to apps never collide with:

- ports already used by the official Runtipi store,
- the reserved ports already in use on the author's server
  (see `RESERVED_PORTS` in `tools/convert.py`), or
- any other converted app.

## Skipped apps (77)

These Umbrel apps were **not** converted. They all depend on Umbrel-only
infrastructure (system Bitcoin / Lightning / Electrs / Monero nodes, Tor hidden
services, `$UMBREL_ROOT/app-data`) that does not exist on Runtipi, so they cannot
run there.

### Lightning (36)

agora · alby-nostr-wallet-connect · bleskomat-server · bluewallet · bolt12-pay · circuitbreaker · core-lightning · core-lightning-rtl · helipad · kollider · lightning · lightning-shell · lightning-terminal · lightningmate · ln-visualizer · lnbits · lndboss · lndg · lnmarkets · lnplus · lnswitchboard · nolooking · oak-node · ride-the-lightning · saifa · satsale · satsbook · sparkkiosk · sphinx-relay · squeaknode · squeakroad · tallycoin-connect · thunderhub · torq · usocial · woofbot-lnd

### Bitcoin / Electrs / Monero (31)

bassin · bitbalance · bitcoin · bitcoin-cash-node · bitcoin-knots · bitfeed · btc-rpc-explorer · btcpay-server · canary · chainforensics · electrumx · elements · fedimint-gateway · fedimintd · fulcrum · gobrrr-pool · hashrate-autopilot · itchysats · jam · joinstr · ordinals · peerswap · pogolo · public-pool · samourai-server · satwatch · specter-desktop · suredbits-wallet · sv2-ui · urbit-bitcoin-connector · woofbot

### Umbrel-specific / other (10)

albyhub · am-i-exposed · blockstream-blind-oracle · chantools · libre-relay · monero · paperclip · solidtime · synapse · tdex

> The exact `APP_*` variables each app needs are listed in `conversion-report.md`
> under **"Skipped: require Umbrel bitcoin/lightning infra"**.

## Limitations

The conversion is best-effort; these known limitations apply:

- **Missing system nodes** — the 77 skipped apps above reference Umbrel-only
  services (`APP_BITCOIN_NODE_IP`, `APP_LIGHTNING_NODE_*`, `APP_ELECTRS_NODE_*`,
  `APP_MONERO_*`, Tor hidden services, `$UMBREL_ROOT/app-data`) that do not exist
  on Runtipi, so they cannot run.
- **Host networking** — apps that use `network_mode: host` (AdGuard Home,
  Homey, Music Assistant, OpenThread Border Router, Technitium DNS) are converted
  best-effort; their ports may need manual configuration.
- **`env_file` removal** — env files created by Umbrel install hooks
  (e.g. `settings.env`, `config/prod.env`, `.env`) do not exist on Runtipi and
  were removed. Affected apps may need their settings set manually in the
  Runtipi UI after install.
- **Secret vars** — Umbrel `APP_PASSWORD` / `APP_SEED` / `APP_*_KEY` become
  Runtipi `type: random` form fields, generated per-install rather than stored
  in the repo.
- **Sibling-app integrations** — Umbrel lets apps talk to each other (Mempool,
  Tor, etc.) via env vars; Runtipi has no equivalent, so such wiring is dropped.
- **`latest` tags** — see *Image tags* above; versions are not pinned by digest,
  so updates can change behavior.

## Notes / caveats

- Apps that used Umbrel's `app_proxy` service are converted to Runtipi's
  Traefik routing (`x-runtipi: is_main + internal_port`).
- Umbrel `APP_PASSWORD` / `APP_SEED` / other secret env vars become Runtipi
  `type: random` form fields.
- Shared downloads/media mounts are remapped from `$UMBREL_ROOT/data/storage/...`
  to `$RUNTIPI_MEDIA_DIR/...`.
- A few apps run with `network_mode: host` on Umbrel (e.g. Home Assistant,
  AdGuard Home, Plex, Pi-hole). They are converted best-effort but may need
  manual port configuration and are flagged in `conversion-report.md`.
