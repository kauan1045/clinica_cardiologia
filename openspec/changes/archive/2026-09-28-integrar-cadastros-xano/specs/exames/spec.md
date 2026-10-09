## ADDED Requirements

### Requirement: Carregar o catálogo de exames da API
A tela Exames SHALL carregar o catálogo de exames da clínica de `GET /exame` na API do Xano, com o token da sessão, ao ser aberta, exibindo estados de carregando, erro e lista vazia no lugar das linhas da tabela.

#### Scenario: Lista carregada
- **WHEN** a tela Exames é aberta por um usuário autenticado
- **THEN** a tabela mostra "Carregando..." enquanto aguarda a API
- **AND** em seguida exibe os exames devolvidos, com a paginação abaixo

#### Scenario: Nenhum exame cadastrado
- **WHEN** a API devolve uma lista vazia e não há termo de busca
- **THEN** a tabela exibe "Nenhum exame cadastrado"

#### Scenario: Falha ao carregar
- **WHEN** a API responde com erro, não responde a tempo ou não é alcançada
- **THEN** a tabela exibe uma mensagem amigável em português e o botão "Tentar novamente"

#### Scenario: Sessão inválida
- **WHEN** a API responde 401 ou corpo `null`
- **THEN** a sessão é encerrada e o usuário volta ao Login com "Sessão expirada. Entre novamente."

### Requirement: Cadastrar exame no catálogo
O botão "+ Novo Exame" SHALL abrir um modal com os campos Nome do exame, Tipo (texto livre), Valor de repasse (R$) e Status (select com "Ativo" e "Inativo", padrão "Ativo") e os botões "Cancelar" e "Salvar", enviando o cadastro para `POST /exame` com o token da sessão, sem campos de paciente ou médico.

#### Scenario: Abrir e cancelar
- **WHEN** o usuário clica em "+ Novo Exame"
- **THEN** o modal "Novo Exame" abre com o formulário vazio e o status "Ativo"
- **WHEN** o usuário clica em "Cancelar"
- **THEN** o modal fecha sem chamar a API

#### Scenario: Validação local
- **WHEN** o usuário clica em "Salvar" sem nome, tipo ou valor, ou com valor não numérico ou negativo
- **THEN** o modal exibe a mensagem correspondente em português e permanece aberto, sem chamar a API

#### Scenario: Cadastro bem-sucedido
- **WHEN** os dados são válidos e a API confirma o cadastro
- **THEN** o botão "Salvar" mostra carregando durante o envio
- **AND** são enviados `nome_do_exame`, `tipo_exame`, `valor_do_exame_por_repasse` como número (aceitando `1.234,50`) e `status` ("Ativo" ou "Inativo")
- **AND** o modal fecha, aparece "Cadastrado com sucesso" e a lista é recarregada

#### Scenario: Erro no cadastro
- **WHEN** a API recusa o cadastro ou falha
- **THEN** o modal permanece aberto com os dados digitados e exibe uma mensagem em português

### Requirement: Sinalizar status do catálogo de exames com badge
O status de cada exame SHALL ser exibido em um badge (pílula) próprio da tela Exames, com o mesmo formato do badge de status compartilhado, cuja cor muda conforme o valor (Ativo ou Inativo), sem alterar os badges das demais telas.

#### Scenario: Exame está ativo
- **WHEN** o status do exame é "Ativo" (sem diferenciar maiúsculas)
- **THEN** o badge exibe "Ativo" com fundo verde-menta translúcido (`#88E0C1` a 30%) e cantos totalmente arredondados, com texto em azul `#05589F`

#### Scenario: Exame está inativo
- **WHEN** o status do exame é "Inativo"
- **THEN** o badge exibe "Inativo" com fundo neutro (cinza) translúcido, visualmente distinto do usado para "Ativo"

#### Scenario: Exame sem status
- **WHEN** o exame não tem status
- **THEN** a coluna Status exibe "—" sem badge


### Requirement: Buscar no catálogo de exames
A busca da tela Exames SHALL consultar a API com o filtro `busca` e exibir a lista devolvida.

#### Scenario: Usuário busca por um exame
- **WHEN** o usuário digita um termo no campo "Buscar exame"
- **THEN** após uma breve pausa na digitação, a lista é recarregada de `GET /exame` com o parâmetro `busca`
- **AND** a paginação volta para a primeira página

#### Scenario: Nenhum exame corresponde à busca
- **WHEN** a API devolve uma lista vazia para o termo digitado
- **THEN** a tabela exibe "Nenhum exame encontrado para a busca" e a paginação não é exibida


## MODIFIED Requirements

### Requirement: Exibir cabeçalho com busca e botão de novo exame
A tela Exames SHALL exibir o título "Catálogo de Exames", o subtítulo "Exames oferecidos pela clínica e valores de repasse.", um campo de busca com placeholder "Buscar exame" e o botão "+ Novo Exame", que abre o modal de cadastro.

#### Scenario: Usuário visualiza o cabeçalho
- **WHEN** a tela Exames é carregada
- **THEN** o usuário vê o título "Catálogo de Exames" com o mesmo estilo do título da tela Pacientes, seguido do subtítulo
- **AND** vê, abaixo da busca global do Topbar, um campo de busca com placeholder "Buscar exame"
- **AND** vê o botão "+ Novo Exame", com a mesma aparência dos botões "+ Novo Médico" e "+ Novo Convênio", à direita do campo de busca

#### Scenario: Usuário interage com "+ Novo Exame"
- **WHEN** o usuário passa o mouse sobre o botão "+ Novo Exame"
- **THEN** o cursor vira pointer e o fundo do botão escurece levemente
- **WHEN** o usuário clica no botão
- **THEN** o modal "Novo Exame" é aberto

### Requirement: Listar exames em tabela
A tela Exames SHALL exibir uma tabela com os exames do catálogo vindos da API, mostrando nas colunas Nome do exame, Tipo, Valor de repasse (R$) e Status, nessa ordem, com o cabeçalho no mesmo estilo do cabeçalho da tabela de Pacientes.

#### Scenario: Usuário consulta a lista de exames
- **WHEN** existem exames cadastrados
- **THEN** cada linha exibe o nome do exame, o tipo, o valor de repasse no formato brasileiro (por exemplo, "1.234,50") e o status
- **AND** as colunas aparecem na ordem Nome do exame, Tipo, Valor de repasse (R$), Status, sem Paciente, Médico Solicitante ou Data
- **AND** a separação entre linhas é feita por espaçamento, sem linhas divisórias pesadas

#### Scenario: Campos com nomes diferentes ou ausentes
- **WHEN** um exame vem sem algum campo ou com nome alternativo (por exemplo, `nome` em vez de `nome_do_exame`)
- **THEN** a linha é exibida com os campos disponíveis, sem quebrar a tela

### Requirement: Paginar a lista de exames
A tabela de exames SHALL oferecer paginação no mesmo padrão da tela Pacientes, Médicos e Convênio, com navegação por setas anterior/próxima e por números de página derivados dos dados, dentro do card, sempre que houver exames na lista.

#### Scenario: Usuário visualiza a paginação
- **WHEN** a lista devolvida pela API tem ao menos um item
- **THEN** o usuário vê a paginação abaixo da tabela, com a seta anterior, os números das páginas derivados da quantidade de exames (5 por página) e a seta próxima
- **AND** a página atual aparece destacada com borda azul `#05589F`

#### Scenario: Lista carregando, com erro ou vazia
- **WHEN** a lista está carregando, falhou ou está vazia
- **THEN** a paginação não é exibida

#### Scenario: Usuário está na primeira ou última página
- **WHEN** o usuário está na primeira página
- **THEN** a seta "anterior" fica desabilitada
- **WHEN** o usuário está na última página
- **THEN** a seta "próxima" fica desabilitada

## REMOVED Requirements

### Requirement: Usar dados mockados substituíveis
**Reason**: O catálogo de exames passa a vir da API do Xano.
**Migration**: Coberto por "Carregar o catálogo de exames da API"; os dados mockados foram removidos.

### Requirement: Sinalizar status do exame com badge colorido
**Reason**: Os status de exame solicitado (Pendente, Concluído, Cancelado) não existem no catálogo da API.
**Migration**: Substituído por "Sinalizar status do catálogo de exames com badge" (Ativo/Inativo).

### Requirement: Buscar exames
**Reason**: A busca por paciente não se aplica ao catálogo, e o filtro passa a ser feito pela API.
**Migration**: Substituído por "Buscar no catálogo de exames".
