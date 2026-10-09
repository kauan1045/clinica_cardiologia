## Why

O CardioVida ainda simula o login e não protege nenhuma tela. A API do Xano já expõe autenticação por JWT (`POST /auth/login`, `GET /auth/me`); esta change integra somente a autenticação, criando o módulo de acesso à API que as próximas integrações (pacientes, agendamentos, médicos, convênios, dashboard) vão reutilizar. As telas continuam com dados mockados.

## What Changes

- Configuração: `XANO_API_URL` lida do arquivo `.env` (nunca fixa no código), `.env` no `.gitignore` e um `.env.example` sem valor. `httpx` e `python-dotenv` entram no `requirements.txt`.
- Novo `api.py`: funções assíncronas com `httpx` (timeout de 10 s), envio de `Authorization: Bearer <token>` quando houver token e tratamento de erros: 401 com token = sessão expirada; resposta `null` com status 200 em endpoint autenticado = sessão inválida; demais falhas viram mensagens amigáveis em português. Inclui `request` (genérica, reutilizável), `login` e `get_me`.
- Login real: o formulário existente envia o valor do campo "Usuário" como `email` (e a senha como `senha`) em `POST /auth/login`, guarda o `authToken` em `rx.LocalStorage` (sobrevive ao recarregar), aproveita o objeto de usuário se vier na resposta (senão chama `GET /auth/me`) e leva ao Início. Falhas 400/401/403 mostram o `message` da API ou "Email ou senha inválidos."; o botão "Entrar" mostra estado de carregando.
- `AuthState` (em `auth.py`) passa a guardar token, perfil e estado de sessão, e concentra `entrar`, `verificar_sessao`, `sessao_expirada` e `sair`.
- Todas as telas, exceto o Login, exigem sessão: sem token, ou com 401/`null` em `GET /auth/me`, redirecionam para o Login (com a mensagem "Sessão expirada. Entre novamente." quando a sessão expirou). O conteúdo só é renderizado depois da verificação, para não piscar dados a quem não está autenticado.
- O Topbar passa a mostrar o `name` do usuário autenticado (senão o `email`) no lugar do nome fixo.
- "Sair" apaga token e perfil e volta ao Login.
- Sem mudança visual em nenhuma tela; as telas seguem com dados mockados. A saudação "Olá, Dr. Roberto" do Início permanece mockada.

## Capabilities

### New Capabilities
- `autenticacao`: configuração e cliente da API do Xano, login por email e senha com token JWT persistido, carregamento do perfil, proteção das telas autenticadas e encerramento de sessão.

### Modified Capabilities
- `login-cardiovida`: o envio do formulário preenchido passa a autenticar na API em vez de exibir um aviso de integração futura.
- `dashboard-inicio`: o controle de perfil da barra superior exibe o nome do usuário autenticado; o botão "Sair" também apaga o token e o perfil.

## Impact

- Novos: `ProjetoCl_nicaCardiologia/api.py`, `.env` (ignorado pelo git), `.env.example`.
- Alterados: `ProjetoCl_nicaCardiologia/auth.py` (estado de autenticação e `require_auth`), `ProjetoCl_nicaCardiologia.py` (login e registro das rotas com proteção), `dashboard.py` (nome no Topbar), `requirements.txt`, `.gitignore`.
- Não altera dados, layout ou lógica de Pacientes, Agendamentos, Médicos, Convênio e Exames, e não chama endpoints de escrita além do `POST /auth/login`.
- Dependências novas: `httpx`, `python-dotenv`.
