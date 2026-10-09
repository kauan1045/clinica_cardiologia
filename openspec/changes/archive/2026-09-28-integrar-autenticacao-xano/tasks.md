## 1. Configuração

- [x] 1.1 Criar `.env` com `XANO_API_URL`, `.env.example` sem valor e adicionar `.env` ao `.gitignore`, confirmando com `git check-ignore` e que a URL não aparece fixa no código.
- [x] 1.2 Adicionar `httpx` e `python-dotenv` ao `requirements.txt`.

## 2. Cliente da API

- [x] 2.1 Criar `api.py` com `request`, `login` e `get_me` assíncronos (httpx, timeout, Bearer quando houver token), lendo `XANO_API_URL` do ambiente.
- [x] 2.2 Tratar erros: 401 com token e `null` com status 200 em endpoint autenticado → `SessionExpired`; 400/401/403 no login → `InvalidCredentials` com o `message` da API ou "Email ou senha inválidos."; 403/4xx/5xx, timeout e falha de conexão → mensagens amigáveis.
- [x] 2.3 Remover os campos `password` e `senha` do perfil devolvido.

## 3. Estado de autenticação

- [x] 3.1 Implementar em `auth.py` o `AuthState` com `token` em `rx.LocalStorage`, `user`, `login_error`, `loading`, `session_ok` e a computed var `user_display_name` (name, senão email).
- [x] 3.2 Implementar `entrar` (validação, estado de carregando, token, perfil do login ou `GET /auth/me`, limpeza do formulário e redirecionamento ao Início).
- [x] 3.3 Implementar `verificar_sessao`, `sessao_expirada` e `sair` (apaga token e perfil, limpa o formulário e vai ao Login).
- [x] 3.4 Implementar `require_auth` e registrar as rotas Início, Pacientes, Agendamentos, Médicos, Convênio e Exames com proteção e `on_load=AuthState.verificar_sessao`.

## 4. Interface (sem mudança visual)

- [x] 4.1 Ligar o formulário de login a `AuthState.entrar`, com `loading` no botão "Entrar" e a mensagem de erro no local do feedback atual; remover o feedback e o `submit_login` antigos de `State`.
- [x] 4.2 Exibir `AuthState.user_display_name` no Topbar no lugar de "Dr. Roberto".

## 5. Specs

- [x] 5.1 Escrever a spec `autenticacao` e os deltas de `login-cardiovida` e `dashboard-inicio`; atualizar o Purpose de `login-cardiovida`.
- [x] 5.2 Rodar `openspec validate integrar-autenticacao-xano --strict` e `openspec validate --all --strict`.

## 6. Validação

- [x] 6.1 Executar `reflex compile --dry` e `reflex run` sem erros.
- [x] 6.2 Testar contra um servidor Xano simulado (sem tocar na API real): sem token → Login em todas as telas; campos vazios; 403 com `message`; 400 sem `message`; 500; botão em carregamento; login ok com perfil buscado e com perfil vindo no login; perfil só com email; token com 401 e com `null` → Login com "Sessão expirada"; sessão preservada ao recarregar; "Sair" apaga token e volta ao Login; nenhuma tela com rolagem horizontal.
- [x] 6.3 Testar `api.py` isoladamente: servidor fora do ar, ausência de `XANO_API_URL`, perfil sem `password`, `null` com e sem token.
- [x] 6.4 Testar o login real com a conta de teste do `.env` (`XANO_TEST_EMAIL` e `XANO_TEST_PASSWORD`, ignorado pelo git): a API devolve `200` com corpo `null` a qualquer chamada de `POST /auth/login` (senha errada, e-mail inexistente e corpo vazio inclusive) e `200 null` em `GET /auth/me` até com token inválido; rotas inexistentes respondem `404` normalmente. Diagnóstico: os endpoints existem, mas sem inputs e resposta configurados no Xano. O app passa a exibir mensagem específica para esse caso.
- [x] 6.5 Tornar o login tolerante ao formato do token (string pura, `authToken`, `auth_token`, `token`, `jwt`, `access_token`) e distinguir corpo vazio de resposta malformada, testado com servidor simulado.
- [x] 6.6 Repetir o login real depois que `POST /auth/login` e `GET /auth/me` devolverem dados no Xano (token no login; usuário em `/auth/me`) e confirmar o fluxo completo até o Início. O `403` vinha da chave da senha: o endpoint espera `{"email", "senha"}`; `api.login` passou a enviar `senha` e, com a conta de teste, recebe `200` com `authToken`, `token` e `user`, e `GET /auth/me` devolve o perfil. Estrutura dos endpoints de leitura registrada em `docs/xano-formatos.md` (somente GET).
