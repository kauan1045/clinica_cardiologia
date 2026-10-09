## MODIFIED Requirements

### Requirement: Disponibilizar barra superior reutilizável
O Dashboard SHALL exibir uma barra superior com busca, notificações e acesso ao perfil, e o controle de perfil SHALL exibir o nome do usuário autenticado.

#### Scenario: Usuário visualiza a barra superior
- **WHEN** o Dashboard é carregado
- **THEN** a barra superior exibe o campo com placeholder "Buscar paciente, médico ou convênio..."
- **AND** exibe um controle de notificações e um controle de perfil
- **AND** os controles têm nomes acessíveis e não dependem apenas de ícones para comunicar sua função

#### Scenario: Controle de perfil mostra o usuário autenticado
- **WHEN** uma tela autenticada é exibida
- **THEN** o controle de perfil exibe o nome (`name`) do usuário autenticado, ou o email quando não houver nome
- **AND** exibe "Usuário" se o perfil ainda não estiver disponível

### Requirement: Encerrar a sessão pelo botão Sair
O botão "Sair" do menu lateral SHALL apagar o token de autenticação e o perfil do usuário, limpar o estado de login e redirecionar o usuário para a tela de Login, com a lógica isolada em um único evento de estado.

#### Scenario: Usuário clica em Sair
- **WHEN** o usuário clica no botão "Sair" em qualquer tela autenticada
- **THEN** o token, o perfil e o estado de login (usuário, senha, opção "lembrar-me" e mensagem de erro) são apagados
- **AND** o usuário é redirecionado para a tela de Login
- **AND** os campos da tela de Login aparecem vazios
