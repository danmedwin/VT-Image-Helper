# VT Image Helper — Roadmap & Handoff Notes

_Last updated: June 2026_

---

## Project Overview

**VT Image Helper** is a static single-page web app that helps Visual T'filah coordinators find and download prayer-matched images for worship slides. It lives at [techrabbi.org/VT-Image-Helper/](https://techrabbi.org/VT-Image-Helper/) and is hosted on GitHub Pages.

**Key facts:**
- Single HTML file: `index.html` (source edited at `/Users/medwin/Documents/VT Image Builder/vt-image-finder.html`, copied to repo)
- Images sourced from [Pexels](https://www.pexels.com) via API (live) or a monthly-refreshed curated library (no-API fallback)
- Prayer/image data stored in Firebase Realtime Database
- Monthly photo refresh runs via GitHub Actions (requires `PEXELS_API_KEY` and `ANTHROPIC_API_KEY` as GitHub Secrets — never hardcode)
- Admin mode is passcode-protected (client-side only — see security notes below)

---

## Pending UI Polish (next session)

_(none pending)_

---

## Feature Roadmap

### High Priority

- ✅ **Service builder redesign + presets** — *(Shipped v2.46, June 2026)* Full 40/60 two-column setup panel: left = ordered service list with drag-to-reorder, inline search-term editing, and quick-start presets (Friday evening / Shabbat morning / Weekday morning / Clear all); right = prayer library chips (button model) + keywords. `findImages()` reads from ordered `_serviceOrder` array.

- ✅ **Photo lightbox / full-screen view** — *(Shipped v2.42, June 2026)* Expand button (⤡) on each card opens a full-screen overlay with large image, caption, photographer credit. ← / → buttons and keyboard arrows to browse all photos in a prayer; Esc to close, Enter to select. Select and Favorite actions available from within the lightbox.

- ✅ **ZIP download** — *(Shipped v2.42, June 2026)* "Download ZIP" button builds a single ZIP file of all selected images using JSZip (CDN), with parallel fetching and a staggered-download fallback if JSZip fails to load.

- **Partial-match search (75% threshold)** — Rather than requiring images to match *every* search term, surface images that match 75% or more of the terms. This should yield more variation in the returned images instead of an over-narrowed result set.

### Medium Priority

- ✅ **Pending prayer email notifications** — *(Shipped v2.72, June 2026)* Admin receives email via EmailJS when a prayer is submitted or an image is flagged, with one-click Approve/Dismiss/Block action buttons in the email.

- **Holiday image sets** — Curated Pexels search-term profiles for Rosh Hashanah, Yom Kippur, Sukkot, Hanukkah, Purim, Passover, Shavuot. Could surface as a secondary filter or preset alongside the service type filters.

- **Image rating / quality flag** — Let admins mark individual photos as "preferred" (beyond favorites) so the best images surface first within a prayer's grid.

### Lower Priority / Nice to Have

- **Additional image sources** — Integrate sources beyond Pexels (e.g. Unsplash, Pixabay). Would give access to a broader photo library and reduce dependency on a single provider. Requires separate API key handling per source and adapting the image card/download flow to each provider's attribution rules.

- **Keyboard navigation** — Arrow keys to move between images in a prayer section; Enter to select; Space to open lightbox.
- **Image & attribution export** — A way for users to get a list of their selected images with proper photographer attributions, e.g. exported as a PDF or printable page. Useful for copyright compliance.
- **Multi-language support** — Hebrew prayer names as an alternate display mode.

---

## Firebase Security Audit

**Current rules file reviewed June 2026.**

### ⚠️ Core limitation

Admin mode is enforced entirely client-side (sessionStorage + passcode). Firebase has no way to distinguish an admin from a regular user, so every path that admins write to is also writable by any visitor who knows the URL. For a small congregational tool with low attack surface this is probably acceptable short-term, but it is a real vulnerability.

### Path-by-path review

| Path | Read | Write | Status | Notes |
|---|---|---|---|---|
| `favorites` | Public | Validated (number 0–9999) | ✅ Good | Write validation prevents garbage data |
| `blocked` | Public | Open | ⚠️ Risk | Anyone can block/unblock photos |
| `blockedKeywords` | Public | Open | ⚠️ Risk | Anyone can corrupt the Claude vision blocklist |
| `searchTerms` | Public | Open | ⚠️ Risk | Anyone can alter prayer search terms for all users |
| `reports` | Public | Open | ⚠️ Mild | Exposing all user reports publicly; write-open is fine for user reporting |
| `customPrayers` | Public | Open | ⚠️ Risk | Anyone can inject or delete custom prayers |
| `hiddenPrayers` | Public | Open | ⚠️ Risk | Anyone can hide prayers from the list |
| `prayerDisplayNames` | Public | Open | ⚠️ Risk | Anyone can rename prayers |
| `prayerOrder` | Public | Open | ⚠️ Risk | Anyone can reorder the prayer list |
| `prayerTags` | Public | Open | ⚠️ Risk | Anyone can change service tags |
| `pendingPrayers` | Public | Open | ⚠️ Mild | Submissions are readable by anyone; write-open needed for submissions |
| `siteDefaults` | Public | Open | ⚠️ Risk | Anyone can overwrite the saved default state |
| `promotedPrayers` | Public | Open | ⚠️ Risk | Anyone can clear the "custom" badge on prayers |

### Recommendations

**Short-term (low effort) — ✅ Completed June 2026:**
- ✅ `.validate` rules for all string fields added to `database.rules.json` (committed to repo). **Needs to be deployed to Firebase:** open Firebase console → Realtime Database → Rules tab → paste the contents of `database.rules.json` → Publish.
- `reports` read exposure: accepted for now (low-sensitivity — only contains photo URLs + user-entered flag reasons).
- `pendingPrayers` public read: accepted for now — restricting it would break the admin Submissions tab without a server-side auth layer.

**Medium-term — ✅ Completed June 2026:**
- ✅ Admin login now uses Firebase Email/Password Auth (Identity Toolkit REST API). Passcode prompt removed; email + password modal replaces it. ID token stored in `sessionStorage` as `vtAdminToken`.
- ✅ All high-risk write paths (`blocked`, `blockedKeywords`, `searchTerms`, `prayerOrder`, `prayerTags`, `prayerDisplayNames`, `customPrayers`, `hiddenPrayers`, `siteDefaults`, `promotedPrayers`) locked to `auth.uid === adminUID` in `database.rules.json`.
- ✅ `reports` reads locked to admin only.
- ✅ `pendingPrayers` writes: admin has full access; public can only write new entries with `status: 'pending'`.
- **Still needed:** Deploy `database.rules.json` to Firebase console (Realtime Database → Rules → Publish). Until deployed, the JS changes are live but the server-side enforcement is not.

---

## Handoff Information

### File locations

| File | Purpose |
|---|---|
| `/Users/medwin/Documents/VT Image Builder/vt-image-finder.html` | **Source file** — edit this |
| `/tmp/vt-image-helper/index.html` | Git working copy — copy source here before committing |
| `/tmp/vt-image-helper/header-bg.jpg` | Header background photo (Pexels, Marek Piwnicki) |
| `/tmp/vt-image-helper/CLAUDE.md` | Claude Code instructions for this repo (auto-push authorized) |
| `~/.claude/projects/-Users-medwin/memory/feedback_vt_version.md` | Version history log (update with every change) |

### Git / deployment

- **Repo:** `github.com/danmedwin/VT-Image-Helper` (private)
- **Hosting:** GitHub Pages — every push to `main` deploys automatically (1–2 min lag)
- **Monthly refresh Action:** `.github/workflows/refresh-curated.yml` — runs on the 1st of each month; requires `PEXELS_API_KEY` and `ANTHROPIC_API_KEY` set as GitHub repository secrets

### Firebase

- **Project:** `vt-image-helper` (Firebase console → Realtime Database)
- **URL:** `https://vt-image-helper-default-rtdb.firebaseio.com`
- **Auth:** None currently (unauthenticated REST API)

#### Key Firebase paths

| Path | What it stores |
|---|---|
| `favorites/` | Per-prayer, per-photo favorite counts (shared across all users) |
| `blocked/` | Photos blocked from appearing in results |
| `blockedKeywords/` | Text keywords fed to Claude vision filter during monthly refresh |
| `searchTerms/` | Admin-edited Pexels search terms per prayer |
| `reports/` | User-submitted photo reports (flagged images) |
| `customPrayers/` | Prayers added by admin or approved from user submissions |
| `promotedPrayers/` | IDs of custom prayers promoted to "official" (no custom badge) |
| `hiddenPrayers/` | Prayers hidden from the public list |
| `prayerDisplayNames/` | Admin-edited display name overrides per prayer |
| `prayerOrder/` | Custom drag-reorder override (empty = use MT order) |
| `prayerTags/` | Service tag overrides per prayer (morning/evening/shabbat/weekday) |
| `pendingPrayers/` | User-submitted prayer suggestions awaiting admin review |
| `siteDefaults/` | Snapshot saved by "Save as default" (order + tags + terms) |

### Admin mode

- Double-click the "Admin" button in the page footer; enter the passcode
- Stored in `sessionStorage` as `vtAdmin` — persists until the tab is closed
- **The passcode is in the client JS source** — visible to anyone who views source. Consider rotating it or moving to proper auth.

### Pexels API key

- Stored in the user's browser `localStorage` (key: `vtImageHelper_pexelsKey`)
- Set via the API Key tab in the admin panel
- Required for live photo search; without it the app falls back to the monthly-refreshed curated library

---

## Current Version

**v3.15** — see full version history in `~/.claude/projects/-Users-medwin/memory/feedback_vt_version.md`
