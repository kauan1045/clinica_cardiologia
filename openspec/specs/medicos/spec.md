# medicos Specification

## Purpose
A capability Médicos permite à equipe da clínica consultar, buscar e navegar pela lista de médicos, reaproveitando a navegação e o layout das demais telas autenticadas.

## Requirements

### Requirement: Reaproveitar navegação e layout compartilhados
A tela Médicos SHALL reaproveitar os componentes `Sidebar` e `Topbar` do Dashboard, sem duplicar código, destacando o item "Médicos" como ativo no menu lateral, e SHALL usar o mesmo layout de página da tela Pacientes (fundo, largura máxima de conteúdo, card branco e estilo de título).

#### Scenario: Usuário acessa a tela Médicos
- **WHEN** a tela Médicos é exibida
- **THEN** o usuário vê a mesma barra superior e o mesmo menu lateral do Dashboard e de Pacientes
- **AND** o item "Médicos" aparece visualmente destacado como ativo
- **AND** a tabela aparece em um card branco sobre o mesmo fundo usado em Pacientes

### Requirement: Exibir cabeçalho com busca e botão de novo médico
A tela Médicos SHALL exibir o título "Médicos", um campo de busca com placeholder "Buscar Médico" e o botão "+ Novo Médico", que abre o modal de cadastro.

#### Scenario: Usuário visualiza o cabeçalho
- **WHEN** a tela Médicos é carregada
- **THEN** o usuário vê o título "Médicos" com o mesmo estilo do título da tela Pacientes
- **AND** vê, abaixo da busca global do Topbar, um campo de busca com placeholder "Buscar Médico"
- **AND** vê o botão "+ Novo Médico" em formato de pílula, à direita do campo de busca

#### Scenario: Usuário interage com "+ Novo Médico"
- **WHEN** o usuário passa o mouse sobre o botão "+ Novo Médico"
- **THEN** o cursor vira pointer e o fundo do botão escurece levemente
- **WHEN** o usuário clica no botão
- **THEN** o modal "Novo Médico" é aberto

### Requirement: Listar médicos em tabela
A tela Médicos SHALL exibir uma tabela com os médicos vindos da API, mostrando nas colunas Nome, Especialidade, CRM e Status, nessa ordem.

#### Scenario: Usuário consulta a lista de médicos
- **WHEN** existem médicos cadastrados
- **THEN** cada linha exibe o nome, a especialidade, o CRM e o status do médico
- **AND** as colunas aparecem na ordem Nome, Especialidade, CRM, Status
- **AND** a separação entre linhas é feita por espaçamento, sem linhas divisórias pesadas

#### Scenario: Campos com nomes diferentes ou ausentes
- **WHEN** um médico vem sem algum campo ou com nome alternativo (por exemplo, `name` em vez de `nome`)
- **THEN** a linha é exibida com os campos disponíveis, sem quebrar a tela

### Requirement: Sinalizar status do médico com badge colorido
O status de cada médico SHALL ser lido do campo `Status` da API ou, na falta dele, de `status`, e exibido com o badge de status compartilhado (pílula), cuja cor muda conforme o valor.

#### Scenario: Médico está ativo
- **WHEN** o status do médico é "ativo" (sem diferenciar maiúsculas)
- **THEN** o badge exibe fundo verde-menta translúcido e cantos totalmente arredondados, com texto em azul `#05589F`

#### Scenario: Médico sem status
- **WHEN** o médico não tem status (por exemplo, recém-cadastrado)
- **THEN** a coluna Status exibe "—" sem badge

### Requirement: Buscar médicos
A busca da tela Médicos SHALL consultar a API com o filtro `busca` e exibir a lista devolvida.

#### Scenario: Usuário busca por um médico
- **WHEN** o usuário digita um termo no campo "Buscar Médico"
- **THEN** após uma breve pausa na digitação, a lista é recarregada de `GET /lista_medico` com o parâmetro `busca`
- **AND** a paginação volta para a primeira página

#### Scenario: Nenhum médico corresponde à busca
- **WHEN** a API devolve uma lista vazia para o termo digitado
- **THEN** a tabela exibe "Nenhum médico encontrado para a busca"

### Requirement: Paginar a lista de médicos
A tabela de médicos SHALL oferecer paginação no mesmo padrão da tela Pacientes, com navegação por setas anterior/próxima e por números de página, dentro do card, sempre que houver médicos na lista.

#### Scenario: Usuário visualiza a paginação
- **WHEN** a lista devolvida pela API tem ao menos um item
- **THEN** o usuário vê a paginação abaixo da tabela, com a seta anterior, os números das páginas derivados da quantidade de médicos (5 por página) e a seta próxima
- **AND** a página atual aparece destacada com borda azul `#05589F`

#### Scenario: Lista carregando, com erro ou vazia
- **WHEN** a lista está carregando, falhou ou está vazia
- **THEN** a paginação não é exibida

#### Scenario: Usuário está na primeira ou última página
- **WHEN** o usuário está na primeira página
- **THEN** a seta "anterior" fica desabilitada
- **WHEN** o usuário está na última página
- **THEN** a seta "próxima" fica desabilitada

### Requirement: Seguir a escala e a largura das telas existentes
Os tamanhos de texto, espaçamentos e componentes da tela Médicos SHALL seguir a escala das telas Dashboard e Pacientes, e o conteúdo SHALL ocupar a largura disponível até o mesmo máximo usado em Pacientes, sem rolagem horizontal.

#### Scenario: Usuário abre a tela em larguras comuns de monitor
- **WHEN** a largura da janela é 1280px, 1366px ou 1920px
- **THEN** não há rolagem horizontal
- **AND** o conteúdo ocupa a mesma largura máxima da tela Pacientes

#### Scenario: Usuário reduz a largura da janela
- **WHEN** a janela fica mais estreita que a largura máxima do conteúdo
- **THEN** o conteúdo encolhe junto com a janela
- **AND** nenhum texto ou componente do conteúdo é cortado

### Requirement: Carregar médicos da API
A tela Médicos SHALL carregar a lista de médicos de `GET /lista_medico` na API do Xano, com o token da sessão, ao ser aberta, exibindo estados de carregando, erro e lista vazia no lugar das linhas da tabela.

#### Scenario: Lista carregada
- **WHEN** a tela Médicos é aberta por um usuário autenticado
- **THEN** a tabela mostra "Carregando..." enquanto aguarda a API
- **AND** em seguida exibe os médicos devolvidos, com a paginação abaixo

#### Scenario: Nenhum médico cadastrado
- **WHEN** a API devolve uma lista vazia e não há termo de busca
- **THEN** a tabela exibe "Nenhum médico cadastrado"

#### Scenario: Falha ao carregar
- **WHEN** a API responde com erro, não responde a tempo ou não é alcançada
- **THEN** a tabela exibe uma mensagem amigável em português e o botão "Tentar novamente"

#### Scenario: Sessão inválida
- **WHEN** a API responde 401 ou corpo `null`
- **THEN** a sessão é encerrada e o usuário volta ao Login com "Sessão expirada. Entre novamente."

### Requirement: Cadastrar médico
O botão "+ Novo Médico" SHALL abrir um modal com os campos Nome, CRM e Especialidade (texto livre) e os botões "Cancelar" e "Salvar", enviando o cadastro para `POST /medico` com o token da sessão.

#### Scenario: Abrir e cancelar
- **WHEN** o usuário clica em "+ Novo Médico"
- **THEN** o modal "Novo Médico" abre com o formulário vazio
- **WHEN** o usuário clica em "Cancelar"
- **THEN** o modal fecha sem chamar a API

#### Scenario: Validação local
- **WHEN** o usuário clica em "Salvar" sem nome ou sem CRM
- **THEN** o modal exibe "Preencha nome e CRM." e permanece aberto, sem chamar a API

#### Scenario: Cadastro bem-sucedido
- **WHEN** os dados são válidos e a API confirma o cadastro
- **THEN** o botão "Salvar" mostra carregando durante o envio
- **AND** são enviados `nome`, `crm` e, se preenchida, `especialidade`
- **AND** o modal fecha, aparece "Cadastrado com sucesso" e a lista é recarregada

#### Scenario: Erro no cadastro
- **WHEN** a API recusa o cadastro ou falha
- **THEN** o modal permanece aberto com os dados digitados e exibe uma mensagem em português
