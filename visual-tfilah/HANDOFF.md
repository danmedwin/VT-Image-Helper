# Handoff — Davis Kabbalat Shabbat VT

Current state of the deck, for whoever (Dan or a future Claude session) picks it
up next. Read this, then [`DAVIS-VT-GUIDE.md`](DAVIS-VT-GUIDE.md) for the house
rules and [`README.md`](README.md) for the full version history.

## Where things are

| What | Where |
|---|---|
| **Current deck** | `~/Documents/Davis Files/Davis VT/DavisKabbalatShabbatVTv3.pptx` |
| Superseded versions | `~/Documents/Davis Files/Davis VT/Old versions/` |
| Repo (scripts, docs, deck copies) | `danmedwin/VT-Image-Helper`, branch `claude/visual-tfilah-davis-leaqqy`, folder `visual-tfilah/` |
| Icon library | `~/Documents/Davis Files/Jewish Life Board/icons-renamed/` (flat, named by subject) |
| Centered-format template | `centered-format-template.pptx` (repo + Davis VT folder) |
| The school's service outline | `Kabbalat Shabbat outline 8-21-2026.pdf` (from Michelle Gimpelevich) |

## The one rule that matters most

**Build every new version from the LATEST hand-edited file — never regenerate
from a script.** Dan edits the deck by hand between rounds (layout, line breaks,
icons, the centered format). Regenerating from `build_*.py` silently discards his
work — this already bit once (v1a) and is why v1c had to be reverse-derived. From
v2e on, each version is *targeted edits* applied to the current file
(`finalize_v2f.py`, `build_v2i.py`, etc. are examples of that pattern), then
shipped as the next letter. Check the highest version present in **both** the
Davis VT folder and the repo before naming a new file.

## State of v3

- **30 slides**, the 8/21/2026 service. Order and sections are in `README.md`.
- **Hand-drawn icons throughout** (LemonadePixel), placed by Dan.
- **Two layouts** now in use (see `DAVIS-VT-GUIDE.md` → *Two layouts*):
  - **Standard two-column** for most prayers.
  - **Centered** for short (~2-line) prayers — Hebrew centred on top,
    transliteration centred below, icon centred, translation centred at the
    bottom. `centered-format-template.pptx` is the reusable worked example
    (Bar'chu); duplicate it and swap the text. Currently used on Hinei Mah Tov,
    Bar'chu, Sh'ma, and Adonai S'fatai.

## Still open

- **Priestly Blessing** wants a split-finger kohanim hand. No such icon exists in
  any LemonadePixel pack we have, or in the old decks — Dan to photoshop one or
  source it elsewhere; then place it (the hamsa is there as a stand-in).
- **Hinei Mah Tov** could use a people/community icon; neither the base packs nor
  the Activity & Recreation / Travel packs have one.
- **Placeholder slides** need the school's own content: Class Song (weekly), the
  Mi Shebeirach English refrain, and Turn the World Around (both copyrighted).
- **Shofar Blessing** — confirm whether to keep the b'rachah (it's Rosh
  HaShanah's; Elul shofar is customarily sounded without one).
- **Melody line breaks** on the freshly-built song slides are best-effort; worth
  a pass with Michelle.

## Verifying before delivery

```bash
python3 "$PPTX_SKILL/scripts/office/validate.py" OUT.pptx --original IN.pptx
```

Then render every changed slide and look — on a Mac, opening in PowerPoint is
best (real fonts). **LibreOffice QA can miss what PowerPoint clips** (its
substitute fonts are narrower), so trust Dan's on-screen reports over the QA
render. Check the columns register line-for-line, no translation runs off the
bottom, the nav highlights the current item, and any Hebrew reads correctly
(RTL, nikud, and — on the V'ahavta — the cantillation).
