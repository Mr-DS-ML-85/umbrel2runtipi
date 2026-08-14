# JupyterLab

Next-generation web interface for interactive computing and data science

JupyterLab is a next-generation web-based user interface for Project Jupyter. 

It enables you to work with documents and activities such as Jupyter notebooks, text editors, terminals, and custom components in a flexible, integrated, and extensible manner. You can arrange multiple documents and activities side by side in the work area using tabs and splitters.

Key features and workflows include:
  - Code Consoles for interactive code execution and linking to a notebook kernel.
  - Kernel-backed documents that allow code in any text file (Markdown, Python, LaTeX) to be run interactively.
  - Mirrored cell outputs for simple dashboards.
  - Multiple views of documents with different editors or viewers (e.g., live preview of Markdown or CSV).
  - A unified model for viewing and handling data formats (images, CSV, JSON, PDF, Vega, etc.).
  - Customizable keyboard shortcuts and an extensible architecture.


JupyterLab uses the same notebook document format as the classic Jupyter Notebook.

---

## Links

- Website: https://jupyterlab.readthedocs.io/en/latest/
- Repository: https://github.com/jupyterlab/jupyterlab
- Support: https://github.com/jupyterlab/jupyterlab/issues

## Release notes

This release includes security and workflow fixes for JupyterLab:
  - Patches multiple security issues affecting image viewing, extension blocklists, plugin manager rules, and crafted settings files.
  - Fixes platform-specific keyboard shortcuts and stale Table of Contents error markers.
  - Improves document loading after file renames, notebook initialization focus behavior, and kernel restart timing.


Full release notes can be found at https://github.com/jupyterlab/jupyterlab/releases/tag/v4.6.2
