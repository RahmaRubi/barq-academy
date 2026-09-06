# Troubleshooting journal

## Entry 1 / 2026-09-07

* **Symptom:**
  `app-01` and `app-02` were running but `unhealthy`.

* **Hypothesis:**
  Docker healthcheck was failing.

* **Command or test:**
  Inspected the healthcheck and searched for `/healthz`.

* **Actual output:**
  Healthcheck targeted `/healthz`, while Flask exposes `/health`.

* **Failed attempt and what changed your thinking:**
  No failed fix attempt. Testing confirmed `/health` → success and `/healthz` → `404`.

* **Root cause:**
  Healthcheck endpoint mismatch between Docker Compose and Flask.

* **Fix:**
  Changed the healthcheck from `/healthz` to `/health`.

* **Retest evidence:**
  Both `app-01` and `app-02` are now running with `healthy` status.
    app-01   ...   healthy
    app-02   ...   healthy
    postgres ...   healthy
    redis    ...   healthy

* **Related commit:**
  `fix: align Docker healthcheck with Flask health endpoint`

* **Remaining uncertainty:**
  None — the issue was resolved and verified.





















<!--
Keep chronological entries. Copy this block for each meaningful investigation.

## Entry / date / time
- Symptom:
- Hypothesis:
- Command or test:
- Actual output:
- Failed attempt and what changed your thinking:
- Root cause:
- Fix:
- Retest evidence:
- Related commit:
- Remaining uncertainty:

Do not fabricate a failed attempt just to fill the template. Record actual attempts. -->
