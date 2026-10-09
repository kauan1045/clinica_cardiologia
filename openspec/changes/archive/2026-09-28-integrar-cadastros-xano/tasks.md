## 1. Descoberta da API

- [x] 1.1 Baixar o Swagger (`apispec:` + `?type=json`) e listar método, token e entradas de `/paciente`, `/medico`, `/lista_medico`, `/convenio` e `/exame`.
- [x] 1.2 Fazer somente `GET` em `/paciente`, `/lista_medico`, `/convenio` e `/exame` (todas vazias na conta de teste) e registrar só a estrutura em `docs/xano-formatos.md`.
- [x] 1.3 Confirmar com o produto: Exames como catálogo, status Ativo/Inativo, tipo e especialidade em texto livre, busca pela API e paginação no app, token em todos os POST.

## 2. Base compartilhada

- [x] 2.1 Criar `cadastros.py` com o mixin `CadastroState` (carregar, buscar, paginar, abrir/fechar modal, salvar), tratamento de `SessionExpired` via `AuthState.sessao_expirada` e mensagens de erro em português.
- [x] 2.2 Criar os formatadores e validadores (CPF, telefone, data, número, percentual, valor) e a extração tolerante da lista.
- [x] 2.3 Criar os componentes comuns: layout da tela, busca com debounce, botão "+ Novo", corpo da lista com carregando/erro/vazia, paginação e modal com "Cancelar"/"Salvar".

## 3. Telas

- [x] 3.1 Pacientes: lista de `/paciente`, colunas Nome, CPF, Telefone, Data de nascimento (sem Email), botão "+ Novo Paciente" e modal (nome, CPF com máscara, data de nascimento, telefone).
- [x] 3.2 Médicos: lista de `/lista_medico`, status de `Status`/`status` ("—" quando vazio), modal (nome, CRM, especialidade) com POST em `/medico`.
- [x] 3.3 Convênio: lista de `/convenio`, colunas Nome, Código, Desconto (%), modal (nome, código, desconto 0–100).
- [x] 3.4 Exames: "Catálogo de Exames" com subtítulo, colunas Nome do exame, Tipo, Valor de repasse (R$), Status (badge Ativo/Inativo), modal (nome, tipo, valor, status com padrão Ativo).
- [x] 3.5 Remover os dados mockados das quatro telas.

## 4. Specs

- [x] 4.1 Escrever os deltas de `pacientes`, `medicos`, `convenio` e `exames`.
- [x] 4.2 Rodar `openspec validate integrar-cadastros-xano --strict`.

## 5. Validação

- [x] 5.1 `reflex compile --dry` e `reflex run --env prod` sem erros.
- [x] 5.2 Testar os estados com servidor Xano simulado (sem tocar na API real): listas e normalização tolerante, busca via `busca` voltando à página 1, lista vazia, 400/500/formato inesperado, 401 e `null` → sessão expirada, validações sem chamada à API, payloads e token dos quatro POST, sucesso (fecha, limpa, toast, recarrega) e erros (duplicado, 4xx, 5xx, 401) sem fechar o modal.
- [ ] 5.3 Testar no navegador com a API real: cadastrar um registro em cada tela pelo app, conferir a exibição, a busca, a paginação, o toast e a ausência de rolagem horizontal; ajustar a normalização se algum campo vier vazio.
