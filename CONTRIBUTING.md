# Contributing

Thanks for looking at Ballast. This is a hackathon entry, so changes are welcome as issues or small pull requests.

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]" ruff
ruff check ballast scripts tests
python -m pytest -q            # offline, no key and no node needed
forge test                     # ReserveVault (needs `git submodule update --init`)
npm ci && npx hardhat test     # ReserveOracle
```

The live drills (`scripts/role_drill.py`, `scripts/attest_drill.py`, `ballast drill`) need a funded key on a testnet and are not part of CI.

## Pull requests

- Keep each PR focused and add or update tests.
- Never commit seeds, keys or `.env` files. `gitleaks` runs in CI.
- Numbers in docs must trace to `docs/PROOF.md`, `docs/RECEIPTS.md`, a test run or a file in `evidence/`.

## Releases

Releases are automatic: on every push to `main`, `.github/workflows/release.yml` reads the commit messages since the last tag and, if any are releasable, tags the next semantic version and publishes a GitHub Release. Use Angular-style prefixes:

| Prefix | Bump |
|---|---|
| `fix:` · `perf:` | patch |
| `feat:` | minor |
| `feat!:` or a `BREAKING CHANGE:` footer | major |
| `docs:` `chore:` `test:` `refactor:` `style:` `ci:` | none |
