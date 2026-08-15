#!/bin/bash
# Transcode the NEW PORTFOLIO masters down to web-sized h264 + poster frames.
SRC="/Volumes/My Book/PORTFOLIO/NEW PORTFOLIO"
OUT="/Users/chenkessler/Downloads/devinci claude mcp/assets/v3/video"
POST="$OUT/posters"
mkdir -p "$POST"

# enc <src> <slug> <scale-filter> <bitrate|crf:NN> <poster-seek>
enc () {
  local src="$1" slug="$2" vf="$3" rate="$4" seek="$5"
  local dst="$OUT/$slug.mp4"
  if [ -f "$dst" ]; then echo "skip $slug"; return; fi
  local ropts
  if [[ "$rate" == crf:* ]]; then
    ropts="-crf ${rate#crf:}"
  else
    ropts="-b:v $rate -maxrate $((${rate%k} * 3 / 2))k -bufsize $((${rate%k} * 3))k"
  fi
  echo ">> $slug"
  ffmpeg -hide_banner -loglevel error -y -hwaccel videotoolbox -i "$src" \
    -vf "$vf" -c:v libx264 -preset medium -pix_fmt yuv420p $ropts \
    -c:a aac -b:a 96k -ac 2 -movflags +faststart "$dst" || { echo "FAIL $slug"; return; }
  ffmpeg -hide_banner -loglevel error -y -ss "$seek" -i "$dst" -frames:v 1 -q:v 3 "$POST/$slug.jpg"
  echo "   $(du -m "$dst" | cut -f1)MB  $slug"
}

W="scale=1280:-2"      # wide films
W16="scale=1920:-2"    # wide short pieces
V="scale=1080:-2"      # vertical pieces

# ---- short films (bitrate-targeted to stay well under GitHub's 100MB/file) ----
enc "$SRC/cinema/Short Movies /שלום, אבא - CAMERA CHIEF COLOR GRADING SOUND DESIGN/שלום אבא - תיקונים אחרונים .mp4" shalom-aba "$W" 900k 60
enc "$SRC/cinema/Short Movies /ערכים ומדליות - EDITOR COLORGRADING SOUND DESIGN/ערכים ומדליות.mp4" erachim-medaliot "$W" 850k 60
enc "$SRC/cinema/Short Movies /אות קין - COLORGRADING/אות קין - צביעה חן.mp4" ot-kayin "$W" 1300k 45
enc "$SRC/cinema/Short Movies /קקטוסים - CAMERA CHIEF COLORGRADING/KAKTUSES FINAL CUT AND SUB.mp4" kaktusim "$W" 1500k 40
enc "$SRC/cinema/Short Movies /Short Doco - FILM EDITOR DIRECTOR SCRIPT/לוטם - דוקו.mp4" lottem-doco "$W" 2200k 30

# ---- brand / corporate films ----
enc "$SRC/סרטי תדמית/EVENT PLANNER.mp4" event-planner "$W16" crf:25 12
enc "$SRC/סרטי תדמית/MASTER GRILL MAN CHEF.mp4" grill-chef "$V" crf:25 10
enc "$SRC/סרטי תדמית/RACING CHAMPIONSHIP.mp4" racing-championship "$W16" crf:25 6

# ---- music, live, dance ----
enc "$SRC/SHOWS - LIve - Music/קליפים וטיזרים לשירים/דור שמר - תמונה בלי שם.mp4" dor-shemer "$W16" crf:27 25
enc "$SRC/SHOWS - LIve - Music/קליפים וטיזרים לשירים/מאיה כביסה מלוכלת  REEL COLOR _V1-0006.mp4" maya-reel "$V" crf:25 5
enc "$SRC/SHOWS - LIve - Music/קליפים וטיזרים לשירים/מאיה כביסה מלוכלת COLOR _V1-0001.mp4" maya-wide "$W16" crf:25 5
enc "$SRC/SHOWS - LIve - Music/קליפים וטיזרים לשירים/MOONLIGHTING V1.mp4" moonlighting "$V" crf:25 8
enc "$SRC/SHOWS - LIve - Music/ריקודים/Dan Odiz - Long Preformance.mp4" dan-odiz "$W16" crf:26 12

# ---- fashion ----
enc "$SRC/FASHION/MALKA VID 1.mp4" malka "$V" crf:25 4

# ---- personal micro-films ----
enc "$SRC/cinema/Personal porjects - shot form film/ABCD.mp4" pp-abcd "$V" crf:25 3
enc "$SRC/cinema/Personal porjects - shot form film/BALANCE V3.mp4" pp-balance "$W16" crf:25 3
enc "$SRC/cinema/Personal porjects - shot form film/BREAK THE PATTERN.mp4" pp-break-the-pattern "$W16" crf:25 3
enc "$SRC/cinema/Personal porjects - shot form film/KEEP PUSHING.mp4" pp-keep-pushing "$W16" crf:25 4
enc "$SRC/cinema/Personal porjects - shot form film/YOUNG ME NO TEXT.mp4" pp-young-me "$W16" crf:25 4

echo "=== DONE ==="
du -sh "$OUT"
ls -la "$OUT" | tail -25
