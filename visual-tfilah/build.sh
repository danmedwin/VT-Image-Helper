#!/usr/bin/env bash
# Rebuild the Davis Kabbalat Shabbat VT deck from the Davis VT template.
#
#   ./build.sh path/to/"New VT Template (in progress w Claude).pptx" [outfile]
#
# Structure first (duplicate the template's authoring slide once per content
# slide, set the running order, drop everything else), then fill-davis-vt.py
# pours in the liturgy.
set -euo pipefail

TEMPLATE="${1:?usage: build.sh TEMPLATE.pptx [OUT.pptx]}"
OUT="${2:-Davis-Kabbalat-Shabbat-VT-v1a.pptx}"
SKILL=/root/.claude/skills/synced/pptx/scripts

# 13 content slides between the Davis title slide and the Davis closing slide.
CONTENT=13

rm -rf unpacked working.pptx
python3 -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall('unpacked')" "$TEMPLATE"

# slide5.xml is the authoring slide: two columns, service sidebar, translation bar.
for _ in $(seq 2 "$CONTENT"); do
  python3 "$SKILL/add_slide.py" unpacked/ slide5.xml >/dev/null
done

python3 - "$CONTENT" <<'PY'
import re, sys
n = int(sys.argv[1])
rels = open('unpacked/ppt/_rels/presentation.xml.rels').read()
target = dict((t, i) for i, t in
              re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', rels))
# the duplicates land at the end, numbered after the template's 47 slides
order = ['slide1.xml', 'slide5.xml'] + \
        [f'slide{47 + i}.xml' for i in range(1, n)] + ['slide47.xml']
x = open('unpacked/ppt/presentation.xml').read()
old = re.search(r'<p:sldIdLst>.*?</p:sldIdLst>', x, re.S).group(0)
new = '<p:sldIdLst>' + ''.join(
    f'<p:sldId id="{256+i}" r:id="{target[s]}"/>' for i, s in enumerate(order)
) + '</p:sldIdLst>'
open('unpacked/ppt/presentation.xml', 'w').write(x.replace(old, new))
print(f'ordered {len(order)} slides')
PY

python3 "$SKILL/clean.py" unpacked/ >/dev/null
(cd unpacked && zip -Xrq ../working.pptx .)
rm -rf unpacked

python3 fill-davis-vt.py "$OUT"
python3 "$SKILL/office/validate.py" "$OUT" --original "$TEMPLATE"
