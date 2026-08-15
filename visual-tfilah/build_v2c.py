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
    (None, None, ("D", 1)),                                   # title — v1d's blue slide
    ("Opening", "Pledge / HaTikvah", ("NEW", "hatikvah")),
    ("Opening", "Hinei Mah Tov", ("NEW", "hinei")),
    ("Opening", "Living Our Values", ("T", 3)),
    ("Opening", "Modeh Ani", ("NEW", "modehani")),
    ("Opening", "Ozi V'zimrat Yah", ("NEW", "ozi")),
    ("Sh'ma and Its Blessings", "Bar'chu", ("NEW", "barchu")),
    ("Sh'ma and Its Blessings", "Sh'ma", ("NEW", "shma")),
    ("Sh'ma and Its Blessings", "V'ahavta", ("NEW", "vahavta1")),
    ("Sh'ma and Its Blessings", "V'ahavta", ("NEW", "vahavta2")),
    ("Sh'ma and Its Blessings", "V'ahavta", ("NEW", "vahavta3")),
    ("Sh'ma and Its Blessings", "Mi Chamochah", ("NEW", "michamochah")),
    ("Amidah", "Amidah", ("NEW", "amidah1")),
    ("Amidah", "Amidah", ("NEW", "amidah2")),
    ("Amidah", "Mi Shebeirach", ("NEW", "mishebeirach")),
    ("Amidah", "Mi Shebeirach", ("HOLD", "mishebeirach_english")),
    ("Amidah", "Oseh Shalom", ("D", 12)),
    ("The Blessings of Our Lives", "Class Song", ("HOLD", "classsong")),
    ("The Blessings of Our Lives", "Birthday Blessings", ("NEW", "birthday")),
    ("The Blessings of Our Lives", "Rock Counting", ("D", 14)),
    ("Prayers of Welcome", "Candles", ("D", 5)),
    ("Prayers of Welcome", "Kiddush", ("D", 7)),
    ("Prayers of Welcome", "Kiddush", ("D", 8)),
    ("Prayers of Welcome", "Kiddush", ("D", 9)),
    ("Prayers of Welcome", "Motzi", ("D", 11)),
    ("Conclusion", "Priestly Blessing", ("D", 13)),
    ("Conclusion", "Shofar Blessing", ("NEW", "shofar")),
    ("Conclusion", "Turn the World Around", ("HOLD", "turntheworld")),
    (None, None, ("DUP", 1)),                                 # closing — copy of the title
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


# --- slides rebuilt out of the school's older full-bleed designs -----------------
# Each carried its own header bar and title boxes, ran content to the slide edge,
# and used whatever type sizes it was drawn at. Rebuilt on the authoring frame at
# the standard sizes so the nav fits and the deck reads as one deck.
# "flag" marks a slide where the Hebrew and transliteration did NOT break line for
# line and had to be re-broken at phrase boundaries — check against the melody.
REBUILT = {
    "hatikvah": dict(
        en="HaTikvah", he_title="הַתִּקְוָה",
        translit=["Kol od baleivav p’nimah", "nefesh Y’hudi homiyah", "ul’faatei mizrach kadimah",
                  "ayin l’Tziyon tzofiyah.", "Od lo av’dah tikvateinu", "hatikvah bat sh’not alpayim",
                  "lih’yot am chofshi b’artzeinu", "eretz Tziyon virushalayim."],
        hebrew=["כֹּל עוֹד בַּלֵּבָב פְּנִימָה", "נֶפֶשׁ יְהוּדִי הוֹמִיָּה,", "וּלְפַאֲתֵי מִזְרָח קָדִימָה,",
                "עַיִן לְצִיּוֹן צוֹפִיָּה,", "עוֹד לֹא אָבְדָה תִּקְוָתֵנוּ,", "הַתִּקְוָה בַּת שְׁנוֹת אַלְפַּיִם,",
                "לִהְיוֹת עַם חָפְשִׁי בְּאַרְצֵנוּ,", "אֶרֶץ צִיּוֹן וִירוּשָׁלַיִם."],
        translation="So long as within the inmost heart a Jewish spirit sings, and the eye looks eastward gazing toward Zion, our hope is not lost — the hope of two thousand years: to be a free people in our land, the land of Zion and Jerusalem.",
        notes="HaTikvah. Eight lines each, already matched.",
    ),
    "modehani": dict(
        en="Modeh Ani", he_title="מוֹדֶה אֲנִי", flag=True,
        translit=["Modeh ani l’fanecha,", "Melech chai v’kayam,", "shehechezarta bi nishmati",
                  "b’chemlah, rabbah emunatecha."],
        hebrew=["מוֹדֶה אֲנִי לְפָנֶֽיךָ,", "מֶֽלֶךְ חַי וְקַיָּם,", "שֶׁהֶחֱזַֽרְתָּ בִּי נִשְׁמָתִי",
                "בְּחֶמְלָה רַבָּה אֱמוּנָתֶֽךָ."],
        translation="I offer thanks to You, ever-living Sovereign, that You have restored my soul to me. How great is Your trust.",
        notes="Modeh Ani. Transliteration was 3 lines against 4 of Hebrew; re-broken to 4. Also read 'Modah ani' while the Hebrew said מוֹדֶה — set to Modeh to agree with the Hebrew and with Michelle's outline.",
    ),
    "ozi": dict(
        en="Ozi V’zimrat Yah", he_title="עׇזִּי וְזִמְרָת יָהּ", flag=True,
        translit=["Ozi v’zimrat Yah,", "vay’hi li vay’hi li", "lishuah, lishuah, lishuah."],
        hebrew=["עׇזִּי וְזִמְרָת יָהּ,", "וַיְהִי־לִי וַיְהִי־לִי", "לִישׁוּעָה, לִישׁוּעָה, לִישׁוּעָה."],
        translation="My strength and the song of God will be my salvation.",
        notes="Ozi V'zimrat Yah (Tigay). Hebrew was one long line against 3 of transliteration; re-broken to 3 to follow the repetitions. Was set at 88pt Hebrew / 60pt transliteration — now the standard 45/36.",
    ),
    "shma": dict(
        en="Sh’ma", he_title="שְׁמַע",
        translit=["Sh’ma Yisrael,", "Adonai Eloheinu, Adonai Echad!", "Baruch shem k’vod malchuto",
                  "l’olam va-ed."],
        hebrew=["שְׁמַע יִשְׂרָאֵל,", "יְיָ אֱלֹהֵֽינוּ, יְיָ אֶחָד!", "בָּרוּךְ שֵׁם כְּבוֹד מַלְכוּתוֹ",
                "לְעוֹלָם וָעֶד!"],
        translation="Hear O Israel: Adonai is our God, Adonai is One! Blessed is God’s glorious majesty for ever and ever.",
        notes="Sh'ma (Pik). Had no translation at all — one added. Tetragrammaton changed from יְהֹוָה to יְיָ to match Reform practice and the rest of the deck.",
    ),
    "vahavta2": dict(
        en="V’ahavta", he_title="וְאָהַבְתָּ", flag=True, body_h=8400000,
        translit=["Repeat them to your children", "and speak them", "when you sit at home",
                  "and when you walk on the street,", "when you lie down and when you get up.",
                  "Tie them as a sign on your hand,", "and let them be a symbol between your eyes.",
                  "Write them on the doorposts", "of your house and on your gates."],
        hebrew=["וְשִׁנַּנְתָּם לְבָנֶֽיךָ", "וְדִבַּרְתָּ בָּם", "בְּשִׁבְתְּךָ בְּבֵיתֶֽךָ",
                "וּבְלֶכְתְּךָ בַדֶּֽרֶךְ", "וּבְשָׁכְבְּךָ וּבְקוּמֶֽךָ.", "וּקְשַׁרְתָּם לְאוֹת עַל־יָדֶֽךָ",
                "וְהָיוּ לְטֹטָפֹת בֵּין עֵינֶֽיךָ.", "וּכְתַבְתָּם עַל־מְזֻזוֹת", "בֵּיתֶֽךָ וּבִשְׁעָרֶֽיךָ."],
        translation="",
        notes="V'ahavta 2 of 3. The left column is the English reading, not transliteration — that is how this prayer was already laid out. English was 11 lines against 9 of Hebrew; re-broken to 9.",
    ),
    "vahavta3": dict(
        en="V’ahavta", he_title="וְאָהַבְתָּ", body_h=8400000,
        translit=["In this way, you will remember", "and do all My mitzvot,", "and you will be holy",
                  "to your God.", "I am Adonai your God", "who brought you out of",
                  "the land of Egypt", "to be your God.", "I am Adonai your God."],
        hebrew=["לְמַֽעַן תִּזְכְּרוּ", "וַעֲשִׂיתֶם אֶת־כָּל־מִצְוֹתָי", "וִהְיִיתֶם קְדֹשִׁים",
                "לֵאלֹהֵיכֶם.", "אֲנִי יְיָ אֱלֹהֵיכֶם", "אֲשֶׁר הוֹצֵֽאתִי אֶתְכֶם",
                "מֵאֶֽרֶץ מִצְרַֽיִם", "לִהְיוֹת לָכֶם לֵאלֹהִים", "אֲנִי יְיָ אֱלֹהֵיכֶם."],
        translation="",
        notes="V'ahavta 3 of 3. Nine lines each, already matched. Stray masora circles (U+05AF) stripped from the Hebrew; יְהֹוָה changed to יְיָ.",
    ),
    "amidah1": dict(
        en="Amidah", he_title="עֲמִידָה",
        translit=["Please rise and open your siddur:", "Adonai S’fatai — 124 or 98",
                  "Avot v’Imahot — 126 or 100", "G’vurot — 128 or 102", "K’dushah — 130 or 104"],
        hebrew=[],
        translation="Student siddur: page 10.",
        notes="Amidah — a stage-direction slide, not liturgy, so it has no Hebrew body.",
    ),
    "vahavta1": dict(
        en="V\u2019ahavta", he_title="\u05d5\u05b0\u05d0\u05b8\u05d4\u05b7\u05d1\u05b0\u05ea\u05bc\u05b8", body_h=8400000,
        translit=["You shall love Adonai your God", "with all your heart,", "with all your soul,",
                  "and with all your might.", "Place these words", "which I command you today",
                  "on your heart.", "\u2026"],
        hebrew=["\u05d5\u05b0\u05d0\u05b8\u05d4\u05b7\u05d1\u05b0\u05ea\u05bc\u05b8 \u05d0\u05b5\u05ea \u05d9\u05b0\u05d9\u05b8 \u05d0\u05b1\u05dc\u05b9\u05d4\u05b6\u05bd\u05d9\u05da\u05b8",
                "\u05d1\u05bc\u05b0\u05db\u05b8\u05dc\u05be\u05dc\u05b0\u05d1\u05b8\u05d1\u05b0\u05da\u05b8", "\u05d5\u05bc\u05d1\u05b0\u05db\u05b8\u05dc\u05be\u05e0\u05b7\u05e4\u05b0\u05e9\u05c1\u05b0\u05da\u05b8",
                "\u05d5\u05bc\u05d1\u05b0\u05db\u05b8\u05dc\u05be\u05de\u05b0\u05d0\u05b9\u05d3\u05b6\u05bd\u05da\u05b8\u05c3", "\u05d5\u05b0\u05d4\u05b8\u05d9\u05d5\u05bc \u05d4\u05b7\u05d3\u05bc\u05b0\u05d1\u05b8\u05e8\u05b4\u05d9\u05dd \u05d4\u05b8\u05d0\u05b5\u05bc\u05dc\u05b6\u05bc\u05d4",
                "\u05d0\u05b2\u05e9\u05c1\u05b6\u05e8 \u05d0\u05b8\u05e0\u05b9\u05db\u05b4\u05d9 \u05de\u05b0\u05e6\u05b7\u05d5\u05bc\u05b0\u05da\u05b8", "\u05d4\u05b7\u05d9\u05bc\u05d5\u05b9\u05dd \u05e2\u05b7\u05dc\u05be\u05dc\u05b0\u05d1\u05b8\u05d1\u05b6\u05bd\u05da\u05b8\u05c3", "\u2026"],
        translation="",
        notes="V'ahavta 1 of 3. Left column is the English reading, matching how this prayer was already laid out. Was a full-bleed rose-illustration slide; rebuilt on the Davis frame with the nav. Yod-vav divine name corrected to yy.",
    ),
    "amidah2": dict(
        en="Eternity Utters a Day", he_title="\u05e2\u05b2\u05de\u05b4\u05d9\u05d3\u05b8\u05d4",
        translit=["A thought has blown the marketplace away,", "there is a song on the wind and joy in the trees.",
                  "Shabbat has arrived in the world,", "scattering a song in the silence of the night,",
                  "and eternity utters a day. (2x)"],
        hebrew=["\u05d0\u05b2\u05d3\u05b9\u05e0\u05b8\u05d9, \u05e9\u05c2\u05b0\u05e4\u05b8\u05ea\u05b7\u05d9 \u05ea\u05b4\u05e4\u05b0\u05ea\u05bc\u05b8\u05d7,",
                "\u05d5\u05bc\u05e4\u05b4\u05d9 \u05d9\u05b7\u05d2\u05bc\u05b4\u05d9\u05d3 \u05ea\u05bc\u05b0\u05d4\u05b4\u05dc\u05b8\u05ea\u05b6\u05bd\u05da\u05b8\u05c3"],
        flag=True,
        translation="\u201cAdonai, open my lips, that my mouth may declare Your praise.\u201d (Psalm 51:17)",
        notes="Amidah 2 \u2014 Dan Nichols' \u2018Eternity Utters a Day\u2019, on the Amidah opening (Ps. 51:17). Was a full-bleed slide; rebuilt on the frame. Left is the song's English verse; right is the Hebrew psalm line. NEEDS: the sung transliteration (Adonai, s'fatai tiftach, ufi yagid t'hilatecha) and the 'Dan Nichols' credit added \u2014 the standard frame has no slot for a second transliteration block or a song credit.",
    ),
    "birthday": dict(
        en="Birthday Blessings", he_title="יוֹם הֻלֶּדֶת שָׂמֵחַ", flag=True,
        translit=["Baruch atah, Adonai,", "Eloheinu Melech haolam,",
                  "shehecheyanu v’kiy’manu", "v’higianu lazman hazeh."],
        hebrew=["בָּרוּךְ אַתָּה יְיָ,", "אֱלֹהֵינוּ מֶלֶךְ הָעוֹלָם,",
                "שֶׁהֶחֱיָנוּ וְקִיְּמָנוּ", "וְהִגִּיעָנוּ לַזְּמַן הַזֶּה."],
        translation="Blessed are You, Adonai our God, Sovereign of the universe, who has kept us alive, sustained us, and brought us to this season.",
        notes="Birthday Blessings (Shehecheyanu, Lapidus). Transliteration was only the closing clause while the Hebrew ran the whole b'rachah; both now carry the full blessing in 4 matched lines.",
    ),
}
NEW.update(REBUILT)

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


# --- illustrations ------------------------------------------------------------
# Icons come from the Jewish Life board library (LemonadePixel). Placed in the
# open area under the two columns, where the Candles and Kiddush slides put theirs.
ICONS = {
    "shofar": (os.path.expanduser("~/Documents/Davis Files/Jewish Life Board/icons/hanukkah/"
                                  "lemonadepixel_hanukkah/PNGs/lemonadepixel_hanukkah-21.png"),
               5486400, 5120640, 4114800, 2637790),      # 6.0", 5.6", 4.5 x 2.88"
}


def add_icon(work, slide_file, key, ct_path):
    src, ox, oy, cx, cy = ICONS[key]
    dest = f"icon_{key}.png"
    shutil.copy(src, f"{work}/ppt/media/{dest}")

    rp = f"{work}/ppt/slides/_rels/{slide_file}.rels"
    rels = open(rp, encoding="utf-8").read()
    rid = "rId%d" % (max(int(r[3:]) for r in re.findall(r'Id="(rId\d+)"', rels)) + 1)
    rels = rels.replace("</Relationships>",
                        f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
                        f'officeDocument/2006/relationships/image" Target="../media/{dest}"/>'
                        "</Relationships>")
    open(rp, "w", encoding="utf-8").write(rels)

    ct = open(ct_path, encoding="utf-8").read()
    if 'Extension="png"' not in ct:
        ct = ct.replace("<Default", '<Default Extension="png" ContentType="image/png"/><Default', 1)
        open(ct_path, "w", encoding="utf-8").write(ct)

    pic = (f'<p:pic><p:nvPicPr><p:cNvPr id="950" name="Shofar"/><p:cNvPicPr/><p:nvPr/>'
           f'</p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/>'
           f'</a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{ox}" y="{oy}"/>'
           f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/>'
           f'</a:prstGeom></p:spPr></p:pic>')
    sp = f"{work}/ppt/slides/{slide_file}"
    x = open(sp, encoding="utf-8").read()
    open(sp, "w", encoding="utf-8").write(x.replace("</p:spTree>", pic + "</p:spTree>", 1))


# ------------------------------------------------------------------- fix-ups
# Freeform 9's geometry is a SQUARE path (2224801 x 2224801). v1d renders it at
# 2.29 x 1.36, which squashes the mark; the template's 2.43 square is the true
# aspect. Dan asked for v1d's position, so move it down to the corner and keep
# the square — never copy v1d's dimensions.
LOGO_XY = (15511536, 7791450, 2222500, 2222500)   # 16.96", 8.52", 2.43 x 2.43


def global_fixes(x):
    """Everything that has to be true on every content slide of the deck."""
    # 1. The teal column is a group of the bar plus an empty text box the same
    #    size. The box holds nothing and just travels with the bar. Drop it.
    def degroup(m):
        g = m.group(0)
        if 'name="Group 6"' not in g:
            return g
        return re.sub(r'<p:sp>(?:(?!</p:sp>).)*?name="TextBox 8".*?</p:sp>', "", g, flags=re.S)
    x = re.sub(r"<p:grpSp>(?:(?!<p:grpSp>).)*?</p:grpSp>", degroup, x, flags=re.S)

    # 2. Logo down into the corner, matching v1d rather than the template.
    def logo(m):
        b = m.group(0)
        if 'name="Freeform 9"' not in b:
            return b
        return re.sub(r'<a:off x="\d+" y="\d+"/><a:ext cx="\d+" cy="\d+"/>',
                      '<a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/>' % LOGO_XY, b, count=1)
    x = re.sub(r"<p:sp>.*?</p:sp>", logo, x, flags=re.S)

    # 3. Hebrew runs: David Libre in every slot — setting only <a:latin> leaves
    #    PowerPoint choosing a fallback for the Hebrew glyphs — and no leading
    #    space, which several of the school's slides had before מלך, יי and others.
    def run(m):
        r = m.group(0)
        txts = re.findall(r"<a:t[^>]*>(.*?)</a:t>", r, re.S)
        if not any(any("֐" <= c <= "׿" for c in t) for t in txts):
            return r
        for slot in ("latin", "ea", "cs", "sym"):
            if "<a:%s " % slot in r:
                r = re.sub(r'<a:%s typeface="[^"]*"' % slot, '<a:%s typeface="David Libre"' % slot, r)
            elif "</a:rPr>" in r:
                r = r.replace("</a:rPr>", '<a:%s typeface="David Libre"/></a:rPr>' % slot, 1)
        return re.sub(r"(<a:t[^>]*>)[  ]+", r"\1", r)
    x = re.sub(r"<a:r>(?:(?!</a:r>).)*</a:r>", run, x, flags=re.S)

    # 4. A body run with no <a:solidFill> inherits the theme colour, which reads
    #    grey on the dark panel — one line of Oseh Shalom lost its white exactly
    #    this way. Give every body run an explicit fill.
    WHITE = '<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
    GREY = re.compile(r'<a:solidFill><a:schemeClr val="tx1"><a:lumMod[^>]*/><a:lumOff[^>]*/>'
                      r'</a:schemeClr></a:solidFill>')

    def whiten(m):
        r = m.group(0)
        # v1d shipped one line of Oseh Shalom as a 50%-grey schemeClr — recolour it.
        r = GREY.sub(WHITE, r)
        # a run with no fill at all inherits the theme colour, also grey — add white.
        if "<a:solidFill>" not in r and "<a:rPr" in r:
            r = re.sub(r"(<a:rPr\b[^>/]*)(/?)>",
                       lambda mm: mm.group(1) + ">" + WHITE + ("</a:rPr>" if mm.group(2) else ""),
                       r, count=1)
        return r
    x = re.sub(r"<a:r>(?:(?!</a:r>).)*</a:r>", whiten, x, flags=re.S)

    # 5. Bottom-align the translation box so its last line sits at the same height
    #    however many lines the translation runs to.
    def bottom(m):
        b = m.group(0)
        if 'name="TextBox 18"' not in b or "<a:bodyPr" not in b:
            return b
        return re.sub(r"<a:bodyPr([^>]*?)(/?)>",
                      lambda mm: "<a:bodyPr" + re.sub(r'\s*anchor="[^"]*"', "", mm.group(1))
                      + ' anchor="b"' + mm.group(2) + ">", b, count=1)
    return re.sub(r"<p:sp>.*?</p:sp>", bottom, x, flags=re.S)


def rescale(x, f, dy=0):
    """Scale every shape's geometry and type size by f, then nudge down by dy.

    Used on Living Our Values, a designed layout rather than a two-column prayer:
    it gets squeezed clear of the nav column instead of being rebuilt.
    """
    x = re.sub(r'<a:off x="(-?\d+)" y="(-?\d+)"/>',
               lambda m: '<a:off x="%d" y="%d"/>' % (int(int(m.group(1)) * f),
                                                     int(int(m.group(2)) * f) + dy), x)
    x = re.sub(r'<a:ext cx="(\d+)" cy="(\d+)"/>',
               lambda m: '<a:ext cx="%d" cy="%d"/>' % (int(int(m.group(1)) * f),
                                                       int(int(m.group(2)) * f)), x)
    return re.sub(r'sz="(\d+)"', lambda m: 'sz="%d"' % max(100, int(int(m.group(1)) * f)), x)


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

# The chrome that makes a slide "Davis": header accent, teal column, logo. Lifted
# once from the authoring frame so it can be grafted onto designed slides.
def top_level_shapes(xml):
    """Yield each top-level shape in the spTree with its tags balanced.

    A lazy "<p:(sp|grpSp)>.*?</p:(sp|grpSp)>" will happily close an opening grpSp
    against the first </p:sp> inside it, which yields malformed XML. Groups also
    nest, so depth has to be tracked rather than pattern-matched.
    """
    body = re.search(r"<p:spTree>(.*)</p:spTree>", xml, re.S)
    if not body:
        return
    text, i = body.group(1), 0
    tag = re.compile(r"</?p:(sp|grpSp|pic|graphicFrame|cxnSp)[ >/]")
    while True:
        m = tag.search(text, i)
        if not m:
            return
        if m.group(0).startswith("</"):
            i = m.end()
            continue
        name, depth, j = m.group(1), 0, m.start()
        scan = re.compile(r"</?p:%s[ >/]" % name)
        for t in scan.finditer(text, m.start()):
            if text[t.start():t.start() + 2] == "</":
                depth -= 1
                if depth == 0:
                    end = text.index(">", t.start()) + 1
                    yield text[j:end]
                    i = end
                    break
            elif not text[t.start():t.end()].endswith("/>"):
                depth += 1
        else:
            return


_auth = open(f"{WORK}/ppt/slides/{AUTHORING}", encoding="utf-8").read()
CHROME = "".join(sh for sh in top_level_shapes(_auth)
                 if re.search(r'name="(Group 2|Group 6|Freeform 5|Freeform 9)"', sh))
if CHROME.count("<p:grpSp>") != CHROME.count("</p:grpSp>") or CHROME.count("<p:sp>") != CHROME.count("</p:sp>"):
    sys.exit("chrome extraction produced unbalanced XML")

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

dup = {}
for _, _, src in PLAN:
    if src[0] != "DUP" or src[1] in dup:
        continue
    r = subprocess.run([sys.executable, f"{PPTX}/scripts/add_slide.py", WORK, imported[src[1]][0]],
                       capture_output=True, text=True)
    m = re.search(r"Created ppt/slides/(slide\d+\.xml)", r.stdout)
    if not m:
        sys.exit(f"add_slide failed duplicating v1d slide {src[1]}: {r.stdout}{r.stderr}")
    dup[src[1]] = m.group(1)
print(f"duplicated {len(dup)} slide(s) for the closing")


def fill_new(path, d):
    x = open(path, encoding="utf-8").read()
    x = set_shape_text(x, "TextBox 15", para(d["en"], RPR_EN.format(sz=3199, b=' b="1"', col="FFFFFF")))
    x = set_shape_text(x, "TextBox 12", para(d["he_title"], RPR_HE.format(sz=4200, b="", col="FFFFFF"),
                                             algn="l", rtl=True))
    x = set_shape_text(x, "TextBox 10", "".join(
        para(t, RPR_EN.format(sz=3600, b="", col="FFFFFF"), lnspc=5760) for t in d["translit"]))
    x = set_shape_text(x, "TextBox 11", "".join(
        para(t, RPR_HE.format(sz=4500, b="", col="FFFFFF"), algn="r", rtl=True, lnspc=5760)
        for t in d["hebrew"]) or "<a:p/>")
    if d.get("body_h"):        # the V'ahavta readings run 9 lines and need the room
        for box in ("TextBox 10", "TextBox 11"):
            x = re.sub(r'(name="' + box + r'".*?<a:ext cx="\d+" cy=")\d+',
                       lambda m: m.group(1) + str(d["body_h"]), x, flags=re.S)
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

NAV_X, NAV_Y, NAV_W, NAV_H = 15167006, 758952, 2807208, 5303520   # 16.59" 0.83" — Dan's v2a position


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
    elif src[0] == "DUP":
        fname = dup[src[1]]
    else:
        fname = built[src[1]]

    path = f"{WORK}/ppt/slides/{fname}"
    x = strip_old_nav(open(path, encoding="utf-8").read())

    # Living Our Values is a designed layout, not a two-column prayer, so instead of
    # rebuilding it we squeeze it clear of the nav column and graft the chrome on.
    if src == ("T", 3):
        x = rescale(x, 16.15 / 18.63, dy=274320)
        x = x.replace("</p:spTree>", CHROME + "</p:spTree>", 1)

    if sec:
        x = global_fixes(x)
    if sec:
        k = (sec, item)
        seen_item[k] = seen_item.get(k, 0) + 1
        # The nav only fits slides built on the Davis frame — the teal header bar
        # ("Group 2") plus the right-hand column ("Group 6") that reserves its space.
        # Several of the school's older prayer slides use a different, full-bleed
        # design with art running to the right edge; dropping a nav on those puts
        # white text straight over the Hebrew. Skip them and report instead.
        # Detect the frame by the teal column's actual fill, not by shape name —
        # "Group 2"/"Group 6" are generic and several unrelated slides reuse them.
        if 'srgbClr val="008C95"' in x:
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
# One apostrophe glyph across the whole package. The CCAR guide sets the
# typographic ’ and v1d was normalised to it, but the nav is written after the
# per-slide fix-ups and the title/closing never see them — so sweep at the end.
for _name in sorted(os.listdir(f"{WORK}/ppt/slides")):
    if not _name.endswith(".xml"):
        continue
    _p = f"{WORK}/ppt/slides/{_name}"
    _x = open(_p, encoding="utf-8").read()
    _n = re.sub(r"(<a:t[^>]*>)([^<]*)(</a:t>)",
                lambda m: m.group(1) + m.group(2).replace("'", "\u2019") + m.group(3), _x)
    if _n != _x:
        open(_p, "w", encoding="utf-8").write(_n)

add_icon(WORK, built["shofar"], "shofar", ct_path)
print("added the shofar icon to the Shofar Blessing")

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
