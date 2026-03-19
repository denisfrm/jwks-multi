# AGENTS

## Project intent
- This is a small async Python library that verifies JWTs against multiple JWKS sources with optional in-memory caching and local fallback keys.
- Public API is intentionally minimal: import `get_public_keys` and `decode_token` from `jwks_multi` (see `jwks_multi/__init__.py`).

## Core architecture
- Main logic lives in `jwks_multi/jwks_multi_verifier.py` (functions: `get_public_keys(...)`, `decode_token(...)`).
- JWT claim validation behavior is customized in `jwks_multi/extentions/jwt_clains.py` (`ExtendedJWTClaims`).
- Runtime state is module-global in `jwks_multi_verifier.py`: `_jwk_set` (cached keys + expiry) and `_jwk_locks` (per-URI `asyncio.Lock`).
- Tests in `tests/multi_jwks/` and `tests/extentions/jwt_clains/` are the best behavioral spec and cover edge cases (cache, lock reuse, HTTP failures, claims validation paths).

## Data flow to preserve
- `get_public_keys(jwks_urls, pre_public_keys, *, cache_jwk_set=True, jwks_ttl=None, jwks_timeout=5.0)` merges local keys (`pre_public_keys`) and remote JWKS from `jwks_urls`, then returns one `KeySet`.
- Local keys are stored under pseudo-URI `"localhost"`; `_get_remote_jwks()` explicitly skips this URI.
- `_get_remote_jwks()` performs a double cache check (before and inside lock) to avoid redundant fetches under concurrency.
- TTL handling: `expires_at = -1` means no expiry; otherwise `_is_cached(now, uri, *, cache_jwk_set)` compares current time with stored expiry.
- `decode_token(token, key, options=None, issuers=None, audiences=None)` calls `authlib.jose.jwt.decode` with `claims_cls=ExtendedJWTClaims`, then `claims.validate(leeway=...)` (leeway from `options` dict or 0 by default).

## External integrations
- `authlib` is used for `JsonWebKey.import_key_set`, `KeySet`, `jwt.decode`, and `AuthlibHTTPError`.
- `httpx.AsyncClient` performs remote JWKS fetches with timeout controlled by `jwks_timeout`.
- HTTP/network failures are wrapped as `AuthlibHTTPError` in `_get_remote_jwks()`.

## Development workflows
- Python requirement is `>=3.13` (`pyproject.toml`); local setup in `Makefile` uses `uv` and currently pins Python `3.14.3`.
- Install deps: `make install` (prod) or `make install-dev` (all groups).
- Run tests: `make test` (or `make test file=tests/multi_jwks/test_get_remote_jwks.py`).
- Run coverage: `make coverage`.
- Lint/format path used by maintainers: `make lint` and `make lint-fix`.

## Project-specific conventions
- Keep async behavior and per-URI locking semantics intact; regressions here will break concurrency assumptions.
- When touching cache logic, update tests that freeze time (`pytest-freezer`) such as `tests/multi_jwks/test_get_public_keys.py`.
- Test fixtures in `tests/multi_jwks/conftest.py` clear `_jwk_set` and `_jwk_locks`; new tests should rely on that isolation pattern.
- Maintain existing misspelt module path `extentions/jwt_clains.py` for compatibility unless doing an explicit migration.
