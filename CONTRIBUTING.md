# Contributing Guidelines

Thanks for your interest in contributing! This project is distributed under the MIT License (see LICENSE). By contributing, you agree your contributions will be licensed under the same.

## Getting started

1. Fork the repository and create a feature branch from `main`.
2. Ensure you can run the app with Docker: `docker compose up -d`.
3. Make your changes with clear, readable code and English comments/docstrings.

## Coding style

- Prefer explicit names and early returns.
- Avoid deep nesting; add docstrings for complex functions.
- Keep unrelated changes in separate commits.

## Pull requests

- Describe the motivation and scope. Include screenshots/logs if UX changes.
- Ensure no secrets are committed; rely on `.env`/secrets.
- Keep PRs small and focused; add tests if logic is complex.

## Security

- Do not remove SSRF protections or relax URL validation.
- Never hardcode tokens; use environment variables.

## Contact

For sensitive security issues, please open a private channel with the maintainer.
