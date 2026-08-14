# Trip

Minimalist Map Tracker and Trip Planner

🗺️ TRIP is a self-hostable minimalist Map tracker and Trip planner to visualize your points of interest (POI) and organize your next adventure details.

Core Features:
  - Map and manage POIs on interactive maps
  - Plan multi-day trips with detailed itineraries
  - Collaborate and share with travel companions


No telemetry. No tracking. No ads. Free, forever.

---

## Links

- Website: https://itskovacs-trip.netlify.app/
- Repository: https://github.com/itskovacs/trip
- Support: https://github.com/itskovacs/trip/issues

## Release notes

This update reworks the Trip API and API-key authentication. API keys now authenticate normal API requests with the `X-Api-Token` header; scripts using the old `/api/token/...` endpoints must be updated.
It also adds calendar sync, MCP server tools, admin-configurable size limits for backups and provider imports, improved links UI, booking-day editing, day-notes toggles, packing suggestions, and link editing from place and item dialogs.
It fixes packing and checklist models.
Full release notes can be found at https://github.com/itskovacs/trip/releases/tag/1.47.0
