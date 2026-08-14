# OctoPrint

A snappy web interface for your 3D printer

OctoPrint provides a snappy web interface for controlling consumer 3D printers. OctoPrint's powerful plugin system allows extending its functionality with awesome plugins from the community.

Plug your 3D printer into your Umbrel to control and monitor every aspect of your 3D printer and your printing jobs right from within your browser.

---

## Links

- Website: https://octoprint.org/
- Repository: https://github.com/OctoPrint/OctoPrint
- Support: https://community.octoprint.org/

## Release notes

This release fixes two security issues affecting OctoPrint 1.11.7 and earlier:
  - Fixed an XSS vulnerability in suppressed command notifications
  - Fixed a file exfiltration issue in upload endpoints


It also fixes a serial connection thread leak when connecting to a printer that does not respond to handshake attempts.

Full release notes can be found at https://github.com/OctoPrint/OctoPrint/releases/tag/1.11.8
