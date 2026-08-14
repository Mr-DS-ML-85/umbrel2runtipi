# LocalAI

Drop-in OpenAI replacement

LocalAI is the free, Open Source OpenAI alternative. LocalAI act as a drop-in replacement REST API that's compatible with OpenAI API specifications for local inferencing.

It allows you to run LLMs, generate images, audio locally with consumer grade hardware, supporting multiple model families and architectures.

⚠️ Note
Before running a model, make sure your device has enough free RAM to support it. Attempting to run a model that exceeds your available memory could cause your device to crash or become unresponsive. Always check the model requirements before downloading or starting it.

---

## Links

- Website: https://localai.io/
- Repository: https://github.com/mudler/LocalAI
- Support: https://github.com/mudler/LocalAI/discussions

## Release notes

If you installed a backend in a LocalAI version before backend persistence was added, you may need to reinstall it once after updating.

This update improves the model gallery with cached indexes and mirror fallbacks when the primary gallery source is unavailable.

It also adds the NVIDIA NeMo-Speech.cpp backend and refreshes API docs and model gallery metadata.

Full release notes can be found at https://github.com/mudler/LocalAI/releases/tag/v4.8.2
