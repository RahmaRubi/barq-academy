# Technical decisions

## Decision1 - non necessity to persistant data

- **Choice:** Keep Redis non-persistent (`--save "" --appendonly no`) and do not attach a persistent volume.

- **Why:** Redis is used only by the `/counter` endpoint to increment the temporary `barq:requests` counter. It tracks `/counter` requests during the current Redis data lifetime; it is not business data. Persistent application records are stored in PostgreSQL.

- **Alternative:** Enable Redis persistence using RDB snapshots or AOF and mount a named volume.

- **Trade-off:** The counter is lost when the Redis container is recreated or its in-memory data is lost. This is acceptable because the counter is non-critical and can start again from zero. The benefit is avoiding unnecessary persistent state and storage for ephemeral data.

- **Evidence / commit:** Runtime verification showed only one Redis key, `barq:requests`, with value `2`. After `docker compose up -d --force-recreate redis`, `DBSIZE` returned `0` and the counter key was absent. No configuration change was required; the decision was documented.

- **Production improvement:** If Redis becomes responsible for sessions, queues, rate-limit state, or other data that must survive failures, enable an appropriate persistence strategy (AOF/RDB), use a persistent volume, and define backup/recovery requirements.

**Assumption:** Losing the `/counter` value does not affect application correctness or business data.

**Limit:** This decision applies only to the current application implementation. A future change in Redis usage would require reassessing the persistence requirement.




## Decision2 - restart application with unless-stopped

- **Choice:** Use `restart: unless-stopped` for the Flask application containers.

- **Why:** Automatically recover app containers after unexpected crashes or host/Docker restarts, while still allowing intentional manual stops during testing and maintenance.

- **Alternative:** Keep `restart: "no"` or use `restart: always`.

- **Trade-off:** `unless-stopped` improves availability, but an unhealthy application process that remains running may not be restarted based on the healthcheck alone.

- **Evidence / commit:** The policy is compatible with the required failure test: `docker stop app-01` intentionally stops the selected backend without immediately restarting it, allowing NGINX to continue serving through `app-02`. The container can then be restored with `docker start app-01`.
**Related commit:** `fix: configure application restart policy`

- **Production improvement:** Combine the restart policy with application health monitoring, alerting, resource limits, and orchestration/failover mechanisms for higher availability.

**Assumption:** The application container should recover automatically from unexpected process/container failures, while intentional manual stops should remain stopped.

**Limit:** `unless-stopped` does not by itself provide high availability if both application instances fail or if the host itself becomes unavailable.




## Decision3 — Run the application as a non-root user

* **Choice:** Run the Flask application as the dedicated `app` user with UID 10001 instead of `root`.

* **Why:** The application only needs to execute Python, read its application files, listen on port 8080, and connect to PostgreSQL and Redis. None of these operations require root privileges. Running as a dedicated non-root user follows the principle of least privilege and reduces the potential impact of an application compromise.

* **Alternative:** Run the application as `root`, which is the default behavior when no runtime user is specified.

* **Trade-off:** Non-root execution improves security but requires application files and any writable directories to have appropriate ownership and permissions. The application directory is therefore copied with ownership assigned to the `app` user.

* **Evidence / commit:** The Dockerfile creates the `app` user with UID 10001 and sets `USER app` for runtime execution. Verification with `docker exec app-01 id` and `docker exec app-02 id` confirms `uid=10001(app)` while the application health and readiness endpoints remain functional.

* **Production improvement:** Apply additional container hardening where compatible with the application, such as dropping unnecessary Linux capabilities, using a read-only root filesystem where possible, and enforcing resource and security policies at the orchestration level.

* **Assumption:** The Flask application does not need to modify protected system files or bind to privileged ports below 1024.

* **Limit:** Non-root execution reduces process privileges but does not by itself provide complete container security. Docker, the host, dependencies, application code, and network configuration still require appropriate security controls.










Record at least 5 decisions. Include assumptions and limits.

## Decision
- Choice:
- Why:
- Alternative:
- Trade-off:
- Evidence / commit:
- Production improvement:

Cover your base image, health checks, networks, timeouts/retries, restart/resource settings,
storage and any other meaningful choices.
