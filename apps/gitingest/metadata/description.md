# Gitingest

An effortless way to make Git repositories LLM-friendly

Gitingest is an open-source tool that converts Git repositories into structured, LLM-friendly text summaries, making it easier to analyze and process code with AI models like ChatGPT and Claude. By simply replacing "github.com" with "gitingest.com" in any repository URL, users can instantly generate an AI-optimized digest of the codebase. Additionally, a one-click button provides seamless integration with GitHub, ensuring a smooth workflow for developers.

The tool offers smart formatting to present repository content in a structured way that enhances prompt effectiveness for LLMs. Users can either rely on the default GitIngest service or configure their own setup for added flexibility. With a strong emphasis on privacy, Gitingest collects no data and works entirely offline, making it a secure choice for developers and organizations alike.

Gitingest is particularly useful for AI developers crafting precise prompts, teams working with AI-assisted development, and anyone who needs quick insights into a codebase. As part of the GitIngest ecosystem, it also provides CLI tools and Python packages for more advanced usage. Whether you're looking to streamline your AI-powered development workflow or improve your understanding of complex repositories, Gitingest offers a simple yet powerful solution.

---


## Preview

![Preview](https://getumbrel.github.io/umbrel-apps-gallery/gitingest/1.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/gitingest/2.jpg)
![Preview](https://getumbrel.github.io/umbrel-apps-gallery/gitingest/3.jpg)

## Links

- Website: https://gitingest.com/
- Repository: https://github.com/cyclotruc/gitingest
- Support: https://github.com/cyclotruc/gitingest/issues

## Release notes

This release brings new features and improvements to Gitingest.

New features include:
  - Support for Git submodules
  - Caching system to serve previously generated digests faster
  - Enhanced logging for better troubleshooting


Key improvements:
  - Better handling of large files with improved size processing
  - Improved cleanup of temporary files after processing
  - Better error handling for network issues during token estimation
  - Enhanced pattern matching for include and exclude rules


Bug fixes include:
  - Fixed cache handling for repository subpaths
  - Fixed directory tree display issues
  - Resolved container launch problems
  - Better processing of gitignore and gitingestignore files


Full release notes are found at https://github.com/cyclotruc/gitingest/releases
