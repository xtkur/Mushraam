# Mushraam

Single-file terminal app: peer-to-peer LAN chat over UDP broadcast. No server, no tests, no build step.

## Run

- `python3 Mushraam.py` (or `python Mushraam.py`). Requires an interactive TTY; exits E001 otherwise.
- Python 3.13 target (bytecode in `__pycache__`); runs on 3.14 in practice.

## Structure

- Everything lives in `Mushraam.py` (~1139 lines). No packages/modules.
- Persisted state: `mushraam.config` (lang/name/port), created on first run via inline arrow selection.

## Conventions / gotchas

- No tests/lint/typecheck commands exist; don't invent them.
- Interactive TTY required; cannot run in CI/sandbox meaningfully.
- Broadcasts UDP on port 50000 to whole segment; no encryption or auth.
- Codename for this file: `md`.
- Respond in Russian.
- Update this file after a prompt if there's something important to record.
- Don't commit secrets: none used, but `mushraam.config` holds user name/port.