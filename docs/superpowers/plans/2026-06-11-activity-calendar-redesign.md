# Activity Calendar Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the plain 8-column table in the Activity Calendar section of `wireframe-group-activities-v3.html` with a prettier, richer, mobile-aware session-chip week grid — static HTML/CSS only, within the locked monochrome design system.

**Architecture:** One CSS block appended to the page's existing `<style>` (a `.cal` CSS grid + chip/rail/legend rules + a `@media (max-width:768px)` reflow). One markup swap: the `.wire-card`-wrapped tab-row + `<table>` + caption becomes a kept tab row + `.cal` grid (corner, 7 day headers, 6 window rails each followed by 7 session chips) + a `.cal-legend`. The DOM is row-major (window → Mon..Sun), so on mobile the grid reflows to stacked-by-window blocks with no duplicated markup.

**Tech Stack:** Static HTML + CSS only. No JS (consistent with the entire deck). Python 3 stdlib for the structure check.

**Spec:** `docs/superpowers/specs/2026-06-11-activity-calendar-redesign-design.md` (approved 2026-06-11).

**Commit policy:** This repo's `main` is pushed directly to a client-visible remote, so we avoid committing a broken half-state. ONE commit at the end (Task 4). The commit MUST add files explicitly — `git add wireframe-group-activities-v3.html tests/check_calendar.py` — because `tests/` also contains untracked files from a PAUSED unrelated feature (`check_structure.py`, `check_search_logic.mjs`) that must NOT be swept into this commit.

---

## File Structure

- Modify: `wireframe-group-activities-v3.html` — (a) CSS appended before `</style>` (~line 197); (b) markup swap inside the Activity Calendar section (~lines 442–475).
- Create: `tests/check_calendar.py` — Python stdlib structure checks scoped to the Activity Calendar section.
- NOT touched: the locked token block, the two prose schedules, every other section of the page, every other deck file, and the paused `tests/check_structure.py` / `tests/check_search_logic.mjs`.

---

### Task 1: Write the structure check and watch it fail

**Files:**
- Create: `tests/check_calendar.py`

- [ ] **Step 1: Write the checker**

Create `tests/check_calendar.py` with exactly:

```python
#!/usr/bin/env python3
"""Structure checks for the activity calendar redesign."""
import re
import sys
from pathlib import Path

html = Path(__file__).resolve().parent.parent.joinpath(
    'wireframe-group-activities-v3.html').read_text(encoding='utf-8')
failures = []


def check(name, ok):
    print(('PASS' if ok else 'FAIL') + '  ' + name)
    if not ok:
        failures.append(name)


# Isolate the Activity Calendar section so we don't match the prose schedules above.
start = html.find('<!-- ACTIVITY CALENDAR')
end = html.find('<!-- WHERE ACTIVITIES HAPPEN')
section = html[start:end] if start != -1 and end != -1 else ''
check('calendar section located', bool(section))

check('grid container present', 'class="cal"' in section)
check('day headers present', 'cal-dayhead' in section)
check('rail cells present', 'cal-rail' in section)
check('chip cells present', 'cal-chip' in section)
check('chip-day spans present', 'chip-day' in section)
check('today marker present', 'd-today' in section)
check('legend present', 'cal-legend' in section)
check('old wire-table removed from section', 'wire-table' not in section)

chips = re.findall(r'class="cal-chip(?: is-anchor)?"', section)
check('exactly 42 chips', len(chips) == 42)
check('seven stretch anchor chips', section.count('cal-chip is-anchor') == 7)

names = ['Mat Pilates', 'Yin Yoga', 'Tai Chi', 'Yoga Flow', 'Pool Noodle',
         'Hand Buoy', 'Aqua Boxing', 'Stretch', 'HIIT', 'TRX', 'Tabata',
         'Circuit', 'Zumba', 'Step Aerobics', 'Boot Camp', 'Pranayama',
         'Singing Bowl', 'Floating Med.', 'Aerial Yoga', 'Candlelight Med.',
         'Better Sleep', 'Star Gazing']
for n in names:
    check('session present: ' + n, n in section)

check('mobile reflow marker present', 'calendar: stack by window on mobile' in html)
check('no script added to page', '<script' not in html)
check('locked token block intact',
      html.count('JAYASOM DESIGN TOKENS (locked, do not modify)') == 1)

sys.exit(1 if failures else 0)
```

- [ ] **Step 2: Run it and verify it fails (red)**

Run: `cd "/mnt/d/Code Files/Jayasom/jayasom-content-wireframes" && python3 tests/check_calendar.py; echo "exit=$?"`
Expected: `PASS  calendar section located`, `PASS  old wire-table removed from section` is **FAIL** (table still present), plus `FAIL` for `grid container present`, `cal-dayhead`, `cal-rail`, `cal-chip`, `chip-day`, `d-today`, `legend`, `exactly 42 chips`, `seven stretch anchor chips`, and `mobile reflow marker present`. The 22 `session present:` lines PASS (names still in the old table), and `no script added` + `locked token block intact` PASS. `exit=1`.

Do NOT commit (see commit policy).

---

### Task 2: Add the calendar CSS

**Files:**
- Modify: `wireframe-group-activities-v3.html` — insert before the closing `</style>` (the `  </style>` line, ~197, immediately after the `.activity-card .a-body { ... }` rule).

- [ ] **Step 1: Insert the CSS block**

Find the `  </style>` line near the top of the file (the one that ends the page's style block, right after the `.activity-card .a-body` rule). Insert the following immediately before it:

```css
/* === ACTIVITY CALENDAR === */
.cal {
  display: grid;
  grid-template-columns: 160px repeat(7, 1fr);
  border-top: 1px solid hsl(var(--border));
  border-left: 1px solid hsl(var(--border));
}
.cal > * {
  border-right: 1px solid hsl(var(--border));
  border-bottom: 1px solid hsl(var(--border));
}
.cal-corner { background: hsl(var(--muted)); }
.cal-dayhead {
  background: hsl(var(--muted));
  padding: 12px 8px; text-align: center;
  display: flex; flex-direction: column; align-items: center; gap: 5px;
}
.cal-dayhead .d-name {
  font-size: 12px; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase; color: hsl(var(--foreground));
}
.cal-dayhead .d-today {
  font-size: 8px; letter-spacing: 0.15em; text-transform: uppercase;
  color: hsl(var(--primary-foreground)); background: hsl(var(--foreground));
  padding: 2px 6px;
}
.cal-rail { background: hsl(var(--muted)); padding: 16px 14px; }
.cal-rail .r-cue {
  font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase;
  color: hsl(var(--muted-foreground)); margin-bottom: 5px;
}
.cal-rail .r-name {
  font-size: 14px; font-weight: 700; color: hsl(var(--foreground)); line-height: 1.25;
}
.cal-chip {
  background: hsl(var(--background));
  padding: 12px 12px 14px;
  display: flex; flex-direction: column; gap: 5px;
  cursor: pointer; transition: background 160ms ease;
}
.cal-chip:hover { background: hsl(var(--muted)); }
.cal-chip .chip-day { display: none; }
.cal-chip .chip-cat {
  font-size: 9px; letter-spacing: 0.18em; text-transform: uppercase;
  color: hsl(var(--muted-foreground));
}
.cal-chip .chip-name {
  font-size: 13px; font-weight: 300; color: hsl(var(--foreground)); line-height: 1.3;
}
.cal-chip .chip-tap {
  margin-top: 2px; font-size: 10px; color: hsl(var(--muted-foreground));
  display: inline-flex; align-items: center; gap: 5px;
}
.cal-chip .chip-tap::before {
  content: ""; width: 5px; height: 5px; border-radius: 50%;
  background: hsl(var(--muted-foreground));
}
.cal-chip.is-anchor { background: hsl(var(--accent)); }
.cal-chip.is-anchor .chip-name { font-weight: 700; }
.cal-legend {
  display: flex; flex-wrap: wrap; gap: 18px 32px;
  margin-top: 20px; padding-top: 20px; border-top: 1px solid hsl(var(--border));
}
.cal-legend .leg-item { display: flex; gap: 10px; align-items: flex-start; max-width: 300px; }
.cal-legend .leg-key {
  font-size: 9px; letter-spacing: 0.15em; text-transform: uppercase; font-weight: 700;
  color: hsl(var(--muted-foreground)); flex-shrink: 0; padding-top: 1px;
}
.cal-legend .leg-text { font-size: 11px; color: hsl(var(--muted-foreground)); line-height: 1.5; }

/* calendar: stack by window on mobile */
@media (max-width: 768px) {
  .cal { display: block; border: 1px solid hsl(var(--border)); border-bottom: 0; }
  .cal-corner, .cal-dayhead { display: none; }
  .cal > * { border-right: 0; }
  .cal-rail { padding: 14px 16px; }
  .cal-chip {
    flex-direction: row; flex-wrap: wrap; align-items: baseline; gap: 4px 10px;
    padding: 12px 16px;
  }
  .cal-chip .chip-day {
    display: inline-block; min-width: 40px;
    font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700;
    color: hsl(var(--foreground));
  }
  .cal-chip .chip-cat { order: 3; width: 100%; }
  .cal-chip .chip-tap { order: 4; width: 100%; margin-top: 0; }
}
```

Do NOT modify the `JAYASOM DESIGN TOKENS (locked, do not modify)` block.

- [ ] **Step 2: Run the checker — markup checks still red, marker now green**

Run: `python3 tests/check_calendar.py; echo "exit=$?"`
Expected: `mobile reflow marker present` now **PASS**; the markup checks (`grid container present`, `cal-dayhead`, `cal-rail`, `cal-chip`, `chip-day`, `d-today`, `legend`, `exactly 42 chips`, `seven stretch anchor chips`) still **FAIL**; `old wire-table removed from section` still **FAIL**. `exit=1`.

---

### Task 3: Swap the table markup for the chip grid

**Files:**
- Modify: `wireframe-group-activities-v3.html` — the Activity Calendar section (~lines 442–475).

- [ ] **Step 1: Confirm the exact current block**

Run: `sed -n '433,477p' "/mnt/d/Code Files/Jayasom/jayasom-content-wireframes/wireframe-group-activities-v3.html"`
Expected: the section starting `<!-- ACTIVITY CALENDAR (live module placeholder) -->`, containing `<div class="wire-card">`, the `tag-row`, the `<table class="wire-table">` with six `<tr>` rows, the caption, and the closing `</div>`s before `</section>`. Use the printed text as the exact `old_string` for the Edit in Step 2.

- [ ] **Step 2: Replace the wire-card block**

Using Edit, replace this exact block (the `.wire-card` wrapper through its closing `</div>`):

```html
    <div class="wire-card">
      <div class="pad" style="padding:32px;">
        <div class="tag-row mb-6">
          <span class="tag active">Adults</span>
          <span class="tag">Children</span>
          <span class="tag">Family</span>
          <span class="tag">Visiting Practitioners</span>
        </div>
        <table class="wire-table">
          <thead>
            <tr>
              <th>Window</th>
              <th class="center">Mon</th>
              <th class="center">Tue</th>
              <th class="center">Wed</th>
              <th class="center">Thu</th>
              <th class="center">Fri</th>
              <th class="center">Sat</th>
              <th class="center">Sun</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>Sunrise · Morning Movement</td><td class="center">Mat Pilates</td><td class="center">Yin Yoga</td><td class="center">Tai Chi</td><td class="center">Yoga Flow</td><td class="center">Mat Pilates</td><td class="center">Yin Yoga</td><td class="center">Tai Chi</td></tr>
            <tr><td>Mid-morning · Aqua</td><td class="center">Pool Noodle</td><td class="center">Hand Buoy</td><td class="center">Aqua Boxing</td><td class="center">Pool Noodle</td><td class="center">Hand Buoy</td><td class="center">Aqua Boxing</td><td class="center">Pool Noodle</td></tr>
            <tr><td>Midday · Stretch</td><td class="center">Stretch</td><td class="center">Stretch</td><td class="center">Stretch</td><td class="center">Stretch</td><td class="center">Stretch</td><td class="center">Stretch</td><td class="center">Stretch</td></tr>
            <tr><td>Afternoon · Strength &amp; HIIT</td><td class="center">HIIT</td><td class="center">TRX</td><td class="center">Tabata</td><td class="center">Circuit</td><td class="center">Zumba</td><td class="center">Step Aerobics</td><td class="center">Boot Camp</td></tr>
            <tr><td>Early evening · Breath &amp; Meditation</td><td class="center">Pranayama</td><td class="center">Singing Bowl</td><td class="center">Floating Med.</td><td class="center">Aerial Yoga</td><td class="center">Pranayama</td><td class="center">Singing Bowl</td><td class="center">Floating Med.</td></tr>
            <tr><td>Closing · Night Practice</td><td class="center">Candlelight Med.</td><td class="center">Better Sleep</td><td class="center">Star Gazing</td><td class="center">Candlelight Med.</td><td class="center">Better Sleep</td><td class="center">Star Gazing</td><td class="center">Candlelight Med.</td></tr>
          </tbody>
        </table>
        <p class="caption mt-4" style="font-style:italic;">Names are indicative; times confirmed daily at the front desk. Tap a session for the day's confirmed time.</p>
      </div>
    </div>
```

with this new block:

```html
    <div class="tag-row mb-6">
      <span class="tag active">Adults</span>
      <span class="tag">Children</span>
      <span class="tag">Family</span>
      <span class="tag">Visiting Practitioners</span>
    </div>

    <div class="cal">
      <div class="cal-corner"></div>
      <div class="cal-dayhead"><span class="d-name">Mon</span></div>
      <div class="cal-dayhead"><span class="d-name">Tue</span></div>
      <div class="cal-dayhead"><span class="d-name">Wed</span><span class="d-today">Today</span></div>
      <div class="cal-dayhead"><span class="d-name">Thu</span></div>
      <div class="cal-dayhead"><span class="d-name">Fri</span></div>
      <div class="cal-dayhead"><span class="d-name">Sat</span></div>
      <div class="cal-dayhead"><span class="d-name">Sun</span></div>

      <div class="cal-rail"><div class="r-cue">Sunrise</div><div class="r-name">Morning Movement</div></div>
      <div class="cal-chip"><span class="chip-day">Mon</span><span class="chip-cat">Pilates</span><span class="chip-name">Mat Pilates</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Tue</span><span class="chip-cat">Yoga</span><span class="chip-name">Yin Yoga</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Wed</span><span class="chip-cat">Tai Chi</span><span class="chip-name">Tai Chi</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Thu</span><span class="chip-cat">Yoga</span><span class="chip-name">Yoga Flow</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Fri</span><span class="chip-cat">Pilates</span><span class="chip-name">Mat Pilates</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Sat</span><span class="chip-cat">Yoga</span><span class="chip-name">Yin Yoga</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Sun</span><span class="chip-cat">Tai Chi</span><span class="chip-name">Tai Chi</span><span class="chip-tap">Tap for time</span></div>

      <div class="cal-rail"><div class="r-cue">Mid-morning</div><div class="r-name">Aqua</div></div>
      <div class="cal-chip"><span class="chip-day">Mon</span><span class="chip-cat">Aqua</span><span class="chip-name">Pool Noodle</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Tue</span><span class="chip-cat">Aqua</span><span class="chip-name">Hand Buoy</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Wed</span><span class="chip-cat">Aqua</span><span class="chip-name">Aqua Boxing</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Thu</span><span class="chip-cat">Aqua</span><span class="chip-name">Pool Noodle</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Fri</span><span class="chip-cat">Aqua</span><span class="chip-name">Hand Buoy</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Sat</span><span class="chip-cat">Aqua</span><span class="chip-name">Aqua Boxing</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Sun</span><span class="chip-cat">Aqua</span><span class="chip-name">Pool Noodle</span><span class="chip-tap">Tap for time</span></div>

      <div class="cal-rail"><div class="r-cue">Midday</div><div class="r-name">Stretch</div></div>
      <div class="cal-chip is-anchor"><span class="chip-day">Mon</span><span class="chip-cat">Stretch</span><span class="chip-name">Stretch</span><span class="chip-tap">Every day</span></div>
      <div class="cal-chip is-anchor"><span class="chip-day">Tue</span><span class="chip-cat">Stretch</span><span class="chip-name">Stretch</span><span class="chip-tap">Every day</span></div>
      <div class="cal-chip is-anchor"><span class="chip-day">Wed</span><span class="chip-cat">Stretch</span><span class="chip-name">Stretch</span><span class="chip-tap">Every day</span></div>
      <div class="cal-chip is-anchor"><span class="chip-day">Thu</span><span class="chip-cat">Stretch</span><span class="chip-name">Stretch</span><span class="chip-tap">Every day</span></div>
      <div class="cal-chip is-anchor"><span class="chip-day">Fri</span><span class="chip-cat">Stretch</span><span class="chip-name">Stretch</span><span class="chip-tap">Every day</span></div>
      <div class="cal-chip is-anchor"><span class="chip-day">Sat</span><span class="chip-cat">Stretch</span><span class="chip-name">Stretch</span><span class="chip-tap">Every day</span></div>
      <div class="cal-chip is-anchor"><span class="chip-day">Sun</span><span class="chip-cat">Stretch</span><span class="chip-name">Stretch</span><span class="chip-tap">Every day</span></div>

      <div class="cal-rail"><div class="r-cue">Afternoon</div><div class="r-name">Strength &amp; HIIT</div></div>
      <div class="cal-chip"><span class="chip-day">Mon</span><span class="chip-cat">Strength</span><span class="chip-name">HIIT</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Tue</span><span class="chip-cat">Strength</span><span class="chip-name">TRX</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Wed</span><span class="chip-cat">Strength</span><span class="chip-name">Tabata</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Thu</span><span class="chip-cat">Strength</span><span class="chip-name">Circuit</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Fri</span><span class="chip-cat">Dance</span><span class="chip-name">Zumba</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Sat</span><span class="chip-cat">Cardio</span><span class="chip-name">Step Aerobics</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Sun</span><span class="chip-cat">Strength</span><span class="chip-name">Boot Camp</span><span class="chip-tap">Tap for time</span></div>

      <div class="cal-rail"><div class="r-cue">Early evening</div><div class="r-name">Breath &amp; Meditation</div></div>
      <div class="cal-chip"><span class="chip-day">Mon</span><span class="chip-cat">Breath</span><span class="chip-name">Pranayama</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Tue</span><span class="chip-cat">Sound</span><span class="chip-name">Singing Bowl</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Wed</span><span class="chip-cat">Meditation</span><span class="chip-name">Floating Med.</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Thu</span><span class="chip-cat">Yoga</span><span class="chip-name">Aerial Yoga</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Fri</span><span class="chip-cat">Breath</span><span class="chip-name">Pranayama</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Sat</span><span class="chip-cat">Sound</span><span class="chip-name">Singing Bowl</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Sun</span><span class="chip-cat">Meditation</span><span class="chip-name">Floating Med.</span><span class="chip-tap">Tap for time</span></div>

      <div class="cal-rail"><div class="r-cue">Closing</div><div class="r-name">Night Practice</div></div>
      <div class="cal-chip"><span class="chip-day">Mon</span><span class="chip-cat">Meditation</span><span class="chip-name">Candlelight Med.</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Tue</span><span class="chip-cat">Rest</span><span class="chip-name">Better Sleep</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Wed</span><span class="chip-cat">Outdoor</span><span class="chip-name">Star Gazing</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Thu</span><span class="chip-cat">Meditation</span><span class="chip-name">Candlelight Med.</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Fri</span><span class="chip-cat">Rest</span><span class="chip-name">Better Sleep</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Sat</span><span class="chip-cat">Outdoor</span><span class="chip-name">Star Gazing</span><span class="chip-tap">Tap for time</span></div>
      <div class="cal-chip"><span class="chip-day">Sun</span><span class="chip-cat">Meditation</span><span class="chip-name">Candlelight Med.</span><span class="chip-tap">Tap for time</span></div>
    </div>

    <div class="cal-legend">
      <div class="leg-item"><span class="leg-key">Category</span><span class="leg-text">Each session is tagged by discipline — yoga, breath, aqua, strength, sound and more.</span></div>
      <div class="leg-item"><span class="leg-key">Anchor</span><span class="leg-text">The Midday Stretch is the daily anchor — held every day, it is always there.</span></div>
      <div class="leg-item"><span class="leg-key">Times</span><span class="leg-text">Names are indicative; tap any session for the day's confirmed time, set daily at the front desk.</span></div>
    </div>
```

- [ ] **Step 3: Run the checker — all green**

Run: `python3 tests/check_calendar.py; echo "exit=$?"`
Expected: every line `PASS`; `exit=0`.

---

### Task 4: Browser verification and commit

**Files:**
- No new edits expected; fix-forward if verification finds issues, re-running Task 3 Step 3 after any fix.

- [ ] **Step 1: Confirm the dev server is up**

Run: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/wireframe-group-activities-v3.html`
Expected: `200`. (If not running: `cd "/mnt/d/Code Files/Jayasom/jayasom-content-wireframes" && python3 dev-server.py` in the background.)

- [ ] **Step 2: Verify in the browser**

Open `http://localhost:8765/wireframe-group-activities-v3.html`, scroll to "The Activity Calendar". Check:
1. Desktop ~1200px: an 8-column grid — window rail on the left, day headers Mon–Sun across the top, Wed marked "Today"; muted fill on rail + headers; hairline borders form a clean matrix with no doubled/!missing edges.
2. Each chip shows a small category label above the session name, plus a "Tap for time" dot cue. The Midday Stretch row reads as a filled anchor with bold names and "Every day" cues.
3. The legend (Category / Anchor / Times) renders below the grid.
4. Narrow to ~390px (DevTools device toolbar): the calendar reflows to stacked-by-window blocks — each window's rail label as a heading, then its 7 sessions as rows each showing its day label (Mon, Tue, …); no horizontal scrollbar/overflow.
5. The rest of the page (prose schedules, hero, FAQ, footer) is visually unchanged.

- [ ] **Step 3: Commit (explicit adds only)**

```bash
cd "/mnt/d/Code Files/Jayasom/jayasom-content-wireframes"
git add wireframe-group-activities-v3.html tests/check_calendar.py
git commit -m "Redesign activity calendar as session-chip week grid

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git status --porcelain
```

Expected: one commit on `main`. `git status --porcelain` afterward still shows the paused, untracked `tests/check_structure.py` and `tests/check_search_logic.mjs` (and the untracked docs plan, if not separately committed) — confirm those were NOT included in this commit. Do NOT push (the user pushes to main themselves).
