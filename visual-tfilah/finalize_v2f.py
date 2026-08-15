#!/usr/bin/env python3
"""Build v2f as targeted edits on Dan's v2e — never a regeneration.

Dan hand-edits the deck between rounds (slide-4 layout, translation line breaks,
the wider slide-10 box). Regenerating from a script would discard those, the same
way build.sh would have discarded his v1a work. So v2f takes v2e as the source of
truth and applies only the fixes from his v2e notes.

Usage: finalize_v2f.py V2E.pptx OUT.pptx
"""
import os
import re
import shutil
import subprocess
import sys
import zipfile

SRC, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_v2fwork")
PPTX = os.environ.get("PPTX_SKILL") or subprocess.run(
    ["bash", "-c", "find \"$HOME/Library/Application Support/Claude\" -type d -name pptx "
                   "-path '*/skills/*' 2>/dev/null | tail -1"],
    capture_output=True, text=True).stdout.strip()

DIM, LIT = "B8E3E6", "FFFFFF"
CLOSED, OPEN, BULLET = "‣", "▾", "•"
EMU = 914400
LNSPC = 5760                       # 57.6pt body line spacing
NAV_X, NAV_W, NAV_H = 15167006, 2807208, 5303520
NAV_Y = 1024128                    # 1.12" — top-aligned with the transliteration box (item 2)

RPR_EN = ('<a:rPr lang="en-US" sz="{sz}"{b}><a:solidFill><a:srgbClr val="{col}"/></a:solidFill>'
          '<a:latin typeface="Calibri (MS)"/><a:cs typeface="Calibri (MS)"/></a:rPr>')
RPR_HE = ('<a:rPr lang="he-IL" sz="{sz}"{b}><a:solidFill><a:srgbClr val="{col}"/></a:solidFill>'
          '<a:latin typeface="David Libre"/><a:ea typeface="David Libre"/>'
          '<a:cs typeface="David Libre"/><a:sym typeface="David Libre"/><a:rtl/></a:rPr>')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def para(text, rpr, algn="l", rtl=False, lnspc=None, indent=0):
    ppr = f'<a:pPr algn="{algn}"' + (' rtl="1"' if rtl else "")
    ppr += f' marL="{indent}" indent="0"' if indent else ""
    ppr += ">" + (f'<a:lnSpc><a:spcPts val="{lnspc}"/></a:lnSpc>' if lnspc else "") + "</a:pPr>"
    sp = ' xml:space="preserve"' if text != text.strip() else ""
    return f"<a:p>{ppr}<a:r>{rpr}<a:t{sp}>{esc(text)}</a:t></a:r></a:p>"


# ------------------------------------------------------------ the 30-slide plan
# (section, item). None,None = title/closing (no nav). This is v2e's order with
# slide 14 split into Adonai S'fatai + Eternity Utters a Day.
PLAN = [
    (None, None),
    ("Opening", "Pledge / HaTikvah"),
    ("Opening", "Hinei Mah Tov"),
    ("Opening", "Living Our Values"),
    ("Opening", "Modeh Ani"),
    ("Opening", "Ozi V'zimrat Yah"),
    ("Sh'ma and Its Blessings", "Bar'chu"),
    ("Sh'ma and Its Blessings", "Sh'ma"),
    ("Sh'ma and Its Blessings", "V'ahavta"),
    ("Sh'ma and Its Blessings", "V'ahavta"),
    ("Sh'ma and Its Blessings", "V'ahavta"),
    ("Sh'ma and Its Blessings", "Mi Chamochah"),
    ("Amidah", "Amidah"),
    ("Amidah", "Adonai S'fatai"),          # 14a (new)
    ("Amidah", "Eternity Utters a Day"),   # 14b (new)
    ("Amidah", "Mi Shebeirach"),
    ("Amidah", "Mi Shebeirach"),
    ("Amidah", "Oseh Shalom"),
    ("The Blessings of Our Lives", "Class Song"),
    ("The Blessings of Our Lives", "Birthday Blessings"),
    ("The Blessings of Our Lives", "Rock Counting"),
    ("Prayers of Welcome", "Candles"),
    ("Prayers of Welcome", "Kiddush"),
    ("Prayers of Welcome", "Kiddush"),
    ("Prayers of Welcome", "Kiddush"),
    ("Prayers of Welcome", "Motzi"),
    ("Conclusion", "Priestly Blessing"),
    ("Conclusion", "Shofar Blessing"),
    ("Conclusion", "Turn the World Around"),
    (None, None),
]

SECTIONS, SPAN = [], {}
for sec, item in PLAN:
    if sec is None:
        continue
    if not SECTIONS or SECTIONS[-1][0] != sec:
        SECTIONS.append((sec, []))
    if item not in SECTIONS[-1][1]:
        SECTIONS[-1][1].append(item)
    SPAN[(sec, item)] = SPAN.get((sec, item), 0) + 1


def nav_xml(cur_sec, cur_item, dot_pos):
    ps = []
    for sec, items in SECTIONS:
        openit = sec == cur_sec
        ps.append(para(f"{OPEN if openit else CLOSED} {sec}",
                       RPR_EN.format(sz=1800, b=' b="1"', col=LIT if openit else DIM), lnspc=2200))
        if not openit:
            continue
        for it in items:
            here = it == cur_item
            ps.append(para(f"{BULLET} {it}",
                           RPR_EN.format(sz=1800, b=' b="1"' if here else "", col=LIT if here else DIM),
                           lnspc=2200, indent=182880))
            n = SPAN.get((sec, it), 1)
            if here and n > 1 and dot_pos:
                dots = " ".join("●" if k == dot_pos else "○" for k in range(1, n + 1))
                ps.append(para(dots, RPR_EN.format(sz=1400, b="", col=LIT), lnspc=2000, indent=365760))
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="900" name="Service Nav"/><p:cNvSpPr txBox="1"/>'
            f'<p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{NAV_X}" y="{NAV_Y}"/>'
            f'<a:ext cx="{NAV_W}" cy="{NAV_H}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/>'
            f'</a:prstGeom><a:noFill/></p:spPr><p:txBody><a:bodyPr lIns="0" tIns="0" rIns="0" '
            f'bIns="0" rtlCol="0" anchor="t" wrap="square"/><a:lstStyle/>{"".join(ps)}</p:txBody></p:sp>')


# --------------------------------------------------------------- slide helpers
def slide_files(root):
    rels = open(f"{root}/ppt/_rels/presentation.xml.rels", encoding="utf-8").read()
    rmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', rels))
    order = re.findall(r'<p:sldId[^>]*r:id="(rId\d+)"', open(
        f"{root}/ppt/presentation.xml", encoding="utf-8").read())
    return [rmap[r] for r in order]


def set_shape_text(xml, name, paragraphs):
    def repl(m):
        b = m.group(0)
        if f'name="{name}"' not in b:
            return b
        return re.sub(r"(<a:lstStyle/>).*?(</p:txBody>)",
                      lambda mm: mm.group(1) + paragraphs + mm.group(2), b, flags=re.S)
    return re.sub(r"<p:sp>.*?</p:sp>", repl, xml, flags=re.S)


def read_path(f):
    return f"{WORK}/ppt/slides/{f}"


# =============================================================================
if os.path.exists(WORK):
    shutil.rmtree(WORK)
zipfile.ZipFile(SRC).extractall(WORK)
order = slide_files(WORK)
print(f"v2e: {len(order)} slides")

# -------------------------------------------------- item 9: split slide 14
IDX14 = 13                                 # 0-based; slide 14 is "Eternity Utters a Day"
orig14 = order[IDX14]
r = subprocess.run([sys.executable, f"{PPTX}/scripts/add_slide.py", WORK, orig14, "--after", orig14],
                   capture_output=True, text=True)
m = re.search(r"Created ppt/slides/(slide\d+\.xml)", r.stdout)
if not m:
    sys.exit(f"add_slide failed splitting slide 14: {r.stdout}{r.stderr}")
new14 = m.group(1)

# original slide 14 -> "Adonai S'fatai" (the Amidah opening prayer)
a = open(read_path(orig14), encoding="utf-8").read()
a = set_shape_text(a, "TextBox 15", para("Adonai S’fatai", RPR_EN.format(sz=3199, b=' b="1"', col=LIT)))
a = set_shape_text(a, "TextBox 12", para("אֲדֹנָי שְׂפָתַי", RPR_HE.format(sz=4200, b="", col=LIT), algn="r", rtl=True))
a = set_shape_text(a, "TextBox 10", "".join(
    para(t, RPR_EN.format(sz=3600, b="", col=LIT), lnspc=LNSPC)
    for t in ["Adonai, s’fatai tiftach,", "ufi yagid t’hilatecha."]))
open(read_path(orig14), "w", encoding="utf-8").write(a)

# new slide -> "Eternity Utters a Day" (the Dan Nichols song), Hebrew psalm removed
b = open(read_path(new14), encoding="utf-8").read()
b = set_shape_text(b, "TextBox 11", "<a:p/>")               # drop the Adonai s'fatai Hebrew
b = set_shape_text(b, "TextBox 18",
                   para("“Eternity Utters a Day” — Dan Nichols, on Psalm 51:17",
                        RPR_EN.format(sz=2799, b="", col=LIT)))
open(read_path(new14), "w", encoding="utf-8").write(b)
print(f"split slide 14: Adonai S'fatai ({orig14}) + Eternity Utters a Day ({new14})")

order = slide_files(WORK)                                   # refresh after the split


# ----------------------------- item 6: V'ahavta cantillation (Deut 6:5-9, Num 15:40-41)
# Pointed te'amim from Sefaria, Tetragrammaton rendered יְיָ, re-broken to match the
# existing English rows on each slide. David Libre renders the marks correctly.
VAHAVTA = {
    "You shall love Adonai your God": [   # slide 9 — Deut 6:5-6
        "וְאָ֣הַבְתָּ֔ אֵ֖ת יְיָ֣ אֱלֹהֶ֑יךָ", "בְּכׇל־לְבָבְךָ֥", "וּבְכׇל־נַפְשְׁךָ֖",
        "וּבְכׇל־מְאֹדֶֽךָ׃", "וְהָי֞וּ הַדְּבָרִ֣ים הָאֵ֗לֶּה", "אֲשֶׁ֨ר אָנֹכִ֧י מְצַוְּךָ֛",
        "הַיּ֖וֹם עַל־לְבָבֶֽךָ׃"],
    "Repeat them to your children": [     # slide 10 — Deut 6:7-9
        "וְשִׁנַּנְתָּ֣ם לְבָנֶ֔יךָ", "וְדִבַּרְתָּ֖ בָּ֑ם", "בְּשִׁבְתְּךָ֤ בְּבֵיתֶ֙ךָ֙",
        "וּבְלֶכְתְּךָ֣ בַדֶּ֔רֶךְ", "וּֽבְשׇׁכְבְּךָ֖ וּבְקוּמֶֽךָ׃", "וּקְשַׁרְתָּ֥ם לְא֖וֹת עַל־יָדֶ֑ךָ",
        "וְהָי֥וּ לְטֹטָפֹ֖ת בֵּ֥ין עֵינֶֽיךָ׃", "וּכְתַבְתָּ֛ם עַל־מְזֻז֥וֹת", "בֵּיתֶ֖ךָ וּבִשְׁעָרֶֽיךָ׃"],
    "In this way, you will remember": [   # slide 11 — Num 15:40-41
        "לְמַ֣עַן תִּזְכְּר֔וּ", "וַעֲשִׂיתֶ֖ם אֶת־כׇּל־מִצְוֺתָ֑י", "וִהְיִיתֶ֥ם קְדֹשִׁ֖ים",
        "לֵאלֹֽהֵיכֶֽם׃", "אֲנִ֞י יְיָ֣ אֱלֹֽהֵיכֶ֗ם", "אֲשֶׁ֨ר הוֹצֵ֤אתִי אֶתְכֶם֙",
        "מֵאֶ֣רֶץ מִצְרַ֔יִם", "לִהְי֥וֹת לָכֶ֖ם לֵאלֹהִ֑ים", "אֲנִ֖י יְיָ֥ אֱלֹהֵיכֶֽם׃"],
}


def apply_vahavta(f):
    x = open(read_path(f), encoding="utf-8").read()
    left = "".join(re.findall(r"<a:t[^>]*>(.*?)</a:t>", x, re.S))
    key = next((k for k in VAHAVTA if k in left), None)
    if not key:
        return False
    heb = VAHAVTA[key]
    x = set_shape_text(x, "TextBox 11", "".join(
        para(t, RPR_HE.format(sz=4500, b="", col=LIT), algn="r", rtl=True, lnspc=LNSPC) for t in heb))
    open(read_path(f), "w", encoding="utf-8").write(x)
    return True


# ---------------------------- item 10: Mi Shebeirach placeholder text
LOREM = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
         "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")


def apply_misheb_placeholder(f):
    x = open(read_path(f), encoding="utf-8").read()
    if "English refrain" not in x:
        return False
    # real translation styling — Calibri 28, white — so it shows font/size/color
    x = set_shape_text(x, "TextBox 18", para(LOREM, RPR_EN.format(sz=2799, b="", col=LIT)))
    open(read_path(f), "w", encoding="utf-8").write(x)
    return True


# ---------------------------------------- items 1, 3, 11: per-slide geometry fixes
LINE_EMU = int(round(LNSPC / 100 * 12700))     # 57.6pt in EMU
BODY_BOXES = ("TextBox 10", "TextBox 11", "Hebrew Body")


def fix_geometry(f):
    x = open(read_path(f), encoding="utf-8").read()

    # item 11: the crowd logo's blip carries negative top/bottom fillRect insets
    # from v1d that stretch it tall once the box is square — reset to a flush fill.
    def logo(m):
        b = m.group(0)
        if 'name="Freeform 9"' not in b:
            return b
        return re.sub(r"<a:stretch>.*?</a:stretch>", "<a:stretch><a:fillRect/></a:stretch>", b, flags=re.S)
    x = re.sub(r"<p:sp>.*?</p:sp>", logo, x, flags=re.S)

    # items 1 & 3: body boxes sized to their content (a little pad below the last
    # line), autofit off — an oversized box overlaps the translation and reads as
    # a stray grouped shape.
    def grow(m):
        b = m.group(0)
        nm = re.search(r'name="([^"]*)"', b)
        if not nm or nm.group(1) not in BODY_BOXES:
            return b
        nlines = sum(1 for p in re.finditer(r"<a:p>(.*?)</a:p>", b, re.S)
                     if "".join(re.findall(r"<a:t[^>]*>(.*?)</a:t>", p.group(1), re.S)).strip())
        cy = max(1, nlines) * LINE_EMU + 274320       # + 0.3"
        b = re.sub(r'(<a:ext cx="\d+" cy=")\d+', lambda mm: mm.group(1) + str(cy), b, count=1)
        return b.replace("<a:spAutoFit/>", "").replace("<a:normAutofit/>", "")
    return re.sub(r"<p:sp>.*?</p:sp>", grow, x, flags=re.S)


# ------------------------------------------------- item 2 + nav: regenerate the nav
def apply_nav(f, sec, item, dot_pos):
    x = open(read_path(f), encoding="utf-8").read()
    x = re.sub(r'<p:sp>(?:(?!</p:sp>).)*?name="Service Nav".*?</p:sp>', "", x, flags=re.S)
    if sec is not None:
        x = x.replace("</p:spTree>", nav_xml(sec, item, dot_pos) + "</p:spTree>", 1)
    return x


# --------------------------------------------------------------- run every pass
seen = {}
for f, (sec, item) in zip(order, PLAN):
    apply_vahavta(f)
    apply_misheb_placeholder(f)
    x = fix_geometry(f)
    open(read_path(f), "w", encoding="utf-8").write(x)
    dot = 0
    if sec is not None:
        seen[(sec, item)] = seen.get((sec, item), 0) + 1
        dot = seen[(sec, item)]
    navved = apply_nav(f, sec, item, dot)      # read the file BEFORE opening it for write
    open(read_path(f), "w", encoding="utf-8").write(navved)

print("applied geometry, nav, V'ahavta trop, Mi Shebeirach placeholder")

# --------------------------------------------------------------------- repack
subprocess.run([sys.executable, f"{PPTX}/scripts/clean.py", WORK], check=True)
subprocess.run([sys.executable, f"{HERE}/pack.py", WORK, OUT, SRC], check=True)
subprocess.run([sys.executable, f"{PPTX}/scripts/office/validate.py", OUT, "--original", SRC])
