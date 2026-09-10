# Technical decisions

## Decision1

- **Choice:** Keep Redis non-persistent (`--save "" --appendonly no`) and do not attach a persistent volume.

- **Why:** Redis is used only by the `/counter` endpoint to increment the temporary `barq:requests` counter. It tracks `/counter` requests during the current Redis data lifetime; it is not business data. Persistent application records are stored in PostgreSQL.

- **Alternative:** Enable Redis persistence using RDB snapshots or AOF and mount a named volume.

- **Trade-off:** The counter is lost when the Redis container is recreated or its in-memory data is lost. This is acceptable because the counter is non-critical and can start again from zero. The benefit is avoiding unnecessary persistent state and storage for ephemeral data.

- **Evidence / commit:** Runtime verification showed only one Redis key, `barq:requests`, with value `2`. After `docker compose up -d --force-recreate redis`, `DBSIZE` returned `0` and the counter key was absent. No configuration change was required; the decision was documented.

- **Production improvement:** If Redis becomes responsible for sessions, queues, rate-limit state, or other data that must survive failures, enable an appropriate persistence strategy (AOF/RDB), use a persistent volume, and define backup/recovery requirements.

**Assumption:** Losing the `/counter` value does not affect application correctness or business data.

**Limit:** This decision applies only to the current application implementation. A future change in Redis usage would require reassessing the persistence requirement.















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
