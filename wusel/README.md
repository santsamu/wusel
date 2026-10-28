# Wusel

**von Wild & Weich · Version 1.0.1**

Home Assistant marks this release as stable.

Wusel includes a custom AppArmor profile (`apparmor.txt` beside `config.yaml`). It allows the required Python runtime, read-only app files, private `/data` writes/locks, and TCP/DNS for the interface and weather. Shell execution, app-code changes and access to unrelated data directories are not allowed. It does not restrict TCP destinations. A 5/8 security rating is expected after Home Assistant OS successfully loads the profile; direct network access is retained. Copy the profile with all app files. Linux CI checks actual AppArmor enforcement; final target-device validation is still required.

Version 0.12.0 uses the app identity `wusel` (`local_wusel` for local installations). This is a clean-install release with a new `/data/wusel.sqlite3` database, `WUSEL_*` environment variables and new session identifiers. Previous installation identities and data are not migrated. Copy the current inner app folder to `/local_apps/wusel` (or `/addons/wusel`), reload the store and install Wusel fresh. Create the first parent account using the setup code from the app logs.

The task editor suggests brief, concrete steps and offers an optional first small action, shown beneath the child’s task title. I need help reveals existing guidance; Ask an adult asks the child to seek a nearby adult and does not send a message. Come back later moves the step behind other unfinished steps for that day without completion or points; it is disabled with an explanation when no other available step exists. Under Family → Child support settings, parents can hide series badges and enable quiet rewards per child. Earned badges and points are retained; quiet rewards suppress point animations, level celebrations and badge messages independently of device motion settings. Corrections use neutral wording while retaining parental controls. Upgrade defaults preserve visible series and normal rewards. Child reset clears these preferences and deferrals, retaining tasks and guidance.

Visible parent and child screens check for changes every 10 seconds using lightweight authenticated revision markers. Full state is loaded only when needed. Changes appear without a reload, while form drafts, open help, focus, scroll position and remaining undo time are retained. Background tabs pause polling and recheck on return; connection failures back off without retrying saved actions. Changes meant for tomorrow still wait until tomorrow.

Wusel uses the selected petrol, cream and ochre hedgehog logo, with matching browser favicons, an Apple touch icon and Home Assistant icon/logo files. Functional icons use original bundled SVG artwork for tasks, badges, weather, navigation and status symbols. Shapes and colors no longer depend on the operating system emoji font, and no external icon service is needed. The task editor has a labeled, keyboard-accessible SVG picker. Plain task icons use identical shapes with a neutral palette; saved task IDs, badges and progress are retained.

The parent Overview shows the same first small action beneath the task title as the child’s main task card. Additional guidance remains available to the child under I need help.

From 18:00 in Wusel’s timezone, the child’s weather card also shows Prepare for tomorrow with a forecast and short clothing-preparation hints. The detail view offers Today/Tomorrow; parents can open tomorrow’s forecast at any time. Tomorrow’s hints use only morning/daytime conditions (06:00–18:59), separately from today’s weather. Incomplete hourly coverage falls back to a labeled daily forecast where available; its overnight low alone does not trigger warm-clothing advice. Missing and stale forecasts are shown clearly. The view updates at evening and midnight while open; no routines are created automatically.

The current time appears in the header on every parent and child screen. On parent screens, it replaces the account name beside the Family and Settings controls. It uses Wusel’s timezone and the device’s regional time format, updates each minute, and refreshes immediately when returning to the app.

The snack-box icon shows an open lunchbox with a sandwich and apple. Parent Settings uses the same heading spacing and language-row alignment as child Settings. Weekly plan columns adapt to the available content width, keeping full weekday names and date numbers together.

Parents can choose from 21 optional task icons, including toothbrush, clothes, meal, schoolbag, bed, medicine, piano, guitar, snack box, homework, hairbrush, toilet, jacket and exercise. Parents choose it when creating or editing a task; No icon is the default. Icons accompany the task text in focus view, checklist and weekly plan. Apply today/From tomorrow also controls icon edits. The medicine icon is a visual reminder, not confirmation that a dose was taken. Under Family → Child support settings, parents can also switch a child's task icons to a single neutral color instead of full color.

Child screens use Later today before a scheduled time, Now for the following 30 minutes, and Still open afterward. The home screen prioritizes current steps, then upcoming ones. Older unfinished steps stay in a collapsed From earlier section; Do next brings one into focus without completing it. This explicit choice lasts for the current page session and child/day until completion or deferral. Time labels and selection update during the regular refresh, without reloading. Come back later also keeps the step out of automatic focus after reload; Do next can bring it back. When the collapsed list contains deferred current/future tasks, it is called For later. No task is automatically skipped or completed. Children can undo their own completions for exactly 15 seconds, using either the quick Undo action or the checklist. The server enforces the same deadline after reloads or across devices. Afterward only parents can reopen a completed step. Parent-confirmed completions and older completions from before this update cannot be undone by children. Unfinished steps can still be completed normally. Save/connection status is visible; uncertain saves are checked without automatic resubmission. The next badge goal stays stable until earned, with readable award dates available on demand. Parent confirmations name the child and effective timing. Weekly plan → Manage rest days lets parents plan or remove today/future date ranges. Rest days neither increase nor break a series; steps remain optional and completing them still earns points. Past rest days cannot be changed.

Parents can permanently reset a child account’s progress under Family. This removes completions, points, badges, day/streak history, planned rest days and personal settings, returning the child to level 1 and signing them out everywhere. Name, username, password and all created tasks (including archived tasks and pending changes) are kept. Confirmation requires the child username and the current parent password. The reset is recorded in the parent activity log.

When editing or archiving routines, parents choose Apply today or From tomorrow (the default). New routines default to today. Apply today deliberately updates today’s tasks and full-day target; From tomorrow leaves both unchanged today. Pending changes appear in the weekly plan and become effective from the selected date. Earned badges are retained. The badge screen starts with one next goal and progress, plus earned badges; See all badges expands the collection into Steps, Full days and Streaks.

17 badges celebrate steps (1, 5, 10, 20, 50, 100, 150, 250, 500, 1000), full days (1, 10, 30), and streaks (3, 7, 14, 30 consecutive calendar days). Full days start counting with version 0.6.0 and require at least one planned step and every step completed. Empty or incomplete days break a streak unless a rest day was planned; today has until midnight. Past daily plans survive later schedule edits. Corrections recalculate streaks; earned badges remain and parents can revoke them.

Parent and child passwords require at least 4 characters. Dates and times follow the browser’s regional format, with full month and weekday names. Temperatures are shown as whole numbers.

A calm routine app for children and parents, hosted locally on Home Assistant OS on a Raspberry Pi 5. Children use it in a phone or tablet browser.

[Deutsche Anleitung](README.de.md)

## Tablet Home Screen and fullscreen

Open Wusel directly at `http://homeassistant.local:8099/` (or the Pi's IP address) on the tablet. On iPad, use Safari → Share → Add to Home Screen, enable **Open as Web App** if offered, and launch the new Wusel icon. On Android, use the browser menu → **Add to Home screen** / **Install app**, then launch that icon. Menu names and support vary by browser and OS version. You may need to sign in again in the installed view; sessions still expire after 12 hours.

Wusel supplies a manifest and Apple Home Screen metadata with its existing hedgehog icons. The manifest requests fullscreen; browsers can fall back to standalone (without an address bar) or a normal browser view. System bars may remain. Existing shortcuts may need to be removed and added again after updating.

Local HTTP access remains supported. A Home Screen shortcut does not guarantee installation or fullscreen over HTTP; browsers normally require trusted HTTPS for standard PWA installation promotion. The localhost exception refers to the tablet itself, not the Pi. If your browser only creates a regular shortcut, use trusted HTTPS or a kiosk browser. HTTPS can stay within the home network; no router port forwarding is needed. Enable secure cookies only when using HTTPS consistently.

This adds no service worker or offline mode: the tablet must reach Wusel to load and save routines. It does not lock the device to Wusel or keep the screen awake. Use iPad Guided Access or an Android kiosk browser when those controls are needed.

## What is included

- One next task with a large **Done** button, an optional instruction, and a small daily count.
- A slim level bar, brief point feedback, and a small celebration for new levels. Reduced-motion settings are respected.
- A full checklist and badges available on request. Parents choose each child's default home view.
- Separate parent and child logins. All parents manage all children in this family installation.
- Routines for selected weekdays, weekends, every day, or one specific date.
- English and German, plus six personal themes: Forest, Ocean, Berry, Lavender, Sunshine, and Lagoon (petrol).
- A compact weather hint with a detailed forecast on request, using your existing Home Assistant weather entity.

## Folder layout

After extracting the ZIP, open the outer `wusel` project folder:

```text
wusel/
  README.md
  README.de.md
  VALIDATION.md
  wusel/                 # Copy this inner folder to Home Assistant
    config.yaml
    Dockerfile
    app.py
    weather.py
    server.py
    requirements.txt
    static/
    translations/
    DOCS.md
    DOCS.de.md
  tests/
  tools/package.py
```

## Install on Home Assistant OS

1. Use the **Samba share** or **Terminal & SSH** app to access Home Assistant's local apps folder. Current versions expose `/local_apps`; older installations may expose `/addons`.
2. Copy the **inner `wusel` app folder** into that folder. The result is `/local_apps/wusel/config.yaml`, or `/addons/wusel/config.yaml` on older installations. Copy only the app folder, not the outer project folder containing tests and tools.
3. Open **Settings → Apps → Install app** and check for updates. Older versions call this **Add-ons → Add-on store**. Find **Wusel** under local apps and install it. The first build needs internet to download the container image and Python packages.
4. In Wusel's Configuration tab, check `timezone`, for example `Europe/Zurich`. Leave `secure_cookie: false` for direct local HTTP access. Start Wusel and enable Start on boot.
5. Copy the **first-run setup code** from Wusel's Logs. Select **Open Web UI** and use that code to create the first parent account. There are no default credentials.
6. In **Family**, create a child account. Select the child and use **Weekly plan** to add routines.
7. On the child's device, open `http://YOUR_HOME_ASSISTANT_IP:8099` and sign in with the child's account. You can add this page to the home screen. The child does not need a Home Assistant login.

The local apps folder and update process are described in Home Assistant's [first app guide](https://contributors.home-assistant.io/apps/first-app/) and [local testing guide](https://contributors.home-assistant.io/apps/guides/testing/).

## IPv4 and IPv6 access

From version 0.5.2, Wusel uses the Pi's host network and listens on IPv4 and IPv6 on fixed HTTP port **8099**. This avoids an IPv4-only container port mapping when a name such as `homeassistant.local` resolves to IPv6. Home Assistant no longer needs a separate `8099/tcp` mapping for Wusel; a Network port field may no longer appear. Port 8099 must be free on the Pi.

After updating, test `http://homeassistant.local:8099/health` and the Pi's IPv4 address, for example `http://YOUR_PI_IP:8099/health`. Both should return `{"ok":true}`. Wusel logs the bound addresses (`0.0.0.0:8099` and `[::]:8099` when IPv6 is enabled), followed by `Wusel ready: HTTP port 8099`.

Copy all updated app files, including `server.py`, `Dockerfile`, and `config.yaml`. Update/rebuild the installed app and confirm version **1.0.1** before starting it; restarting an older container alone does not switch its network mode. For subsequent updates, keep the app slug set to `wusel`.

Host networking shares the Pi's network interfaces with the app. It does not require protection mode to be disabled or router port forwarding to be enabled. The existing family authentication and HTTP/HTTPS guidance still apply.

Implementation references: [Waitress dual-stack listeners](https://docs.pylonsproject.org/projects/waitress/en/latest/arguments.html), [Home Assistant host networking](https://contributors.home-assistant.io/apps/reference/configuration/).

## Future updates after installing 0.12.0

1. Make a Home Assistant backup that includes Wusel, then stop Wusel.
2. Find the existing Wusel source folder in Home Assistant's local apps folder. Rename that source folder to `wusel` if necessary, then replace its app files with the new inner `wusel` folder's contents. Keep only one source copy of this app in the scanned local apps folder; keep source backups elsewhere.
3. For updates after this clean installation, keep `slug: wusel` in `config.yaml`. Home Assistant uses this ID to identify the app and its persistent data.
4. Check for updates in the app store, update or rebuild Wusel, and start it. Keep the app installed throughout the update so its data volume is retained.

For subsequent updates of this installation, accounts and progress stay in `/data/wusel.sqlite3`; schema changes are migrated automatically.

Home Assistant documents the distinction between app folders and installation IDs in [How apps work](https://contributors.home-assistant.io/apps/how-apps-work/).

## Everyday use

**Children:** Complete the next task with **Done**. **See my day** opens the checklist, including undo. **My badges** opens rewards. **Settings** contains language, color theme, and sign out. Tap the weather row for the forecast.

**Parents:** Use **Family** to create accounts, reset passwords, and choose each child's default home view. Use **Weekly plan** to create or edit routines, **Review** to reverse or restore completions, and **Badges** to remove or restore badges. Parents choose their language, color theme and sign-out together in **Settings**, matching the child's settings page. Family and Settings are compact icon buttons in the header, leaving the navigation row with only the child selector plus Overview, Weekly plan, Badges and Review. Redundant visible child, administration, language and account-role labels are omitted; controls retain accessible names.

Each completion gives 10 points. Every 100 points advances a level; step badges are awarded at 1, 5, 10, 20, 50, 100, 150, 250, 500 and 1000 completed steps, with additional full-day and streak badges. Duplicate taps and undo/recheck do not multiply points or replay the reward animation. Overview and Review use the same correction flow: Reopen step removes its points and locks it until a parent selects Confirm done. The child home screen keeps the task details visible while awaiting confirmation. Remove an incorrectly earned badge separately.

For different weekday/weekend times, create two routines with different day selections. A date-specific task adds a task for that date; it does not cancel other recurring tasks. Times are helpful cues, not alarms or restrictions on when today's tasks can be completed.

Language and theme choices are saved per account across devices. Routine titles and instructions stay as entered. On a shared device, sign out before switching people.

## Weather

Set `weather_entity` in Wusel's Home Assistant Configuration to the ID of a weather entity for your location, such as `weather.forecast_home`, then restart Wusel. An empty value disables weather. Find entity IDs under **Settings → Devices & services → Entities**.

```yaml
timezone: Europe/Zurich
weather_entity: weather.forecast_home
secure_cookie: false
```

Hourly forecasts depend on the selected provider. A daily-only forecast is labelled; unavailable readings are not invented. The app uses Home Assistant's temperature unit and the configured timezone. Weather failures do not block the checklist. Stale weather is labelled and preparation hints are suppressed.

The app uses the server-side Supervisor token and the `homeassistant_api` permission to read the selected weather state and request forecasts. Tokens are never sent to the browser. Preview screenshots use labelled example weather.

## Storage and current limits

Include Wusel in Home Assistant backups. The app requests cold backups so SQLite is stopped during copying. Keep backups private because they contain family data.

This version is for your trusted home network. Access from outside it requires an appropriately configured HTTPS proxy or private VPN. Enable `secure_cookie` only for HTTPS access. There is no ingress integration, push notification service, offline mode, email password recovery, or automatic account deletion/deactivation. Account renaming, role changes, and assignment of individual children to selected parents are not implemented.

## Run locally

Requires Python 3.12+. From the outer project folder, in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\wusel\requirements.txt
$env:WUSEL_DATA = Join-Path $PWD "work\dev-data"
$env:WUSEL_DEV = "1"
.\.venv\Scripts\python.exe .\wusel\app.py
```

Open `http://127.0.0.1:8099` and use the setup code printed in the terminal. Local development uses the `WUSEL_*` environment variables. The development server binds to localhost; the container uses Waitress for production.

## Test and package

From the outer project folder:

```powershell
python -m pip install -r requirements-dev.txt
python tools/validate.py
python -m unittest discover -s tests -v
node tests/test_i18n.cjs
node tests/test_badge_view.cjs
python tools/package.py
python tools/validate.py --archive dist/wusel-1.0.1.zip
```

The package command writes `wusel-1.0.1.zip` inside the project’s `dist` folder, with `wusel/wusel/config.yaml` inside the ZIP. It excludes local data, virtual environments, and bytecode.

See [VALIDATION.md](../VALIDATION.md) for checks and test boundaries. The production server has been tested over IPv4 and IPv6 locally. The updated container network mode, hostname access, live weather, and backup/restore still need verification after updating the Pi.

## GitHub CI

The [pipeline](https://github.com/santsamu/wusel/actions/workflows/ci.yml) runs on pull requests, pushes to main, and manual dispatch. It checks Python/JavaScript tests, YAML/JSON, versions, translations and source-package integrity, then builds and starts AMD64 and ARM64 images (ARM64 via QEMU) with disposable empty data. HTTP checks cover health, the frontend, static assets and first-run API. The validated source ZIP is available as an Actions artifact for 14 days. Images are not published to a registry and the installed Pi is not modified. Actions are pinned to commit SHAs with read-only repository permissions.
