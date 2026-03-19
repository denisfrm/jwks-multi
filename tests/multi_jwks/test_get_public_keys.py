from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from jwks_multi import jwks_multi_verifier


@pytest.fixture
def mock_key_set():
    with patch('jwks_multi.jwks_multi_verifier.KeySet') as mocked:
        mocked.side_effect = lambda keys: SimpleNamespace(keys=list(keys))
        yield mocked


@pytest.fixture
def mock_import_key_set():
    with patch(
        'jwks_multi.jwks_multi_verifier.JsonWebKey.import_key_set'
    ) as mocked:
        mocked.side_effect = lambda jwks: SimpleNamespace(
            keys=list(jwks['keys'])
        )
        yield mocked


@pytest.mark.freeze_time(datetime.fromtimestamp(100, tz=timezone.utc))
async def test_get_public_keys_merges_local_and_remote_sources(
    mock_import_key_set,
    mock_key_set,
    mock_async_client,
    verifier,
):
    _, client = mock_async_client
    response = MagicMock()
    response.json.return_value = {'keys': [{'kid': 'remote-key'}]}
    client.get.return_value = response

    result = await verifier.get_public_keys(
        jwks_urls=['https://issuer.example/.well-known/jwks.json'],
        pre_public_keys={'keys': [{'kid': 'local-key'}]},
        jwks_ttl=30,
    )

    assert {key['kid'] for key in result.keys} == {"local-key", "remote-key"}
    assert (
        jwks_multi_verifier._jwk_set[
            "https://issuer.example/.well-known/jwks.json"
        ]["expires_at"]
        == 130.0
    )
    client.get.assert_awaited_once_with(
        "https://issuer.example/.well-known/jwks.json"
    )
    response.raise_for_status.assert_called_once_with()
    assert mock_import_key_set.call_count == 2
    mock_key_set.assert_called_once()
