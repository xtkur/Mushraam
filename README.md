# Mushraam

**P2P LAN chat over UDP broadcast. No server, no dependencies, single file.**

## Features

- **Zero config** — run, enter name, start chatting
- **P2P over UDP broadcast** — works on local network without a server
- **Single file** — `Mushraam.py` (~1100 lines)
- **Terminal UI** — colors, input history, scrolling, inline menus
- **Commands** — `/help`, `/clear`, `/enick`, `/ms`, `/language`, `/delconf`, `/exit`
- **Private messages** — `/ms name text` (plaintext)
- **Cross-platform** — Linux, macOS, Windows
- **Persisted config** — `mushraam.config` (name, language, port)

## Requirements

- Python 3.10+
- Interactive TTY (won't work in CI/sandbox)

## Install & Run

```bash
git clone https://github.com/xtkur/Mushraam
cd Mushraam
python3 Mushraam.py
```

First run — interactive setup (language, name, port, save config).

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/clear` | Clear chat screen |
| `/enick <name>` | Change nickname |
| `/ms <name> <text>` | Private message |
| `/language <ru/en>` | Change language |
| `/delconf` | Delete config |
| `/exit` | Exit chat |

## How it works

- UDP broadcast on port **50000** (configurable)
- Heartbeat every 3 sec — maintains online user list
- 10 sec timeout — marks users offline
- JSON messages: `join`, `ping`, `msg`, `pm`, `rename`, `bye`
- No encryption, no auth — trusted LAN only

## Config

Created automatically: `mushraam.config`

```json
{
  "lang": "en",
  "name": "Aurelius",
  "port": 50000
}
```

Delete: `/delconf` or remove the file.

## License

MIT — see [LICENSE](LICENSE)

## Author

xtkur — 2026