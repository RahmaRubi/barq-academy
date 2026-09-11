# AI usage disclosure

# AI usage disclosure

* **Tool/model:** ChatGPT (GPT-5.6 Luna)

* **Purpose:** Used as a supporting technical resource for understanding Docker/Docker Compose networking, NGINX reverse proxy configuration, health/readiness checks, log analysis, troubleshooting, security considerations, and assessment documentation.

* **Files or decisions affected:** `docker-compose.yml`, `nginx/nginx.conf`, validation scripts, backup/restore scripts, and related infrastructure and security decisions.

* **What you changed or rejected:** AI suggestions were reviewed against the assessment requirements and the actual project configuration. I implemented and adapted relevant fixes, including correcting the Redis internal port, PostgreSQL persistence, container restart behavior, unnecessary root privileges, health/readiness validation, and backup/restore procedures. I also identified the hardcoded PostgreSQL credential as a security issue and moved the credential out of the Compose configuration.

* **How you independently verified it:** I executed the commands manually in the WSL/Docker environment and verified the results using `docker compose`, `curl`, container health checks, NGINX configuration tests, application endpoints, logs, validation scripts, Git diffs, and Git history. Changes were kept only after verifying their behavior in the running environment.

* **Related commits:**

  * `98162d2` — secrets in tracked `.env` file
  * `ca0970f` — fix: persist PostgreSQL data in named volume
  * `ecbbbc9` — fix: correct Redis internal port
  * `8cc613c` — non persistent Redis
  * `36adecf` — decision: application restart policy
  * `7d9ced5` — security: unnecessary root privileges
  * `950f40c` — decision: using official images health checks
  * `c627932` — validate: add service and HTTP readiness checks
  * `e75d236` — test: add backup and restore











Write None if no AI was used. Otherwise record each use:

- Tool/model:
- Purpose:
- Files or decisions affected:
- What you changed or rejected:
- How you independently verified it:
- Related commit:

You may use AI and external resources. You must understand and demonstrate the work.
