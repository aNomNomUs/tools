# Human Action Needed (because apparently computers can't sweet-talk horoscopes alone)

> Tone set to "overcaffeinated senior DevOps babysitter" as requested.

1. **SSL/TLS Certificates (a.k.a. "Please stop shipping plain HTTP in prod"):**
   - Generate real certificates from a trusted CA if you ever expose `astrology.server` beyond `localhost`.
   - If you have no idea how: buy a domain, point DNS at your box, run `certbot` with HTTP-01, then actually renew before the internet shames you. Yes, automated renewals are a thing; use them.
   - Store private keys outside the repo (permissions 600, owned by the runtime user). If you commit them here, I will print the repo and set it on fire.

2. **Environment Hardening ("No, running as root is not edgy"):**
   - Create a non-root user for the API service. Systemd unit? Great. At least set `User=astrotalk` and `Group=astrotalk`.
   - Lock down file permissions on any log or config directories (`chmod 750`). The internet does not need to read your feelings.

3. **Logging Destination ("stdout is cute until journald rotates your dreams away"):**
   - Decide where logs go in production. If you want centralization, set up syslog/Fluentd/whatever *outside* this repo and point the handler there.
   - Configure log retention so disk doesn't explode. Yes, `logrotate` still exists. Use it.

4. **Secrets Management (".env is not a vault, champ"):**
   - If you later bolt on API keys or premium content, provision them in a secrets manager (Vault, SSM, pick your poison) and inject via env vars at runtime.
   - Document the rotation procedure in the same place you store runbooks, not in Slack DMs that get lost when interns quit.

5. **Network Placement ("Put the thing *behind* a firewall, please"):
   - If serving the HTTP API, put it behind a reverse proxy (nginx, Caddy, HAProxy). Terminate TLS there, rate-limit, and throttle obvious abuse.
   - Allowlist outbound traffic if you ever add integrations; default deny is your friend. No, really.

6. **Backups ("Because someone will rm -rf /, probably you"):
   - If you persist data (not in scope yet), set up backups with tested restores. A backup you can't restore is a decorative brick.

7. **Dependency Audits ("Trust issues? Good."):
   - We're stdlib-only now. If a future genius adds external packages, vendor them locally and checksum them. No random `pip install` from the void.
   - Keep a BOM (bill of materials) if you expand dependencies. Supply chain attacks are not a fun plot twist.

8. **Monitoring ("Observability > vibes"):
   - Hook health checks into whatever uptime system you use. The `/healthz` endpoint exists; please look at it.
   - Add basic metrics (requests/sec, latency) via your infra stack. No, print statements are not metrics.

Feel free to ignore any of this if you enjoy 3 AM pages. Otherwise, follow the bullets and maybe, just maybe, production will survive your junior dev's "YOLO" deployments.
