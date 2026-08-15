#!/usr/bin/env python3
"""Repack an unpacked .pptx without directory entries.

`zip -r` writes directory entries, which make PowerPoint offer to repair the
deck and lock its objects. Cloning entry order from the original archive and
writing files only avoids that.
"""
import os, sys, zipfile

unpacked, out, original = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else None)

present = set()
for root, _, files in os.walk(unpacked):
    for f in files:
        present.add(os.path.relpath(os.path.join(root, f), unpacked))

order = []
if original:
    for n in zipfile.ZipFile(original).namelist():
        if n in present and n not in order:
            order.append(n)
order += sorted(present - set(order))

if os.path.exists(out):
    os.remove(out)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for name in order:
        z.write(os.path.join(unpacked, name), name)
print(f"wrote {out} ({len(order)} entries, {os.path.getsize(out)/1e6:.1f} MB)")
