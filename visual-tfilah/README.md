# Davis Kabbalat Shabbat — Visual T'filah

`Davis-Kabbalat-Shabbat-VT-v1a.pptx` — 15 slides, built on the Davis VT template
(`New VT Template (in progress w Claude).pptx`), following the printed service outline.
Superseded versions live in `Old versions/`.

## Service order

| # | Slide | Leader |
|---|-------|--------|
| 1 | Title (Davis template slide) | |
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
| 15 | Shabbat Shalom (Davis template slide) | |

## Changelog

### v1a
- **Full Kiddush** replaces the short blessing over wine, running across three
  slides with `● ○ ○` progress dots: wine blessing, then *asher kid'shanu…
  zeicher litziat Mitzrayim*, then *Ki vanu vacharta…* closing with the chatimah
  *m'kadeish haShabbat*.
- **Progress dots** added for prayers spanning several slides. They sit in the
  header bar between the English title (which ends at 6.86") and the Hebrew title
  (which starts at 13.07"), so they cannot collide with either.
- Kiddush 2 of 3 translation condensed to three lines. See the box limits below.
- Build is now scripted end to end: `./build.sh TEMPLATE.pptx [OUT.pptx]`.

### v1
- First build from the outline.

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

- **Last Word prompts (slides 4, 6, 10) are drafts.** The prompts on the back of
  the printed outline were not legible in the photo. Replace with the real ones.
- **Video (slide 3)** and **Rocks (slide 14)** have open content areas by design.
  Drop the video and the rocks content in.

## Rebuilding

```
./build.sh "New VT Template (in progress w Claude).pptx" Davis-Kabbalat-Shabbat-VT-v1b.pptx
```

`build.sh` does the structural work: duplicate the template's authoring slide
(slide 5 of the template, the two-column one with the service sidebar) once per
content slide, set the running order, drop everything else, and repack. Then
`fill-davis-vt.py` pours in the liturgy, transliteration, translations, sidebar
highlighting, progress dots, and speaker notes.

Edit the text in `fill-davis-vt.py` and re-run rather than hand-editing the deck,
so the Hebrew and transliteration line breaks stay in sync.

## Notes

- Hebrew is real editable text in David Libre, not outlines. Some older template
  slides have their Hebrew converted to vector paths; none of those were used here.
- Transliteration follows Mishkan T'filah / CCAR conventions.
- The title and closing slides use `TT Berlinerins`. That font has to be installed
  locally or those two slides will reflow.
