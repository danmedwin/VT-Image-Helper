#!/usr/bin/env python3
"""Bring the deck's transliteration into line with the CCAR Press Style Guide.

Authority: https://ravblog.ccarnet.org/wp-content/uploads/2023/08/CCAR-Press-Style-Guide.pdf

The rules that bite here:

  * "Apostrophe for sh'va nah ... No apostrophe for sh'va nach" — so vacharta and
    kidashta lose theirs, and kodsh'cha keeps only the live one.
  * "'ei' for tzeirei" — zecher becomes zeicher.
  * "Hyphen for two vowels together where necessary ... but maariv, Shavuot" — the
    apostrophe is NOT the two-vowel separator, so ha'olam/ha'aretz/ya'aseh lose it.
    The guide's own word list spells it haolam.
  * The word list gives the blessing formula verbatim:
    "Baruch atah, Adonai, Eloheinu Melech haolam, asher kid'shanu b'mitzvotav v'tzivanu"
  * Prefixes are lowercase in the text of a prayer ("V'zot haTorah asher…"),
    so the chatimah reads m'kadeish haShabbat.

Apostrophes are unified on the typographic ’ (U+2019), which is what the guide
itself sets and what the deck's English possessives ("God's face") already use.

Usage: ccar_normalize.py UNPACKED_DIR
"""
import os
import re
import sys

# Exact whole-paragraph rewrites, keyed on the current text with whitespace stripped.
# Anything not listed here is left alone.
REWRITES = {
    # the blessing opener, identical on Candles / Kiddush 1 / Kiddush 2 / Motzi
    "Baruch atah Adonai,": "Baruch atah, Adonai,",
    "Baruch atah, Adonai": "Baruch atah, Adonai,",
    "Eloheinu Melech ha'olam,": "Eloheinu Melech haolam,",
    "Eloheinu, Melech haolam,": "Eloheinu Melech haolam,",
    # Candles
    "asher kid'shanu b'mitzvotav": "asher kid’shanu b’mitzvotav",
    "v'tzivanu l'hadlik": "v’tzivanu l’hadlik",
    # Kiddush 1
    "borei p'ri hagafen.": "borei p’ri hagafen.",
    # Kiddush 3
    "zecher litziat Mitzrayim.": "zeicher litziat Mitzrayim.",
    "Ki vanu vachar’ta v’otanu": "Ki vanu vacharta v’otanu",
    "kidash’ta mikol haamim,": "kidashta mikol haamim,",
    "v’Shabbat kodshecha": "v’Shabbat kodsh’cha",
    "Baruch atah, Adonai, m’kadeish HaShabbat.": "Baruch atah, Adonai, m’kadeish haShabbat.",
    # Motzi
    "hamotzi lechem min ha'aretz.": "hamotzi lechem min haaretz.",
    # Oseh Shalom
    "hu ya'aseh shalom aleinu,": "hu yaaseh shalom aleinu,",
    "v'al kol Yisrael,": "v’al kol Yisrael,",
    "v'al kol yosh'vei teiveil,": "v’al kol yosh’vei teiveil,",
    "v'imru: Amen.": "v’imru: Amen.",
    # Priestly Blessing
    "Y'varech'cha Adonai v'yishm'recha.": "Y’varech’cha Adonai v’yishm’recha.",
    "Ya'er Adonai panav eilecha vichuneka.": "Ya’eir Adonai panav eilecha vichuneka.",
    "v'yasem l'cha shalom.": "v’yasem l’cha shalom.",
    # Kiddush 2 translation — "who finding favor with us" needs the comma after "who"
    "Praise to You, Adonai our God, Sovereign of the universe who finding favor with us, "
    "sanctified us with mitzvot. In love and favor, You made the holy Shabbat our heritage "
    "as a reminder of the work of Creation.":
    "Praise to You, Adonai our God, Sovereign of the universe who, finding favor with us, "
    "sanctified us with mitzvot. In love and favor, You made the holy Shabbat our heritage "
    "as a reminder of the work of Creation.",
}

if len(sys.argv) != 2:
    sys.exit(__doc__.strip().splitlines()[-1])
slides = os.path.join(sys.argv[1], "ppt", "slides")

RUN = re.compile(r"<a:r>(?:(?!</a:r>).)*</a:r>", re.S)
TEXT = re.compile(r"<a:t>(.*?)</a:t>", re.S)
# Must handle both forms; a lazy ".*?(?:/>|</a:rPr>)" stops at the first
# self-closing CHILD (<a:srgbClr .../>) and truncates the element.
RPR = re.compile(r"<a:rPr\b[^>]*/>|<a:rPr\b[^>]*>.*?</a:rPr>", re.S)

changed = []


def rewrite_paragraph(m):
    body = m.group(1)
    runs = RUN.findall(body)
    if not runs:
        return m.group(0)
    joined = "".join("".join(TEXT.findall(r)) for r in runs)
    new = REWRITES.get(joined.strip())
    if new is None or new == joined:
        return m.group(0)

    # Collapse to a single run. Safe only when every run is formatted identically.
    # These paragraphs are split by PowerPoint's spellchecker, which stamps err="1"
    # on each word it does not recognise (every transliterated word, naturally) and
    # dirty="0" as it goes. Neither affects appearance, so both are ignored when
    # comparing — and dropped from the run that survives.
    def formatting(run):
        pr = RPR.search(run)
        return re.sub(r'\s+(?:err|dirty)="[^"]*"', "", pr.group(0)) if pr else ""

    props = {formatting(r) for r in runs}
    if len(props) != 1:
        sys.exit(f"refusing to collapse mixed-format paragraph: {joined!r}")

    esc = new.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    space = ' xml:space="preserve"' if new != new.strip() else ""
    single = f"<a:r>{props.pop()}<a:t{space}>{esc}</a:t></a:r>"
    changed.append((joined.strip(), new))
    # <a:pPr> and friends sit before the runs, so dropping the runs and appending
    # the replacement keeps paragraph properties intact.
    return "<a:p>" + RUN.sub("", body) + single + "</a:p>"


for name in sorted(os.listdir(slides)):
    if not name.endswith(".xml"):
        continue
    path = os.path.join(slides, name)
    xml = open(path, encoding="utf-8").read()
    before = len(changed)
    out = re.sub(r"<a:p>(.*?)</a:p>", rewrite_paragraph, xml, flags=re.S)
    if len(changed) > before:
        open(path, "w", encoding="utf-8").write(out)
        print(f"{name}:")
        for old, new in changed[before:]:
            print(f"    {old!r}\n -> {new!r}")

print(f"\n{len(changed)} paragraphs rewritten")
unused = set(REWRITES) - {o for o, _ in changed}
if unused:
    print("WARNING — these mappings never matched:")
    for u in sorted(unused):
        print(f"    {u!r}")
