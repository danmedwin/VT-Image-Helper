#!/usr/bin/env python3
"""Add the obvious thematic icons to the deck — a targeted edit on the latest file.

Only the unambiguous matches go in automatically (cupcake for the birthday
blessing, a globe for Turn the World Around, an olive branch for Oseh Shalom's
"who makes peace"). Everything else is a suggestion for Dan, not an auto-add.

Usage: add_icons.py IN.pptx OUT.pptx
"""
import os
import re
import shutil
import subprocess
import sys
import zipfile

SRC, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_iconwork")
ICONS = os.path.expanduser("~/Documents/Davis Files/Jewish Life Board/icons-renamed")
PPTX = os.environ.get("PPTX_SKILL") or subprocess.run(
    ["bash", "-c", "find \"$HOME/Library/Application Support/Claude\" -type d -name pptx "
                   "-path '*/skills/*' 2>/dev/null | tail -1"],
    capture_output=True, text=True).stdout.strip()
EMU = 914400

# (1-based slide, header to confirm we've got the right slide, icon, x, y, w, h in inches)
# Each icon sits in the open zone below the text and above the bottom translation,
# centered near x=7.5", matching where Candles/Hamotzi/Shofar put theirs.
ADD = [
    (18, "Oseh Shalom", "olive-branch", 6.00, 6.05, 3.00, 2.17),
    (20, "Birthday Blessings", "cupcake", 6.51, 5.55, 1.98, 2.90),
    (29, "Turn the World Around", "earth-globe", 5.85, 5.35, 3.30, 3.21),
]


def slide_files(root):
    rels = open(f"{root}/ppt/_rels/presentation.xml.rels", encoding="utf-8").read()
    rmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', rels))
    order = re.findall(r'<p:sldId[^>]*r:id="(rId\d+)"', open(
        f"{root}/ppt/presentation.xml", encoding="utf-8").read())
    return [rmap[r] for r in order]


if os.path.exists(WORK):
    shutil.rmtree(WORK)
zipfile.ZipFile(SRC).extractall(WORK)
order = slide_files(WORK)

ct_path = f"{WORK}/[Content_Types].xml"
ct = open(ct_path, encoding="utf-8").read()
if 'Extension="png"' not in ct:
    ct = ct.replace("<Default", '<Default Extension="png" ContentType="image/png"/><Default', 1)
    open(ct_path, "w", encoding="utf-8").write(ct)

pid = 970
for n, header, icon, x, y, w, h in ADD:
    f = order[n - 1]
    sp = f"{WORK}/ppt/slides/{f}"
    sx = open(sp, encoding="utf-8").read()
    got = "".join(re.findall(r"<a:t[^>]*>(.*?)</a:t>",
                             next(m.group(0) for m in re.finditer(r"<p:sp>.*?</p:sp>", sx, re.S)
                                  if 'name="TextBox 15"' in m.group(0)), re.S)).strip()
    assert got == header, f"slide {n} header is {got!r}, expected {header!r}"

    dest = f"icon_{icon}.png"
    shutil.copy(f"{ICONS}/{icon}.png", f"{WORK}/ppt/media/{dest}")
    rp = f"{WORK}/ppt/slides/_rels/{f}.rels"
    rels = open(rp, encoding="utf-8").read()
    rid = "rId%d" % (max(int(r[3:]) for r in re.findall(r'Id="(rId\d+)"', rels)) + 1)
    rels = rels.replace("</Relationships>",
                        f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
                        f'officeDocument/2006/relationships/image" Target="../media/{dest}"/>'
                        "</Relationships>")
    open(rp, "w", encoding="utf-8").write(rels)

    ox, oy, cx, cy = (int(round(v * EMU)) for v in (x, y, w, h))
    pic = (f'<p:pic><p:nvPicPr><p:cNvPr id="{pid}" name="Icon {icon}"/><p:cNvPicPr/>'
           f'<p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/><a:stretch>'
           f'<a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{ox}" y="{oy}"/>'
           f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/>'
           f'</a:prstGeom></p:spPr></p:pic>')
    sx = sx.replace("</p:spTree>", pic + "</p:spTree>", 1)
    open(sp, "w", encoding="utf-8").write(sx)
    print(f"slide {n} ({header}): added {icon}")
    pid += 1

subprocess.run([sys.executable, f"{HERE}/pack.py", WORK, OUT, SRC], check=True)
subprocess.run([sys.executable, f"{PPTX}/scripts/office/validate.py", OUT, "--original", SRC])
