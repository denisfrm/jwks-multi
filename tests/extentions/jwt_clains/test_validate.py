import pytest
from joserfc.errors import ExpiredTokenError, InvalidClaimError

from jwks_multi.extentions.jwt_clains import ExtendedJWTClaims

_EXPIRED_TIMESTAMP = 0
_FUTURE_TIMESTAMP = 9_999_999_999


def test_skips_validation_when_allow_blank_is_true():
    claims = ExtendedJWTClaims(exp={'allow_blank': True})
    claims.validate_exp(_EXPIRED_TIMESTAMP)


def test_raises_when_allow_blank_is_false():
    claims = ExtendedJWTClaims(exp={'allow_blank': False})
    with pytest.raises(ExpiredTokenError):
        claims.validate_exp(_EXPIRED_TIMESTAMP)


def test_raises_when_allow_blank_is_not_set():
    claims = ExtendedJWTClaims()
    with pytest.raises(ExpiredTokenError):
        claims.validate_exp(_EXPIRED_TIMESTAMP)


def test_skips_validation_when_nbf_allow_blank_is_true():
    claims = ExtendedJWTClaims(nbf={'allow_blank': True})
    claims.validate_nbf(_FUTURE_TIMESTAMP)


def test_raises_when_nbf_allow_blank_is_false():
    claims = ExtendedJWTClaims(nbf={'allow_blank': False})
    with pytest.raises(InvalidClaimError):
        claims.validate_nbf(_FUTURE_TIMESTAMP)


def test_raises_when_nbf_allow_blank_is_not_set():
    claims = ExtendedJWTClaims()
    with pytest.raises(InvalidClaimError):
        claims.validate_nbf(_FUTURE_TIMESTAMP)


def test_skips_validation_when_iat_allow_blank_is_true():
    claims = ExtendedJWTClaims(iat={'allow_blank': True})
    claims.validate_iat(_FUTURE_TIMESTAMP)


def test_raises_when_iat_allow_blank_is_false():
    claims = ExtendedJWTClaims(iat={'allow_blank': False})
    with pytest.raises(InvalidClaimError):
        claims.validate_iat(_FUTURE_TIMESTAMP)


def test_raises_when_iat_allow_blank_is_not_set():
    claims = ExtendedJWTClaims()
    with pytest.raises(InvalidClaimError):
        claims.validate_iat(_FUTURE_TIMESTAMP)
