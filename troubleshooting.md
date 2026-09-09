# Troubleshooting journal

## Entry(1) - health endpoint - 2026-09-06 - 1:09 AM

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



## Entry(2) - docker port mapping - 2026-09-08 - 6:07

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



## Entry(3) -  app-01:8081 port fix - 2026-09-08 - 8:37

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
* **Related commit:** `fix: app-01 listening port with App-port`
* **Remaining uncertainty:** Need to verify why the upstream applications are still return `502` with `Connection refused` on the configured ports.


## Entry(4) - bind application to 0.0.0.0 - 2026-09-08 - 9:30

* **Symptom:** Requests through Nginx were still returning `502 Bad Gateway` with `Connection refused`, even after correcting the upstream application port to `8080`.

* **Hypothesis:** The application might be listening only on the loopback interface (`127.0.0.1`), making it unreachable from Nginx over the Docker network.

* **Command or test:** Tested connectivity to port `8080` from inside `app-01` using:

  ```bash
  docker compose exec app-01 python -c "import socket; s=socket.socket(); print('localhost:', s.connect_ex(('127.0.0.1',8080))); print('container:', s.connect_ex(('172.18.0.2',8080)))"
  ```

* **Actual output:**

  ```text
  localhost: 0
  container: 106
  ```

  This confirmed that the application accepted connections through `127.0.0.1:8080` but refused connections through the container's network IP.

* **Failed attempt and what changed your thinking:** The Docker healthcheck continued to report the application as healthy because it tested `127.0.0.1:8080/health` from inside the same container. Therefore, a `healthy` container did not prove that the application was reachable from other containers. This shifted the investigation from the upstream port to the application's network binding.

* **Root cause:** The application was configured with `APP_HOST=127.0.0.1`, so Flask was listening only on the container's loopback interface and was not reachable by Nginx through the Docker network.

* **Fix:** Changed:

  ```yaml
  APP_HOST: "127.0.0.1"
  ```

  to:

  ```yaml
  APP_HOST: "0.0.0.0"
  ```

  and recreated both application containers:

  ```bash
  docker compose up -d --force-recreate app-01 app-02
  ```

* **Retest evidence:** Tested the application through the published Nginx endpoint:

  ```bash
  curl -v http://127.0.0.1:8080/health
  ```

  The request returned:

  ```text
  HTTP/1.1 200 OK
  X-Instance-ID: app-01
  ```

  with the application response:

  ```json
  {"instance_id":"app-01","service":"barq-api","status":"alive","version":"2.0.0"}
  ```

  This confirmed successful end-to-end connectivity from the client through Nginx to the application.

* **Related commit:** `fix: bind application services to all network interfaces`

* **Remaining uncertainty:** None. The application is now reachable through the Docker network and the published Nginx endpoint returns `200 OK`.




## Entry(5) - Application Instance ID Misconfiguration - 2026-09-08 - 11:28

* **Symptom:**
  `app-02` was receiving requests, but its application logs reported `"instance_id": "app-01"`.

* **Hypothesis:**
  `app-02` was configured with the wrong `INSTANCE_ID` environment variable.

* **Command or test:**

  ```bash
  for i in {1..10}; do curl -s http://127.0.0.1:8080/health; echo; done
  ```

  Then inspected both application logs:

  ```bash
  docker compose logs app-01 --tail=20
  docker compose logs app-02 --tail=20
  ```

* **Actual output:**
  Requests reached both application containers, but `app-02` logs contained:

  ```json
  "instance_id": "app-01"
  ```

* **Root cause:**
  `app-02` had been configured with:

  ```yaml
  INSTANCE_ID: "app-01"
  ```

  instead of its own instance ID.

* **Fix:**
  Changed the `app-02` configuration to:

  ```yaml
  INSTANCE_ID: "app-02"
  ```

  Then recreated the container:

  ```bash
  docker compose up -d --force-recreate app-02
  ```

* **Retest evidence:**
  Repeated the health requests and checked `app-02` logs to verify that requests were now associated with:

  ```json
  "instance_id": "app-02"
  ```

* **Related commit:**
  `fix: correct app-02 instance identity`

* **Remaining uncertainty:**
  None regarding the instance ID configuration after successful retest.




## Entry(6) - PostgreSQL connection failure -  2026-09-09 - 12:50 AM

* **Symptom:** Flask could not connect to PostgreSQL.

* **Failed connection test:**

  ```bash
  docker compose exec app-01 python -c "import psycopg; import os; psycopg.connect(os.getenv('DATABASE_URL'), connect_timeout=2); print('DB connection successful')"
  ```

  Result: `Connection refused` on port `5433`.

* **Root cause:** `DATABASE_URL` used the wrong PostgreSQL port (`5433`). PostgreSQL listens on **5432 inside the Docker network**. The Compose mapping `127.0.0.1:15432:5432` exposes container port `5432` as host port `15432`; this host port is not used for container-to-container communication. The password was also incorrect.

* **Fix:** Changed `DATABASE_URL` to use `postgres:5432` with the correct password, then recreated `app-01` and `app-02`.

* **Retest:** Direct connection returned `DB connection successful`.

* **Application verification:** `GET /records` returned `200 OK` with records retrieved from PostgreSQL.

* **Related commit:** `fix: correct database connection configuration`


* **Remaining uncertainty:**
  None




## Entry 7 — Redis connection failure - 2026-09-09 - 1:01AM

* **Symptom:** `GET /counter` returned `503 redis_unavailable`.
* **Failed test:**

  ```bash
  curl -v http://127.0.0.1:8080/counter
  ```
* **Root cause:** `REDIS_URL` used the wrong Redis port for container-to-container communication.
* **Fix:** Corrected the Redis port in `config/app.env` and recreated `app-01` and `app-02` to apply the updated environment.
* **Retest:**

  ```bash
  curl -v http://127.0.0.1:8080/counter
  ```

  Result: `HTTP/1.1 200 OK` with `{"counter":1,...}`.
* **Conclusion:** Flask successfully connected to Redis and executed the counter operation.
* **Related commit:** `fix: correct redis connection configuration`

* **Remaining uncertainty:**
  None




## Entry 8 — services appropriate host port - 2026-09-09 - 10:51 AM

* **Symptom:** PostgreSQL and Redis had published host ports; requirement allows only NGINX on host port `8080`.
* **Hypothesis:** Unnecessary `ports` mappings were exposing backend services to the host.
* **Command or test:** Reviewed `ports` in `docker-compose.yml`.
* **Actual output:** PostgreSQL → `15432:5432`, Redis → `16379:6379`, NGINX → `${PUBLIC_PORT:-8080}:81`.
* **Failed attempt and what changed your thinking:** `127.0.0.1` limits access to the local host but still publishes the ports. The requirement says not to publish them.
* **Root cause:** PostgreSQL and Redis had unnecessary host-port mappings.
* **Fix:** Remove `ports` from PostgreSQL and Redis; set NGINX to `127.0.0.1:8080:81`.
* **Retest evidence:** Verify with `docker compose ps`.
* **Related commit:** `fix: services appropriate host port`
* **Remaining uncertainty:** None after successful port verification.


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
