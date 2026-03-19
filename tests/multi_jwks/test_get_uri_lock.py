def test_get_uri_lock_reuses_same_lock_instance(verifier) -> None:
    uri = 'https://issuer.example/.well-known/jwks.json'

    first_lock = verifier._get_uri_lock(uri)
    second_lock = verifier._get_uri_lock(uri)

    assert first_lock is second_lock
