## ADDED Requirements

### Requirement: Reaproveitar navegação e layout compartilhados
A tela Convênio SHALL reaproveitar os componentes `Sidebar` e `Topbar` do Dashboard, sem duplicar código, destacando o item "Convênio" como ativo no menu lateral, e SHALL usar o mesmo layout de página das telas Pacientes e Médicos (fundo, largura máxima de conteúdo, card branco e estilo de título).

#### Scenario: Usuário acessa a tela Convênio
- **WHEN** a tela Convênio é exibida
- **THEN** o usuário vê a mesma barra superior e o mesmo menu lateral do Dashboard, de Pacientes e de Médicos
- **AND** o item "Convênio" aparece visualmente destacado como ativo
- **AND** a tabela aparece em um card branco sobre o mesmo fundo usado em Pacientes

### Requirement: Exibir cabeçalho com busca e botão de novo convênio
A tela Convênio SHALL exibir o título "Convênio", um campo de busca com placeholder "Buscar Convênio" e o botão "+ Novo Convênio", que é apenas visual e não executa ação.

#### Scenario: Usuário visualiza o cabeçalho
- **WHEN** a tela Convênio é carregada
- **THEN** o usuário vê o título "Convênio" com o mesmo estilo do título da tela Pacientes
- **AND** vê, abaixo da busca global do Topbar, um campo de busca com placeholder "Buscar Convênio"
- **AND** vê o botão "+ Novo Convênio", com a mesma aparência do botão "+ Novo Médico", à direita do campo de busca

#### Scenario: Usuário interage com "+ Novo Convênio"
- **WHEN** o usuário passa o mouse sobre o botão "+ Novo Convênio"
- **THEN** o cursor vira pointer e o fundo do botão escurece levemente
- **WHEN** o usuário clica no botão
- **THEN** nenhuma ação é executada e a tela permanece a mesma

### Requirement: Listar convênios em tabela
A tela Convênio SHALL exibir uma tabela com os convênios, mostrando nas colunas Nome, Registro ANS, Cobertura, Pacientes vinculados e Status, nessa ordem, com o cabeçalho no mesmo estilo do cabeçalho da tabela de Pacientes.

#### Scenario: Usuário consulta a lista de convênios
- **WHEN** existem convênios cadastrados
- **THEN** o usuário vê "Amil Saúde", "326305", "Consultas e Exames", "200" e status "ativo"
- **AND** vê "Bradesco Saúde", "418862", "Consultas, Exames e Cirurgias", "184" e status "ativo"
- **AND** vê "SulAmérica", "006246", "Consultas e Exames", "97" e status "ativo"
- **AND** vê "Unimed Nacional", "359661", "Consultas, Exames e Cirurgias", "300" e status "ativo"
- **AND** vê "Porto Seguro Saúde", "033286", "Consultas e Exames", "15" e status "inativo"
- **AND** as colunas aparecem na ordem Nome, Registro ANS, Cobertura, Pacientes vinculados, Status
- **AND** o registro ANS preserva os zeros à esquerda
- **AND** a separação entre linhas é feita por espaçamento, sem linhas divisórias pesadas

### Requirement: Sinalizar status do convênio com badge colorido
O status de cada convênio SHALL ser exibido com o mesmo badge (pílula) usado na tela Pacientes, cuja cor muda conforme o valor.

#### Scenario: Convênio está ativo
- **WHEN** o status do convênio é "ativo"
- **THEN** o badge exibe fundo verde-menta translúcido e cantos totalmente arredondados, com texto em azul `#05589F`

#### Scenario: Convênio está inativo
- **WHEN** o status do convênio é "inativo"
- **THEN** o badge exibe o mesmo estilo neutro (cinza) usado para "inativo" na tela Pacientes

### Requirement: Buscar convênios
A busca da tela Convênio SHALL filtrar a lista de convênios exibida conforme o termo digitado.

#### Scenario: Usuário busca por um convênio
- **WHEN** o usuário digita um termo no campo "Buscar Convênio"
- **THEN** a tabela passa a exibir apenas os convênios cujo nome, registro ANS ou cobertura correspondem ao termo digitado
- **AND** a paginação volta para a primeira página do resultado filtrado

#### Scenario: Nenhum convênio corresponde à busca
- **WHEN** o termo digitado não corresponde a nenhum convênio
- **THEN** a tabela não exibe linhas e a paginação mostra uma única página

### Requirement: Paginar a lista de convênios
A tabela de convênios SHALL oferecer paginação no mesmo padrão das telas Pacientes e Médicos, com navegação por setas anterior/próxima e por números de página derivados dos dados, dentro do card.

#### Scenario: Usuário visualiza a paginação
- **WHEN** a tela Convênio é carregada
- **THEN** o usuário vê a paginação abaixo da tabela, com a seta anterior, os números das páginas derivados da quantidade de convênios e a seta próxima
- **AND** a página atual aparece destacada com borda azul `#05589F`

#### Scenario: Usuário está na primeira ou última página
- **WHEN** o usuário está na primeira página
- **THEN** a seta "anterior" fica desabilitada
- **WHEN** o usuário está na última página
- **THEN** a seta "próxima" fica desabilitada

### Requirement: Seguir a escala e a largura das telas existentes
Os tamanhos de texto, espaçamentos e componentes da tela Convênio SHALL seguir a escala das telas Dashboard, Pacientes e Médicos, e o conteúdo SHALL ocupar a largura disponível até o mesmo máximo usado em Pacientes, sem rolagem horizontal.

#### Scenario: Usuário abre a tela em larguras comuns de monitor
- **WHEN** a largura da janela é 1280px, 1366px ou 1920px
- **THEN** não há rolagem horizontal
- **AND** o conteúdo ocupa a mesma largura máxima da tela Pacientes

#### Scenario: Usuário reduz a largura da janela
- **WHEN** a janela fica mais estreita que a largura máxima do conteúdo
- **THEN** o conteúdo encolhe junto com a janela
- **AND** nenhum texto ou componente do conteúdo é cortado

### Requirement: Usar dados mockados substituíveis
Os dados de convênios exibidos SHALL vir de dados mockados mantidos separados da composição visual, carregados por função isolada, com campos compatíveis com uma futura fonte de dados real.

#### Scenario: Fonte de convênios é substituída
- **WHEN** a equipe conectar uma API ou banco de dados futuramente
- **THEN** a origem dos convênios pode ser substituída sem alterar o contrato visual da tabela
- **AND** os campos de nome, registro ANS, cobertura, pacientes vinculados e status continuam disponíveis para a tela
