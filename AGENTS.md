# AGENTS

## Project intent
- This is a small async Python library that verifies JWTs against multiple JWKS sources with optional in-memory caching and local fallback keys.
- Public API is intentionally minimal: import `get_public_keys` and `decode_token` from `jwks_multi` (see `jwks_multi/__init__.py`).

## Core architecture
- Main logic lives in `jwks_multi/jwks_multi_verifier.py` (functions: `get_public_keys(...)`, `decode_token(...)`).
- JWT claim validation behavior is customized in `jwks_multi/extentions/jwt_clains.py` (`ExtendedJWTClaims` extends `joserfc.jwt.JWTClaimsRegistry`).
- Runtime state is module-global in `jwks_multi_verifier.py`: `_jwk_set` (cached keys + expiry) and `_jwk_locks` (per-URI `asyncio.Lock`).
- Tests in `tests/multi_jwks/` and `tests/extentions/jwt_clains/` are the best behavioral spec and cover edge cases (cache, lock reuse, HTTP failures, claims validation paths).

## Data flow to preserve
- `get_public_keys(jwks_urls, pre_public_keys, *, cache_jwk_set=True, jwks_ttl=None, jwks_timeout=5.0)` merges local keys (`pre_public_keys`) and remote JWKS from `jwks_urls`, then returns one `KeySet`.
- Local keys are stored under pseudo-URI `"localhost"`; `_get_remote_jwks()` explicitly skips this URI.
- `_get_remote_jwks()` performs a double cache check (before and inside lock) to avoid redundant fetches under concurrency.
- TTL handling: `expires_at = -1` means no expiry; otherwise `_is_cached(now, uri, *, cache_jwk_set)` compares current time with stored expiry.
- `decode_token(token, key, options=None, issuers=None, audiences=None)` calls `joserfc.jwt.decode(value=token, key=key)`, then constructs `ExtendedJWTClaims(leeway=..., iss=..., aud=..., sub=..., exp=..., nbf=..., iat=..., jti=...)` with per-claim `allow_blank` flags driven by `options`, and calls `claims_requests.validate(token.claims)`; leeway comes from `options.get('leeway') or 0`.

## External integrations
- `joserfc` is the primary JWT/JWK library: `KeySet`, `KeySetSerialization`, `Key` (from `joserfc.jwk`), `jwt.decode`, `JWTClaimsRegistry`, `ClaimsOption` (from `joserfc.jwt`).
- `joserfc.errors.MissingKeyError` is raised by `_get_jwks_set()` when no keys are available (replaces older `authlib` dependency).
- `httpx.AsyncClient` performs remote JWKS fetches with timeout controlled by `jwks_timeout`; `httpx.HTTPError` is caught and logged without re-raising.

## Development workflows
- Python requirement is `>=3.13` (`pyproject.toml`); local setup in `Makefile` uses `uv` and currently pins Python `3.14.3`.
- Full local init: `make init-local` (creates venv with Python 3.14.3, installs all groups, runs lint-fix).
- Install deps: `make install` (prod) or `make install-dev` (all groups).
- Run tests: `make test` (or `make test file=tests/multi_jwks/test_get_remote_jwks.py`).
- Run coverage: `make coverage`.
- Lint/format path used by maintainers: `make lint` and `make lint-fix`.
- Changelog: create a fragment in `changelog.d/` named `<ticket>.<type>` (types: `.feature`, `.bugfix`, `.doc`, `.removal`, `.misc`, `.health`, `.security`). The release commands (`make release-major`, `make release-minor`, `make release-patch`) invoke `towncrier build` automatically before bumping the version.

## Code and Documentation Conventions
- **Language Strategy:** Portuguese for chat/task descriptions; English for all code, variable names, inline docstrings, and code documentation. See `.github/instructions/python.instructions.md` for detailed rules.
- **Docstrings Policy:** Use docstrings only when function name and type hints are insufficient (complex logic, side effects, public API contracts). Avoid restating function names or parameter types. Follow PEP 257 or Google style.
- **Type Hints:** Mandatory for all functions. Use modern typing (e.g., `list[str]` instead of `List[str]`).
- **SOLID Principles:** Apply Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion principles. See `.github/instructions/python.instructions.md` for detailed guidance.
- **Code Review:** When reviewing code, enforce type hints, flag redundant documentation, and validate instruction file front matter (if created in `.github/instructions/`).

## Project-specific conventions
- Keep async behavior and per-URI locking semantics intact; regressions here will break concurrency assumptions.
- When touching cache logic, update tests that freeze time (`pytest-freezer`) such as `tests/multi_jwks/test_get_public_keys.py`.
- Test fixtures in `tests/multi_jwks/conftest.py` clear `_jwk_set` and `_jwk_locks`; new tests should rely on that isolation pattern.
- Maintain existing misspelt module path `extentions/jwt_clains.py` for compatibility unless doing an explicit migration.
