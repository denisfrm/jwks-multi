# Changelog

## [Unreleased]

## [0.1.0] - 2026-03-19

### Added

- Lançamento inicial da biblioteca `jwks-multi-verifier`, com a API pública `JWKSMultiSourceVerifier` para validar JWTs usando múltiplas fontes JWKS, cache em memória com TTL opcional, chaves locais de fallback e validação estendida de claims. (first)

### Changed

- documentação de uso no README.md, com fluxo básico, exemplo avançado, parâmetros e observações importantes (first)

### Changed

- Estruturado o fluxo inicial de empacotamento e release da biblioteca, com metadados do projeto, licença MIT, dependências de release (`build` e `twine`) e o alvo `make release-check` para validar artefatos localmente. (first)
