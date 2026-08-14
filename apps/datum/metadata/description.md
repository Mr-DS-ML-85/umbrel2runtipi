# DATUM

Self-sovereign Bitcoin mining

⚙️ Please read the important setup instructions at the bottom of this page.

DATUM (Decentralized Alternative Templates for Universal Mining) is a brand new bitcoin mining protocol that allows you to create your own block templates using your own Bitcoin node.

With DATUM on the server, you gain full control over your Bitcoin mining setup, allowing you to use your own Bitcoin node to generate custom block templates and directly issue work to your miners. DATUM enables you to either solo mine or participate in pool mining while optimizing block creation without relying on third-party servers.

Over the years, mining has drifted toward centralization, with large pools dominating the process and reducing miners to mere sellers of hash power. DATUM seeks to bring back the core principle of Bitcoin: decentralization, giving miners direct control over the block construction process once again.

🛠️ SET-UP INSTRUCTIONS

### Bitcoin Node:

Datum connects automatically to your Bitcoin Knots app upon installation. A full archival node is not required for mining, so you may wish to prune your node to save disk space. You can adjust this setting under Advanced Settings in the Bitcoin Knots app.

### Configuring DATUM:

⚠️ The DATUM team is aware that Safari currently cannot be used to change configuration settings within the app. Please use a different browser to change settings.

In order for DATUM to be fully initialized, you need to add your Bitcoin address in the "Config" tab within the DATUM app. This is the default address that mining rewards will be sent to. Your in-app credentials needed to change settings can be found by right-clicking on the DATUM app icon from your the server homescreen and selecting "Show default credentials".

### Connecting Your Miner:

Refer to your miner's documentation for specific setup details. Here's a general guide to connect your miner with Datum:

  - Stratum URL/Host/Pool: Use your the server device’s IP address (found in Settings on the the server home screen) and port 23334.
  e.g., stratum+tcp://192.168.4.56:23334

  - Username/Worker: Enter the Bitcoin address for receiving OCEAN rewards. Optionally, add a worker name after a period to identify your miner.
  e.g., bc1qabcdefghijklmnopqrstuvwxyz or bc1qabcdefghijklmnopqrstuvwxyz.bitaxe

  - Password: Leave blank or enter any value if your miner requires a password.


For more information on Datum, please visit https://github.com/OCEAN-xyz/datum_gateway

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/datum/1.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/datum/2.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/datum/3.jpg)

## Links

- Website: https://ocean.xyz
- Repository: https://github.com/OCEAN-xyz/datum_gateway
- Support: https://ocean.xyz

## Default credentials

- Username: `admin`

## Release notes

This update improves DATUM Gateway stability for setups with many connected miners by increasing the service's open file limit to match the Debian DATUM Gateway package. No action is required after updating.
