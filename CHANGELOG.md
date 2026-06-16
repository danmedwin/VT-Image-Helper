# VT Image Helper — Changelog

---

## v2.96 — June 2026
- Fix captions and photographer attribution not appearing in Safari (or any browser without API keys and no local curated library): removed isLive gating from photoCardHtml so captions always render when photo.caption or photo.photographer is present; also fixes favorites view showing images only with no caption/attribution

## v2.95 — June 2026
- Prayers & Terms tab: theme text column added to each prayer row (between tag and search terms); Save button writes both search terms and theme to Firebase; saveAsDefault/resetToDefault include themes; loadCustomThemes() applies Firebase overrides at startup

## v2.94 — June 2026
- Per-prayer "★ Favorites (N)" button in each section header (disabled when N=0); toggles grid to show only favorited photos for that prayer
- approveSuggestion now writes the full photo object to Firebase pinnedPhotos/{prayer} so approved suggestions appear immediately in the favorites view
- pinnedPhotos loaded at startup and merged into curated photo sets for each prayer

## v2.93 — June 2026
- Suggestion emails now include Approve and Dismiss action buttons; Approve sets the photo as a favorite for the suggested prayer in Firebase and cleans up the suggestion entry; Dismiss just deletes it

## v2.92 — June 2026
- Block and report modals: circled × button in top-right corner to close; Esc key also closes whichever is open (lightbox and admin login already had both)

## v2.91 — June 2026
- Report modal: Cancel/Report buttons moved to directly below notes textarea; "Fits another prayer?" wrapped in a rounded rectangle instead of a divider line

## v2.90 — June 2026
- Report modal now includes a "Fits another prayer?" section: prayer dropdown + green Suggest button
- Suggestion saves to Firebase and emails admin without closing the modal, so users can report and suggest independently

## v2.89 — June 2026
- Full cross-section keyboard navigation: ArrowDown lands on same column in next section's top row; ArrowUp lands on same column in previous section's bottom row; ArrowRight from last card wraps to first card of next section; ArrowLeft from first card wraps to last card of previous section

## v2.88 — June 2026
- ArrowDown on the bottom row of a prayer section now jumps to the first card of the next section
- Space closes the lightbox when it is open (in addition to Esc)

---

## v2.82 — June 2026
- Unsplash added as a second photo source alongside Pexels
- Admin API Keys tab now has separate Pexels and Unsplash sections
- When both keys are set, 4 photos are fetched from each in parallel and interleaved
- Works with either key alone (8 photos from that source) or both together
- Per-prayer Refresh and library Refresh both use both sources
- Photo cards link to the correct source (Pexels or Unsplash); attribution text updates dynamically
- Report email uses a generic "View photo" link that works for either source

---

## v2.81 — June 2026
- Refresh library now paginates (up to 5 pages × 15) until 8 non-blocked photos are collected per prayer — fixes Review tab showing fewer than 8 photos for prayers with many blocked images

---

## v2.80 — June 2026
- Filters tab auto-seeds Firebase with default lists on first admin open — all filter data is now Firebase-backed from day one, no manual edit required to initialize

---

## v2.79 — June 2026
- Filters tab reordered: Excluded keywords → Excluded visuals → Jewish holidays
- Renamed "Always excluded" → "Excluded keywords"; "Visual blocklist" → "Excluded visuals"

---

## v2.78 — June 2026
- Merged Blocklist tab into Filters tab — Visual blocklist now appears as a third section below Always excluded and Jewish holidays

---

## v2.77 — June 2026
- New **Filters** admin tab with two editable sections:
  - **Always excluded** (teal chips): keywords that remove a photo regardless of search terms — non-Jewish holidays, etc.
  - **Jewish holidays** (purple, expandable groups): each group holds spelling variants; photos excluded unless that holiday is in the prayer's search terms
- Both lists saved to Firebase `/filters` and loaded on page load; fall back to built-in defaults

---

## v2.76 — June 2026
- Non-Jewish holidays (Christmas, Easter, Ramadan, Diwali, Halloween, Kwanzaa, etc.) always filtered from photo results — applies in live search, per-prayer refresh, and admin review

---

## v2.75 — June 2026
- Sim Shalom added to prayer library (morning tag, peaceful sunrise search terms)
- Sim Shalom added to Weekday morning preset after Oseh Shalom
- Sim Shalom added to Shabbat morning preset after Kedushah
- Sim Shalom added to canonical MT order

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
