## ADDED Requirements

### Requirement: Reaproveitar navegação e layout compartilhados
A tela Exames SHALL reaproveitar os componentes `Sidebar` e `Topbar` do Dashboard, sem duplicar código, destacando o item "Exames" como ativo no menu lateral, e SHALL usar o mesmo layout de página das telas Pacientes, Médicos e Convênio (fundo, largura máxima de conteúdo, card branco e estilo de título).

#### Scenario: Usuário acessa a tela Exames
- **WHEN** a tela Exames é exibida
- **THEN** o usuário vê a mesma barra superior e o mesmo menu lateral do Dashboard e das demais telas
- **AND** o item "Exames" aparece visualmente destacado como ativo
- **AND** a tabela aparece em um card branco sobre o mesmo fundo usado em Pacientes

### Requirement: Exibir cabeçalho com busca e botão de novo exame
A tela Exames SHALL exibir o título "Exames", um campo de busca com placeholder "Buscar paciente ou exame" e o botão "+ Novo Exame", que é apenas visual e não executa ação.

#### Scenario: Usuário visualiza o cabeçalho
- **WHEN** a tela Exames é carregada
- **THEN** o usuário vê o título "Exames" com o mesmo estilo do título da tela Pacientes
- **AND** vê, abaixo da busca global do Topbar, um campo de busca com placeholder "Buscar paciente ou exame"
- **AND** vê o botão "+ Novo Exame", com a mesma aparência dos botões "+ Novo Médico" e "+ Novo Convênio", à direita do campo de busca

#### Scenario: Usuário interage com "+ Novo Exame"
- **WHEN** o usuário passa o mouse sobre o botão "+ Novo Exame"
- **THEN** o cursor vira pointer e o fundo do botão escurece levemente
- **WHEN** o usuário clica no botão
- **THEN** nenhuma ação é executada e a tela permanece a mesma

### Requirement: Listar exames em tabela
A tela Exames SHALL exibir uma tabela com os exames, mostrando nas colunas Paciente, Tipo de Exame, Médico Solicitante, Data e Status, nessa ordem, com o cabeçalho no mesmo estilo do cabeçalho da tabela de Pacientes.

#### Scenario: Usuário consulta a lista de exames
- **WHEN** existem exames cadastrados
- **THEN** o usuário vê "Beatriz Souza", "Ecocardiograma", "Dr. Felipe Costa", "26/09/2026" e status "Pendente"
- **AND** vê "João Pedro Alves", "Teste Ergométrico", "Dra. Juliana Almeida", "10/09/2026" e status "Concluído"
- **AND** vê "Helena Ribeiro", "Holter 24h", "Dr. Marcelo Cavalcante", "10/09/2026" e status "Concluído"
- **AND** vê "Carlos Mota", "Eletrocardiograma", "Dra. Juliana Almeida", "10/09/2026" e status "Pendente"
- **AND** vê "Luana Vitória Souza", "MAPA 24h", "Dr. Felipe Costa", "10/09/2026" e status "Cancelado"
- **AND** as colunas aparecem na ordem Paciente, Tipo de Exame, Médico Solicitante, Data, Status
- **AND** a separação entre linhas é feita por espaçamento, sem linhas divisórias pesadas

### Requirement: Sinalizar status do exame com badge colorido
O status de cada exame SHALL ser exibido em um badge (pílula) próprio da tela Exames, com o mesmo formato do badge da tela Pacientes, cuja cor muda conforme o valor (Pendente, Concluído ou Cancelado), sem alterar os badges das demais telas.

#### Scenario: Exame está pendente
- **WHEN** o status do exame é "Pendente"
- **THEN** o badge exibe fundo amarelo-limão translúcido (`#DCED6D` a 30%) e cantos totalmente arredondados, com texto em azul `#05589F`

#### Scenario: Exame está concluído
- **WHEN** o status do exame é "Concluído"
- **THEN** o badge exibe fundo verde-menta translúcido (`#88E0C1` a 30%) e cantos totalmente arredondados, com texto em azul `#05589F`

#### Scenario: Exame está cancelado
- **WHEN** o status do exame é "Cancelado"
- **THEN** o badge exibe fundo vermelho translúcido (`#ED6D6D` a 30%) e cantos totalmente arredondados, com texto em azul `#05589F`

### Requirement: Buscar exames
A busca da tela Exames SHALL filtrar a lista de exames exibida conforme o termo digitado, considerando o paciente e o tipo de exame.

#### Scenario: Usuário busca por paciente ou tipo de exame
- **WHEN** o usuário digita um termo no campo "Buscar paciente ou exame"
- **THEN** a tabela passa a exibir apenas os exames cujo paciente ou tipo de exame correspondem ao termo digitado
- **AND** a paginação volta para a primeira página do resultado filtrado

#### Scenario: Nenhum exame corresponde à busca
- **WHEN** o termo digitado não corresponde a nenhum exame
- **THEN** a tabela não exibe linhas e a paginação mostra uma única página

### Requirement: Paginar a lista de exames
A tabela de exames SHALL oferecer paginação no mesmo padrão das telas Pacientes, Médicos e Convênio, com navegação por setas anterior/próxima e por números de página derivados dos dados, dentro do card.

#### Scenario: Usuário visualiza a paginação
- **WHEN** a tela Exames é carregada
- **THEN** o usuário vê a paginação abaixo da tabela, com a seta anterior, os números das páginas derivados da quantidade de exames e a seta próxima
- **AND** a página atual aparece destacada com borda azul `#05589F`

#### Scenario: Usuário está na primeira ou última página
- **WHEN** o usuário está na primeira página
- **THEN** a seta "anterior" fica desabilitada
- **WHEN** o usuário está na última página
- **THEN** a seta "próxima" fica desabilitada

### Requirement: Seguir a escala e a largura das telas existentes
Os tamanhos de texto, espaçamentos e componentes da tela Exames SHALL seguir a escala das telas Dashboard, Pacientes, Médicos e Convênio, e o conteúdo SHALL ocupar a largura disponível até o mesmo máximo usado em Pacientes, sem rolagem horizontal.

#### Scenario: Usuário abre a tela em larguras comuns de monitor
- **WHEN** a largura da janela é 1280px, 1366px ou 1920px
- **THEN** não há rolagem horizontal
- **AND** o conteúdo ocupa a mesma largura máxima da tela Pacientes

#### Scenario: Usuário reduz a largura da janela
- **WHEN** a janela fica mais estreita que a largura máxima do conteúdo
- **THEN** o conteúdo encolhe junto com a janela
- **AND** nenhum texto ou componente do conteúdo é cortado

### Requirement: Usar dados mockados substituíveis
Os dados de exames exibidos SHALL vir de dados mockados mantidos separados da composição visual, carregados por função isolada, com campos compatíveis com uma futura fonte de dados real.

#### Scenario: Fonte de exames é substituída
- **WHEN** a equipe conectar uma API ou banco de dados futuramente
- **THEN** a origem dos exames pode ser substituída sem alterar o contrato visual da tabela
- **AND** os campos de paciente, tipo de exame, médico solicitante, data e status continuam disponíveis para a tela
