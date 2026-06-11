# Activity Calendar Redesign — Design

**Date:** 2026-06-11
**Status:** Approved by user (2026-06-11)
**Scope:** the single `ACTIVITY CALENDAR` section of `wireframe-group-activities-v3.html` (currently lines 433–476)

## Context

`wireframe-group-activities-v3.html` is one page of the Jayasom V3 wireframe deck — a self-contained HTML file using the locked monochrome design system (warm-grey tokens, no color, no images, `--radius: 0`, no build step, no JS anywhere in the deck). The page has three calendar-ish blocks: a prose "Adults Schedule", a prose "Children's Schedule", and — lower down — the **Activity Calendar** section, a live-module placeholder.

Today that Activity Calendar is: a `.wire-card` holding four static filter `.tag`s (Adults active, then Children / Family / Visiting Practitioners) above a plain `.wire-table` — a "Window" column plus Mon–Sun, six time-window rows, every cell just a bare class name. It has no visual hierarchy, no session-type cue, no tap affordance despite the caption promising one, and the 8-column table is unusable on a phone.

## Goal

Make the week grid markedly prettier and give each session richer detail, while keeping it a static, monochrome, JS-free wireframe and degrading cleanly on mobile. Content is unchanged — this is presentation only.

## Decisions (locked during brainstorming)

- **Approach A — Session-chip week grid** (chosen over window-bands and day-tab-timeline).
- **Static**, pure HTML/CSS. No JS — consistent with the rest of the deck. Filter tabs are drawn, not wired.
- **Monochrome toolkit only** — differentiate with labels, weight, borders, and `--muted`/`--foreground` fills, never color. Do not modify the locked token block.
- **No invented clock times** — the page deliberately avoids a fixed timeline; the named windows (Sunrise, Mid-morning, …) are the only time cue.
- **Mobile fix folded in** as table-stakes (the deck's other sections all carry `@media (max-width: 768px)` rules).

## Content (unchanged — reproduced for the implementer)

Six windows (left rail), each with a name and a time-of-day cue:

| Window name | Time-of-day cue |
|---|---|
| Morning Movement | Sunrise |
| Aqua | Mid-morning |
| Stretch | Midday |
| Strength & HIIT | Afternoon |
| Breath & Meditation | Early evening |
| Night Practice | Closing |

Session cells, row-major (window → Mon..Sun), each with its category micro-label:

- **Morning Movement:** Mat Pilates `PILATES` · Yin Yoga `YOGA` · Tai Chi `TAI CHI` · Yoga Flow `YOGA` · Mat Pilates `PILATES` · Yin Yoga `YOGA` · Tai Chi `TAI CHI`
- **Aqua:** Pool Noodle `AQUA` · Hand Buoy `AQUA` · Aqua Boxing `AQUA` · Pool Noodle `AQUA` · Hand Buoy `AQUA` · Aqua Boxing `AQUA` · Pool Noodle `AQUA`
- **Stretch:** Stretch `STRETCH` ×7 (the daily anchor)
- **Strength & HIIT:** HIIT `STRENGTH` · TRX `STRENGTH` · Tabata `STRENGTH` · Circuit `STRENGTH` · Zumba `DANCE` · Step Aerobics `CARDIO` · Boot Camp `STRENGTH`
- **Breath & Meditation:** Pranayama `BREATH` · Singing Bowl `SOUND` · Floating Med. `MEDITATION` · Aerial Yoga `YOGA` · Pranayama `BREATH` · Singing Bowl `SOUND` · Floating Med. `MEDITATION`
- **Night Practice:** Candlelight Med. `MEDITATION` · Better Sleep `REST` · Star Gazing `OUTDOOR` · Candlelight Med. `MEDITATION` · Better Sleep `REST` · Star Gazing `OUTDOOR` · Candlelight Med. `MEDITATION`

Days: Mon, Tue, Wed, Thu, Fri, Sat, Sun. One day (Wed) carries a "Today" marker for realism.

## UI / structure

Inside the existing section (heading, eyebrow, intro copy kept verbatim):

1. **Filter tabs** — keep the four tags, Adults active. Restyle as a clean tab row reading as a view switcher (drawn only).
2. **Calendar** — a CSS-grid card (`.cal`) with 8 columns: a left **window rail** column + 7 day columns.
   - **Corner cell** (top-left): empty (no label — keeps the header row uncluttered).
   - **Day headers** (row 1, cols 2–8): day abbrev in bold; Wed shows a small `Today` chip.
   - **Window rail** (col 1, rows 2–7): window name in bold + time-of-day cue as a tiny eyebrow; `--muted` fill.
   - **Session chips** (the 42 cells): each = a micro uppercase category label + the session name + a subtle "tap for time" cue (small underlined dot/affordance, non-functional). Hairline borders between cells; a hover state matching the deck's row-hover convention. The **Stretch** anchor row uses a steady/filled chip variant so "always there" reads visually. Each chip also carries a `.chip-day` span (the day abbrev) that is `display:none` on desktop and revealed on mobile.
3. **Legend** — replaces the lone italic caption: a short key explaining the category labels, the Stretch anchor, and the "tap for confirmed time" affordance. Keep the substance of the existing note ("Names are indicative; times confirmed daily at the front desk").

## Responsive behavior

- **Desktop (>768px):** full 8-column grid; scan a single day down its column.
- **Mobile (≤768px):** the grid reflows **by window** (the DOM is already row-major, so this needs no duplicated markup). Each window becomes a full-width block: the rail label as a heading, then its 7 session chips stacked/wrapped as a list, each chip now showing its `.chip-day` label. Pure CSS via the media query; single source of truth.

## Implementation shape

- One **CSS addition** inside the existing `<style>` block: `.cal` grid, `.cal-corner`, `.cal-dayhead`, `.cal-rail`, `.cal-chip` (+ `.is-anchor`, `.chip-cat`, `.chip-name`, `.chip-day`, `.chip-tap`), `.cal-legend`, and the `@media (max-width:768px)` reflow. Reuse existing tokens and the `.tag` styles for the tab row.
- One **markup replacement**: swap the `<table class="wire-table">…</table>` (and its surrounding `.pad`) for the new grid + legend. Keep the section, heading, intro, and tab row.
- **No** new files, **no** JS, **no** token changes, **no** edits elsewhere in the file or the deck.

## Verification

- **Structure check** (`tests/check_calendar.py`, Python stdlib): asserts the new hooks exist (`class="cal"`, `cal-chip`, `cal-rail`, `chip-day`, `cal-legend`), the old `wire-table` is gone from this section, every distinct session name from the content table still appears and there are exactly 42 `cal-chip` cells, the mobile media query is present, the locked token block is intact (appears exactly once), and no `<script>` was introduced on the page.
- **Browser check** against the dev server (port 8765) at `wireframe-group-activities-v3.html`:
  1. Desktop ~1200px: grid renders 8 columns, window rail on the left, day headers across the top, Wed marked "Today".
  2. Each chip shows category label + name; Stretch row reads as a steady anchor; "tap for time" cue visible.
  3. Legend renders below the grid.
  4. Narrow to ~390px: calendar reflows to stacked-by-window blocks, each chip showing its day label; no horizontal overflow.
  5. Rest of the page visually unchanged.

## Out of scope

- The two prose schedules above the calendar, and every other section.
- Any interactivity (wired filters, real tap popovers), real dates/times, color, images.
- Any change to the locked design-token block or other deck pages.
