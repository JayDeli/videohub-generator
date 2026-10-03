#!/usr/bin/env python3
"""Load labels + routing into a Blackmagic Videohub over Ethernet (TCP 9990).

Usage:
  python3 videohub_push.py videohub_load.txt 192.168.1.50   # send the file from the generator page
  python3 videohub_push.py videohub.csv 192.168.1.50        # or the CSV from the generator page
  python3 videohub_push.py videohub.csv                     # no IP: just writes videohub_load.txt

Loading REPLACES the labels and routes on the unit. Note down the current ones first.
"""
import csv, socket, sys, time

def from_csv(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    block = lambda name, lines: name + ":\n" + "\n".join(lines) + "\n\n"
    msg = block("INPUT LABELS", [f"{int(r['PORT'])-1} {r['IN_LABEL']}" for r in rows])
    msg += block("OUTPUT LABELS", [f"{int(r['PORT'])-1} {r['OUT_LABEL']}" for r in rows])
    msg += block("VIDEO OUTPUT ROUTING", [f"{int(r['PORT'])-1} {int(r['XPT_IN'])-1}" for r in rows if r["XPT_IN"].strip()])
    return msg

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    msg = from_csv(path) if path.lower().endswith(".csv") else open(path, encoding="utf-8").read().replace("\r\n", "\n")
    if path.lower().endswith(".csv"):
        open("videohub_load.txt", "w", encoding="utf-8").write(msg)
        print("wrote videohub_load.txt")
    if len(sys.argv) < 3:
        return
    ip = sys.argv[2]
    s = socket.create_connection((ip, 9990), timeout=5)
    time.sleep(1)
    s.recv(65536)                                   # protocol preamble + current device state
    bad = False
    for b in [x for x in msg.strip().split("\n\n") if x.strip()]:
        s.sendall((b.strip() + "\n\n").encode())
        time.sleep(0.4)
        reply = s.recv(4096).decode(errors="replace").strip().splitlines()
        status = reply[0] if reply else "(no reply)"
        print(b.split(":")[0], "->", status)
        bad |= not status.startswith("ACK")
    s.close()
    sys.exit(1 if bad else 0)

main()
