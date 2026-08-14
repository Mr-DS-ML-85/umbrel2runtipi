# Mattermost

Team Chat, Open Source, Self-Hosted

🚉 Mattermost is an open-source platform designed for secure collaboration throughout the software development lifecycle.

💬 It serves as a team messaging application that emphasizes developer productivity and the benefits of open-source software.

💾 Mattermost offers a self-hosted alternative to proprietary SaaS messaging services such as Slack and Microsoft Teams.

Note: Mattermost can be used locally within your network. However, if you want others outside your local network to access your server, you'll need to make it accessible on the public internet. If you have a domain name, you can set this up using the Cloudflare Tunnel or Nginx Proxy Manager apps in the Umbrel Apps Store.

---

## Links

- Website: https://mattermost.com
- Repository: https://github.com/mattermost/mattermost
- Support: https://forum.mattermost.com/

## Release notes

Mattermost 11.9.0 adds Azure Blob Storage support, image-preview zoom and pan controls, incoming webhook last-triggered visibility, personal access token lifetime controls, and updated bundled plugins for Calls, Boards, Playbooks, Jira, GitLab, and Agents.

This release includes database migrations that upstream says do not require downtime, though very large workspaces may take longer to remove orphaned thread memberships.

Note: OAuth Dynamic Client Registration redirect URI allowlist patterns now match URL components separately. Admins using DCR allowlists should review their patterns after updating.

Full release notes can be found at https://docs.mattermost.com/product-overview/mattermost-v11-changelog.html#release-v11-9-feature-release
