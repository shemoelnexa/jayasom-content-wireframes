# Index Search & Filters Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a sticky search bar + single-select category filter chips to `index.html` so anyone can find any of the 69 wireframe pages by typing or clicking. (The hero says "67 pages" but the index actually holds 69 rows — the hero figure is stale, and the new DOM-derived counts will correct it automatically.)

**Architecture:** Everything lives inside `index.html` (the deck convention: self-contained files, no build step, no dependencies). One CSS block extends the existing `<style>`; one vanilla-JS IIFE before `</body>` treats the existing DOM as the data model (rows = `a.page-row`, groups = `section.section-group`) and toggles an `.is-hidden` class. Pure matching helpers sit between sentinel comments so the Node test can extract and exercise the exact shipped code. Two committed test scripts (Python stdlib + Node stdlib) verify structure and matching logic; interactive behavior is verified against the running dev server.

**Tech Stack:** Static HTML, vanilla ES5-compatible JS, Python 3 (stdlib only) and Node ≥18 (stdlib only) for checks. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-06-11-index-search-filters-design.md` (approved 2026-06-11).

**Commit policy note:** This repo's `main` is pushed directly to the client-visible remote and its history is feature-level commits (see `git log`). To avoid a broken half-feature state on `main`, this plan makes ONE commit at the end (Task 4) containing `index.html` + `tests/`, instead of per-task commits.

---

## File Structure

- Modify: `index.html` — three edits: (a) `id="hero-count"` on the intro count line, (b) toolbar + empty-state sections after the intro, (c) CSS addition inside the existing `<style>`, (d) `<script>` IIFE before `</body>`.
- Create: `tests/check_structure.py` — static assertions that the markup/style/script hooks exist (Python stdlib).
- Create: `tests/check_search_logic.mjs` — extracts the pure helpers from the shipped script and runs matching assertions against the real 69 rows parsed from `index.html` (Node stdlib).
- NOT touched: the locked token block in `index.html`, `index-client.html`, all `wireframe-*.html`, `dev-server.py`, `README.md`.

---

### Task 1: Write both test scripts and watch them fail

**Files:**
- Create: `tests/check_structure.py`
- Create: `tests/check_search_logic.mjs`

- [ ] **Step 1: Write the structure checker**

Create `tests/check_structure.py` with exactly:

```python
#!/usr/bin/env python3
"""Static structure checks for the index search/filter feature."""
import re
import sys
from pathlib import Path

html = Path(__file__).resolve().parent.parent.joinpath('index.html').read_text(encoding='utf-8')
failures = []


def check(name, ok):
    print(('PASS' if ok else 'FAIL') + '  ' + name)
    if not ok:
        failures.append(name)


check('toolbar section present', 'class="toolbar"' in html)
check('search input present', 'id="page-search"' in html)
check('clear button present', 'id="clear-search"' in html)
check('chip row present', 'id="chip-row"' in html)
check('result count present', 'id="result-count"' in html)
check('empty state present', 'id="empty-wrap"' in html)
check('hero count has id', 'id="hero-count"' in html)
check('toolbar before first group',
      0 < html.find('class="toolbar"') < html.find('class="section-group"'))
check('toolbar styles present', 'position: sticky' in html)
check('active chip style present', '.chip.is-active' in html)
check('hidden helper style present', '.is-hidden' in html)
check('script with pure helpers present',
      re.search(r'<script>[\s\S]*pure helpers[\s\S]*</script>', html) is not None)
check('keyboard shortcuts wired',
      "event.key === '/'" in html and "'Escape'" in html and "'Enter'" in html)
check('locked token block intact',
      html.count('JAYASOM DESIGN TOKENS (locked, do not modify)') == 1)

sys.exit(1 if failures else 0)
```

- [ ] **Step 2: Write the logic checker**

Create `tests/check_search_logic.mjs` with exactly:

```js
#!/usr/bin/env node
// Behavioural checks for the index search matching logic.
// Extracts the pure helpers from index.html's inline script and runs them
// against the real row data parsed from the same file.
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const html = readFileSync(join(dirname(fileURLToPath(import.meta.url)), '..', 'index.html'), 'utf8');

const helperSrc = html.match(/\/\/ --- pure helpers[\s\S]*?\/\/ --- end pure helpers ---/);
assert.ok(helperSrc, 'pure helper sentinels found in index.html');
const { normalize, rowMatches } = new Function(`${helperSrc[0]}\nreturn { normalize, rowMatches };`)();

// Parse every page row: group title + row title + href.
const rows = [];
for (const groupMatch of html.matchAll(/<section class="section-group">[\s\S]*?<\/section>/g)) {
  const group = groupMatch[0].match(/class="group-title">([^<]*)</)[1];
  for (const row of groupMatch[0].matchAll(/href="([^"]+)"><span class="title">([\s\S]*?)<\/span>/g)) {
    const title = row[2].replace(/&amp;/g, '&');
    rows.push({ group, href: row[1], title, haystack: normalize(`${title} ${group} ${row[1]}`) });
  }
}

const matchCount = (query) => {
  const tokens = normalize(query).split(' ').filter(Boolean);
  return rows.filter((r) => rowMatches(r.haystack, tokens)).length;
};

assert.ok(rows.length >= 60, `parsed ${rows.length} rows (expected the full index)`);

// Normalisation
assert.equal(normalize("Reiki T'aqa"), 'reiki taqa');
assert.equal(normalize('QALBAIN — Two Hearts'), 'qalbain - two hearts');
assert.equal(normalize('Rooms & Villas'), 'rooms and villas');

// Every page is findable by its own full title.
for (const r of rows) {
  assert.ok(rowMatches(r.haystack, normalize(r.title).split(' ').filter(Boolean)),
    `row not findable by own title: ${r.title}`);
}

// Spot behaviour from the spec.
assert.equal(matchCount('taqa'), 1, "'taqa' finds exactly Reiki T'aqa");
assert.ok(matchCount('villa') >= 4, "'villa' finds the villa pages");
assert.equal(matchCount('qalbain'), 1, "'qalbain' finds QALBAIN — Two Hearts");
assert.equal(matchCount('zzzzzz'), 0, 'gibberish finds nothing');
assert.equal(matchCount('vagus ritual'), 1, 'multi-token query composes');

// Empty query matches everything.
assert.equal(matchCount(''), rows.length);

console.log(`PASS  ${rows.length} rows, all logic checks green`);
```

- [ ] **Step 3: Run both and verify they fail (red)**

Run: `cd "/mnt/d/Code Files/Jayasom/jayasom-content-wireframes" && python3 tests/check_structure.py; echo "exit=$?"`
Expected: `FAIL` lines for every check except `locked token block intact` (which passes); `exit=1`.

Run: `node tests/check_search_logic.mjs; echo "exit=$?"`
Expected: AssertionError `pure helper sentinels found in index.html`; `exit=1`.

Do NOT commit yet (see commit policy note).

---

### Task 2: Add toolbar markup, empty state, and styles to index.html

**Files:**
- Modify: `index.html` (hero line ~119, after intro `</section>` ~121, inside `<style>` before `</style>` ~112)

- [ ] **Step 1: Give the hero count line an id**

In `index.html`, replace:

```html
    <p class="body-copy" style="margin: 12px auto 0;">67 pages · V3</p>
```

with:

```html
    <p class="body-copy" id="hero-count" style="margin: 12px auto 0;">67 pages · V3</p>
```

- [ ] **Step 2: Insert the toolbar + empty-state sections**

Immediately after the intro section's closing tag (the `</section>` that follows the hero count line) and before the first `<section class="section-group">`, insert:

```html
<section class="toolbar">
  <div class="shell">
    <div class="search-box" id="search-box">
      <span class="glyph" aria-hidden="true">⌕</span>
      <input id="page-search" type="text" placeholder="Search pages…" autocomplete="off" aria-label="Search pages"/>
      <button class="clear-btn" id="clear-search" type="button" aria-label="Clear search">✕</button>
    </div>
    <div class="chip-row" id="chip-row" role="group" aria-label="Filter by section"></div>
    <p class="result-count" id="result-count" aria-live="polite"></p>
  </div>
</section>

<section class="empty-wrap" id="empty-wrap" hidden>
  <div class="shell">
    <div class="empty-state">
      <p class="empty-title">No pages match <span id="empty-query"></span></p>
      <button class="clear-all" id="clear-all" type="button">Clear search &amp; filters</button>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Add the toolbar styles**

Inside the existing `<style>` block, immediately before the closing `</style>` (after the `.section-group .group-count` rule), insert:

```css
/* === SEARCH & FILTER TOOLBAR === */
.toolbar {
  position: sticky; top: 0; z-index: 10;
  background: hsl(var(--background));
  border-bottom: 1px solid hsl(var(--border));
  padding: 16px 32px 14px;
}
.toolbar .shell { display: flex; flex-direction: column; gap: 12px; }
.search-box {
  display: flex; align-items: center; gap: 10px;
  border: 1px solid hsl(var(--border));
  padding: 10px 14px;
}
.search-box:focus-within { border-color: hsl(var(--foreground)); }
.search-box .glyph { font-size: 16px; color: hsl(var(--muted-foreground)); line-height: 1; }
.search-box input {
  flex: 1; min-width: 0; background: transparent; outline: none;
  font: inherit; font-size: 14px; color: hsl(var(--foreground));
}
.search-box input::placeholder { color: hsl(var(--muted-foreground)); }
.search-box .clear-btn {
  display: none; background: transparent; cursor: pointer;
  font: inherit; font-size: 13px; line-height: 1; padding: 2px 4px;
  color: hsl(var(--muted-foreground));
}
.search-box .clear-btn:hover { color: hsl(var(--foreground)); }
.search-box.has-query .clear-btn { display: block; }
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  font: inherit; font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
  padding: 7px 12px; border: 1px solid hsl(var(--border));
  background: transparent; color: hsl(var(--muted-foreground)); cursor: pointer;
  transition: color 160ms ease, border-color 160ms ease, background 160ms ease;
}
.chip:hover { border-color: hsl(var(--foreground)); color: hsl(var(--foreground)); }
.chip.is-active {
  background: hsl(var(--primary)); border-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}
.result-count {
  font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
  color: hsl(var(--muted-foreground));
}
.empty-wrap { padding: 32px; }
.empty-state {
  border: 1px dashed hsl(var(--border));
  padding: 56px 24px; text-align: center;
}
.empty-state .empty-title { font-size: 15px; color: hsl(var(--foreground)); margin-bottom: 18px; }
.empty-state .clear-all {
  font: inherit; font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
  padding: 10px 18px; border: 1px solid hsl(var(--foreground));
  background: transparent; color: hsl(var(--foreground)); cursor: pointer;
  transition: background 160ms ease, color 160ms ease;
}
.empty-state .clear-all:hover { background: hsl(var(--primary)); color: hsl(var(--primary-foreground)); }
.is-hidden { display: none !important; }
```

Do NOT touch the `JAYASOM DESIGN TOKENS (locked, do not modify)` block.

- [ ] **Step 4: Run the structure checker — only script checks still red**

Run: `python3 tests/check_structure.py; echo "exit=$?"`
Expected: all `PASS` except two `FAIL` lines — `script with pure helpers present` and `keyboard shortcuts wired`; `exit=1`.

---

### Task 3: Add the search/filter script

**Files:**
- Modify: `index.html` (immediately before `</body>`)

- [ ] **Step 1: Insert the script block**

Immediately before `</body>` (after the `<section style="height: 64px;"></section>` spacer), insert:

```html
<script>
(function () {
  // --- pure helpers (extracted by tests/check_search_logic.mjs — keep sentinels) ---
  function normalize(text) {
    return text
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/['\u2018\u2019\u0060]/g, '')
      .replace(/[\u2013\u2014\u2212]/g, '-')
      .replace(/&/g, ' and ')
      .replace(/\s+/g, ' ')
      .trim();
  }
  function rowMatches(haystack, tokens) {
    for (var i = 0; i < tokens.length; i++) {
      if (haystack.indexOf(tokens[i]) === -1) return false;
    }
    return true;
  }
  // --- end pure helpers ---

  var searchBox = document.getElementById('search-box');
  var searchInput = document.getElementById('page-search');
  var clearBtn = document.getElementById('clear-search');
  var chipRow = document.getElementById('chip-row');
  var resultCount = document.getElementById('result-count');
  var emptyWrap = document.getElementById('empty-wrap');
  var emptyQuery = document.getElementById('empty-query');
  var clearAllBtn = document.getElementById('clear-all');
  var heroCount = document.getElementById('hero-count');

  var groups = Array.prototype.map.call(
    document.querySelectorAll('section.section-group'),
    function (section) {
      var name = section.querySelector('.group-title').textContent;
      var rows = Array.prototype.map.call(
        section.querySelectorAll('a.page-row'),
        function (row) {
          var title = row.querySelector('.title').textContent;
          return { el: row, haystack: normalize(title + ' ' + name + ' ' + row.getAttribute('href')) };
        }
      );
      return { el: section, name: name, countEl: section.querySelector('.group-count'), rows: rows };
    }
  );

  var total = groups.reduce(function (n, g) { return n + g.rows.length; }, 0);
  if (heroCount) heroCount.textContent = total + ' pages · V3';

  var activeGroup = null; // null = All

  function setActiveChip(chip) {
    Array.prototype.forEach.call(chipRow.children, function (c) {
      var on = c === chip;
      c.classList.toggle('is-active', on);
      c.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function makeChip(label, group) {
    var chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'chip';
    chip.textContent = label;
    chip.setAttribute('aria-pressed', 'false');
    chip.addEventListener('click', function () {
      activeGroup = group;
      setActiveChip(chip);
      apply();
    });
    chipRow.appendChild(chip);
    return chip;
  }

  var allChip = makeChip('All', null);
  groups.forEach(function (g) { makeChip(g.name, g); });

  function apply() {
    var raw = searchInput.value;
    var tokens = normalize(raw).split(' ').filter(Boolean);
    var filtering = tokens.length > 0 || activeGroup !== null;
    var visibleTotal = 0;

    groups.forEach(function (g) {
      var inScope = activeGroup === null || activeGroup === g;
      var visible = 0;
      g.rows.forEach(function (r) {
        var show = inScope && rowMatches(r.haystack, tokens);
        r.el.classList.toggle('is-hidden', !show);
        if (show) visible += 1;
      });
      g.el.classList.toggle('is-hidden', visible === 0);
      g.countEl.textContent = filtering
        ? visible + ' of ' + g.rows.length + ' pages'
        : g.rows.length + ' pages';
      visibleTotal += visible;
    });

    searchBox.classList.toggle('has-query', raw.length > 0);
    resultCount.textContent = visibleTotal + ' of ' + total + ' pages';
    emptyWrap.hidden = visibleTotal !== 0;
    if (visibleTotal === 0) {
      emptyQuery.textContent = raw.trim() ? '“' + raw.trim() + '”' : 'the current filters';
    }
  }

  function clearAll(refocus) {
    searchInput.value = '';
    activeGroup = null;
    setActiveChip(allChip);
    apply();
    if (refocus) searchInput.focus();
  }

  searchInput.addEventListener('input', apply);
  clearBtn.addEventListener('click', function () {
    searchInput.value = '';
    apply();
    searchInput.focus();
  });
  clearAllBtn.addEventListener('click', function () { clearAll(true); });

  searchInput.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      event.preventDefault();
      if (searchInput.value) {
        searchInput.value = '';
        apply();
      } else {
        searchInput.blur();
      }
    } else if (event.key === 'Enter') {
      var first = document.querySelector('a.page-row:not(.is-hidden)');
      if (first) window.location.href = first.getAttribute('href');
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === '/' && document.activeElement !== searchInput) {
      event.preventDefault();
      searchInput.focus();
    }
  });

  apply();
})();
</script>
```

- [ ] **Step 2: Run both checkers — all green**

Run: `python3 tests/check_structure.py; echo "exit=$?"`
Expected: every line `PASS`; `exit=0`.

Run: `node tests/check_search_logic.mjs; echo "exit=$?"`
Expected: `PASS  69 rows, all logic checks green`; `exit=0`.

---

### Task 4: Browser verification and commit

**Files:**
- No new edits expected; fix-forward if verification finds issues, re-running Task 3 Step 2 checks after any fix.

- [ ] **Step 1: Confirm the dev server is up**

Run: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/index.html`
Expected: `200`. (If not running: `cd "/mnt/d/Code Files/Jayasom/jayasom-content-wireframes" && python3 dev-server.py` in the background.)

- [ ] **Step 2: Verify in the browser at http://localhost:8765/**

Walk the spec's verification list (a human does this; report what you see):

1. Toolbar appears under the hero; the hero line now reads "69 pages · V3" (JS corrects the stale 67 from the DOM); toolbar sticks to the top when scrolling.
2. Typing `villa` live-narrows to the villa pages; count line updates ("6 of 69 pages" or similar); empty groups disappear.
3. `taqa` finds *Reiki T'aqa*; `qalbain` finds *QALBAIN — Two Hearts*.
4. Chip **Treatments** + query `ritual` shows only the ritual treatment pages; group header reads "X of 17 pages".
5. Gibberish (`zzzz`) shows the "No pages match…" panel; its button clears query + chip and restores all 69 rows.
6. `/` focuses search from anywhere; `Esc` clears it; `Enter` opens the first visible page.
7. ✕ button appears only while the input has text and clears it on click.
8. With JS disabled (DevTools → Command Menu → "Disable JavaScript", reload): the full grouped list renders exactly as before; toolbar is inert; no empty-state panel.

- [ ] **Step 3: Commit**

```bash
cd "/mnt/d/Code Files/Jayasom/jayasom-content-wireframes"
git add index.html tests/check_structure.py tests/check_search_logic.mjs
git commit -m "Add search bar and category filters to wireframe index

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: one commit on `main`; `git status` clean afterwards. Do NOT push (the user pushes to main themselves).
