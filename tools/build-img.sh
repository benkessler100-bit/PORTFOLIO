#!/bin/bash
# Copy + downsize the NEW PORTFOLIO stills, and the client logos, into assets/v3.
SRC="/Volumes/My Book/PORTFOLIO/NEW PORTFOLIO"
OUT="/Users/chenkessler/Downloads/devinci claude mcp/assets/v3/img"

# grab <src-file> <section> <slug>   — resize long edge to 1800px
grab () {
  local src="$1" sec="$2" slug="$3"
  mkdir -p "$OUT/$sec"
  cp "$src" "$OUT/$sec/$slug.jpg" 2>/dev/null || return
  sips -Z 1800 "$OUT/$sec/$slug.jpg" >/dev/null 2>&1
}

# ---- fashion / brand stills ----
i=1; for f in "Artboard 2" "Artboard 9" "Artboard 12" "CHICODE-109" "CHICODE-111" "CHICODE PURIM 2026-30" "DSC03367" "DSC04396"; do
  grab "$SRC/FASHION/$f.jpg" fashion "$(printf 'fashion-%02d' $i)"; i=$((i+1))
done
i=1; for f in "Makisu-225" "Makisu-310"; do
  grab "$SRC/FASHION/$f.jpg" food "$(printf 'food-%02d' $i)"; i=$((i+1))
done

# ---- portraits ----
i=1; for f in "MAYA STILLS-3" "MAYA STILLS-5" "MAYA STILLS-6" "MAYA STILLS-9" "MAYA STILLS-24" "MAYA STILLS-39" "MAYA STILLS-41" "MAYA STILLS-45" "MAYA STILLS-52"; do
  grab "$SRC/Portraits/$f.jpg" portrait "$(printf 'portrait-%02d' $i)"; i=$((i+1))
done
for f in "RON SABRI-7" "RON SABRI-8" "RON SABRI-10" "RON SABRI-11" "RON SABRI-14" "RON SABRI-24"; do
  grab "$SRC/Portraits/$f.jpg" portrait "$(printf 'portrait-%02d' $i)"; i=$((i+1))
done

# ---- live shows ----
i=1; for f in "DSC07470" "DSC08838" "אגם הופעה מיוזיק סיטי9" "אגם הופעה מיוזיק סיטי11" "אגם הופעה מיוזיק סיטי18" "אגם הופעה מיוזיק סיטי20" "אגם הופעה מיוזיק סיטי21" "אגם הופעה מיוזיק סיטי23" "אגם הופעה מיוזיק סיטי26" "אגם הופעה מיוזיק סיטי27" "אגם הופעה מיוזיק סיטי29" "אגם הופעה מיוזיק סיטי31"; do
  grab "$SRC/SHOWS - LIve - Music/תמונות הופעות/$f.jpg" live "$(printf 'live-%02d' $i)"; i=$((i+1))
done

# ---- travel (everything; culled later once I can see them) ----
i=1
for f in "$SRC/TRAVEL"/*.[jJ][pP][gG]; do
  [ -f "$f" ] || continue
  case "$(basename "$f")" in ._*) continue;; esac
  grab "$f" travel "$(printf 'travel-%02d' $i)"; i=$((i+1))
done

# ---- cinema: bts + film stills ----
i=1; for f in "$SRC/cinema/bts"/*; do
  case "$(basename "$f")" in ._*) continue;; esac
  grab "$f" bts "$(printf 'bts-%02d' $i)"; i=$((i+1))
done
i=1; for f in "$SRC/cinema/Short Movies /שלום, אבא - CAMERA CHIEF COLOR GRADING SOUND DESIGN"/*.png; do
  case "$(basename "$f")" in ._*) continue;; esac
  mkdir -p "$OUT/film-shalom-aba"
  sips -s format jpeg -Z 1800 "$f" --out "$OUT/film-shalom-aba/$(printf 'shalom-aba-%02d' $i).jpg" >/dev/null 2>&1
  i=$((i+1))
done
i=1; for f in "$SRC/cinema/Short Movies /אות קין - COLORGRADING"/*.jpg; do
  case "$(basename "$f")" in ._*) continue;; esac
  grab "$f" film-ot-kayin "$(printf 'ot-kayin-%02d' $i)"; i=$((i+1))
done

# ---- client logos: keep alpha, cap height ----
mkdir -p "$OUT/logos"
python3 - <<'PY'
import os, re, subprocess
src = "/Volumes/My Book/PORTFOLIO/NEW PORTFOLIO/BRANDS I WORKED WITH"
out = "/Users/chenkessler/Downloads/devinci claude mcp/assets/v3/img/logos"
for f in sorted(os.listdir(src)):
    if f.startswith("._") or not f.lower().endswith(".png"):
        continue
    slug = re.sub(r'[^a-z0-9]+', '-', os.path.splitext(f)[0].lower()).strip('-')
    subprocess.run(["sips", "-Z", "420", os.path.join(src, f),
                    "--out", os.path.join(out, slug + ".png")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(slug)
PY

# The page serves stills through <picture>, so every JPEG/PNG written above needs
# its WebP twin or the browser silently falls back to the heavy original.
echo "=== webp ==="
python3 "$(dirname "$0")/build-webp.py"

echo "=== counts ==="
for d in "$OUT"/*/; do printf "%-28s %s\n" "$(basename "$d")" "$(ls "$d" | wc -l | tr -d ' ')"; done
du -sh "$OUT"
