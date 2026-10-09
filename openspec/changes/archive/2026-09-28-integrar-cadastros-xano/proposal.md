## Why

As telas Pacientes, Médicos, Convênio e Exames ainda exibem dados mockados, e os botões "+ Novo ..." não fazem nada. A autenticação com o Xano já está integrada, e a API expõe listagem e cadastro desses recursos (Swagger de 2026-09-28, registrado em `docs/xano-formatos.md`). Esta change liga as quatro telas à API para listar e incluir registros reais.

## What Changes

- As quatro telas carregam a lista da API ao abrir, com Bearer token: `GET /paciente`, `/lista_medico`, `/convenio` e `/exame`. Mostram estado de carregando, erro amigável com "Tentar novamente" e lista vazia ("Nenhum paciente cadastrado" etc.).
- A busca usa o filtro `busca` da API; a paginação continua no app (5 por página).
- O botão "+ Novo ..." abre um modal com os campos do POST, botões "Cancelar" e "Salvar" (com carregando) e validação local. Em sucesso, fecha, mostra "Cadastrado com sucesso" e recarrega a lista; em erro, mostra mensagem em português sem fechar. Todos os POST levam o token, inclusive `/convenio`.
- **Pacientes**: novo botão "+ Novo Paciente"; colunas Nome, CPF, Telefone, Data de nascimento. **BREAKING** (visual): a coluna Email sai.
- **Médicos**: colunas mantidas (Nome, Especialidade, CRM, Status), com o status lido de `Status` ou `status`.
- **Convênio**: colunas Nome, Código, Desconto (%). **BREAKING** (visual): saem Registro ANS, Cobertura, Pacientes vinculados e Status.
- **Exames**: a tela passa a ser o catálogo de exames da clínica (título "Catálogo de Exames"), com colunas Nome do exame, Tipo, Valor de repasse (R$), Status (badge Ativo/Inativo). **BREAKING** (visual): saem Paciente, Médico Solicitante e Data, que a API não possui.
- Os dados mockados dessas quatro telas são removidos.
- Em 401 ou resposta `null`, a sessão é encerrada por `AuthState.sessao_expirada`.

## Capabilities

### New Capabilities
<!-- nenhuma -->

### Modified Capabilities
- `pacientes`: lista vinda da API, busca pela API, colunas sem Email, estados de lista e cadastro de paciente.
- `medicos`: lista vinda da API, busca pela API, status tolerante, estados de lista e cadastro de médico (o botão deixa de ser apenas visual).
- `convenio`: lista vinda da API, colunas Nome/Código/Desconto, estados de lista e cadastro de convênio.
- `exames`: tela vira catálogo de exames, com novas colunas, badge Ativo/Inativo, estados de lista e cadastro de exame.

## Impact

- Código: novo `ProjetoCl_nicaCardiologia/cadastros.py` (estado base `CadastroState`, formatação, validação e componentes compartilhados); `patients.py`, `medicos.py`, `convenio.py` e `exames.py` reescritos sobre ele. `api.py`, `auth.py`, rotas, Login, Início e Agendamentos não mudam.
- API: `GET` e `POST` em `/paciente`, `/convenio`, `/exame`; `GET /lista_medico` e `POST /medico`. Nenhum PUT, PATCH ou DELETE.
- Sem novas dependências.
