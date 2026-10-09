## ADDED Requirements

### Requirement: Carregar convênios da API
A tela Convênio SHALL carregar a lista de convênios de `GET /convenio` na API do Xano, com o token da sessão, ao ser aberta, exibindo estados de carregando, erro e lista vazia no lugar das linhas da tabela.

#### Scenario: Lista carregada
- **WHEN** a tela Convênio é aberta por um usuário autenticado
- **THEN** a tabela mostra "Carregando..." enquanto aguarda a API
- **AND** em seguida exibe os convênios devolvidos, com a paginação abaixo

#### Scenario: Nenhum convênio cadastrado
- **WHEN** a API devolve uma lista vazia e não há termo de busca
- **THEN** a tabela exibe "Nenhum convênio cadastrado"

#### Scenario: Falha ao carregar
- **WHEN** a API responde com erro, não responde a tempo ou não é alcançada
- **THEN** a tabela exibe uma mensagem amigável em português e o botão "Tentar novamente"

#### Scenario: Sessão inválida
- **WHEN** a API responde 401 ou corpo `null`
- **THEN** a sessão é encerrada e o usuário volta ao Login com "Sessão expirada. Entre novamente."

### Requirement: Cadastrar convênio
O botão "+ Novo Convênio" SHALL abrir um modal com os campos Nome, Código e Desconto (%) e os botões "Cancelar" e "Salvar", enviando o cadastro para `POST /convenio` com o token da sessão.

#### Scenario: Abrir e cancelar
- **WHEN** o usuário clica em "+ Novo Convênio"
- **THEN** o modal "Novo Convênio" abre com o formulário vazio
- **WHEN** o usuário clica em "Cancelar"
- **THEN** o modal fecha sem chamar a API

#### Scenario: Validação local
- **WHEN** o usuário clica em "Salvar" sem nome, código ou desconto, ou com desconto não numérico ou fora do intervalo de 0 a 100
- **THEN** o modal exibe a mensagem correspondente em português e permanece aberto, sem chamar a API

#### Scenario: Cadastro bem-sucedido
- **WHEN** os dados são válidos e a API confirma o cadastro
- **THEN** o botão "Salvar" mostra carregando durante o envio
- **AND** são enviados `nome`, `codigo` e `desconto` como número (aceitando vírgula decimal)
- **AND** o modal fecha, aparece "Cadastrado com sucesso" e a lista é recarregada

#### Scenario: Erro no cadastro
- **WHEN** a API recusa o cadastro ou falha
- **THEN** o modal permanece aberto com os dados digitados e exibe uma mensagem em português

## MODIFIED Requirements

### Requirement: Exibir cabeçalho com busca e botão de novo convênio
A tela Convênio SHALL exibir o título "Convênio", um campo de busca com placeholder "Buscar Convênio" e o botão "+ Novo Convênio", que abre o modal de cadastro.

#### Scenario: Usuário visualiza o cabeçalho
- **WHEN** a tela Convênio é carregada
- **THEN** o usuário vê o título "Convênio" com o mesmo estilo do título da tela Pacientes
- **AND** vê, abaixo da busca global do Topbar, um campo de busca com placeholder "Buscar Convênio"
- **AND** vê o botão "+ Novo Convênio", com a mesma aparência do botão "+ Novo Médico", à direita do campo de busca

#### Scenario: Usuário interage com "+ Novo Convênio"
- **WHEN** o usuário passa o mouse sobre o botão "+ Novo Convênio"
- **THEN** o cursor vira pointer e o fundo do botão escurece levemente
- **WHEN** o usuário clica no botão
- **THEN** o modal "Novo Convênio" é aberto

### Requirement: Listar convênios em tabela
A tela Convênio SHALL exibir uma tabela com os convênios vindos da API, mostrando nas colunas Nome, Código e Desconto, nessa ordem, com o cabeçalho no mesmo estilo do cabeçalho da tabela de Pacientes.

#### Scenario: Usuário consulta a lista de convênios
- **WHEN** existem convênios cadastrados
- **THEN** cada linha exibe o nome, o código e o desconto do convênio
- **AND** o desconto aparece em percentual (por exemplo, "10%" ou "12,5%")
- **AND** o código preserva os zeros à esquerda
- **AND** as colunas aparecem na ordem Nome, Código, Desconto, sem Registro ANS, Cobertura, Pacientes vinculados ou Status
- **AND** a separação entre linhas é feita por espaçamento, sem linhas divisórias pesadas

### Requirement: Buscar convênios
A busca da tela Convênio SHALL consultar a API com o filtro `busca` e exibir a lista devolvida.

#### Scenario: Usuário busca por um convênio
- **WHEN** o usuário digita um termo no campo "Buscar Convênio"
- **THEN** após uma breve pausa na digitação, a lista é recarregada de `GET /convenio` com o parâmetro `busca`
- **AND** a paginação volta para a primeira página

#### Scenario: Nenhum convênio corresponde à busca
- **WHEN** a API devolve uma lista vazia para o termo digitado
- **THEN** a tabela exibe "Nenhum convênio encontrado para a busca" e a paginação não é exibida

### Requirement: Paginar a lista de convênios
A tabela de convênios SHALL oferecer paginação no mesmo padrão da tela Pacientes e Médicos, com navegação por setas anterior/próxima e por números de página derivados dos dados, dentro do card, sempre que houver convênios na lista.

#### Scenario: Usuário visualiza a paginação
- **WHEN** a lista devolvida pela API tem ao menos um item
- **THEN** o usuário vê a paginação abaixo da tabela, com a seta anterior, os números das páginas derivados da quantidade de convênios (5 por página) e a seta próxima
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

### Requirement: Sinalizar status do convênio com badge colorido
**Reason**: A API de convênios não tem campo de status.
**Migration**: A coluna Status foi removida da tabela de convênios.

### Requirement: Usar dados mockados substituíveis
**Reason**: A lista de convênios passa a vir da API do Xano.
**Migration**: Coberto por "Carregar convênios da API"; os dados mockados foram removidos.
