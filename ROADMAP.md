# VT Image Helper — Roadmap & Handoff Notes

_Last updated: June 2026 (through v3.32)_

---

## Project Overview

**VT Image Helper** is a static single-page web app that helps Visual T'filah coordinators find and download prayer-matched images for worship slides. It lives at [techrabbi.org/VT-Image-Helper/](https://techrabbi.org/VT-Image-Helper/) and is hosted on GitHub Pages.

**Key facts:**
- Single HTML file: `index.html` (source edited at `/Users/medwin/Documents/VT Image Builder/vt-image-finder.html`, copied to repo)
- Images sourced from [Pexels](https://www.pexels.com) and [Unsplash](https://unsplash.com) via API (live) or a monthly-refreshed curated library (no-API fallback). Non-admin users can optionally add their own free keys via the "Advanced" box to run live search.
- Prayer/image data stored in Firebase Realtime Database
- Monthly photo refresh runs via GitHub Actions (requires `PEXELS_API_KEY`, `UNSPLASH_ACCESS_KEY`, and `ANTHROPIC_API_KEY` as GitHub Secrets — never hardcode)
- Admin login uses Firebase Email/Password Auth (token in `sessionStorage` as `vtAdminToken`, silently refreshed on expiry); admin write paths locked to the admin UID in `database.rules.json`

---

## Pending UI Polish (next session)

- **Remove the temporary "Test Unsplash download" diagnostic button** (in the admin API Keys panel, added v3.18) once Unsplash production approval is confirmed.

## This session's work (v3.18–v3.32) — summary

Full detail in `CHANGELOG.md`. Highlights:
- **Unsplash API compliance** (v3.16–v3.21): download-trigger ping + canonical "Photo by [Name] on Unsplash" attribution (both UTM-linked) on cards, lightbox, and attribution.html; temp diagnostic button (v3.18, to remove).
- **User-facing optional API keys** (v3.22, v3.25, v3.26, v3.27): per-section + collapsible header "Advanced" box → modal to paste own Pexels/Unsplash keys (shared storage with admin); framed optional per Unsplash guidelines; "Manage API keys" link when a key is set; bad-key errors link to the modal and fall back to curated photos.
- **Search-results redesign** (v3.21, v3.23, v3.24, v3.28, v3.29): 3-column controls bar (explainer + Download | chips + keywords | live-search links + Advanced); "Search these terms on: Pexels · Unsplash" links; additional-keywords → removable chips (refresh for key users, flash live-search column for no-key); "Download selected" + filename subtext; removed "N prayers matched"; red Favorites heart.
- **Bigger curated library** (curated refresh): per-prayer photos 8 → 20; vision filter parallelized 8-wide (run ~10–15 min, was ~hr).
- **Partial-match search variety** (v3.19): 30-candidate pool + `selectWithVariety`.
- **Setup-panel layout** (v3.28, v3.30, v3.31, v3.32): "Add prayers" moved into left column (col-width textarea, "Add to list ↓" below); Prayer library "Filters" label + reordered hint; "Your service list" gets a gold border + gold pulse when prayers are added; Keywords box collapsible.
- **Firebase**: silent admin token refresh (v3.20); added missing `prayerThemes`/`pinnedPhotos`/`suggestions` rules — **republished to the console** (401s resolved).
- **Bug fixes**: lightbox favorite now updates the lightbox button (v3.28).

---

## Unsplash API Compliance

**Audited June 2026 against [Unsplash API Guidelines](https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines).**

✅ **Fixed in v3.16 / v3.17:**
- **Download tracking** (v3.16) — every user download (individual + ZIP) now pings the photo's `links.download_location` with the Unsplash key (`triggerUnsplashDownload`). Captured in live search and the refresh script; stored in `curated.json` going forward.
- **Canonical attribution** (v3.16 → v3.17) — credit reads "Photo by [Name] on [Unsplash]" with both the photographer name (→ profile) and "Unsplash" (→ photo page) as UTM-tagged links, on cards and in the lightbox; `attribution.html` links photographer + source too.

**Production approval (resubmitted June 2026, awaiting Victor):** Applied for Production rates; reviewer (Victor) flagged attribution + download tracking — both since fixed (v3.16–v3.21). **Downloads are now confirmed registering on the Unsplash dev dashboard** (the trigger works; the dashboard counter just lags). Resubmitted with screenshots/recording uploaded to the Application Form. Next: await Victor's confirmation. Note: the download-tracking implementation matches Unsplash's guide exactly — right endpoint (`download_location`), authorized with `client_id`, `ixid` preserved, returns 200 + `{url}`.

✅ **Already compliant:** hotlinking via `urls.regular`; UTM-tagged link back to Unsplash; no "Unsplash" in app name; not reselling; not replicating Unsplash's core experience.

⚠️ **Accepted limitations / watch items:**
- **Client-side key** — the Unsplash key lives in `localStorage`; Unsplash prefers a server-side proxy. Tolerable for a small tool where each user supplies their own demo key (also aligns with the planned user-facing-key feature).
- **Download ping requires a key** — keyless users on the curated fallback can't be tracked (no key to authenticate the ping). Inherent to the cached-fallback design.
- **Inline hardcoded fallback photos** (in `index.html`) predate these fields, so they degrade gracefully (plain-text photographer, no ping). `curated.json` gets the fields on the next monthly refresh.
- **Monthly auto-refresh** — low-volume; disclose honestly if ever applying for Unsplash production (5,000 req/hr) access.

---

## Feature Roadmap

### High Priority

- ✅ **Service builder redesign + presets** — *(Shipped v2.46, June 2026)* Full 40/60 two-column setup panel: left = ordered service list with drag-to-reorder, inline search-term editing, and quick-start presets (Friday evening / Shabbat morning / Weekday morning / Clear all); right = prayer library chips (button model) + keywords. `findImages()` reads from ordered `_serviceOrder` array.

- ✅ **Photo lightbox / full-screen view** — *(Shipped v2.42, June 2026)* Expand button (⤡) on each card opens a full-screen overlay with large image, caption, photographer credit. ← / → buttons and keyboard arrows to browse all photos in a prayer; Esc to close, Enter to select. Select and Favorite actions available from within the lightbox.

- ✅ **ZIP download** — *(Shipped v2.42, June 2026)* "Download ZIP" button builds a single ZIP file of all selected images using JSZip (CDN), with parallel fetching and a staggered-download fallback if JSZip fails to load.

- ✅ **Partial-match search (75% threshold)** — *(Shipped v3.19)* Live search gathers a 30-candidate pool per source and `selectWithVariety` keeps the top matches while spreading the rest deeper into the relevance ranking (where photos match ~75%+ of terms, not all). More variety, no extra API calls.

### Medium Priority

- ✅ **Pending prayer email notifications** — *(Shipped v2.72, June 2026)* Admin receives email via EmailJS when a prayer is submitted or an image is flagged, with one-click Approve/Dismiss/Block action buttons in the email.

- **Holiday image sets** — Curated Pexels search-term profiles for Rosh Hashanah, Yom Kippur, Sukkot, Hanukkah, Purim, Passover, Shavuot. Could surface as a secondary filter or preset alongside the service type filters.

- **Image rating / quality flag** — Let admins mark individual photos as "preferred" (beyond favorites) so the best images surface first within a prayer's grid.

### Lower Priority / Nice to Have

- ✅ **Additional image sources** — *(Unsplash shipped v2.82; compliance v3.16–v3.21)* Unsplash integrated alongside Pexels: both keys managed in the API Keys panel + user-facing modal, results interleaved, source-aware cards/downloads/attribution. Pixabay or others could still be added later.

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
- **Bug fixed June 2026:** the deployed rules were missing three paths the app actually uses — `prayerThemes`, `pinnedPhotos`, and `suggestions` — so Firebase default-denied them, causing 401 errors in the browser console (prayer themes not loading, photo suggestions failing to submit/approve). Added to `database.rules.json` with patterns matching their siblings (themes: public read / admin write; pinnedPhotos: public read / admin write; suggestions: public write / admin read, like `reports`).
- **✅ Republished to Firebase console (June 2026):** `database.rules.json` was pasted into the console and published — the `prayerThemes`/`pinnedPhotos`/`suggestions` 401s are resolved and all admin-write locks are now active. **Reminder for future rule edits:** the repo file is NOT auto-deployed; any change to `database.rules.json` must be manually republished in the console (Realtime Database → Rules → paste → Publish).

---

## Handoff Information

### File locations

| File | Purpose |
|---|---|
| `/Users/medwin/Documents/VT Image Builder/vt-image-finder.html` | **Source file** — edit this |
| `/private/tmp/vt-image-helper/index.html` | Git working copy — copy source here before committing |
| `/private/tmp/vt-image-helper/CLAUDE.md` | Claude Code instructions for this repo (auto-push authorized) |
| `~/.claude/projects/-Users-medwin/memory/feedback_vt_version.md` | Version history log (update with every change) |

> ⚠️ `/private/tmp/` gets wiped periodically (it cleared twice during the June 2026 session). If the working copy is missing, just `gh repo clone danmedwin/VT-Image-Helper /private/tmp/vt-image-helper` — nothing is lost since everything is pushed, and the source of truth in `Documents/` is untouched.

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
| `prayerThemes/` | Per-prayer thematic text (public read / admin write) |
| `pinnedPhotos/` | Admin-approved photo suggestions shown to all (public read / admin write) |
| `suggestions/` | Visitor "this photo fits another prayer" submissions (public write / admin read) |
| `filters/` | Saved filter state (public read / admin write) |

### Admin mode

- Admin login uses **Firebase Email/Password Auth** (Identity Toolkit REST API) — email + password modal (the old client-side passcode is gone).
- ID token stored in `sessionStorage` as `vtAdminToken`; refresh token in `localStorage` as `vtAdminRefreshToken`. On a 401 mid-session the token is **silently refreshed and the request retried** (v3.20), so admins aren't logged out after the 1-hour expiry. Admin UID: `tizvHyzJ7PdsPvFpbEk4CdSPUk42`.
- Admin-only reads (`reports`, `suggestions`) are skipped for non-admin visitors to avoid 401 console noise.

### API keys (Pexels + Unsplash)

- Stored in `localStorage`: `vtImageHelper_pexelsKey` and `vtImageHelper_unsplashKey`.
- Settable via the admin API Keys panel **or** the user-facing "Advanced" modal (`openUserKeyModal`) — same storage, so both paths enable live search. Users can add just one source.
- Required for live photo search; without a key the app shows the monthly-refreshed curated library (~20 photos/prayer).

---

## Current Version

**v3.32** — see full version history in `~/.claude/projects/-Users-medwin/memory/feedback_vt_version.md`
