## MODIFIED Requirements

### Requirement: Listar pacientes em tabela
A tela Pacientes SHALL exibir uma tabela com os pacientes cadastrados, mostrando nas colunas Nome, CPF, Telefone e Email, nessa ordem, sem coluna de status.

#### Scenario: Usuário consulta a lista de pacientes
- **WHEN** existem pacientes cadastrados
- **THEN** cada linha da tabela exibe o nome, o CPF, o telefone e o email do paciente
- **AND** as colunas aparecem na ordem Nome, CPF, Telefone, Email
- **AND** a tabela não exibe coluna nem badge de status
- **AND** a separação entre linhas é feita por espaçamento generoso, sem linhas divisórias pesadas

### Requirement: Buscar pacientes
A busca própria da tela Pacientes SHALL filtrar a lista de pacientes exibida conforme o termo digitado.

#### Scenario: Usuário busca por um paciente
- **WHEN** o usuário digita um termo no campo "Buscar paciente"
- **THEN** a tabela passa a exibir apenas os pacientes cujo nome, CPF, telefone ou email correspondem ao termo digitado
- **AND** a paginação volta para a primeira página do resultado filtrado

### Requirement: Usar dados mockados substituíveis
Os dados de pacientes exibidos SHALL vir de uma lista mockada mantida separada da composição visual, com campos compatíveis com uma futura fonte de dados real.

#### Scenario: Fonte de pacientes é substituída
- **WHEN** a equipe conectar uma API ou banco de dados futuramente
- **THEN** a origem dos pacientes pode ser substituída sem alterar o contrato visual da tabela
- **AND** os campos de nome, CPF, telefone e email continuam disponíveis para a tela

## REMOVED Requirements

### Requirement: Sinalizar status do paciente com badge colorido
**Reason**: A tela Pacientes deixa de exibir o status ativo/inativo; o campo saiu do mock e da tabela.
**Migration**: Nenhuma. O componente `patient_status_badge` permanece em `patients.py` apenas porque as telas Médicos e Convênio o reutilizam.
