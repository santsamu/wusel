# Child screen live updates: implementation plan

Status: proposed, not implemented. The parent Overview reminder removal ships in 0.13.1; that release still uses the existing 60-second refresh.

## Goal

Reflect a parent's changes on an already-open child screen within approximately 3–5 seconds on a healthy local connection, without a manual reload, unnecessary visual changes or accidental completion/reward actions.

Cover parent completion/reopening/confirmation, new routines, routine edits/archiving, rest days, badge corrections, support settings and progress reset. Preserve Apply today versus From tomorrow semantics: a task starting tomorrow must not appear in today's checklist early.

## Existing behavior and constraints

- `wusel/static/app.js` currently polls `/api/state` every 60 seconds when signed in, not busy and no form is open. It also refreshes after visibility returns and connectivity returns.
- `refresh(true)` compares full state; changed data currently rerenders the screen. This can discard an expanded disclosure or keyboard focus.
- Child undo is server-enforced for 15 seconds. State refreshes must use the remaining server-provided time and never reopen the window.
- The backend is synchronous Python WSGI with a four-thread Waitress listener, SQLite and direct Home Assistant host networking. The app has no message broker or asynchronous event service.
- Time labels and the day boundary must still update when no parent has written new data.

## Recommendation: revision-based polling

Use a lightweight authenticated change check every **3 seconds while the child page is visible**. Fetch full state only when the revision or day changes. This avoids repeatedly loading routines, history and reward calculations when there is no change.

Do not add WebSockets or server-sent events in the first implementation. Long-lived streams on the current four-thread WSGI server would occupy workers needed for ordinary requests. Revisit push transport only if measured polling load or the desired latency justifies a different server design.

### 1. Persist a per-child revision

Add an idempotently migrated SQLite table, conceptually:

```sql
CREATE TABLE child_revisions (
    child INTEGER PRIMARY KEY REFERENCES users(id),
    revision INTEGER NOT NULL DEFAULT 0
);
```

- Initialize existing child profiles without changing their progress.
- Use a single helper to increment the affected child's revision **inside the same transaction as a successful change**. Rollbacks must not publish a revision for a failed operation.
- Cover both parent correction paths through `correct_completion`, task create/edit/archive, rest-day changes, badge removal/restoration, support settings, child reset and relevant child preferences/completions/deferrals. This also keeps multiple devices using the same child account coherent.
- Increment the affected child's revision when due pending edits activate. Include a day token in change responses so midnight is detectable even without a write.
- Reset is a normal revision increase, not a counter reset. Keep the audit and existing account/reset behavior.
- A revision is a change marker, not a completion token or authorization grant. SQLite serializes concurrent increments; do not use coarse wall-clock timestamps as revisions.

### 2. Add a small authenticated read endpoint

Proposed endpoint: `GET /api/updates`.

For an authenticated child, return only their own marker, for example:

```json
{"revision": 42, "day": "2026-10-27"}
```

- Derive the child from the session, not a caller-supplied child ID. Preserve authorization and session expiry.
- Keep it a cheap indexed read: no weather fetch, full state calculation or repeated daily-plan snapshots.
- Review the common request preprocessing in `Application.__call__`: the lightweight path should not unintentionally run heavy pending-plan/state work. A day change can trigger a full state request, which activates due changes through the existing transaction path.
- Include the current revision in `/api/state`, read consistently with that state, so clients know which snapshot they applied.
- Preserve private/no-store response behavior. No passwords, setup codes, tokens, task titles or other family data are needed in the change marker.

### 3. Add a single child refresh coordinator

Use a rescheduled timer rather than overlapping `setInterval` requests.

- Poll every 3 seconds while visible and signed in as a child; keep the existing parent behavior for this scope.
- Allow only one change request and one state refresh in flight. If a parent change arrives during a child completion or preference save, queue one refresh and run it after the operation settles.
- Coalesce repeated revisions. Ignore stale responses and never apply an older state over a newer one or across a changed session/day.
- On unchanged revision, do not rerender or show a toast. Update time labels and task selection locally on their existing cadence, and check for midnight.
- Pause polling in hidden tabs. Immediately recheck when the page becomes visible or the browser comes online. Browsers may suspend background pages; do not promise background delivery.
- On network failure, retain the displayed list and existing connection status. Back off, for example 3, 6, 12, then 30 seconds, and recover immediately after an online/visibility event. Do not retry completion POSTs automatically.
- On expired session, stop polling and return through the existing sign-in flow. Never leak another child's marker.
- Weather retains its own cached refresh cadence; a task revision should not force a weather fetch.

### 4. Apply changes without disrupting the child

Refactor the child render path into small update regions rather than replacing the entire app on every remote change.

- Update task content/status, daily count, level/progress, badges and support settings from the new state.
- Keep the active page, scroll position, expanded help/earlier-task disclosures and valid manual Do next choice. Do not switch away from badges or settings to force the home page open.
- Preserve keyboard focus where the control still exists. If a focused task control disappears or becomes unavailable, move focus to the relevant task heading without scrolling unexpectedly.
- If a parent reopens a completed step, show its details and neutral correction message. If a parent confirms it, update the checkmark and counts without playing a child completion celebration.
- If an ordinary current task is removed, completed or locked remotely, choose the next available task using the existing time/deferral rules. Keep older and deferred tasks in the collapsed list.
- Do not automatically expand every disclosure or interrupt with popups for new tasks. The updated count/task list should be enough.
- Reconcile undo from server deadlines. A parent confirmation removes child undo eligibility immediately; repeated polling never extends an existing window.
- Preserve draft edits in settings. Apply remote preferences after any local save settles; do not overwrite a control while the child is using it.

## Implementation order

1. Backend migration, revision helper and transaction/authorization tests.
2. Lightweight endpoint plus consistent revision in state, with query-cost checks.
3. Child polling coordinator, visibility/network lifecycle and stale-response handling.
4. Incremental rendering and focus/disclosure/undo reconciliation.
5. Two-browser integration tests and realistic Pi/network testing, then release.

Likely files: `wusel/app.py`, `wusel/static/app.js`, relevant translations, backend/Node/browser tests, `tools/smoke.py` if startup checks change, and the usual release documentation. Update `agent.md` with the implemented contract. No Home Assistant network/slug change or new external service is needed.

## Acceptance tests

- Parent completes, reopens and confirms a task in Overview and Review: an open child home/checklist reflects each action within 3–5 seconds on a healthy visible connection.
- A new task for today appears without reload; a tomorrow task appears in the plan but not today's checklist. Pending edits activate correctly at midnight and across restart.
- Badges, rest days, support preferences and reset update correctly, including multiple parent/child browser sessions.
- Simultaneous parent correction and child completion cannot bypass a lock, duplicate points or restore expired undo. A queued update wins over an older in-flight response.
- Hidden tabs stop polling and reconcile on return; offline/slow responses back off without parallel requests or replaying mutations. Session expiry returns to sign-in.
- Unchanged revisions cause no DOM replacement or announcement. Help/list disclosures, scroll, manual selection and keyboard focus survive relevant updates.
- English/German, quiet rewards, plain icons and focus/checklist modes remain correct. No automatic celebration for a parent-generated update.
- Lightweight requests avoid weather/full-state work. Measure request rate and latency on a Pi 5 with several visible clients; monitor check-off responsiveness rather than relying only on desktop timing.

## Out of scope

Background phone notifications, email, Home Assistant notifications, cross-household syncing, a new message broker and live parent dashboards. These need separate product decisions.
