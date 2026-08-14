# Davis Kabbalat Shabbat — Visual T'filah

`Davis-Kabbalat-Shabbat-VT-v1.pptx` — 13 slides, built on the Davis VT template
(`New VT Template (in progress w Claude).pptx`), following the printed service outline.

## Service order

| # | Slide | Leader |
|---|-------|--------|
| 1 | Title (Davis template slide) | |
| 2 | Bim Bam | Micah |
| 3 | Video | Cristy |
| 4 | Last Word | Micah facilitates |
| 5 | Candle Blessing | Amy lights |
| 6 | Last Word | Micah facilitates |
| 7 | Kiddush | Dan Medwin |
| 8 | Last Word | Micah facilitates |
| 9 | Hamotzi | Micah |
| 10 | Oseh Shalom | Micah |
| 11 | Priestly Blessing | Micah, Javier, Michelle, Emilie |
| 12 | Rocks | Micah |
| 13 | Shabbat Shalom (Davis template slide) | |

## Still to do

- **Last Word prompts (slides 4, 6, 8) are drafts.** The prompts on the back of the
  printed outline were not legible in the photo. Replace with the real ones.
- **Video (slide 3)** and **Rocks (slide 12)** have open content areas by design.
  Drop the video and the rocks content in.

## How it was built

The template's authoring slide (slide 5 of the template: two-column Hebrew and
transliteration, service-order sidebar, translation bar) was duplicated once per
content slide, reordered, and filled in. The Davis title and closing slides were
carried over untouched.

```
unzip template -> add_slide.py x10 (clone the authoring slide)
              -> rewrite <p:sldIdLst> to the service order
              -> clean.py -> rezip as working.pptx
              -> fill-davis-vt.py -> Davis-Kabbalat-Shabbat-VT-v1.pptx
```

`fill-davis-vt.py` holds all the liturgy, transliteration, translations, and
speaker notes. It expects `working.pptx` (the ordered, still-unfilled deck) in the
same directory. Edit the text there and re-run rather than hand-editing the deck,
so line breaks stay in sync.

## Two deliberate changes to the template frame

- **Transliteration column widened** from 7.05" to 8.5". At the template width
  several transliteration lines wrapped, which broke the line-for-line match with
  the Hebrew. The Hebrew column starts at 9.48", so the gutter absorbs it.
- **Sidebar type reduced** from 24pt to 20pt so "Priestly Blessing" fits on one line.

Hebrew and transliteration share a 57.6pt line spacing so corresponding lines sit
on the same baseline across both columns.

## Notes

- Hebrew is real editable text in David Libre, not outlines. Some older template
  slides have their Hebrew converted to vector paths; none of those were used here.
- Transliteration follows Mishkan T'filah / CCAR conventions.
- The title and closing slides use `TT Berlinerins`. That font has to be installed
  locally or those two slides will reflow.
