# Changelog

## 1.0.0

- Set the Home Assistant release stage to stable, replacing the experimental label.

- Replace the parent account name in the header with the same current-time clock used on child screens, retaining Family and Settings controls.
- Share timezone-aware regional formatting, minute-boundary updates and immediate visibility recovery across both roles, with compact phone layouts.
- Package the 1.0.0 release with the existing task icons, responsive weekly plans, aligned Settings and evening preparation forecasts.

## 0.16.1

- Replace the snack-box artwork with the selected open lunchbox, sandwich and apple while preserving saved task IDs and plain-mode support.
- Match parent Settings heading spacing and language-row alignment to the child Settings layout.
- Make weekly plan columns adapt to actual content width, preventing squeezed child day columns and split weekday/date labels.

## 0.16.0

- Add tomorrow’s Home Assistant forecast, with local-day separation, morning/daytime clothing hints and labeled daily fallback.
- From 18:00 show Prepare for tomorrow alongside today’s weather on child focus/checklist screens. Add Today/Tomorrow choices to child and parent forecast details.
- Update evening/midnight views independently of network polling, preserve forecast selection/focus, and clearly mark missing or stale forecasts.

## 0.15.2

- Show the first small action under each task title in parent Overview, matching the child’s main task card instead of displaying the additional help text. Child guidance remains available under I need help.

## 0.15.1

- Show a quiet hours/minutes clock beside Settings on every child screen, using the configured Wusel timezone and device regional format.
- Update at minute boundaries and immediately on return to the app, independently of network requests or open forms.

## 0.15.0

- Add eight original SVG task icons: piano, guitar, snack box, homework, hairbrush, toilet, jacket and exercise, bringing the picker to 21 icons plus No icon.
- Include English/German labels and the existing neutral palette for plain task icons.

## 0.14.2

- Add a public web app manifest requesting fullscreen with existing hedgehog icons, plus Apple Home Screen metadata. Preserve direct local HTTP access.
- Document iPad/Android Home Screen setup, browser and HTTPS limitations, and the distinction from offline and kiosk modes in English and German.

## 0.14.1

- Use the selected petrol, cream and ochre hedgehog artwork as Wusel's brand mark on sign-in, child and parent screens. Preserve the original artwork in the source package.
- Add cream-backed PNG/ICO favicons, an Apple touch icon and Home Assistant icon/logo assets; serve browser assets through the explicit static allowlist.
- Keep fixed brand colors independent of themes and plain task-icon mode.

## 0.14.0

- Automatically check for changes every 10 seconds on visible parent and child screens; fetch full state only after a revision, day or timezone change, or connection recovery.
- Persist transactional family/per-account revision counters with SQLite triggers, keeping child change markers private and the polling endpoint read-only and inexpensive.
- Reconcile changed screens while preserving form drafts, radio choices, caret, open help/disclosures, focus and scroll. Queue changes behind local actions and keep confirmation dialogs intact.
- Pause background polling, recheck immediately on return/online, back off on failures, serialize state reads and reject snapshots overtaken by a local mutation.
- Preserve strict child undo deadlines, existing task timing/deferrals and neutral parent corrections; remote updates do not trigger reward celebrations.

## 0.13.1

- Remove the parent Overview reminder panel so today's tasks use the full available width.
- Document the proposed child live-update design separately; the existing 60-second refresh remains in this release.

## 0.13.0

- Replace platform-dependent emoji with original bundled SVG artwork for task icons, badges, weather, navigation, branding, status and empty states. No external icon service or font is required.
- Add an accessible SVG task-icon picker with labeled radio options and preview; preserve unsaved icon choices when changing language or theme.
- Render plain task icons using the same geometry with a neutral palette instead of applying a grayscale filter to platform emoji.
- Preserve task IDs, badge IDs, accounts and progress; SVG assets are included in static serving, packaging and CI startup checks.

## 0.12.7

- Enforce a shared 15-second child undo window on the server and in both the checklist and quick Undo action. Reloads and duplicate completion requests do not extend the window.
- Keep completed tasks checked after expiry; parents can still reopen and confirm them. Parent-confirmed and pre-update completions have no child undo window.
- Restore only the remaining undo time after reload and automatically disable expired checklist controls. The former keyboard-focus extension no longer applies.

## 0.12.6

- Moved the parent account's language and Sign out into the Settings page (next to the color theme), matching the child Settings page, and removed the separate account-name dropdown from the parent header.
- Replaced the parent header's account dropdown with compact Family and Settings icon buttons, so the main navigation row only carries the child-scoped tabs (and the child picker). This shrinks the navigation bar on small screens.

## 0.12.5

- Added a Plain task icons setting under Family → Child support settings. When on, task icons show in a single neutral color instead of full color, on the child's home screen, checklist and earlier-steps list.

## 0.12.4

- Keep Come back later tasks outside automatic focus after refresh or reload, even when their scheduled time is current. Children can explicitly choose them again from the collapsed list.
- Label the collapsed list For later when it also contains deferred current/future tasks; keep From earlier for older tasks.

## 0.12.3

- Label steps as Later today, Now (up to 30 minutes after their scheduled time) or Still open, without overdue warnings.
- Prioritize current tasks on the child home screen and keep older unfinished tasks in a collapsed From earlier section with a Do next action.
- Refresh time-based selection without reloading the page; retain manual choice for the current child/day until completion or deferral.

## 0.12.2

- Keep corrected task titles, icons, times and instructions visible on the child home screen while awaiting parental confirmation, including when other tasks remain.
- Unify Overview and Review: reopening removes points and locks the step until a parent confirms completion, with the same audit trail and no duplicate rewards.
- Use explicit parent action labels and explain the correction flow in English and German.

## 0.12.1

- Fix the web interface URL template to use Home Assistant's required port placeholder so Supervisor can load Wusel in the store.
- Validate Supervisor URL placeholder syntax and the listener port in CI, with a regression for the rejected fixed-port form.

## 0.12.0

- Use wusel consistently for the Home Assistant slug, SQLite database, environment variables, request header, session cookie and browser preferences.
- Remove prior identity compatibility instructions and remaining old branding keys.
- Clean installation required; previous application identities/data are not migrated.

## 0.11.0

- Add parent task-writing guidance and an optional first small action.
- Add progressive child help with ask-an-adult guidance and persistent day-only deferral behind other unfinished steps.
- Add parent-controlled series visibility and quiet rewards per child; retain earned progress and normal defaults on upgrade.
- Use neutral correction wording while preserving parent reopen/restore controls.
- Reset support preferences and deferrals with child progress while keeping task guidance.

## 0.10.0

- Add 13 optional task icons, including medicine, with English/German labels and no icon by default.
- Show icons beside task text in child focus/checklist and weekly/parent task views.
- Preserve icons through scheduled edits, restarts and child resets; migrate existing tasks without changing their appearance or progress.

## 0.9.0

- Distinguish due and future child steps using the configured timezone, without locking early completion.
- Offer direct undo after saved child completions without point farming.
- Show saving, saved, failed and offline states with request timeouts and safe state-only reconnection; reject completions from a stale displayed date.
- Persist one next badge goal until earned, and reveal full award dates on demand in readable text.
- Name the affected child and timing in parent confirmations; show form errors inline.
- Add parent-managed rest-day ranges that neither increase nor break streaks, while leaving steps optional.
- Retain existing account progress on upgrade; child reset also clears pauses and the selected goal.

## 0.8.0

- Add parent-only child account reset with username and parent-password confirmation.
- Delete progress/history and personal settings atomically, revoke child sessions, retain all tasks and login details, and log the reset.
- Rename the Petrol color theme to Lagoon (German: Lagune), retaining its stored identifier and palette.

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
