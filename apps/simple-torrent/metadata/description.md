# SimpleTorrent

Download torrents with your the server

SimpleTorrent is a a self-hosted remote torrent client that starts torrents remotely, download sets of files on your the server, which are then retrievable or streamable via web browser over HTTP. This project is a re-branded fork of cloud-torrent by jpillora. Features:

- Individual file download control
- Run external program on tasks completion: DoneCmd
- Stops task when seeding ratio reached: SeedRatio
- Download/Upload speed limiter: UploadRate/DownloadRate
- Detailed transfer stats in web UI.
- Torrent Watcher
- Extra trackers from external source
- Protocol Handler to magnet:
- Magnet RSS subscribing supported

⚠️ SimpleTorrent downloads torrents over the Clearnet, not Tor.

---

## Links

- Website: https://github.com/boypt
- Repository: https://github.com/boypt/simple-torrent
- Support: https://github.com/boypt/simple-torrent/issues

## Release notes

- SimpleTorrent now utilizes the shared downloads folder that can be accessed by other apps on Umbrel, such as Jellyfin, File Browser, Transmission, Plex, and more.
