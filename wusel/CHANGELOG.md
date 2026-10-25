# Changelog

## 0.7.3

- Add Petrol as a sixth personal color theme for children and parents.
- Keep six theme choices in an even two-column grid and retain per-account persistence.

## 0.7.2

- Greet children by time of day in both focus and checklist views, in English and German.
- Use the configured Wusel timezone: morning 05:00–11:59, evening 18:00–21:59, neutral hello otherwise.
- Update greetings during quiet refreshes without replacing the task or moving keyboard focus.

## 0.7.1

- Compact parent navigation with an inline child selector and shorter labels; remove redundant visible child, administration, language and account-role labels.
- Preserve accessible control names and account-menu keyboard behavior.
- Split earned-badge labels and full dates across lines, containing long dates at every badge-grid size.

## 0.7.0

- Add explicit today/tomorrow timing for routine creation, editing and archiving; edits and archives default to tomorrow.
- Keep today’s tasks and full-day target stable for tomorrow’s changes; label pending changes in the weekly plan and apply them across restarts.
- Freeze daily plans except for intentional Apply today changes; retain earned and revoked badges.
- Focus rewards on one next goal with progress and earned badges, with the full collection grouped on demand.

## 0.6.2

- Replace the child header Settings text with a quiet gear icon, retaining a localized accessible name, tooltip, keyboard focus and a 44-pixel touch target.

## 0.6.1

- Group parent navigation into the selected child’s pages and separate family administration.
- Rename parent My day to Day overview and Review to Review completions.
- Move parent language and sign-out into a compact account dropdown with keyboard dismissal.

## 0.6.0

- Expand to 17 English/German badges, including full-day totals and 3/7/14/30-day streaks.
- Snapshot daily plans from this update onward, preserving history across routine edits and archival.
- Recalculate full-day/streak statistics after undo and parent corrections without re-granting revoked badges.
- Retain existing progress, badges and parental badge controls.

## 0.5.4

- Show the current calendar week from Monday through Sunday in both account views.

## 0.5.3

- Collapse parent weather into a compact expandable summary and show tasks before the level overview.

- Allow passwords of 4–128 characters for parents and children, including setup and resets.
- Follow browser regional date and time formats independently of interface language.
- Spell out month and weekday names and round displayed temperatures to whole numbers.

## 0.5.2

- Bind production HTTP to IPv4 and IPv6 with separate Waitress sockets.
- Use the Pi host network to avoid IPv4-only container port forwarding.
- Use a fixed port 8099 web URL and Docker init for the standard Python image.
- Log the effective listener addresses and explicit readiness.
- Add real HTTP integration tests for both address families.

## 0.5.1

- Renamed project and app source folders to wusel throughout source, tests, and distributions.
- Recreated English and German READMEs and app documentation.
- Added a portable source-package builder with path and archive validation.
- Kept the Home Assistant installation ID and persistent storage compatible.

## 0.5.0

- Five personal color themes in child and parent Settings.
- Theme choices saved per account and restored across devices.
- Partial preference updates preserve language and theme independently.
- Selected markers, readable palettes, and themed keyboard focus.
- Automatic migration adds the Forest default without replacing account data.

## 0.4.1

- Renamed the application to Wusel, by Wild & Weich.
- Updated browser, Home Assistant, login and app branding.
- Retained the existing app identifier and storage for updates.

## 0.4.0

- Slim level bar on the child home and checklist screens.
- Brief +10 animation for newly earned points and animated bar updates.
- Subtle star/glow celebration when a new level is reached.
- Reduced-motion support with static reward feedback.
- Server-confirmed new reward events prevent duplicate, undo/recheck, and concurrent replay.

## 0.3.0

- Quiet child home with one next task, a large Done button, and a small daily count.
- Compact weather hint with tap-through forecast; checklist and rewards on separate screens.
- Language and sign out moved into child Settings.
- Parent-selectable per-child home view, persisted across devices.
- Brief completion feedback and new-badge-only celebrations.
- Correct handling of empty days and remaining parent-locked tasks.

## 0.2.0

- English and German UI with saved per-account preferences and preserved form drafts.
- Current and remaining-day weather using a configured Home Assistant weather entity.
- Hourly/daily fallback, optional rain probabilities, preparation hints, caching, and labelled stale data.
- Authenticated weather endpoint and server-side Supervisor token handling.
- Automatic migration that preserves existing accounts and progress.

## 0.1.0

Initial family accounts, weekly schedules, daily checklists, rewards, and parent review.
