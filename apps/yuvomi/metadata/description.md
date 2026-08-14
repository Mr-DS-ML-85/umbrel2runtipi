# Yuvomi

Self-hosted family planner — calendar, tasks, shopping, meals & budget

Yuvomi is a self-hosted, privacy-focused family planner that bundles everything a household needs into a single fast PWA — no cloud, no tracking, no ads.

Everything runs on your the server and stays on your the server.

✨ FEATURES

- Shared family calendar with recurring events, reminders and birthdays
- CalDAV / Google Calendar / Apple iCloud / ICS subscription sync
- Tasks with multi-assignment and due dates
- Shopping lists and a kitchen/meal planner
- Notes, contacts (CardDAV) and a household budget with recurring entries &
  split expenses

- Housekeeping: staff, chores and supplies
- Weather widget (Open-Meteo, no API key needed)
- Optional single sign-on via OIDC
- Full-text search across every module
- Installable PWA, mobile-first, dark mode, multi-language

🔒 PRIVACY

Yuvomi keeps all data in a local SQLite database (optionally encrypted with SQLCipher). Nothing leaves your device unless you explicitly enable a calendar or contacts sync to a provider you choose.

🛠️ SET-UP

Open Yuvomi from your the server dashboard and create the first account — that account becomes the family admin and can invite the rest of the household.

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/yuvomi/1.webp)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/yuvomi/2.webp)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/yuvomi/3.webp)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/yuvomi/4.webp)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/yuvomi/5.webp)

## Links

- Website: https://github.com/ulsklyc/yuvomi
- Repository: https://github.com/ulsklyc/yuvomi
- Support: https://github.com/ulsklyc/yuvomi/issues

## Release notes

There is nothing new to see in this update and nothing to do after it. It only adds documentation for people who write their own Yuvomi modules, describing how such a module talks to Yuvomi safely and keeps working across updates. The app itself, your data and your settings are unchanged.

Full release notes are available at https://github.com/ulsklyc/yuvomi/releases/tag/v2.7.1
