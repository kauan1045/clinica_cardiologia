## MODIFIED Requirements

### Requirement: Disponibilizar navegação lateral reutilizável
O Dashboard SHALL exibir um menu lateral com os itens Início, Pacientes, Agendamentos, Médicos, Convênio, Exames e Configurações, reutilizável por outras telas autenticadas, cada uma podendo indicar qual item está ativo.

#### Scenario: Usuário acessa o Dashboard
- **WHEN** a tela inicial autenticada é exibida
- **THEN** o usuário vê todos os itens de navegação lateral com seus respectivos nomes e ícones
- **AND** o item Início aparece visualmente destacado como ativo
- **AND** os demais itens permanecem disponíveis como destinos de navegação, incluindo os itens Pacientes, Agendamentos, Médicos, Convênio e Exames que já apontam para as telas implementadas

#### Scenario: Outra tela autenticada reutiliza o menu lateral
- **WHEN** uma tela diferente do Dashboard reutiliza o componente de navegação lateral
- **THEN** o item correspondente àquela tela aparece visualmente destacado como ativo
- **AND** o item Início deixa de aparecer destacado
