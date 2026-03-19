from datetime import datetime, timezone

import pytest

from jwks_multi import jwks_multi_verifier


@pytest.mark.freeze_time(datetime.fromtimestamp(100, tz=timezone.utc))
def test_is_cached_returns_false_when_entry_is_expired(verifier) -> None:
    uri = 'https://issuer.example/.well-known/jwks.json'
    jwks_multi_verifier._jwk_set[uri] = {
        'keys': [{'kid': 'cached-key'}],
        'expires_at': 90.0,
    }
    verifier.cache_jwk_set = True

    assert verifier._is_cached(now=100.0, uri=uri, cache_jwk_set=True) is False
