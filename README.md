# Passe — mercado de jogadores

Solução do desafio **Passe** (SENAI/FIEPE, Desenvolvedor Fullstack I): uma API REST para cadastrar jogadores e clubes, comprar e vender jogadores, consultar o histórico de transações, escalar titulares e jogar partidas, mais uma interface web que consome essa API.

| Parte | Tecnologia | Pasta | Estado |
| --- | --- | --- | --- |
| Backend | Python 3.11+, FastAPI, SQLAlchemy, Alembic | [`backend/`](backend) | Pronto: os 19 endpoints do enunciado |
| Banco | PostgreSQL 16 (Docker) | [`backend/docker-compose.yml`](backend/docker-compose.yml) | Pronto |
| Frontend | Next.js, React, Tailwind CSS | [`frontend/`](frontend) | **A completar** (veja a seção 7) |

Depois de subir a API, o Swagger (documentação interativa de todos os endpoints) fica em **http://localhost:8000/docs**.

---

## 1. Pré-requisitos

Sistema de referência: **Ubuntu 24.04** com **Docker** disponível.

| Ferramenta | Versão | Para quê |
| --- | --- | --- |
| Docker Engine + Docker Compose (plugin `docker compose`) | atuais | Banco PostgreSQL (e, opcionalmente, a API) |
| Python | 3.11 ou superior (o Ubuntu 24.04 traz o 3.12) | Backend |
| `python3-venv` e `python3-pip` | do Ubuntu 24.04 | Criar o ambiente virtual e instalar o Poetry |
| Poetry | 2.5.1 | Instalar as dependências do backend a partir do `poetry.lock` |
| Node.js com npm | 22 LTS | Frontend |
| PostgreSQL | 16 | Já vem na imagem `postgres:16-alpine` do Docker Compose; não precisa instalar |

Instalação do Python, do venv e do Poetry numa máquina limpa (o Ubuntu 24.04 não deixa instalar pacotes Python no sistema com `pip`; por isso o Poetry entra num ambiente virtual próprio):

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 -m venv ~/poetry-env
~/poetry-env/bin/pip install poetry==2.5.1
export PATH="$HOME/poetry-env/bin:$PATH"
poetry --version   # deve mostrar 2.5.1
```

O `export PATH` vale só para o terminal aberto; repita-o em cada terminal novo.

---

## 2. Banco de dados: criar e recriar do zero

O banco é criado por **migrations do Alembic** (versionadas em [`backend/alembic/versions`](backend/alembic/versions)). Ele nasce **vazio**: sem jogadores, clubes, transações nem partidas. Não há dados de exemplo.

Todos os comandos abaixo rodam na pasta `backend`.

### Criar

```bash
cd backend
cp .env.example .env
docker compose up -d --wait db
poetry install
poetry run alembic upgrade head
```

- `docker compose up -d --wait db` sobe o PostgreSQL e espera ele ficar pronto.
- `poetry run alembic upgrade head` cria as 7 tabelas: `jogadores`, `clubes`, `contratos`, `transacoes`, `escalacoes`, `partidas` e `duelos_partida`.

### Recriar do zero (apagar e criar de novo)

```bash
cd backend
docker compose down -v
docker compose up -d --wait db
poetry run alembic upgrade head
```

`docker compose down -v` apaga o contêiner **e o volume** com os dados; os dois comandos seguintes criam o banco de novo, vazio.

---

## 3. Instalar e executar

### Backend (API)

Na pasta `backend`, com o banco criado como na seção 2:

```bash
cd backend
poetry run uvicorn app.main:app --no-access-log
```

- **Origem da API:** `http://localhost:8000` (os endpoints ficam sob `/api/v1`, por exemplo `http://localhost:8000/api/v1/players`).
- **Swagger:** `http://localhost:8000/docs`.
- **Verificação rápida:** `curl http://localhost:8000/health` responde `{"status":"ok"}`.
- **Log de requisições:** cada requisição escreve uma linha, por exemplo `2026-11-02T10:15:00-03:00 POST /api/v1/matches 201 12ms` (data e hora em Brasília, método, caminho, status e duração). O `--no-access-log` desliga a linha de acesso do `uvicorn`, que não tem data, para a requisição não aparecer duas vezes.

**Alternativa com Docker (API e banco juntos):**

```bash
cd backend
cp .env.example .env
docker compose up -d --build
```

A API sobe na mesma origem (`http://localhost:8000`) e aplica as migrations ao iniciar. Para parar: `docker compose down`. Não rode esta alternativa junto com o `uvicorn` acima: os dois usam a porta 8000.

### Testes, lint e formatação (backend)

Na pasta `backend`, com o banco criado (os testes de integração e de API usam o PostgreSQL de verdade) e **sem a API recebendo requisições**:

```bash
poetry run pytest -q                    # testes automatizados (terminam sozinhos, sem modo de observação)
poetry run ruff check .                 # lint
poetry run ruff format --check .        # confere a formatação, sem alterar arquivos
```

Os testes não alteram os dados do banco: cada teste roda numa transação que é desfeita no final.

### Frontend

> **A preencher quando o frontend estiver pronto.** Comandos previstos:

```bash
cd frontend
cp .env.example .env.local     # definir NEXT_PUBLIC_API_URL=http://localhost:8000
npm ci
npm run dev
# Interface em http://localhost:3000

# Lint e formatação (na pasta frontend)
npm run lint                   # lint
npm run format:check           # confere a formatação, sem alterar arquivos
```

A API libera, por padrão, a origem `http://localhost:3000` (CORS). Para outra origem, mude `CORS_ORIGINS` no `backend/.env`.

---

## 4. Variáveis de ambiente

Os valores de exemplo estão em [`backend/.env.example`](backend/.env.example) e [`frontend/.env.example`](frontend/.env.example). Copie para `.env` (backend) e `.env.local` (frontend).

| Variável | Onde | Para quê | Exemplo |
| --- | --- | --- | --- |
| `POSTGRES_USER` | backend | Usuário criado no contêiner do PostgreSQL | `passe` |
| `POSTGRES_PASSWORD` | backend | Senha desse usuário (valor de desenvolvimento) | `passe` |
| `POSTGRES_DB` | backend | Nome do banco | `passe` |
| `DATABASE_URL` | backend | Conexão da API e do Alembic com o banco. Fora do Docker, o servidor é `localhost`; dentro do contêiner da API, o Compose troca por `db` | `postgresql+psycopg://passe:passe@localhost:5432/passe` |
| `CORS_ORIGINS` | backend | Origem do frontend que pode chamar a API (uma só; nunca `*`) | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | frontend | Origem da API, sem `/api/v1` | `http://localhost:8000` |

Os valores de senha são apenas de desenvolvimento local.

---

## 5. Estrutura de pastas e bibliotecas

### Estrutura

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py            # cria a API: CORS, log, tratamento de erros e rotas
│   │   ├── api/               # camada HTTP comum: montagem dos casos de uso, erros, Swagger e log
│   │   ├── infrastructure/    # banco, sessão, relógio, unidade de trabalho e configurações
│   │   ├── shared/            # regras comuns: erros, arredondamento, textos e horário de Brasília
│   │   └── modules/
│   │       ├── players/       # jogadores: cadastro, valor de mercado e listagem
│   │       ├── clubs/         # clubes, contratos e elenco
│   │       ├── market/        # compra, venda, histórico de transações e CSV
│   │       └── league/        # escalação, partidas e classificação
│   ├── alembic/               # migrations do banco
│   ├── tests/                 # unit/ (regras e casos de uso), integration/ (banco) e api/ (HTTP)
│   ├── docker-compose.yml     # PostgreSQL (e a API, opcionalmente)
│   ├── Dockerfile             # imagem da API
│   ├── pyproject.toml e poetry.lock
│   └── .env.example
└── frontend/                  # Next.js
```

Cada módulo de `backend/app/modules` tem as mesmas quatro camadas:

- `domain/`: regras de negócio e cálculos, sem banco nem HTTP;
- `application/`: os casos de uso, que coordenam as regras (`BuyPlayer`, `SellPlayer`, `PlayMatch`...);
- `ports/`: os contratos que o módulo precisa de fora (por exemplo, o repositório);
- `adapters/`: o que fala com o mundo: rotas e schemas HTTP (`inbound`) e SQLAlchemy (`outbound`).

Um módulo não acessa o interior de outro: eles conversam por "operações públicas" (classes pequenas, como `PlayersPublicOperations`), e a montagem de tudo fica em `backend/app/api/dependencies.py`.

### Bibliotecas do backend

| Biblioteca | Motivo |
| --- | --- |
| FastAPI | Framework web da API; gera o Swagger (`/docs`) e valida o corpo das requisições |
| Uvicorn (`uvicorn[standard]`) | Servidor que roda o FastAPI |
| SQLAlchemy | ORM: consultas parametrizadas (seguras contra injeção de SQL) e modelos das tabelas |
| psycopg (`psycopg[binary]`) | Driver do PostgreSQL (versão 3), síncrono |
| Alembic | Migrations: criam e recriam o banco por comando |
| pydantic-settings | Lê e valida a configuração a partir das variáveis de ambiente |
| pytest | Testes automatizados |
| httpx | Cliente HTTP exigido pelo `TestClient` do FastAPI, nos testes de API |
| Ruff | Lint e verificação de formatação com uma ferramenta só |
| Poetry | Gerencia as dependências e trava as versões em `poetry.lock` |

### Bibliotecas do frontend

> **A confirmar quando o frontend estiver pronto.** Instaladas até agora:

| Biblioteca | Motivo |
| --- | --- |
| Next.js e React | Framework e biblioteca da interface |
| Tailwind CSS | Estilo da interface |
| shadcn, `@base-ui/react`, `class-variance-authority`, `cn`, `tw-animate-css` | Componentes de interface reutilizáveis e suas variações de estilo |
| lucide-react | Ícones |
| TypeScript, ESLint | Tipagem e lint |
| axios | Cliente HTTP da camada de serviços: converte a resposta e o erro da API num único formato de resultado |
| zod | Valida os formulários antes de enviar e gera o tipo de cada formulário |
| Prettier, `eslint-config-prettier` | Formatação do código (`npm run format:check` só confere, sem alterar arquivos) e fim do conflito de regras entre ESLint e Prettier |

---

## 6. Decisões e premissas

Detalhes que o enunciado não definiu, e como decidi:

1. **Arquitetura.** Monólito modular com quatro módulos (`players`, `clubs`, `market`, `league`) em camadas. Interface (porta) só onde existe uma fronteira de verdade: o banco e a comunicação entre módulos.
2. **Atomicidade.** Uma sessão de banco por requisição e **um único `commit` por operação** (compra, venda, escalação, partida, mudança para `DOENTE`). Todas as conferências acontecem **antes** de qualquer gravação; assim, uma operação recusada não grava nada.
3. **Valores calculados nunca são gravados.** Valor de mercado, overall, valor do elenco, patrimônio, dias restantes, percentual de multa, resultado da partida, pontos e posição são calculados a cada consulta. Só ficam gravados o valor base (uma vez, no cadastro) e os valores do momento das transações, dos contratos e dos duelos.
4. **Listagem de jogadores.** Como o valor de mercado não existe no banco, o repositório devolve os jogadores ativos e a busca, os filtros, a ordenação e a paginação são aplicados em Python (a ordenação em duas passadas estáveis, com desempate por nome e id).
5. **Dinheiro.** `Decimal` em todo o cálculo; o arredondamento (meio para longe do zero) acontece uma única vez no resultado final. O `float` só aparece na resposta JSON.
6. **Ordem dos erros.** Quando um pedido tem mais de um problema, a resposta segue a ordem: formato do corpo e dos parâmetros (`400`), recurso inexistente (`404`) e regra de negócio (`409`). Nunca se combinam dois erros.
7. **Ids e parâmetros estritos.** Id de recurso na URL só é aceito escrito com dígitos, sem zero à esquerda e até 2.147.483.647; qualquer outra forma (`01`, `abc`, `-1`) é um recurso inexistente (`404`). Nos corpos, inteiro como `3.0` é aceito e `"3"` (texto), `true` e `null` são recusados. Nos parâmetros de consulta (`?club_id=`, `?type=`...), valores como `01`, `+1` e `1e2` são recusados com `400`.
8. **Relógio injetado.** A hora vem de um relógio passado ao caso de uso, não de uma chamada direta; os testes fixam a data e reproduzem os exemplos do enunciado. As datas usam o fuso `-03:00`.
9. **Nome do clube único no banco.** Um índice único sobre `lower(nome)`: ignora maiúsculas e minúsculas, mas considera acentos (“Águias FC” e “Aguias FC” são nomes diferentes).
10. **Escalação.** A formação fica na coluna `clubes.formacao`; os titulares, na tabela `escalacoes`, cuja restrição `UNIQUE(jogador_id)` garante um jogador em uma só escalação. O titular vendido ou que fica `DOENTE` sai da escalação na mesma transação; a formação permanece e o clube só volta a jogar quando escalar de novo.
11. **Partida.** O placar sai de 6 duelos, sem sorteio. O cálculo dos duelos e o da classificação ficam cada um num único arquivo do domínio (`duels.py` e `standings.py`).
12. **Documentação da API.** Cada rota tem resumo, descrição e os erros possíveis no Swagger. O FastAPI documentaria sozinho um `422` que esta API nunca devolve (ela responde `400`); removi esse `422` do esquema.
13. **Erro inesperado.** Responde `500` com `{"message": "Erro interno do servidor."}`, sem detalhes internos, e a operação não grava nada.
14. **CORS.** Restrito a uma origem, lida de `CORS_ORIGINS` (padrão `http://localhost:3000`).
15. **Testes com o PostgreSQL de verdade.** Os testes de integração e de API usam o mesmo PostgreSQL do Compose (e não um banco de mentira), cada um dentro de uma transação desfeita no final.
16. **Docker Compose na pasta `backend`.** O `docker-compose.yml` fica em `backend/`, ao lado do `Dockerfile` e do `.env.example`.

---

## 7. Funcionalidades não implementadas

**Backend:** nenhuma. Os 19 endpoints do enunciado estão implementados e testados:

| Módulo | Endpoints |
| --- | --- |
| Jogadores | `POST /players`, `GET /players`, `GET /players/{id}`, `PUT /players/{id}`, `PATCH /players/{id}/condition`, `DELETE /players/{id}` |
| Clubes | `POST /clubs`, `GET /clubs`, `GET /clubs/{id}` |
| Mercado | `POST /players/{id}/buy`, `POST /players/{id}/sell`, `GET /clubs/{id}/transactions`, `GET /clubs/{id}/transactions/export` |
| Liga | `PUT /clubs/{id}/lineup`, `GET /clubs/{id}/lineup`, `POST /matches`, `GET /matches`, `GET /matches/{id}`, `GET /standings` |

Limitações conhecidas:

- No Swagger, os parâmetros de consulta (`GET /players`, `GET /clubs`, `GET /clubs/{id}/transactions` e `GET /matches`) não aparecem como campos para preencher; estão descritos no texto de cada endpoint (eles são lidos do texto bruto da URL para a validação ser estrita).
- Não há comando único do Docker para subir a interface junto com a API e o banco (diferencial opcional).

**Frontend:** *a preencher quando o frontend estiver pronto, listando o que ficou de fora.*

---

## 8. Uso de inteligência artificial

**Ferramenta:** Claude Code (Anthropic), na extensão do VS Code. Este README também foi redigido com o Claude Code.

**Onde foi usado:**

- no código do backend inteiro: os quatro módulos, a API, a configuração do banco, o Docker e o Ruff;
- em todos os testes automatizados (unitários, de integração e de API);
- no frontend: *a preencher.*

**Como e por que:** usei para acelerar o desenvolvimento, principalmente a escrita do código. Eu defini o que construir e as decisões de arquitetura. O Claude Code propunha um plano para cada etapa, eu aprovava ou pedia mudança, e ele escrevia o código e os testes. Eu rodava os comandos (`pytest`, `ruff`, migrations, Docker) e levava os resultados de volta para ele corrigir.

**Sobre os testes:** tenho conhecimento mínimo de testes unitários e não conhecia os outros tipos (testes de integração e de API). Por isso os testes foram escritos pelo Claude Code. Eu os executo e uso o resultado (`poetry run pytest`) para validar o código, mas não os escrevi. Estou ciente de que isso pode ser perguntado na entrevista.

**O que aceitei, alterei ou descartei (exemplos):**

- **Listagem de jogadores.** Eu queria tudo no SQL. Depois de discutir, aceitei filtrar, ordenar e paginar em memória, porque o valor de mercado é calculado e não existe no banco. Também aceitei deixar a paginação na API em vez de no frontend.
- **Exclusão de jogador.** Questionei se deveria apagar do banco; conferimos no enunciado (RN09) que a exclusão é lógica, e mantive assim.
- **Repositórios.** Entre duas opções, escolhi que o repositório do SQLAlchemy herde explicitamente do contrato (`Protocol`).
- **Erros do Claude Code que foram corrigidos.** Ele usou uma sintaxe do Python 3.12 que quebraria no 3.11 da imagem Docker; fez uma afirmação errada sobre o barema; e escreveu um teste com um parâmetro repetido. Os erros apareceram ao conferir o código, ao rodar os testes ou ao reler o enunciado, e foram corrigidos antes do commit.
