# Davis Kabbalat Shabbat — Visual T'filah

`Davis-Kabbalat-Shabbat-VT-v2f.pptx` — **30 slides, the current deck**, built for the
8/21/2026 service from Michelle Gimpelevich's outline (`Kabbalat Shabbat outline
8-21-2026.pdf`). This is the deck the school uses and modifies going forward.

`Davis-Kabbalat-Shabbat-VT-v1d.pptx` — the previous, 14-slide service. Kept because
v2 reuses eight of its slides. Superseded versions live in `Old versions/`.

**v1c descends from Dan's v1a, not from the template.** That is the important
structural fact about this deck. See [Lineage](#lineage) before running any build
script.

**Versioning.** Dan and Claude both edit this deck, so the version number is
shared and always goes up. Never reuse a letter, and never overwrite a version
that already exists on either side. The next build is **v2g**. Check the highest
letter present in both this folder and `~/Documents/Davis Files/Davis VT/` before naming a
new file.

## Service order (v2, 8/21/2026)

The running order **is** the `PLAN` list at the top of `build_v2d.py` — edit that to
change the order or the nav. 29 slides, grouped into six nav sections:

| # | Slide | Section |
|---|-------|---------|
| 1 | Shabbat Shalom! (title) | — |
| 2 | Pledge / HaTikvah | Opening |
| 3 | Hinei Mah Tov | Opening |
| 4 | Living Our Values | Opening |
| 5 | Modeh Ani | Opening |
| 6 | Ozi V'zimrat Yah | Opening |
| 7 | Bar'chu | Sh'ma and Its Blessings |
| 8 | Sh'ma | Sh'ma and Its Blessings |
| 9–11 | V'ahavta (three slides) | Sh'ma and Its Blessings |
| 12 | Mi Chamochah | Sh'ma and Its Blessings |
| 13–14 | Amidah (two slides) | Amidah |
| 15–16 | Mi Shebeirach (two slides) | Amidah |
| 17 | Oseh Shalom | Amidah |
| 18 | Class Song *(placeholder)* | The Blessings of Our Lives |
| 19 | Birthday Blessings | The Blessings of Our Lives |
| 20 | Rock Counting | The Blessings of Our Lives |
| 21 | Candles | Prayers of Welcome |
| 22–24 | Kiddush (three slides) | Prayers of Welcome |
| 25 | Motzi | Prayers of Welcome |
| 26 | Priestly Blessing | Conclusion |
| 27 | Shofar Blessing | Conclusion |
| 28 | Turn the World Around *(placeholder)* | Conclusion |
| 29 | Shabbat Shalom! (closing) | — |

Three placeholder slides need the school's own content: **Class Song** (changes
weekly), the English refrain on both **Mi Shebeirach** slides, and **Turn the
World Around** (Belafonte) — the last two are copyrighted lyrics.

The 14-slide v1d service (Bim Bam, Video, Last Word ×3, Candles, Kiddush ×3,
Hamotzi, Oseh Shalom, Priestly Blessing, Rocks) is the previous deck.

## Lineage

v1 → (Claude's build, delivered as v1a) → **Dan's v1a** → **v1c**

Dan edited the build Claude delivered, so **v1a is ahead of v1b on every slide**,
not just on Rocks. `Old versions/Davis-Kabbalat-Shabbat-VT-v1b.pptx` is the same
build Dan started from; it is kept only as a reference for the progress dots and
the box measurements below.

What Dan changed in v1a, all of it deliberate and all of it kept in v1c:

- **Title slide** swapped to the template's "Shabbat Shalom!" slide, which
  carries the Spotify QR code.
- **Closing slide removed** — the deck ends on Rocks.
- **Last Word slides (4, 6, 10) stripped of prompts.** They are intentionally
  bare: header bar only, no projected text. Micah facilitates from the printed
  outline. Claude's draft prompts are gone for good; do not restore them.
- **Rocks built out** (see below).
- A 152 MB video embedded as its own slide. That one was **not** kept — see
  the v1c changelog.

## Changelog

### v2f — Claude

**Built from Dan's hand-edited v2e, not regenerated** (`finalize_v2f.py`) — Dan
keeps refining the deck by hand, so from here each version is targeted edits on
the latest file, never a fresh generation that would discard his work. New
[`DAVIS-VT-GUIDE.md`](DAVIS-VT-GUIDE.md) collects the accumulated Davis house
rules.

From Dan's v2e notes:

- **Body boxes sized to their content** (were a fixed 9.5" — so tall they
  overlapped the translation and read as stray grouped shapes when clicked),
  autofit still off so PowerPoint can't clip.
- **Service nav moved down** to top-align with the transliteration box, off the
  Hebrew header.
- **Slide 14 split** into *Adonai S'fatai* (the Amidah opening prayer) and
  *Eternity Utters a Day* (the Dan Nichols song); both are their own nav items.
- **V'ahavta cantillation restored** — te'amim from Sefaria (Deut 6:5-9, Num
  15:40-41), Tetragrammaton as יְיָ, matched to the existing rows. David Libre
  renders them cleanly.
- **Mi Shebeirach placeholders** are now real lorem-ipsum text in the
  translation's font/size/color, showing where Friedman's English refrain lands.
- **Crowd logo un-stretched** on the imported slides (20-26): v1d's blip carried
  negative top/bottom `fillRect` insets that stretched it tall once the box was
  square — reset to a flush fill.

Preserved from Dan's v2e: the Living Our Values layout, the sentence-boundary
translation breaks on Modeh Ani / Sh'ma / Mi Chamochah, and the widened slide-10
box that keeps the English rows matched to the Hebrew.

### v2d — Claude

Dan's notes on v2c, and two latent v1d defects surfaced while fixing them:

- **Living Our Values**: centre logo removed, its title lifted into the header bar,
  and the corner logo now the shared crowd mark like every other slide. (The
  chrome-graft was showing the academy text logo because the grafted `Freeform 9`'s
  embed id collided with LOV's own `rId2` — the crowd logo is now added with its
  own rel.)
- **Hebrew headers right-aligned** on every built slide (they were left-aligned).
- **Bar'chu**: `l'olam va-ed` kept on its own line in both columns.
- **Mi Shebeirach** (Friedman) laid out across its two slides — one Hebrew couplet
  each, with a dim placeholder where the copyrighted English refrain goes.
- **Kiddush cup** persists on all three Kiddush slides, in the empty gutter between
  the columns, clearing the text on each.
- **Kiddush 3's missing transliteration line**: v1d's body boxes carry `spAutoFit`,
  so their stored height was the exact content height under LibreOffice's narrower
  substitute fonts — in real PowerPoint the 7th line fell past the box. Body boxes
  now get a generous fixed height with autofit off.
- **Priestly Blessing space** (`Ya'eir Adonai`, `Yisa Adonai`): the space lived at
  a run boundary with no `xml:space="preserve"`, so every renderer dropped it.
  Leading-space stripping now only touches a paragraph's first run, and any run
  with an edge space gets `xml:space="preserve"`.

### v2c — Claude

Three real defects in v2b, all caught by a full 29-slide review rather than spot
checks:

- **The logo was squished.** `Freeform 9`'s path is a square, but v1d renders it
  at 2.29 x 1.36. v2b copied v1d's *dimensions* along with its position; it should
  have taken only the position and kept the square. Now 2.43 x 2.43 in the corner.
- **Two slides silently lost their nav.** Frame detection matched the shape names
  `Group 2`/`Group 6`, which several unrelated slides also use, so V'ahavta 1 and
  Amidah 2 (Dan Nichols' "Eternity Utters a Day") passed the check and had a nav
  dropped over their full-bleed artwork. Detection now keys on the teal column's
  actual fill (`008C95`), and both slides are rebuilt on the frame like the rest.
- **One Oseh Shalom line rendered grey.** It carried a 50%-grey `schemeClr` from
  v1d that the v2b whitening pass skipped because it only handled *missing* fills.
  Now both grey-scheme and no-fill body runs are forced white.

### v2b — Claude

Built by `build_v2b.py`, from Dan's notes on v2. The big change is that **every
content slide now carries the frame and the nav** — v2 skipped nine of them.

- **Eight of the school's older full-bleed prayer slides were rebuilt** on the
  authoring frame at the standard sizes: HaTikvah, Modeh Ani, Ozi V'zimrat Yah,
  Sh'ma, V'ahavta 2 and 3, Amidah 1, Birthday Blessings. They had been drawn at
  whatever size suited each slide — Ozi V'zimrat Yah was 88pt Hebrew against
  60pt transliteration — and ran content to the slide edge with no room for a nav.
- **Living Our Values keeps its design.** It is a composed layout, not a
  two-column prayer, so it is scaled to 87% to clear the nav column and the Davis
  chrome is grafted on, rather than being rebuilt.
- **Opening and closing slides now come from v1d** — blue `001F70`, the Davis
  mark, and the motion-path animation. The closing is a duplicate of the opening.
- **Logo moved to v1d's position** (16.96", 9.66", 2.29 x 1.36) instead of the
  template's higher, larger placement.
- **`Group 6` untangled.** The teal column was a group of the bar (`Freeform 7`)
  and `TextBox 8`, an empty text box of exactly the same size that did nothing but
  travel with it. The empty box is gone.
- **All Hebrew is David Libre** in all four font slots. Setting only `<a:latin>`
  leaves PowerPoint picking a fallback for Hebrew glyphs — the older slides had
  Hebrew in Pinata Marks, Times New Roman and even Helvetica Italics.
- **Leading spaces stripped** from Hebrew lines (Modeh Ani before מלך, Sh'ma
  before יי, and others) — they push the line off the right margin once RTL.
- **Translations bottom-anchored** so the last line sits at the same height
  regardless of how many lines it runs to.
- **Apostrophes** swept to the typographic `’` across the whole package.
- **Shofar icon** from the Jewish Life board library on the Shofar Blessing.

Line breaks re-broken at phrase boundaries on four slides where Hebrew and
transliteration did not correspond — **check these against the melodies**:
Modeh Ani (3 lines against 4), Ozi V'zimrat Yah (3 against 1), V'ahavta 2
(11 against 9), Birthday Blessings (transliteration was only the closing clause).
Sh'ma also gained a translation it never had, and its יְהֹוָה became יְיָ.

### v2 — Claude

The 8/21/2026 service, 29 slides, built by `build_v2.py` from three sources:

- **The template package is the base** — it is already 20" × 11.25" and carries the
  school's own HaTikvah, L.O.V.E., Modeh Ani, Ozi V'zimrat Yah, Sh'ma, V'ahavta,
  Amidah and Shehecheyanu slides.
- **Eight slides imported from v1d** — Candles, Kiddush ×3, Motzi, Oseh Shalom,
  Priestly Blessing, Rock Counting. The template's own copies of these have their
  Hebrew flattened to outlines; v1d's are live text. The packages share a theme and
  an identical `slideLayout7` (bar a stale date placeholder), so they move cleanly.
- **Five prayers built fresh**, since neither deck had them — Hinei Mah Tov,
  Bar'chu, Mi Chamochah, Mi Shebeirach (Hebrew) and the Shofar Blessing. Hebrew
  from the standard liturgy, transliteration per the CCAR guide, matched line for
  line.

**New grouped service nav**, modelled on the CCAR Visual T'filah pattern in
`7.28.17 Kabbalat Shabbat Slides - Sci-Tech.pptx` but moved to the right to match
the Davis frame: `‣` a closed section, `▾` the open one, `•` its items, the current
item in bold white against `B8E3E6`, and the multi-slide progress dots nested
underneath the current item. The old header-bar dot strip is gone — the nav
carries them now. Six sections, using the school's own names where they exist
(Sh'ma and Its Blessings, Prayers of Welcome, The Blessings of Our Lives).

### v1d — Claude

Transliteration brought into line with the **CCAR Press Style Guide**
([PDF](https://ravblog.ccarnet.org/wp-content/uploads/2023/08/CCAR-Press-Style-Guide.pdf)),
via `ccar_normalize.py`. 25 paragraphs rewritten. The rules that bit:

- *"Apostrophe for sh'va nah … No apostrophe for sh'va nach"* — `vachar'ta` →
  `vacharta`, `kidash'ta` → `kidashta`, and `kodshecha` → `kodsh'cha`.
- *"'ei' for tzeirei"* — `zecher` → `zeicher`, `Ya'er` → `Ya'eir`.
- *"Hyphen for two vowels together where necessary … but maariv, Shavuot"* — the
  apostrophe is not the two-vowel separator, so `ha'olam` → `haolam`,
  `ha'aretz` → `haaretz`, `ya'aseh` → `yaaseh`. The guide's word list spells it
  `haolam` outright.
- The word list gives the blessing formula verbatim — **"Baruch atah, Adonai,
  Eloheinu Melech haolam, asher kid'shanu b'mitzvotav v'tzivanu"** — so all four
  openers (Candles, Kiddush 1, Kiddush 2, Motzi) now match it exactly. The line
  break stays between Adonai and Eloheinu.
- Prefixes are lowercase inside the text of a prayer (*"V'zot haTorah asher…"*),
  so the chatimah reads `m'kadeish haShabbat`.

Also:

- **Apostrophes unified on the typographic `’`** (U+2019), which is what the guide
  itself sets and what the deck's English possessives already used. The deck had
  been 21 straight / 19 curly; it is now 34 curly, 0 straight.
- **Comma added** to the Kiddush 2 translation: "Sovereign of the universe **who,**
  finding favor with us, sanctified us with mitzvot."
- Transliteration paragraphs that PowerPoint's spellchecker had shattered into
  one run per word (`err="1"` on every unrecognised word) are collapsed back to a
  single run each. No visual change; it just makes the text editable again.

### v1c — Claude

Built from Dan's v1a with `./derive-v1c.sh`, which reproduces this file exactly.

- **Video slide removed.** Cristy's `2026-2027 WE ARE READY` mp4 was 152 MB of
  the 155 MB file and was a one-time item, so it is out of the archival deck.
  Slide 3 keeps its reusable "Video" placeholder frame — drop a new video in
  there next time. The deck went 155 MB → 3.2 MB.
- **Kiddush 3's Hebrew was truncated, and is repaired.** Dan built Kiddush 2 and
  3 by duplicating a Last Word slide and pasting content in; the Hebrew came
  along as pasted bitmaps rather than text, and the Kiddush 3 bitmap had lost
  `קִדַּשְׁתָּ מִכָּל הָעַמִּים` and its entire final line — 5 Hebrew lines against 7 of
  transliteration. All the Kiddush Hebrew is now live David Libre text, matched
  line for line to Dan's transliteration, with the missing words restored.
- **Sidebar highlight fixed** on Kiddush 2 and 3, which still pointed at
  "Last Word".
- **Progress dots restored** on the three Kiddush slides: `● ○ ○`, `○ ● ○`,
  `○ ○ ●`.

### v1a — Dan

Dan's own version, in iCloud at `~/Documents/Davis Files/Davis VT/`. Not in this repo —
the embedded video makes it 155 MB. See [Lineage](#lineage) for what it changed.

**The Rocks slide**, recorded here so it can be rebuilt if the file is ever lost.
`rocks.pptx` in this folder is a one-slide copy of it, kept as the source of
truth:

- Standard frame: teal header bar, "Rocks" at left, `אֲבָנִים` at right, service
  sidebar with Rocks highlighted, Davis logo bottom right.
- Psalm 90:12 in English, centered near the top in three lines —
  *"Teach us to count our days, / so that we may acquire a wise and loving
  heart." / - Psalm 90:12* — at 1.88", 0.91", 12.44" × 3.21".
- A photograph of **two mason jars, one nearly empty and one full of stones**,
  under a heavy neon/posterize art filter. Centered at 4.23", 3.58",
  7.28" × 5.78". The source is 677 × 538 px, which lands at about 93 DPI on a
  20"-wide slide — adequate but not sharp, so replace it with something larger
  if a higher-resolution original turns up.
- The Hebrew of Psalm 90:12 along the bottom —
  `לִמְנוֹת יָמֵינוּ, כֵּן הוֹדַע וְנָבִא, לְבַב חָכְמָה` — at 2.09", 9.76", 11.56" × 1.14".
  **Live editable text, not outlines.**

### v1b — Claude

The build Dan started from. Superseded; kept for reference.

- **Full Kiddush** across three slides with progress dots.
- Build scripted end to end via `build.sh`.

### v1

- First build from the outline.

## Building

```bash
./derive-v1c.sh "~/Documents/Davis Files/Davis VT/DavisKabbalatShabbatVTv1a.pptx" OUT.pptx
```

This is the path that preserves Dan's work. It unpacks v1a, drops the video
slide, repairs the Kiddush slides, prunes the media those repairs orphaned,
repacks, and validates. Re-running it reproduces `v1c` byte for byte.

Supporting scripts, each usable on its own:

| Script | What it does |
|---|---|
| `fix_kiddush.py UNPACKED/` | The Kiddush repairs, and the record of what they were |
| `prune_rels.py UNPACKED/` | Drops media relationships no shape references, so `clean.py` can collect the files |
| `pack.py UNPACKED/ OUT.pptx [ORIGINAL.pptx]` | Repacks without directory entries — `zip -r` makes PowerPoint offer to repair the deck |
| `ccar_normalize.py UNPACKED/` | The v1d transliteration rewrites, as an auditable old→new table |
| `build_v2.py TEMPLATE.pptx V1D.pptx OUT.pptx` | Builds v2. The `PLAN` list at the top **is** the service order — edit it to change the running order or the nav |

> **`build.sh` and `fill-davis-vt.py` regenerate every content slide from the
> template.** They predate v1a and would discard Dan's title slide, his Kiddush
> text, his bare Last Word slides, and Rocks. Do not run them to make the next
> version. They are kept only for building a *new* deck from the template, and
> if you ever do, splice `rocks.pptx` back in with the pptx skill's
> `add_slide.py` rather than recreating that slide.

## Changes to the template frame — worth folding back into the template

These were needed to make the frame hold real liturgy. Consider making them
permanent in `New VT Template`:

- **Transliteration column widened from 7.05" to 8.5".** At the template width,
  lines like `asher kid'shanu b'mitzvotav` wrapped, which broke the line-for-line
  match with the Hebrew. That match is the thing that lets someone read across
  the two columns without losing their place, so it cannot be left to chance. The
  Hebrew column starts at 9.48", so the widening fits entirely in the empty gutter.
- **Sidebar type reduced from 24pt to 20pt.** At 24pt "Priestly Blessing" split
  across two lines and the nine-item list read as ten.
- **Hebrew and transliteration line spacing set equal, both 57.6pt.** The template
  had 57.6pt on the transliteration and 56.25pt on the Hebrew, which drifts about
  7pt over five lines and visibly de-aligns the columns.

## Box limits, measured

Useful when writing new slides so text does not overflow:

| Box | Width | Size | Fits |
|-----|-------|------|------|
| Transliteration | 8.5" | Calibri 36pt | ~32 characters per line |
| Hebrew | 6.34" | David Libre 45pt | ~20 letters per line |
| Translation | 14.45" | Calibri 28pt | ~73 characters per line, **3 lines max** |
| Sidebar | 2.97" | Calibri Bold 20pt | ~21 characters per line |

The body area holds about ten lines. A fourth translation line runs off the
bottom of the slide, so keep translations to three.

## Still to do

- **Nine slides still use the school's other, full-bleed design** and have no
  right-hand column, so they carry no nav: Pledge/HaTikvah, Living Our Values,
  Modeh Ani, Ozi V'zimrat Yah, Sh'ma, V'ahavta 2 and 3, Amidah 1, and Birthday
  Blessings. `build_v2.py` skips them rather than laying white text over their
  Hebrew, and lists them on every run. Converting them to the Davis frame is the
  main outstanding job.
- **Three placeholder slides** need the school's own content: the Class Song
  (changes weekly), the English refrain of Mi Shebeirach, and Turn the World
  Around. The last two are copyrighted lyrics rather than liturgy.
- **The Shofar Blessing may not belong.** That b'rachah is Rosh HaShanah's; during
  Elul the shofar is customarily sounded without one.
- **Melody line breaks are guesses** on the five freshly built prayers. Michelle
  named the settings (Arian, Seigel, Friedman, Jagoda, Lapidus); the breaks should
  be checked against how each is actually sung.
- **The sidebar lists "Last Word" once though the slide recurs three times.**
  Dan's rule going forward: every instance of a repeating slide gets its own line
  in the side nav. Not worth fixing here — the Last Word structure was a one-time
  thing — but it applies to any repeating slide in future decks.

## Notes

- All Hebrew in the deck is real editable text in David Libre. Some older
  template slides have their Hebrew converted to vector paths; none of those
  were used here, and the two pasted Hebrew bitmaps Dan's v1a carried were
  converted back to text in v1c.
- Transliteration follows the CCAR Press Style Guide throughout as of v1d; see
  that changelog entry for the specific rules and `ccar_normalize.py` for the
  mapping actually applied.
- The title slide uses `TT Berlinerins`. That font has to be installed locally
  or it will reflow.
- The template is **20" × 11.25"**, not 13.333" × 7.5". All geometry in the
  scripts is in those coordinates.

## Verifying before delivery

```bash
python3 "$PPTX_SKILL/scripts/office/validate.py" OUT.pptx --original "~/Documents/Davis Files/Davis VT/DavisKabbalatShabbatVTv1a.pptx"
```

Then render and look at every slide — on a Mac, opening the deck in PowerPoint is
better still, since the real fonts are installed. Check line-for-line
correspondence between the columns, that no translation runs to a fourth line,
that the sidebar highlights the current item, and that the Kiddush progress dots
read `● ○ ○`, `○ ● ○`, `○ ○ ●`.
