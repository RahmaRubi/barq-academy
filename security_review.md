# Security and production-readiness review

### Entry 1 – Secrets in tracked environment file

* **Risk and evidence:** Git tracked `config/app.env`, which contained sensitive configuration including the PostgreSQL connection string and password.
* **Impact:** Credentials could be exposed through the Git repository and its commit history.
* **Implemented fix / commit:** Added `*.env` to `.gitignore`, removed `config/app.env` from Git tracking, and rewrote the Git history to remove the file from all commits. Commit: `d8de977` (`security: stop tracking environment file`).
* **Production follow-up:** Rotate any credentials that were previously exposed and use a dedicated secrets-management solution for production credentials.
* **How to verify:** `git ls-files | grep 'config/app.env'` returns no output, `git log --all -- config/app.env` returns no output, and `git status --ignored` shows `config/` as ignored.




## Entry 2  Application running with unnecessary root privileges

* **Risk and evidence:** The Flask application containers were initially running as `root`. This was verified with `docker exec app-01 id`, which returned `uid=0(root) gid=0(root) groups=0(root)`. The Dockerfile already created a dedicated `app` user, but `USER root` caused the application to run as root at runtime.

* **Impact:** If the application is compromised, running as root provides more privileges than the application requires and can increase the potential impact of an application-level compromise.

* **Implemented fix / commit:** Configured the application containers to run as the dedicated non-root `app` user (UID 10001) by replacing `USER root` with `USER app` in the Dockerfile. Application files are owned by `app` using `COPY --chown=app:app`.
  **Commit:** `security: unnecessary root privileges`

* **Production follow-up:** Further container hardening can be considered, including dropping unnecessary Linux capabilities and using a read-only root filesystem where compatible with the application.

* **How to verify:**

  ```bash
  docker exec app-01 id
  docker exec app-02 id
  curl http://127.0.0.1:8080/health
  curl http://127.0.0.1:8080/ready
  ```

  Expected user:

  ```text
  uid=10001(app) gid=10001(app) groups=10001(app)
  ```

  The health and readiness endpoints should continue to return successfully.



### Entry3 Hardcoded PostgreSQL Password

**Risk and evidence:**
The PostgreSQL password was hardcoded directly in `docker-compose.yml` under `POSTGRES_PASSWORD`. This exposes a database credential in the repository configuration and creates a risk of accidental disclosure through source control, repository sharing, logs, or configuration inspection.

**Impact:**
Anyone with access to the repository could obtain the database credential and potentially authenticate to PostgreSQL if network access is available. Reusing the same credential across environments could also increase the impact of a credential leak.

**Implemented fix / commit:**
Moved the PostgreSQL credentials out of `docker-compose.yml` into a local environment file (`config/postgres.env`) and added the file to `.gitignore` so it is not tracked by Git.

**Production follow-up:**
Use a dedicated secrets-management solution such as Docker/Kubernetes Secrets, a cloud secret manager, or another approved production secrets store. Credentials should be rotated regularly and should never be committed to source control.

**How to verify:**

1. Confirm that `docker-compose.yml` no longer contains the actual PostgreSQL password.
2. Confirm that the secret file is ignored:

   ```bash
   git check-ignore -v config/postgres.env
   ```
3. Confirm the secret is not tracked:

   ```bash
   git ls-files config/postgres.env
   ```

   The command should return no output.
4. Start the environment and verify PostgreSQL becomes healthy:

   ```bash
   docker compose up -d
   docker compose ps
   ```
5. Verify the application can still reach PostgreSQL through its normal `/ready` endpoint.









Record at least 8 concrete risks or improvements relevant to your final solution.
This is a review requirement, not the number of hidden faults.

For each finding:
- Risk and evidence:
- Impact:
- Implemented fix / commit:
- Production follow-up:
- How to verify:

Cover secrets, ports, container user, image selection, networks, persistence/backup,
logging/monitoring and availability. Separate completed work from planned improvements.
