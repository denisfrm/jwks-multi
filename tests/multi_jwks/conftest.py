from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from jwks_multi import jwks_multi_verifier


@pytest.fixture(autouse=True)
def clear_jwks_state():
    jwks_multi_verifier._jwk_set.clear()
    jwks_multi_verifier._jwk_locks.clear()
    yield
    jwks_multi_verifier._jwk_set.clear()
    jwks_multi_verifier._jwk_locks.clear()


@pytest.fixture()
def verifier():
    return jwks_multi_verifier


@pytest.fixture
def mock_jwt():
    with patch('jwks_multi.jwks_multi_verifier.jwt') as mocked:
        yield mocked


@pytest.fixture
def mock_async_client():
    with patch('jwks_multi.jwks_multi_verifier.httpx.AsyncClient') as mocked:
        client = AsyncMock()
        mocked.return_value.__aenter__.return_value = client
        mocked.return_value.__aexit__.return_value = False
        client.get.return_value.json = MagicMock()
        yield mocked, client
