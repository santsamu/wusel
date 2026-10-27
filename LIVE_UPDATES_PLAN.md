# Parent and child live updates

Status: implemented in **0.14.0**, following the original plan with the requested **10-second** interval and support for **both parent and child screens**.

## User behavior

- While visible, either role checks for changes every 10 seconds. Healthy local connections normally show remote changes by the next check, plus request time.
- Children receive their own profile's changes; parents receive changes anywhere in their local family installation.
- Tasks, completions, parent corrections, badge changes, rest days, settings, new accounts and resets update without a page reload. Tomorrow changes retain their effective date.
- Hidden tabs pause future checks. Returning to the page or coming online triggers an immediate check. Browsers may suspend background pages; this is not background notification delivery.
- Remote changes do not replay completion animations, duplicate points, reopen expired undo windows, switch the selected screen or expand every disclosure.

## Backend contract

`GET /api/updates` requires a valid Wusel session. It derives its scope from that session, ignoring caller-supplied child IDs. It returns only:

```json
{"revision": 42, "day": "2026-10-27", "timezone": "Europe/Zurich"}
```

Parents use the family counter. Children use only their own account counter. The endpoint is a cheap read: no weather access, reward calculation, daily-plan writes or pending-change activation.

SQLite `live_revisions(scope, revision)` stores durable counters. Transactional triggers cover users, routines, completions, badges, daily plans, pending routines, rest days, deferrals and audit activity. Each relevant write updates the family counter and affected account counter; audit affects the family counter. Sessions and throttling attempts do not affect revisions. Counters are monotonic and resets do not reset them. Trigger writes roll back with the originating transaction. This replaces the original proposed explicit revision helper so existing/future write paths cannot silently omit notification.

The state endpoint activates due pending edits and returns the revision matching its snapshot under a transaction. Day/timezone markers detect midnight and configuration changes without requiring a write. Avoid no-op database updates during state construction; an already-empty badge goal must not continually publish revisions.

## Frontend contract

- One rescheduled poller serves both roles. Only one marker check runs at once, and full state reads are serialized.
- On an unchanged revision/day/timezone, update local time labels and undo controls without replacing the screen. Weather retains its separate cache cadence.
- On a change or connection recovery, load the full state. A local mutation epoch rejects a snapshot overtaken by a local POST. A queued foreground refresh fetches the committed result afterward.
- Busy saves/check-offs defer checks; normal local actions still refresh immediately. Form presence alone does not disable background checks.
- Reconcile changed DOM using stable keys for tasks, badges, controls and forms. Preserve form input/radio values, textarea drafts, selection/caret, open details, focused help messages, valid manual task selection and scroll position. If a focused control disappears or becomes disabled, move focus to a relevant heading without scrolling.
- An open confirmation dialog keeps its draft and defers remote state application until closed. Marker checks can continue while it is open.
- Use the server-provided remaining undo seconds and monotonic browser time. Never give an old completion another 15 seconds after a refresh.
- On connectivity failure, retain the displayed state, use existing connection feedback and back off to 20 then 30 seconds. Do not replay mutation requests. Online/visibility events reset the delay.
- A rejected/expired session returns through the existing sign-in state and stops polling until signed in again.

## Why polling

The existing deployment uses a four-thread synchronous Waitress server. Small indexed change checks fit this architecture without dedicating workers to long-lived streams or adding a broker/WebSocket service. The network port, Home Assistant slug and account model remain unchanged.

## Verification and limits

Backend tests cover authenticated/scoped markers, cheap read-only checks, transaction rollback, completion/correction updates, midnight and pending activation, preferences/rest/badges/reset, session expiry, persistence across restart and no revision churn when all badges are earned.

Node tests cover both roles' 10-second cadence, unchanged markers, busy/hidden/modal guards, backoff, in-flight checks and serialized rejection of stale snapshots. Real Chrome sessions verify automatic parent-to-child and child-to-parent updates, parent draft/caret retention, new tasks, open help/focus/scroll retention, an older held response racing a completion, confirmation-dialog preservation and remote reset/sign-out.

Tests use local demo data. Physical Pi latency/load and mobile background behavior still need deployment verification; there is no guaranteed delivery time while offline or suspended.

## Out of scope

Push/email notifications, background phone alerts, cross-household synchronization and a new message broker. The update mechanism stays local to the existing Wusel installation.
