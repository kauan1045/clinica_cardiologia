# Formatos da API do Xano

Estrutura das respostas da API (`XANO_API_URL`), conferida em 2026-10-07. Registra apenas nomes de campos e tipos, nunca valores. O painel e a agenda usam as rotas de leitura do grupo Clinica; as rotas de cadastro continuam descritas a partir do Swagger.

## Autenticação

### `POST /auth/login`

Corpo enviado (JSON). A senha vai na chave `senha`, e não em `password`: com `password` a API responde `403`.

```json
{ "email": "<string>", "senha": "<string>" }
```

Resposta `200`:

| Campo | Tipo | Observação |
|---|---|---|
| `authToken` | string | JWT; o app lê esta chave |
| `token` | string | mesmo valor de `authToken` |
| `user` | objeto | perfil do usuário (o app aproveita e não chama `/auth/me`) |
| `user.id` | int | |
| `user.name` | string | |
| `user.email` | string | |
| `user.role` | string | |
| `user.medico` | null na conta de teste | provável vínculo com o cadastro de médico |

### `GET /auth/me` (Bearer)

Resposta `200`, objeto: `id` (int), `name` (string), `email` (string), `role` (string). Não traz `medico` nem `created_at`.

## Leitura (todas com Bearer)

### `GET /dashboard` → `200`, objeto

Filtros obrigatórios enviados pelo Dashboard (timestamp em milissegundos): `data_inicio` e `data_fim`. O padrão visual é o primeiro dia do mês até a data atual; o administrador pode escolher qualquer intervalo. Todos os totais devem usar esse mesmo intervalo.

| Campo | Tipo |
|---|---|
| `total_consultas` | int |
| `total_exames` | int |
| `total_laudos_enviados` | int | Total de documentos clínicos cujo envio de e-mail foi confirmado pelo SendGrid. |
| `repasse_exames_periodo` | number | Valor em reais somado do repasse dos exames agendados no intervalo. |
| `faturamento_periodo` | int | Soma de `Agendamento.valor_pago`, em centavos. |
| `novos_pacientes` | int |
| `faturamento_por_convenio` | lista (vazia na conta de teste) |

`faturamento_periodo` e os totais dentro de `faturamento_por_convenio` somam `Agendamento.valor_pago`, que é armazenado em centavos. O front-end deve dividir por 100 antes de exibir em reais. `total_consultas`, `total_exames`, `novos_pacientes`, `total_laudos_enviados`, `repasse_exames_periodo` e o faturamento por convênio devem considerar o intervalo recebido. `total_exames` é uma contagem de agendamentos com exame e não representa o valor do catálogo. A agenda de próximos atendimentos segue filtrada apenas para hoje.

`pagamentos_pendentes` deve trazer até 100 agendamentos não cancelados com `status_pagamento` pendente no período. Cada item inclui paciente, `data_hora`, `forma_pagamento`, nome do convênio, status do pagamento e `valor_pago` em centavos (valor já pago/registrado, não saldo devido). `total_pagamentos_pendentes` é a contagem desse conjunto. A tela mostra essa lista apenas ao administrador; a lista também entra no CSV.

Cada item de `faturamento_por_convenio` precisa trazer o nome do convênio (`convenio`, `nome` ou `convenio_nome`) e o total em centavos (`faturamento`, `valor` ou `total`). O Xano deve agrupar os agendamentos pelo `Agendamento.convenio_id`, somar `Agendamento.valor_pago` e relacionar o nome em `Convenio`. Se a lista trouxer apenas os nomes, o front-end não tem dados para calcular ou inferir os valores.

`GET /dashboard` conta somente prescrições com `prescricao.email_enviado_em` dentro do período. `POST /prescricoes` apenas grava o documento e deixa essa coluna sem valor; a rota separada de envio preenche `email_enviado_em` somente depois que a função do SendGrid retorna sem erro. Prescrições existentes permanecem sem data de envio e não são contadas retroativamente.

### `GET /agendamento` (Bearer)

Rota privada de listagem. Retorna os agendamentos encontrados, com nomes legíveis para paciente e médico. Filtros aceitos por query:

| Campo | Tipo |
|---|---|
| `busca` | text |
| `paciente_id` | int |
| `medico_id` | int |
| `especialidade` | text |
| `exame_id` | int |
| `convenio_id` | int |
| `status` | text |
| `status_pagamento` | text |
| `forma_pagamento` | text |
| `data_inicio` | timestamp |
| `data_fim` | timestamp |
| `page` | int |
| `per_page` | int |

O endpoint restringe automaticamente os resultados de uma conta com perfil médico ao médico vinculado ao usuário autenticado. A tela envia o período selecionado, a busca textual e `page`/`per_page` (50 registros por página) para carregar lotes sem transferir o período inteiro de uma vez.

A resposta deve incluir o nome do paciente (ou a relação `paciente` com `nome`). Se vier somente `paciente_id`, a agenda tenta resolver o nome com `GET /paciente`, uma vez por sessão da tela; o perfil precisa ter permissão de leitura nessa rota.

### `POST /agendamento` (Bearer)

Cadastro de agendamento. `data_hora` (timestamp em milissegundos), `paciente_id` (int) e `medico_id` (int) são obrigatórios. Os demais campos opcionais são `status`, `valor_pago` (int em centavos efetivamente pagos), `forma_pagamento`, `status_pagamento`, `resultado`, `exame_id`, `convenio_id`, `valor_paciente` e `valor_convenio` (valores de responsabilidade em centavos). O front-end identifica o convênio pelos três últimos dígitos de `Paciente.numero_carteirinha`, calcula o valor coberto como `Exame.valor_do_exame_por_repasse * Convenio.desconto / 100` e atribui o saldo ao paciente. `valor_pago` permanece independente, pois registra pagamento feito, não saldo devido. O endpoint exige autenticação e o fluxo do Xano verifica perfil de administrador ou secretaria. Ao cadastrar, o próprio endpoint tenta enviar a confirmação ao paciente por e-mail.

A tela também pré-valida a sobreposição de horários do médico usando `Exame.duracao_minutos`; consultas sem exame usam 30 minutos. O `POST /agendamento` deve repetir essa validação no Xano para evitar conflitos causados por duas criações simultâneas.

### `DELETE /agendamento/{agendamento_id}` (Bearer)

Rota existente no grupo de API do Xano. A agenda pede confirmação e só permite a chamada para administrador/secretaria. A resposta de sucesso deve ser JSON não nulo para o cliente reconhecer a sessão como válida.

### Recuperação de senha

A rota disponível está no grupo Auth Quick Start e usa uma base separada (`XANO_PASSWORD_RESET_API_URL`): `GET /reset/request-reset-link?email=<endereço>`. Ela solicita o envio do link de redefinição. O Xano precisa ter o envio de e-mail configurado; o fluxo existente direciona o link para a página de demonstração do Quick Start.

### Cadastros (Swagger de 2026-09-28)

Fonte: Swagger do grupo de API (`XANO_API_URL` com `apispec:` no lugar de `api:` e `?type=json`). As listas `GET /paciente`, `/lista_medico`, `/convenio` e `/exame` responderam `200` com lista vazia na conta de teste; os campos abaixo vêm do Swagger.

#### Pacientes

| Método | Rota | Token | Entrada |
|---|---|---|---|
| GET | `/paciente` | sim | query `busca` (filtra por nome) |
| POST | `/paciente` | sim | Swagger atual: `nome`*, `cpf`*, `data_nascimento`* (date), `telefone`; adicionar `numero_carteirinha` (text, opcional) |
| GET | `/paciente/{paciente_id}` | sim | path `paciente_id` |
| PUT | `/paciente/{paciente_id}` | sim | `nome`, `cpf`, `data_nascimento`, `telefone`, `numero_carteirinha` (text, opcional) |

O Swagger consultado não expõe `DELETE /paciente/{paciente_id}`. A interface já tenta essa rota quando o usuário confirma a remoção; para efetivar a ação, crie-a no Xano com autenticação e autorização para administrador/secretaria. Recomenda-se bloquear a exclusão enquanto existirem agendamentos ou prescrições vinculados.

Item: `id` (int), `nome`, `email` (string), `cpf`, `data_nascimento` (date `AAAA-MM-DD`, pode ser null), `telefone`, `numero_carteirinha` (text, opcional), `created_at` (timestamp em ms).

A tela local agora exige e envia `email` no cadastro do paciente. O campo existe na resposta do registro, mas o Swagger atual não o expõe como entrada: adicione `email` à entrada de `POST /paciente` e grave-o na tabela para que o endereço fique disponível na prescrição.

O campo `numero_carteirinha` precisa ser adicionado à tabela Paciente e às entradas de `POST /paciente` e `PUT /paciente/{paciente_id}`. Ele deve ser texto para preservar zeros à esquerda. O app aceita vazio ou exatamente 17 dígitos; a exibição separa os 14 primeiros dos três últimos. Os três finais devem corresponder ao `Convenio.codigo` (código de três dígitos, incluindo zeros à esquerda). O `GET /paciente` deve devolver esse campo.

O schema de paciente não precisa de `convenio_id`: o código dos três dígitos finais da carteirinha é associado ao registro de Convênio. Para gravar a divisão financeira do exame, adicionar `valor_paciente` e `valor_convenio` (inteiros em centavos) ao schema e às entradas/respostas de Agendamento. O Xano deve validar os vínculos e recalcular os valores com os dados atuais de Exame e Convênio; não confiar nos valores recebidos pelo front-end. Essa alteração no contrato precisa ser publicada no Xano para persistir carteirinhas e divisões de valores.

Em 2026-10-07, a regra no Xano foi atualizada para autorizar o perfil Médico somente nas rotas de leitura `GET /paciente` e `GET /paciente/{paciente_id}`. `POST /paciente` e `PUT /paciente/{paciente_id}` mantêm suas regras anteriores de acesso restrito. O grupo não possui endpoint `DELETE /paciente`; a tela continua chamando `DELETE /paciente/{paciente_id}`, então o Xano precisa publicar essa rota com autenticação e permissão de administrador/secretaria.

#### Médicos

| Método | Rota | Token | Entrada |
|---|---|---|---|
| GET | `/lista_medico` | sim | query `especialidade`, `status`, `busca` |
| GET | `/medico` | sim | query `crm` (um médico) |
| POST | `/medico` | sim | `nome`*, `crm`*, `especialidade` |
| PATCH | `/medico` | sim | `medico_id`, `nome`, `crm`, `especialidade`, `Status` |

Item: `id`, `nome`, `crm`, `especialidade`, `Status` (string, S maiúsculo), além de campos herdados de outra tabela: `status`, `data_hora` (timestamp, null), `valor_pago` (int), `forma_pagamento`, `status_pagamento`, `resultado`, `user_id` (int).

A tela de Médicos usa `PATCH /medico` com `medico_id` e `Status` (`Ativo`/`Inativo`) para alternar a disponibilidade. O acesso à ação é restrito ao perfil administrador.

#### Convênio

| Método | Rota | Token | Entrada |
|---|---|---|---|
| GET | `/convenio` | sim | query `busca` |
| POST | `/convenio` | **não** | `nome`, `codigo`, `desconto` (number); nenhum obrigatório |
| PATCH | `/convenio` | sim | `convenio_id` (string), `nome`, `codigo`, `desconto` |
| DELETE | `/convenio` | sim | `convenio_id` (int) no corpo |

Item: `id` (int), `created_at` (timestamp), `nome`, `codigo`, `desconto` (number).

#### Exames

| Método | Rota | Token | Entrada |
|---|---|---|---|
| GET | `/exame` | sim | query `busca`, `status`, `tipo_exame` (ordem alfabética); retorna duração e prazo do resultado |
| POST | `/exame` | sim | `nome_do_exame`, `valor_do_exame_por_repasse` (number), `tipo_exame`, `status`, `duracao_minutos` (int), `prazo_resultado_dias` (int) |
| PUT | `/exame/{exame_id}` | sim | campos atuais do POST |

Item observado no Swagger: `id` (int), `nome_do_exame`, `valor_do_exame_por_repasse` (number), `tipo_exame`, `status`, `created_at` (timestamp). Não há `paciente_id`, `medico_id` nem data do exame: é um catálogo de exames, não uma solicitação por paciente. O Swagger não define valores fixos (enum) para `status` e `tipo_exame`.

Em 2026-10-09, foram criadas na tabela Xano `Exame` as colunas inteiras opcionais `duracao_minutos` e `prazo_resultado_dias`, preservando os exames existentes com `null`. `POST /exame` e `PUT /exame/{exame_id}` recebem e salvam os dois campos; o endpoint de listagem retorna a tabela completa. A relação de agenda continua vinculada por `Agendamento.exame_id`, sem alterar registros existentes.

A tela permite editar o exame e o status usando `PUT /exame/{exame_id}`. A duração alimenta a validação de sobreposição da agenda; o prazo de resultado é exibido no catálogo.

`*` obrigatório no Swagger.

#### Prescrições

| Método | Rota | Token | Entrada |
|---|---|---|---|
| POST | `/prescricoes` | sim | `paciente_id` (int), `medico_id` (int), `agendamento_id` (int), `tipo_doc` (text), `conteudo_doc` (text) |
| GET | `/prescricoes` | sim | `paciente_id` (int, opcional), `medico_id` (int, opcional), demais filtros e paginação; lista documentos |
| GET | `/prescricoes/{prescricao_id}` | sim | `prescricao_id` no path |
| POST | `/prescricoes/{prescricao_id}/enviar-email` | sim | `prescricao_id` no path; secretaria/administrador |

Em 2026-10-09, `POST /prescricoes` foi publicado para somente gravar a prescrição e responder com o registro criado; uma falha do SendGrid não deve cancelar nem fazer o cliente tratar o salvamento como falho. A rota `POST /prescricoes/{prescricao_id}/enviar-email` (#4093842) foi criada como privada e autenticada para administrador/secretaria. A mensagem usa o e-mail do paciente, inclui a prescrição, o médico, resultado e valor do exame; `email_enviado_em` só é preenchido depois da confirmação do SendGrid.

Em 2026-10-09, `GET /prescricoes` foi publicado com `paciente_id` declarado como inteiro opcional e filtro condicional direto em `$db.prescricao.paciente_id`. Com o parâmetro omitido, secretaria/administrador consultam a lista clínica; para médicos, o endpoint deve sempre limitar os resultados ao vínculo médico autenticado. A resposta inclui joins de paciente, médico, agendamento e exame com nome/e-mail, resultado, valor do exame, valor pago e status do pagamento.

O Xano já tinha `paciente_id` declarado como inteiro opcional e o filtro XanoScript comparava `prescricao.paciente_id`; a validação anterior apontava erro na execução, apesar da declaração. Revise a coluna tipada no schema da tabela e o stack para preservar a comparação opcional como número inteiro.

### Endpoints que exigem parâmetros (`400 ERROR_CODE_INPUT_ERROR`)

| Endpoint | `message` do Xano | Leitura |
|---|---|---|
| `GET /medico` sem `crm` | `Missing param: field_value` | busca de um médico por CRM; a listagem é `/lista_medico` |
| `GET /prescricoes` | Corrigido em 2026-10-09: `ParseError: Invalid value for param:"prescricao.paciente_id"` | Publicada entrada `int? paciente_id?` com filtro condicional na coluna `prescricao.paciente_id`. Se a API voltar a rejeitar o filtro, verifique a relação da coluna no schema e o token/perfil da chamada. |

## Comportamentos gerais

- Erros de input vêm como `{"code", "message"}` (às vezes com `payload`), com status `400`.
- Sem token, os endpoints protegidos respondem `200` com corpo `null` (levantamento anterior); o app trata `null` com token como sessão inválida.
