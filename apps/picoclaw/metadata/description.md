# PicoClaw

Ultra-lightweight personal AI assistant

PicoClaw is an ultra-lightweight personal AI assistant written in Go and designed to run efficiently on low-cost hardware with a small memory footprint and fast startup times.

PicoClaw provides a browser-based WebUI Launcher for configuring model providers, chat channels, tools, and the gateway process. It supports multiple LLM providers, MCP integration, multimodal file and image handling, web search tools, smart model routing, and chat app channels for building a compact self-hosted AI assistant.

After opening PicoClaw, define your password, add your LLM provider API key, configure a channel such as Telegram if desired, start the gateway, and begin chatting.

---

## Links

- Website: https://picoclaw.io
- Repository: https://github.com/sipeed/picoclaw
- Support: https://github.com/sipeed/picoclaw/issues

## Release notes

This release adds the NEAR AI Cloud provider, configurable channel settings, and support for configured remote cron commands.
It improves provider/model error handling, native search handling, gateway startup reporting, and Brave/web search diagnostics. It also fixes Evolution heartbeat and file-lock handling, Telegram forum topics, Gemini thought signatures, media and WebSocket cleanup paths, and hardens inbound media/web fetch handling.
Full release notes can be found at https://github.com/sipeed/picoclaw/releases/tag/v0.3.1
