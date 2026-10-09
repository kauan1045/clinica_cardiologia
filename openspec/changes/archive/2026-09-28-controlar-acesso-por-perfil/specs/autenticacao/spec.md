## ADDED Requirements

### Requirement: Controlar o acesso por perfil
A aplicação SHALL definir, num único mapa de permissões, as rotas permitidas, a tela inicial e as ações de cada perfil (Administrador, secretaria e medico), comparando o `role` do usuário sem diferenciar maiúsculas, minúsculas e acentos. O mesmo mapa SHALL ser usado pelo menu lateral, pela proteção das páginas e pelas verificações de ação.

#### Scenario: Administrador ou secretaria
- **WHEN** o usuário tem perfil Administrador ou secretaria
- **THEN** pode abrir Início, Pacientes, Agendamentos, Médicos, Convênio e Exames, como antes

#### Scenario: Médico abre tela não permitida
- **WHEN** um usuário com perfil medico abre Início, Pacientes, Médicos, Convênio ou Exames, pela URL ou por link
- **THEN** é redirecionado para Agendamentos sem ver o conteúdo da tela solicitada

#### Scenario: Médico com sessão ativa abre o Login
- **WHEN** um usuário com perfil medico e sessão válida abre `/`
- **THEN** é redirecionado para Agendamentos

#### Scenario: Perfil com maiúsculas ou acento
- **WHEN** o `role` vem como "ADMINISTRADOR", "Secretaria" ou "Médico"
- **THEN** é reconhecido como o perfil correspondente

#### Scenario: Perfil alterado para um valor desconhecido durante a sessão
- **WHEN** `GET /auth/me` devolve um `role` fora do mapa ou sem `role`
- **THEN** a sessão é apagada e o Login exibe "Seu perfil não tem permissão para acessar o CardioVida. Contate o administrador."

#### Scenario: Perfil indisponível por falha de rede
- **WHEN** `GET /auth/me` falha por rede ou servidor
- **THEN** vale o perfil guardado no login para decidir o acesso, sem encerrar a sessão

### Requirement: Restringir ações de agendamento por perfil
O mapa de permissões SHALL conceder `agendamento:consultar` a todos os perfis permitidos e `agendamento:gerenciar` (criar, editar, alterar status e excluir agendamentos) somente a Administrador e secretaria. Os controles e eventos dessas ações SHALL ser exibidos e executados apenas quando o perfil tiver `agendamento:gerenciar`.

#### Scenario: Médico consulta a agenda
- **WHEN** um usuário com perfil medico abre Agendamentos
- **THEN** vê a agenda, mas nenhum botão ou ação de criar, editar, alterar status ou excluir agendamento (por exemplo, "+ Novo Agendamento")

#### Scenario: Administrador ou secretaria gerenciam a agenda
- **WHEN** um usuário com perfil Administrador ou secretaria abre Agendamentos
- **THEN** as ações de gerenciamento, quando existirem, ficam disponíveis

### Requirement: Guardar o médico vinculado
Ao entrar, a aplicação SHALL guardar no estado de autenticação o id do médico vinculado ao usuário (campo `medico` do login), mantendo-o entre recarregamentos até o fim da sessão, para uso da agenda do médico.

#### Scenario: Login de médico com vínculo
- **WHEN** o login devolve `medico` com um id, ou um objeto com `id`
- **THEN** esse id fica disponível no estado de autenticação
- **AND** continua disponível após recarregar a página, mesmo que `GET /auth/me` não traga `medico`

#### Scenario: Usuário sem médico vinculado
- **WHEN** o login devolve `medico` nulo ou ausente
- **THEN** o id do médico fica vazio e o acesso segue as regras do perfil

## MODIFIED Requirements

### Requirement: Autenticar por email e senha
O formulário de login SHALL enviar o valor do campo "Usuário" como `email` e a senha como `senha` no corpo JSON de `POST /auth/login`, mostrando estado de carregando no botão "Entrar" enquanto aguarda a resposta. O login SHALL ser concluído somente para perfis presentes no mapa de permissões, levando o usuário à tela inicial do seu perfil.

#### Scenario: Login bem-sucedido com perfil buscado
- **WHEN** a API devolve `authToken` sem dados do usuário
- **THEN** o perfil é obtido por `GET /auth/me`
- **AND** se o perfil for permitido, o token é guardado e o usuário é levado à tela inicial do perfil
- **AND** se `GET /auth/me` falhar, o Login exibe a mensagem de erro e nenhum token é guardado

#### Scenario: Login bem-sucedido com perfil na resposta
- **WHEN** a API devolve `authToken` junto com o objeto do usuário
- **THEN** o perfil da resposta é aproveitado sem nova chamada obrigatória
- **AND** o usuário é levado à tela inicial do perfil: Início para Administrador e secretaria, Agendamentos para medico

#### Scenario: Perfil sem permissão
- **WHEN** o login é aceito pela API, mas o `role` do usuário está ausente ou fora do mapa de permissões
- **THEN** a tela de Login exibe "Seu perfil não tem permissão para acessar o CardioVida. Contate o administrador."
- **AND** o usuário permanece no Login e nenhum token é guardado

#### Scenario: Credenciais inválidas
- **WHEN** a API responde 400, 401 ou 403 ao login
- **THEN** a tela de Login exibe o `message` da resposta, se existir, ou "Email ou senha inválidos."
- **AND** o usuário permanece no Login e nenhum token é guardado

#### Scenario: Falha do servidor no login
- **WHEN** o login falha por erro de servidor, tempo esgotado ou falta de conexão
- **THEN** a tela de Login exibe uma mensagem amigável e o botão volta ao estado normal

#### Scenario: Servidor sem token na resposta
- **WHEN** a API responde ao login com sucesso, mas sem token (corpo `null`)
- **THEN** a tela de Login exibe "O servidor não retornou o token de acesso. Contate o administrador do sistema."
- **AND** para qualquer outro corpo sem token, exibe "Resposta inesperada do servidor."
- **AND** nenhum token é guardado

#### Scenario: Token em formatos diferentes
- **WHEN** a API devolve o token como texto puro ou em uma das chaves `authToken`, `auth_token`, `token`, `jwt` ou `access_token`
- **THEN** o login é concluído normalmente

#### Scenario: Login em andamento
- **WHEN** o usuário envia o formulário
- **THEN** o botão "Entrar" indica carregamento e não aceita novo envio até a resposta

### Requirement: Proteger as telas autenticadas
Todas as telas, exceto o Login, SHALL exigir sessão e perfil com permissão para a rota: sem token, ou com sessão inválida ou expirada, o usuário SHALL ser redirecionado para o Login; com rota não permitida ao perfil, SHALL ser redirecionado para a tela inicial do perfil. O conteúdo da tela não SHALL ser exibido antes da verificação.

#### Scenario: Acesso sem token
- **WHEN** o usuário abre Início, Pacientes, Agendamentos, Médicos, Convênio ou Exames sem token
- **THEN** é redirecionado para o Login sem ver o conteúdo da tela

#### Scenario: Sessão expirada
- **WHEN** `GET /auth/me` responde 401 ou `null` com status 200
- **THEN** o token e o perfil são apagados
- **AND** o usuário é redirecionado para o Login, que exibe "Sessão expirada. Entre novamente."

#### Scenario: Rota não permitida ao perfil
- **WHEN** um usuário autenticado abre uma tela fora das rotas do seu perfil
- **THEN** é redirecionado para a tela inicial do perfil sem ver o conteúdo da tela solicitada

### Requirement: Encerrar a sessão
Ao sair, a aplicação SHALL apagar o token, o perfil do usuário e o médico vinculado e levar o usuário ao Login.

#### Scenario: Usuário clica em Sair
- **WHEN** o usuário clica em "Sair"
- **THEN** o token, o perfil e o médico vinculado do armazenamento local, e os campos do formulário de login, são apagados
- **AND** o usuário é redirecionado para o Login
- **AND** abrir uma tela autenticada em seguida leva novamente ao Login
