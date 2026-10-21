## Como trabalhamos (regra mais importante)

1. **Mostrar antes de escrever.** Antes de criar ou alterar código, o Claude mostra na conversa exatamente o que vai gerar, arquivo por arquivo, e só grava no disco depois do "sim" explícito do Ailton.
2. **A decisão é do Ailton.** O Claude debate opções, recomenda e aponta o trade-off. Não decide sozinho nem implementa uma escolha que o Ailton ainda não confirmou.

## Regras de código

1. **Interfaces nas fronteiras, não em todo lugar.** `Protocol` (ou ABC quando precisar de comportamento compartilhado) em `ports/`, definido por quem consome. Onde não há fronteira (infra, outro módulo, algo que precisa ser trocado ou mockado), use o tipo concreto. Não crie interface, factory ou classe "porque Clean Code manda".
2. **Nomes que explicam.** O nome diz o que a variável ou função representa. Sem `data`, `info`, `handle`, `process`, `tmp`. `snake_case` para funções e variáveis, `PascalCase` para classes, conforme PEP 8; nomes curtos só em escopo curto (`i`, `req`, `err`). **Identificadores em inglês:** classes, funções, variáveis, arquivos e nomes de teste ficam em inglês, iguais aos campos da API (`base_value`, `club_id`). Só ficam em português os nomes do banco definidos pelo enunciado (tabelas e colunas), os valores de lista do enunciado (membros dos enums, como `GOL`, `APTO` e `COMPRA`), os textos exibidos ao usuário (`message`) e as mensagens de commit. Misturar idiomas nos identificadores é punido no barema (B2).
3. **Funções pequenas.** Uma função faz uma coisa bem definida. Se precisa de "e" para descrevê-la, divida.
4. **Responsabilidade única.** Router (endpoint FastAPI) converte HTTP em chamada de caso de uso e o resultado em `response_model`. Caso de uso coordena o fluxo, e a regra de negócio fica no `domain`. Adapter de persistência (que implementa a porta de repositório) fala com o banco. Integração externa fica atrás de uma porta.
5. **Simples primeiro.** Sem metaclasses, decorators mágicos, herança elaborada ou generics sem necessidade concreta e presente.
6. **Poucos parâmetros.** Passou de 3 ou 4, agrupe num `dataclass` ou modelo Pydantic de input com nome claro.
7. **Sem booleano mágico.** `enviar(True)` não. Use `Enum`, `dataclass`/modelo Pydantic com campos nomeados, ou duas funções.
8. **Sem comentário óbvio.** Comente o porquê, nunca o quê. Todo pacote (`__init__.py`) tem docstring curta explicando seu propósito.
9. **Sem lógica duplicada.** A mesma regra em dois lugares vira uma função no `domain`. Mas só abstraia na segunda ou terceira repetição real, nunca na primeira.
10. **Erro tratado de verdade.** Nunca `except Exception: pass`, nunca engolir. Faça `raise ... from err` preservando contexto. Erros de domínio são classes próprias (`class PlayerNotFound(DomainError)`) reconhecidas via `isinstance`/`except`. **Um único lugar** (exception handler global do FastAPI, `@app.exception_handler`) traduz erro de domínio em status HTTP. `assert`/exceção não tratada só em bug de programação.
11. **Separação HTTP × regra × banco × integração.** Ver regra 4. Entidade de `domain` é `dataclass`/classe pura, sem `BaseModel` do Pydantic nem modelo do ORM; schema de request/response (Pydantic) e modelo de banco (SQLAlchemy/SQLModel) ficam no adapter.
12. **Sem abstração prematura.** Ver regra 1. Prefira duplicar um pouco a abstrair errado.
13. **Consistência.** Mesmo padrão de nome, estrutura e estilo em todos os módulos. Antes de inventar, olhe como os outros módulos fazem. `black`, `ruff` e `mypy` são a palavra final.
14. **Sem código morto.** Nada de código comentado, função sem uso ou variável sem uso. Git guarda o histórico.
15. **Composição.** Monte comportamento com classes pequenas e composição com critério. Sem hierarquias profundas de herança.
16. **Dependência explícita.** Toda dependência chega por construtor ou `Depends()` do FastAPI (`XService(repo, clock)`). Nada de variável global, estado de módulo com efeito colateral ou singleton escondido. Relógio, gerador de ID e similares também são injetados.
17. **Testável.** Regra isolada de I/O é fácil de testar. Se está difícil de testar, o design está errado: ajuste o design, não o teste.
18. **Poucos efeitos colaterais.** O nome da função anuncia o que ela faz. Nada de função `validar` que também grava.
<!-- 19. **Refatore continuamente.** Funcionando não é terminado. Ao tocar numa área, deixe-a melhor, mas em commit separado do da feature. -->

## Arquitetura (Clean Architecture + Monólito Modular)

1. **Regra de dependência.** Dependências sempre apontam para dentro: `adapters` conhece `domain`, nunca o contrário. `domain` não importa FastAPI, SQLAlchemy ou Pydantic.
2. **Módulo é fatia vertical fechada.** Cada módulo (`players`, `clubs`, `market`, `league`) tem seu próprio `domain/application/ports/adapters` e não importa o interior de outro módulo. Comunicação entre módulos passa por uma porta explícita ou pela camada de aplicação — nunca acesso direto à entidade/tabela de outro módulo.
3. **Caso de uso coordena, não absorve.** Cada ação da aplicação (`CreatePlayer`, `BuyPlayer`, `SellPlayer`, `PlayMatch`...) orquestra passos (buscar, validar, calcular, persistir, confirmar transação). Cálculo e invariante de negócio ficam no `domain`, não no caso de uso.
4. **Entidade ≠ modelo de persistência ≠ schema de API.** Entidade de domínio representa a regra; modelo SQLAlchemy mapeia tabela; schema Pydantic valida I/O da API. Não funde os três quando isso gera acoplamento real. Converta na borda (adapter), sem criar conversão complexa que não agrega valor.
5. **Porta é contrato de necessidade, não de time.** Caso de uso depende do que precisa fazer (`ports/`), adapter implementa com SQLAlchemy. Crie interface só quando protege uma fronteira real ou permite troca com benefício concreto — não por classe.
6. **Injeção, não criação.** Dependência chega de fora (`Depends()` em produção, fake nos testes). Caso de uso nunca instancia seu próprio repositório.
7. **Transação atômica onde a regra exige.** Compra, venda, partida e qualquer fluxo com múltiplas escritas confirmam ou revertem juntos. Transação do SQLAlchemy é suficiente; Unit of Work só se simplificar de verdade.
8. **Erro por responsabilidade, não `HTTPException` espalhada.** `domain` detecta violação de regra; caso de uso decide o que fazer; adapter HTTP traduz para status (ex.: saldo insuficiente → 409); adapter de persistência traduz erro técnico de banco quando precisa. `domain` não conhece HTTP.
9. **Teste na camada certa.** Unitário de `domain` (cálculo/regra, sem banco), de caso de uso (coordenação, com fake de porta), de integração (adapter contra Postgres real), de API/E2E (fluxo completo). Não depender só de E2E.
10. **`shared/` não é depósito.** Só entra o que é realmente transversal (abstração de transação, tipo básico, infra comum). Regra de um módulo (ex.: comissão do mercado) continua nele; outros módulos acessam via interface, nunca copiando a fórmula.
11. **Pasta não é arquitetura.** Ter `domain/application/ports/adapters` não garante nada se caso de uso tiver SQL direto, entidade conhecer FastAPI, adapter decidir regra, módulo acessar tabela de outro direto, ou interface existir sem necessidade. O que importa é direção de dependência e separação de responsabilidade.

## Testes

Nada entra sem teste. O teste prova que a implementação está certa.

- **Unitário:** `domain` e `service`, com fakes escritos à mão das portas (`Protocol`). Parametrizado com `pytest.mark.parametrize`. Rápidos, sem I/O.
- **Integração:** adapters de banco contra Postgres real (testcontainers), com migrations aplicadas. Não use mock de banco para validar SQL.
- **End-to-end:** a API de pé, requisições HTTP reais via `httpx.AsyncClient`/`TestClient`, banco real, cobrindo os fluxos principais de ponta a ponta.
- **Arquitetura:** teste dedicado (ex.: `import-linter` ou verificação customizada em `tests/test_architecture.py`) falha o CI se `domain` importar infra ou se um módulo importar o interior de outro.
- Bug corrigido ganha primeiro um teste que o reproduz.
- Teste não é feature: nome diz o comportamento (`test_buy_player_over_cash_limit_returns_conflict`).

## Commits

- **Graduais: uma unidade pequena por commit** (um arquivo, uma regra ou uma rota). O projeto compila e os testes passam em cada commit.
- Refactor, formatação e feature não se misturam no mesmo commit.
- Mensagem em Conventional Commits, em português, no imperativo: `feat(players): cria cálculo do valor de mercado`.
- Escopo = módulo (`players`, `clubs`, `market`, `league`) ou área (`infra`, `db`, `api`, `docs`).
- Ao fim de cada entrega, o Claude sugere os cortes de commit e as mensagens. **Quem executa git é só o Ailton.** Nunca `--no-verify`, nunca force push em histórico publicado.
