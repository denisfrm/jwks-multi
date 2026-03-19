from datetime import datetime, timezone
from unittest.mock import call, patch

import httpx
import pytest
from authlib.common.errors import AuthlibHTTPError

from jwks_multi import jwks_multi_verifier


@pytest.fixture
def mock_is_cached():
    with patch('jwks_multi.jwks_multi_verifier._is_cached') as mocked:
        mocked.return_value = True
        mocked.side_effect = (False, False)
        yield mocked


@pytest.mark.freeze_time(datetime.fromtimestamp(100, tz=timezone.utc))
async def test_get_remote_jwks_skips_fetch_when_cache_is_valid(
    mock_async_client,
    verifier,
    mock_is_cached,
) -> None:
    mock_is_cached.side_effect = (True, True)
    _, client = mock_async_client
    uri = 'https://issuer.example/.well-known/jwks.json'
    jwks_multi_verifier._jwk_set[uri] = {
        'keys': [{'kid': 'cached-key'}],
        'expires_at': 150.0,
    }

    result = await verifier._get_remote_jwks(
        jwks_urls=[uri],
        jwks_timeout=5.0,
        jwks_ttl=None,
        cache_jwk_set=True,
    )

    assert result[uri]['keys'] == [{'kid': 'cached-key'}]
    client.get.assert_not_awaited()
    mock_is_cached.assert_called_once_with(100.0, uri, cache_jwk_set=True)


@pytest.mark.freeze_time(datetime.fromtimestamp(100, tz=timezone.utc))
async def test_get_remote_jwks_wraps_http_errors(
    mock_async_client,
    verifier,
) -> None:
    mock_async_client_class, client = mock_async_client

    client.get.side_effect = httpx.HTTPError('network failure')

    uri = 'https://issuer.example/.well-known/jwks.json'

    with pytest.raises(
        AuthlibHTTPError, match='Fail to fetch data from the url'
    ):
        await verifier._get_remote_jwks(
            jwks_urls=[uri],
            jwks_timeout=5.0,
            jwks_ttl=None,
            cache_jwk_set=False,
        )


@pytest.mark.freeze_time(datetime.fromtimestamp(100, tz=timezone.utc))
async def test_get_remote_jwks_skips_localhost_uri(
    mock_async_client,
    verifier,
    mock_is_cached,
) -> None:
    _, client = mock_async_client

    result = await verifier._get_remote_jwks(
        jwks_urls=['localhost'],
        jwks_timeout=5.0,
        jwks_ttl=None,
        cache_jwk_set=False,
    )

    assert result == {}
    client.get.assert_not_awaited()
    mock_is_cached.assert_not_called()


@pytest.mark.freeze_time(
    datetime.fromtimestamp(100, tz=timezone.utc),
    auto_tick_seconds=1,
)
async def test_get_remote_jwks_rechecks_cache_inside_lock(
    mock_async_client,
    verifier,
    mock_is_cached,
) -> None:
    mock_is_cached.side_effect = (False, True)
    _, client = mock_async_client
    uri = 'https://issuer.example/.well-known/jwks.json'
    jwks_multi_verifier._jwk_set[uri] = {
        'keys': [{'kid': 'cached-key'}],
        'expires_at': 150.0,
    }

    result = await verifier._get_remote_jwks(
        jwks_urls=[uri],
        jwks_timeout=5.0,
        jwks_ttl=None,
        cache_jwk_set=True,
    )

    assert result[uri]['keys'] == [{'kid': 'cached-key'}]
    client.get.assert_not_awaited()
    mock_is_cached.assert_has_calls(
        [
            call(101.0, uri, cache_jwk_set=True),
            call(102.0, uri, cache_jwk_set=True),
        ]
    )
