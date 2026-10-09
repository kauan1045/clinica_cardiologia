# pacientes Specification

## Purpose

A capability Pacientes permite à equipe da clínica consultar, buscar e navegar pela lista de pacientes cadastrados, reaproveitando a navegação compartilhada do Dashboard.

## Requirements

### Requirement: Reaproveitar navegação compartilhada
A tela Pacientes SHALL reaproveitar os componentes `Sidebar` e `Topbar` já existentes do Dashboard, sem duplicar código, destacando o item "Pacientes" como ativo no menu lateral.

#### Scenario: Usuário acessa a tela Pacientes
- **WHEN** a tela Pacientes é exibida
- **THEN** o usuário vê a mesma barra superior e o mesmo menu lateral do Dashboard
- **AND** o item "Pacientes" do menu lateral aparece visualmente destacado como ativo
- **AND** os demais itens do menu permanecem disponíveis como antes

### Requirement: Exibir cabeçalho com busca própria
A tela Pacientes SHALL exibir o título "Pacientes", um campo de busca próprio da tela, separado da busca global do Topbar, e o botão "+ Novo Paciente" à direita do campo de busca.

#### Scenario: Usuário visualiza o cabeçalho
- **WHEN** a tela Pacientes é carregada
- **THEN** o usuário vê o título "Pacientes"
- **AND** vê, abaixo da busca global do Topbar, um campo de busca com placeholder "Buscar paciente"
- **AND** vê o botão "+ Novo Paciente" em formato de pílula, com a mesma aparência de "+ Novo Médico"

### Requirement: Listar pacientes em tabela
A tela Pacientes SHALL exibir uma tabela com os pacientes vindos da API, mostrando nas colunas Nome, E-mail, CPF, Telefone e Data de nascimento, nessa ordem, sem coluna de status.

#### Scenario: Usuário consulta a lista de pacientes
- **WHEN** existem pacientes cadastrados
- **THEN** cada linha da tabela exibe o nome, o e-mail, o CPF (`000.000.000-00`), o telefone (`(00) 00000-0000`) e a data de nascimento (`DD/MM/AAAA`) do paciente
- **AND** as colunas aparecem na ordem Nome, E-mail, CPF, Telefone, Data de nascimento
- **AND** a tabela não exibe badge de status
- **AND** a separação entre linhas é feita por espaçamento generoso, sem linhas divisórias pesadas

### Requirement: Buscar pacientes
A busca própria da tela Pacientes SHALL consultar a API com o filtro `busca` e exibir a lista devolvida.

#### Scenario: Usuário busca por um paciente
- **WHEN** o usuário digita um termo no campo "Buscar paciente"
- **THEN** após uma breve pausa na digitação, a lista é recarregada de `GET /paciente` com o parâmetro `busca`, que a API aplica ao nome
- **AND** a paginação volta para a primeira página

#### Scenario: Nenhum paciente corresponde à busca
- **WHEN** a API devolve uma lista vazia para o termo digitado
- **THEN** a tabela exibe "Nenhum paciente encontrado para a busca"

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

### Requirement: Carregar pacientes da API
A tela Pacientes SHALL carregar a lista de pacientes de `GET /paciente` na API do Xano, com o token da sessão, ao ser aberta, exibindo estados de carregando, erro e lista vazia no lugar das linhas da tabela.

#### Scenario: Lista carregada
- **WHEN** a tela Pacientes é aberta por um usuário autenticado
- **THEN** a tabela mostra "Carregando..." enquanto aguarda a API
- **AND** em seguida exibe os pacientes devolvidos, com a paginação abaixo

#### Scenario: Nenhum paciente cadastrado
- **WHEN** a API devolve uma lista vazia e não há termo de busca
- **THEN** a tabela exibe "Nenhum paciente cadastrado"

#### Scenario: Falha ao carregar
- **WHEN** a API responde com erro, não responde a tempo ou não é alcançada
- **THEN** a tabela exibe uma mensagem amigável em português e o botão "Tentar novamente"
- **AND** a mensagem da API em inglês não é exibida

#### Scenario: Sessão inválida
- **WHEN** a API responde 401 ou corpo `null`
- **THEN** a sessão é encerrada e o usuário volta ao Login com "Sessão expirada. Entre novamente."

#### Scenario: Campos com nomes diferentes
- **WHEN** um paciente vem sem algum campo ou com nome alternativo (por exemplo, `name` em vez de `nome`)
- **THEN** a linha é exibida com os campos disponíveis, sem quebrar a tela

### Requirement: Cadastrar paciente
A tela Pacientes SHALL oferecer o botão "+ Novo Paciente", no mesmo estilo de "+ Novo Médico" e à direita da busca, que abre um modal com os campos Nome, E-mail, CPF, Data de nascimento e Telefone e os botões "Cancelar" e "Salvar", enviando o cadastro para `POST /paciente` com o token da sessão.

#### Scenario: Abrir e cancelar
- **WHEN** o usuário clica em "+ Novo Paciente"
- **THEN** o modal "Novo Paciente" abre com o formulário vazio
- **WHEN** o usuário clica em "Cancelar"
- **THEN** o modal fecha sem chamar a API

#### Scenario: Máscara de CPF e telefone
- **WHEN** o usuário digita o CPF ou o telefone
- **THEN** o CPF é formatado como `000.000.000-00` e o telefone como `(00) 00000-0000`

#### Scenario: Validação local
- **WHEN** o usuário clica em "Salvar" sem nome, e-mail, CPF ou data de nascimento, com e-mail inválido, CPF sem 11 dígitos, com data inexistente, futura ou anterior a 1900, ou com telefone preenchido sem 10 ou 11 dígitos
- **THEN** o modal exibe a mensagem correspondente em português e permanece aberto
- **AND** a API não é chamada

#### Scenario: Cadastro bem-sucedido
- **WHEN** os dados são válidos e a API confirma o cadastro
- **THEN** o botão "Salvar" mostra carregando durante o envio
- **AND** são enviados `nome`, `email`, `cpf` (só dígitos), `data_nascimento` (`AAAA-MM-DD`) e, se preenchido, `telefone` (só dígitos)
- **AND** o modal fecha, aparece "Cadastrado com sucesso" e a lista é recarregada

#### Scenario: Erro no cadastro
- **WHEN** a API recusa o cadastro ou falha
- **THEN** o modal permanece aberto com os dados digitados e exibe uma mensagem em português
- **AND** um registro duplicado exibe "Já existe um cadastro com esses dados."
