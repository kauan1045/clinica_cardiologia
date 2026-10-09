## MODIFIED Requirements

### Requirement: Disponibilizar navegação lateral reutilizável
O Dashboard SHALL exibir um menu lateral com os itens Início, Pacientes, Agendamentos, Médicos, Convênio e Exames permitidos ao perfil do usuário, conforme o mapa de permissões, sem o item "Configurações", e um botão "Sair" fixo no rodapé do menu, reutilizável por outras telas autenticadas, cada uma podendo indicar qual item está ativo.

#### Scenario: Usuário acessa o Dashboard
- **WHEN** a tela inicial autenticada é exibida para um usuário Administrador ou secretaria
- **THEN** o usuário vê todos os itens de navegação lateral com seus respectivos nomes e ícones
- **AND** o item Início aparece visualmente destacado como ativo
- **AND** os demais itens permanecem disponíveis como destinos de navegação, incluindo os itens Pacientes, Agendamentos, Médicos, Convênio e Exames que já apontam para as telas implementadas
- **AND** o menu não exibe o item "Configurações"

#### Scenario: Médico visualiza o menu
- **WHEN** um usuário com perfil medico vê o menu lateral
- **THEN** o menu exibe somente o item "Agendamentos" e o botão "Sair"

#### Scenario: Outra tela autenticada reutiliza o menu lateral
- **WHEN** uma tela diferente do Dashboard reutiliza o componente de navegação lateral
- **THEN** o item correspondente àquela tela aparece visualmente destacado como ativo
- **AND** o item Início deixa de aparecer destacado

#### Scenario: Menu lateral permanece fixo ao rolar a página
- **WHEN** o conteúdo da tela é mais alto que a janela e o usuário rola a página
- **THEN** o menu lateral mantém a altura da janela e permanece fixo no topo, sem rolar junto com o conteúdo
- **AND** o botão "Sair" continua visível no rodapé do menu

#### Scenario: Usuário visualiza o botão Sair
- **WHEN** qualquer tela que reutiliza o menu lateral é exibida
- **THEN** o botão "Sair", com ícone de logout, aparece no rodapé do menu lateral, na mesma escala e estilo dos itens do menu
- **AND** ao passar o mouse sobre o botão, o cursor vira pointer e o fundo do botão reage com o mesmo destaque discreto usado nos itens do menu
