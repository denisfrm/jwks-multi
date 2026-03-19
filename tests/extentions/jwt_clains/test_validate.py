from unittest.mock import MagicMock, patch

import pytest

from jwks_multi.extentions.jwt_clains import ExtendedJWTClaims


@pytest.fixture
def mock_time():
    with patch(
        'jwks_multi.extentions.jwt_clains.time.time',
        return_value=123.0,
    ) as mocked:
        yield mocked


@pytest.fixture
def claims():
    return ExtendedJWTClaims(payload={}, header={})


def test_validate_uses_time_and_validates_all_claim_paths(mock_time, claims):
    claims.options = {
        'custom': {'verify': True},
        'exp': {'verify': True},
        'aud': {'verify': False},
        'iss': {'verify': True},
    }
    claims._validate_essential_claims = MagicMock()
    claims._validate_claim_value = MagicMock()
    claims.validate_exp = MagicMock()
    claims.validate_aud = MagicMock()
    claims.validate_iss = MagicMock()

    claims.validate(leeway=4)

    mock_time.assert_called_once_with()
    claims._validate_essential_claims.assert_called_once_with()
    claims._validate_claim_value.assert_called_once_with('custom')
    claims.validate_exp.assert_called_once_with(123, 4)
    claims.validate_aud.assert_not_called()
    claims.validate_iss.assert_called_once_with()


def test_validate_prefers_explicit_now_over_current_time(mock_time, claims):
    claims.options = {
        'nbf': {'verify': True},
    }
    claims._validate_essential_claims = MagicMock()
    claims._validate_claim_value = MagicMock()
    claims.validate_nbf = MagicMock()

    claims.validate(now=999, leeway=2)

    mock_time.assert_not_called()
    claims._validate_essential_claims.assert_called_once_with()
    claims._validate_claim_value.assert_not_called()
    claims.validate_nbf.assert_called_once_with(999, 2)
