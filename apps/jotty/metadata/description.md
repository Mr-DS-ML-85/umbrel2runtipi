# Jotty

A simple app, for your checklists and notes

Tired of bloated, cloud-based to-do apps? Jotty is a lightweight alternative for managing your personal checklists and notes.

Features:
  - Checklists: Create task lists with drag & drop reordering, progress bars, and categories. Supports both simple checklists and advanced task projects with Kanban boards and time tracking.
  - Rich Text Notes: A clean WYSIWYG editor for your notes, powered by TipTap with full Markdown support and syntax highlighting.
  - Sharing: Share checklists or notes with other users on your instance, including public sharing with shareable links.
  - File-Based: No database needed! Everything is stored in simple Markdown and JSON files in a single data directory.
  - User Management: An admin panel to create and manage user accounts with session tracking.

---

## Links

- Website: https://jotty.page
- Repository: https://github.com/fccview/jotty
- Support: https://github.com/fccview/jotty/issues

## Release notes

This release includes a data migration. Please back up your Jotty data before updating.

Jotty now uses UUID-backed categories with metadata files, enabling folder sharing, sharing badges, inherited-access notices, and folder-sharing controls.

It also adds checklist emoji visibility preferences, border-radius customization, first-day-of-week preferences, note pinning from the note view, AVIF image support, and fixes for navigation, sharing permissions, ordering, Kanban operations, protected PWA manifest access, and due-date handling.

Full release notes can be found at https://github.com/fccview/jotty/releases/tag/1.26.0
