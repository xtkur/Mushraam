import socket
import threading
import json
import time
import os
import sys
import shutil
import select
try:
    import readline
except Exception:
    readline = None
import io
import locale
from datetime import datetime

try:
    locale.setlocale(locale.LC_ALL, '')
except Exception:
    pass

try:
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stdin, 'buffer'):
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass

IS_WINDOWS = os.name == 'nt'

if IS_WINDOWS:
    import msvcrt
    import ctypes
else:
    import termios
    import tty


CONFIG_FILE = 'mushraam.config'

import random

NAMES = ['Aurelius','Quintus','Lucius','Marcus','Gaius','Titus','Publius','Sextus','Aulus','Decimus','Flavius','Claudius','Valerius','Cornelius','Octavius','Julius','Antonius','Cassius','Livius','Terentius','Fabius','Horatius','Sergius','Tullius','Vipsanius','Aemilius','Caecilius','Domitius','Junius','Manlius','Numerius','Oppius','Postumus','Spurius','Tiberius','Vergilius','Aulus','Servius','Appius','Hostus','Camillus','Crispus','Faustus','Felix','Gratus','Magnus','Maximus','Priscus','Rufus','Severus']

def random_name():
    return random.choice(NAMES)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def save_config(cfg):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

PORT = 50000
BROADCAST_IP = '<broadcast>'
HEARTBEAT_INTERVAL = 3
TIMEOUT = 10
LANG = 'ru'

L = {
 'ru': {
   'terminal_small': 'Терминал слишком мал',
   'online': 'Онлайн',
   'no_users': 'Нет активных пользователей',
   'help_title': 'Доступные команды:',
   'help_this': 'эта справка',
   'help_clear': '/clear — очистить экран чата',
   'help_delconf': '/delconf — удалить конфиг',
   'help_language': '/language <ru/en> — сменить язык',
   'help_enick': '/enick <имя> — сменить ник',
   'help_ms': '/ms <имя> <текст> — личное сообщение (в открытом виде)',
   'help_exit': '/exit — выйти из чата',
   'usage_language': 'Использование: /language <ru/en>',
   'usage_enick': 'Использование: /enick <новое имя>',
   'same_lang': 'Такой язык уже установлен',
   'name_no_spaces': 'Имя не должно содержать пробелов',
   'now_known': 'теперь известен как «{new}»',
   'you_are_now': 'Вы теперь «{new}»',
   'usage_ms': 'Использование: /ms <имя> <текст>',
   'empty_msg': 'Пустое сообщение',
   'unknown_cmd': 'Неизвестная команда: {cmd} (см. /help)',
   'left_chat': 'вышел из чата',
   'timeout': 'отключился (таймаут)',
   'tty_required': 'Требуется интерактивный терминал (TTY).',
   'your_name': 'Ваше имя: ',
   'port_prompt': 'Порт (по умолч. 50000): ',
   'bad_port': 'Неверный порт.',
   'exit': 'Выход.',
   'save_config': 'Сохранить конфиг? (y/n): ',
   'choose_lang': 'Choose language (ru/en): ',
   'joined': 'присоединился к чату',
   'config_deleted': 'Конфиг удалён',
   'config_error': 'Ошибка',
   'config_not_exists': 'Конфиг не существует',
   'language_set': 'Язык установлен',
   'user_offline': 'Пользователь не в сети',
   'cant_msg_self': 'Нельзя отправить сообщение самому себе',
   'config_already_deleted': 'Конфиг уже удалён',
 },
 'en': {
   'terminal_small': 'Terminal too small',
   'online': 'Online',
   'no_users': 'No active users',
   'help_title': 'Available commands:',
   'help_this': 'this help',
   'help_clear': '/clear — clear chat screen',
   'help_delconf': '/delconf — delete config',
   'help_language': '/language <ru/en> — change language',
   'help_enick': '/enick <name> — change nickname',
   'help_ms': '/ms <name> <text> — private message (plaintext)',
   'help_exit': '/exit — exit chat',
   'usage_language': 'Usage: /language <ru/en>',
   'usage_enick': 'Usage: /enick <new name>',
   'same_lang': 'This language is already set',
   'name_no_spaces': 'Name must not contain spaces',
   'now_known': 'now known as «{new}»',
   'you_are_now': 'You are now «{new}»',
   'usage_ms': 'Usage: /ms <name> <text>',
   'empty_msg': 'Empty message',
   'unknown_cmd': 'Unknown command: {cmd} (see /help)',
   'left_chat': 'left the chat',
   'timeout': 'disconnected (timeout)',
   'tty_required': 'Interactive terminal (TTY) required.',
   'your_name': 'Your name: ',
   'port_prompt': 'Port (default 50000): ',
   'bad_port': 'Invalid port.',
   'exit': 'Exit.',
   'save_config': 'Save config? (y/n): ',
   'choose_lang': 'Choose language (ru/en): ',
   'joined': 'joined the chat',
   'config_deleted': 'Config deleted',
   'config_error': 'Error',
   'config_not_exists': 'Config does not exist',
   'language_set': 'Language set',
   'user_offline': 'User not online',
   'cant_msg_self': 'Cannot send message to yourself',
   'config_already_deleted': 'Config already deleted',
 }
}

def t(key, **kw):
    s = L.get(LANG, L['ru']).get(key, key)
    return s.format(**kw) if kw else s


# ------------------- colors -------------------

class C:
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    REV     = '\033[7m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    GRAY    = '\033[90m'


PALETTE = [C.CYAN, C.MAGENTA, C.YELLOW, C.BLUE, C.GREEN, C.RED]


def color_for(name):
    return PALETTE[sum(ord(c) for c in name) % len(PALETTE)]


# ------------------- terminal -------------------

class Terminal:
    def __init__(self):
        if IS_WINDOWS:
            try:
                k = ctypes.windll.kernel32
                h = k.GetStdHandle(-11)
                mode = ctypes.c_uint32()
                k.GetConsoleMode(h, ctypes.byref(mode))
                k.SetConsoleMode(h, mode.value | 0x0004)
            except Exception:
                pass
            self.restore = lambda: None
        else:
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            tty.setraw(self.fd)

            def _restore():
                try:
                    termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
                except Exception:
                    pass
            self.restore = _restore

    def read_key(self, timeout=0.05):
        if IS_WINDOWS:
            try:
                import msvcrt
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    if ch in ('\x00', '\xe0'):
                        try:
                            ch2 = msvcrt.getwch()
                            if ch2 == 'H':
                                return 'UP'
                            if ch2 == 'P':
                                return 'DOWN'
                            if ch2 == 'K':
                                return 'LEFT'
                            if ch2 == 'M':
                                return 'RIGHT'
                            if ch2 == 'G':
                                return 'HOME'
                            if ch2 == 'O':
                                return 'END'
                            if ch2 == 'S':
                                return '\x1b[3~'
                        except Exception:
                            pass
                        return None
                    return ch
                time.sleep(timeout)
                return None
            except Exception:
                time.sleep(timeout)
                return None
        else:
            try:
                r, _, _ = select.select([sys.stdin], [], [], timeout)
                if not r:
                    return None
                first = os.read(self.fd, 1)
                if not first:
                    return None
                b = bytearray(first)
                if b[0] & 0x80:
                    if b[0] & 0xE0 == 0xC0:
                        try:
                            b += os.read(self.fd, 1)
                        except Exception:
                            pass
                    elif b[0] & 0xF0 == 0xE0:
                        try:
                            b += os.read(self.fd, 2)
                        except Exception:
                            pass
                    elif b[0] & 0xF8 == 0xF0:
                        try:
                            b += os.read(self.fd, 3)
                        except Exception:
                            pass
                try:
                    ch = bytes(b).decode('utf-8')
                except Exception:
                    ch = bytes(b).decode('utf-8', 'replace')
                if ch == '\x1b':
                    seq = ch
                    while True:
                        r2, _, _ = select.select([self.fd], [], [], 0.05)
                        if not r2:
                            break
                        try:
                            fb = os.read(self.fd, 1)
                            if not fb:
                                break
                            bb = bytearray(fb)
                            if bb[0] & 0x80:
                                if bb[0] & 0xE0 == 0xC0:
                                    bb += os.read(self.fd, 1)
                                elif bb[0] & 0xF0 == 0xE0:
                                    bb += os.read(self.fd, 2)
                                elif bb[0] & 0xF8 == 0xF0:
                                    bb += os.read(self.fd, 3)
                            seq += bytes(bb).decode('utf-8', 'replace')
                        except Exception:
                            break
                        if len(seq) > 4096:
                            break
                        if seq.endswith('\x1b[201~'):
                            break
                    return seq
                return ch
            except (KeyboardInterrupt, IOError, OSError):
                return None


# ------------------- state -------------------

class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.users = {}            # name -> monotonic
        self.messages = []         # (ts, kind, name, text, to)
        self.input_buf = ''
        self.input_pos = 0
        self.input_history = []
        self.history_idx = -1
        self.history_stash = ''
        self.running = True
        self.my_name = ''
        self.dirty = True
        self._renaming_from = None


state = State()


# ------------------- network -------------------

def send(sock, payload):
    try:
        sock.sendto(json.dumps(payload, ensure_ascii=False).encode('utf-8'), (BROADCAST_IP, PORT))
    except OSError:
        pass


def make_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(('', PORT))
    return s


def receiver(sock):
    while state.running:
        try:
            data, _ = sock.recvfrom(65535)
            msg = json.loads(data.decode('utf-8'))
        except Exception:
            if not state.running:
                break
            continue

        name = msg.get('name')
        kind = msg.get('type')
        if not name:
            continue

        ts = datetime.now().strftime('%H:%M:%S')

        if kind == 'rename':
            old = name
            new = msg.get('new', '')
            if old == getattr(state, '_renaming_from', None) and new == state.my_name:
                continue  # skip our own rename echo
            with state.lock:
                state.users.pop(old, None)
                if new and new != state.my_name:
                    state.users[new] = time.monotonic()
                state.messages.append((ts, 'sys', old, t('now_known', new=new), None))
                state.dirty = True
                if len(state.messages) > 500:
                    del state.messages[:len(state.messages) - 500]
            continue

        if name == state.my_name:
            continue

        with state.lock:
            if kind == 'join':
                is_new = name not in state.users
                state.users[name] = time.monotonic()
                if is_new:
                    state.messages.append((ts, 'sys', name, t('joined'), None))
                state.dirty = True
            elif kind == 'ping':
                is_new = name not in state.users
                state.users[name] = time.monotonic()
                if is_new:
                    state.messages.append((ts, 'sys', name, t('joined'), None))
                state.dirty = True
            elif kind == 'msg':
                state.users[name] = time.monotonic()
                state.messages.append((ts, 'msg', name, msg.get('text', ''), msg.get('to')))
                state.dirty = True
            elif kind == 'pm':
                if msg.get('to') == state.my_name:
                    state.messages.append((ts, 'pm', name, msg.get('text', ''), state.my_name))
                    state.dirty = True
            elif kind == 'bye':
                state.users.pop(name, None)
                state.messages.append((ts, 'sys', name, t('left_chat'), None))
                state.dirty = True

            if len(state.messages) > 500:
                del state.messages[:len(state.messages) - 500]


def heartbeat(sock):
    while state.running:
        send(sock, {'type': 'ping', 'name': state.my_name})
        time.sleep(HEARTBEAT_INTERVAL)
        if int(time.time()) % 30 == 0:
            send(sock, {'type': 'join', 'name': state.my_name})


def prune_offline():
    while state.running:
        now = time.monotonic()
        ts = datetime.now().strftime('%H:%M:%S')
        with state.lock:
            for n in [u for u, t in state.users.items() if now - t > TIMEOUT]:
                state.users.pop(n, None)
                state.messages.append((ts, 'sys', n, t('timeout'), None))
                state.dirty = True
        time.sleep(1)


# ------------------- rendering -------------------

def _clip(text, w):
    """Грубая обрезка по длине (ANSI коды не учитываются)."""
    return text if len(text) <= w else text[:w]


def build_lines(w, h):
    with state.lock:
        users = sorted(state.users.keys())
        lines = []

        # Шапка
        title = f" Mushraam  │  {state.my_name}  │  {t('online')}: {len(users)} "
        lines.append(C.REV + C.BOLD + title[:w].ljust(w) + C.RESET)

        # Список пользователей
        if users:
            parts = [f"{color_for(u)}{u}{C.RESET}" for u in users]
            lines.append(_clip("  " + "  ".join(parts), w))
        else:
            lines.append(f"  {C.DIM}{t('no_users')}{C.RESET}")

        # Разделитель
        lines.append(C.DIM + '─' * w + C.RESET)

        # Лог
        body_h = max(1, h - 4)
        for ts, kind, name, text, to in state.messages[-body_h:]:
            if kind == 'sys':
                if name:
                    # имя + пробел + текст с маленькой буквы не нужно принудительно, но текст уже задан
                    line = f"{C.DIM}[{ts}] * {name} {text}{C.RESET}"
                else:
                    line = f"{C.DIM}[{ts}] * {text}{C.RESET}"
            elif kind == 'pm':
                line = f"{C.DIM}[{ts}]{C.RESET} {C.RED}{C.BOLD}[личное от {name}]{C.RESET} {text}"
            else:
                col = color_for(name)
                if to:
                    line = (f"{C.DIM}[{ts}]{C.RESET} <{col}{name}{C.RESET}"
                            f"{C.YELLOW}→{C.RESET}{color_for(to)}{to}{C.RESET}> "
                            f"{C.DIM}{text}{C.RESET}")
                else:
                    line = f"{C.DIM}[{ts}]{C.RESET} <{col}{name}{C.RESET}> {text}"
            lines.append(_clip(line, w + 32))

        while len(lines) < h - 1:
            lines.append('')

    max_input = max(1, w - 4)
    with state.lock:
        buf = state.input_buf
        pos = state.input_pos
    if len(buf) > max_input:
        start = max(0, pos - max_input + 1)
        if start + max_input > len(buf):
            start = max(0, len(buf) - max_input)
        view = buf[start:start+max_input]
        view_pos = pos - start
    else:
        view = buf
        view_pos = pos
    lines.append(f"{C.GREEN}{C.BOLD}>{C.RESET} {view}")

    return lines, view_pos


def render(w, h):
    if w < 20 or h < 6:
        sys.stdout.write('\033[H\033[2J' + C.RESET + t('terminal_small'))
        sys.stdout.flush()
        return

    lines, view_pos = build_lines(w, h)

    out = []
    for i, line in enumerate(lines):
        out.append(f'\033[{i+1};1H')  # cursor to start of line i+1
        out.append(line)
        out.append('\033[K')          # erase line tail

    # cursor position on input line
    out.append(f'\033[{h};{3 + view_pos}H')

    sys.stdout.write(''.join(out))
    sys.stdout.flush()


# ------------------- commands -------------------

def help_lines():
    return [
        '/help — ' + t('help_this'),
        t('help_clear'),
        t('help_delconf'),
        t('help_language'),
        t('help_enick'),
        t('help_ms'),
        t('help_exit'),
    ]


def _sys(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    with state.lock:
        state.messages.append((ts, 'sys', '', msg, None))
        state.dirty = True


def handle_command(sock, line):
    global LANG
    if not line.startswith('/'):
        return False

    parts = line.split(' ', 2)
    cmd = parts[0].lower()

    if cmd == '/help':
        _sys(t('help_title'))
        for hline in help_lines():
            _sys('  ' + hline)
        return True

    if cmd == '/exit' or cmd == '/quit':
        try:
            state.running = False
        except Exception:
            pass
        return False

    if cmd == '/clear':
        with state.lock:
            state.messages.clear()
            state.dirty = True
        return True

    if cmd == '/delconf':
        try:
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
                _sys(t('config_deleted'))
            else:
                _sys(t('config_not_exists'))
        except Exception:
            _sys(t('config_error'))
        return True

    if cmd == '/language':
        if len(parts) < 2 or parts[1].strip().lower() not in ('ru','en'):
            _sys(t('usage_language'))
            return True
        newlang = parts[1].strip().lower()
        if newlang == LANG:
            _sys(t('same_lang'))
            return True
        LANG = newlang
        cfg = load_config()
        if cfg:
            cfg['lang'] = LANG
            save_config(cfg)
        _sys(t('language_set'))
        return True

    if cmd == '/enick':
        if len(parts) < 2 or not parts[1].strip():
            _sys(t('usage_enick'))
            return True
        new = parts[1].strip()
        if ' ' in new:
            _sys(t('name_no_spaces'))
            return True
        old = state.my_name
        state._renaming_from = old
        state.my_name = new
        cfg = load_config()
        if cfg:
            cfg['name'] = new
            save_config(cfg)
        send(sock, {'type': 'rename', 'name': old, 'new': new})
        time.sleep(0.1)
        state._renaming_from = None
        _sys(t('you_are_now', new=new))
        return True

    if cmd == '/ms':
        rest = line[len('/ms'):].strip()
        if not rest or ' ' not in rest:
            _sys(t('usage_ms'))
            return True
        target, text = rest.split(' ', 1)
        target, text = target.strip(), text.strip()
        if not text:
            _sys(t('empty_msg'))
            return True
        if target == state.my_name:
            _sys(t('cant_msg_self'))
            return True
        with state.lock:
            if target not in state.users:
                _sys(t('user_offline'))
                return True
        try:
            send(sock, {'type': 'msg', 'name': state.my_name, 'text': text, 'to': target})
        except Exception:
            _sys(t('user_offline'))
            return True
        ts = datetime.now().strftime('%H:%M:%S')
        with state.lock:
            state.messages.append((ts, 'msg', state.my_name, text, target))
            state.dirty = True
        return True

    _sys(t('unknown_cmd', cmd=cmd))
    return True


# ------------------- input -------------------

def process_key(key, sock):
    if key is None:
        return True

    if key in ('\x03', '\x04'):           # Ctrl+C / Ctrl+D
        return False

    # bracketed paste
    if key.startswith('\x1b[200~'):
        payload = key[len('\x1b[200~'):]
        end = payload.find('\x1b[201~')
        if end >= 0:
            pasted = payload[:end]
            with state.lock:
                pos = state.input_pos
                buf = state.input_buf
                state.input_buf = buf[:pos] + pasted + buf[pos:]
                state.input_pos = pos + len(pasted)
                state.dirty = True
            return True
        # incomplete; treat as text? ignore
        return True

    if key in ('\r', '\n'):
        with state.lock:
            text = state.input_buf.strip()
            if text:
                state.input_history.append(text)
                if len(state.input_history) > 100:
                    state.input_history = state.input_history[-100:]
            state.input_buf = ''
            state.input_pos = 0
            state.history_idx = -1
            state.history_stash = ''
            state.dirty = True
        if text and not handle_command(sock, text):
            send(sock, {'type': 'msg', 'name': state.my_name, 'text': text})
            ts = datetime.now().strftime('%H:%M:%S')
            with state.lock:
                state.messages.append((ts, 'msg', state.my_name, text, None))
                state.dirty = True
        elif text:
            # command handled, ensure it's not broadcast as message
            pass
        return True

    if key in ('\x7f', '\x08'):           # Backspace
        with state.lock:
            pos = state.input_pos
            if pos > 0:
                state.input_buf = state.input_buf[:pos-1] + state.input_buf[pos:]
                state.input_pos = pos - 1
                state.dirty = True
        return True

    # Delete
    if key == '\x1b[3~':
        with state.lock:
            pos = state.input_pos
            if pos < len(state.input_buf):
                state.input_buf = state.input_buf[:pos] + state.input_buf[pos+1:]
                state.dirty = True
        return True

    # arrows up/down - история ввода
    if key in ('\x1b[A', '\x1bOA', 'UP'):
        with state.lock:
            if not state.input_history:
                return True
            if state.history_idx == -1:
                state.history_stash = state.input_buf
                state.history_idx = len(state.input_history) - 1
            elif state.history_idx > 0:
                state.history_idx -= 1
            state.input_buf = state.input_history[state.history_idx]
            state.input_pos = len(state.input_buf)
            state.dirty = True
        return True
    if key in ('\x1b[B', '\x1bOB', 'DOWN'):
        with state.lock:
            if state.history_idx == -1:
                return True
            if state.history_idx < len(state.input_history) - 1:
                state.history_idx += 1
                state.input_buf = state.input_history[state.history_idx]
            else:
                state.history_idx = -1
                state.input_buf = state.history_stash
            state.input_pos = len(state.input_buf)
            state.dirty = True
        return True

    # arrows left/right
    if key in ('\x1b[C', '\x1bOC', 'RIGHT'):       # right
        with state.lock:
            if state.input_pos < len(state.input_buf):
                state.input_pos += 1
                state.dirty = True
        return True
    if key in ('\x1b[D', '\x1bOD', 'LEFT'):       # left
        with state.lock:
            if state.input_pos > 0:
                state.input_pos -= 1
                state.dirty = True
        return True
    if key in ('\x1b[H', '\x1b[1~', '\x1bOH', 'HOME'):  # Home
        with state.lock:
            state.input_pos = 0
            state.dirty = True
        return True
    if key in ('\x1b[F', '\x1b[4~', '\x1bOF', 'END'):  # End
        with state.lock:
            state.input_pos = len(state.input_buf)
            state.dirty = True
        return True

    if key == '\x1b':                     # ESC alone
        return True

    if key and len(key) == 1 and key.isprintable():
        with state.lock:
            pos = state.input_pos
            state.input_buf = state.input_buf[:pos] + key + state.input_buf[pos:]
            state.input_pos = pos + 1
            state.dirty = True
        return True
    if key and len(key) > 1 and not key.startswith('\x1b'):
        try:
            if all(ord(c) >= 32 or c in '\t' for c in key):
                with state.lock:
                    pos = state.input_pos
                    state.input_buf = state.input_buf[:pos] + key + state.input_buf[pos:]
                    state.input_pos = pos + len(key)
                    state.dirty = True
                return True
        except Exception:
            pass

    # ignore other escape sequences
    return True


def main_loop(terminal, sock):
    last_size = shutil.get_terminal_size((80, 24))
    while state.running:
        cur_size = shutil.get_terminal_size((80, 24))
        if cur_size != last_size:
            last_size = cur_size
            state.dirty = True

        if state.dirty:
            try:
                render(cur_size.columns, cur_size.lines)
                state.dirty = False
            except Exception:
                pass

        key = terminal.read_key(timeout=0.05)
        if key is not None and not process_key(key, sock):
            break


# ------------------- main -------------------

def select_option_inline(prompt, options, default_index=0):
    sel = default_index
    if sel < 0:
        sel = 0
    if sel >= len(options):
        sel = len(options) - 1
    if IS_WINDOWS:
        try:
            sys.stdout.write('\n')
            sys.stdout.flush()
            while True:
                sys.stdout.write('\r\033[K')
                sys.stdout.write(prompt + ' ')
                for i, opt in enumerate(options):
                    if i == sel:
                        sys.stdout.write(C.REV + str(opt) + C.RESET)
                    else:
                        sys.stdout.write(str(opt))
                    if i < len(options) - 1:
                        sys.stdout.write('   ')
                sys.stdout.flush()
                try:
                    import msvcrt
                    if not msvcrt.kbhit():
                        time.sleep(0.1)
                        continue
                    ch = msvcrt.getwch()
                except Exception:
                    time.sleep(0.1)
                    continue
                if ch in ('\r', '\n'):
                    sys.stdout.write('\r\033[K')
                    sys.stdout.write(prompt + ' ')
                    for i, opt in enumerate(options):
                        if i == sel:
                            sys.stdout.write(C.REV + str(opt) + C.RESET)
                        else:
                            sys.stdout.write(str(opt))
                        if i < len(options) - 1:
                            sys.stdout.write('   ')
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                    return options[sel]
                if ch == '\t':
                    sel = (sel + 1) % len(options)
                    continue
                if ch in ('\x00', '\xe0'):
                    try:
                        import msvcrt
                        ch2 = msvcrt.getwch()
                        if ch2 == 'K':
                            sel = (sel - 1 + len(options)) % len(options)
                            continue
                        if ch2 == 'M':
                            sel = (sel + 1) % len(options)
                            continue
                    except Exception:
                        pass
                    continue
                if isinstance(ch, str) and len(ch) == 1 and ch.isalpha():
                    kl = ch.lower()
                    for i, o in enumerate(options):
                        if str(o).lower().startswith(kl):
                            sel = i
                            break
                    continue
                continue
        except KeyboardInterrupt:
            sys.stdout.write('\n')
            raise
    fd = sys.stdin.fileno()
    old = None
    try:
        import termios, tty
        old = termios.tcgetattr(fd)
        tty.setraw(fd)
    except Exception:
        old = None
    try:
        sys.stdout.write('\n')
        sys.stdout.flush()
        while True:
            sys.stdout.write('\r\033[K')
            sys.stdout.write(prompt + ' ')
            for i, opt in enumerate(options):
                if i == sel:
                    sys.stdout.write(C.REV + str(opt) + C.RESET)
                else:
                    sys.stdout.write(str(opt))
                if i < len(options) - 1:
                    sys.stdout.write('   ')
            sys.stdout.flush()
            try:
                r, _, _ = select.select([sys.stdin], [], [], 0.2)
            except Exception:
                break
            if not r:
                continue
            try:
                data = os.read(fd, 32)
            except Exception:
                break
            if not data:
                continue
            if b'\x03' in data or b'\x04' in data:
                raise KeyboardInterrupt
            if b'\r' in data or b'\n' in data:
                sys.stdout.write('\r\033[K')
                sys.stdout.write(prompt + ' ')
                for i, opt in enumerate(options):
                    if i == sel:
                        sys.stdout.write(C.REV + str(opt) + C.RESET)
                    else:
                        sys.stdout.write(str(opt))
                    if i < len(options) - 1:
                        sys.stdout.write('   ')
                sys.stdout.write('\n')
                sys.stdout.flush()
                return options[sel]
            if b'\t' in data:
                sel = (sel + 1) % len(options)
                continue
            if b'\x1b' in data:
                if b'[C' in data or (b'O' in data and b'C' in data):
                    sel = (sel + 1) % len(options)
                    continue
                if b'[D' in data or (b'O' in data and b'D' in data):
                    sel = (sel - 1 + len(options)) % len(options)
                    continue
                continue
            for b in data:
                if 32 <= b < 127:
                    c = chr(b)
                    if c.isalpha():
                        kl = c.lower()
                        for i, o in enumerate(options):
                            if str(o).lower().startswith(kl):
                                sel = i
                                break
                        break
            continue
    except KeyboardInterrupt:
        sys.stdout.write('\n')
        raise
    finally:
        try:
            if old is not None:
                import termios
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            pass


select_option = select_option_inline


def main():
    global LANG, PORT
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print(t('tty_required'))
        return

    cfg = load_config()
    if cfg:
        LANG = cfg.get('lang', 'ru')
        name = cfg.get('name', '') or random_name()
        PORT = cfg.get('port', 50000)
    else:
        try:
            lang_choice = select_option(t('choose_lang'), ['RU', 'EN'], 0 if LANG == 'ru' else 1)
            if lang_choice is None:
                lang_choice = 'RU'
            LANG = 'ru' if str(lang_choice).strip().upper().startswith('R') else 'en'
            sys.stdout.write('\r\033[K')
            sys.stdout.flush()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        try:
            sys.stdout.write(t('your_name'))
            sys.stdout.flush()
            try:
                name = input().rstrip()
            except Exception:
                name = sys.stdin.readline()
                if name == '':
                    raise EOFError
                name = name.rstrip('\r\n')
            name = name.strip() or random_name()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        try:
            sys.stdout.write(t('port_prompt'))
            sys.stdout.flush()
            try:
                port_input = input().rstrip()
            except Exception:
                port_input = sys.stdin.readline()
                if port_input == '':
                    raise EOFError
                port_input = port_input.rstrip('\r\n')
            port_input = port_input.strip()
            if port_input:
                try:
                    PORT = int(port_input)
                except ValueError:
                    print(t('bad_port'))
                    return
        except (EOFError, KeyboardInterrupt):
            print()
            return

        try:
            save_choice = select_option(t('save_config'), ['Да', 'Нет'] if LANG == 'ru' else ['Yes', 'No'], 0)
            if LANG == 'ru':
                saveq = 'y' if save_choice == 'Да' else 'n'
            else:
                if save_choice is None:
                    saveq = 'n'
                else:
                    saveq = 'y' if str(save_choice).strip().lower().startswith('y') else 'n'
            sys.stdout.write('\r\033[K')
            sys.stdout.flush()
        except (EOFError, KeyboardInterrupt):
            saveq = ''
        if saveq in ("y", "yes", "да"):
            save_config({"lang": LANG, "name": name, "port": PORT})

    state.my_name = name

    sock = make_socket()
    send(sock, {'type': 'ping', 'name': name})
    try:
        send(sock, {'type': 'join', 'name': name})
    except Exception:
        pass

    threading.Thread(target=receiver, args=(sock,), daemon=True).start()
    threading.Thread(target=heartbeat, args=(sock,), daemon=True).start()
    threading.Thread(target=prune_offline, daemon=True).start()

    # Alt screen - keep terminal history clean
    sys.stdout.write('\033[?1049h\033[?2004h')
    sys.stdout.flush()

    terminal = Terminal()
    try:
        try:
            send(sock, {'type': 'join', 'name': name})
        except Exception:
            pass
        try:
            ts = datetime.now().strftime('%H:%M:%S')
            with state.lock:
                if LANG == 'ru':
                    state.messages.append((ts, 'sys', name, 'присоединился к чату', None))
                else:
                    state.messages.append((ts, 'sys', name, 'joined the chat', None))
                state.dirty = True
        except Exception:
            pass
        main_loop(terminal, sock)
    finally:
        state.running = False
        try:
            send(sock, {'type': 'bye', 'name': state.my_name})
        except Exception:
            pass
        time.sleep(0.15)
        try:
            sock.close()
        except Exception:
            pass
        try:
            terminal.restore()
        except Exception:
            pass
        sys.stdout.write('\033[?2004l\033[?1049l' + C.RESET)
        sys.stdout.flush()
        try:
            print(t('exit'))
        except Exception:
            print('Exit.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Error: E010")
    except Exception as e:
        print(f"Error: E999 ({e})")