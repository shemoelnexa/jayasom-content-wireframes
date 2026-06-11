# Index Search & Filters — Design

**Date:** 2026-06-11
**Status:** Approved by user (2026-06-11)
**Scope:** `index.html` only

## Context

`index.html` is the front door of the Jayasom V3 wireframe deck: 67 page links arranged in 10 themed `section.section-group` blocks. Each link is an `a.page-row` with a `.title` span; each group has a `.group-title` and `.group-count` in its header. The page is fully static (no JS) and styled exclusively with the locked Jayasom design tokens. `index-client.html` merely redirects to it and is not touched.

## Goal

Anyone opening the deck can find a page by typing a few characters or clicking a category, instead of scrolling a 67-row list.

## UI

A toolbar section inserted between the intro (`section.intro`) and the first `section-group`:

- **Search input** — placeholder "Search pages…", ⌕ glyph on the left, ✕ clear button shown only while the input is non-empty.
- **Filter chips** — "All" plus one chip per group, generated at load from the `.group-title` texts. Single-select; the active chip uses the `--primary` fill with `--primary-foreground` text. Default selection: All.
- **Count line** — "N of 67 pages", updated live.
- The toolbar is `position: sticky; top: 0`, filled with `--background` and finished with a 1px bottom border so rows scroll beneath it cleanly.
- Styling uses the existing tokens and conventions only: square corners, 1px `hsl(var(--border))` borders, uppercase 10–11px letter-spaced labels, the existing font stack. The locked token block is not modified.

## Behavior

- **Matching** — the query is split on whitespace; a row matches if every token is a substring of its haystack. Haystack = title text + group title + href filename. Both haystack and query are normalized: lowercase; Unicode NFD with combining marks stripped; apostrophes (`'`, `’`, `` ` ``) removed; dash variants (`–`, `—`, `−`) unified to `-`; `&` treated as "and"; whitespace collapsed. So "taqa" finds *Reiki T'aqa*, "qalbain" finds *QALBAIN — Two Hearts*.
- **Composition** — the active chip restricts candidates to its group; the search query applies within that. Each works alone.
- **Visibility** — non-matching rows get an `.is-hidden` class (`display: none`). A group with zero visible rows is hidden whole, header included. While a filter is active (query non-empty, or a chip other than All selected), each visible group's count reads "X of Y pages"; otherwise it reads "Y pages".
- **Empty state** — zero visible rows overall shows a "No pages match …" panel containing a "Clear search & filters" button that resets the query and chip.
- **Keyboard** — `/` pressed outside the input focuses the search; `Esc` clears the query (a second `Esc` blurs); `Enter` opens the first visible row's href.
- **Counts from the DOM** — at load, JS recomputes the hero "67 pages" figure, every `.group-count`, and the toolbar count line from the actual rows present, and derives chips from the group headers. Adding page 68 or an 11th group later requires no JS edits.
- **No-JS degradation** — without JS the page renders exactly as today (full grouped list); the toolbar controls are inert HTML.

## Implementation shape

- One addition to the existing `<style>` block (toolbar, chip states, `.is-hidden`, empty-state panel).
- One `<script>` block before `</body>`: ~120 lines of vanilla JS, no dependencies, works from `file://`.
- The DOM is the data model — no duplicated page list in JS. Rows: `a.page-row` (title from `.title` textContent, slug from `href`). Groups: `section.section-group` (name from `.group-title`).
- No build step. No other file changes.

## Out of scope

- Search on the wireframe pages themselves (decided with user: index only).
- Fuzzy/typo-tolerant ranking, URL/hash state sync, multi-select chips.
- Any change to the locked design-token block.

## Verification

Drive the page in a browser against the dev server (port 8765):

1. "villa" narrows to the villa pages; "taqa" finds Reiki T'aqa (normalization).
2. Chip *Treatments* + query "ritual" composes correctly.
3. Groups with no matches disappear; counts read "X of Y pages"; total count updates.
4. Gibberish query shows the empty-state panel; its clear button restores all 67 rows.
5. `/` focuses search, `Esc` clears, `Enter` opens the first visible result.
6. With JS disabled, the page renders the full list as before.
