import sys
import platform

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, ORANGE, PINK = range(10)

_has_colors = None

def _check_colors():
    global _has_colors
    if _has_colors is not None:
        return _has_colors
    try:
        if not sys.stdout.isatty():
            _has_colors = False
            return False
        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.GetStdHandle(-11)
                mode = ctypes.c_uint32()
                kernel32.GetConsoleMode(handle, ctypes.byref(mode))
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
                _has_colors = True
                return True
            except:
                _has_colors = False
                return False
        import curses
        curses.setupterm()
        _has_colors = curses.tigetnum("colors") > 2
        return _has_colors
    except:
        _has_colors = False
        return False

def pout(text, color=WHITE, bold=False, reset=True):
    if _check_colors():
        seq = "\x1b[1;%dm" % (30 + color) if bold else "\x1b[0;%dm" % (30 + color)
        seq += text
        if reset:
            seq += "\x1b[0m"
        sys.stdout.write(seq)
    else:
        sys.stdout.write(text)
    sys.stdout.flush()

def pout_b(text, color=WHITE):
    pout(text, color, bold=True)

def pin(text, color=YELLOW):
    pout(text, color)
    return input()

def perror(text):
    pout(f"[!] {text}\n", RED)
    
def pok(text):
    pout(f"[+] {text}\n", GREEN)

def pinfo(text):
    pout(f"[*] {text}\n", CYAN)

def pheader(text):
    w = 60
    pout("\n" + "=" * w + "\n", BLUE, bold=True)
    pout(f"  {text}\n", BLUE, bold=True)
    pout("=" * w + "\n", BLUE, bold=True)

def psep():
    pout("-" * 60 + "\n", WHITE)

def ptable(headers, rows):
    col_widths = []
    for i, h in enumerate(headers):
        max_w = len(str(h))
        for row in rows:
            if i < len(row):
                max_w = max(max_w, len(str(row[i])))
        col_widths.append(min(max_w + 2, 40))

    sep = "+" + "+".join("-" * w for w in col_widths) + "+"
    pout(sep + "\n", CYAN)
    hdr = "|"
    for i, h in enumerate(headers):
        hdr += str(h).ljust(col_widths[i]) + "|"
    pout(hdr + "\n", CYAN, bold=True)
    pout(sep + "\n", CYAN)
    for row in rows:
        r = "|"
        for i, cell in enumerate(row):
            if i < len(col_widths):
                r += str(cell).ljust(col_widths[i]) + "|"
        pout(r + "\n")
    pout(sep + "\n", CYAN)
