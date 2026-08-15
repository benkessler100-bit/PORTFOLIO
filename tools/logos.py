#!/usr/bin/env python3
"""Rebuild the client logo wall from the original sources.

Two kinds of file are mixed in that folder and they need opposite treatment:

  flat  - artwork that is one single tone on transparency (most of the
          wordmarks). Masking these to a single ink is lossless and gives the
          tidy one-colour wall.
  full  - full-colour illustrations, or artwork with knocked-out text sitting
          on a filled block (Sparco's white type on its blue bar, Drift King's
          car). Masking these destroys them, so they stay real images; any
          opaque background gets flood-removed from the border inwards.
"""
import json, os, glob, re, colorsys
from collections import deque
from PIL import Image

SRC = "/Volumes/My Book/PORTFOLIO/NEW PORTFOLIO/BRANDS I WORKED WITH"
OUT = "/Users/chenkessler/Downloads/devinci claude mcp/assets/v3/img/logos"
os.makedirs(OUT, exist_ok=True)

def slug(f):
    s = re.sub(r'[^a-z0-9]+', '-', os.path.splitext(f)[0].lower()).strip('-')
    return {"": "goldstar", "2x": "jessica"}.get(s, s)

def visible(im):
    a = im.getchannel("A"); l = im.convert("L")
    return [p for p, al in zip(l.getdata(), a.getdata()) if al > 120]

def strip_background(im):
    """Flood the opaque background in from the border with a colour tolerance."""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    opaque = [c for c in corners if c[3] > 200]
    if len(opaque) < 3:
        return im, False
    r0 = sum(c[0] for c in opaque) / len(opaque)
    g0 = sum(c[1] for c in opaque) / len(opaque)
    b0 = sum(c[2] for c in opaque) / len(opaque)
    if max(abs(c[0] - r0) + abs(c[1] - g0) + abs(c[2] - b0) for c in opaque) > 70:
        return im, False                       # corners disagree: not a flat bg

    tol = 62
    seen = bytearray(w * h)
    q = deque()
    for x in range(w):
        q.append((x, 0)); q.append((x, h - 1))
    for y in range(h):
        q.append((0, y)); q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        i = y * w + x
        if seen[i]:
            continue
        seen[i] = 1
        r, g, b, a = px[x, y]
        if a > 8 and abs(r - r0) + abs(g - g0) + abs(b - b0) > tol:
            continue                            # hit the artwork, stop here
        px[x, y] = (r, g, b, 0)
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx]:
                q.append((nx, ny))
    return im, True

def key_light_box(im):
    """Some files are artwork sitting on a solid light rectangle inside a
    transparent margin, so the border flood never reaches it. Sample the ring
    of the trimmed artwork; if it is uniformly light, key that colour out."""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    ring = []
    for x in range(w):
        for y in (0, 1, h - 2, h - 1):
            if 0 <= y < h: ring.append(px[x, y])
    for y in range(h):
        for x in (0, 1, w - 2, w - 1):
            if 0 <= x < w: ring.append(px[x, y])
    ring = [c for c in ring if c[3] > 200]
    if len(ring) < (w + h):
        return im, False
    r0 = sum(c[0] for c in ring) / len(ring)
    g0 = sum(c[1] for c in ring) / len(ring)
    b0 = sum(c[2] for c in ring) / len(ring)
    close = sum(1 for c in ring
                if abs(c[0]-r0) + abs(c[1]-g0) + abs(c[2]-b0) < 60) / len(ring)
    if close < .9 or (r0 + g0 + b0) / 3 < 214:
        return im, False
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            d = abs(r - r0) + abs(g - g0) + abs(b - b0)
            if d < 46:
                px[x, y] = (r, g, b, 0)
            elif d < 96:
                px[x, y] = (r, g, b, int(a * (d - 46) / 50))
    return im, True

def trim(im):
    bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    return im.crop(bb) if bb else im

# auto-detection is right for most of the set; these few need to be told.
# their background box is inside a transparent margin and doesn't form a clean
# ring, so the generic test can't see it.
FORCE_KEY  = {"flatout-racing", "be-live", "goldstar"}
FORCE_FLAT = {"nook-social-app"}      # white artwork: invisible on cream unless inked
SKIP       = {"street-festival"}      # a photo, not a logo
# goldstar is dark artwork printed on a solid plaque: the plaque is the outer
# shape, so the "enclosed highlight" rule can't see it as background. Take the
# alpha straight from darkness instead and the star and type come out clean.
FORCE_INK  = {"goldstar"}

def key_dominant(im, min_lum=150, tol=58):
    """Key out the single most common opaque colour when it is a flat box."""
    im = im.convert("RGBA")
    counts = {}
    for (r, g, b, a) in im.getdata():
        if a > 200:
            k = (r // 8, g // 8, b // 8)
            counts[k] = counts.get(k, 0) + 1
    if not counts:
        return im
    (r0, g0, b0) = [c * 8 + 4 for c in max(counts, key=counts.get)]
    if (r0 + g0 + b0) / 3 < min_lum:
        return im
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            d = abs(r - r0) + abs(g - g0) + abs(b - b0)
            if d < tol:
                px[x, y] = (r, g, b, 0)
            elif d < tol + 50:
                px[x, y] = (r, g, b, int(a * (d - tol) / 50))
    return im

manifest = []
for f in sorted(os.listdir(SRC)):
    if f.startswith("._") or not f.lower().endswith((".png", ".jpg")):
        continue
    name = slug(f)
    if name in SKIP:
        continue
    im = Image.open(os.path.join(SRC, f)).convert("RGBA")

    im, removed = strip_background(im)
    im = trim(im)
    im, keyed = key_light_box(im)
    if name in FORCE_KEY:
        # goldstar's plaque is a mid-tone gold, below the usual light-box floor
        # goldstar's plaque is a mid-tone gold *gradient*, so it needs both a
        # lower lightness floor and a much wider colour tolerance
        im = (key_dominant(im, 96, 132) if name == "goldstar" else key_dominant(im))
        keyed = True
    im = trim(im)
    removed = removed or keyed

    vis = visible(im)
    if not vis:
        print("!! empty after processing:", f); continue
    spread = max(vis) - min(vis)
    mean = sum(vis) / len(vis)

    # colourfulness of the visible artwork
    small = im.copy(); small.thumbnail((90, 90))
    sats = []
    for (r, g, b, a) in small.getdata():
        if a > 120:
            sats.append(colorsys.rgb_to_hls(r/255, g/255, b/255)[2])
    chroma = (sum(1 for s in sats if s > .28) / len(sats)) if sats else 0

    kind = "flat" if (spread <= 36 or name in FORCE_FLAT) else "full"

    # ---- one ink for the whole wall ----
    # A single-tone file masks straight across: its alpha already *is* the ink.
    # A multi-tone file needs its layers separated, but only where a light area
    # is genuinely a knockout. The test is whether that light area is enclosed
    # by ink: Sparco's white "sparco" is trapped inside its blue bar, so it must
    # punch through; Bodymania's white "MANIA" and DVDent's purple "DVD" sit on
    # open transparency, so they *are* ink and have to stay. Flood inwards from
    # the transparent surround through the light pixels — whatever the flood
    # reaches is standalone artwork, whatever it cannot reach is a knockout.
    if name in FORCE_INK:
        lum = im.convert("L")
        lo, hi = min(vis), max(vis)
        span = max(hi - lo, 1)
        ink = lum.point(lambda v: max(0, min(255, int(255 * (hi - v) / span))))
        ink = ink.point(lambda v: 0 if v < 60 else min(255, int((v - 60) * 255 / 120)))
        im.putalpha(ink)
        im = trim(im)
    elif kind == "full":
        w2, h2 = im.size
        px2 = im.load()
        lum = im.convert("L")
        L = lum.load()
        lo, hi = min(vis), max(vis)
        span = max(hi - lo, 1)
        cut = lo + span * 0.55                      # above this counts as "light"

        opaque = bytearray(w2 * h2)
        light  = bytearray(w2 * h2)
        for y in range(h2):
            for x in range(w2):
                i = y * w2 + x
                if px2[x, y][3] > 120:
                    opaque[i] = 1
                    if L[x, y] > cut:
                        light[i] = 1

        reach = bytearray(w2 * h2)                  # light pixels open to the outside
        q = deque()
        for x in range(w2):
            for y in (0, h2 - 1):
                if not opaque[y * w2 + x]: q.append((x, y))
        for y in range(h2):
            for x in (0, w2 - 1):
                if not opaque[y * w2 + x]: q.append((x, y))
        seen2 = bytearray(w2 * h2)
        while q:
            x, y = q.popleft()
            i = y * w2 + x
            if seen2[i]: continue
            seen2[i] = 1
            if opaque[i] and not light[i]:
                continue                            # ink blocks the flood
            if light[i]: reach[i] = 1
            for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if 0 <= nx < w2 and 0 <= ny < h2 and not seen2[ny*w2+nx]:
                    q.append((nx, ny))

        a = im.getchannel("A")
        src_a = a.load()
        newa = Image.new("L", im.size)
        put = newa.load()
        for y in range(h2):
            for x in range(w2):
                i = y * w2 + x
                al = src_a[x, y]
                if not al:
                    put[x, y] = 0
                elif light[i] and not reach[i]:
                    put[x, y] = 0                   # enclosed highlight: knock it out
                else:
                    put[x, y] = al                  # everything else is ink
        im.putalpha(newa)
        im = trim(im)

    im.thumbnail((560, 560), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".png"))
    manifest.append({"slug": name, "kind": kind, "light": mean > 168,
                     "w": im.width, "h": im.height})
    print(f"{kind:5} {'bg-removed' if removed else '          '} "
          f"spread {spread:3d} chroma {chroma:.2f} mean {mean:5.1f}  {name}")

json.dump(manifest, open("/private/tmp/claude-501/-Users-chenkessler-Downloads-devinci-claude-mcp/18ef61fe-1240-414d-ac0b-cbf3f4d0f4f4/scratchpad/logos.json", "w"), indent=1)
print("\nflat:", sum(1 for m in manifest if m["kind"] == "flat"),
      " full:", sum(1 for m in manifest if m["kind"] == "full"))
