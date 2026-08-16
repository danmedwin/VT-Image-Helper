# Davis Academy VT — house rules

Davis-specific decisions for the Kabbalat Shabbat deck. The generic
[`visual-tfilah`](https://…) skill governs universal VT typography and layout;
**this file holds what is specific to Davis** — the frame, the nav, the sources,
and the accumulated per-slide rulings. Read both before editing the deck.

Keep this current: when Dan rules on something, record it here.

## The frame

- Slide size **20" × 11.25"** (not 13.333" × 7.5").
- **Teal header bar** across the top: English prayer title at the left
  (`TextBox 15`, Calibri Bold ~32pt white), Hebrew title at the right
  (`TextBox 12`, David Libre ~42pt white, **right-aligned** — Hebrew is always
  right-aligned; a header is never the centered exception).
- **Right-hand teal nav column** (`Group 6`), full height.
- **Crowd logo** (Davis mark) bottom-right of the content area, **square
  2.43" × 2.43"** — never stretched. It is filled from `image8.png`; keep the
  blip's `<a:fillRect/>` with no insets, or the figures stretch tall.
- Body: transliteration/English left (`TextBox 10`), Hebrew right
  (`TextBox 11`), translation along the bottom (`TextBox 18`).

## Type

- Hebrew **David Libre 45**, transliteration **Calibri 36**, translation
  **Calibri 28** — consistent across every slide. Set David Libre in all four
  font slots (`latin`, `ea`, `cs`, `sym`) on Hebrew runs, or PowerPoint falls
  back for the Hebrew glyphs.
- Body line spacing **57.6pt** on both columns, so the rows register across.
- **Body text boxes are sized to their content** — a couple tenths of margin
  below the last line, no more. Do NOT leave them 9"+ tall; an oversized box
  overlaps the translation and reads as a stray/grouped shape when clicked.
- Body boxes use a **fixed height with autofit off**, not `spAutoFit` — an
  autofit box stores the height LibreOffice computed with its narrower
  substitute fonts, and real PowerPoint then clips the last line (this ate
  Kiddush 3's 7th line once).

## Two layouts

**Standard (two-column)** — the default. Transliteration/English left
(`TextBox 10`), Hebrew right (`TextBox 11`), translation along the bottom
(`TextBox 18`), icon in the open zone below. Use for anything more than ~2 lines.

**Centered (short prayers)** — for prayers of about two lines, a centered
vertical stack instead of two columns. `centered-format-template.pptx` (in the
repo and the Davis VT folder) is the worked example (Bar'chu); duplicate it and
replace the text. In v3, Hinei Mah Tov, Bar'chu, Sh'ma and Adonai S'fatai use it.

The stack, all centered on the content-area midline (x ≈ 8.8", left of the nav):

| Element | Box | Position (x, y, w, h ") | Align | Size |
|---|---|---|---|---|
| Hebrew (top) | `TextBox 11` | 5.18, 1.78, 7.23, 2.15 | centre, RTL | David Libre 45 |
| Transliteration | `TextBox 10` | 4.49, 3.94, 8.58, 1.98 | centre | Calibri 36 |
| Icon | — | centred ≈ 7.7, 6.8, ~2.2 sq | — | — |
| Translation (bottom) | `TextBox 18` | 0.64, 10.21, 15.24, 0.8 | centre, bottom-anchored | Calibri 28 |

Header boxes (`TextBox 12` Hebrew right, `TextBox 15` English left) and the nav
are unchanged from the standard frame. Same 57.6pt line spacing; Hebrew still
sits **above** its transliteration. On the Sh'ma the arched Sh'ma artwork takes
the top slot in place of a separate icon.

## The service nav

Modeled on the CCAR Visual T'filah pattern (see `7.28.17 Kabbalat Shabbat
Slides - Sci-Tech.pptx`), but on the **right** to match the Davis frame:

- `‣` a closed section, `▾` the open one, `•` its items.
- Current item **bold white**; everything else the resting ice-blue `B8E3E6`.
- A multi-slide item gets **progress dots nested under it** (`● ○`, `○ ●`, …).
- **Top-aligned with the body text** (same y as the transliteration box), not
  tucked up against the Hebrew header.
- **Every instance of a repeating slide gets its own nav line.** (One-time
  structures like the old "Last Word" were the exception, and are gone.)
- Section names, from the school's own template: **Opening · Sh'ma and Its
  Blessings · Amidah · The Blessings of Our Lives · Prayers of Welcome ·
  Conclusion.**

## Text

- **Transliteration** follows the **CCAR Press Style Guide**. Its word list
  carries the blessing formula verbatim — *"Baruch atah, Adonai, Eloheinu Melech
  haolam, asher kid'shanu b'mitzvotav v'tzivanu."* Apostrophe marks sh'va na
  only; it is **not** the two-vowel separator, so `haolam`, `haaretz`, `haamim`
  have none. `"ei"` for tzeirei (`zeicher`, `Ya'eir`). One typographic
  apostrophe `’` throughout.
- **Divine Name**: two-yud **יְיָ**, not the spelled-out יְהֹוָה, per Reform
  practice.
- **Translations break at sentence boundaries** when they run to more than one
  line — each sentence starts a fresh line rather than wrapping mid-thought
  (e.g. Modeh Ani breaks after *"…soul to me."* before *"How great…"*). Within a
  line the text still wraps naturally.
- **A wider transliteration/English box is a fine fix** for keeping the left
  rows matched to the Hebrew rows, as long as the text does not start to overlap
  the Hebrew column.
- **Cantillation (trop)** on the V'ahavta is kept — David Libre renders te'amim
  correctly. Source the pointed text from Sefaria (Torah with te'amim), then
  substitute יְיָ for the Tetragrammaton.

## Icons

- Library: `~/Documents/Davis Files/Jewish Life Board/icons-renamed/` — 188
  LemonadePixel PNGs renamed to what they depict, flat at the top level.
- **Placement**: in the open zone below the body text and above the bottom
  translation, centred near x≈7.5", ~2–3.5" tall — where Candles / Hamotzi /
  Shofar / Kiddush-cup already sit. On slides where one column is empty (e.g. the
  Amidah page-directions), the icon can go in that empty column instead.
- **Recolour art for the dark background.** Graphics built for a light ground
  (e.g. the blue arched Sh'ma from the old template) wash out on the dark-blue
  slide — threshold the alpha and fill the glyphs solid white so they read.
- More packs are on the LemonadePixel Etsy shop; buy → drop PNGs into the library.

## Sources

- Service outlines come from **Michelle Gimpelevich** (Lower School teacher),
  who names the musical setting per prayer (Arian, Seigel, Friedman, Jagoda,
  Lapidus). Confirm melodies/phrasing with her — sung line breaks can't be
  derived from the text.
- **Icons** come from the Jewish Life board library (LemonadePixel) at
  `~/Documents/Davis Files/Jewish Life Board/icons/`.
- **Copyrighted song lyrics** (Belafonte's *Turn the World Around*, Friedman's
  *Mi Shebeirach* English refrain) are never reproduced — placeholder only; the
  school pastes in its own slides.

## Open per-slide rulings

- **Shofar Blessing**: that b'rachah is Rosh HaShanah's; during Elul the shofar
  is customarily sounded **without** a blessing. Confirm with Dan before use.
- **Kiddush cup** persists on all three Kiddush slides, in the empty gutter
  between the columns.
- **Mi Chamochah** is the **Friedman** setting, not the "Don't Worry Be Happy"
  parody that was in the old template.

## Lineage & build

Dan and Claude both edit this deck by hand, so **each new version builds on the
latest hand-edited file, never regenerated from scratch** — regenerating
silently discards Dan's edits (the v1a lesson). `build_v2*.py` scripts generated
the earlier drafts; from v2e on, changes are applied as targeted edits to the
current file. See `README.md` for the version history.
