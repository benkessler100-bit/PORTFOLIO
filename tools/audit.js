(function () {
  // force every reveal so we measure the settled layout, not mid-animation
  document.querySelectorAll('.rv, .vid.player').forEach(function (e) { e.classList.add('in'); });
  document.querySelectorAll('.stagger>*').forEach(function (k) {
    k.classList.add('in'); k.style.transitionDelay = '0ms';
  });
  document.querySelectorAll('.head, .piece-head, .collab, .state, .foot')
    .forEach(function (e) { e.classList.add('wiped'); });

  var W = window.innerWidth, out = { width: W, issues: {} };
  var add = function (k, v) { (out.issues[k] = out.issues[k] || []).push(v); };
  var name = function (el) {
    return el.tagName.toLowerCase() +
      (el.className && typeof el.className === 'string'
        ? '.' + el.className.trim().split(/\s+/).slice(0, 3).join('.') : '') +
      (el.id ? '#' + el.id : '');
  };

  // 1. page-level horizontal overflow
  out.scrollWidth = document.documentElement.scrollWidth;
  if (out.scrollWidth > W + 1) { add('pageOverflow', out.scrollWidth - W); }

  // 2. any element sticking out past the viewport
  document.querySelectorAll('body *').forEach(function (el) {
    if (!el.offsetParent && getComputedStyle(el).position !== 'fixed') { return; }
    var r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) { return; }
    if (r.right > W + 2) { add('stickingOut', name(el) + ' +' + Math.round(r.right - W)); }
    if (r.left < -2 && getComputedStyle(el).position !== 'fixed') {
      add('offLeft', name(el) + ' ' + Math.round(r.left));
    }
  });

  // 3. grid children overlapping each other
  document.querySelectorAll('.media, .logos, .tools, .profile').forEach(function (g) {
    var kids = [].slice.call(g.children).map(function (k) { return k.getBoundingClientRect(); });
    var over = 0;
    for (var i = 0; i < kids.length; i++) {
      for (var j = i + 1; j < kids.length; j++) {
        var a = kids[i], b = kids[j];
        if (a.left < b.right - 1 && b.left < a.right - 1 &&
            a.top < b.bottom - 1 && b.top < a.bottom - 1) { over++; }
      }
    }
    if (over) { add('overlap', name(g) + ' x' + over); }
  });

  // 4. text too small to read on a phone
  var seenSmall = {};
  document.querySelectorAll('p, li, span, small, a, b, i, div, h1, h2, h3').forEach(function (el) {
    if (!el.offsetParent) { return; }
    var direct = [].slice.call(el.childNodes)
      .some(function (n) { return n.nodeType === 3 && n.textContent.trim().length > 1; });
    if (!direct) { return; }
    var fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < 11.5) {
      var k = name(el) + ' @' + fs.toFixed(1) + 'px';
      if (!seenSmall[k]) { seenSmall[k] = 1; add('tinyText', k); }
    }
  });

  // 5. tap targets under 40px
  var seenTap = {};
  document.querySelectorAll('a[href], button, .vid, .shot').forEach(function (el) {
    var r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) { return; }
    if (r.height < 40 || r.width < 40) {
      var k = name(el) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height);
      if (!seenTap[k]) { seenTap[k] = 1; add('smallTap', k); }
    }
  });

  // 6. media that ended up absurdly tall or short for its slot
  document.querySelectorAll('.vid').forEach(function (v) {
    var r = v.getBoundingClientRect();
    if (r.height > window.innerHeight * 1.6) {
      add('tallMedia', name(v) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
    }
  });

  out.height = Math.round(document.body.scrollHeight);
  Object.keys(out.issues).forEach(function (k) {
    if (out.issues[k].length > 6) {
      out.issues[k] = out.issues[k].slice(0, 6).concat(['…+' + (out.issues[k].length - 6) + ' more']);
    }
  });
  return JSON.stringify(out);
})()
