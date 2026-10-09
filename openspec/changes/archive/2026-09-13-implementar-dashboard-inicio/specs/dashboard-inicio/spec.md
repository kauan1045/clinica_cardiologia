## Purpose

O Dashboard de Início oferece à equipe da clínica uma visão operacional rápida do dia e estabelece a navegação compartilhada para as demais áreas do CardioVida.

## ADDED Requirements

### Requirement: Disponibilizar navegação lateral reutilizável
O Dashboard SHALL exibir um menu lateral com os itens Início, Pacientes, Agendamentos, Médicos, Convênio, Exames e Configurações, preparado para ser reutilizado pelas próximas telas.

#### Scenario: Usuário acessa o Dashboard
- **WHEN** a tela inicial autenticada é exibida
- **THEN** o usuário vê todos os itens de navegação lateral com seus respectivos nomes e ícones
- **AND** o item Início aparece visualmente destacado como ativo
- **AND** os demais itens permanecem disponíveis como destinos de navegação futuros, sem indicar que suas telas foram implementadas nesta change

### Requirement: Disponibilizar barra superior reutilizável
O Dashboard SHALL exibir uma barra superior com busca, notificações e acesso ao perfil.

#### Scenario: Usuário visualiza a barra superior
- **WHEN** o Dashboard é carregado
- **THEN** a barra superior exibe o campo com placeholder "Buscar paciente, médico ou convênio..."
- **AND** exibe um controle de notificações e um controle de perfil
- **AND** os controles têm nomes acessíveis e não dependem apenas de ícones para comunicar sua função

### Requirement: Exibir resumo do dia
O Dashboard SHALL exibir uma saudação ao usuário, um texto de resumo, a data atual por extenso e o indicador "Total de pacientes hoje".

#### Scenario: Usuário abre o resumo diário
- **WHEN** a tela é carregada
- **THEN** o usuário vê uma saudação no formato "Olá, {nome do usuário}"
- **AND** vê o texto "Aqui está um resumo do que acontece hoje na clínica"
- **AND** vê a data atual em português por extenso, incluindo dia da semana, dia, mês e ano
- **AND** vê o total mockado de pacientes do dia e a variação em relação ao dia anterior

### Requirement: Listar próximos atendimentos ordenados
O Dashboard SHALL exibir a seção "Próximos atendimentos" com atendimentos mockados ordenados pelo horário.

#### Scenario: Usuário consulta os próximos atendimentos
- **WHEN** existem atendimentos mockados para o dia
- **THEN** cada item exibe horário, nome do paciente e médico responsável
- **AND** cada item exibe o status "confirmado" ou "aguardando"
- **AND** os itens aparecem em ordem crescente de horário
- **AND** a seção exibe o link "Ver Todos" apontando para a área de Agendamentos

### Requirement: Separar dados de apresentação
Os dados mockados do Dashboard SHALL ser mantidos em uma estrutura separada da composição visual, com campos compatíveis com uma futura fonte de dados real.

#### Scenario: Fonte de atendimentos é substituída
- **WHEN** a equipe conectar uma API ou banco de dados futuramente
- **THEN** a origem dos pacientes e atendimentos pode ser substituída sem alterar o contrato visual das seções
- **AND** os campos de horário, paciente, médico e status continuam disponíveis para a tela
