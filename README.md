# watchertoucher

A Jellyfin media library refresher that watches for filesystem changes and triggers library scans automatically.


## Features

- Watches your media library folder for new, deleted, or moved media files.
- Debounces multiple file changes and triggers Jellyfin library refresh with a configurable delay.
- Supports a variety of media file types and subtitle formats.
- Configurable via environment variables or `.env` file.
- Logs events to stdout and/or a log file.
- Dockerized for easy deployment.
- Uses polling observer for better compatibility with network filesystems.


## Usage

### Requirements

- Python 3.11+
- `watchdog`, `requests`, `python-dotenv` Python packages (installed via `pip install -r requirements.txt`)
- Jellyfin server with an API key

### Environment Variables

Configure your settings via a `.env` file or environment variables:

| Variable        | Description                                   | Example                      |
|-----------------|-----------------------------------------------|------------------------------|
| JELLYFIN_URL    | Jellyfin server URL                            | `http://127.0.0.1:8096`      |
| JELLYFIN_API_KEY| Jellyfin API token                             | `abc123yourtoken`             |
| MEDIA_FOLDER    | Absolute path to your media library            | `/mediaserver/libraries` or `/data` in Docker |
| LOG_TO_FILE     | Enable logging to file (`true` or `false`)     | `true`                       |
| LOG_TO_STDOUT   | Enable logging to stdout (`true` or `false`)   | `true`                       |
| LOGFILE         | Path to the log file                            | `/var/log/watchertoucher.log`|
| DELAY_SECONDS   | Delay before triggering refresh (to debounce) | `60`                         |
| POLL_TIMEOUT    | Polling observer timeout (seconds)             | `5`                          |

### Running locally

1. Clone the repo:

```bash
git clone https://github.com/yourusername/watchertoucher.git
cd watchertoucher/app
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r ../requirements.txt
```

4. Create `.env` file in root folder with your config.

5. Run the script:

```bash
python watchertoucher.py
```

---

### Using Docker

Build and run via Docker Compose:

1. Edit `.env` with your configuration.

2. Edit `docker-compose.yml` to mount your media folder correctly.

3. Run:

```bash
docker compose up -d
```

---

## Supported file types

- Video: `.mkv`, `.mp4`, `.avi`, `.m4v`, `.mov`, `.ts`, `.vob`, `.webm`
- Audio: `.mp3`, `.mp2`, `.ogg`, `.flac`, `.m4a`
- Subtitles: `.srt`, `.sub`, `.ass`, `.idx`, `.smi`



## License

MIT License


## Contributing

Feel free to open issues or pull requests to improve watchertoucher.

---
