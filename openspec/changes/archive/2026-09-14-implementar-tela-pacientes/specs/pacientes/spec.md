## Purpose

A capability Pacientes permite à equipe da clínica consultar, buscar e navegar pela lista de pacientes cadastrados, reaproveitando a navegação compartilhada do Dashboard.

## ADDED Requirements

### Requirement: Reaproveitar navegação compartilhada
A tela Pacientes SHALL reaproveitar os componentes `Sidebar` e `Topbar` já existentes do Dashboard, sem duplicar código, destacando o item "Pacientes" como ativo no menu lateral.

#### Scenario: Usuário acessa a tela Pacientes
- **WHEN** a tela Pacientes é exibida
- **THEN** o usuário vê a mesma barra superior e o mesmo menu lateral do Dashboard
- **AND** o item "Pacientes" do menu lateral aparece visualmente destacado como ativo
- **AND** os demais itens do menu permanecem disponíveis como antes

### Requirement: Exibir cabeçalho com busca própria
A tela Pacientes SHALL exibir o título "Pacientes" e um campo de busca próprio da tela, separado da busca global do Topbar.

#### Scenario: Usuário visualiza o cabeçalho
- **WHEN** a tela Pacientes é carregada
- **THEN** o usuário vê o título "Pacientes"
- **AND** vê, abaixo da busca global do Topbar, um campo de busca com placeholder "Buscar paciente"

### Requirement: Listar pacientes em tabela
A tela Pacientes SHALL exibir uma tabela com os pacientes cadastrados, mostrando nas colunas Nome, CPF, Telefone e Status, nessa ordem.

#### Scenario: Usuário consulta a lista de pacientes
- **WHEN** existem pacientes cadastrados
- **THEN** cada linha da tabela exibe o nome, o CPF, o telefone e o status do paciente
- **AND** as colunas aparecem na ordem Nome, CPF, Telefone, Status
- **AND** a separação entre linhas é feita por espaçamento generoso, sem linhas divisórias pesadas

### Requirement: Sinalizar status do paciente com badge colorido
O status de cada paciente SHALL ser exibido como um badge (pílula) cuja cor muda conforme o valor "ativo" ou "inativo".

#### Scenario: Paciente está ativo
- **WHEN** o status do paciente é "ativo"
- **THEN** o badge exibe fundo verde-menta translúcido e cantos totalmente arredondados

#### Scenario: Paciente está inativo
- **WHEN** o status do paciente é "inativo"
- **THEN** o badge exibe uma cor visualmente distinta da usada para "ativo"

### Requirement: Buscar pacientes
A busca própria da tela Pacientes SHALL filtrar a lista de pacientes exibida conforme o termo digitado.

#### Scenario: Usuário busca por um paciente
- **WHEN** o usuário digita um termo no campo "Buscar paciente"
- **THEN** a tabela passa a exibir apenas os pacientes cujo nome, CPF ou telefone correspondem ao termo digitado
- **AND** a paginação volta para a primeira página do resultado filtrado

### Requirement: Paginar a lista de pacientes
A tabela de pacientes SHALL oferecer paginação com navegação por setas anterior/próxima e por números de página.

#### Scenario: Usuário navega entre páginas
- **WHEN** a lista de pacientes (filtrada ou não) tem mais itens do que cabem em uma página
- **THEN** o usuário pode avançar e retroceder usando as setas de navegação
- **AND** pode saltar diretamente para uma página pelo número correspondente
- **AND** a página atual aparece destacada com borda azul `#05589F`

#### Scenario: Usuário está na primeira ou última página
- **WHEN** o usuário está na primeira página
- **THEN** a seta "anterior" fica desabilitada
- **WHEN** o usuário está na última página
- **THEN** a seta "próxima" fica desabilitada

### Requirement: Usar dados mockados substituíveis
Os dados de pacientes exibidos SHALL vir de uma lista mockada mantida separada da composição visual, com campos compatíveis com uma futura fonte de dados real.

#### Scenario: Fonte de pacientes é substituída
- **WHEN** a equipe conectar uma API ou banco de dados futuramente
- **THEN** a origem dos pacientes pode ser substituída sem alterar o contrato visual da tabela
- **AND** os campos de nome, CPF, telefone e status continuam disponíveis para a tela
