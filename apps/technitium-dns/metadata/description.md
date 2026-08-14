# Technitium DNS Server

Block ads & malware at the DNS level for your entire network

Technitium DNS Server is an open source authoritative, as well as recursive, DNS server that can be used for self hosting a DNS server for privacy & security. It works out-of-the-box with no or minimal configuration.

---

## Links

- Website: https://technitium.com/dns/
- Repository: https://github.com/TechnitiumSoftware/DnsServer
- Support: https://github.com/TechnitiumSoftware/DnsServer/discussions

## Default credentials

- Username: `admin`

## Release notes

⚠️ Security note from 15.3: Technitium DNS Server removed the default Delete permission from DNS Administrators in the Apps and Settings sections. Existing installations should manually remove that permission from DNS Administrators in those sections.

If you're updating from a pre-15 version, Technitium DNS Server 15.x runs on .NET 10. Most Umbrel users do not need to take action, but if you use Technitium clustering, upgrade all cluster nodes together for compatibility.

Key highlights include:
  - Fixed UDP socket binding issues that could affect response routing in some deployments
  - Fixed RFC compliance checks that could affect DNS resolution and zone transfers
  - Added Unix Domain Socket support for Web Service over HTTPS and DNS-over-HTTPS
  - Included other minor bug fixes and improvements


Full release notes can be found at https://github.com/TechnitiumSoftware/DnsServer/releases/tag/v15.4.0
