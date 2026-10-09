## Context

A autenticação com o Xano já existe: `api.request(method, path, token=..., json=..., params=...)` trata erros e sinaliza `SessionExpired` em 401 ou corpo `null` com token, e `AuthState.token` guarda o JWT. As telas Pacientes, Médicos, Convênio e Exames usam listas mockadas com busca e paginação locais; os botões "+ Novo ..." não têm ação. Pelo Swagger (ver `docs/xano-formatos.md`):

| Tela | Lista | Cadastro | Campos do item |
|---|---|---|---|
| Pacientes | `GET /paciente?busca=` | `POST /paciente`: `nome`*, `cpf`*, `data_nascimento`* (date), `telefone` | `id`, `nome`, `email`, `cpf`, `data_nascimento`, `telefone`, `created_at` |
| Médicos | `GET /lista_medico?busca=` | `POST /medico`: `nome`*, `crm`*, `especialidade` | `id`, `nome`, `crm`, `especialidade`, `Status`, e campos soltos de outra tabela (`status`, `valor_pago`...) |
| Convênio | `GET /convenio?busca=` | `POST /convenio`: `nome`, `codigo`, `desconto` (number) | `id`, `nome`, `codigo`, `desconto`, `created_at` |
| Exames | `GET /exame?busca=` | `POST /exame`: `nome_do_exame`, `valor_do_exame_por_repasse` (number), `tipo_exame`, `status` | `id`, `nome_do_exame`, `valor_do_exame_por_repasse`, `tipo_exame`, `status`, `created_at` |

Todas as listas estavam vazias na conta de teste; o formato real dos itens ainda não foi observado.

## Goals / Non-Goals

**Goals:**
- Listar e incluir registros reais nas quatro telas, mantendo visual e escala atuais.
- Código tolerante a variações de nomes de campo, já que as listas ainda estão vazias.
- Uma base comum para não repetir estado, paginação, estados de lista e modal em quatro arquivos.

**Non-Goals:**
- Editar ou excluir registros (PUT/PATCH/DELETE), filtros além de `busca`, paginação no servidor.
- Vincular exames a pacientes e médicos (a API não tem esses campos).
- Mudar Agendamentos, Início, Login, `api.py` ou `auth.py`.

## Decisions

### Base comum (`cadastros.py`)
- `CadastroState` é um mixin de estado do Reflex (`rx.State, mixin=True`) com `itens`, `search`, `page`, `carregando`, `erro_lista`, `modal_aberto`, `salvando` e `erro_form`; os eventos `carregar_dados`, `set_search`, paginação, `abrir_modal`, `fechar_modal`, `alterar_modal` e `salvar`; e as computed vars `total_pages`, `page_numbers`, `pagina_itens` e `mensagem_vazia`. Cada tela herda (`class PatientsState(CadastroState, rx.State)`) e define `ENDPOINT`, `LIST_ENDPOINT` (Médicos lista em `/lista_medico` e cadastra em `/medico`), textos e os métodos `_normalizar`, `_validar` e `_limpar_formulario`.
- Componentes compartilhados: `tela_cadastro` (o mesmo layout das telas atuais), `campo_busca`, `botao_novo` (o mesmo estilo de "+ Novo Médico"), `corpo_lista`, `paginacao`, `modal_cadastro`, `campo_input`, `campo_select` e `cabecalho_coluna`. As funções de paginação e de botão, antes repetidas em cada tela, passam a existir uma vez só.
- Alternativa descartada: manter o estado em cada arquivo. Quadruplicaria carregamento, tratamento de erro e modal.

### Carregamento e sessão
- A lista carrega no `on_mount` da página. Como `require_auth` só renderiza a página depois de `verificar_sessao` confirmar a sessão, o token já está validado quando a busca dispara. Rotas e `on_load` não mudam.
- O token vem de `(await self.get_state(AuthState)).token`. `SessionExpired`, que cobre 401 e `null`, dispara `AuthState.sessao_expirada`. Os demais `ApiError` viram mensagem em português. As mensagens do Xano (em inglês) nunca aparecem cruas: um 4xx vira "Não foi possível ... Verifique os dados e tente novamente.", e um erro de duplicidade vira "Já existe um cadastro com esses dados.". 5xx, timeout e falha de conexão usam as mensagens do `api.py`.
- A resposta é aceita como lista ou como objeto com `items`, `itens`, `data`, `result` ou `results`. Qualquer outro formato mostra "Resposta inesperada do servidor.".

### Busca e paginação
- `set_search` envia `busca` à API (apenas quando preenchido) e volta à página 1. O input já é debounced pelo Reflex (`debounce_timeout=400`). Os eventos de um mesmo estado são processados em ordem, então não há resposta fora de ordem.
- A paginação é local, com 5 itens por página, sobre a lista devolvida.

### Normalização tolerante
- Cada tela converte o item da API num dicionário de strings já formatadas para exibição, com nomes alternativos de campo (`nome`/`name`, `telefone`/`phone`, `Status`/`status`, `nome_do_exame`/`nome` etc.). Campo ausente vira texto vazio. Status vazio aparece como "—", sem badge.
- Formatos: CPF `000.000.000-00` (se tiver 11 dígitos), telefone `(00) 00000-0000`, data `DD/MM/AAAA` (a partir de `AAAA-MM-DD`, ISO ou timestamp em ms), desconto `10%`/`12,5%` e valor `1.234,50`.
- Médicos: o status vem de `Status` e, se faltar, de `status`, em minúsculas, para reaproveitar `patient_status_badge` ("ativo" verde, demais neutro). O POST de médico não aceita status, então o médico recém-cadastrado aparece com "—" até o status ser definido no Xano.

### Formulários e envio
- Campos controlados pelo estado com setters explícitos (o Reflex 0.9 não gera setters automáticos). O modal usa `rx.form` para que Enter também envie. "Cancelar", fechar pelo X ou pelo Esc são ignorados enquanto salva.
- Validação e payload:
  - **Paciente**: nome, CPF e data de nascimento obrigatórios; CPF com máscara progressiva e 11 dígitos; data em `type="date"`, válida, entre 1900 e hoje; telefone opcional, com 10 ou 11 dígitos se preenchido. CPF e telefone são enviados só com dígitos.
  - **Médico**: nome e CRM obrigatórios; especialidade em texto livre, enviada só se preenchida.
  - **Convênio**: nome, código e desconto obrigatórios (a API não obriga nenhum, mas um convênio sem eles não é útil); desconto numérico de 0 a 100, aceitando vírgula.
  - **Exame**: nome, tipo (texto livre) e valor de repasse obrigatórios; valor numérico ≥ 0 no formato brasileiro (`1.234,50`) ou com ponto; status em select Ativo/Inativo, com padrão Ativo, enviado como "Ativo"/"Inativo".
- Todo POST envia o Bearer token, inclusive `/convenio`, que no Swagger não exige.
- Sucesso: fecha o modal, limpa o formulário, mostra o toast "Cadastrado com sucesso" (o toaster já vem no app) e recarrega a lista. Erro: mantém o modal e os dados digitados e mostra a mensagem acima dos botões.

### Exames como catálogo
A API trata exame como catálogo (nome, tipo, valor de repasse, status), sem paciente, médico ou data. Por decisão do produto, a tela passa a ser "Catálogo de Exames", com o subtítulo "Exames oferecidos pela clínica e valores de repasse." e a busca "Buscar exame". O badge de exame passa a usar Ativo (verde-menta) e Inativo (neutro).

## Risks / Trade-offs

- [Risk] O formato real dos itens pode diferir do Swagger (listas vazias até agora). → Mitigation: normalização com nomes alternativos; ajustar depois dos primeiros cadastros feitos pelo app.
- [Risk] Um POST bem-sucedido cuja resposta não é JSON aparece como erro, embora o registro possa ter sido criado. → Mitigation: pouco provável no Xano (devolve o objeto criado); a lista recarregada mostra o estado real.
- [Risk] A busca de pacientes na API filtra só por nome, e não mais por CPF ou telefone. → Mitigation: comportamento definido pela API; documentado na spec.
- [Risk] Os campos soltos em `/lista_medico` (`status`, `valor_pago`...) indicam um problema no endpoint do Xano. → Mitigation: `Status` tem prioridade; o restante é ignorado.
- [Trade-off] A paginação local carrega a lista inteira a cada busca; é aceitável para o volume de uma clínica.
