# Security Policy

## Supported Versions

The current `main` branch receives security fixes on a best-effort basis.

## Reporting a Vulnerability

Please report security vulnerabilities privately to the maintainer. Do not open public issues for sensitive reports.

## Hardening Notes

- Outbound HTTP requests validate public IPs and follow safe redirects.
- Telegram publishing enforces size limits and input validation.
- Secrets are supplied via environment variables (`.env` in dev, secrets in prod).
- Containers are configured with restart policies and minimal packages.

## Recommendations for Production

- Use a secrets manager (AWS/GCP/Vault) instead of plain `.env`.
- Restrict egress traffic via firewall or VPC rules to required endpoints.
- Enable structured logging, rate limiting and monitoring.
- Store media in S3/MinIO with encryption at rest; avoid world-readable buckets.
