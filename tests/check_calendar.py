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
check('today marker removed', 'd-today' not in section)
check('old wire-table removed from section', 'wire-table' not in section)

# Simplified content: only window names, session names, and day names remain.
check('category labels removed', 'chip-cat' not in section)
check('tap / time text removed', 'chip-tap' not in section)
check('time-of-day cue removed', 'r-cue' not in section)
check('legend removed', 'cal-legend' not in section)
check('window rail names kept', 'r-name' in section)

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
