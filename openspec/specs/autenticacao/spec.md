# autenticacao Specification

## Purpose
A capability Autenticação permite que a equipe da clínica entre no CardioVida com email e senha pela API do Xano, mantenha a sessão entre recarregamentos, veja o próprio perfil e encerre a sessão, protegendo todas as telas autenticadas e oferecendo à aplicação um módulo único de acesso à API.

## Requirements

### Requirement: Configurar a URL da API por variável de ambiente
A aplicação SHALL ler a URL base da API da variável `XANO_API_URL` (definida no arquivo `.env`), sem fixá-la no código, e o arquivo `.env` SHALL ser ignorado pelo controle de versão.

#### Scenario: URL configurada
- **WHEN** `XANO_API_URL` está definida
- **THEN** todas as chamadas à API usam essa URL como base
- **AND** o código-fonte não contém a URL da API

#### Scenario: URL ausente
- **WHEN** `XANO_API_URL` não está definida ou está vazia
- **THEN** a chamada à API falha com uma mensagem amigável orientando a definir `XANO_API_URL` no `.env`, sem quebrar a tela

### Requirement: Oferecer um módulo reutilizável de acesso à API
A aplicação SHALL oferecer um módulo assíncrono de acesso à API que envie o cabeçalho `Authorization: Bearer <token>` quando houver token, aplique tempo limite às chamadas e converta falhas em erros com mensagens amigáveis, para reutilização pelas próximas integrações.

#### Scenario: Sessão expirada
- **WHEN** um endpoint autenticado responde 401
- **THEN** o módulo sinaliza sessão expirada
- **AND** quando um endpoint autenticado responde `null` com status 200, o módulo também sinaliza sessão inválida

#### Scenario: Falha de comunicação ou do servidor
- **WHEN** a API não responde a tempo, não é alcançada ou responde com erro de servidor
- **THEN** o módulo sinaliza um erro com mensagem amigável em português
- **AND** a mensagem não expõe detalhes técnicos, credenciais ou o token

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

### Requirement: Persistir a sessão entre recarregamentos
O token de autenticação SHALL ser guardado no armazenamento local do navegador, de modo que a sessão sobreviva ao recarregamento da página.

#### Scenario: Usuário recarrega uma tela autenticada
- **WHEN** o usuário autenticado recarrega qualquer tela
- **THEN** a sessão continua válida e a tela abre normalmente, sem novo login

### Requirement: Carregar e exibir o perfil do usuário
Ao abrir uma tela autenticada, a aplicação SHALL obter o perfil por `GET /auth/me` e exibir no Topbar o nome do usuário (`name`), ou o email quando não houver nome, sem quebrar se algum campo faltar e sem manter a senha.

#### Scenario: Perfil completo
- **WHEN** `GET /auth/me` devolve `name` e `email`
- **THEN** o Topbar exibe o `name`

#### Scenario: Perfil sem nome
- **WHEN** `GET /auth/me` devolve o usuário sem `name`
- **THEN** o Topbar exibe o `email`

#### Scenario: Perfil indisponível
- **WHEN** a busca do perfil falha por erro de rede ou de servidor
- **THEN** a tela abre normalmente com o texto "Usuário" no lugar do nome

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

### Requirement: Controlar o acesso por perfil
A aplicação SHALL definir, num único mapa de permissões, as rotas permitidas, a tela inicial e as ações de cada perfil (Administrador, secretaria e medico), comparando o `role` do usuário sem diferenciar maiúsculas, minúsculas e acentos. O mesmo mapa SHALL ser usado pelo menu lateral, pela proteção das páginas e pelas verificações de ação.

#### Scenario: Administrador
- **WHEN** o usuário tem perfil Administrador
- **THEN** pode abrir Início, Pacientes, Agendamentos, Médicos, Convênio e Exames

#### Scenario: Secretaria
- **WHEN** o usuário tem perfil secretaria
- **THEN** pode abrir somente Pacientes e Agendamentos

#### Scenario: Médico abre Agendamentos ou Prescrições
- **WHEN** o usuário tem perfil medico
- **THEN** pode abrir Agendamentos e Prescrições

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
