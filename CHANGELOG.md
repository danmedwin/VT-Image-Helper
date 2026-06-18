# VT Image Helper — Changelog

---

## v3.11 — June 2026
- Quick-start row: surface background + border + rounded rect to visually distinguish from prayer chips
- Service list explainer: added pencil icon hint ("Click the ✎ icon to edit a prayer's default search terms")

## v3.10 — June 2026
- Removing a search term chip auto-refreshes results (400ms debounce, live API keys only)

## v3.09 — June 2026
- Add SVG favicon: dark indigo background, gold "VT" monogram

## v3.08 — June 2026
- Fix invisible Reports sub-tab active state and Reverse button: define missing `--accent` CSS variable
- Remove 3 dead CSS classes: `.setup-hr`, `.setup-two-col`, `.field-row` (defined but never used in HTML)
- Replace 8+ hardcoded old-palette hex colors with CSS variables (`--teal-light`, `--gold-light`, `--gold-dark`, `--teal`)
- Add `fbPut()` and `fbDel()` Firebase helper functions; replace ~48 raw fetch boilerplate blocks with helpers (~100 lines removed)

## v3.07 — June 2026
- Email action links (Approve/Dismiss) now skip the login modal if you've previously logged in — a stored refresh token silently exchanges for a fresh session and executes the action directly

## v3.06 — June 2026
- Header: title changed to "VT Image Helper" with dark text and no shadow; "Visual T'filah" eyebrow removed
- Explainer: removed "Click ♡ to save favorites across sessions" from the setup panel intro
- Frosted glass panel opacity reduced slightly (0.94 → 0.88)

## v3.05 — June 2026
- Frosted Sanctuary visual redesign (CSS-only re-skin)
- New design tokens: updated navy/gold/teal palette, new page-bg, footer-bg, fav-heart, radius-card, radius-chip variables
- Figtree font (Google Fonts) replaces system-ui stack
- Header restructured: hero wordmark with eyebrow + large title sits above frosted glass setup panel; header is now a full-bleed photo with darker gradient overlay
- Setup panel: frosted glass card (blur, white/translucent bg, rounded 22px, deep shadow) nested inside the header
- Find/Add buttons: "Find images" is navy-mid with stronger shadow; "Add to list" is gold
- Prayer chips, filter chips, search-term chips all use radius-chip (30px pill shape)
- Prayer theme text changed from teal to gold
- Prayer header uses a subtle lavender gradient instead of flat navy-light
- Image cards use radius-card (11px) and hover with lavender border instead of navy
- Favorites button: gold tint (instead of teal) when active; heart color updated to #e0566a
- Footer: full-width, footer-bg color, no max-width constraint
- Admin header: indigo gradient instead of flat navy
- Version bumped to v3.05

## v3.04 — June 2026
- Replace all hardcoded stub photos in PRAYERS array with full curated.json photo objects (src, caption, photographer, sourceUrl, source) — the page now shows real photos immediately, before Firebase or curated.json loads
- Update 22 prayers' hardcoded searchTerms to match current Firebase defaults saved via the admin panel

## v3.03 — June 2026
- Switch header/Beta row to 60/40 ratio (was 40/60)

## v3.02 — June 2026
- Separate header and Beta box into two independent cards in a 40/60 grid matching the lower column layout

## v3.01 — June 2026
- Add Beta notice panel on the right side of the "Find images for your service" header box: soft orange styling, explains the tool is in development and invites users to ♥ favorite great images and 🚩 flag photos that don't fit or belong with a different prayer

## v3.00 — June 2026
- Fix Favorites button staying disabled after live photo fetch: getFavCount now reads from the DOM grid (`.btn-fav.favorited` count) instead of getCuratedPhotos, so it correctly reflects favorited live-search photos
- Fix Favorites view showing empty for live-fetched prayers: toggleFavoritesView now clones favorited img-card elements directly from the DOM instead of rebuilding from getCuratedPhotos
- Refresh script now processes Firebase custom prayers: customPrayers loaded from Firebase and appended to the prayer list if they have search terms, so all custom prayers (e.g. Maariv Aravim) get curated photos in curated.json — fixing the "no photos" state in Safari

## v2.99 — June 2026
- Fix custom prayers (Maariv Aravim etc.) stuck on "Fetching photos…" in Safari: when no API key is set and no curated photos exist for a prayer, prayerSectionHtml now shows "No curated photos available. Add an API key to search live." instead of the infinite loading spinner

## v2.98 — June 2026
- Fix "Find Images does nothing" when all prayer chips are selected: custom prayers from Firebase lack a photos/searchTerms field; three null-guards added (prayer.searchTerms.trim(), prayer.photos.map in catch block, p.photos.filter in no-API fallback)

## v2.97 — June 2026
- Block list now enforced in the no-API-key fallback paths: curated photos and hardcoded p.photos fallback are both filtered against per-prayer blockedData before rendering
- Captions suppressed for hardcoded fallback photos (p.photos) which have no src field and carry unreliable hand-written descriptions; captions still show for all curated/API/pinned photos

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
