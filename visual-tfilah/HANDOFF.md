# Handoff — Davis Kabbalat Shabbat VT

> **CLOSED — this handoff is complete, and parts of it are wrong.** v1c is built.
> Read `README.md` instead. Two things below turned out not to hold: the Rocks
> slide is **slide 15** of v1a, not 14; and Rocks was **not** the only thing
> that had diverged — v1a is ahead of v1b on the title slide, the closing slide,
> the Last Word slides, and the Kiddush, so v1c was derived from v1a rather than
> regenerated from the template. Kept for the record.

For a **local** Claude Code session on Dan's Mac. The work so far was done in a
cloud session, which cannot reach iCloud. Everything below is current as of
commit `1b1d212` on branch `claude/visual-tfilah-davis-leaqqy`.

## Why this handoff exists

The deck needs Dan's Rocks slide, which lives only in his `v1a`. That file has a
video embedded, so it is too large to upload into a chat, and a cloud session has
no filesystem access to iCloud. A local session can open it directly.

## Start here

```bash
cd <VT-Image-Helper checkout>
git fetch origin claude/visual-tfilah-davis-leaqqy
git checkout claude/visual-tfilah-davis-leaqqy
cd visual-tfilah
```

Read `README.md` first. It has the service order, the changelog, the measured box
limits, and the frame changes. This file only covers what the cloud session
could not finish.

Invoke the **visual-tfilah** skill (rules for VT decks) and the **pptx** skill
(deck mechanics) before editing anything.

## Where the files are

| What | Where |
|---|---|
| Davis VT template | `~/Documents/Davis VT/New VT Template (in progress w Claude).pptx` |
| Dan's v1a (has the Rocks slide + embedded video) | `~/Documents/Davis VT/` |
| Current Claude build, v1b | `visual-tfilah/Davis-Kabbalat-Shabbat-VT-v1b.pptx` in this repo |
| Superseded versions | `visual-tfilah/Old versions/` |

If `~/Documents` is not the iCloud folder on this machine, try
`~/Library/Mobile Documents/com~apple~CloudDocs/Documents/Davis VT/`.

## Versioning — read before naming any file

Dan and Claude both edit this deck, so the version number is shared and always
goes up. Never reuse a letter. Never overwrite a version that exists on either
side. v1 and v1b are Claude's, v1a is Dan's. **The next build is v1c**, and
`build.sh` already defaults to that name. Check the highest letter present in
both the repo and `~/Documents/Davis VT/` before naming a new file.

## The job: build v1c

**The one blocking task is Dan's Rocks slide.**

`build.sh` regenerates all 13 content slides from the template every run, so a
plain re-run would wipe the Rocks slide. v1c has to import Dan's slide instead of
regenerating it.

1. Open Dan's v1a, find the Rocks slide, and inspect it: background, imagery,
   text, and whether its Hebrew is live text or vector outlines. Several older
   slides in the Davis template have their Hebrew flattened to paths.
2. Record that description in `README.md` under the v1a changelog entry, so the
   slide can be rebuilt if the file is ever lost. This was explicitly asked for.
3. Carry the slide into v1c. Copy it in rather than recreating it. The pptx
   skill's `add_slide.py` handles the package bookkeeping; a hand-copied slide
   file will not register correctly.
4. Make it survive future rebuilds — either teach `build.sh` to splice the slide
   in after `fill-davis-vt.py` runs, or keep a one-slide `rocks.pptx` alongside
   the scripts as the source of truth. Otherwise every future rebuild loses it
   again, which is the exact trap this handoff is meant to close.

Watch the embedded video: it is why v1a is large. Only the Rocks slide is needed,
so do not drag the video along unless Rocks itself contains it.

## Also open

- **Last Word prompts (slides 4, 6, 10) are drafts.** The real prompts are on the
  back of the printed outline. The photo showed them only as bleed-through and
  they were not legible, so plausible stand-ins were written instead. They need
  replacing with the real text. Ask Dan for the sheet.
- **Video (slide 3)** is an intentionally open content area. Cristy's video drops
  in there.

## How the build works

```bash
./build.sh "~/Documents/Davis VT/New VT Template (in progress w Claude).pptx" \
           Davis-Kabbalat-Shabbat-VT-v1c.pptx
```

`build.sh` does the structural work: it duplicates the template's authoring slide
(**slide 5** of the template, the two-column one with the service sidebar) once
per content slide, sets the running order, drops the other 45 template slides,
and repacks. Then `fill-davis-vt.py` pours in the liturgy, transliteration,
translations, sidebar highlighting, progress dots, and speaker notes.

Edit text in `fill-davis-vt.py` and re-run. Do not hand-edit the deck, or the
Hebrew and transliteration line breaks drift out of sync.

## Things that will bite

- **The template is 20" × 11.25"**, not 13.333" × 7.5". All geometry in the
  scripts is in those coordinates.
- **Use template slide 5, not slides 36–40.** Slides 36–40 already contain
  Candles, Kiddush, Hamotzi, and the Priestly Blessing, but they came from a
  Keynote or PDF import and their Hebrew is vector outlines, not text. Slide 5 is
  the new authoring template with real editable Hebrew in David Libre.
- **Translations are capped at three lines** (~73 characters each). A fourth runs
  off the bottom of the slide. This already bit once, on Kiddush 2 of 3.
- **Transliteration and Hebrew must break line for line.** That correspondence is
  what lets someone read across the two columns. It is why the transliteration
  column was widened to 8.5" and why both columns share 57.6pt line spacing.
- **`TT Berlinerins`** is used on the title and closing slides. It must be
  installed locally or those two slides reflow. This is also why they looked
  broken in the cloud session's renders; they are fine on Dan's Mac.
- **The repo's root `CLAUDE.md` is about the VT Image Helper web app**, not this
  deck. Its rules about bumping `v{major}.{minor}` in `index.html` and updating
  `feedback_vt_version.md` do **not** apply to this work. Do not bump `index.html`
  for deck changes.

## Verifying before delivery

```bash
python3 /path/to/pptx/scripts/office/validate.py OUT.pptx --original TEMPLATE.pptx
soffice --headless --convert-to pdf OUT.pptx && pdftoppm -jpeg -r 60 OUT.pdf slide
```

Then look at every slide image. On a Mac, opening the deck in PowerPoint is
better still, since the real fonts are installed. Check line-for-line
correspondence between the columns, that no translation runs to a fourth line,
that the sidebar highlights the current item, and that the Kiddush progress dots
read `● ○ ○`, `○ ● ○`, `○ ○ ●`.
