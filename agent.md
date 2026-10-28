# Wusel: development and agent guide

This guide describes the current application and the conventions needed to change it safely. Read it alongside the code, the user's current request, `README.md` / `README.de.md`, `wusel/CHANGELOG.md` and `VALIDATION.md`. Current user instructions take precedence over this guide. Update this guide when behavior or workflows change.

## Product and UX

Wusel is a daily-routine app by **Wild & Weich**, designed for children who benefit from a simple, calm interface, including children with ADHD. It runs locally on Home Assistant OS, primarily on a Raspberry Pi 5, and is used from phones and tablets. It is not a clinical or medication-administration system.

- Multiple parent and child accounts belong to one local family installation. Every parent can manage every child; there is no separate family/tenant ownership model.
- Parents create routines, manage accounts and support preferences, review completions and correct badges. Children see only their own routines and progress.
- Show the current time in both parent and child headers (replacing the parent account name, with Family and Settings controls retained), using Wusel’s timezone and the device’s regional hours/minutes format. Update at minute boundaries and immediately on return from a hidden tab, independently of network requests, open forms and task actions. Do not announce clock ticks as live-region updates.
- Keep the child interface quiet: one main task, progressive help, optional icons, compact weather and level feedback, and settings behind a gear icon.
- Use neutral wording for missed steps and corrections. Never infer deliberate misbehavior from an inaccurate checkmark. Do not introduce shame, red overdue warnings, forced catch-up, automatic completion or loss of earned badges.
- Keep English and German complete. Use accessible names for icon controls, visible focus, readable wrapping and text accompanying decorative task icons.
- Preserve reduced reward feedback independently of the device's reduced-motion setting. Plain task icons are a separate per-child setting.

## Architecture and repository map

There is no frontend framework, Node package installation, transpilation or asset build step. Node is used for JavaScript regression tests.

| Location | Responsibility |
| --- | --- |
| `wusel/app.py` | Python 3.12 WSGI application, SQLite schema/migrations, authentication, JSON API, routines, progress, corrections and static-file allowlist |
| `wusel/server.py` | Production Waitress listener on port 8099, separate IPv4/IPv6 sockets where available |
| `wusel/weather.py` | Server-side Home Assistant weather adapter, bounded requests, caching and fallback |
| `wusel/static/app.js` | Rendering, navigation, client state, API requests, task selection, undo controls, feedback and themes |
| `wusel/static/icons.js` | Original bundled SVG registry and whitelist-based renderer for tasks, badges, weather and UI; no platform emoji, fonts or external icon requests |
| `wusel/static/i18n.js` | English/German catalogs, locale formatting, timezone-aware greetings and task-time classification |
| `wusel/static/style.css` | Layout and component styling |
| `wusel/static/themes.css` | Theme tokens and color overrides |
| `wusel/static/index.html` | Frontend entry point |
| `wusel/translations/*.json` | Home Assistant app option translations; separate from frontend translations |
| `wusel/config.yaml` | Home Assistant manifest, slug, architectures, network and options |
| `wusel/Dockerfile` | Python slim container, dependencies, runtime files and version label |
| `tests/test_*.py` | Standard-library unittest backend, migration, security, HTTP, weather and packaging regressions |
| `tests/test_*.cjs` | Node/VM frontend logic, rendering, translations and formatting regressions |
| `tools/validate.py` | Source, manifest, version, workflow and archive validation; development-only PyYAML dependency |
| `tools/package.py` | Source ZIP packaging, excluding private/runtime files |
| `tools/smoke.py` | Real HTTP startup, frontend asset and first-run API checks |
| `.github/workflows/ci.yml` | Tests, source validation, ZIP artifact and AMD64/ARM64 container checks |
| `VALIDATION.md` | Verification history and limitations, including use of demo data and emulated ARM64 |
| `work/`, `dist/`, `.venv/` | Ignored local artifacts; do not rely on them being present in a fresh clone |

Production dependencies are in `wusel/requirements.txt`: Waitress and tzdata. `requirements-dev.txt` includes them plus PyYAML. Node 22 and Python 3.12 are used by CI.

## Local development

Run commands from the repository root. Use a disposable local data directory, not a copied production database.

### Windows / PowerShell

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:PYTHONUTF8 = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:WUSEL_DATA = Join-Path $PWD "work\dev-data"
$env:WUSEL_DEV = "1"
.venv\Scripts\python.exe wusel/app.py
```

### Linux / macOS

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
WUSEL_DATA="$PWD/work/dev-data" WUSEL_DEV=1 .venv/bin/python wusel/app.py
```

Open `http://127.0.0.1:8099/`. The terminal prints the first-run setup code while no accounts exist. Development mode uses the standard-library server on localhost. Without `WUSEL_DEV=1`, the app uses the production Waitress listener.

| Setting | Meaning |
| --- | --- |
| `WUSEL_DATA` | Data directory; defaults to `/data` |
| `WUSEL_TIMEZONE` | Default `Europe/Zurich`; controls the day boundary and routine scheduling |
| `WUSEL_WEATHER_ENTITY` | Optional Home Assistant entity such as `weather.forecast_home` |
| `WUSEL_SECURE_COOKIE=1` | Secure cookie flag; requires HTTPS for normal browser use |
| `WUSEL_DEV=1` | Local development server |
| `SUPERVISOR_TOKEN` | Injected by Home Assistant for server-side weather access; never expose it to the browser |

`options.json` in the data directory supplies Home Assistant options. `timezone` and `weather_entity` override their environment defaults when present; the secure-cookie option or environment flag can enable secure cookies.

## Branding assets

The selected hedgehog is Wusel's fixed brand artwork. `wusel/static/wusel-logo.png` is the unchanged original; header images, favicons, Apple touch icon and Home Assistant `icon.png`/`logo.png` are exports from it. See [BRANDING.md](BRANDING.md) for filenames, regeneration and provenance. Do not silently redesign the hedgehog or replace it with a different generated concept. Functional task/weather/badge icons remain SVG; brand colors are independent of themes and plain task-icon mode. The optional Sharp exporter is development-only; generated assets are committed and require no image-processing dependency in production or CI.

## Tablet Home Screen support

`static/manifest.webmanifest` is public and explicitly allowlisted as `application/manifest+json`. It uses relative URLs resolving to the app root and existing 192/512 icons, and requests fullscreen with browser-defined fallback. The entry HTML includes Apple standalone/title/status-bar metadata. Keep local HTTP usable; Home Screen installation and fullscreen depend on browser/OS, with trusted HTTPS normally needed for standard PWA promotion. No service worker, offline cache, device locking or wake lock is implemented. Installed sessions retain the normal 12-hour expiry. Keep bilingual tablet setup guidance accurate.

## Identity, storage and authentication

- Home Assistant slug: `wusel`; local installation ID: `local_wusel`.
- SQLite database: `/data/wusel.sqlite3`; the app uses WAL and foreign keys.
- Setup code: randomly generated with `secrets.token_urlsafe(18)`, stored in `/data/setup-code`, retained across restarts. Setup is blocked once an account exists.
- Session cookie: `wusel_session`, HttpOnly, SameSite Strict, 12-hour expiration, optional Secure flag. Only a hash of each session token is stored in SQLite.
- Passwords: 4–128 characters for parents and children, salted PBKDF2-HMAC-SHA256 hashes with 600,000 iterations. Preserve authentication throttling and timing-safe comparisons.
- Mutations use JSON POSTs with `X-Wusel-Request: 1`; authenticated mutations also require the session's `X-CSRF-Token`.
- The browser stores its language fallback as `wusel-language`. Do not introduce aliases for the old application identity.
- Home Assistant authentication and Wusel accounts are separate. Do not assume a logged-in Home Assistant session grants Wusel parent access.
- Do not commit databases, setup codes, options, passwords, cookies, tokens, `.env` files or real family exports. Keep local screenshots and fixtures under ignored `work/`.

Schema migrations live in `Application.__init__` and must retain existing accounts, routines and progress. Do not modify the SQLite schema without testing both fresh startup and an existing database.

| Table | Meaning |
| --- | --- |
| `users` | Roles, credentials, language/theme and per-child support settings |
| `routines` | Schedule and task content, including optional icon and first action |
| `completions` | One record per routine/day, points, voided/locked state and persisted `undo_until` deadline |
| `daily_plans` | Historical daily task snapshots used for full-day and streak calculations |
| `pending_routines` | Edits scheduled to take effect later |
| `badges` | Earned milestones and parental revocation state |
| `rest_days` | Planned neutral days for streak calculations |
| `deferred_steps` | Per-child/day saved task deferral ordering |
| `live_revisions` | Persistent family/per-account change counters, maintained by transactional triggers |
| `sessions`, `attempts`, `audit` | Sessions, rate limiting and parent activity |

## Behavior to preserve

### Routines and scheduling

- Weekly plan columns use the available container width (minimum 160px per card, or one card on narrower screens), not viewport-only 7/4/2 breakpoints. Keep full weekday names and date numbers on one line, and normal task titles wrapping at word boundaries. Parent/child Settings share heading and language-picker spacing/alignment.
- Weekdays use Python's Monday-first numbering: Monday 0 through Sunday 6. All weekly views and editors start on Monday.
- Routines can repeat on selected weekdays or use a specific date. Keep backend validation and frontend choices aligned.
- New routines default to today. Edits and archives offer Apply today or From tomorrow; tomorrow is the default for edits.
- Apply today deliberately updates today's plan. Tomorrow edits leave today's task target intact and activate from their effective date.
- Historical daily plans must not change when a routine is edited or archived. Test changes across restart and midnight.
- Complete and defer requests include the displayed day; reject stale-day changes after midnight.

### Child task selection and help

- Before scheduled time: Later today / Später heute.
- At scheduled time through 30 minutes afterward: Now it's time / Jetzt dran.
- More than 30 minutes afterward: Still open / Noch offen. This is neutral, not a penalty.
- Prefer an available current task, then an upcoming one. Older unfinished tasks stay in a collapsed From earlier / Von vorhin list.
- Saved deferrals do not enter automatic focus again after reload. If the collapsed list contains current/future deferred tasks, label it For later / Für später.
- Do next explicitly selects a task for the current child/day and page session. Completion or another deferral ends that choice; no points or completion change merely from selecting it.
- Parent Overview shows `first_action` under task titles, matching the child’s main card; do not substitute `description` when no first action is set.
- I need help reveals existing task instructions. Ask an adult tells the child to seek a nearby adult; it does not send a message.
- Come back later persists the deferral for today, switches to another available step, and changes neither points nor completion. Disable it with an explanation when no other available step exists.
- Keep corrected-task title, optional icon, time, first action and description visible on the child's first page, including when other tasks remain.

### Completion, undo and parent corrections

- First completion earns 10 points; every 100 points advances a level. Duplicate taps and undo/recheck must not multiply points or replay initial reward animations.
- A child can undo their own completion for exactly 15 seconds, from either the quick Undo action or Mein Tag checklist. The server enforces the deadline.
- `completions.undo_until` persists across restart and sessions. Duplicate done requests do not extend it. A valid undo followed by recheck opens a new window without awarding extra points.
- The API returns remaining `undo_seconds`. The frontend accounts for request latency and uses monotonic browser time, rather than trusting the device's wall clock.
- Reload restores only the remaining window. Checklist controls disable automatically at expiry; keyboard focus does not extend the deadline.
- Parent-confirmed completions and pre-migration completions have no child undo window. Unfinished steps remain completable.
- Overview and Review share `correct_completion`: reopen removes points and locks completion; a parent confirms done to restore it. A child cannot bypass that lock.
- Parent corrections clear child undo eligibility. Both parent entry points retain the same audit and reward behavior.

### Rewards, rest days and reset

- Badge definitions and thresholds live in `app.py`: step milestones, full days and consecutive full days. Full days need at least one planned step and every planned step completed.
- Preserve earned badges across corrections. Parents can remove or restore badges separately.
- The next badge goal is stored per child, stays stable until earned or invalidated, and respects hidden series settings in child views.
- Rest days may be planned for today/future dates, up to 366 days per range. They neither increase nor interrupt streaks. Tasks remain optional and can still earn points. Past rest days are immutable.
- Per-child support includes focus/checklist home view, show series badges, quiet rewards and plain task icons. Hidden/reduced feedback does not delete earned progress.
- Child reset requires the child's username and the current parent's password. It deletes completions, rewards, daily/rest/deferral history, sessions and personal support preferences. It retains account/login details, all routines (including archived tasks), first-action/icon guidance, pending changes and the audit trail.

### Localization, icons, themes and weather

- Add frontend strings in both catalogs in `i18n.js`; avoid duplicate keys and preserve interpolation placeholders. Backend errors and audit text need translations too.
- Use full date/month/day names, browser regional date/time formatting, and whole-number displayed temperatures. A native time input may show AM/PM on an English-configured device.
- App timezone controls scheduling, greetings and time labels; it is separate from the browser's display locale. Check DST and midnight boundaries.
- Optional icons are shared backend/frontend IDs, including `medicine`, `piano`, `guitar`, `snack-box`, `homework`, `hairbrush`, `toilet`, `jacket` and `exercise` (21 task icons). The `snack-box` artwork is the selected open lunchbox with a sandwich and apple; retain its ID when changing artwork. Text remains present; decorative icons are hidden from assistive technology. Plain icons use the same SVG geometry with neutral color tokens rather than grayscale emoji. The task picker uses labeled radio options with SVG previews, and drafts must preserve the selected radio and picker disclosure when language or theme changes.
- Theme IDs are `forest`, `ocean`, `berry`, `lavender`, `sunshine`, `petrol`. The visible name for `petrol` is Lagoon / Lagune. Keep backend validation and frontend palettes aligned.
- Weather uses a configured `weather.*` entity and the fixed Supervisor Core API destination, with hourly forecast and daily fallback. Preserve request timeouts, bounded response sizes, cache/stale labels and nonblocking refresh locking. Never put the Supervisor token in frontend state or accept arbitrary weather request URLs.
- Keep today and tomorrow forecast data separate, date-stamped in Wusel’s timezone. Fetch hourly once for both days, with one daily fallback request when today lacks hours or tomorrow lacks morning/afternoon coverage. Bound each day to 25 hours for DST. Server request bounds, nonblocking cache refresh and token isolation remain unchanged; the browser allows 16 seconds for the weather-only request (other requests stay at 12 seconds).
- From 18:00, child focus/checklist weather shows Prepare for tomorrow, retaining today’s summary. Detail views offer Today/Tomorrow; parents can inspect tomorrow all day. Local minute/visibility updates preserve forecast selection and focus; midnight invalidates yesterday’s forecast dates and refreshes weather independently. Tomorrow advice uses only 06:00–18:59 hours, falling back to a labeled daily forecast. Do not use the daily overnight low alone for cold-clothing hints, blend today’s observations into tomorrow advice, invent missing values or show clothing hints for stale forecasts. No routines are generated automatically.
- Keep weather compact; it must not obscure the parent's tasks. Show unavailable/stale states honestly.

## API map

All mutations are POST. See `Application.dispatch` for exact body fields, authorization and errors.

| Endpoint | Access and role |
| --- | --- |
| `GET /health` | Public health check |
| `GET /api/state` | First-run state or authenticated profile/day data |
| `GET /api/updates` | Authenticated own-child or family revision/day/timezone; cheap read-only polling |
| `GET /api/weather` | Authenticated weather |
| `/api/setup`, `/api/login` | First parent setup and sign-in, with throttling |
| `/api/logout`, `/api/preferences` | Authenticated session and own preferences |
| `/api/complete`, `/api/defer` | Own scheduled child tasks, or authorized parent; day and lock checks apply |
| `/api/users`, `/api/password`, `/api/child-settings` | Parent account/support administration |
| `/api/routines`, `/api/archive`, `/api/rest-days` | Parent planning |
| `/api/correct`, `/api/badge`, `/api/reset-child` | Parent correction, badges and progress reset |

Keep authorization in the backend. Hiding a control is not access control. Preserve child isolation, atomic writes, idempotency, request-size limits and parameterized SQL.

## Live updates

See [LIVE_UPDATES_PLAN.md](LIVE_UPDATES_PLAN.md) for the implemented contract. Both roles poll authenticated `GET /api/updates` every 10 seconds while visible. Parent markers use the family scope; child markers expose only their own account. The endpoint reads revision/day/timezone without activating pending changes, calculating state or loading weather. Full state reads activate due changes and return a consistent revision under a transaction.

`live_revisions` is maintained by SQLite triggers on profile/planning/progress/audit tables, in the same transaction as the change. Rollbacks cannot publish revisions; session/rate-limit writes do not cause state churn. Avoid unconditional updates during state construction (especially an already-empty badge goal), or polling will continually fetch full state.

The client serializes state reads and uses a mutation epoch to discard superseded snapshots. It never automatically replays POSTs. Busy actions queue checks, hidden tabs pause, visibility/online events recheck immediately, and failures back off to 20/30 seconds. Weather keeps its existing independent cache cadence. Changed state is patched into the DOM, preserving keyed tasks/badges, form drafts and radio values, caret, disclosures, focused help and scroll. Open confirmation dialogs defer remote application until closed. Expired sessions return to sign-in. Preserve server-derived remaining undo time and never celebrate remote completions.

## Testing and verification

With the virtual environment activated (or replace `python` below with its interpreter path):

```sh
python -m unittest discover -s tests -q
node --check wusel/static/icons.js
node --check wusel/static/app.js
node --check wusel/static/i18n.js
```

Run every Node regression, not just one file:

```powershell
Get-ChildItem tests/test_*.cjs | ForEach-Object { node $_.FullName }
```

```sh
for test in tests/test_*.cjs; do node "$test"; done
```

Then validate and package, using the actual manifest version:

```sh
python tools/validate.py
python tools/package.py
python tools/validate.py --archive dist/wusel-VERSION.zip
```

- The Python `tests/test_app.py` Client calls the real WSGI app, carries cookies/CSRF and supplies the custom request header. Use temporary data and injected `today`/`now` clocks for deterministic logic tests.
- Add meaningful coverage for changed behavior, especially permissions, migrations, timing boundaries, duplicate requests, restart and day rollover. Avoid tests that only repeat implementation constants.
- Run focused tests while developing; use the full suite for backend/security changes and the complete GitHub pipeline for a release. Frontend changes require relevant Node regressions and browser verification of affected flows.
- On restricted Windows environments, loopback integration checks can fail with WinError 10013. Distinguish a sandbox restriction from an application failure and rerun the affected HTTP checks with appropriate local networking access.
- Test UI changes in real Chrome with disposable local data, at phone width (for example 390 x 844), plus wider layouts where relevant. Inspect screenshots, overflow, keyboard focus and JavaScript errors. Check English and German and relevant support settings.
- Existing `work/` scripts/screenshots are optional local helpers, not a portable test dependency. Do not use real children's accounts to create test completions or resets.
- Document the tests actually run and their limits in `VALIDATION.md`. Do not claim physical Pi validation from a QEMU build.

## CI and release workflow

When changing user-visible behavior, setup, configuration or deployment, update the affected README and DOCS files in both English and German. Keep their descriptions aligned with implemented behavior; documentation-only changes do not require a version bump.

1. Inspect `git status` and current instructions. Preserve unrelated changes. Use `codex/` for a new working branch unless the user specifies otherwise.
2. Make the authorized change, update relevant tests and documentation, and inspect the diff. Keep current product semantics unless the user asks to change them.
3. For an application release, advance the semantic version consistently in `wusel/config.yaml`, `wusel/Dockerfile` (`BUILD_VERSION`), the six English/German README/DOCS files and their current ZIP references. Add a changelog entry. Preserve historical changelog/validation versions.
4. For documentation-only changes, update the guide/docs without inventing a runtime release. Include the guide in source packaging.
5. Run appropriate checks and build/validate the source ZIP. Commit and push according to the user's authorized repository/branch workflow; do not claim a push or deployment before it succeeds.
6. Check GitHub Actions for the published revision. Report failures or pending work accurately.

CI runs on main pushes, pull requests and manual dispatch. The quality job validates metadata, runs all Python and Node tests, builds/validates the source ZIP and uploads an artifact. Dependent container jobs build AMD64 and ARM64, then check real HTTP startup; ARM64 uses QEMU. Actions are pinned to commit SHAs and repository permissions are read-only. No image is pushed to a registry and nothing is automatically deployed to the Pi.

## Home Assistant deployment and troubleshooting

- Install the **inner `wusel` app folder**, whose immediate contents include `config.yaml`, `Dockerfile`, `app.py`, `server.py`, `weather.py`, `requirements.txt` and `static/`.
- With the default source archive, that app manifest is at `wusel/wusel/config.yaml` inside the ZIP. Copy the app contents to `/local_apps/wusel` (or `/addons/wusel` on installations using that mount name).
- The 1.0.0 manifest explicitly uses `stage: stable`; version numbers and Home Assistant lifecycle labels are separate metadata. Keep the stage aligned with the intended release status.
- Preserve `slug: wusel` on updates. Do not uninstall to perform an ordinary update; its persistent data belongs to the installed app.
- The manifest uses `host_network: true`, `init: true` and exactly `webui: "http://[HOST]:[PORT:8099]/"`. A literal port in the webui template is rejected by Supervisor, even though host networking is enabled. Keep this regression covered.
- No ingress is configured. The web interface is reached directly on the Pi's port 8099, for example `http://homeassistant.local:8099/` or the Pi's numeric IP.
- Copy all changed runtime files, including `static/`, then reload the app store, update/rebuild Wusel and wait for it to finish. Restarting an existing container alone does not replace the files built into it.
- Home Assistant's installed version and the README's version can differ during an update: README text is not evidence of the running container version.
- If the UI still shows old behavior, inspect the served static JavaScript and installation/rebuild status before blaming browser caching. `/health` should return `{"ok":true}`; startup logs show listener addresses and `Wusel ready: HTTP port 8099`.
- Store reload timeouts and "already a task in progress" are Supervisor/store problems. Read Supervisor logs and check the source manifest; do not promise that renaming an app or changing frontend files fixes the store.
- Each Home Assistant app has its own `/data` mount. Studio Code Server's `/data` is not Wusel's `/data`. Use supported backup/container access rather than assuming identical paths across apps.
- Manifest backups are `cold` so SQLite data is backed up while stopped. Preserve setup-code and database files as private installation data.
- Do not open router ports, disable protection mode or expose family HTTP traffic publicly as a routine troubleshooting step. Configure HTTPS and secure cookies coherently if secure access is required.

## When finishing work

Report the actual behavior changed, how it was verified, the published version or commit when relevant, and any remaining deployment step. Keep the user response concise. A successful repository push or CI run is not the same as an updated Home Assistant installation.
