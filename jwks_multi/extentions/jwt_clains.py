from collections.abc import Callable

from joserfc.jwt import ClaimsOption, JWTClaimsRegistry


class ExtendedJWTClaims(JWTClaimsRegistry):
    def __init__(
        self,
        now: int | Callable[[], int] | None = None,
        leeway: int = 0,
        **claims_options: ClaimsOption,
    ) -> None:
        super().__init__(now, leeway, **claims_options)

    def validate_exp(self, value: int) -> None:
        if self.options.get('exp', {}).get('allow_blank', False):
            return
        super().validate_exp(value)

    def validate_nbf(self, value: int) -> None:
        if self.options.get('nbf', {}).get('allow_blank', False):
            return
        super().validate_nbf(value)

    def validate_iat(self, value: int) -> None:
        if self.options.get('iat', {}).get('allow_blank', False):
            return
        super().validate_iat(value)
