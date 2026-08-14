# Agent Zero

A personal, organic agentic framework that grows and learns with you

Agent Zero is a personal, organic agentic framework that grows and learns with you. It is fully Dockerized and includes features like Speech-to-Text and TTS.

**Key Features:**
  - **General Purpose Assistant:** Can handle various tasks.
  - **Computer Use:** Can use the computer (in the container).
  - **Coding:** Can write and execute code.
  - **Memory:** Learns from interactions.


**Getting Started:**
  1. Launch Agent Zero.
  2. Configure your models in the settings.


⚠️ **Warning:** Agent Zero can execute code. Run with caution.

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/agent-zero/1.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/agent-zero/2.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/agent-zero/3.jpg)

## Links

- Website: https://github.com/agent0ai/agent-zero
- Repository: https://github.com/agent0ai/agent-zero
- Support: https://github.com/agent0ai/agent-zero/issues

## Release notes

Agent Zero v2.9 is a follow-up to the recent v2.0 major update. If you're updating from a pre-v2.0 version, Agent Zero recommends creating a backup from Settings > Check for Updates > Backup & Restore before upgrading, then checking chats, projects, memory, settings, and plugins after the update.

Important changes in this release:
  - Adds the Agent Editor for creating and managing agent profiles, prompts, model presets, tool policies, skills, avatars, and project-scoped profiles from the WebUI
  - Adds scoped tool and skill policies so local, plugin, MCP, and skill access can be controlled per project/profile
  - Adds `/profile` and `/permissions` chat commands plus profile duplication, restore, and switching improvements
  - Bundles the Migrate Agents plugin and improves native Kokoro voice blending, plugin settings, and capability discovery
  - Adds time-travel shadow-repo cleanup for deleted or stale chat history
  - Fixes a document-query SSRF issue, file download path resolution, chat deletion validation, project update persistence, provider fallback behavior, plugin edit preservation, Codex OAuth headers, desktop canvas resizing, and several WebUI polish issues


Full release notes can be found at https://github.com/agent0ai/agent-zero/releases/tag/v2.9
