#!/usr/bin/env node
// Fetches 4 landscape photos per prayer from Pexels and writes curated.json.
// Reads favorites from Firebase — favorited photos are fetched by ID and
// preserved even if the new Pexels search doesn't return them.
// Reads blocked from Firebase — blocked photos are excluded entirely.
// Run by the GitHub Action; requires PEXELS_API_KEY env var.

const https = require('https');
const fs    = require('fs');
const path  = require('path');

const API_KEY      = process.env.PEXELS_API_KEY;
const FIREBASE_URL = 'https://vt-image-helper-default-rtdb.firebaseio.com';

if (!API_KEY) { console.error('PEXELS_API_KEY is not set'); process.exit(1); }

const PRAYERS = [
  { id: 'mahtovu',       searchTerms: 'open tent morning light peaceful sunrise' },
  { id: 'modehanee',     searchTerms: 'sunrise morning light awakening dawn' },
  { id: 'asheryatzar',   searchTerms: 'human hands healing light body nature' },
  { id: 'barchu',        searchTerms: 'morning horizon gathering nature sunrise meadow' },
  { id: 'yotzeior',      searchTerms: 'sunrise golden light sky dawn radiant' },
  { id: 'ahavarabbah',   searchTerms: 'open book warm light love embrace' },
  { id: 'shema',         searchTerms: 'vast sky horizon single light unity one' },
  { id: 'vahavta',       searchTerms: 'mezuzah doorway love family path forward' },
  { id: 'michamocha',    searchTerms: 'ocean sea waves freedom shore sunrise' },
  { id: 'amidah',        searchTerms: 'mountain path mist still lake reflection nature solitude' },
  { id: 'avotimahot',    searchTerms: 'ancient tree roots heritage generational nature' },
  { id: 'gevurot',       searchTerms: 'rain dew water drops morning renewal' },
  { id: 'kedushah',      searchTerms: 'mountain peak clouds sky radiant light nature' },
  { id: 'torahservice',  searchTerms: 'open book scroll calligraphy parchment old letters' },
  { id: 'hineimahtov',   searchTerms: 'community friends together joyful outdoor' },
  { id: 'lechadodi',     searchTerms: 'sunset friday shabbat candles warm glow' },
  { id: 'shabbatcandles',searchTerms: 'candles soft warm light flame shabbat' },
  { id: 'kiddushshabbat',searchTerms: 'wine glass grapes vineyard kiddush' },
  { id: 'motzi',         searchTerms: 'challah bread golden loaf fresh baked' },
  { id: 'oseishalom',    searchTerms: 'white dove peace sky serene blue' },
  { id: 'aleinu',        searchTerms: 'child planting nature world hope future' },
  { id: 'kaddish',       searchTerms: 'candle flame memory sunset quiet light' },
  { id: 'einkelo',       searchTerms: 'joyful celebration music light festive' },
  { id: 'adonolam',      searchTerms: 'universe stars galaxy infinity night sky' },
  { id: 'yigdal',        searchTerms: 'sunrise expansive sky mountains grandeur' },
  { id: 'psalm150',      searchTerms: 'musical instruments trumpet praise joyful' },
  { id: 'mahrabu',       searchTerms: 'wildflowers field nature wonder creation colorful' },
  { id: 'kavanah',       searchTerms: 'tree roots grounded stillness meditation' },
  { id: 'hashkivenu',    searchTerms: 'sunset evening dusk peaceful sky rest' },
  { id: 'veshamru',      searchTerms: 'shabbat rest peaceful nature covenant light' },
  { id: 'torahblessings',searchTerms: 'open book scroll learning light wisdom' },
  { id: 'wherever',      searchTerms: 'globe world map wandering journey' },
];

function get(url, headers = {}) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers }, res => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => resolve({ status: res.statusCode, body }));
    }).on('error', reject);
  });
}

async function pexelsSearch(query) {
  const url = `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&per_page=4&orientation=landscape`;
  const { status, body } = await get(url, { Authorization: API_KEY });
  if (status !== 200) throw new Error(`Pexels search HTTP ${status}`);
  return JSON.parse(body);
}

async function pexelsFetchById(photoId) {
  const { status, body } = await get(`https://api.pexels.com/v1/photos/${photoId}`, { Authorization: API_KEY });
  if (status !== 200) return null;
  return JSON.parse(body);
}

async function getFirebase(path) {
  try {
    const { status, body } = await get(`${FIREBASE_URL}/${path}.json`);
    if (status !== 200) return {};
    return JSON.parse(body) || {};
  } catch (e) {
    console.warn(`Could not fetch Firebase ${path}:`, e.message);
    return {};
  }
}

function toPhotoObj(p) {
  return {
    id:           p.id,
    caption:      p.alt || p.photographer,
    src:          p.src.large,
    pexelsUrl:    p.url,
    photographer: p.photographer,
  };
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  console.log('Reading favorites, blocked, and custom search terms from Firebase…');
  const [favorites, blocked, customTerms] = await Promise.all([
    getFirebase('favorites'),
    getFirebase('blocked'),
    getFirebase('searchTerms'),
  ]);

  // Apply admin-edited search terms
  for (const prayer of PRAYERS) {
    if (customTerms[prayer.id]) prayer.searchTerms = customTerms[prayer.id];
  }

  const prayers = {};

  for (let i = 0; i < PRAYERS.length; i++) {
    const { id, searchTerms } = PRAYERS[i];
    process.stdout.write(`[${i + 1}/${PRAYERS.length}] ${id} … `);

    const blockedInPrayer = new Set(
      Object.entries(blocked[id] || {})
        .filter(([, v]) => v === true)
        .map(([photoId]) => String(photoId))
    );

    // 1. Fresh Pexels search — exclude blocked photos
    let freshPhotos = [];
    try {
      const data = await pexelsSearch(searchTerms);
      freshPhotos = (data.photos || [])
        .map(toPhotoObj)
        .filter(p => !blockedInPrayer.has(String(p.id)));
      process.stdout.write(`${freshPhotos.length} fresh`);
    } catch (e) {
      process.stdout.write(`search failed (${e.message})`);
    }

    // 2. Fetch favorited photos not in fresh results and not blocked
    const freshIds = new Set(freshPhotos.map(p => String(p.id)));
    const favoritedIds = Object.entries(favorites[id] || {})
      .filter(([photoId, count]) => count > 0 && !blockedInPrayer.has(photoId))
      .map(([photoId]) => photoId);
    const missingFavIds = favoritedIds.filter(pid => !freshIds.has(pid));

    const protectedPhotos = [];
    for (const photoId of missingFavIds) {
      await sleep(150);
      const p = await pexelsFetchById(photoId);
      if (p) {
        protectedPhotos.push({ ...toPhotoObj(p), favorited: true });
        process.stdout.write(` +protected(${photoId})`);
      }
    }

    prayers[id] = [...protectedPhotos, ...freshPhotos];
    console.log();

    if (i < PRAYERS.length - 1) await sleep(250);
  }

  const today = new Date().toISOString().split('T')[0];
  const out   = { refreshed: today, prayers };
  const outPath = path.join(process.cwd(), 'curated.json');
  fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
  console.log(`\nWritten ${outPath} (refreshed: ${today})`);
}

main().catch(e => { console.error(e); process.exit(1); });
