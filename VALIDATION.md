# Validation history

## 0.12.7 validation

- Added a persisted undo deadline per completion, with a 15-second server-enforced window for child-created completions. Duplicate checks preserve the deadline, valid undo/recheck does not duplicate points, and parental actions clear child undo eligibility. Migration preserves existing completion and reward data without reopening an undo window.
- All 108 Python tests passed, including seven new tests for the exact deadline, recheck rewards, duplicate requests, restart/session persistence, expired parent corrections, parent-created completions and migration with retained progress.
- All JavaScript regressions passed. New checks cover checklist and quick Undo expiry, server-provided remaining time after reload, independent overlapping windows, parent-confirmed tasks, and open tasks remaining completable.
- Chrome at 390 x 844 with the real WSGI backend passed checklist undo/recheck during the window, reload with only remaining time, strict automatic expiry even with keyboard focus, blocked direct API undo after expiry, reload after expiry, parental reopen/restore, retained points and no overflow or JavaScript errors. Screenshot visually inspected. Only local demo data was used.
- Source metadata and the 0.12.7 ZIP passed validation; GitHub Actions runs all tests and AMD64/ARM64 container startup checks.

## 0.12.6 validation

- Consolidated the parent account's personal controls (language, color theme, Sign out) into the Settings page, matching the child Settings page, and removed the header's account-name dropdown in favor of compact Family/Settings icon buttons.
- Python regressions (101 tests via `unittest discover`) passed unchanged, confirming no backend/API behavior was affected by this frontend-only change.
- Node i18n regressions passed; no new strings were needed since existing Family/Settings/Sign out/Language labels were reused.
- Chrome with the real WSGI backend verified: header shows Family/Settings icon buttons with active-state highlighting, Settings page now includes language and Sign out, and the parent navigation row at 390 x 844 no longer wraps across 3 rows (child picker + 4 child-scoped tabs only, down from 6 buttons plus a full-width select). Source metadata and the 0.12.6 version/changelog checks passed.

## 0.12.5 validation

- Added a per-child Plain task icons support setting (default off) that renders task icons in grayscale on the child's home screen, checklist and earlier-steps list, without affecting badges or other colors.
- Python regressions passed for setting persistence across restart, parent-only/CSRF-protected changes, boolean validation, reset-to-default, and safe migration when upgrading from a database missing the column.
- Node i18n regressions passed, confirming the new English/German strings and catalog parity.
- Chrome with the real WSGI backend and demo family data verified the toggle in Family → Child support settings, grayscale icon rendering on reload, and no change when the setting is off. Source metadata and the 0.12.5 version/changelog checks passed.

## 0.12.4 validation

- Time-aware focus now excludes saved deferrals from automatic selection, including after reload. Explicit Do next remains available. The collapsed list uses For later when it contains deferred current/future tasks.
- Node regressions passed for deferred-current versus upcoming priority, simulated reload with cleared page choice, explicit reselection, deferred-only state and German labeling, together with all existing time, translation, correction and badge regressions.
- Chrome at 390 x 844 with real WSGI demo data verified deferring a task still within its current window, unchanged selection after reload, discoverable deferred-task details, explicit reselection, no points before completion and normal points afterward. No overflow or JavaScript errors; screenshot visually inspected.
- Focused metadata/package tests and the 0.12.4 source archive passed validation. GitHub Actions runs all backend checks and both architecture builds.

## 0.12.3 validation

- Added neutral time windows and time-aware focus selection. Earlier unfinished steps stay available in a collapsed section, with explicit Do next selection scoped to the current child/day and page session. No backend completion or reward changes.
- Node tests passed for 30/31-minute boundaries, configured timezones, current-before-future priority, older-only and mixed tasks, manual choice, child/day isolation, completed/locked exclusions, deferral ordering, rest days, escaping, English/German rendering and existing correction/badge regressions.
- Chrome at 390 x 844 with the real WSGI backend and a controlled browser clock passed collapsed earlier tasks, manual selection without points, completion, transition to Still open via unchanged-state refresh, live future-to-current transition while preserving an open disclosure, deferral, earlier-only state and no horizontal overflow or JavaScript errors. Screenshots were visually inspected. All data was local demo data.
- Source metadata, focused manifest/package regressions and the 0.12.3 source ZIP passed validation. GitHub Actions runs the full backend suite plus AMD64 and ARM64 container build/startup checks.

## 0.12.2 validation

- Unified parent Overview and Review corrections through the same backend helper. New lifecycle coverage checks reopening/restoring across both routes, child lock enforcement, points and audit records.
- The full 101-test Python run passed 100 checks and exposed an obsolete fixed-port manifest assertion from 0.12.1. That assertion was corrected and passed a focused rerun alongside the correction lifecycle test. CI reruns the complete suite.
- Node checks passed for English/German corrected-task details (only pending tasks, mixed tasks, multiple pending steps and rest days), explicit parent controls, escaping, translations and existing badge regressions.
- Chrome at 390 x 844 with the real WSGI backend passed task details and instructions on the child home screen, Overview reopen, Review confirmation and Overview confirmation, correct points and no overflow or JavaScript errors. Screenshots were visually inspected. Only local demo data was used.
- Source metadata and the 0.12.2 source package passed validation; GitHub Actions builds and checks both container architectures.

## 0.12.1 validation

- Fixed the Supervisor-rejected webui URL: the host-network manifest now uses the required port placeholder. The earlier validator accepted the invalid literal port and did not validate this Supervisor constraint.
- Six focused metadata/packaging tests passed, including a regression rejecting literal ports, incorrect listener ports, missing host placeholders and missing values. Source metadata and the 0.12.1 ZIP passed validation.
- AMD64 and ARM64 container checks and the complete test suite run in GitHub Actions; store loading on the actual Pi still requires replacing the local manifest and reloading the store.

## 0.12.0 validation

- Renamed the Home Assistant identity, database, environment variables, request header, session cookie, browser language storage and remaining internal branding to Wusel. No tracked file contents or paths retain the prior garden name.
- All 98 existing Python tests passed with local HTTP access enabled. The new clean-install environment regression passed separately (99 total); persistence checks also verify the new database and cookie identifiers.
- Node translation, formatting, greeting, optional-icon and badge-view regressions passed, plus JavaScript syntax checks.
- Metadata/version checks and the 0.12.0 source ZIP validation passed. This release requires a fresh installation; no live Home Assistant data was modified.
- Container builds and startup checks for AMD64 and ARM64 run in GitHub Actions. ARM64 validation uses QEMU, not a physical Pi.


## CI pipeline validation

- Added read-only, commit-pinned GitHub Actions for pull requests, main pushes and manual runs, with gated AMD64/ARM64 image builds and fresh-container HTTP checks.
- Local metadata/version/YAML/JSON/Python-syntax checks and packaged-source validation passed. Five CI-tool regressions passed, including duplicate YAML rejection, missing/private/traversal archive rejection and real HTTP smoke checks against both fresh and initialized local application data.
- Existing 93 backend tests and JavaScript regressions passed for 0.11.0. The CI run installs development dependencies and runs all 98 Python tests plus Node checks.
- Both image builds and boot checks execute on GitHub-hosted Linux; ARM64 uses QEMU rather than physical Pi hardware. Current results and downloadable source packages: https://github.com/santsamu/wusel/actions/workflows/ci.yml . The pipeline does not publish images or modify the installed Pi.


## 0.11.0 validation

- All 93 Python tests passed, including eight new support tests for first-action validation and scheduled/restarted edits, deferral ordering without points/completion, restart/day boundaries, child isolation/CSRF/stale-day/completed/locked/last-step rejection, atomic parent-only preferences, retained hidden-series awards and eligible goals, reset cleanup and migration with retained progress.
- Node catalog and badge-view regressions passed, including child-hidden/parent-visible series.
- Chrome at 390 × 844 with the actual WSGI backend passed first-action display, progressive guidance, ask-an-adult instruction, persistent deferral across reloads, optional series visibility with retained parent records, quiet reward acknowledgement and a level-up without point/celebration markers while device reduced motion was off, last-step explanation, neutral locked correction and parental restoration. Help, quiet feedback and neutral correction screens were visually inspected. No overflow or JavaScript errors; local demo data only.
- Built wusel-0.11.0.zip. No live Pi accounts or configuration modified.


## 0.10.0 validation

- All 85 backend checks passed across the full suite and focused rerun. Six icon regressions cover default/allowed choices including medicine, frontend/backend choice parity, invalid-value atomicity, child authorization, today/tomorrow behavior, restart, legacy edits, reset preservation, explicit removal and migration with retained points/old pending edits. The final focused icon/catalog run passed all nine checks after fixing a missing test import.
- The HTTP integration tests required an unrestricted rerun because Windows sandbox loopback access was blocked; those checks passed in the full rerun.
- Chrome at 360 × 844 with the actual WSGI backend passed 13 icon choices plus No icon, English/German medicine labels, icon/title draft preservation while changing language, persisted edits, child focus/checklist/week rendering, icon removal and no horizontal overflow or JavaScript errors. The medicine icon was visually inspected; text remained present and the decorative icon had aria-hidden. All data was local demo data.
- Node translation/format/greeting, optional-icon and badge-view checks passed. Built wusel-0.10.0.zip; no live Pi data changed.


## 0.9.0 validation

- All 79 Python tests passed. New tests cover neutral rest-day gaps, full-day totals on optional-task days, current-series grace, stable goal selection across changes/restart/earning/revocation, rest-day add/remove permissions and validation, account isolation, reset cleanup, stale-date completion rejection and migration without losing points or badges.
- Node checks passed 230 direct UI lookups, task timing boundaries/timezones, grouped rest-range API limits, stable-goal rendering and existing badge/language/greeting checks.
- Chrome with the actual WSGI backend and local demo accounts passed due/later transitions, saving status, direct undo/recheck without extra points, aborted requests before saving and lost responses after saving, state-only reconciliation without duplicate completion POSTs, background offline status/retry, a 12-second hung-request timeout releasing controls, stable badge targets, parent rest-range planning/removal, optional rest-day tasks preserving streaks, parent messages naming the child and timing, and inline invalid-range errors.
- Child focus/checklist greeting and quiet-refresh focus retention passed in English/German at 390 × 844. Readable earned-date disclosures were checked at phone and 960-pixel widths with no overflow; child feedback, rest-day and badge-detail screenshots were visually inspected. No JavaScript errors.
- Built wusel-0.9.0.zip. No live Pi accounts, progress or configuration were changed during validation.


## 0.8.0 validation

- All 70 Python tests passed. Four new reset tests cover atomic rejection of wrong confirmation/password, parent-only access, CSRF, invalid targets, deleting progress/plans/settings/sessions, exact preservation of task rows and pending changes, retained credentials, isolation of other accounts, audit records, repeat reset, restart, no old badges reappearing and fresh point earning.
- Chrome at 390 × 844 used the actual WSGI backend with local demo accounts: child-specific confirmation, cancel preserving 20 points, invalid username leaving the dialog open, successful reset, retained pending task edit, child-session revocation, login with the original password, zero points/default settings and the German Lagune label. No horizontal overflow or JavaScript errors; the confirmation dialog was visually inspected.
- Node translation, format, greeting, reset-audit/Lagoon naming and badge-view checks passed. No live Pi data was reset.


## 0.7.3 validation

- All seven theme tests and three catalog tests passed. Theme tests now include Petrol in the allowlist and exercise its persistence across restart/login. Existing isolation, partial updates, invalid inputs, migration and authorization checks passed.
- Chrome at 390 × 844 with the actual WSGI backend passed parent/child selection of Petrol, six options, reload persistence, theme-color meta update, CSS accent and account isolation. No overflow or JavaScript errors. The parent screen was visually inspected using local demo data.
- Main checked Petrol contrast ratios: white/button 6.79:1, body/paper 10.42:1, muted/soft 4.53:1, accent/soft 5.68:1. These are targeted palette checks.
- Node translation, regional format, greeting and badge-view checks passed.


## 0.7.2 validation

- Node tests passed greeting time boundaries, configured timezone differences, summer offset and English/German interpolation, plus existing translation/format and badge-view regressions.
- Chrome at 390 × 844 passed English/German focus and checklist views: morning/day/evening/night greetings, updates on unchanged-state refreshes, retained task-button focus and heading DOM node, no overflow or JavaScript errors. Browser timezone was New York while Wusel used Zurich, confirming the app setting controls the greeting. The German evening screen was visually inspected with local demo data.
- JavaScript syntax and Python catalog checks passed. No backend changes.


## 0.7.1 validation

- Chrome checks passed at 360, 390, 960 and 1280 pixels: child selector aligned with the first menu item, redundant visible labels removed, language/child switching, management routing, account-menu focus/Escape/outside dismissal and no horizontal overflow or JavaScript errors.
- German earned badge dates were checked in 3-column grids at 960/1280 pixels and 2-column phone grids. Every pill stayed within its card content width; full dates were retained. Phone and 3-column screenshots were visually inspected using local demo data.
- JavaScript syntax, Node badge-view regression tests and translation/format checks passed (209 direct UI lookups), plus Python catalog checks. No backend changes.


## 0.7.0 validation

- All 65 existing and new backend tests passed, followed by one additional legacy-upgrade regression (66 total). Coverage includes queued edit/archive timing, stable today targets, intentional immediate changes, future tasks rejected today, replacement of pending edits, restart activation, invalid timing, child authorization and badge progress units. The upgrade test retained routines, points, full days and sessions from a database without the new schema.
- Node badge-view regressions passed for closest-progress selection, empty/all-earned views, retained revocation, parent-only controls and German labels. Translation/format checks passed (212 direct UI lookups).
- Chrome at 390 × 844 used the actual WSGI backend through a local request adapter: edited and archived a routine for tomorrow, verified today's task remained, deliberately archived today, and checked the focused badge view, 1-of-3 progress, two earned badges, collapsed/grouped 17-badge collection and parent-only controls. Each request recreated the application, exercising persisted pending changes. No JavaScript errors or horizontal overflow; the child view was visually inspected. All data was local demo data.
- Built wusel-0.7.0.zip. Not deployed to the Pi by these checks.


## 0.6.2 validation

- Chrome at 390 × 844 passed German and English child settings-icon checks: no visible label, localized accessible name and tooltip, touch target at least 44 × 44 pixels, keyboard activation, settings-page navigation, current-page state and return to the child's day. No horizontal overflow or JavaScript errors. The German screen was visually inspected.
- Node catalog and regional-format checks passed (199 direct UI lookups). No backend changes.


## 0.6.1 validation

- Chrome checks at 360, 390 and 1280 pixels passed: separate child and administration navigation, child switching and context labels, active-tab scope, Family/Settings routing, collapsed account menu, English/German language changes with retained focus, Escape and outside-click dismissal, and no horizontal overflow or JavaScript errors. Phone and desktop views were visually inspected. Local demo account/weather data only.
- JavaScript syntax, Node translation/format checks and Python catalog checks passed. Backend behavior is unchanged from the 58-test 0.6.0 run.


## 0.6.0 validation

- All 58 Python tests passed. New cases cover partial/empty/missing days, consecutive calendar days across the year boundary, every full-day/streak threshold through 30, today's unfinished-day grace, undo/recheck, historical correction/restore, retained revocation, routine archival/edits, restart, account isolation and safe legacy step-badge backfill.
- Parent revoke/restore of special badges passed; child requests were rejected.
- Node catalog and format checks passed (195 direct UI lookups).
- Chrome at 390 × 844 passed both child and parent badge views: 17 cards, translated streak requirement, earned state, controls restricted to parents, no overflow or JavaScript errors. The child view was visually inspected using demo award data.
- Daily plans are recorded from this release onward; historical full-day awards are not inferred from incomplete legacy evidence. No live Pi data was modified.


## 0.5.3 validation

- Parent weather: Chrome checks at 390 and 1280 pixels passed. The forecast starts collapsed under 110 pixels high, the first task fits within an 844-pixel viewport, details expand/collapse, an open forecast stays open after weather refresh, and only one weather-panel ID exists. No horizontal overflow or JavaScript errors. The mobile result was visually inspected with demo weather.

- All 50 Python tests passed, including four-character passwords for both account roles, initial setup, password resets and rejection of three-character passwords.
- Node translation checks passed for 190 direct UI lookups, plus regional formatting checks for en-US and de-CH independently of interface language, timezone-aware timestamps, full month/weekday names and rounded temperatures.
- Chrome at 390 × 844 passed child-screen date/time and integer weather checks for de-CH and en-US. Both weekly plans had no horizontal overflow or JavaScript errors; the German weekly plan was visually inspected. Weather was a local demo fixture.
- Built wusel-0.5.3.zip. Changes have not been installed on the Pi.


## Passed

- IPv6 release: all 48 tests passed with the exact Waitress 3.0.2 production dependency installed. Five new checks cover the host-network manifest and real production HTTP requests over IPv4 and IPv6 for health, the application page, styles, and state API. Neither address family was skipped.
- A separate subprocess launched the actual app.py production entry point on port 8099. Both http://127.0.0.1:8099/health and http://[::1]:8099/health returned HTTP 200 and {"ok":true}. The log printed both listener addresses and the explicit readiness message. The temporary server was stopped after checking.
- Home Assistant configuration now uses host networking and a fixed 8099 web URL, so the host's IPv6 interfaces are reachable without depending on Docker's IPv4 port publishing. Docker init is enabled for the standard Python base image.

## Deployment boundary for 0.5.2

The new production HTTP server was tested on this Windows workstation, including both address families. The updated ARM64 container and Home Assistant host-network mode have not yet been deployed/tested on the Pi. Install/update/rebuild to 0.5.2, then check the hostname health URL from a client on the same LAN. The existing app ID and data volume were preserved. No live accounts, configuration, or files on the user's Pi were modified by this release work.

## Earlier feature checks

- Path cleanup release: all 43 backend tests and the Node translation checks passed using the renamed wusel source folder. A browser smoke check passed login, retained progress and theme, static styles, and all five theme options. Project/import paths, helper-script references, historical ZIP names, and ZIP member paths were audited. English/German READMEs and app docs were recreated. Home Assistant’s compatibility ID remains unchanged; it is not a source path.

- Theme update: all 43 backend tests passed. Seven additional theme scenarios cover all allowed values, persistence across restart/login, account isolation, preservation of language and theme during partial updates, atomic rejection of invalid updates, authentication/CSRF, and migration with retained account data.
- Chrome/Chromium browser checks passed for all five palettes at 390 × 844: selected check marks, English/German labels, main Done button above the fold, no horizontal overflow, saved preference after reload, another device, separate child accounts, sign-out/account switching, and parent Settings at desktop size. No page errors. Theme picker, Ocean, and Berry previews were visually inspected.
- Main button and primary text color pairs were calculated for all five palettes. Minimum among the checked pairs was 5.15:1; each exceeded 4.5:1. This is a targeted palette check, not a full accessibility audit.

- Wusel branding checked in the browser: title, login, child header, English/German company byline, retained account progress, no overflow, and Done still visible above the fold. The branding update does not change the app slug, database, or account logic. The branding check preceded the theme update; the full 43-test suite was rerun for the theme changes.

- Reward UI in Chrome/Chromium on a 390 × 844 phone viewport: small level bar, Done above the fold, animated +10, level 1 → 2 celebration and bar wrap, no replay on reload/undo/recheck, new points in checklist mode, German messages, reduced-motion feedback with all reward movement disabled, and no horizontal overflow. No JavaScript page errors. Screenshots of the bar, point gain, and new-level state were visually inspected.
- Two new backend tests verify that exactly one first-completion reward event is emitted, including eight concurrent requests, and that undo/recheck does not produce another earned-points event.

- New quiet child experience in Chrome/Chromium at 390 × 844 and 1024 × 900: exactly one task card, Done button visible on the first phone screen, no large rewards panel, footer, navigation, or language selector on the home screen, English/German Settings, compact weather with tap-through details, brief success before advancement, new-badge-only notification, all-done state, checklist undo, and parent choice of default focus/checklist view.
- Four additional backend scenarios cover default home view, persistence, per-child isolation, child/anonymous rejection, validation, CSRF, and migration of existing accounts.

- 43 Python unittest scenarios: original routine and account behavior, migration from the old user schema, saved language preferences, per-account isolation, CSRF protection for preferences, weather endpoint authentication, hourly filtering to the remaining local day, daily fallback, missing forecasts and temperatures, caching and expired data, stale observations, outage behavior, and fixed Supervisor API request/auth/timeout construction.
- Translation checks cover English/German key parity, interpolation fields, every static backend error, and 190 direct UI translation lookups. A separate Node catalog/interpolation check also passed.
- JavaScript and Python syntax checks passed.
- Chrome/Chromium browser checks at tablet (1280 × 1100) and phone (390 × 844) sizes: English/German rendering, language persistence after reload, preserving unfinished routine forms through a language switch, leaving entered routine content unchanged, localized badges/login errors, daily task completion, current/hourly weather, daily-only fallback, current-only weather, stale warnings with advice suppressed, and unavailable/unconfigured weather while routines remain usable. No JavaScript page errors. No horizontal overflow in phone day/plan views.
- New English and German quiet-home screenshots were rendered and visually inspected. Preview weather is visibly labelled as example data; no sample accounts, credentials, or weather database are included in the ZIP.

## Test boundaries

Browser requests were fulfilled by a local process adapter calling the real WSGI application and SQLite storage, because this environment blocks browser loopback networking. Weather responses were controlled fixtures supplied to the real weather adapter. Tests cover the UI, authentication cookies, application API, parsing, and fallback logic; they do not establish a live Home Assistant network connection.

Docker/ARM64 building, the updated Home Assistant Supervisor installation/network mode, real weather-provider capabilities, and backup/restore on the Pi have not been tested. Production Waitress HTTP over IPv4/IPv6 is now tested locally as described above. The Docker daemon is unavailable here and the Pi is not connected.

## On-device acceptance

1. Back up the existing app and update to 0.5.2 without removing its data volume.
2. Verify existing users, schedules, points, and badges remain intact.
3. Change one child's language to German, sign in from another device, and verify the saved language and isolation from other children.
4. Configure weather_entity with your actual weather entity ID, restart, and verify current temperature/units/location and local forecast times.
5. Verify hourly forecasts if your provider supports them; otherwise confirm the clearly labelled daily fallback.
6. Check that check-offs still work during a weather-provider outage.
7. Restart, then back up/restore the app and confirm data persists.

Parent review of locked tasks, restoration, and an empty child day were also checked in the browser. Live Home Assistant and Pi validation remain pending.
