#!/usr/bin/env python3
"""Send labels and routes to a Blackmagic Videohub, or read them back, over Ethernet (TCP 9990).
Part of the PixelTach Videohub File Generator (https://videohub.pixeltach.com). Python 3, standard library only.

Usage:
  python3 videohub_push.py videohub_load.txt 192.168.1.50            send the file, print ACK/NAK for each block
  python3 videohub_push.py videohub_load.txt 192.168.1.50 --verify   send, then check the router now holds what was sent
  python3 videohub_push.py --read 192.168.1.50                       save what the router holds to videohub_state.txt
  python3 videohub_push.py --read 192.168.1.50 my_backup.txt         ...or to a file name you choose
  python3 videohub_push.py videohub.csv                              convert the page's CSV to videohub_load.txt (no IP: nothing is sent)
  python3 videohub_push.py videohub.csv 192.168.1.50                 convert, then send

Sending REPLACES the labels and routes you list on the unit. Read the router first (--read) to keep a backup.
Exit status is 0 when everything was accepted (and, with --verify, matches), 1 otherwise.
"""
import csv, socket, sys, time

PORT = 9990


def from_csv(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    def block(name, lines):
        return name + ":\n" + "\n".join(lines) + "\n\n" if lines else ""
    msg = block("INPUT LABELS", [f"{int(r['PORT'])-1} {r['IN_LABEL']}" for r in rows if r["IN_LABEL"].strip()])
    msg += block("OUTPUT LABELS", [f"{int(r['PORT'])-1} {r['OUT_LABEL']}" for r in rows if r["OUT_LABEL"].strip()])
    msg += block("VIDEO OUTPUT ROUTING", [f"{int(r['PORT'])-1} {int(r['XPT_IN'])-1}" for r in rows if r["XPT_IN"].strip()])
    return msg


class Hub:
    """A connection that reads whole blocks (ended by a blank line) and keeps the router's state up to date."""

    def __init__(self, host, port=PORT, timeout=5):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.buf = b""
        self.state = {"INPUT LABELS": {}, "OUTPUT LABELS": {}, "VIDEO OUTPUT ROUTING": {}, "VIDEOHUB DEVICE": {}}
        self.raw = []

    def close(self):
        self.s.close()

    def _block(self, wait):
        """Next complete block as text, or None if nothing complete arrives within `wait` seconds."""
        end = time.time() + wait
        while True:
            i = self.buf.find(b"\n\n")
            if i >= 0:
                blk, self.buf = self.buf[:i], self.buf[i + 2:]
                return blk.decode("utf-8", "replace").replace("\r", "")
            left = end - time.time()
            if left <= 0:
                return None
            self.s.settimeout(left)
            try:
                d = self.s.recv(65536)
            except socket.timeout:
                return None
            if not d:
                if self.buf.strip():
                    blk, self.buf = self.buf, b""
                    return blk.decode("utf-8", "replace").replace("\r", "")
                return None
            self.buf += d

    def _absorb(self, text):
        lines = text.split("\n")
        head = lines[0].strip()
        if not head.endswith(":"):
            return
        name = head[:-1]
        self.raw.append(text)
        if name == "VIDEOHUB DEVICE":
            for ln in lines[1:]:
                k, _, v = ln.partition(":")
                self.state[name][k.strip().lower()] = v.strip()
        elif name in self.state:
            for ln in lines[1:]:
                n, _, v = ln.partition(" ")
                if n.isdigit():
                    self.state[name][int(n)] = v

    def drain(self, quiet=1.0, limit=15):
        """Read everything the router sends until it has been quiet for `quiet` seconds."""
        end = time.time() + limit
        while time.time() < end:
            b = self._block(quiet)
            if b is None:
                return
            self._absorb(b)

    def send(self, block, wait=5):
        """Send one block; return 'ACK' or 'NAK' (or None on timeout). Status blocks arriving first are kept."""
        self.s.sendall((block.strip() + "\n\n").encode("utf-8"))
        end = time.time() + wait
        while time.time() < end:
            b = self._block(end - time.time())
            if b is None:
                return None
            if b.strip() in ("ACK", "NAK"):
                return b.strip()
            self._absorb(b)
        return None


def wanted(msg):
    """What a load file asks for: {block name: {index: value}}."""
    want = {}
    for b in [x for x in msg.strip().split("\n\n") if x.strip()]:
        lines = b.strip().split("\n")
        name = lines[0].strip().rstrip(":")
        want[name] = {}
        for ln in lines[1:]:
            n, _, v = ln.partition(" ")
            if n.isdigit():
                want[name][int(n)] = v
    return want


def read_state(host, out):
    hub = Hub(host)
    hub.drain()
    hub.close()
    text = "\n\n".join(hub.raw) + "\n\n"
    if not hub.raw:
        sys.exit("Connected, but the router sent nothing. Is that the Videohub's address?")
    open(out, "w", encoding="utf-8").write(text)
    d = hub.state["VIDEOHUB DEVICE"]
    print("saved", out, "-", d.get("model name", "Videohub"), f"({len(hub.state['INPUT LABELS'])} input labels, "
          f"{len(hub.state['OUTPUT LABELS'])} output labels, {len(hub.state['VIDEO OUTPUT ROUTING'])} routes)")


def push(msg, host, verify):
    hub = Hub(host)
    hub.drain()                                   # protocol preamble + current device state
    if not hub.raw:
        sys.exit("Connected, but the router sent nothing. Is that the Videohub's address?")
    bad = False
    for b in [x for x in msg.strip().split("\n\n") if x.strip()]:
        status = hub.send(b)
        print(b.split(":")[0], "->", status or "(no reply)")
        bad |= status != "ACK"
    if verify:
        hub.drain(quiet=1.0, limit=5)            # let any last status updates arrive
        diffs = []
        for name, items in wanted(msg).items():
            have = hub.state.get(name, {})
            for i, v in sorted(items.items()):
                if have.get(i) != v:
                    diffs.append((name, i, v, have.get(i)))
        if diffs:
            bad = True
            print(f"VERIFY: {len(diffs)} item(s) differ")
            for name, i, v, h in diffs[:40]:
                print(f"  {name} {i + 1}: sent {v!r}, router has {h!r}")
        else:
            print("VERIFY: the router holds everything that was sent")
    hub.close()
    return 0 if not bad else 1


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--help" in flags or "-h" in sys.argv or not sys.argv[1:] or flags - {"--read", "--verify"}:
        sys.exit(__doc__)
    try:
        if "--read" in flags:
            if not args:
                sys.exit(__doc__)
            read_state(args[0], args[1] if len(args) > 1 else "videohub_state.txt")
            return 0
        path = args[0]
        if path.lower().endswith(".csv"):
            msg = from_csv(path)
            open("videohub_load.txt", "w", encoding="utf-8").write(msg)
            print("wrote videohub_load.txt")
        else:
            msg = open(path, encoding="utf-8").read().replace("\r\n", "\n")
        if len(args) < 2:
            return 0
        return push(msg, args[1], "--verify" in flags)
    except (OSError, socket.timeout) as e:
        sys.exit(f"Could not reach the router: {e}")


sys.exit(main())
