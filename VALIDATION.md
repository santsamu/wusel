# Validation — version 0.5.2, 25 October 2026

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
