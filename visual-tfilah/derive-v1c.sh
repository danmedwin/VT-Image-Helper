#!/bin/bash
# Build v1c from Dan's v1a.
#
# v1c descends from Dan's v1a, NOT from the template. build.sh regenerates every
# content slide from scratch and would discard Dan's Rocks slide, his title
# slide, and his Kiddush text — see README. This is the path that keeps them.
#
#   ./derive-v1c.sh "~/Documents/Davis Files/Davis VT/DavisKabbalatShabbatVTv1a.pptx" [OUT.pptx]
set -euo pipefail

SRC="${1:?usage: derive-v1c.sh V1A.pptx [OUT.pptx]}"
OUT="${2:-Davis-Kabbalat-Shabbat-VT-v1c.pptx}"
HERE="$(cd "$(dirname "$0")" && pwd)"
# The pptx skill ships inside Claude's per-session skills-plugin tree, so its path
# moves. Take PPTX_SKILL if set, otherwise find the newest copy on disk.
PPTX="${PPTX_SKILL:-$(find "$HOME/Library/Application Support/Claude" -type d -name pptx -path '*/skills/*' 2>/dev/null | tail -1)}"
if [ ! -f "${PPTX:-/nonexistent}/scripts/clean.py" ]; then
  echo "Cannot find the pptx skill. Set PPTX_SKILL=/path/to/skills/pptx and re-run." >&2
  exit 1
fi
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

python3 -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$SRC" "$WORK"

# Slide 4 is the one-time 152 MB "2026-2027 WE ARE READY" video. Dan asked for it
# out of the archival deck; drop it in Cristy's video again next time it is needed.
python3 - "$WORK" <<'PY'
import re, sys
p = f"{sys.argv[1]}/ppt/presentation.xml"
x = open(p, encoding="utf-8").read()
rels = open(f"{sys.argv[1]}/ppt/_rels/presentation.xml.rels", encoding="utf-8").read()
rmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', rels))
gone = [e for e in re.findall(r"<p:sldId[^>]*/>", x)
        if rmap[re.search(r'r:id="(rId\d+)"', e).group(1)] == "slide4.xml"]
assert len(gone) == 1, gone
open(p, "w", encoding="utf-8").write(x.replace(gone[0], ""))
PY

python3 "$HERE/fix_kiddush.py" "$WORK"
python3 "$HERE/prune_rels.py" "$WORK"
python3 "$PPTX/scripts/clean.py" "$WORK"
python3 "$HERE/pack.py" "$WORK" "$OUT" "$SRC"
python3 "$PPTX/scripts/office/validate.py" "$OUT" --original "$SRC"
