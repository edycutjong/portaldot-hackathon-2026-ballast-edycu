# Security Policy

Ballast is a hackathon build (Portaldot Hacker House 2026). It runs against testnets only and holds no real funds.

## Supported versions

Only the `main` branch is maintained.

## Reporting a vulnerability

Please do not open a public issue for a security problem. Use GitHub's
[private vulnerability reporting](https://github.com/edycutjong/portaldot-hackathon-2026-ballast-edycu/security/advisories/new)
for this repository. Expect an acknowledgement within a few days.

## Scope notes

- Keys: the repo ships no private keys. Demo keys are seed files created locally (mode 600) and are ignored by git.
- CI is offline by design: no workflow needs a seed, a funded key or a live RPC write.
- Secret scanning, push protection, Dependabot alerts and CodeQL are enabled on this repository.
