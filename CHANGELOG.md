# VT Image Helper — Changelog

---

## v2.46 — June 2026
**40/60 service builder redesign**

- New two-column layout for the setup panel: left 40% = "Your service," right 60% = "Prayer library" + Keywords
- **Your service (left):** ordered list of selected prayers with drag-to-reorder (≡ handle), pencil icon to expand and edit per-prayer search terms inline, × to remove
- **Quick-start presets:** Friday evening · Shabbat morning · Weekday morning — one click populates the service list. Clear all link also added.
- **Prayer library (right):** chips are now buttons (replaced checkbox + `:has()` pattern with `.chip-selected` class). Selected prayers show as highlighted; clicking toggles them in/out of the service list.
- Keywords section moved into the right column below the prayer library
- `findImages()` now reads from `_serviceOrder` array (ordered) instead of checked checkboxes

---

## v2.45 — June 2026
Added helper text under "Select prayers" label: "Select from saved prayers below, and/or add additional prayers in the text box."

---

## v2.44 — June 2026
Fixed 4 prayer ID spellings: `ahavatoolam→ahavatolam`, `einkelo→einkeloheinu`, `yotzeior→yotzeror`, `oseishalom→osehshalom` (in HTML source and refresh-curated.js).

---

## v2.43 — June 2026
Renamed prayer ID `modehanee → modehani` (spelling fix).

---

## v2.42 — June 2026
- Lightbox / full-screen view: expand button on each card, ←→ navigation, Esc/Enter keyboard shortcuts, Select and Favorite from within lightbox
- ZIP download: "Download ZIP" button using JSZip (CDN), parallel fetch, staggered fallback

---

_Earlier version history in `~/.claude/projects/-Users-medwin/memory/feedback_vt_version.md`_
