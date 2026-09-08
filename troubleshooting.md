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



## Entry 2 / 2026-09-08

* **Symptom:** application was not  reachable through the published url http://127.0.0.1:8080.
* **Hypothesis:** Possible mismatch between Docker's published container port and Nginx's listening port.
* **Command or test:** checked container status through `docker compose -p barq-assessment ps` and found app1, app2 healthy. however application cannot be reached. Therefore, Inspected `docker-compose.yml` and `nginx/nginx.conf`.
* **Actual output:** Docker mapped `8080 → 81`, while Nginx was configured with `listen 80;`.
* **Failed attempt and what changed your thinking:** The expected traffic path could not reach Nginx because nothing was listening on container port `81`.
* **Root cause:** Docker and Nginx were configured to use different container ports.
* **Fix:** Changed Nginx from `listen 80;` to `listen 81;`.
* **Retest evidence:** Ran:

  ```bash
  docker compose exec nginx nginx -t
  docker compose restart nginx
  ```
* **Related commit:** `fix: align nginx listening port with docker mapping`
* **Remaining uncertainty:** Docker now can connect to nginx on the appropiate port mapping, however response for http://127.0.0.1:8080 returns 502 bad Gateway which means nginx connected at least.



## Entry 3 / 2026-09-08

* **Symptom:** Requests through Nginx return `502 Bad Gateway`.
* **Hypothesis:** Nginx may be unable to connect to one or more upstream applications.
* **Command or test:** `docker compose logs nginx --tail=50`
* **Actual output:** Nginx reports `connect() failed (111: Connection refused) while connecting to upstream` for `app-01:8081` and `app-02:8080`.
* **Failed attempt and what changed your thinking:** `curl http://127.0.0.1:8080/` successfully reached Nginx but returned `502`, proving the public port/Nginx path works and the failure is downstream.
* **Root cause:** The configured upstream application ports are refusing connections.
* **Fix:** changed nginx server app-1 port to listen on port *8080*
* **Retest evidence:** Ran:

  ```bash
  docker compose exec nginx nginx -t
  docker compose restart nginx
  ```
* **Related commit:** `fix: align nginx listening port with docker mapping`
* **Remaining uncertainty:** Need to verify why the upstream applications are still return `502` with `Connection refused` on the configured ports.













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
