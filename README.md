# Videohub File Generator

A single-page tool for Blackmagic Videohub 40x40 routers. Paste a router table, check it, edit it, and download the Videohub load file and a CSV. Share a link or QR code so a tech opens the same table with no accounts.

Runs entirely in the browser. Nothing is uploaded or stored; the table data travels inside the link after the `#`.

## Use

1. Copy the router table (header row down) from your doc, then press Ctrl+V (Cmd+V) on the page.
2. Fix anything the checks flag. Edit IN LABEL, OUT LABEL or XPT directly in the grid.
3. Download `videohub_load.txt` or the CSV, or copy the link / QR to share the table.

Expected columns: IN, FROM (PATCH), IN LABEL, OUT LABEL, ROUTED SOURCE, XPT, OUT. Rows are matched by the "IN 01" to "IN 40" labels. A CSV with the header `PORT,IN_PATCH,IN_LABEL,XPT_IN,OUT_LABEL` also loads.

## Copy back into Lucid

"Copy table for Lucid" copies the current table (ROUTED SOURCE filled in) as a table. In Lucid click the first cell under the header ("▶ IN 01"), press Esc, paste, then select the whole table and set font size 5 + Bold (Lucid pastes at 12pt, so it looks blank until you do; row shading is not carried over).

## Output

`videohub_load.txt` uses the Videohub Ethernet protocol blocks (`INPUT LABELS:`, `OUTPUT LABELS:`, `VIDEO OUTPUT ROUTING:`), 0-based, one blank line between blocks. Test on your own unit before relying on it.

`videohub_push.py` sends the file to a unit: `python3 videohub_push.py videohub_load.txt 192.168.1.50` (Python 3, same network as the Videohub). Loading replaces the labels and routes on the unit.

## Host on GitHub Pages

1. Create a public repo (the name becomes part of every shared link, so choose it once).
2. Upload `index.html` and this README to the repo root.
3. Settings > Pages > Source: "Deploy from a branch", Branch: `main`, folder `/ (root)`. Save.
4. After a minute the page is live at `https://<user>.github.io/<repo>/`.

## Notes

- Includes `qrcode-generator` by Kazuhiko Arase (MIT license) inline for the QR code.
- Not affiliated with or endorsed by Blackmagic Design.
