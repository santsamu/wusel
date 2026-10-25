# Wusel

**von Wild & Weich · Version 0.7.2**

When editing or archiving routines, parents choose Apply today or From tomorrow (the default). New routines default to today. Apply today deliberately updates today’s tasks and full-day target; From tomorrow leaves both unchanged today. Pending changes appear in the weekly plan and become effective from the selected date. Earned badges are retained. The badge screen starts with one next goal and progress, plus earned badges; See all badges expands the collection into Steps, Full days and Streaks.

17 badges celebrate steps (1, 5, 10, 20, 50, 100, 150, 250, 500, 1000), full days (1, 10, 30), and streaks (3, 7, 14, 30 consecutive calendar days). Full days start counting with version 0.6.0 and require at least one planned step and every step completed. Empty or incomplete days break a streak; today has until midnight. Past daily plans survive later schedule edits. Corrections recalculate streaks; earned badges remain and parents can revoke them.

Parent and child passwords require at least 4 characters. Dates and times follow the browser’s regional format, with full month and weekday names. Temperatures are shown as whole numbers.

A calm routine app for children and parents, hosted locally on Home Assistant OS on a Raspberry Pi 5. Children use it in a phone or tablet browser.

[Deutsche Anleitung](DOCS.de.md)

## What is included

- One next task with a large **Done** button, an optional instruction, and a small daily count.
- A slim level bar, brief point feedback, and a small celebration for new levels. Reduced-motion settings are respected.
- A full checklist and badges available on request. Parents choose each child's default home view.
- Separate parent and child logins. All parents manage all children in this family installation.
- Routines for selected weekdays, weekends, every day, or one specific date.
- English and German, plus five personal themes: Forest, Ocean, Berry, Lavender, and Sunshine.
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

Copy all updated app files, including `server.py`, `Dockerfile`, and `config.yaml`. Update/rebuild the installed app and confirm version **0.7.2** before starting it; restarting an older container alone does not switch its network mode. The installation ID and persistent data remain unchanged.

Host networking shares the Pi's network interfaces with the app. It does not require protection mode to be disabled or router port forwarding to be enabled. The existing family authentication and HTTP/HTTPS guidance still apply.

Implementation references: [Waitress dual-stack listeners](https://docs.pylonsproject.org/projects/waitress/en/latest/arguments.html), [Home Assistant host networking](https://contributors.home-assistant.io/apps/reference/configuration/).

## Updating an existing installation

1. Make a Home Assistant backup that includes Wusel, then stop Wusel.
2. Find the existing Wusel source folder in Home Assistant's local apps folder. Rename that source folder to `wusel` if necessary, then replace its app files with the new inner `wusel` folder's contents. Keep only one source copy of this app in the scanned local apps folder; keep source backups elsewhere.
3. Leave the `slug` value in `config.yaml` unchanged. It is the existing installation's compatibility ID, separate from its display name and source folder. Home Assistant uses this ID to identify the app and its persistent data.
4. Check for updates in the app store, update or rebuild Wusel, and start it. Keep the app installed throughout the update so its data volume is retained.

Existing users, routines, completions, themes, and language choices remain in the app's persistent `/data` directory. Database settings added by earlier releases are migrated automatically. This release adds dual-stack host networking and startup diagnostics; the storage format is unchanged.

Home Assistant documents the distinction between app folders and installation IDs in [How apps work](https://contributors.home-assistant.io/apps/how-apps-work/).

## Everyday use

**Children:** Complete the next task with **Done**. **See my day** opens the checklist, including undo. **My badges** opens rewards. **Settings** contains language, color theme, and sign out. Tap the weather row for the forecast.

**Parents:** Use **Family** to create accounts, reset passwords, and choose each child's default home view. Use **Weekly plan** to create or edit routines, **Review** to reverse or restore completions, and **Badges** to remove or restore badges. Parents choose their own colors in **Settings**; language and sign-out are in the account menu at the top right. The child selector sits beside Overview, Weekly plan, Badges and Review, followed by Family and Settings. Redundant visible child, administration, language and account-role labels are omitted; controls retain accessible names.

Each completion gives 10 points. Every 100 points advances a level; step badges are awarded at 1, 5, 10, 20, 50, 100, 150, 250, 500 and 1000 completed steps, with additional full-day and streak badges. Duplicate taps and undo/recheck do not multiply points or replay the reward animation. Reversing a completion removes its points and locks it until a parent restores it. Remove an incorrectly earned badge separately.

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
$env:GARDEN_DATA = Join-Path $PWD "work\dev-data"
$env:GARDEN_DEV = "1"
.\.venv\Scripts\python.exe .\wusel\app.py
```

Open `http://127.0.0.1:8099` and use the setup code printed in the terminal. The existing `GARDEN_*` environment variable names are supported for compatibility. The development server binds to localhost; the container uses Waitress for production.

## Test and package

From the outer project folder:

```powershell
python -m unittest discover -s tests -v
node tests/test_i18n.cjs
python tools/package.py
```

The package command writes `wusel-0.7.2.zip` inside the project’s `dist` folder, with `wusel/wusel/config.yaml` inside the ZIP. It excludes local data, virtual environments, and bytecode.

See [VALIDATION.md](../VALIDATION.md) for checks and test boundaries. The production server has been tested over IPv4 and IPv6 locally. The updated container network mode, hostname access, live weather, and backup/restore still need verification after updating the Pi.
