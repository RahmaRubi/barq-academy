# Security and production-readiness review

### Entry 1 – Secrets in tracked environment file

* **Risk and evidence:** Git tracked `config/app.env`, which contained sensitive configuration including the PostgreSQL connection string and password.
* **Impact:** Credentials could be exposed through the Git repository and its commit history.
* **Implemented fix / commit:** Added `*.env` to `.gitignore`, removed `config/app.env` from Git tracking, and rewrote the Git history to remove the file from all commits. Commit: `d8de977` (`security: stop tracking environment file`).
* **Production follow-up:** Rotate any credentials that were previously exposed and use a dedicated secrets-management solution for production credentials.
* **How to verify:** `git ls-files | grep 'config/app.env'` returns no output, `git log --all -- config/app.env` returns no output, and `git status --ignored` shows `config/` as ignored.










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
