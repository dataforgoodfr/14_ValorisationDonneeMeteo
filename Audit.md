# Audit : Valorisation Donnée Météo : )

## Code Quality

The baseline setup is solid : Ruff for Python, ESLint + Prettier for the frontend, pre-commit hooks that also run in CI. For an open-source volunteer project.

What's missing :
- Type checking isn't part of CI : no mypy on the Python side, no `vue-tsc` on the frontend :  so type errors slip through unnoticed. 
- There's no minimum coverage threshold either, meaning tests can be quietly removed without anything complaining.

Ruff is configured for `py311` while the project targets Python 3.12+. 
And pre-commit hooks can always be bypassed with `--no-verify`, which happens more often than it should when people are in a hurry.

- **Automated:** Python and TS linting via pre-commit + CI
- **Manual:** type checking, dead code detection, human review
- **Main risk:** no real safety net on quality : someone can degrade the codebase without CI catching it

## Testing

The backend has a real test foundation :
- pytest-django, 
- factory-boy, 
- unit tests for weather indicators, 
- integration tests against TimescaleDB. 

The problem is that **none of these tests ever run in CI**. The GitHub Actions workflows have no `pytest` step. In practice, broken code can reach staging without anyone knowing.

On the frontend, vitest is installed and a `test: unit` script exists in `package.json` but there are zero test files. It's an empty shell.

Other gaps:  no E2E tests (Playwright/Cypress), no load testing, no API contract validation. Also, `tox.ini` targets Python 3.14 which doesn't exist yet.

- **Automated:** nothing in CI
- **Manual:** everything : when it runs at all
- **Main risk:** broken code can reach staging with no warning

## Deployment process

The build pipeline is well-thought-out:  
- multi-stage Docker images, 
- push to GHCR, 
- SSH deployment over Tailscale triggered on `v*.*.*` tags.

There's no automatic rollback if something goes wrong. No smoke test after deployment to verify the app is actually responding. Django migrations run inside `entrypoint.sh`. If a migration fails, the container won't start and the app goes down.

There's also no separate `docker-compose.prod.yml`, the staging compose uses `: latest` tags without digests.

- **Automated:** build, push, deploy on tag
- **Manual:** rollback, post-deploy verification, production release
- **Main risk:** a failed deployment has no safety net : and no way to detect it quickly

## Monitoring

There's a Docker health check on TimescaleDB (`pg_isready` every 10s) and default Nginx access logs.

No Sentry, no Prometheus, no `/health` endpoint in the Django API, no structured logging. If the app crashes, a user will probably report it before anyone on the team notices. Debugging a production issue means SSH-ing in and grepping through plain-text logs.

- **Automated:** DB health check
- **Manual:** everything else
- **Main risk:** outages are invisible until someone complains

## Security

- the `.env` file was committed to the repo. It contains the Django `SECRET_KEY` and the database password (`infoclimat2026`). Even if it's since been deleted, it's still in the git history.

- the dev `.env` has `DEBUG=False` but `ALLOWED_HOSTS=*` : that's a contradictory and unsafe configuration that could make its way to staging.

Everything else : no dependency vulnerability scanning (no Dependabot, no `pip audit` or `npm audit` in CI), no rate limiting on API endpoints, the API appears fully public with no authentication, and the same DB credentials are shared between dev and staging.

On the positive side:  Tailscale for deployment (no public SSH port exposed), CORS is configured, Django security middleware is in place, CI secrets live in GitHub Secrets.

- **Automated:** CI secret management
- **Manual:** CVE scanning, access review, secret rotation
- **Main risk:** credentials in git history + no detection when new vulnerabilities appear

## Documentation

Main README, backend and frontend README, TimescaleDB setup guide, structured PR template.

What's missing is operational documentation. No runbook explaining what to do when something breaks in production. No ADRs to explain why certain technical choices were made. No changelog. The OpenAPI spec (`openapi.yaml`) is maintained by hand : it will inevitably drift from the actual code over time.

- **Automated:** Swagger UI via DRF Spectacular
- **Manual:** OpenAPI spec, changelog, everything operational
- **Main risk:** no runbook = first production incident = panic + reverse-engineering under pressure


## Improvement Plan

1. **Clean the git history** to remove the committed `.env` (use BFG Repo Cleaner or `git filter-repo`) : and rotate every exposed secret immediately
2. **Add a `pytest` step to CI** : without it, backend tests provide zero protection
3. **Fix `ALLOWED_HOSTS`** in the dev/staging `.env`
4. **Enable Dependabot** on the repo for automatic security updates
5. **Add a `/health` endpoint** in Django and a post-deploy check in the workflow
6. **Restore `.env.example`** at the root with all required variables documented
7. **Write at least one frontend test** to confirm vitest actually works
8. **Write a minimal runbook** : how to restart the app, how to rollback, where the logs are

### Issue 1 — Credentials committed to git

The `.env` is out of the repo now, but the info is in the history. Anyone who ever cloned it has the DB password and secret key.

- **Short-term:** Change the DB password, generate a new Django `SECRET_KEY`, revoke any exposed tokens.
- **Long-term:** Run `git filter-repo --path .env --invert-paths` to scrub the file from history, then force-push. Going forward, enforce secret scanning in CI so committed secrets get caught before they merge. Add a pre-commit hook that blocks `.env` files specifically.
- **Tools:** `git filter-repo`, GitHub Secret Scanning, `detect-secrets` pre-commit hook, `gitleaks` for CI scanning.

### Issue 2 — Tests never run in CI

Having tests is only useful if they run automatically. 

- **Short-term:** Add a `test` job to the existing `pre-commit.yaml` workflow. Two steps: spin up a TimescaleDB service container, then run `uv run pytest`. 
- **Long-term:** Split tests into fast (unit, no DB) and slow (integration, with DB) so the fast ones run on every push and the slow ones run on PRs. Add `--cov-fail-under=70` to enforce a coverage floor. Set up vitest in the frontend CI job too.
- **Tools:** GitHub Actions `services` for PostgreSQL/TimescaleDB, `pytest-cov` (already installed), `vitest` (already installed), `codecov` or `coveralls` for coverage reporting.

### Issue 3 — No visibility once deployed

- **Short-term:** Add a `/health` endpoint to Django that checks DB connectivity and returns a JSON status. Add a `curl` check at the end of the deployment workflow that hits that endpoint and fails the job if it doesn't respond with 200.
- **Long-term:** Set up Sentry for error tracking on both backend and frontend. Add Prometheus metrics to Django (via `django-prometheus`) and a Grafana dashboard for request rates and error rates. Use UptimeRobot for external uptime monitoring with email/Slack alerts.
- **Tools:** Sentry (free tier), `django-prometheus`, Grafana Cloud (free tier), UptimeRobot (free), structlog for structured JSON logging.

### Issue 4 — Deployments have no safety net

A bad deploy currently means: app is down, someone SSH in, manually pulls the previous image, restarts. No automation, no fast recovery.

- **Short-term:** Pin image versions in `docker-compose.test.yml` using image digests instead of `:latest`. Add a `docker-compose pull && docker-compose up -d` with a health check wait in the deploy script, so the workflow fails if the new containers don't come up healthy.
- **Long-term:** Introduce a simple rollback step in the deployment workflow that re-deploys the previous image tag if the health check fails. Keep the last N image versions in GHCR with proper tagging (not just `:latest`). Separate staging and production into distinct workflows with a manual approval gate before production.
- **Tools:** GitHub Actions `environment` with required reviewers for production, `docker-compose` healthcheck + `--wait` flag, GHCR image retention policies.

### Issue 5 — No dependency vulnerability tracking

The project uses a lot of third-party packages. Right now there's no process to find out when one of them has a known CVE.

- **Short-term:** Enable Dependabot in `.github/dependabot.yml` for both `pip` (pyproject.toml) and `npm` (package.json). It opens PRs automatically when updates are available — takes five minutes to set up.
- **Long-term:** Add `pip audit` and `npm audit` as steps in the CI pipeline so any build with a known vulnerable dependency fails. Set Dependabot to auto-merge patch updates if CI passes, and flag minor/major updates for human review.
- **Tools:** Dependabot (built into GitHub, free), `pip-audit` (Pypi, free), `npm audit` (built into npm), `trivy` for container image scanning in the build workflow.
