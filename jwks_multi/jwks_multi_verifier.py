import asyncio
import logging
import time
from typing import Any

import httpx
from joserfc import jwt
from joserfc.errors import MissingKeyError
from joserfc.jwk import Key, KeySet, KeySetSerialization

from jwks_multi.extentions.jwt_clains import ExtendedJWTClaims

logger = logging.getLogger('jwks_multi')

_jwk_set: dict[str, dict[str, list[Key] | float]] = {}
_jwk_locks: dict[str, asyncio.Lock] = {}


async def get_public_keys(
    jwks_urls: list[str],
    pre_public_keys: dict[str, Any],
    *,
    cache_jwk_set: bool = True,
    jwks_ttl: float | None = None,
    jwks_timeout: float = 5.0,
) -> KeySet:
    if pre_public_keys:
        _add_keys_from_jwks(
            uri='localhost',
            jwks=pre_public_keys,
        )
    await _get_remote_jwks(
        jwks_urls,
        jwks_timeout,
        jwks_ttl,
        cache_jwk_set=cache_jwk_set,
    )
    return _get_jwks_set()


async def decode_token(
    token: str,
    key: KeySet,
    options: dict[str, bool | int | float] | None = None,
    issuers: list[str] | None = None,
    audiences: list[str] | None = None,
) -> jwt.Claims:
    if not options:
        options = {}
    if not issuers:
        issuers = []
    if not audiences:
        audiences = []
    token = jwt.decode(
        value=token,
        key=key,
    )
    claims_requests = ExtendedJWTClaims(
        leeway=options.get('leeway') or 0,
        iss={
            'essential': True,
            'values': issuers,
        },
        aud={
            'essential': True,
            'values': audiences,
        },
        sub={
            'essential': True,
            'allow_blank': not options.get('verify_sub', True),
        },
        exp={
            'essential': False,
            'allow_blank': not options.get('verify_exp', True),
        },
        nbf={
            'essential': False,
            'allow_blank': not options.get('verify_nbf', True),
        },
        iat={
            'essential': True,
            'allow_blank': not options.get('verify_iat', True),
        },
        jti={
            'essential': True,
            'allow_blank': not options.get('verify_jti', True),
        },
    )
    claims_requests.validate(token.claims)
    return token.claims


def _get_jwks_set() -> KeySet:
    jwks_set = []
    for jwk in _jwk_set.values():
        jwks_set.extend(jwk['keys'])
    if not jwks_set:
        raise MissingKeyError(
            description=(
                'No JWKS keys available. '
                'Verify the provided URLs and pre_public_keys.'
            ),
        )
    return KeySet(jwks_set)


def _add_keys_from_jwks(
    uri: str,
    jwks: KeySetSerialization,
    expires_at: float = -1,
) -> None:
    if jwks and 'keys' in jwks:
        key_set = KeySet.import_key_set(jwks)
        _jwk_set[uri] = {'keys': key_set.keys, 'expires_at': expires_at}


def _is_cached(now: float, uri: str, *, cache_jwk_set: bool) -> bool:
    if not cache_jwk_set:
        return False
    jwks_data = _jwk_set.get(uri)
    if not jwks_data:
        return False
    expires = jwks_data.get('expires_at') or -1
    return expires == -1 or now < expires


def _get_uri_lock(uri: str) -> asyncio.Lock:
    lock = _jwk_locks.get(uri)
    if lock is None:
        lock = asyncio.Lock()
        _jwk_locks[uri] = lock
    return lock


async def _get_remote_jwks(
    jwks_urls: list[str],
    jwks_timeout: float = 5.0,
    jwks_ttl: float | None = None,
    *,
    cache_jwk_set: bool = True,
) -> dict[str, dict[str, list[Any] | float]]:
    try:
        async with httpx.AsyncClient(timeout=jwks_timeout) as client:
            for uri in jwks_urls:
                if uri == 'localhost':
                    continue
                if _is_cached(time.time(), uri, cache_jwk_set=cache_jwk_set):
                    continue
                async with _get_uri_lock(uri):
                    if _is_cached(
                        time.time(),
                        uri,
                        cache_jwk_set=cache_jwk_set,
                    ):
                        continue
                    logger.info(
                        '[ExtendedPyJWKClient] Fetching data from %s',
                        uri,
                    )
                    response = await client.get(uri)
                    response.raise_for_status()
                    jwks_data = response.json()

                    expires_at = -1
                    if jwks_ttl:
                        expires_at = time.time() + jwks_ttl
                    _add_keys_from_jwks(
                        uri=uri,
                        jwks=jwks_data,
                        expires_at=expires_at,
                    )

    except httpx.HTTPError:
        logger.exception('Fail to fetch data from the url %s', uri)

    return _jwk_set
