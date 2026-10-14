#!/usr/bin/env python3
"""Regenerate data.js from the Masters gnome spreadsheet (stdlib only).

Usage: python3 scripts/build_data.py path/to/masters-gnome-database.xlsx
"""
import json, re, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

M = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
ns = {'m': M, 'r': R}

def col(ref):
    n = 0
    for c in re.match(r'[A-Z]+', ref).group():
        n = n * 26 + ord(c) - 64
    return n - 1

def read_sheets(path):
    z = zipfile.ZipFile(path)
    ss = [''.join(t.text or '' for t in si.iter(f'{{{M}}}t'))
          for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns)]
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    out = {}
    for s in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets', ns):
        target = rels[s.get(f'{{{R}}}id')].lstrip('/').removeprefix('xl/')
        rows = []
        for r in ET.fromstring(z.read('xl/' + target)).iter(f'{{{M}}}row'):
            row = {}
            for c in r.findall('m:c', ns):
                v = c.find('m:v', ns)
                if c.get('t') == 'inlineStr':
                    val = ''.join(x.text or '' for x in c.iter(f'{{{M}}}t'))
                elif v is None:
                    continue
                elif c.get('t') == 's':
                    val = ss[int(v.text)]
                else:
                    val = v.text
                row[col(c.get('r'))] = val
            if row:
                rows.append([row.get(i, '') for i in range(max(row) + 1)])
        out[s.get('name')] = rows
    return out

def table(raw, name, keys):
    return [dict(zip(keys, [c.strip() for c in r] + [''] * (len(keys) - len(r))))
            for r in raw[name][1:]]

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raw = read_sheets(sys.argv[1])
    data = {
        'gnomes': table(raw, 'Gnomes', ['id', 'year', 'type', 'champion', 'outfit', 'facts', 'height', 'price', 'where', 'quantity', 'evidence', 'sources', 'conflicts', '_a', '_b', '_c', 'photoCount']),
        'editions': table(raw, 'Editions', ['year', 'edition', 'sold', 'count', 'context', 'champion', 'score', 'toPar', 'playoff', 'status']),
        'notables': table(raw, 'Notables', ['year', 'champion', 'fact', 'sources', 'evidence']),
        'photos': table(raw, 'Photos', ['id', 'year', 'gnome', 'role', 'img', 'page', 'outlet', 'credit', 'shows', 'source', 'size', 'note', 'checked', 'reuse']),
        'sources': table(raw, 'Sources', ['id', 'outlet', 'title', 'date', 'url']),
        'questions': table(raw, 'Open_Questions', ['n', 'topic', 'says', 'resolve']),
    }
    for g in data['gnomes']:  # personal-tracking columns are not published
        for k in ('_a', '_b', '_c'):
            g.pop(k)
    dest = Path(__file__).resolve().parent.parent / 'data.js'
    dest.write_text('window.GNOME_DATA=' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
    print(f'wrote {dest}: ' + ', '.join(f'{k}={len(v)}' for k, v in data.items()))

main()
