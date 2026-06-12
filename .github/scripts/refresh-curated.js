#!/usr/bin/env node
// Refreshes curated.json with Pexels photos filtered by Claude vision analysis.
// Each prayer fetches up to 10 candidates from Pexels; Claude scores each for
// "clear space suitable for text overlay on a projected slide." Favorited photos
// are preserved regardless of Claude score; blocked photos are excluded entirely.
// Requires: PEXELS_API_KEY (mandatory), ANTHROPIC_API_KEY (optional — skips analysis if absent)

const https = require('https');
const fs    = require('fs');
const path  = require('path');

const PEXELS_KEY    = process.env.PEXELS_API_KEY;
const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY;
const FIREBASE_URL  = 'https://vt-image-helper-default-rtdb.firebaseio.com';
const CLAUDE_MODEL  = 'claude-haiku-4-5-20251001';
const CANDIDATES_PER_PRAYER = 10;
const TARGET_PER_PRAYER     = 4;

if (!PEXELS_KEY) { console.error('✗ PEXELS_API_KEY is not set'); process.exit(1); }
if (!ANTHROPIC_KEY) { console.warn('⚠ ANTHROPIC_API_KEY not set — skipping visual analysis'); }

const PRAYERS = [
  { id: 'mahtovu',        searchTerms: 'open tent morning light peaceful sunrise' },
  { id: 'modehanee',      searchTerms: 'sunrise morning light awakening dawn' },
  { id: 'asheryatzar',    searchTerms: 'human hands healing light body nature' },
  { id: 'barchu',         searchTerms: 'morning horizon gathering nature sunrise meadow' },
  { id: 'yotzeior',       searchTerms: 'sunrise golden light sky dawn radiant' },
  { id: 'ahavarabbah',    searchTerms: 'open book warm light love embrace' },
  { id: 'shema',          searchTerms: 'vast sky horizon single light unity one' },
  { id: 'vahavta',        searchTerms: 'mezuzah doorway love family path forward' },
  { id: 'michamocha',     searchTerms: 'ocean sea waves freedom shore sunrise' },
  { id: 'amidah',         searchTerms: 'mountain path mist still lake reflection nature solitude' },
  { id: 'avotimahot',     searchTerms: 'ancient tree roots heritage generational nature' },
  { id: 'gevurot',        searchTerms: 'rain dew water drops morning renewal' },
  { id: 'kedushah',       searchTerms: 'mountain peak clouds sky radiant light nature' },
  { id: 'torahservice',   searchTerms: 'open book scroll calligraphy parchment old letters' },
  { id: 'hineimahtov',    searchTerms: 'community friends together joyful outdoor' },
  { id: 'lechadodi',      searchTerms: 'sunset friday shabbat candles warm glow' },
  { id: 'shabbatcandles', searchTerms: 'candles soft warm light flame shabbat' },
  { id: 'kiddushshabbat', searchTerms: 'wine glass grapes vineyard kiddush' },
  { id: 'motzi',          searchTerms: 'challah bread golden loaf fresh baked' },
  { id: 'oseishalom',     searchTerms: 'white dove peace sky serene blue' },
  { id: 'aleinu',         searchTerms: 'child planting nature world hope future' },
  { id: 'kaddish',        searchTerms: 'candle flame memory sunset quiet light' },
  { id: 'einkelo',        searchTerms: 'joyful celebration music light festive' },
  { id: 'adonolam',       searchTerms: 'universe stars galaxy infinity night sky' },
  { id: 'yigdal',         searchTerms: 'sunrise expansive sky mountains grandeur' },
  { id: 'psalm150',       searchTerms: 'musical instruments trumpet praise joyful' },
  { id: 'mahrabu',        searchTerms: 'wildflowers field nature wonder creation colorful' },
  { id: 'kavanah',        searchTerms: 'tree roots grounded stillness meditation' },
  { id: 'hashkivenu',     searchTerms: 'sunset evening dusk peaceful sky rest' },
  { id: 'veshamru',       searchTerms: 'shabbat rest peaceful nature covenant light' },
  { id: 'torahblessings', searchTerms: 'open book scroll learning light wisdom' },
  { id: 'wherever',       searchTerms: 'globe world map wandering journey' },
];

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

function toPhotoObj(p) {
  return {
    id:          p.id,
    caption:     p.alt || p.photographer,
    src:         p.src.large2x || p.src.large,
    srcMedium:   p.src.medium,   // used for Claude vision analysis (faster)
    pexelsUrl:   p.url,
    photographer: p.photographer,
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

let claudeConsecutiveFailures = 0;
const CLAUDE_FAILURE_THRESHOLD = 5; // stop trying after 5 consecutive errors

async function hasTextSpace(photoUrl, warnings) {
  if (!ANTHROPIC_KEY) return true;
  if (claudeConsecutiveFailures >= CLAUDE_FAILURE_THRESHOLD) return true;

  const reqBody = JSON.stringify({
    model: CLAUDE_MODEL,
    max_tokens: 50,
    messages: [{
      role: 'user',
      content: [
        {
          type: 'image',
          source: { type: 'url', url: photoUrl },
        },
        {
          type: 'text',
          text: 'Does this photo have a clear, uncluttered area — such as open sky, solid background, or negative space — where prayer text could be legibly overlaid on a projected slide? Answer only YES or NO.',
        },
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
      const msg = 'Claude rate limit hit — including photo without analysis';
      warnings.push(msg);
      process.stdout.write(' [Claude rate-limited]');
      claudeConsecutiveFailures++;
      return true;
    }
    if (status !== 200) {
      const msg = `Claude API error ${status} — including photo without analysis`;
      warnings.push(msg);
      process.stdout.write(` [Claude ${status}]`);
      claudeConsecutiveFailures++;
      return true;
    }

    claudeConsecutiveFailures = 0;
    const parsed = JSON.parse(body);
    const answer = (parsed.content?.[0]?.text || '').trim().toUpperCase();
    return answer.startsWith('YES');
  } catch (e) {
    const msg = `Claude network error: ${e.message}`;
    warnings.push(msg);
    process.stdout.write(` [Claude err]`);
    claudeConsecutiveFailures++;
    return true; // include on error — don't punish network blips
  }
}

// ─── MAIN ────────────────────────────────────────────────────────────────────

async function main() {
  const warnings = [];
  let pexelsFailures = 0;

  console.log('Reading Firebase data (favorites, blocked, custom search terms)…');
  const [favorites, blocked, customTerms] = await Promise.all([
    getFirebase('favorites'),
    getFirebase('blocked'),
    getFirebase('searchTerms'),
  ]);

  for (const prayer of PRAYERS) {
    if (customTerms[prayer.id]) prayer.searchTerms = customTerms[prayer.id];
  }

  if (ANTHROPIC_KEY) {
    console.log(`Using Claude (${CLAUDE_MODEL}) to filter for text-overlay space.`);
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

    // 1. Fresh Pexels search (fetch extra candidates for Claude to filter down)
    let candidates = [];
    try {
      const data = await pexelsSearch(searchTerms);
      candidates = (data.photos || [])
        .map(toPhotoObj)
        .filter(p => !blockedInPrayer.has(String(p.id)));
      process.stdout.write(`${candidates.length} candidates`);
    } catch (e) {
      const msg = `Pexels search failed for ${id}: ${e.message}`;
      warnings.push(msg);
      pexelsFailures++;
      process.stdout.write(`search failed (${e.message})`);
    }

    // 2. Claude visual filter — keep up to TARGET_PER_PRAYER that pass
    let freshPhotos = [];
    if (candidates.length && ANTHROPIC_KEY) {
      process.stdout.write(' → filtering…');
      for (const photo of candidates) {
        await sleep(120); // avoid Claude rate limits
        const passes = await hasTextSpace(photo.srcMedium || photo.src, warnings);
        if (passes) {
          freshPhotos.push(photo);
          if (freshPhotos.length >= TARGET_PER_PRAYER) break;
        }
      }
      // If Claude rejected everything, fall back to unfiltered candidates
      if (freshPhotos.length === 0 && candidates.length > 0) {
        const msg = `Claude rejected all candidates for ${id} — using unfiltered`;
        warnings.push(msg);
        freshPhotos = candidates.slice(0, TARGET_PER_PRAYER);
        process.stdout.write(' (all rejected, using unfiltered)');
      } else {
        process.stdout.write(` ${freshPhotos.length} pass`);
      }
    } else {
      // No Claude key — take first TARGET_PER_PRAYER unblocked candidates
      freshPhotos = candidates.slice(0, TARGET_PER_PRAYER);
    }

    // 3. Fetch favorited photos not already in fresh results
    const freshIds = new Set(freshPhotos.map(p => String(p.id)));
    const favoritedIds = Object.entries(favorites[id] || {})
      .filter(([photoId, count]) => count > 0 && !blockedInPrayer.has(photoId))
      .map(([photoId]) => photoId);
    const missingFavIds = favoritedIds.filter(pid => !freshIds.has(pid));

    const protectedPhotos = [];
    for (const photoId of missingFavIds) {
      await sleep(150);
      try {
        const p = await pexelsFetchById(photoId);
        if (p) {
          protectedPhotos.push({ ...toPhotoObj(p), favorited: true });
          process.stdout.write(` +fav(${photoId})`);
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

  // Write GitHub Actions step summary (visible in the Actions UI)
  const summaryPath = process.env.GITHUB_STEP_SUMMARY;
  if (summaryPath) {
    const lines = [
      `## Curated Photo Refresh — ${today}`,
      '',
      `| | |`,
      `|---|---|`,
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

  // Exit non-zero to trigger GitHub email alert on significant failures
  const claudeDown = ANTHROPIC_KEY && claudeConsecutiveFailures >= CLAUDE_FAILURE_THRESHOLD;
  const pexelsDown = pexelsFailures > PRAYERS.length / 2;

  if (pexelsDown) {
    console.error(`\n✗ Pexels API failed for ${pexelsFailures}/${PRAYERS.length} prayers — check PEXELS_API_KEY secret`);
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
