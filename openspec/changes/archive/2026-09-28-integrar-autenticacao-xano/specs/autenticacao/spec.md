## Purpose

A capability Autenticação permite que a equipe da clínica entre no CardioVida com email e senha pela API do Xano, mantenha a sessão entre recarregamentos, veja o próprio perfil e encerre a sessão, protegendo todas as telas autenticadas e oferecendo à aplicação um módulo único de acesso à API.

## ADDED Requirements

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
O formulário de login SHALL enviar o valor do campo "Usuário" como `email` e a senha como `senha` no corpo JSON de `POST /auth/login`, mostrando estado de carregando no botão "Entrar" enquanto aguarda a resposta.

#### Scenario: Login bem-sucedido com perfil buscado
- **WHEN** a API devolve `authToken` sem dados do usuário
- **THEN** o token é guardado e o perfil é obtido por `GET /auth/me`
- **AND** o usuário é levado à tela Início

#### Scenario: Login bem-sucedido com perfil na resposta
- **WHEN** a API devolve `authToken` junto com o objeto do usuário
- **THEN** o perfil da resposta é aproveitado sem nova chamada obrigatória
- **AND** o usuário é levado à tela Início

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
Todas as telas, exceto o Login, SHALL exigir sessão: sem token, ou com sessão inválida ou expirada, o usuário SHALL ser redirecionado para o Login, e o conteúdo da tela não SHALL ser exibido antes da verificação.

#### Scenario: Acesso sem token
- **WHEN** o usuário abre Início, Pacientes, Agendamentos, Médicos, Convênio ou Exames sem token
- **THEN** é redirecionado para o Login sem ver o conteúdo da tela

#### Scenario: Sessão expirada
- **WHEN** `GET /auth/me` responde 401 ou `null` com status 200
- **THEN** o token e o perfil são apagados
- **AND** o usuário é redirecionado para o Login, que exibe "Sessão expirada. Entre novamente."

### Requirement: Encerrar a sessão
Ao sair, a aplicação SHALL apagar o token e o perfil do usuário e levar o usuário ao Login.

#### Scenario: Usuário clica em Sair
- **WHEN** o usuário clica em "Sair"
- **THEN** o token do armazenamento local, o perfil e os campos do formulário de login são apagados
- **AND** o usuário é redirecionado para o Login
- **AND** abrir uma tela autenticada em seguida leva novamente ao Login
