# Masters Gnome Database

Static site (plain HTML/CSS/JS, no backend) cataloging the gnomes sold at the Masters. Data comes from `masters-gnome-database_1.xlsx`, embedded in `data.js`.

Open `index.html` in a browser, or serve the folder with any static host (e.g. GitHub Pages).

Reference photos are linked, not hosted.

## Updating the data

After editing the spreadsheet, regenerate `data.js` (Python 3, no dependencies) and push:

```sh
python3 scripts/build_data.py path/to/masters-gnome-database.xlsx
```
