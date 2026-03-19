from unittest.mock import MagicMock

from jwks_multi.jwks_multi_verifier import ExtendedJWTClaims


async def test_decode_token_uses_expected_claim_options(
    mock_jwt,
    verifier,
) -> None:
    claims = MagicMock()
    mock_jwt.decode.return_value = claims

    result = await verifier.decode_token(
        token='token-value',
        key=MagicMock(name='key_set'),
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
    mock_jwt.decode.assert_called_once()
    decode_kwargs = mock_jwt.decode.call_args.kwargs
    assert decode_kwargs['s'] == 'token-value'
    assert decode_kwargs['claims_cls'] is ExtendedJWTClaims
    assert decode_kwargs['claims_options']['iss'] == {
        'essential': True,
        'verify': True,
        'values': ['issuer-a'],
    }
    assert decode_kwargs["claims_options"]["aud"] == {
        "essential": True,
        "verify": True,
        "values": ["audience-a"],
    }
    assert decode_kwargs["claims_options"]["sub"]["verify"] is False
    assert decode_kwargs["claims_options"]["exp"]["verify"] is False
    assert decode_kwargs["claims_options"]["jti"]["verify"] is False
    claims.validate.assert_called_once_with(leeway=7)


async def test_decode_token_initializes_empty_options_when_none(
    mock_jwt,
    verifier,
) -> None:
    claims = MagicMock()
    mock_jwt.decode.return_value = claims

    result = await verifier.decode_token(
        token="token-value",
        key=MagicMock(name="key_set"),
        options=None,
        issuers=None,
        audiences=None,
    )

    assert result is claims
    mock_jwt.decode.assert_called_once()
    decode_kwargs = mock_jwt.decode.call_args.kwargs

    assert decode_kwargs["claims_options"]["sub"]["verify"] is True
    assert decode_kwargs["claims_options"]["exp"]["verify"] is True
    assert decode_kwargs["claims_options"]["nbf"]["verify"] is True
    assert decode_kwargs["claims_options"]["iat"]["verify"] is True
    assert decode_kwargs["claims_options"]["jti"]["verify"] is True
    claims.validate.assert_called_once_with(leeway=0)
