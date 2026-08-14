# Wavelog

Amateur radio logging software

⚠️ See below for important set-up instructions.

 Wavelog is a powerful web-based amateur radio logging application that allows you to log and manage your radio contacts with ease. It supports various features like QSO logging, award tracking, and integration with online services like LoTW and eQSL.

🛠️ SET-UP INSTRUCTIONS

 During the setup wizard, you will be prompted to configure the application's database connection. Please use the following settings:

  - Hostname: wavelog-db
  - Database: wavelog
  - Username: wavelog
  - Password: wavelog

This ensures that the app will connect to the correct database and function properly.

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/wavelog/1.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/wavelog/2.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/wavelog/3.jpg)

## Links

- Website: https://www.wavelog.org
- Repository: https://github.com/wavelog/wavelog
- Support: https://github.com/wavelog/wavelog/issues

## Release notes

Wavelog 3.1.0 introduces APIv2 for third-party services alongside the legacy API. If you use WavelogGate, update it to a version with APIv2 support. If you're updating from a pre-3.0.0 version, note that Wavelog 3.0.0 introduced a new multiuser contesting engine and QSL card designer.

This release adds the Activation Planner, a new AMSAT satellite status page, improved satellite QSO handling, QSL/confirmation API endpoints, station UUIDs in the Station API, and new SOTA/POTA/WWFF award maps and database-backed reference data.

It also improves Advanced Logbook row actions, contest serial reservations, Cronmanager safeguards, Wavelog installer behavior, club-member bulk editing, OQRS validation, QSL label/queue workflows, propagation filters, imports, maps, and several dashboard, logbook, satellite, and award views.

Full release notes can be found at https://github.com/wavelog/wavelog/releases/tag/3.1.0
