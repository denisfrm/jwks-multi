from unittest.mock import MagicMock, patch

from pytest import fixture


@fixture
def mock_extended_jwt_claims():
    with patch('jwks_multi.jwks_multi_verifier.ExtendedJWTClaims') as mocked:
        yield mocked


async def test_decode_token_uses_expected_claim_options(
    mock_jwt,
    verifier,
    mock_extended_jwt_claims,
) -> None:
    claims = MagicMock()
    mock_jwt.decode.return_value.claims = claims
    mock_key = MagicMock(name='key_set')

    result = await verifier.decode_token(
        token='token-value',
        key=mock_key,
        options={
            'verify_sub': False,
            'verify_exp': False,
            'verify_nbf': True,
            'verify_iat': True,
            'verify_jti': False,
            'leeway': 7,
        },
        issuers=['issuer-a'],
        audiences=['audience-a'],
    )

    assert result is claims
    mock_jwt.decode.assert_called_once_with(
        value='token-value',
        key=mock_key,
    )
    mock_extended_jwt_claims.assert_called_once_with(
        leeway=7,
        iss={'essential': True, 'values': ['issuer-a']},
        aud={'essential': True, 'values': ['audience-a']},
        sub={'essential': True, 'allow_blank': True},
        exp={'essential': False, 'allow_blank': True},
        nbf={'essential': False, 'allow_blank': False},
        iat={'essential': True, 'allow_blank': False},
        jti={'essential': True, 'allow_blank': True},
    )
    mock_extended_jwt_claims.return_value.validate.assert_called_once_with(
        mock_jwt.decode.return_value.claims,
    )


async def test_decode_token_initializes_empty_options_when_none(
    mock_jwt,
    verifier,
    mock_extended_jwt_claims,
) -> None:
    claims = MagicMock()
    mock_jwt.decode.return_value.claims = claims
    mock_key = MagicMock(name='key_set')

    result = await verifier.decode_token(
        token='token-value',
        key=mock_key,
        options=None,
        issuers=None,
        audiences=None,
    )

    assert result is claims
    mock_jwt.decode.assert_called_once_with(
        value='token-value',
        key=mock_key,
    )
    mock_extended_jwt_claims.assert_called_once_with(
        leeway=0,
        iss={'essential': True, 'values': []},
        aud={'essential': True, 'values': []},
        sub={'essential': True, 'allow_blank': False},
        exp={'essential': False, 'allow_blank': False},
        nbf={'essential': False, 'allow_blank': False},
        iat={'essential': True, 'allow_blank': False},
        jti={'essential': True, 'allow_blank': False},
    )
    mock_extended_jwt_claims.return_value.validate.assert_called_once_with(
        mock_jwt.decode.return_value.claims,
    )
