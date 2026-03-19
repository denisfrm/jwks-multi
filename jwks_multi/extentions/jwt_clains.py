import time

from authlib.jose import JWTClaims


class ExtendedJWTClaims(JWTClaims):
    def __init__(self, *args: list, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self.claims_with_expiration = ['exp', 'nbf', 'iat']

    def validate(
        self,
        now: float | None = None,
        leeway: float = 0,
    ) -> None:
        if now is None:
            now = float(time.time())
        self._validate_essential_claims()
        for key, values in self.options.items():
            if key not in self.REGISTERED_CLAIMS:
                self._validate_claim_value(key)
                continue
            if values.get('verify') is False:
                continue
            validation = getattr(self, f'validate_{key}')
            if key in self.claims_with_expiration:
                validation(now, leeway)
            else:
                validation()
