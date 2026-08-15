#!/usr/bin/env python3
"""v2i — Dan's next round of icon notes, applied to v2h (build-from-latest).

  * Hamotzi: swap the covered challah for the uncovered braided loaf.
  * Adonai S'fatai: speech bubbles.
  * Amidah: the Star-of-David book.
  * Mi Shebeirach (both slides): the second, so-far-unused hamsa (healing).
  * Sh'ma: the arched Sh'ma-text artwork lifted from the school's old template
    slide (an image, not live text).

Priestly Blessing's split-finger kohanim hand is left for a separate step —
no such icon exists in our packs yet.

Usage: build_v2i.py IN.pptx OUT.pptx
"""
import os
import re
import shutil
import subprocess
import sys
import zipfile

SRC, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_v2iwork")
ICONS = os.path.expanduser("~/Documents/Davis Files/Jewish Life Board/icons-renamed")
TEMPLATE = "/Users/medwin/Documents/Davis Files/Davis VT/New VT Template (in progress w Claude).pptx"
PPTX = os.environ.get("PPTX_SKILL") or subprocess.run(
    ["bash", "-c", "find \"$HOME/Library/Application Support/Claude\" -type d -name pptx "
                   "-path '*/skills/*' 2>/dev/null | tail -1"],
    capture_output=True, text=True).stdout.strip()
EMU = 914400


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


def add_pic(slide_file, src_png, dest_name, x, y, w, h, pid, name):
    sp = f"{WORK}/ppt/slides/{slide_file}"
    sx = open(sp, encoding="utf-8").read()
    shutil.copy(src_png, f"{WORK}/ppt/media/{dest_name}")
    rp = f"{WORK}/ppt/slides/_rels/{slide_file}.rels"
    rels = open(rp, encoding="utf-8").read()
    rid = "rId%d" % (max(int(r[3:]) for r in re.findall(r'Id="(rId\d+)"', rels)) + 1)
    rels = rels.replace("</Relationships>",
                        f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
                        f'officeDocument/2006/relationships/image" Target="../media/{dest_name}"/>'
                        "</Relationships>")
    open(rp, "w", encoding="utf-8").write(rels)
    ox, oy, cx, cy = (int(round(v * EMU)) for v in (x, y, w, h))
    pic = (f'<p:pic><p:nvPicPr><p:cNvPr id="{pid}" name="{name}"/><p:cNvPicPr/>'
           f'<p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/><a:stretch>'
           f'<a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{ox}" y="{oy}"/>'
           f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/>'
           f'</a:prstGeom></p:spPr></p:pic>')
    open(sp, "w", encoding="utf-8").write(sx.replace("</p:spTree>", pic + "</p:spTree>", 1))


def find(header):
    for f in order:
        sx = open(f"{WORK}/ppt/slides/{f}", encoding="utf-8").read()
        if header_of(sx) == header:
            return f
    sys.exit(f"no slide with header {header!r}")


# --- Hamotzi: remove the covered challah (Picture 18), add the uncovered loaf ---
ham = find("Hamotzi")
hx = open(f"{WORK}/ppt/slides/{ham}", encoding="utf-8").read()
hx = re.sub(r'<p:pic>(?:(?!</p:pic>).)*?name="Picture 18".*?</p:pic>', "", hx, flags=re.S)
open(f"{WORK}/ppt/slides/{ham}", "w", encoding="utf-8").write(hx)
add_pic(ham, f"{ICONS}/challah.png", "icon_challah.png", 5.88, 6.10, 3.90, 1.76, 971, "Icon challah")
print("Hamotzi: covered challah -> uncovered braided loaf")

# --- Adonai S'fatai: speech bubbles -----------------------------------------
add_pic(find("Adonai S’fatai"), f"{ICONS}/speech-bubbles.png", "icon_speech.png",
        6.65, 5.55, 2.70, 2.36, 972, "Icon speech-bubbles")
print("Adonai S'fatai: speech bubbles")

# --- Amidah: Star-of-David book (right side, where the page-numbers leave room) --
add_pic(find("Amidah"), f"{ICONS}/book-star-of-david.png", "icon_sod_book.png",
        11.60, 2.60, 3.20, 2.74, 973, "Icon book-star-of-david")
print("Amidah: Star-of-David book")

# --- Mi Shebeirach (both): the unused hamsa (hamsa-2) -------------------------
pid = 974
for f in order:
    sx = open(f"{WORK}/ppt/slides/{f}", encoding="utf-8").read()
    if header_of(sx) == "Mi Shebeirach":
        add_pic(f, f"{ICONS}/hamsa-2.png", f"icon_hamsa2_{pid}.png", 7.55, 5.25, 2.20, 2.96, pid, "Icon hamsa-2")
        pid += 1
print("Mi Shebeirach x2: hamsa-2 (healing)")

# --- Sh'ma: the arched Sh'ma artwork from the old template slide --------------
# The template art is blue on its yellow background; recolour the glyphs solid
# white so they read on the Davis dark-blue slide (thresholding the alpha fills
# the anti-aliased edges so the strokes stay bold).
from PIL import Image
with zipfile.ZipFile(TEMPLATE) as tz:
    tz.extract("ppt/media/image15.png", f"{WORK}/_tmpl")
arch = Image.open(f"{WORK}/_tmpl/ppt/media/image15.png").convert("RGBA")
apx = arch.load()
white = Image.new("RGBA", arch.size, (0, 0, 0, 0))
wpx = white.load()
for yy in range(arch.height):
    for xx in range(arch.width):
        if apx[xx, yy][3] >= 48:
            wpx[xx, yy] = (255, 255, 255, 255)
white.save(f"{WORK}/_tmpl/shma_arch_white.png")
add_pic(find("Sh’ma"), f"{WORK}/_tmpl/shma_arch_white.png", "shma_arch.png",
        2.64, 5.80, 11.00, 1.83, 977, "Sh'ma Arch")
shutil.rmtree(f"{WORK}/_tmpl")
print("Sh'ma: arched Sh'ma artwork (recoloured white for the dark background)")

subprocess.run([sys.executable, f"{PPTX}/scripts/clean.py", WORK], check=True)
subprocess.run([sys.executable, f"{HERE}/pack.py", WORK, OUT, SRC], check=True)
subprocess.run([sys.executable, f"{PPTX}/scripts/office/validate.py", OUT, "--original", SRC])
