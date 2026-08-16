# Chen Kessler — Portfolio Site · Handoff

Written 15 Aug 2026 at the end of a long build session, for whoever picks this up next.
Read this before touching anything. It will save you from re-deriving decisions and
from re-breaking things that were already broken once.

---

## 1. What this is

A single-page portfolio for **Chen Kessler** — filmmaker, videographer and colourist,
based in Tel Aviv, studying at the **Sam Spiegel Film & Television School in Jerusalem**
(he corrected this mid-session; it is *not* Tel Aviv University).

- **Live:** https://chenkessler.com — served by **AWS Amplify**, not GitHub Pages.
  Route53 holds the zone; the four AWS name servers were set at the registrar on
  16 Aug 2026. `www` and the apex both resolve; http 301s to https.
- **Repo:** https://github.com/benkessler100-bit/PORTFOLIO (branch `main`).
  Amplify builds from `main`, so a push is a deploy. The old GitHub Pages URL
  still answers and is now pointed home by `rel=canonical`.
- **Amplify app:** `PORTFOLIO`, default URL `main.d2v3el4f35ivho.amplifyapp.com`.
- **The whole site is one file:** `index.html` — inline `<style>` and inline `<script>`,
  no build step, no framework, no dependencies.

> **Cost note.** Amplify bills egress at roughly $0.15/GB and this repo carries
> 614MB of video. GitHub Pages served the same files free. Watch the first
> month's bill before assuming this is settled.

### Design origin
Chen sent a Behance gallery as the reference:
`behance.net/gallery/239334841` — "PORTFOLIO VIDEOGRAPHER" by Muhammad Sandy Rizkyono.
Cream paper + forest green, torn-paper section transitions, a profile card, per-project
header blocks, a client logo wall. We rebuilt that language with **Chen's own work**,
then diverged where his content demanded it.

---

## 2. Current state — what is live

| Section | Contents |
|---|---|
| Hero | `Portfolio` wordmark with a cut-out FX3 rig floating in the gap |
| Statement | The single green band on the page |
| Profile | Photo card + film credits + commercial + education + tools + contact |
| Films | 5 shorts, each with real credits as pill tags, + Personal Projects |
| Brand Films | Racing, Master Grill/Malka, Event Planner, Fashion stills |
| Music & Live | Dan Odiz, Dor Shemer, Maya + live stills |
| Stills | Portrait and Travel, both justified galleries |
| Brands | 27 client logos as two opposing infinite marquees |
| Contact | Full-bleed travel frame + contact links |

**Section order is Chen's, not chronological, and he asked for it explicitly:**
- Films: **Lottem → Shalom Aba → Kaktusim → Ot Kayin → Erachim U'Medaliot**
- Music: **Dan Odiz → Dor Shemer → Maya**
- Brand: **Racing → Master Grill/Malka → Event Planner**

Assets: **~663MB** in `assets/v3/` — 23 videos, 9 portraits, 60 travel stills,
28 logos, plus fashion/food/live/bts/film stills.

---

## 3. Source of truth for media — read this before adding anything

**`/Volumes/My Book/PORTFOLIO/NEW PORTFOLIO/` — and only that folder.**

Chen curated it himself and said so in as many words: pull site material from nowhere
else. Everything in `assets/v3/` came from there. The parent `PORTFOLIO/` folder holds
the *older* curation that fed the retired site — do not mix them.

Structure:
```
NEW PORTFOLIO/
  BRANDS I WORKED WITH/   29 client logo PNGs
  FASHION/                stills + MALKA VID
  Portraits/              9 frames (4 Maya, 5 Ron Sabri) — he trimmed these
  SHOWS - LIve - Music/   clips, dance, live stills
  TRAVEL/                 58 stills + 4 clips (3 Mongolia drone, 1 Japan)
  cinema/                 Short Movies, bts, Personal projects
  סרטי תדמית/              brand films
  HERO REFERNCE/          screen recording of the Behance hero
```

**Two things in there are easy to miss and both matter:**

1. **The Short Movies folder names carry Chen's real credits.** e.g.
   `שלום, אבא - CAMERA CHIEF COLOR GRADING SOUND DESIGN`. Use those. Do not guess roles.
2. Everything is a **4K master** (single files up to 6GB). It all needs transcoding.

---

## 4. How the page is built

### Content is declared in attributes, expanded by inline JS
You rarely edit markup by hand. Grids are declared like this:

| Attribute | Meaning |
|---|---|
| `data-seq="folder/prefix\|1-8"` | a contiguous run of stills |
| `data-list="folder/prefix\|1,4,9"` | a hand-picked selection |
| `data-vid="name\|Label,name\|Label"` | a grid of players |
| `data-vid="name\|Label\|1.7778"` | third field = that clip's true aspect ratio |
| `data-shots="folder/prefix\|1:0.667,4:1.5"` | justified gallery, `index:ratio` pairs |
| `data-autoplay="always"` | this grid autoplays below the 760px cutoff too |

So adding work usually means editing **one attribute**.

### The three grid systems

1. **Plain grids** — `.g2 .g3 .g4` with fixed aspect classes (`.ar-169`, `.ar-34`…).
   For sets that share a shape.

2. **`.just`** — flex, shape-aware, for **mixed-orientation video** (Personal Projects).
   Each tile carries `--ar`; `flex-grow` and `flex-basis` are proportional to it, so a
   row lands at one height with nothing cropped.

3. **`.justg`** — a **real justified gallery**, laid out in JS (`layoutJustified`).
   Used for Portrait and Travel, whose frames run 0.667 → 2.0. It groups frames into
   rows, then sets exact pixel widths so every row spans the full width.

### Language — English / Hebrew, added 16 Aug 2026
The toggle sits in the hero bar. There is still **one HTML file**; Hebrew is
switched in at runtime and lives at `?lang=he`, which is a distinct URL so Google
can index and rank it separately (`hreflang` declares the pair, and `setLang`
rewrites `canonical`/`og:url` to whichever is active).

Translation is keyed off **the English text itself**, in the `HE` map at the top
of the script — so a string that repeats, like "Colour grading" ×4, is translated
once and there is no id to keep in sync with the markup. Two escape hatches:

- **`data-he="…"`** on an element whose *inner markup* matters — a `<br>` inside a
  heading, the `<em>` in the statement — wins over the map and replaces its whole
  subtree. Also used where one English word needs two different Hebrew words
  ("Contact" is nav / footer / phone-label in three places).
- **`HE_ATTR`** covers `aria-label`, `title` and `alt`; `META` covers `<title>`
  and the description.

Original text nodes are cached on first pass, so switching back to English
restores the source rather than a back-translation. RTL is a `[dir="rtl"]` block
at the very end of the stylesheet — **it must stay last**, several of its rules
tie with base rules on specificity.

**RTL traps already hit here:**
- **Poppins and Plus Jakarta Sans carry no Hebrew glyphs.** Every heading has to
  be reassigned to Rubik or it silently falls back to a system face.
- **Latin display tracking (`-.05em`) destroys Hebrew** — reset to 0. The wide
  tracking on uppercase micro-labels is worse: Hebrew has no case, so it just
  shreds the word. Reset those and drop `text-transform`.
- **Hebrew has no italic and Rubik ships no oblique**, so `font-style:italic`
  gets synthesised into a mechanical shear that reads as a rendering fault.
  Carry emphasis on weight instead.
- **Force `direction:ltr` on Latin islands** — the wordmark, the app badges, the
  phone number, the email. Otherwise bidi reorders "Portfolio" into "folioPort".
- **`.foot>img` and `.card>img` are direct-child selectors** and the `<picture>`
  wrapper (below) breaks them. `picture{display:contents}` keeps every rule
  written against the image's own box working, but `>` selectors still have to
  name the wrapper.

### Images — WebP, added 16 Aug 2026
Every still has a WebP twin from `tools/build-webp.py` (48MB → 19MB, 61% off;
the hero rig alone went 713KB → 91KB and it is the LCP element). They are served
through `<picture>`, so the original JPEG/PNG stays on disk as the fallback and
nothing breaks without WebP support. `build-img.sh` now calls the converter, so
new stills get their twin automatically — **if you add images by hand, run it,**
or `<picture>` quietly serves the heavy original.

### The loading screen
Counts the hero's own assets rather than `window.load` — on a 23,000px-tall page
`load` sits behind every lazy image. It self-releases after 4s so a stalled request
can never trap a visitor on the splash.

---

## 5. Traps — every one of these bit us already

**Verify layout by measuring, not by looking.** Screenshots hid three separate bugs
this session. `tools/audit.js` measures overflow, grid-child intersection, sub-11px
type and sub-40px tap targets. Run it at 320 / 375 / 768 / 1440.

- **`offsetWidth`, not `getBoundingClientRect()`,** when checking grid maths. The scroll
  reveal applies `scale(.978)`, which silently shrinks every measured rect by ~2% and
  makes a correct layout look broken.
- **`clientWidth` rounds up.** Summing widths against it overflows the real line box by
  a fraction, and flex drops the last item to the next row. Measure fractionally and
  keep half a pixel spare.
- **`:has()` carries its argument's specificity.** `.piece-head:has(.client)` outranked a
  plain `.piece-head` inside a media query, so client-logo blocks stayed three-column on
  phones. Name the `:has()` variant again in the override.
- **Media-query blocks must sit *after* the base rules.** Equal specificity means source
  order decides. Mobile hero rules were written correctly twice and had no effect.
- **`.hero .mark-foot` beats `.mark-foot`.** Two classes beat one. Match the weight.
- **Never put a click-to-toggle listener on a wrapper around `<video controls>`.** The
  scrub bar lives inside the element; the wrapper swallowed the clicks and dragging the
  playhead just paused the video.
- **Give every player its `src` on approach, not on click.** With `preload="none"` this
  costs nothing and means the browser's own play button works first press.
- **Only add `.playing` when `play()` resolves.** Hiding the badge optimistically leaves
  a stopped video with no visible way to start it when autoplay is refused.
- **Grid items with `grid-row: span N` against fixed `grid-auto-rows` overflow their
  track** when content has no fixed aspect ratio — with `dense` packing the overflow
  lands on top of later items. This was the "images on top of each other" bug.
- **Class-name collisions.** The loading screen's inner `.bar` inherited the top nav's
  `.bar` padding and rendered as a thick block. Renamed `.lbar`.
- **`python -m http.server` ignores Range**, so video seeking is dead locally and it
  looks exactly like a front-end bug. It is also single-threaded, so a streaming video
  starves every image behind it — that was "why aren't the images loading". Use
  `tools/serve.py` (Range-capable, threaded). GitHub Pages handles both correctly.

---

## 6. Chen's preferences, learned the hard way

- **Big videos, few grids.** He rejected a denser layout outright.
- **Cream-led, green as an accent.** One green band plus the footer. He asked for the
  green to come down.
- **Clean even grids.** He called a zero-gap mosaic "בלאגן אטומי" and it was removed.
- **Don't stack several structural changes before he has seen any of them.** Propose,
  then build one thing at a time.
- **One name per language — superseded the festival-style stacking on 16 Aug 2026.**
  The page used to show the Hebrew title with the transliteration beneath, because
  there was a single page serving both readers. Once the toggle shipped Chen was
  explicit: *"אם הוספנו טוגל שפות אז שהאנגלית יהיה רק אנגלית."* So every
  Hebrew-titled work now carries `.he` **and** `.ltr-name`, and CSS shows whichever
  matches `dir`. Do not reintroduce the stack.
  Hebrew still needs **Rubik** (Poppins and Plus Jakarta Sans have no Hebrew glyphs)
  and `lang="he" dir="rtl"` + `unicode-bidi:isolate`, or "שלום, אבא" puts its comma
  on the wrong side.
- **He iterates fast and reverses himself.** He asked for a staggered wordmark, then
  centred, then staggered again the other way. Just measure and follow.

---

## 7. Tooling — `tools/`

| File | What it does |
|---|---|
| `serve.py` | Range-capable **threaded** dev server. `.claude/launch.json` points here. |
| `logos.py` | Rebuilds the client logo wall from the drive. See §8. |
| `build-img.sh` | Copies + resizes stills from NEW PORTFOLIO into `assets/v3/img`. |
| `build-video.sh` | Transcodes the 4K masters. Bitrate-targeted to clear GitHub's 100MB limit. |
| `tvenc.sh` | The travel clips specifically. |
| `build-webp.py` | WebP twin for every still. Called by `build-img.sh`; needs Pillow. |
| `build-sitemap.py` | Rebuilds `sitemap.xml` from the gallery attributes in `index.html`. **Rerun it after changing any `data-seq`/`data-list`/`data-shots`.** |
| `cutout.swift` | macOS Vision subject-lifting → transparent PNG. `swiftc -O cutout.swift -o cutout` |
| `audit.js` | Paste into the console to measure a viewport. |

**Run the preview:**
```bash
python3 tools/serve.py 8013 .
```

---

## 8. The logo wall — the fiddliest part of the build

27 client logos, all rendered in **one green ink**, as two opposing marquees.

Flattening every logo to a single ink **destroys some of them**: Sparco is white type
knocked out of a blue bar; Drift King is a full-colour car illustration. So `logos.py`
classifies each source by the tonal spread of its visible pixels:

- **spread ≤ 36 → "flat"** — masks to one ink losslessly (16 of them)
- **more → "full"** — needs its layers separated first

For "full" logos the rule that makes it work is **whether a light area is enclosed by
ink**. Sparco's white type is trapped inside its blue bar, so it must punch through as a
hole; Bodymania's white "MANIA" sits on open transparency, so it *is* ink and must stay.
Implemented as a flood fill inwards from the transparent surround.

Special cases hard-coded in the script: `flatout-racing`, `be-live`, `goldstar` need a
forced background key; `nook-social-app` is white artwork that vanishes on cream so it is
forced to ink; `goldstar`'s plaque is the outermost shape so it takes alpha from darkness
instead; `street-festival` is a photo, not a logo — skipped.

---

## 9. Deploying and rolling back

```bash
git add -A && git commit -m "..." && git push origin main
```
Amplify builds on push, 1–2 min. Verify with a real request, not just the push:
```bash
curl -s -o /dev/null -w "%{http_code}\n" https://chenkessler.com/
```

**Rollback point for the old site:** tag `pre-relaunch-2026-08-15`.
```bash
git checkout pre-relaunch-2026-08-15 -- .
```
That restores the retired split-gate site (`index/commercial/art` + `assets/img` +
`assets/video`, ~830MB). Nothing was rewritten out of history.

`folio.html` still exists as a redirect to `/` — the page lived there before it became
the homepage, and links to it are still in the wild.

---

## 10. SEO — what is in place, and what is still Chen's to do

Added 16 Aug 2026: `robots.txt`, an **image sitemap** covering all 49 displayed
stills on both language URLs (generated — see `build-sitemap.py`; it exists
because every gallery is JS-injected, and image discovery through rendering is
the least reliable path Google has), JSON-LD (`Person` + `ProfessionalService` +
`WebSite`, plus a `VideoObject` per player), real `alt` text on every gallery
image, full OG/Twitter card tags, and the Hebrew URL above.

The `VideoObject` set is **generated from the players on the page**, so a clip
added through `data-vid` describes itself with no second list to update.
Durations are parsed back out of the copy — "· 0:34", "· 3 min" — for the same
reason. Two things to know about that:

- **A tagged tile must not read the heading's runtime.** Tiles carrying a `.tag`
  are separate clips under a shared heading; before this was fixed, Moonlighting
  inherited Maya's 0:31. Only an article's main player reads the `.lat`.
- **`uploadDate` is the site's publish date for all of them.** Real production
  dates go in the `SHOT_ON` map at the top of that block, keyed by file stem —
  one line each. It is one of the four properties Google *requires* for a video
  rich result, so real dates are worth collecting from Chen.

Fonts load non-blocking (`media="print"` promoted on load, with a `<noscript>`
fallback). Contact links were taken to ≥40px tap targets and the smallest type
to 11px; **the hero nav was deliberately left compact** — 40px there adds ~17px
to the wordmark bar, and that lockup is Chen's call, not a maintenance decision.

Alt text comes from `ALT` (a sentence per folder) and `ALTX` (per-frame override,
one line each). The nine portraits are named; **the other sets still describe
themselves generically, and Chen is the only one who knows what is actually in
each frame** — adding a real line per travel still is the single cheapest
remaining win, because image search is a genuine traffic channel for a
photographer.

Still outstanding, and needing Chen or the AWS console:

1. **Search Console** — verify `chenkessler.com`, submit the sitemap. Nothing
   else on this list matters until Google is actually looking.
2. **www → apex 301.** Both hostnames serve the site today. `canonical` covers
   it for Google, but a real redirect belongs in Amplify →
   Hosting → Rewrites and redirects. Amplify has **no repo-side redirects file**,
   so this cannot be committed — it is console-only.
3. **`folio.html`** answers 200 with a meta-refresh. It now carries
   `noindex, follow`, which solves the duplicate; a real 301 would be better and
   is the same console screen.
4. **Google Business Profile** — free, local, and he has no listing.
5. **Inbound links** — clients, festivals, Sam Spiegel. Still the strongest
   single factor and the one no amount of markup substitutes for.
6. **One URL is the ceiling.** Every film shares `/`, so "שלום, אבא" and
   "אות קין" cannot rank separately. Splitting into a page per film is a real
   structural change and was deliberately *not* done — propose it before building it.

## 11. Open items

1. **Repo weight.** `.git` was ~1GB before this session and `assets/v3` added 600MB+.
   Deleting the old `assets/` from the working tree did **not** shrink history — that
   needs a `git filter-repo` rewrite, or moving video off-repo (Vimeo/CDN). Five files
   are over GitHub's recommended 50MB (all under the 100MB hard limit).
2. **Travel clips do not autoplay on phones.** They are 20–24MB each; four of them is
   ~90MB on a mobile connection. Chen was offered either enabling it as-is or cutting
   them to 10–15s loops first. He has not answered.
3. **No before/after grade slider.** It was proposed and he liked it, but it needs an
   **ungraded frame export** from Ot Kayin, which does not exist on the drive. Ask him
   for one raw/LOG still and it is about fifteen minutes of work.
4. **`portfolio.html` and `v2/`** sit untracked in the working directory. Leftovers from
   earlier sessions, not live, never committed. Probably deletable — ask.
5. **`assets/v3/img/camera-rig.png`** is the current hero. Earlier alternatives are gone
   from the tree but recoverable from history if he wants the photographed BTS rig back.

---

## 12. Things Chen asked for that were declined, and why

- **Running his Gemini API key.** He pasted a live key in chat and asked twice for it to
  be used directly. Declined both times — API keys are not handled in plain text. He was
  given `gen-rig.sh` (in the old scratchpad; regenerate if needed) which prompts for the
  key with echo off. **He was told to revoke that key. Confirm he did.**
- **AI image generation.** No image tool is available in this environment and the Adobe
  connectors are unauthorized. Chen generated the FX3 rig image himself and dropped it in
  the drive as `Generated Image August 15, 2026 - 7_59PM.jpg`.
