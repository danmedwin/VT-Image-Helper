#!/usr/bin/env python3
"""v2j — icons for the song/theme slides, from Dan's Activity & Recreation and
Travel packs, applied to v2i (build-from-latest).

  * Modeh Ani (morning gratitude) -> sun
  * Ozi V'zimrat Yah ("my strength and song") -> guitar
  * Eternity Utters a Day (song) -> microphone
  * Mi Chamochah (crossing the sea) -> sailboat on waves

All interpretive matches — flagged for Dan.

Usage: build_v2j.py IN.pptx OUT.pptx
"""
import os
import re
import shutil
import subprocess
import sys
import zipfile

SRC, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_v2jwork")
ICONS = os.path.expanduser("~/Documents/Davis Files/Jewish Life Board/icons-renamed")
PPTX = os.environ.get("PPTX_SKILL") or subprocess.run(
    ["bash", "-c", "find \"$HOME/Library/Application Support/Claude\" -type d -name pptx "
                   "-path '*/skills/*' 2>/dev/null | tail -1"],
    capture_output=True, text=True).stdout.strip()
EMU = 914400

# header, icon, x, y, w, h (inches) — centred in the open zone below the text
ADD = [
    ("Modeh Ani", "sun", 6.30, 5.55, 2.50, 2.45),
    ("Ozi V’zimrat Yah", "guitar", 6.55, 5.20, 2.40, 2.96),
    ("Eternity Utters a Day", "microphone", 11.10, 3.40, 3.30, 2.21),  # right half is empty (no Hebrew)
    ("Mi Chamochah", "sailboat", 6.35, 5.55, 2.90, 2.68),
]


def slide_files(root):
    rels = open(f"{root}/ppt/_rels/presentation.xml.rels", encoding="utf-8").read()
    rmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', rels))
    order = re.findall(r'<p:sldId[^>]*r:id="(rId\d+)"', open(
        f"{root}/ppt/presentation.xml", encoding="utf-8").read())
    return [rmap[r] for r in order]


def header_of(sx):
    hdr = next((m.group(0) for m in re.finditer(r"<p:sp>.*?</p:sp>", sx, re.S)
                if 'name="TextBox 15"' in m.group(0)), "")
    return "".join(re.findall(r"<a:t[^>]*>(.*?)</a:t>", hdr, re.S)).strip()


if os.path.exists(WORK):
    shutil.rmtree(WORK)
zipfile.ZipFile(SRC).extractall(WORK)
order = slide_files(WORK)

ct_path = f"{WORK}/[Content_Types].xml"
ct = open(ct_path, encoding="utf-8").read()
if 'Extension="png"' not in ct:
    ct = ct.replace("<Default", '<Default Extension="png" ContentType="image/png"/><Default', 1)
    open(ct_path, "w", encoding="utf-8").write(ct)

pid = 980
for header, icon, x, y, w, h in ADD:
    f = next((ff for ff in order if header_of(open(f"{WORK}/ppt/slides/{ff}", encoding="utf-8").read()) == header), None)
    if not f:
        sys.exit(f"no slide with header {header!r}")
    sp = f"{WORK}/ppt/slides/{f}"
    sx = open(sp, encoding="utf-8").read()
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
    open(sp, "w", encoding="utf-8").write(sx.replace("</p:spTree>", pic + "</p:spTree>", 1))
    print(f"{header}: {icon}")
    pid += 1

subprocess.run([sys.executable, f"{HERE}/pack.py", WORK, OUT, SRC], check=True)
subprocess.run([sys.executable, f"{PPTX}/scripts/office/validate.py", OUT, "--original", SRC])
