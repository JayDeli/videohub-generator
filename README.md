# Videohub File Generator

Live at <https://videohub.pixeltach.com>. A free, single-page tool from [PixelTach](https://pixeltach.com) for Blackmagic Videohub routers. Build or paste a router table, check it, edit it, and download files the Videohub accepts directly. Share a link or QR code so a tech opens the same table with no accounts.

Runs entirely in the browser. Nothing is uploaded or stored; the table travels inside the link after the `#`.

## What it does

- **Any router size.** Pick 10x10, 20x20, 40x40, 80x80, 120x120, the Minis (4x2, 6x2, 8x4), CleanSwitch 12x12 or a custom size up to 288. Older 40x40 share links still open.
- **Videohub Setup label set.** Download the label file Videohub Setup loads (Settings gear, then "load label set"). Format taken from files saved by Videohub Setup: CSV, no header, `Input,<port>,<label>` then `Output,<port>,<label>`, ports from 1, every port listed, CRLF line endings. Commas in labels become spaces and accents are dropped, since the file is comma-separated plain ASCII.
- **Network load file.** `videohub_load.txt` uses the Videohub Ethernet Protocol (TCP 9990): `INPUT LABELS:`, `OUTPUT LABELS:`, `VIDEO OUTPUT ROUTING:`, ports from 0, a blank line after each block. It also carries routes.
- **Check or back up a router.** Read the router's report with one terminal command, paste it into the page, and compare it with the table, download a backup that restores it, or load it into the table.
- **Import.** Paste a table copied from Lucid, a Videohub Setup label set, a router report, or this page's CSV. The size is worked out from what you paste.
- **Label limit.** Labels over a limit (default 18, adjustable) get a warning. Blackmagic's protocol document states no limit; 18 is a working limit from field use.
- **Unused ports.** By default ports still named `IN 15` / `OUT 15` are left blank so the router keeps what it has. Untick the box in step 1 to send them.
- **Exports.** Label set, load file, CSV, and a multi-page PDF. Copy the table back into Lucid.

## Use

1. Copy the router table (header row down) from your doc, then press Ctrl+V (Cmd+V) on the page. Or press "Start blank".
2. Fix anything the checks flag. Edit IN LABEL, OUT LABEL or XPT directly in the grid.
3. Download the label set or load file, or copy the link / QR to share the table.

Expected columns: IN, FROM (PATCH), IN LABEL, OUT LABEL, ROUTED SOURCE, XPT, OUT. Rows are matched by the "IN 01" to "IN 40" labels. A CSV with the header `PORT,IN_PATCH,IN_LABEL,XPT_IN,OUT_LABEL` also loads.

## Helper script (`videohub_push.py`)

Optional. Python 3, standard library only; the computer must be on the same network as the Videohub.

```
python3 videohub_push.py videohub_load.txt 192.168.1.50            # send, print ACK/NAK per block
python3 videohub_push.py videohub_load.txt 192.168.1.50 --verify   # send, then check the router holds it
python3 videohub_push.py --read 192.168.1.50                       # save the router's state to videohub_state.txt
python3 videohub_push.py videohub.csv                              # convert the CSV to videohub_load.txt
```

Without Python, the page shows one-line `nc` commands for macOS and Linux; on Windows use PuTTY as in the Videohub manual. Loading replaces what you list on the unit, so read the router first to keep a backup, and try a new file on a bench unit before show day.

## Not yet verified on hardware

Tested against label sets saved by Videohub Setup (40x40 and 120x120) and a mock router. Not yet confirmed on a real unit: how Videohub Setup treats a label set whose size does not match the router, its handling of commas or quotes in labels, and the real label length limit.

## Host on GitHub Pages

Files: `index.html`, `favicon.svg`, `videohub_push.py`, `README.md`, `CNAME`. Settings > Pages > Source: "Deploy from a branch", branch `main`, folder `/ (root)`.

## Notes

- Includes `qrcode-generator` by Kazuhiko Arase (MIT license) inline for the QR code.
- Not affiliated with or endorsed by Blackmagic Design.
