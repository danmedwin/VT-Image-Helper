#!/usr/bin/env python3
"""Build v2 — the 8/21/2026 Kabbalat Shabbat deck, from Michelle's outline.

Sources, in order of preference:
  * "New VT Template (in progress w Claude).pptx" — the base package. Already
    20" x 11.25", and it carries the school's own Hatikvah, L.O.V.E., Modeh Ani,
    Ozi V'zimrat Yah, Sh'ma, V'ahavta, Amidah and Shehecheyanu slides.
  * v1d — Candles, Kiddush x3, Motzi, Oseh Shalom, Priestly Blessing, Rocks.
    The template's own versions of these have their Hebrew flattened to outlines;
    v1d's are live text. The two packages share a theme and an identical
    slideLayout7 (bar a stale date placeholder), so the slides move over cleanly.
  * Built fresh here — Hinei Mah Tov, Bar'chu, Mi Chamochah, Mi Shebeirach and
    the Shofar Blessing, none of which exist in either deck.

Three slides are deliberate placeholders: the Class Song (changes weekly), the
English refrain of Mi Shebeirach, and Turn the World Around. The latter two are
copyrighted lyrics rather than liturgy and need to come from the school's own
slides.

Usage: build_v2.py TEMPLATE.pptx V1D.pptx OUT.pptx
"""
import os
import re
import shutil
import subprocess
import sys
import zipfile

TEMPLATE, V1D, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_v2work")

DIM, LIT = "B8E3E6", "FFFFFF"          # Davis sidebar: resting vs current
CLOSED, OPEN, BULLET = "‣", "▾", "•"

# ---------------------------------------------------------------- the service
# (section, item, source) where source is ("T", n) template slide n,
# ("D", n) v1d slide n, ("NEW", key), or ("HOLD", key) for a placeholder.
# An item spanning several slides repeats, and gets progress dots in the nav.
PLAN = [
    (None, None, ("T", 1)),                                   # title
    ("Opening", "Pledge / HaTikvah", ("T", 2)),
    ("Opening", "Hinei Mah Tov", ("NEW", "hinei")),
    ("Opening", "Living Our Values", ("T", 3)),
    ("Opening", "Modeh Ani", ("T", 9)),
    ("Opening", "Ozi V'zimrat Yah", ("T", 7)),
    ("Sh'ma and Its Blessings", "Bar'chu", ("NEW", "barchu")),
    ("Sh'ma and Its Blessings", "Sh'ma", ("T", 15)),
    ("Sh'ma and Its Blessings", "V'ahavta", ("T", 16)),
    ("Sh'ma and Its Blessings", "V'ahavta", ("T", 17)),
    ("Sh'ma and Its Blessings", "V'ahavta", ("T", 18)),
    ("Sh'ma and Its Blessings", "Mi Chamochah", ("NEW", "michamochah")),
    ("Amidah", "Amidah", ("T", 24)),
    ("Amidah", "Amidah", ("T", 23)),
    ("Amidah", "Mi Shebeirach", ("NEW", "mishebeirach")),
    ("Amidah", "Mi Shebeirach", ("HOLD", "mishebeirach_english")),
    ("Amidah", "Oseh Shalom", ("D", 12)),
    ("The Blessings of Our Lives", "Class Song", ("HOLD", "classsong")),
    ("The Blessings of Our Lives", "Birthday Blessings", ("T", 32)),
    ("The Blessings of Our Lives", "Rock Counting", ("D", 14)),
    ("Prayers of Welcome", "Candles", ("D", 5)),
    ("Prayers of Welcome", "Kiddush", ("D", 7)),
    ("Prayers of Welcome", "Kiddush", ("D", 8)),
    ("Prayers of Welcome", "Kiddush", ("D", 9)),
    ("Prayers of Welcome", "Motzi", ("D", 11)),
    ("Conclusion", "Priestly Blessing", ("D", 13)),
    ("Conclusion", "Shofar Blessing", ("NEW", "shofar")),
    ("Conclusion", "Turn the World Around", ("HOLD", "turntheworld")),
    (None, None, ("T", 47)),                                  # closing
]

# ------------------------------------------------------ text for the new slides
# Hebrew from the standard liturgy; transliteration per the CCAR Press Style
# Guide (apostrophe for sh'va na only, "ei" for tzeirei, no apostrophe as a
# two-vowel separator). Line breaks pair Hebrew to transliteration one for one.
NEW = {
    "hinei": dict(
        en="Hinei Mah Tov", he_title="הִנֵּה מַה טּוֹב",
        translit=["Hineih mah tov u'mah na-im", "shevet achim gam yachad."],
        hebrew=["הִנֵּה מַה־טּוֹב וּמַה־נָּעִים", "שֶׁבֶת אַחִים גַּם־יָחַד."],
        translation="How good and how pleasant it is that brothers and sisters dwell together. (Psalm 133:1)",
        notes="Hinei Mah Tov — Psalm 133:1. Setting: Arian.",
    ),
    "barchu": dict(
        en="Bar'chu", he_title="בָּרְכוּ",
        translit=["Bar'chu et Adonai ham'vorach!", "Baruch Adonai ham'vorach l'olam va-ed!"],
        hebrew=["בָּרְכוּ אֶת יְיָ הַמְבֹרָךְ!", "בָּרוּךְ יְיָ הַמְבֹרָךְ לְעוֹלָם וָעֶד!"],
        translation="Praise Adonai, to whom praise is due! Praise Adonai, to whom praise is due, now and forever!",
        notes="Bar'chu — the call to worship. Setting: Seigel. Leader sings line 1, congregation responds with line 2.",
    ),
    "michamochah": dict(
        en="Mi Chamochah", he_title="מִי כָמֹכָה",
        translit=["Mi chamochah ba-eilim, Adonai!", "Mi kamochah nedar bakodesh,",
                  "nora t'hilot, oseih fele!"],
        hebrew=["מִי כָמֹכָה בָּאֵלִם יְיָ,", "מִי כָּמֹכָה נֶאְדָּר בַּקֹּדֶשׁ,",
                "נוֹרָא תְהִלֹּת עֹשֵׂה פֶלֶא."],
        translation="Who is like You, Adonai, among the gods that are worshipped? Who is like You, majestic in holiness, awesome in splendor, working wonders!",
        notes="Mi Chamochah — Setting: Debbie Friedman (NOT the Miriam setting, and NOT the 'Don't Worry Be Happy' version in the old template).",
    ),
    "mishebeirach": dict(
        en="Mi Shebeirach", he_title="מִי שֶׁבֵּרַךְ",
        translit=["Mi shebeirach avoteinu,", "m'kor hab'rachah l'imoteinu.",
                  "Mi shebeirach imoteinu,", "m'kor hab'rachah la'avoteinu."],
        hebrew=["מִי שֶׁבֵּרַךְ אֲבוֹתֵינוּ,", "מְקוֹר הַבְּרָכָה לְאִמּוֹתֵינוּ.",
                "מִי שֶׁבֵּרַךְ אִמּוֹתֵינוּ,", "מְקוֹר הַבְּרָכָה לַאֲבוֹתֵינוּ."],
        translation="May the One who blessed our fathers be the source of blessing for our mothers; may the One who blessed our mothers be the source of blessing for our fathers.",
        notes="Mi Shebeirach — Setting: Debbie Friedman. The English refrain is Friedman's own copyrighted lyric; it goes on the NEXT slide, from the school's existing file.",
    ),
    "shofar": dict(
        en="Shofar Blessing", he_title="תְּקִיעַת שׁוֹפָר",
        translit=["Baruch atah, Adonai,", "Eloheinu Melech haolam,",
                  "asher kid'shanu b'mitzvotav", "v'tzivanu lishmoa kol shofar."],
        hebrew=["בָּרוּךְ אַתָּה יְיָ,", "אֱלֹהֵינוּ מֶלֶךְ הָעוֹלָם,",
                "אֲשֶׁר קִדְּשָׁנוּ בְּמִצְוֹתָיו", "וְצִוָּנוּ לִשְׁמֹעַ קוֹל שׁוֹפָר."],
        translation="Blessed are You, Adonai our God, Sovereign of the universe, who makes us holy with mitzvot and calls us to hear the sound of the shofar.",
        notes="Shofar Blessing — all shofar blowers. NOTE for Dan: this b'rachah belongs to Rosh HaShanah. During Elul the shofar is customarily sounded WITHOUT a blessing. Confirm before Friday.",
    ),
}

HOLD = {
    "mishebeirach_english": ("Mi Shebeirach", "מִי שֶׁבֵּרַךְ",
                            "English refrain — Debbie Friedman",
                            "Friedman's English refrain is her own copyrighted lyric, so it is not "
                            "reproduced here. Paste in the school's existing slide."),
    "classsong": ("Class Song", "שִׁיר הַכִּתָּה", "Class Song",
                  "Changes weekly. Drop this week's song in — same frame, same type sizes."),
    "turntheworld": ("Turn the World Around", "", "Turn the World Around — Harry Belafonte",
                     "Belafonte's lyric is copyrighted, so it is not reproduced here. "
                     "Paste in the school's existing slide."),
}

# --------------------------------------------------------------------- helpers
PPTX = os.environ.get("PPTX_SKILL") or subprocess.run(
    ["bash", "-c", "find \"$HOME/Library/Application Support/Claude\" -type d -name pptx "
                   "-path '*/skills/*' 2>/dev/null | tail -1"],
    capture_output=True, text=True).stdout.strip()

RPR_HE = ('<a:rPr lang="he-IL" sz="{sz}"{b}><a:solidFill><a:srgbClr val="{col}"/></a:solidFill>'
          '<a:latin typeface="David Libre"/><a:ea typeface="David Libre"/>'
          '<a:cs typeface="David Libre"/><a:sym typeface="David Libre"/><a:rtl/></a:rPr>')
RPR_EN = ('<a:rPr lang="en-US" sz="{sz}"{b}><a:solidFill><a:srgbClr val="{col}"/></a:solidFill>'
          '<a:latin typeface="Calibri (MS)"/><a:cs typeface="Calibri (MS)"/></a:rPr>')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def para(text, rpr, algn="l", rtl=False, lnspc=None, indent=0):
    ppr = f'<a:pPr algn="{algn}"' + (' rtl="1"' if rtl else "")
    ppr += f' marL="{indent}" indent="0"' if indent else ""
    ppr += ">" + (f'<a:lnSpc><a:spcPts val="{lnspc}"/></a:lnSpc>' if lnspc else "") + "</a:pPr>"
    return f"<a:p>{ppr}<a:r>{rpr}<a:t>{esc(text)}</a:t></a:r></a:p>"


def set_shape_text(xml, shape_name, paragraphs_xml):
    """Replace the body of the named text box, keeping its geometry."""
    def repl(m):
        b = m.group(0)
        if f'name="{shape_name}"' not in b:
            return b
        return re.sub(r"(<a:lstStyle/>).*?(</p:txBody>)",
                      lambda mm: mm.group(1) + paragraphs_xml + mm.group(2), b, flags=re.S)
    return re.sub(r"<p:sp>.*?</p:sp>", repl, xml, flags=re.S)


def slide_files(pkg_dir):
    rels = open(f"{pkg_dir}/ppt/_rels/presentation.xml.rels", encoding="utf-8").read()
    rmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', rels))
    order = re.findall(r'<p:sldId[^>]*r:id="(rId\d+)"', open(
        f"{pkg_dir}/ppt/presentation.xml", encoding="utf-8").read())
    return [rmap[r] for r in order]


# ------------------------------------------------------------------- the build
if os.path.exists(WORK):
    shutil.rmtree(WORK)
zipfile.ZipFile(TEMPLATE).extractall(WORK)
tmpl_slides = slide_files(WORK)
print(f"template: {len(tmpl_slides)} slides")

# --- import the v1d slides -----------------------------------------------------
V1DDIR = os.path.join(HERE, "_v1dwork")
if os.path.exists(V1DDIR):
    shutil.rmtree(V1DDIR)
zipfile.ZipFile(V1D).extractall(V1DDIR)
v1d_slides = slide_files(V1DDIR)

ct_path = f"{WORK}/[Content_Types].xml"
ct = open(ct_path, encoding="utf-8").read()
pres_rels_path = f"{WORK}/ppt/_rels/presentation.xml.rels"
pres_rels = open(pres_rels_path, encoding="utf-8").read()

next_slide = max(int(re.search(r"(\d+)", s).group(1)) for s in os.listdir(f"{WORK}/ppt/slides")
                 if s.startswith("slide")) + 1
next_rid = max(int(r[3:]) for r in re.findall(r'Id="(rId\d+)"', pres_rels)) + 1
imported = {}      # v1d slide number -> new slide filename

for _, _, src in PLAN:
    if src[0] != "D" or src[1] in imported:
        continue
    n = src[1]
    sxml = open(f"{V1DDIR}/ppt/slides/{v1d_slides[n-1]}", encoding="utf-8").read()
    srels = open(f"{V1DDIR}/ppt/slides/_rels/{v1d_slides[n-1]}.rels", encoding="utf-8").read()

    new_name = f"slide{next_slide}.xml"
    next_slide += 1

    # carry the media across under collision-proof names
    out_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for rid, typ, tgt in re.findall(r'Id="(rId\d+)"\s+Type="([^"]*)"\s+Target="([^"]*)"', srels):
        if "slideLayout" in typ:
            out_rels.append(f'<Relationship Id="{rid}" Type="{typ}" Target="../slideLayouts/slideLayout7.xml"/>')
        elif "notesSlide" in typ:
            continue                                    # speaker notes are rebuilt below
        elif "/media/" in tgt:
            base = os.path.basename(tgt)
            dest = f"v1d_{n}_{base}"
            shutil.copy(f"{V1DDIR}/ppt/media/{base}", f"{WORK}/ppt/media/{dest}")
            ext = base.rsplit(".", 1)[1].lower()
            if f'Extension="{ext}"' not in ct:
                mime = {"png": "image/png", "jpeg": "image/jpeg", "jpg": "image/jpeg",
                        "wdp": "image/vnd.ms-photo"}.get(ext, "application/octet-stream")
                ct = ct.replace("<Default", f'<Default Extension="{ext}" ContentType="{mime}"/><Default', 1)
            out_rels.append(f'<Relationship Id="{rid}" Type="{typ}" Target="../media/{dest}"/>')
        else:
            out_rels.append(f'<Relationship Id="{rid}" Type="{typ}" Target="{tgt}"/>')
    out_rels.append("</Relationships>")

    sxml = re.sub(r'<p:sldLayoutId[^>]*/>', "", sxml)
    open(f"{WORK}/ppt/slides/{new_name}", "w", encoding="utf-8").write(sxml)
    open(f"{WORK}/ppt/slides/_rels/{new_name}.rels", "w", encoding="utf-8").write("".join(out_rels))
    ct = ct.replace("</Types>",
                    f'<Override PartName="/ppt/slides/{new_name}" ContentType="application/vnd.'
                    f'openxmlformats-officedocument.presentationml.slide+xml"/></Types>')
    pres_rels = pres_rels.replace("</Relationships>",
                                  f'<Relationship Id="rId{next_rid}" Type="http://schemas.openxml'
                                  f'formats.org/officeDocument/2006/relationships/slide" '
                                  f'Target="slides/{new_name}"/></Relationships>')
    imported[n] = (new_name, f"rId{next_rid}")
    next_rid += 1

open(ct_path, "w", encoding="utf-8").write(ct)
open(pres_rels_path, "w", encoding="utf-8").write(pres_rels)
print(f"imported {len(imported)} slides from v1d")

# --- clone the authoring slide for everything that has to be built fresh -------
AUTHORING = tmpl_slides[4]                       # template slide 5, the two-column frame
built = {}
for _, _, src in PLAN:
    if src[0] not in ("NEW", "HOLD") or src[1] in built:
        continue
    r = subprocess.run([sys.executable, f"{PPTX}/scripts/add_slide.py", WORK, AUTHORING],
                       capture_output=True, text=True)
    m = re.search(r"Created ppt/slides/(slide\d+\.xml)", r.stdout)
    if not m:
        sys.exit(f"add_slide failed for {src[1]}: {r.stdout}{r.stderr}")
    built[src[1]] = m.group(1)
print(f"cloned {len(built)} new slides from the authoring frame")


def fill_new(path, d):
    x = open(path, encoding="utf-8").read()
    x = set_shape_text(x, "TextBox 15", para(d["en"], RPR_EN.format(sz=3199, b=' b="1"', col="FFFFFF")))
    x = set_shape_text(x, "TextBox 12", para(d["he_title"], RPR_HE.format(sz=4200, b="", col="FFFFFF"),
                                             algn="l", rtl=True))
    x = set_shape_text(x, "TextBox 10", "".join(
        para(t, RPR_EN.format(sz=3600, b="", col="FFFFFF"), lnspc=5760) for t in d["translit"]))
    x = set_shape_text(x, "TextBox 11", "".join(
        para(t, RPR_HE.format(sz=4500, b="", col="FFFFFF"), algn="r", rtl=True, lnspc=5760)
        for t in d["hebrew"]))
    # The translation sits in "TextBox 18" INSIDE Group 16; the group's other child
    # is a background freeform whose empty txBody is easy to hit by accident.
    x = set_shape_text(x, "TextBox 18",
                       para(d["translation"], RPR_EN.format(sz=2799, b="", col="FFFFFF")))
    open(path, "w", encoding="utf-8").write(x)


def fill_hold(path, key):
    en, he, label, note = HOLD[key]
    x = open(path, encoding="utf-8").read()
    x = set_shape_text(x, "TextBox 15", para(en, RPR_EN.format(sz=3199, b=' b="1"', col="FFFFFF")))
    x = set_shape_text(x, "TextBox 12", para(he, RPR_HE.format(sz=4200, b="", col="FFFFFF"),
                                             algn="l", rtl=True) if he else "<a:p/>")
    x = set_shape_text(x, "TextBox 10", para(f"[ {label} ]", RPR_EN.format(sz=3600, b="", col=DIM),
                                             lnspc=5760))
    x = set_shape_text(x, "TextBox 11", "<a:p/>")
    x = set_shape_text(x, "TextBox 18", para(note, RPR_EN.format(sz=2799, b="", col=DIM)))
    open(path, "w", encoding="utf-8").write(x)


for key, fname in built.items():
    p = f"{WORK}/ppt/slides/{fname}"
    if key in NEW:
        fill_new(p, NEW[key])
    else:
        fill_hold(p, key)

# --- the grouped service nav ---------------------------------------------------
SECTIONS = []
for sec, item, _ in PLAN:
    if sec is None:
        continue
    if not SECTIONS or SECTIONS[-1][0] != sec:
        SECTIONS.append((sec, []))
    if item not in SECTIONS[-1][1]:
        SECTIONS[-1][1].append(item)

# how many slides each item spans, for the progress dots
SPAN = {}
for sec, item, _ in PLAN:
    if sec:
        SPAN[(sec, item)] = SPAN.get((sec, item), 0) + 1

NAV_X, NAV_Y, NAV_W, NAV_H = 15258420, 1170432, 2807208, 5303520   # 16.69" 1.28" 3.07" 5.80"


def nav_xml(cur_sec, cur_item, dot_pos):
    ps = []
    for sec, items in SECTIONS:
        openit = sec == cur_sec
        ps.append(para(f"{OPEN if openit else CLOSED} {sec}",
                       RPR_EN.format(sz=1800, b=' b="1"', col=LIT if openit else DIM),
                       lnspc=2200))
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
                ps.append(para(dots, RPR_EN.format(sz=1400, b="", col=LIT),
                               lnspc=2000, indent=365760))
    body = "".join(ps)
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="900" name="Service Nav"/><p:cNvSpPr txBox="1"/>'
            f'<p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{NAV_X}" y="{NAV_Y}"/>'
            f'<a:ext cx="{NAV_W}" cy="{NAV_H}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/>'
            f'</a:prstGeom><a:noFill/></p:spPr><p:txBody><a:bodyPr lIns="0" tIns="0" rIns="0" '
            f'bIns="0" rtlCol="0" anchor="t" wrap="square"/><a:lstStyle/>{body}</p:txBody></p:sp>')


def strip_old_nav(x):
    """Remove the old nav box and the 'M: # / MT: ###' page-reference placeholder."""
    def drop(m):
        b = m.group(0)
        txt = "".join(re.findall(r"<a:t>(.*?)</a:t>", b, re.S))
        off = re.search(r'<a:off x="(-?\d+)"', b)
        inside = off and int(off.group(1)) > 14_000_000
        if inside and re.search(r'name="TextBox 13"', b):
            return ""
        if re.match(r"^\s*M:\s*#", txt):
            return ""
        # v1d put progress dots in the header bar. The grouped nav now nests them
        # under the current item, so the header strip would be a second set.
        if re.search(r'name="Progress Dots"', b):
            return ""
        return b
    return re.sub(r"<p:sp>.*?</p:sp>", drop, x, flags=re.S)


# --- lay out the running order -------------------------------------------------
seen_item, order_rids, NO_FRAME = {}, [], []
pres_rels = open(pres_rels_path, encoding="utf-8").read()
rid_of = dict((v, k) for k, v in re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"',
                                            pres_rels))

for sec, item, src in PLAN:
    if src[0] == "T":
        fname = tmpl_slides[src[1] - 1]
    elif src[0] == "D":
        fname = imported[src[1]][0]
    else:
        fname = built[src[1]]

    path = f"{WORK}/ppt/slides/{fname}"
    x = strip_old_nav(open(path, encoding="utf-8").read())
    if sec:
        k = (sec, item)
        seen_item[k] = seen_item.get(k, 0) + 1
        # The nav only fits slides built on the Davis frame — the teal header bar
        # ("Group 2") plus the right-hand column ("Group 6") that reserves its space.
        # Several of the school's older prayer slides use a different, full-bleed
        # design with art running to the right edge; dropping a nav on those puts
        # white text straight over the Hebrew. Skip them and report instead.
        if re.search(r'name="Group 6"', x) and re.search(r'name="Group 2"', x):
            x = x.replace("</p:spTree>", nav_xml(sec, item, seen_item[k]) + "</p:spTree>", 1)
        else:
            NO_FRAME.append(f"{len(order_rids)+1:>2}. {item}")
    open(path, "w", encoding="utf-8").write(x)
    order_rids.append(rid_of[fname])

pres_path = f"{WORK}/ppt/presentation.xml"
pres = open(pres_path, encoding="utf-8").read()
lst = "".join(f'<p:sldId id="{256 + i}" r:id="{r}"/>' for i, r in enumerate(order_rids))
pres = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", f"<p:sldIdLst>{lst}</p:sldIdLst>", pres, flags=re.S)
open(pres_path, "w", encoding="utf-8").write(pres)
print(f"running order set: {len(order_rids)} slides")
if NO_FRAME:
    print("\nNO NAV — these use the school's other, full-bleed slide design and have")
    print("no right-hand column to put a nav in. They need converting to the Davis frame:")
    for n in NO_FRAME:
        print("   ", n)

# The template's nav entries were hyperlinks to other slides. Stripping the nav
# leaves those relationships dangling, and clean.py reads a dangling slide link as
# a broken reference, so drop every relationship the slide no longer points at.
# slideLayout and notesSlide are referenced implicitly, never by r:id, so they stay.
IMPLICIT = ("slideLayout", "notesSlide")
for name in sorted(os.listdir(f"{WORK}/ppt/slides/_rels")):
    rp = f"{WORK}/ppt/slides/_rels/{name}"
    sx = open(f"{WORK}/ppt/slides/{name[:-5]}", encoding="utf-8").read()
    used = set(re.findall(r'r:(?:embed|link|id)="(rId\d+)"', sx))
    rels = open(rp, encoding="utf-8").read()

    def keep(m):
        e = m.group(0)
        rid = re.search(r'Id="(rId\d+)"', e).group(1)
        if any(t in e for t in IMPLICIT):
            return e
        return e if rid in used else ""

    open(rp, "w", encoding="utf-8").write(re.sub(r"<Relationship [^>]*/>", keep, rels))

subprocess.run([sys.executable, f"{PPTX}/scripts/clean.py", WORK], check=True)
subprocess.run([sys.executable, f"{HERE}/pack.py", WORK, OUT, TEMPLATE], check=True)
subprocess.run([sys.executable, f"{PPTX}/scripts/office/validate.py", OUT, "--original", TEMPLATE])
