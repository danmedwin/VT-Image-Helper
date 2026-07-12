#!/usr/bin/env node
// Refreshes curated.json with photos from Pexels and/or Unsplash, filtered by Claude vision.
// Each prayer fetches up to CANDIDATES_PER_PRAYER candidates from each active source;
// Claude scores each for "clear space suitable for text overlay on a projected slide."
// Favorited photos are preserved regardless of Claude score; blocked photos are excluded.
// Requires at least one of: PEXELS_API_KEY, UNSPLASH_ACCESS_KEY
// Optional: ANTHROPIC_API_KEY (skips Claude visual analysis if absent)

const https = require('https');
const fs    = require('fs');
const path  = require('path');

const PEXELS_KEY    = process.env.PEXELS_API_KEY;
const UNSPLASH_KEY  = process.env.UNSPLASH_ACCESS_KEY;
const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY;
const FIREBASE_URL  = 'https://vt-image-helper-default-rtdb.firebaseio.com';
const CLAUDE_MODEL  = 'claude-haiku-4-5-20251001';
const CANDIDATES_PER_PRAYER = 40;  // fetched per source (Unsplash caps at its 30/page max)
const TARGET_PER_PRAYER     = 20;  // photos kept per prayer in curated.json
const UTM = '?utm_source=vt_image_helper&utm_medium=referral';

if (!PEXELS_KEY && !UNSPLASH_KEY) {
  console.error('✗ Neither PEXELS_API_KEY nor UNSPLASH_ACCESS_KEY is set');
  process.exit(1);
}
if (!ANTHROPIC_KEY) { console.warn('⚠ ANTHROPIC_API_KEY not set — skipping visual analysis'); }

const PRAYERS = [
  { id: 'mahtovu',        searchTerms: 'open tent morning light peaceful sunrise' },
  { id: 'modehani',       searchTerms: 'sunrise morning light awakening dawn' },
  { id: 'asheryatzar',    searchTerms: 'human hands healing light body nature' },
  { id: 'barchu',         searchTerms: 'morning horizon gathering nature sunrise meadow' },
  { id: 'yotzeror',       searchTerms: 'sunrise golden light sky dawn radiant' },
  { id: 'ahavarabbah',    searchTerms: 'open book warm light love embrace' },
  { id: 'ahavatolam',     searchTerms: 'night stars love open book candlelight evening soft light' },
  { id: 'shema',          searchTerms: 'open sky horizon blue light sunrise nature' },
  { id: 'vahavta',        searchTerms: 'doorway wooden arch home path garden love family' },
  { id: 'michamocha',     searchTerms: 'ocean sea waves freedom shore sunrise' },
  { id: 'amidah',         searchTerms: 'mountain path mist lake reflection nature peaceful' },
  { id: 'avotimahot',     searchTerms: 'ancient oak tree roots nature forest landscape' },
  { id: 'gevurot',        searchTerms: 'rain dew water drops morning leaves' },
  { id: 'kedushah',       searchTerms: 'mountain peak clouds sky radiant light nature' },
  { id: 'torahservice',   searchTerms: 'open book scroll calligraphy parchment old letters' },
  { id: 'hineimahtov',    searchTerms: 'community friends together joyful outdoor' },
  { id: 'lechadodi',      searchTerms: 'sunset warm golden candles evening glowing light' },
  { id: 'shabbatcandles', searchTerms: 'candles warm soft light flame evening glow' },
  { id: 'kiddushshabbat', searchTerms: 'wine glass grapes vineyard harvest evening golden' },
  { id: 'motzi',          searchTerms: 'braided bread golden loaf fresh baked' },
  { id: 'osehshalom',     searchTerms: 'white dove peace sky serene blue' },
  { id: 'simshalomtova',  searchTerms: 'sunrise golden rays light morning warmth sky' },
  { id: 'aleinu',         searchTerms: 'child hands soil seedling planting garden earth' },
  { id: 'kaddish',        searchTerms: 'candle flame memorial sunset evening light' },
  { id: 'einkeloheinu',   searchTerms: 'celebration people music instruments colorful light' },
  { id: 'adonolam',       searchTerms: 'stars galaxy nebula cosmos night sky space' },
  { id: 'yigdal',         searchTerms: 'mountain peaks sunrise panorama landscape majestic' },
  { id: 'psalm150',       searchTerms: 'musical instruments drums trumpet brass orchestra' },
  { id: 'mahrabu',        searchTerms: 'colorful wildflowers meadow spring flowers nature' },
  { id: 'hashkivenu',     searchTerms: 'sunset evening dusk peaceful sky rest' },
  { id: 'veshamru',       searchTerms: 'rest peaceful meadow nature sunset golden light' },
  { id: 'torahblessings', searchTerms: 'open book scroll learning light wisdom' },
];

// ─── HOLIDAY FILTERS ──────────────────────────────────────────────────────────
// Defaults mirror the client (vt-image-finder.html); live lists are loaded from
// Firebase /filters at the start of main(), so admin edits in the Filters tab
// apply here too. Jewish groups exclude on mismatch (holiday in alt text but not
// in search terms); non-Jewish keywords always exclude.

const HOLIDAY_FILTER_DEFAULT = [
  ['hanukkah', 'chanukah', 'hanukah', 'channukah', 'hannukah', 'chanukkah', 'hanuka', 'chanuka'],
  ['passover', 'pesach', 'seder'],
  ['sukkot', 'sukkos', 'succot', 'succos', 'sukkah', 'succah'],
  ['rosh hashanah', 'rosh hashana', 'rosh hashannah'],
  ['yom kippur', 'yom kipper', 'yom kipur'],
  ['purim', 'hamantash', 'hamantashen'],
  ['shavuot', 'shavuos', 'shavuoth'],
  ['simchat torah', 'simchas torah'],
];

const NON_JEWISH_FILTER_DEFAULT = [
  'christmas', 'xmas', 'christmas tree', 'santa claus', 'santa', 'nativity', 'advent',
  'easter', 'easter egg', 'easter bunny',
  'ramadan', 'eid', 'eid al-fitr', 'eid al-adha', 'iftar',
  'diwali', 'deepavali',
  'halloween', 'jack-o-lantern', 'jack o lantern',
  'kwanzaa',
  'thanksgiving turkey',
  'chinese new year', 'lunar new year',
  'dussehra', 'holi',
];

let filterJewish    = HOLIDAY_FILTER_DEFAULT;
let filterNonJewish = NON_JEWISH_FILTER_DEFAULT;

function isHolidayMismatch(altText, searchTerms) {
  const alt = (altText || '').toLowerCase();
  const search = (searchTerms || '').toLowerCase();
  if (filterNonJewish.some(s => alt.includes(s))) return true;
  return filterJewish.some(spellings =>
    spellings.some(s => alt.includes(s)) && !spellings.some(s => search.includes(s))
  );
}

// ─── HTTP HELPERS ─────────────────────────────────────────────────────────────

function httpGet(url, headers = {}) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers }, res => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => resolve({ status: res.statusCode, body }));
    }).on('error', reject);
  });
}

function httpPost(hostname, path, headers, body) {
  return new Promise((resolve, reject) => {
    const req = https.request(
      { hostname, path, method: 'POST', headers },
      res => {
        let data = '';
        res.on('data', c => data += c);
        res.on('end', () => resolve({ status: res.statusCode, body: data }));
      }
    );
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ─── PEXELS ──────────────────────────────────────────────────────────────────

async function pexelsSearch(query, perPage = CANDIDATES_PER_PRAYER) {
  const url = `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&per_page=${perPage}&orientation=landscape`;
  const { status, body } = await httpGet(url, { Authorization: PEXELS_KEY });
  if (status === 429) throw new Error('Pexels rate limit (429)');
  if (status !== 200) throw new Error(`Pexels HTTP ${status}`);
  return JSON.parse(body);
}

async function pexelsFetchById(photoId) {
  const { status, body } = await httpGet(
    `https://api.pexels.com/v1/photos/${photoId}`,
    { Authorization: PEXELS_KEY }
  );
  if (status !== 200) return null;
  return JSON.parse(body);
}

function toPexelsPhotoObj(p) {
  return {
    id:           p.id,
    caption:      p.alt || p.photographer,
    src:          p.src.large2x || p.src.large,
    srcMedium:    p.src.medium,
    sourceUrl:    p.url,
    photographer: p.photographer,
    source:       'pexels',
  };
}

// ─── UNSPLASH ────────────────────────────────────────────────────────────────

async function unsplashSearch(query, perPage = CANDIDATES_PER_PRAYER) {
  const url = `https://api.unsplash.com/search/photos?query=${encodeURIComponent(query)}&per_page=${Math.min(perPage, 30)}&orientation=landscape`;
  const { status, body } = await httpGet(url, { Authorization: 'Client-ID ' + UNSPLASH_KEY });
  if (status === 429) throw new Error('Unsplash rate limit (429)');
  if (status !== 200) throw new Error(`Unsplash HTTP ${status}`);
  return JSON.parse(body);
}

async function unsplashFetchById(photoId) {
  const { status, body } = await httpGet(
    `https://api.unsplash.com/photos/${photoId}`,
    { Authorization: 'Client-ID ' + UNSPLASH_KEY }
  );
  if (status !== 200) return null;
  return JSON.parse(body);
}

function toUnsplashPhotoObj(p) {
  return {
    id:           p.id,
    caption:      p.alt_description || p.description || p.user.name,
    src:          p.urls.regular,
    srcMedium:    p.urls.small,
    sourceUrl:    'https://unsplash.com/photos/' + p.id + UTM,
    photographer: p.user.name,
    photographerUrl: p.user.links.html + UTM,
    downloadLocation: (p.links && p.links.download_location) || '',
    source:       'unsplash',
  };
}

// ─── FIREBASE ────────────────────────────────────────────────────────────────

async function getFirebase(fbPath) {
  try {
    const { status, body } = await httpGet(`${FIREBASE_URL}/${fbPath}.json`);
    if (status !== 200) return {};
    return JSON.parse(body) || {};
  } catch (e) {
    console.warn(`  ⚠ Firebase fetch failed (${fbPath}): ${e.message}`);
    return {};
  }
}

// ─── CLAUDE VISION ───────────────────────────────────────────────────────────

const REASON_LABELS = {
  inappropriate:   'inappropriate or offensive content',
  too_distracting: 'busy or cluttered composition',
  wrong_tone:      "tone that doesn't fit Jewish prayer context",
  poor_quality:    'poor image quality (blurry, dark, or pixelated)',
  too_commercial:  'commercial or generic stock-photo aesthetic',
  off_topic:       'subject matter off-topic for a Jewish prayer service',
};

function buildClaudePrompt(negativeKeywords, avoidCriteria) {
  const rejectLines = [];
  if (negativeKeywords.length) {
    rejectLines.push(`- Visually contains any of: ${negativeKeywords.join(', ')}`);
  }
  avoidCriteria.forEach(c => rejectLines.push(`- Has ${c}`));

  const lines = [
    'Evaluate this image for a projected Jewish prayer service slide. Answer YES to include it, NO to reject it.',
    '',
    'INCLUDE if: The image has a clear, uncluttered area (open sky, simple background, or negative space) where prayer text can be legibly overlaid.',
    '',
  ];
  if (rejectLines.length) {
    lines.push('REJECT if any of these apply:');
    rejectLines.forEach(l => lines.push(l));
    lines.push('');
  }
  lines.push('Answer only YES or NO.');
  return lines.join('\n');
}

function aggregateBlockReasons(blocked) {
  const counts = {};
  for (const photos of Object.values(blocked)) {
    for (const val of Object.values(photos || {})) {
      if (val && typeof val === 'object' && val.blocked) {
        (val.reasons || []).forEach(r => { counts[r] = (counts[r] || 0) + 1; });
      }
    }
  }
  return Object.entries(counts)
    .filter(([reason]) => reason !== 'no_clear_space' && REASON_LABELS[reason])
    .sort(([, a], [, b]) => b - a)
    .map(([reason]) => REASON_LABELS[reason]);
}

let claudeConsecutiveFailures = 0;
const CLAUDE_FAILURE_THRESHOLD = 5;

async function evaluatePhoto(photoUrl, claudePrompt, warnings) {
  if (!ANTHROPIC_KEY) return true;
  if (claudeConsecutiveFailures >= CLAUDE_FAILURE_THRESHOLD) return true;

  const reqBody = JSON.stringify({
    model: CLAUDE_MODEL,
    max_tokens: 50,
    messages: [{
      role: 'user',
      content: [
        { type: 'image', source: { type: 'url', url: photoUrl } },
        { type: 'text', text: claudePrompt },
      ],
    }],
  });

  try {
    const { status, body } = await httpPost(
      'api.anthropic.com',
      '/v1/messages',
      {
        'x-api-key': ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
        'content-length': Buffer.byteLength(reqBody),
      },
      reqBody
    );

    if (status === 429) {
      warnings.push('Claude rate limit hit — including photo without analysis');
      process.stdout.write(' [Claude rate-limited]');
      claudeConsecutiveFailures++;
      return true;
    }
    if (status !== 200) {
      warnings.push(`Claude API error ${status} — including photo without analysis`);
      process.stdout.write(` [Claude ${status}]`);
      claudeConsecutiveFailures++;
      return true;
    }

    claudeConsecutiveFailures = 0;
    const parsed = JSON.parse(body);
    const answer = (parsed.content?.[0]?.text || '').trim().toUpperCase();
    return answer.startsWith('YES');
  } catch (e) {
    warnings.push(`Claude network error: ${e.message}`);
    process.stdout.write(` [Claude err]`);
    claudeConsecutiveFailures++;
    return true;
  }
}

// ─── MAIN ────────────────────────────────────────────────────────────────────

async function main() {
  const warnings = [];
  let pexelsFailures  = 0;
  let unsplashFailures = 0;
  const sources = [PEXELS_KEY && 'Pexels', UNSPLASH_KEY && 'Unsplash'].filter(Boolean);
  console.log(`Sources: ${sources.join(' + ')}`);

  console.log('Reading Firebase data…');
  const [favorites, blocked, customTerms, blockedKeywordsRaw, customPrayers, filtersRaw] = await Promise.all([
    getFirebase('favorites'),
    getFirebase('blocked'),
    getFirebase('searchTerms'),
    getFirebase('blockedKeywords'),
    getFirebase('customPrayers'),
    getFirebase('filters'),
  ]);

  if (Array.isArray(filtersRaw.nonJewish)) filterNonJewish = filtersRaw.nonJewish.filter(Boolean);
  if (Array.isArray(filtersRaw.jewish))    filterJewish    = filtersRaw.jewish.filter(Array.isArray);
  console.log(`Holiday filters: ${filterJewish.length} Jewish groups, ${filterNonJewish.length} non-Jewish keywords` +
    (Array.isArray(filtersRaw.nonJewish) || Array.isArray(filtersRaw.jewish) ? ' (from Firebase)' : ' (defaults)'));

  for (const prayer of PRAYERS) {
    if (customTerms[prayer.id]) prayer.searchTerms = customTerms[prayer.id];
  }

  // Append Firebase custom prayers that have search terms (from customPrayers or customTerms)
  if (customPrayers && typeof customPrayers === 'object') {
    const existingIds = new Set(PRAYERS.map(p => p.id));
    for (const [id, cp] of Object.entries(customPrayers)) {
      if (existingIds.has(id)) continue;
      const terms = customTerms[id] || (cp && cp.searchTerms) || '';
      if (!terms) {
        console.log(`  Skipping custom prayer "${id}" — no search terms`);
        continue;
      }
      PRAYERS.push({ id, searchTerms: terms });
    }
  }

  const negativeKeywords = Array.isArray(blockedKeywordsRaw) ? blockedKeywordsRaw : [];
  const avoidCriteria    = aggregateBlockReasons(blocked);
  const claudePrompt     = buildClaudePrompt(negativeKeywords, avoidCriteria);

  if (ANTHROPIC_KEY) {
    console.log(`Using Claude (${CLAUDE_MODEL}) to evaluate photos.`);
    if (negativeKeywords.length) console.log(`  Visual blocklist: ${negativeKeywords.join(', ')}`);
    if (avoidCriteria.length)    console.log(`  Learned criteria: ${avoidCriteria.join('; ')}`);
  }
  console.log();

  const prayers = {};

  for (let i = 0; i < PRAYERS.length; i++) {
    const { id, searchTerms } = PRAYERS[i];
    process.stdout.write(`[${i + 1}/${PRAYERS.length}] ${id} … `);

    const blockedInPrayer = new Set(
      Object.entries(blocked[id] || {})
        .filter(([, v]) => v === true || (v && v.blocked === true))
        .map(([photoId]) => String(photoId))
    );

    // 1. Fetch candidates from each active source in parallel
    const fetchPromises = [];
    if (PEXELS_KEY) {
      fetchPromises.push(
        pexelsSearch(searchTerms)
          .then(data => (data.photos || []).map(toPexelsPhotoObj))
          .catch(e => {
            warnings.push(`Pexels search failed for ${id}: ${e.message}`);
            pexelsFailures++;
            process.stdout.write(`[Pexels err] `);
            return [];
          })
      );
    }
    if (UNSPLASH_KEY) {
      fetchPromises.push(
        unsplashSearch(searchTerms)
          .then(data => (data.results || []).map(toUnsplashPhotoObj))
          .catch(e => {
            warnings.push(`Unsplash search failed for ${id}: ${e.message}`);
            unsplashFailures++;
            process.stdout.write(`[Unsplash err] `);
            return [];
          })
      );
    }

    const results = await Promise.all(fetchPromises);

    // Interleave results from each source, then filter blocked/holiday photos
    const interleaved = [];
    const maxLen = Math.max(...results.map(r => r.length));
    for (let j = 0; j < maxLen; j++) {
      for (const sourceResults of results) {
        if (j < sourceResults.length) interleaved.push(sourceResults[j]);
      }
    }
    const candidates = interleaved
      .filter(p => !blockedInPrayer.has(String(p.id)))
      .filter(p => !isHolidayMismatch(p.caption, searchTerms));

    process.stdout.write(`${candidates.length} candidates`);

    // 2. Claude visual filter — keep up to TARGET_PER_PRAYER that pass
    let freshPhotos = [];
    if (candidates.length && ANTHROPIC_KEY) {
      process.stdout.write(' → filtering…');
      // Evaluate candidates in concurrent batches (preserves ranked order; stops
      // once TARGET_PER_PRAYER pass). Sequential was far too slow at higher targets.
      const VISION_CONCURRENCY = 8;
      for (let b = 0; b < candidates.length && freshPhotos.length < TARGET_PER_PRAYER; b += VISION_CONCURRENCY) {
        const batch = candidates.slice(b, b + VISION_CONCURRENCY);
        const verdicts = await Promise.all(
          batch.map(p => evaluatePhoto(p.srcMedium || p.src, claudePrompt, warnings))
        );
        for (let k = 0; k < batch.length; k++) {
          if (verdicts[k]) {
            freshPhotos.push(batch[k]);
            if (freshPhotos.length >= TARGET_PER_PRAYER) break;
          }
        }
      }
      if (freshPhotos.length === 0 && candidates.length > 0) {
        const msg = `Claude rejected all candidates for ${id} — using unfiltered`;
        warnings.push(msg);
        freshPhotos = candidates.slice(0, TARGET_PER_PRAYER);
        process.stdout.write(' (all rejected, using unfiltered)');
      } else {
        // Pad with unfiltered candidates if Claude approved fewer than target
        if (freshPhotos.length < TARGET_PER_PRAYER && candidates.length > freshPhotos.length) {
          const seen = new Set(freshPhotos.map(p => String(p.id)));
          const pad = candidates.filter(p => !seen.has(String(p.id))).slice(0, TARGET_PER_PRAYER - freshPhotos.length);
          freshPhotos = [...freshPhotos, ...pad];
        }
        process.stdout.write(` ${freshPhotos.length} photos`);
      }
    } else {
      freshPhotos = candidates.slice(0, TARGET_PER_PRAYER);
    }

    // 3. Fetch favorited photos not already in fresh results
    // Detect source by ID shape: numeric string = Pexels, else = Unsplash
    const freshIds = new Set(freshPhotos.map(p => String(p.id)));
    const favoritedIds = Object.entries(favorites[id] || {})
      .filter(([photoId, count]) => count > 0 && !blockedInPrayer.has(photoId))
      .map(([photoId]) => photoId);
    const missingFavIds = favoritedIds.filter(pid => !freshIds.has(pid));

    const protectedPhotos = [];
    for (const photoId of missingFavIds) {
      await sleep(150);
      try {
        const isPexels = /^\d+$/.test(photoId);
        if (isPexels && PEXELS_KEY) {
          const p = await pexelsFetchById(photoId);
          if (p) {
            protectedPhotos.push({ ...toPexelsPhotoObj(p), favorited: true });
            process.stdout.write(` +fav(${photoId})`);
          }
        } else if (!isPexels && UNSPLASH_KEY) {
          const p = await unsplashFetchById(photoId);
          if (p) {
            protectedPhotos.push({ ...toUnsplashPhotoObj(p), favorited: true });
            process.stdout.write(` +fav(${photoId})`);
          }
        }
      } catch (e) {
        warnings.push(`Could not fetch favorited photo ${photoId} for ${id}: ${e.message}`);
      }
    }

    prayers[id] = [...protectedPhotos, ...freshPhotos];
    console.log();

    if (i < PRAYERS.length - 1) await sleep(250);
  }

  // ── Write output ───────────────────────────────────────────────────────────

  const today = new Date().toISOString().split('T')[0];
  const out = {
    refreshed: today,
    sources,
    claudeFiltered: !!ANTHROPIC_KEY,
    prayers,
    ...(warnings.length ? { warnings } : {}),
  };
  const outPath = path.join(process.cwd(), 'curated.json');
  fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
  console.log(`\n✓ Written ${outPath} (${today})`);

  // ── Summary & alerts ───────────────────────────────────────────────────────

  if (warnings.length) {
    console.log(`\n⚠ ${warnings.length} warning(s) during refresh:`);
    warnings.forEach(w => console.log(`  - ${w}`));
  } else {
    console.log('✓ No warnings.');
  }

  const summaryPath = process.env.GITHUB_STEP_SUMMARY;
  if (summaryPath) {
    const lines = [
      `## Curated Photo Refresh — ${today}`,
      '',
      `| | |`,
      `|---|---|`,
      `| Sources | ${sources.join(' + ')} |`,
      `| Prayers refreshed | ${PRAYERS.length} |`,
      `| Claude visual filter | ${ANTHROPIC_KEY ? `✓ (${CLAUDE_MODEL})` : '✗ (no key)'} |`,
      `| Warnings | ${warnings.length} |`,
      '',
    ];
    if (warnings.length) {
      lines.push('### Warnings');
      warnings.forEach(w => lines.push(`- ${w}`));
    }
    fs.appendFileSync(summaryPath, lines.join('\n') + '\n');
  }

  const claudeDown   = ANTHROPIC_KEY && claudeConsecutiveFailures >= CLAUDE_FAILURE_THRESHOLD;
  const pexelsDown   = PEXELS_KEY   && pexelsFailures   > PRAYERS.length / 2;
  const unsplashDown = UNSPLASH_KEY && unsplashFailures > PRAYERS.length / 2;

  if (pexelsDown) {
    console.error(`\n✗ Pexels API failed for ${pexelsFailures}/${PRAYERS.length} prayers — check PEXELS_API_KEY secret`);
    process.exit(1);
  }
  if (unsplashDown) {
    console.error(`\n✗ Unsplash API failed for ${unsplashFailures}/${PRAYERS.length} prayers — check UNSPLASH_ACCESS_KEY secret`);
    process.exit(1);
  }
  if (claudeDown) {
    console.error(`\n✗ Claude API failed ${claudeConsecutiveFailures} times in a row — check ANTHROPIC_API_KEY secret`);
    process.exit(1);
  }
}

main().catch(e => {
  console.error('✗ Fatal error:', e.message);
  process.exit(1);
});
