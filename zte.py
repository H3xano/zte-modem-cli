import io
import json
import os
import sys

from colorama import Fore, Style, init
from dotenv import load_dotenv

# Ensure stdout/stderr support UTF-8 on Windows (cp1252 terminals reject ✓ ✗ ⚠)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

init(autoreset=True)


def ok(msg):
    print(Fore.GREEN + f"✓ {msg}")


def err(msg):
    print(Fore.RED + f"✗ {msg}")


def info(msg):
    print(Fore.CYAN + msg)


def warn(msg):
    print(Fore.YELLOW + f"⚠ {msg}")


HELP = """\
Usage: python zte.py [--ip IP] [--password PASS] <command> [args]

Commands:
  login  <on|off>              Login or logoff
  ls                           List all SMS messages
  rm     <id|*>                Delete message by ID or all (*)
  snd    <phone> <message>     Send SMS
  wifi   <on|off>              Enable or disable WiFi
  wan    <on|off>              Connect or disconnect WAN
  hack                         Hack modem (Method 2 — built-in telnetd)
  hack3  [tftp_ip]             Hack modem (Method 3 — TFTP via zte_debug.sh)
  hack3d [tftp_ip]             Hack modem (Method 3 direct — raw tftp cmd)
"""


def print_help():
    info(HELP)


def _resolve_credentials(args):
    """Strip --ip / --password flags from args and return (modem_ip, password, remaining_args)."""
    modem_ip = None
    password = None
    remaining = []
    i = 0
    while i < len(args):
        if args[i] == "--ip" and i + 1 < len(args):
            modem_ip = args[i + 1]
            i += 2
        elif args[i] == "--password" and i + 1 < len(args):
            password = args[i + 1]
            i += 2
        else:
            remaining.append(args[i])
            i += 1
    if modem_ip is None:
        modem_ip = os.getenv("MODEM_IP")
    if password is None:
        password = os.getenv("PASSWORD")
    return modem_ip, password, remaining


def _cmd_login(modem_ip, password, args):
    from src.login import login, logout
    if not args or args[0] not in ("on", "off"):
        err("Usage: login <on|off>")
        return
    if args[0] == "on":
        ok("Logged in.") if login(modem_ip, password) else err("Login failed.")
    else:
        ok("Logged out.") if logout(modem_ip) else err("Logout failed.")


def _cmd_ls(modem_ip, password, cmd_args=None):
    from src.login import login, logout
    from src.sms import list_sms
    login(modem_ip, password)
    messages = list_sms(modem_ip)
    logout(modem_ip)
    if not messages:
        warn("No messages found.")
        return
    for msg in messages:
        parts = msg["date"].split(",")
        date_str = (
            f"{parts[2]}/{parts[1]}/{parts[0]} {parts[3]}:{parts[4]}:{parts[5]}"
            if len(parts) >= 6
            else msg["date"]
        )
        info(f"[#{msg['id']}] {msg['number']} | {date_str} | {msg['content']}")


def _cmd_rm(modem_ip, password, args):
    from src.login import login, logout
    from src.sms import delete_sms
    if not args:
        err("Usage: rm <id|*>")
        return
    login(modem_ip, password)
    results = delete_sms(modem_ip, args[0])
    logout(modem_ip)
    if not results:
        warn("No messages to delete.")
        return
    for r in results:
        if r["success"]:
            ok(f"Message #{r['id']} deleted.")
        else:
            err(f"Could not delete message #{r['id']}.")


def _cmd_snd(modem_ip, password, args):
    from src.login import login, logout
    from src.sms import send_sms
    if len(args) < 2:
        err("Usage: snd <phone> <message>")
        return
    login(modem_ip, password)
    success = send_sms(modem_ip, args[0], args[1])
    logout(modem_ip)
    ok(f"SMS sent to {args[0]}.") if success else err("Could not send SMS.")


def _cmd_wifi(modem_ip, password, args):
    from src.login import login, logout
    from src.wifi import set_wifi
    if not args or args[0] not in ("on", "off"):
        err("Usage: wifi <on|off>")
        return
    login(modem_ip, password)
    enable = args[0] == "on"
    success = set_wifi(modem_ip, enable)
    logout(modem_ip)
    state = "enabled" if enable else "disabled"
    ok(f"WiFi {state}.") if success else err(f"Could not {'enable' if enable else 'disable'} WiFi.")


def _cmd_wan(modem_ip, password, args):
    from src.login import login, logout
    from src.wan import set_wan
    if not args or args[0] not in ("on", "off"):
        err("Usage: wan <on|off>")
        return
    login(modem_ip, password)
    connect = args[0] == "on"
    success = set_wan(modem_ip, connect)
    logout(modem_ip)
    state = "connected" if connect else "disconnected"
    ok(f"WAN {state}.") if success else err(f"Could not {'connect' if connect else 'disconnect'} WAN.")


def _cmd_hack(modem_ip, password, cmd_args=None):
    from src.login import login, logout
    from src.hack import exploits_nvram, factory_backdoor
    login(modem_ip, password)
    info("Step 1: Enabling factory backdoor...")
    ok("Factory backdoor enabled.") if factory_backdoor(modem_ip, password) else err("Factory backdoor failed.")
    info("Step 2: Exploiting NVRAM...")
    if exploits_nvram(modem_ip):
        ok("NVRAM exploit succeeded. Telnet available on port 4719 (admin/admin).")
    else:
        err("NVRAM exploit failed.")
    logout(modem_ip)


def _cmd_hack3(modem_ip, password, args):
    from src.login import login, logout
    from src.hack import factory_backdoor, tftp_telnetd
    tftp_ip = args[0] if args else "192.168.0.22"
    login(modem_ip, password)
    info("Step 1: Enabling factory backdoor...")
    ok("Factory backdoor enabled.") if factory_backdoor(modem_ip, password) else err("Factory backdoor failed.")
    info(f"Step 2: Fetching telnetd via TFTP from {tftp_ip}...")
    if tftp_telnetd(modem_ip, tftp_ip):
        ok("TFTP exploit sent. Telnet available on port 23 (admin/admin).")
    else:
        err("TFTP exploit failed.")
    logout(modem_ip)


def _cmd_hack3d(modem_ip, password, args):
    from src.login import login, logout
    from src.hack import factory_backdoor, tftp_telnetd_direct
    tftp_ip = args[0] if args else "192.168.0.22"
    login(modem_ip, password)
    info("Step 1: Enabling factory backdoor...")
    ok("Factory backdoor enabled.") if factory_backdoor(modem_ip, password) else err("Factory backdoor failed.")
    info(f"Step 2: Fetching telnetd via TFTP (direct) from {tftp_ip}...")
    if tftp_telnetd_direct(modem_ip, tftp_ip):
        ok("TFTP direct exploit sent. Telnet available on port 23 (admin/admin).")
    else:
        err("TFTP direct exploit failed.")
    logout(modem_ip)


COMMANDS = {
    "login": _cmd_login,
    "ls": _cmd_ls,
    "rm": _cmd_rm,
    "snd": _cmd_snd,
    "wifi": _cmd_wifi,
    "wan": _cmd_wan,
    "hack": _cmd_hack,
    "hack3": _cmd_hack3,
    "hack3d": _cmd_hack3d,
}


def main():
    load_dotenv()
    modem_ip, password, args = _resolve_credentials(sys.argv[1:])

    if not args:
        print_help()
        sys.exit(0)

    cmd = args[0]
    cmd_args = args[1:]

    if cmd not in COMMANDS:
        err(f"Unknown command: '{cmd}'")
        print_help()
        sys.exit(1)

    if not modem_ip or not password:
        err("Modem IP and password required. Set MODEM_IP/PASSWORD in .env or use --ip/--password.")
        sys.exit(1)

    try:
        fn = COMMANDS[cmd]
        fn(modem_ip, password, cmd_args)
    except Exception as e:
        err(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
