#!/usr/bin/env node
// Fetches 4 landscape photos per prayer from Pexels and writes curated.json.
// Run by the GitHub Action; requires PEXELS_API_KEY env var.

const https = require('https');
const fs    = require('fs');
const path  = require('path');

const API_KEY = process.env.PEXELS_API_KEY;
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

function pexelsFetch(query) {
  return new Promise((resolve, reject) => {
    const url = `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&per_page=4&orientation=landscape`;
    https.get(url, { headers: { Authorization: API_KEY } }, res => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        if (res.statusCode !== 200) return reject(new Error(`HTTP ${res.statusCode}`));
        resolve(JSON.parse(body));
      });
    }).on('error', reject);
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  const prayers = {};

  for (let i = 0; i < PRAYERS.length; i++) {
    const { id, searchTerms } = PRAYERS[i];
    console.log(`[${i + 1}/${PRAYERS.length}] ${id}`);
    try {
      const data = await pexelsFetch(searchTerms);
      prayers[id] = (data.photos || []).map(p => ({
        id:           p.id,
        caption:      p.alt || p.photographer,
        src:          p.src.large,
        pexelsUrl:    p.url,
        photographer: p.photographer,
      }));
    } catch (e) {
      console.error(`  ✗ ${e.message}`);
      prayers[id] = [];
    }
    if (i < PRAYERS.length - 1) await sleep(250); // stay within rate limits
  }

  const today = new Date().toISOString().split('T')[0];
  const out = { refreshed: today, prayers };
  const outPath = path.join(process.cwd(), 'curated.json');
  fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
  console.log(`\nWritten ${outPath} (refreshed: ${today})`);
}

main().catch(e => { console.error(e); process.exit(1); });
