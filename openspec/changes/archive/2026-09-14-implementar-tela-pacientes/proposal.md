## Why

A clínica precisa consultar rapidamente quem está cadastrado no CardioVida. As telas de Login e Dashboard já existem, mas ainda não há nenhuma listagem de pacientes; esta change adiciona a tela Pacientes reaproveitando a navegação já estabelecida pelo Dashboard.

## What Changes

- Criar a tela Pacientes com cabeçalho "Pacientes", busca própria (placeholder "Buscar paciente") e tabela com Nome, CPF, Telefone e Status.
- Reaproveitar os componentes `Sidebar` e `Topbar` já existentes do Dashboard, sem duplicar código, destacando o item "Pacientes" como ativo no menu.
- Generalizar o componente `Sidebar` para aceitar qual item está ativo (antes fixo em "Início"), e apontar o link "Pacientes" do menu para a nova rota `/pacientes`.
- Implementar badge de status ("ativo"/"inativo") com cor conforme o valor, verde-menta translúcido para ativo.
- Implementar paginação (setas anterior/próxima + números de página, página atual destacada com borda azul `#05589F`).
- Usar uma lista mockada de pacientes (nome, CPF, telefone, status), estruturada para ser substituída por uma chamada real ao back-end depois.

## Capabilities

### New Capabilities
- `pacientes`: Listagem de pacientes cadastrados na clínica, com busca e paginação, reaproveitando a navegação compartilhada do Dashboard.

### Modified Capabilities
- `dashboard-inicio`: o componente `Sidebar` passa a aceitar qual item do menu está ativo (em vez de sempre destacar "Início"), para ser reutilizado por outras telas autenticadas.

## Impact

- Afeta `ProjetoCl_nicaCardiologia/dashboard.py` (generalização do `Sidebar`) e `ProjetoCl_nicaCardiologia/ProjetoCl_nicaCardiologia.py` (nova rota `/pacientes`).
- Adiciona `ProjetoCl_nicaCardiologia/patients.py` com a tela, o estado de busca/paginação e os dados mockados.
- Não adiciona dependências externas, banco de dados ou APIs; cadastro/edição e perfil detalhado do paciente ficam fora de escopo.
