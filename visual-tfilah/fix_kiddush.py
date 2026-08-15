#!/usr/bin/env python3
"""Repair the three Kiddush slides in the v1c working tree.

Dan built Kiddush 2 and 3 in PowerPoint by duplicating a Last Word slide and
pasting text in. Three things came along with that:

  * the Hebrew went in as pasted bitmaps rather than text, and the Kiddush 3
    bitmap is truncated — it loses "kidash'ta mikol haamim" and the whole
    final line, leaving 5 Hebrew lines against 7 of transliteration
  * the sidebar still highlights "Last Word" instead of "Kiddush"
  * the progress dots from v1b are gone

This puts the Hebrew back as live David Libre text matched line for line to
Dan's transliteration, repoints the sidebar, and restores the dots.

Usage: fix_kiddush.py UNPACKED_DIR   (the directory a v1a-derived deck was unzipped into)
"""
import os
import re
import sys

if len(sys.argv) != 2:
    sys.exit(__doc__.strip().splitlines()[-1])
WORK = os.path.join(sys.argv[1], "ppt", "slides", "")

HEB_X, HEB_Y, HEB_CX, HEB_CY = 8665588, 1095006, 5794490, 6438900
LNSPC = 5760  # 57.6pt — shared with the transliteration column so the rows register

# Hebrew transcribed from Dan's own bitmaps, with Kiddush 3's missing words restored.
KIDDUSH2 = [
    "בָּרוּךְ אַתָּה, יְיָ,",
    "אֱלֹהֵינוּ, מֶלֶךְ הָעוֹלָם,",
    "אֲשֶׁר קִדְּשָׁנוּ בְּמִצְוֹתָיו",
    "וְרָצָה בָנוּ, וְשַׁבַּת קָדְשׁוֹ",
    "בְּאַהֲבָה וּבְרָצוֹן הִנְחִילָנוּ,",
    "זִכָּרוֹן לְמַעֲשֵׂה בְרֵאשִׁית.",
]
KIDDUSH3 = [
    "כִּי הוּא יוֹם תְּחִלָּה",
    "לְמִקְרָאֵי קֹדֶשׁ,",
    "זֵכֶר לִיצִיאַת מִצְרָיִם.",
    "כִּי בָנוּ בָחַרְתָּ וְאוֹתָנוּ",
    "קִדַּשְׁתָּ מִכָּל הָעַמִּים,",
    "וְשַׁבַּת קָדְשְׁךָ",
    "בְּאַהֲבָה וּבְרָצוֹן הִנְחַלְתָּנוּ.",
]
CHATIMAH = "בָּרוּךְ אַתָּה, יְיָ, מְקַדֵּשׁ הַשַּׁבָּת."


def rpr(sz):
    return (
        f'<a:rPr lang="he-IL" sz="{sz}"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
        '<a:latin typeface="David Libre"/><a:ea typeface="David Libre"/>'
        '<a:cs typeface="David Libre"/><a:sym typeface="David Libre"/><a:rtl/></a:rPr>'
    )


def hebrew_box(shape_id, name, lines, x, y, cx, cy, sz=4500, algn="r"):
    paras = "".join(
        f'<a:p><a:pPr algn="{algn}" rtl="1"><a:lnSpc><a:spcPts val="{LNSPC}"/></a:lnSpc></a:pPr>'
        f"<a:r>{rpr(sz)}<a:t>{line}</a:t></a:r></a:p>"
        for line in lines
    )
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{name}"/>'
        '<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr>'
        f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody>'
        '<a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="t">'
        f"<a:spAutoFit/></a:bodyPr><a:lstStyle/>{paras}</p:txBody></p:sp>"
    )


def dots_box(shape_id, pattern):
    """v1b's dot strip: sits in the header bar between the English and Hebrew titles."""
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="Progress Dots"/>'
        '<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr>'
        '<a:xfrm><a:off x="7315200" y="64008"/><a:ext cx="3657600" cy="557784"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr><p:txBody>'
        '<a:bodyPr wrap="none" anchor="ctr" lIns="0" rIns="0" tIns="0" bIns="0">'
        "<a:spAutoFit/></a:bodyPr><a:lstStyle/>"
        '<a:p><a:pPr algn="ctr"/><a:r><a:rPr sz="2200">'
        '<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
        f'<a:latin typeface="Calibri (MS)"/></a:rPr><a:t>{pattern}</a:t></a:r></a:p>'
        "</p:txBody></p:sp>"
    )


def next_id(xml):
    return max(int(n) for n in re.findall(r'<p:cNvPr id="(\d+)"', xml)) + 1


def drop_pic(xml, rid):
    """Remove the <p:pic> that embeds rid. Returns (xml, removed_name)."""
    for m in re.finditer(r"<p:pic>.*?</p:pic>", xml, re.S):
        if f'r:embed="{rid}"' in m.group(0):
            name = re.search(r'name="([^"]*)"', m.group(0))
            return xml[: m.start()] + xml[m.end() :], (name.group(1) if name else "?")
    sys.exit(f"could not find a <p:pic> embedding {rid}")


def rel_id(slide, target):
    rels = open(f"{WORK}_rels/{slide}.rels", encoding="utf-8").read()
    m = re.search(r'Id="(rId\d+)"[^>]*Target="\.\./media/' + re.escape(target) + '"', rels)
    return m.group(1) if m else sys.exit(f"{target} not referenced by {slide}")


def highlight(xml, item):
    """Repoint the sidebar highlight: dim every entry, then brighten `item`."""
    def fix(m):
        blk = m.group(1)
        text = "".join(re.findall(r"<a:t>(.*?)</a:t>", blk, re.S)).strip()
        want = "FFFFFF" if text == item else "B8E3E6"
        return "<a:p>" + re.sub(r'(<a:solidFill><a:srgbClr val=")[0-9A-Fa-f]{6}',
                                lambda c: c.group(1) + want, blk) + "</a:p>"

    def in_sidebar(m):
        return "<a:t>Bim Bam</a:t>" in m.group(0)

    out = []
    last = 0
    for sp in re.finditer(r"<p:sp>.*?</p:sp>", xml, re.S):
        if not in_sidebar(sp):
            continue
        out.append(xml[last : sp.start()])
        out.append(re.sub(r"<a:p>(.*?)</a:p>", fix, sp.group(0), flags=re.S))
        last = sp.end()
        break
    out.append(xml[last:])
    return "".join(out)


def insert(xml, *shapes):
    return xml.replace("</p:spTree>", "".join(shapes) + "</p:spTree>", 1)


def save(slide, xml):
    open(WORK + slide, "w", encoding="utf-8").write(xml)


# --- Kiddush 1: dots only -----------------------------------------------------
x = open(WORK + "slide8.xml", encoding="utf-8").read()
x = insert(x, dots_box(next_id(x), "● ○ ○"))
save("slide8.xml", x)
print("slide8  (Kiddush 1 of 3): added progress dots ● ○ ○")

# --- Kiddush 2: bitmap Hebrew -> live text, sidebar, dots ---------------------
x = open(WORK + "slide9.xml", encoding="utf-8").read()
x, name = drop_pic(x, rel_id("slide9.xml", "image9.png"))
i = next_id(x)
x = insert(x,
           hebrew_box(i, "Hebrew Body", KIDDUSH2, HEB_X, HEB_Y, HEB_CX, HEB_CY),
           dots_box(i + 1, "○ ● ○"))
x = highlight(x, "Kiddush")
save("slide9.xml", x)
print(f"slide9  (Kiddush 2 of 3): replaced bitmap '{name}' with {len(KIDDUSH2)} lines of live Hebrew;"
      " sidebar Last Word -> Kiddush; added dots ○ ● ○")

# --- Kiddush 3: two bitmaps -> live text (restoring the lost words) -----------
x = open(WORK + "slide10.xml", encoding="utf-8").read()
body_rid = rel_id("slide10.xml", "image10.png")
chat_rid = rel_id("slide10.xml", "image11.png")

# The transliterated chatimah sets the column the Hebrew chatimah must sit over.
# Find it by shape name — its text is split across runs, so matching on the text fails.
chat_sp = next(sp.group(0) for sp in re.finditer(r"<p:sp>.*?</p:sp>", x, re.S)
               if 'name="Baruch atah, Adonai, m’kadeish HaShabbat."' in sp.group(0))
geo = re.search(r'<a:off x="(\d+)" y="(\d+)"/><a:ext cx="(\d+)" cy="(\d+)"', chat_sp)
x_tr, cx_tr = int(geo.group(1)), int(geo.group(3))
cy_tr = 813816  # the height the Hebrew bitmap occupied, one line at 45pt

x, body_name = drop_pic(x, body_rid)
x, chat_name = drop_pic(x, chat_rid)
i = next_id(x)
x = insert(
    x,
    hebrew_box(i, "Hebrew Body", KIDDUSH3, HEB_X, HEB_Y, HEB_CX, HEB_CY),
    hebrew_box(i + 1, "Hebrew Chatimah", [CHATIMAH], x_tr, 6705600, cx_tr, cy_tr,
               algn="ctr"),
    dots_box(i + 2, "○ ○ ●"),
)
x = highlight(x, "Kiddush")
save("slide10.xml", x)
print(f"slide10 (Kiddush 3 of 3): replaced bitmaps '{body_name}' and '{chat_name}' with live Hebrew;"
      f" restored the truncated words, {len(KIDDUSH3)} lines matching the transliteration;"
      " sidebar Last Word -> Kiddush; added dots ○ ○ ●")
