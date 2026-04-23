# JWKs Multi Verifier

Biblioteca Python para validacao de JWT com suporte a multiplas fontes JWKS, cache e chaves locais de fallback.

API publica principal:

- `from jwks_multi import get_public_keys, decode_token`

## Instalacao via URL (Git)

### pip

```bash
pip install "git+ssh://git@<repo>/jwks-multi.git"
pip install "git+ssh://git@<repo>/jwks-multi.git@main"
pip install "git+ssh://git@<repo>/jwks-multi.git@v<tag>"
pip install "git+ssh://git@<repo>/jwks-multi.git@<commit_sha>"
```

## Uso

### Fluxo basico

```python
import asyncio

from jwks_multi import get_public_keys, decode_token


async def main() -> None:
	key_set = await get_public_keys(
		jwks_urls=["https://idp.exemplo.com/.well-known/jwks.json"],
		pre_public_keys={},
	)

	claims = await decode_token(
		token="<jwt>",
		key=key_set,
		options={},
		issuers=["https://idp.exemplo.com/"],
		audiences=["minha-api"],
	)

	print(claims)


asyncio.run(main())
```

### Parametros disponiveis

#### `get_public_keys(...)`

Retorna um `KeySet` com a uniao de chaves locais (`pre_public_keys`) e chaves remotas (`jwks_urls`).

| Parametro | Tipo | Padrao | Descricao |
| --- | --- | --- | --- |
| `jwks_urls` | `list[str]` | obrigatorio | Lista de endpoints JWKS remotos. |
| `pre_public_keys` | `dict[str, Any]` | obrigatorio | JWKS local no formato `{"keys": [...]}` para fallback. |
| `cache_jwk_set` | `bool` | `True` | Habilita/desabilita cache em memoria por URI. |
| `jwks_ttl` | `int \| float \| None` | `None` | Tempo de vida (segundos) do cache remoto. `None` significa sem expiracao. |
| `jwks_timeout` | `int \| float` | `5.0` | Timeout (segundos) das requisicoes HTTP para JWKS remoto. |

#### `decode_token(...)`

Decodifica e valida o token com `ExtendedJWTClaims`.

| Parametro | Tipo | Padrao | Descricao |
| --- | --- | --- | --- |
| `token` | `str` | obrigatorio | JWT serializado. |
| `key` | `KeySet` | obrigatorio | Chaves retornadas por `get_public_keys(...)`. |
| `options` | `dict[str, bool \| float] \| None` | `None` | Controle fino das validacoes (`verify_sub`, `verify_exp`, `verify_nbf`, `verify_iat`, `verify_jti`). Inclui `leeway` (folga em segundos para validacao temporal). |
| `issuers` | `list[str] \| None` | `None` | Lista de emissores aceitos para claim `iss`. |
| `audiences` | `list[str] \| None` | `None` | Lista de audiencias aceitas para claim `aud`. |

### Exemplo avancado

```python
import asyncio

from jwks_multi import get_public_keys, decode_token


async def validate(token: str) -> dict:
	key_set = await get_public_keys(
		jwks_urls=[
			"https://idp-a.exemplo.com/.well-known/jwks.json",
			"https://idp-b.exemplo.com/.well-known/jwks.json",
		],
		pre_public_keys={
			"keys": [
				{
					"kty": "RSA",
					"kid": "local-fallback-kid",
					"use": "sig",
					"alg": "RS256",
					"n": "<modulus>",
					"e": "AQAB",
				}
			]
		},
		cache_jwk_set=True,
		jwks_ttl=300,
		jwks_timeout=2.5,
	)

	claims = await decode_token(
		token=token,
		key=key_set,
		options={
			"verify_sub": True,
			"verify_exp": True,
			"verify_nbf": True,
			"verify_iat": True,
			"verify_jti": True,
			"leeway": 5,
		},
		issuers=["https://idp-a.exemplo.com/", "https://idp-b.exemplo.com/"],
		audiences=["api-interna"],
	)

	return dict(claims)


# asyncio.run(validate("<jwt>"))
```

### Observacoes importantes

- O cache e mantido em memoria no processo e separado por URI de JWKS.
- Quando `jwks_ttl=None`, as chaves remotas nao expiram (ate reinicio do processo).
- URLs com valor literal `"localhost"` sao tratadas como pseudo-origem local e nao geram chamada HTTP.

## Desenvolvimento local

```bash
pip install -e .
python -c "from jwks_multi import get_public_keys, decode_token; print('API loaded successfully')"
```

## Changelog

O Changelog é gerado pela ferramenta [towncrier](https://github.com/twisted/towncrier).

Para criar o changelog da sua alteração, é necessário criar um arquivo em `changelog.d` com o sufixo desejado:

- ``.feature``: para nova funcionalidade
- ``.bugfix``: para correção de bug.
- ``.doc``: para uma melhoria na documentação.
- ``.removal``: para uma suspensão de uso ou remoção de API pública.
- ``.misc``: para uma alteração que não é de interesse do usuário.
- ``.health``: para refatoração, atualização de dependências.
- ``.security``: para correção de vulnerabilidade de segurança.

É recomendado como uso do prefixo o código do card referente ao MR.
Ex: ```TST123-xablau.feature```

Cada entrada do changelog deve estar em um arquivo separado.

### Categorias do changelog

As categorias do changelog seguem o padrão [Keep a Changelog](https://keepachangelog.com/en/1.1.0/):

- **Added**: Nova funcionalidade.
- **Changed**: Alteração em funcionalidade existente (refatoração, atualização de dependências, melhorias internas).
- **Fixed**: Correção de bug.
- **Removed**: Remoção de funcionalidade.
- **Deprecated**: Funcionalidade que será removida em breve.
- **Security**: Correção de vulnerabilidade de segurança.