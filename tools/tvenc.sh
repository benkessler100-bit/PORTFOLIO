#!/bin/bash
SRC="/Volumes/My Book/PORTFOLIO/NEW PORTFOLIO/TRAVEL"
OUT="/Users/chenkessler/Downloads/devinci claude mcp/assets/v3/video"
enc(){ ffmpeg -hide_banner -loglevel error -y -hwaccel videotoolbox -i "$1" \
  -vf "scale=1280:-2" -c:v libx264 -preset medium -pix_fmt yuv420p \
  -b:v "$3" -maxrate $(( ${3%k}*3/2 ))k -bufsize $(( ${3%k}*3 ))k \
  -c:a aac -b:a 96k -ac 2 -movflags +faststart "$OUT/$2.mp4"
  ffmpeg -hide_banner -loglevel error -y -ss "$4" -i "$OUT/$2.mp4" -frames:v 1 -q:v 3 "$OUT/posters/$2.jpg"
  echo "  $(du -m "$OUT/$2.mp4" | cut -f1)MB $2"; }
enc "$SRC/1719768233365.MOV" travel-mongolia-1 1700k 8
enc "$SRC/1722051858715.MOV" travel-mongolia-2 1700k 10
enc "$SRC/1720509301957.mov" travel-mongolia-3 1700k 6
enc "$SRC/copy_CD9D5F76-D0E0-4448-A57D-5953281F31D9.mov" travel-japan 1800k 3
echo DONE
