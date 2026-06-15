# VT Image Helper — Changelog

---

## v2.74 — June 2026
- Photo fetching now paginates (up to 5 pages × 15) until 8 non-blocked, non-holiday results are found — grids stay full regardless of how many photos are blocked
- EmailJS report emails fixed: photo thumbnail and Pexels link now passed as pre-built HTML strings; removes invalid `{{#if}}` syntax that caused "corrupted variables" error
- Unrecognized prayers silently submitted to Firebase (and admin emailed) when user saves search terms — no visible submit button

---

## v2.72 — June 2026
- EmailJS admin notifications: prayer submissions and image flags now send an email with action buttons
- Approve/Dismiss links for prayer submissions; Block image/Dismiss links for reports
- Clicking an action link opens the app, prompts admin login if needed, then executes automatically

---

## v2.71 — June 2026
Quick-start links (Friday evening · Shabbat morning · Weekday morning · Weekday evening) moved from the "Add prayers" input box to the top of the Prayer library box, just below the header.

---

## v2.59 — June 2026
- "Find images for your service" h2 + explainer paragraph moved into their own full-width rounded box
- Input box reordered: textarea + Add to list button appear first, quick-start links below
- All `svc-section-box` elements now have a white background + subtle shadow, so they read as cards against the light blue-gray page background

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
