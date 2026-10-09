## Purpose

A capability Médicos permite à equipe da clínica consultar, buscar e navegar pela lista de médicos, reaproveitando a navegação e o layout das demais telas autenticadas.

## ADDED Requirements

### Requirement: Reaproveitar navegação e layout compartilhados
A tela Médicos SHALL reaproveitar os componentes `Sidebar` e `Topbar` do Dashboard, sem duplicar código, destacando o item "Médicos" como ativo no menu lateral, e SHALL usar o mesmo layout de página da tela Pacientes (fundo, largura máxima de conteúdo, card branco e estilo de título).

#### Scenario: Usuário acessa a tela Médicos
- **WHEN** a tela Médicos é exibida
- **THEN** o usuário vê a mesma barra superior e o mesmo menu lateral do Dashboard e de Pacientes
- **AND** o item "Médicos" aparece visualmente destacado como ativo
- **AND** a tabela aparece em um card branco sobre o mesmo fundo usado em Pacientes

### Requirement: Exibir cabeçalho com busca e botão de novo médico
A tela Médicos SHALL exibir o título "Médicos", um campo de busca com placeholder "Buscar Médico" e o botão "+ Novo Médico", que é apenas visual e não executa ação.

#### Scenario: Usuário visualiza o cabeçalho
- **WHEN** a tela Médicos é carregada
- **THEN** o usuário vê o título "Médicos" com o mesmo estilo do título da tela Pacientes
- **AND** vê, abaixo da busca global do Topbar, um campo de busca com placeholder "Buscar Médico"
- **AND** vê o botão "+ Novo Médico" em formato de pílula, à direita do campo de busca

#### Scenario: Usuário interage com "+ Novo Médico"
- **WHEN** o usuário passa o mouse sobre o botão "+ Novo Médico"
- **THEN** o cursor vira pointer e o fundo do botão escurece levemente
- **WHEN** o usuário clica no botão
- **THEN** nenhuma ação é executada e a tela permanece a mesma

### Requirement: Listar médicos em tabela
A tela Médicos SHALL exibir uma tabela com os médicos, mostrando nas colunas Nome, Especialidade, CRM e Status, nessa ordem.

#### Scenario: Usuário consulta a lista de médicos
- **WHEN** existem médicos cadastrados
- **THEN** o usuário vê "Dr. Felipe Costa", "Ecocardiografia", "12345SP" e status "ativo"
- **AND** vê "Dra. Juliana Almeida", "Cardiologista", "67890SP" e status "ativo"
- **AND** vê "Dr. Marcelo Cavalcante", "Cardiologista", "00098SP" e status "ativo"
- **AND** as colunas aparecem na ordem Nome, Especialidade, CRM, Status
- **AND** a separação entre linhas é feita por espaçamento, sem linhas divisórias pesadas

### Requirement: Sinalizar status do médico com badge colorido
O status de cada médico SHALL ser exibido com o mesmo badge (pílula) usado na tela Pacientes, cuja cor muda conforme o valor.

#### Scenario: Médico está ativo
- **WHEN** o status do médico é "ativo"
- **THEN** o badge exibe fundo verde-menta translúcido e cantos totalmente arredondados, com texto em azul `#05589F`

### Requirement: Buscar médicos
A busca da tela Médicos SHALL filtrar a lista de médicos exibida conforme o termo digitado.

#### Scenario: Usuário busca por um médico
- **WHEN** o usuário digita um termo no campo "Buscar Médico"
- **THEN** a tabela passa a exibir apenas os médicos cujo nome, especialidade ou CRM correspondem ao termo digitado
- **AND** a paginação volta para a primeira página do resultado filtrado

### Requirement: Paginar a lista de médicos
A tabela de médicos SHALL oferecer paginação no mesmo padrão da tela Pacientes, com navegação por setas anterior/próxima e por números de página, dentro do card.

#### Scenario: Usuário visualiza a paginação
- **WHEN** a tela Médicos é carregada
- **THEN** o usuário vê a paginação abaixo da tabela, com a seta anterior, os números das páginas e a seta próxima
- **AND** a página atual aparece destacada com borda azul `#05589F`

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

### Requirement: Usar dados mockados substituíveis
Os dados de médicos exibidos SHALL vir de dados mockados mantidos separados da composição visual, carregados por função isolada, com campos compatíveis com uma futura fonte de dados real.

#### Scenario: Fonte de médicos é substituída
- **WHEN** a equipe conectar uma API ou banco de dados futuramente
- **THEN** a origem dos médicos pode ser substituída sem alterar o contrato visual da tabela
- **AND** os campos de nome, especialidade, CRM e status continuam disponíveis para a tela
