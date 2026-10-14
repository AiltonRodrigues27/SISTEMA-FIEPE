## Regras de código

1. **Interfaces nas fronteiras, não em todo lugar.** `Protocol` (ou ABC quando precisar de comportamento compartilhado) em `ports/`, definido por quem consome. Onde não há fronteira (infra, outro módulo, algo que precisa ser trocado ou mockado), use o tipo concreto. Não crie interface, factory ou classe "porque Clean Code manda".
2. **Nomes que explicam.** O nome diz o que a variável ou função representa. Sem `data`, `info`, `handle`, `process`, `tmp`. `snake_case` para funções e variáveis, `PascalCase` para classes, conforme PEP 8; nomes curtos só em escopo curto (`i`, `req`, `err`).
3. **Funções pequenas.** Uma função faz uma coisa bem definida. Se precisa de "e" para descrevê-la, divida.
4. **Responsabilidade única.** Router (endpoint FastAPI) converte HTTP em chamada de caso de uso e o resultado em `response_model`. Service aplica regra. Repository fala com o banco. Integração externa fica atrás de uma porta.
5. **Simples primeiro.** Sem metaclasses, decorators mágicos, herança elaborada ou generics sem necessidade concreta e presente.
6. **Poucos parâmetros.** Passou de 3 ou 4, agrupe num `dataclass` ou modelo Pydantic de input com nome claro.
7. **Sem booleano mágico.** `enviar(True)` não. Use `Enum`, `dataclass`/modelo Pydantic com campos nomeados, ou duas funções.
8. **Sem comentário óbvio.** Comente o porquê, nunca o quê. Todo pacote (`__init__.py`) tem docstring curta explicando seu propósito.
9. **Sem lógica duplicada.** A mesma regra em dois lugares vira uma função no `domain`. Mas só abstraia na segunda ou terceira repetição real, nunca na primeira.
10. **Erro tratado de verdade.** Nunca `except Exception: pass`, nunca engolir. Faça `raise ... from err` preservando contexto. Erros de domínio são classes próprias (`class PetNaoEncontrado(DomainError)`) reconhecidas via `isinstance`/`except`. **Um único lugar** (exception handler global do FastAPI, `@app.exception_handler`) traduz erro de domínio em status HTTP. `assert`/exceção não tratada só em bug de programação.
11. **Separação HTTP × regra × banco × integração.** Ver regra 4. Entidade de `domain` é `dataclass`/classe pura, sem `BaseModel` do Pydantic nem modelo do ORM; schema de request/response (Pydantic) e modelo de banco (SQLAlchemy/SQLModel) ficam no adapter.
12. **Sem abstração prematura.** Ver regra 1. Prefira duplicar um pouco a abstrair errado.
13. **Consistência.** Mesmo padrão de nome, estrutura e estilo em todos os módulos. Antes de inventar, olhe como os outros módulos fazem. `black`, `ruff` e `mypy` são a palavra final.
14. **Sem código morto.** Nada de código comentado, função sem uso ou variável sem uso. Git guarda o histórico.
15. **Composição.** Monte comportamento com classes pequenas e composição com critério. Sem hierarquias profundas de herança.
16. **Dependência explícita.** Toda dependência chega por construtor ou `Depends()` do FastAPI (`XService(repo, clock)`). Nada de variável global, estado de módulo com efeito colateral ou singleton escondido. Relógio, gerador de ID e similares também são injetados.
17. **Testável.** Regra isolada de I/O é fácil de testar. Se está difícil de testar, o design está errado: ajuste o design, não o teste.
18. **Poucos efeitos colaterais.** O nome da função anuncia o que ela faz. Nada de função `validar` que também grava.
19. **Refatore continuamente.** Funcionando não é terminado. Ao tocar numa área, deixe-a melhor, mas em commit separado do da feature.

## Testes

Nada entra sem teste. O teste prova que a implementação está certa.
- **Unitário:** `domain` e `service`, com fakes escritos à mão das portas (`Protocol`). Parametrizado com `pytest.mark.parametrize`. Rápidos, sem I/O.
- **Integração:** adapters de banco contra Postgres real (testcontainers), com migrations aplicadas. Não use mock de banco para validar SQL.
- **End-to-end:** a API de pé, requisições HTTP reais via `httpx.AsyncClient`/`TestClient`, banco real, cobrindo os fluxos principais de ponta a ponta.
- **Arquitetura:** teste dedicado (ex.: `import-linter` ou verificação customizada em `tests/test_architecture.py`) falha o CI se `domain` importar infra ou se um módulo importar o interior de outro.
- Bug corrigido ganha primeiro um teste que o reproduz.
- Teste não é feature: nome diz o comportamento (`test_agendar_horario_ocupado_retorna_erro`).

## Commits

- **Commit por feature, e gradual:** cada commit faz uma coisa só e deixa o projeto compilando com testes passando.
- Refactor, formatação e feature não se misturam no mesmo commit.
- Mensagem no padrão Conventional Commits, em português, no imperativo: `feat(scheduling): cria caso de uso de agendar consulta`.
- Escopo = módulo (`identity`, `organization`, `customer`, `pet`, `scheduling`, `clinical`, `platform`) ou área (`ci`, `db`).
- **Só commita quando o Ailton pedir.** Nunca `--no-verify`, nunca force push, nunca reescrever histórico publicado.

