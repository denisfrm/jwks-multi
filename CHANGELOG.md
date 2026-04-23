# Changelog

## [Unreleased]

## [0.3.0] - 2026-04-23

No significant changes.


## [0.2.0] - 2026-03-24

### Added

- Adjust for raise only dont have any public keys. (raise-only-not-keys)

### Changed

- Adjust quality pipeline to dont copy .env-sample file to the build folder, as it is not needed for the quality pipeline and it can cause confusion if it is present in the build folder. (quality-pipeline)

### Changed

- Adjust logger name to match the new package structure. This is necessary to ensure that log messages are correctly categorized and can be filtered appropriately in logging systems. The new logger name should reflect the updated package structure while maintaining clarity and consistency with existing logging practices. (logger-name)


## [0.1.0] - 2026-03-19

### Added

- Lançamento inicial da biblioteca `jwks-multi-verifier`, com a API pública `JWKSMultiSourceVerifier` para validar JWTs usando múltiplas fontes JWKS, cache em memória com TTL opcional, chaves locais de fallback e validação estendida de claims. (first)

### Changed

- documentação de uso no README.md, com fluxo básico, exemplo avançado, parâmetros e observações importantes (first)

### Changed

- Estruturado o fluxo inicial de empacotamento e release da biblioteca, com metadados do projeto, licença MIT, dependências de release (`build` e `twine`) e o alvo `make release-check` para validar artefatos localmente. (first)
