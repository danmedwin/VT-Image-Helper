#!/usr/bin/env python3
"""Drop media relationships no shape references any more.

clean.py treats a media file as live if any rels file names it, so pictures
deleted from a slide keep their bytes in the package. Run this first to cut the
dangling relationships; clean.py then collects the orphaned media.

Usage: prune_rels.py UNPACKED_DIR
"""
import glob
import os
import re
import sys

# an <a:blip> carries a PNG plus, often, an HD Photo companion — both go when the picture does
MEDIA = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
    "http://schemas.microsoft.com/office/2007/relationships/hdphoto",
)

if len(sys.argv) != 2:
    sys.exit(__doc__.strip().splitlines()[-1])
root = sys.argv[1]

for rels_path in sorted(glob.glob(os.path.join(root, "ppt/slides/_rels/*.xml.rels"))):
    slide_name = os.path.basename(rels_path)[: -len(".rels")]
    slide = open(os.path.join(root, "ppt/slides", slide_name), encoding="utf-8").read()
    rels = open(rels_path, encoding="utf-8").read()
    used = set(re.findall(r'r:(?:embed|link|id)="(rId\d+)"', slide))
    dropped = []

    def keep(m):
        entry = m.group(0)
        rid = re.search(r'Id="(rId\d+)"', entry).group(1)
        if any(f'Type="{t}"' in entry for t in MEDIA) and rid not in used:
            dropped.append(re.search(r'Target="([^"]*)"', entry).group(1))
            return ""
        return entry

    out = re.sub(r"<Relationship [^>]*/>", keep, rels)
    if dropped:
        open(rels_path, "w", encoding="utf-8").write(out)
        print(f"{slide_name:<16} dropped {', '.join(dropped)}")
