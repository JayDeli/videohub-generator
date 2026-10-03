# Videohub File Generator

A single-page tool for Blackmagic Videohub 40x40 routers. Paste a router table, check it, edit it, and download the Videohub load file and a CSV. Share a link or QR code so a tech opens the same table with no accounts.

Runs entirely in the browser. Nothing is uploaded or stored; the table data travels inside the link after the `#`.

## Use

1. Copy the router table (header row down) from your doc, then press Ctrl+V (Cmd+V) on the page.
2. Fix anything the checks flag. Edit IN LABEL, OUT LABEL or XPT directly in the grid.
3. Download `videohub_load.txt` or the CSV, or copy the link / QR to share the table.

Expected columns: IN, FROM (PATCH), IN LABEL, OUT LABEL, ROUTED SOURCE, XPT, OUT. Rows are matched by the "IN 01" to "IN 40" labels. A CSV with the header `PORT,IN_PATCH,IN_LABEL,XPT_IN,OUT_LABEL` also loads.

## Output

`videohub_load.txt` uses the Videohub Ethernet protocol blocks (`INPUT LABELS:`, `OUTPUT LABELS:`, `VIDEO OUTPUT ROUTING:`), 0-based, one blank line between blocks. Test on your own unit before relying on it.

## Host on GitHub Pages

1. Create a public repo (the name becomes part of every shared link, so choose it once).
2. Upload `index.html` and this README to the repo root.
3. Settings > Pages > Source: "Deploy from a branch", Branch: `main`, folder `/ (root)`. Save.
4. After a minute the page is live at `https://<user>.github.io/<repo>/`.

## Notes

- Includes `qrcode-generator` by Kazuhiko Arase (MIT license) inline for the QR code.
- Not affiliated with or endorsed by Blackmagic Design.
