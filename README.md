# Anka Tech — Backend

Backend assíncrono em FastAPI com PostgreSQL, Redis e integração de mercado (Yahoo Finance) com retry/backoff e cache TTL de 1h.
Foco em MVP funcional, código limpo e base pronta para evolução.

> Para subir tudo via Docker (DB, Redis, Backend e Front), use o repo infra.
Passos completos no README.md do repositório anka-tech-infra.

## 🏗 Stack principal

- FastAPI + Uvicorn
- SQLAlchemy 2 (Async) + Alembic
- Pydantic v2
- httpx (HTTP/2) + tenacity (retry/backoff)
- redis.asyncio (cache com TTL)
- JWT (login) + escopos admin e read-only

## 🚧 Coleção do Insomnia (para testes manuais)

No desenvolvimento utilizei do app Insomnia para visualizar e acompanhar o funcionamento das rotas, e inclui no repositório a coleção anka_tech_insomnia_routes.json para que qualquer um também fazer o mesmo.

**Como usar:**

- Abra o Insomnia → Application → Import → From File…
- Selecione anka_tech_insomnia_routes.json.
- Faça login em POST /auth/login:

```bash
email: admin@example.com
senha: changeme
```
- O token Bearer é propagado automaticamente para as demais rotas.

## 🚦 Endpoints (resumo)

- Auth
  - POST /auth/login → { access_token, token_type }

- Clientes
  - GET /clients?search=&status=&page=&page_size=
  - POST /clients
  - GET /clients/{id}
  - PUT/PATCH /clients/{id}
  - DELETE /clients/{id}

- Ativos
  - GET /assets/available?q=VALE&limit=10
  > Busca dinâmica Yahoo + cache (TTL 1h). Headers de inspeção: X-Cache, X-Cache-TTL, X-Cache-Key.

- Alocações por cliente
  - GET /clients/{client_id}/allocations
  > Inclui current_price e daily_change_pct (best-effort).
  - POST /clients/{client_id}/allocations
  - PATCH /clients/{client_id}/allocations/{allocation_id}
  - DELETE /clients/{client_id}/allocations/{allocation_id} (204)

## 📝 Checklist do Case (PDF)

### Funcionalidades obrigatórias

- Clientes: CRUD, paginação, busca e filtro por status ✔
- Ativos: cadastro de alocação por cliente; lista dinâmica da Yahoo ✔
- Alocação: exibir preço atual, variação diária % (on-the-fly) e rentabilidade acumulada - **pendente**
- Rentabilidade diária: consulta do preço de fechamento e atualização de **daily_returns** - **pendente**
- Exportação: endpoint CSV/Excel - **pendente**

### Requisitos técnicos (backend)

- FastAPI (async) + Uvicorn, SQLAlchemy 2 + Alembic, Pydantic v2, JWT com perfis ✔
- Cache de preços com TTL 1h (Redis) ✔
- Backoff para rate-limit da Yahoo (tenacity) ✔
- Celery + Redis (tarefas assíncronas) - **pendente**
- Pytest (≥80%), Ruff/Black - **pendente**
- PostgreSQL 15 em container ✔

### Desafios de lógica

- Cache preços (TTL 1h) ✔
- Lidar com rate-limit (back-off) ✔
- IRR simples (rentabilidade diária com série de preços) - **pendente**
- WebSocket com streaming de preços (5s) - **pendente**

## 📌 Notas técnicas

- Eager load (selectinload) nos relacionamentos evita lazy-load assíncrono e o erro MissingGreenlet em consulta de alocações.
- Batch + cache nas cotações: reduz latência e consumo da API externa.

<hr/>

🚀 Projeto desenvolvido com dedicação e carinho.
✨ Animado para poder contribuir profissionalmente com o time.
