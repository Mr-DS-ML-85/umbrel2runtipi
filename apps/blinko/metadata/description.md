# Blinko

An AI-powered hub for your ideas and notes

😉 Blinko is an open-source application that combines note-taking, microblogging, pastebin functionality, task management, and AI-powered features in a self-hosted environment. The platform allows users to quickly and efficiently capture their thoughts, with full Markdown support for easy formatting.

With the integration of AI models like OpenAI or Ollama, content can be intelligently searched and organized.
If you want to use the Ollama instance of your the server, enter the following URL in the settings to connect to it: **http://ollama_ollama_1:11434**

The application provides a flexible way to manage notes, which can remain private or be shared publicly. Regular automatic backups and seamless data import and export ensure that users always retain control over their content. Since Blinko is self-hosted, users maintain full data sovereignty and can rely on a secure environment without commercial restrictions.

Built on Next.js, Blinko is optimized for speed and efficiency, offering a responsive and modern user experience. As an open-source project, it encourages collaboration and is available for free without hidden fees. It is designed for anyone looking for a powerful and customizable solution for digital organization.

---


## Preview

![Preview](./app/public/run-on-pikapods.svg)

## Links

- Website: https://blinko-demo.vercel.app/
- Repository: https://github.com/blinko-space/blinko
- Support: https://github.com/blinko-space/blinko/issues

## Release notes

This update includes new features, bug fixes, and improvements.

Key highlights in this version:
  - Added LiteLLM as an AI gateway provider option
  - Added streamable HTTP MCP support
  - Upgraded MiniMax provider models to M3 and removed older M2.5 options
  - Fixed note editor behavior, chat state resets, embedding delete errors, and Qwen prompt compatibility
  - Added Ukrainian localization and refreshed Japanese and German translations


Full release notes are available at https://github.com/blinko-space/blinko/releases/tag/1.8.8
