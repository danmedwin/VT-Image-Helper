# Davis Kabbalat Shabbat — Visual T'filah

`Davis-Kabbalat-Shabbat-VT-v1c.pptx` — 14 slides, the current deck.
Superseded versions live in `Old versions/`.

**v1c descends from Dan's v1a, not from the template.** That is the important
structural fact about this deck. See [Lineage](#lineage) before running any build
script.

**Versioning.** Dan and Claude both edit this deck, so the version number is
shared and always goes up. Never reuse a letter, and never overwrite a version
that already exists on either side. The next build is **v1d**. Check the highest
letter present in both this folder and `~/Documents/Davis VT/` before naming a
new file.

## Service order

| # | Slide | Leader |
|---|-------|--------|
| 1 | Shabbat Shalom! (title, with Spotify QR) | |
| 2 | Bim Bam | Micah |
| 3 | Video | Cristy |
| 4 | Last Word | Micah facilitates |
| 5 | Candle Blessing | Amy lights |
| 6 | Last Word | Micah facilitates |
| 7–9 | Kiddush (full text, three slides) | Dan Medwin |
| 10 | Last Word | Micah facilitates |
| 11 | Hamotzi | Micah |
| 12 | Oseh Shalom | Micah |
| 13 | Priestly Blessing | Micah, Javier, Michelle, Emilie |
| 14 | Rocks | Micah |

The deck ends on Rocks. There is no closing slide — the title slide already
carries the "learn our Shabbat prayers and songs" QR code that the old closing
slide duplicated.

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

Dan's own version, in iCloud at `~/Documents/Davis VT/`. Not in this repo —
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
./derive-v1c.sh "~/Documents/Davis VT/DavisKabbalatShabbatVTv1a.pptx" OUT.pptx
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

- **Kiddush transliteration is inconsistent between slide 7 and slides 8–9.**
  Dan's slides 8–9 came from another source and use `Eloheinu, Melech haolam`,
  `zecher`, `vachar'ta`, `kodshecha` and curly apostrophes, where slide 7 uses
  `Eloheinu Melech ha'olam`, `zeicher`, `vacharta`, `kodsh'cha` and straight ones.
  Both readings are defensible; they just should not sit in one prayer. Dan's
  call which convention wins.
- **Slide 8's translation reads "Sovereign of the universe who finding favor
  with us, sanctified us with mitzvot."** A comma after "who" fixes it. Left
  alone because it is the school's wording, not Claude's.
- **Video (slide 3)** has an open content area by design. Drop the next video in.

## Notes

- All Hebrew in the deck is real editable text in David Libre. Some older
  template slides have their Hebrew converted to vector paths; none of those
  were used here, and the two pasted Hebrew bitmaps Dan's v1a carried were
  converted back to text in v1c.
- Transliteration follows Mishkan T'filah / CCAR conventions, except on the
  two Kiddush slides noted above.
- The title slide uses `TT Berlinerins`. That font has to be installed locally
  or it will reflow.
- The template is **20" × 11.25"**, not 13.333" × 7.5". All geometry in the
  scripts is in those coordinates.

## Verifying before delivery

```bash
python3 "$PPTX_SKILL/scripts/office/validate.py" OUT.pptx --original "~/Documents/Davis VT/DavisKabbalatShabbatVTv1a.pptx"
```

Then render and look at every slide — on a Mac, opening the deck in PowerPoint is
better still, since the real fonts are installed. Check line-for-line
correspondence between the columns, that no translation runs to a fourth line,
that the sidebar highlights the current item, and that the Kiddush progress dots
read `● ○ ○`, `○ ● ○`, `○ ○ ●`.
