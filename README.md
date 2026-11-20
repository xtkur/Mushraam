# Mushraam

**P2P LAN chat over UDP broadcast. No server, no dependencies, single file.**

```
┌─────────────────────────────────────┐
│  Mushraam  │  Aurelius  │  Онлайн: 3  │
├─────────────────────────────────────┤
│  Aurelius  Marcus  Gaius            │
│  ─────────────────────────────────  │
│  [14:32] * Marcus присоединился к чату
│  [14:33] <Aurelius> привет всем
│  [14:33] <Marcus> ←Aurelius> пнг
│  [14:34] <Gaius> кого сюда звать?
│  > _                                  │
└─────────────────────────────────────┘
```

## Features

- **Zero config** — запустил, ввёл имя, в чате
- **P2P over UDP broadcast** — работает в локальной сети без сервера
- **Single file** — `Mushraam.py` (~1100 строк)
- **Terminal UI** — цвета, история ввода, прокрутка, inline-меню
- **Commands** — `/help`, `/clear`, `/enick`, `/ms`, `/language`, `/delconf`, `/exit`
- **Private messages** — `/ms имя текст` (в открытом виде)
- **Cross-platform** — Linux, macOS, Windows
- **Persisted config** — `mushraam.config` (имя, язык, порт)

## Requirements

- Python 3.10+
- Interactive TTY (не работает в CI/sandbox)

## Install & Run

```bash
git clone https://github.com/xtkur/Mushraam
cd Mushraam
python3 Mushraam.py
```

Первый запуск — интерактивная настройка (язык, имя, порт, сохранить конфиг).

## Commands

| Команда | Описание |
|---------|----------|
| `/help` | Справка |
| `/clear` | Очистить экран |
| `/enick <имя>` | Сменить ник |
| `/ms <имя> <текст>` | Личное сообщение |
| `/language <ru/en>` | Сменить язык |
| `/delconf` | Удалить конфиг |
| `/exit` | Выйти |

## How it works

- UDP broadcast на порт **50000** (настраивается)
- Heartbeat каждые 3 сек — держит список онлайн
- Таймаут 10 сек — помечает оффлайн
- JSON-сообщения: `join`, `ping`, `msg`, `pm`, `rename`, `bye`
- Без шифрования, без авторизации — доверенная LAN только

## Config

Создаётся автоматически: `mushraam.config`

```json
{
  "lang": "ru",
  "name": "Aurelius",
  "port": 50000
}
```

Удалить: `/delconf` или удалить файл.

## License

MIT — см. [LICENSE](LICENSE)

## Author

xtkur — 2026