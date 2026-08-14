# Rusty Kaspad

A Rust implementation of a Kaspa full node

Rusty Kaspad is a Rust implementation of a Kaspa full node. This node software provides essential Kaspa network services including peer-to-peer networking and RPC functionality.

Kaspa is a proof-of-work cryptocurrency with instant transaction confirmation through blockDAG technology.

The very heart of Kaspa is the public nodes. Please consider making your node public by forwarding TCP port 16111 on your firewall to your Umbrel node IP address to support the network.

This package uses the Docker container maintained by [supertypo](https://hub.docker.com/r/kaspanet/rusty-kaspad), based on [Rusty Kaspa](https://github.com/kaspanet/rusty-kaspa).

Packaged for Umbrel by Luke Dunshea (https://dunshea.au).

---

## Links

- Website: https://github.com/kaspanet/rusty-kaspa
- Repository: https://github.com/kaspanet/rusty-kaspa
- Support: https://github.com/elldeeone/umbrel-community-app-store/pulls

## Release notes

This release updates Rusty Kaspa to v2.0.1, a drop-in maintenance update for v2.0.0 nodes.

Key highlights in this release:
  - New RPC support for Toccata seq-commit state and lane proofs
  - Wallet/core and Wasm notifications for SMT sync progress
  - SMT database inspection tooling for operators and developers
  - Improved transaction-generation tooling for user-lane workflows
  - Node sync and error-reporting refinements
  - Refined covenant binding handling across client and wallet components


Full release notes can be found at https://github.com/kaspanet/rusty-kaspa/releases

All mainnet operators are encouraged to upgrade from v2.0.0 to v2.0.1.
