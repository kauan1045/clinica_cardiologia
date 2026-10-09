## Context

A API do Xano (`XANO_API_URL`) autentica com JWT: `POST /auth/login` recebe `{"email", "senha"}` (com `password` a API responde `403`) e devolve `authToken`, `token` (mesmo valor) e `user` (`id`, `name`, `email`, `role`, `medico`); `GET /auth/me` devolve o usuário (`id`, `name`, `email`, `role`) e exige `Authorization: Bearer <token>`. Sem token, os endpoints protegidos não respondem 401: devolvem `200` com corpo `null` (verificado em `/dashboard`, `/paciente`, `/agendamento`, `/medico` e `/lista_medico`). O login atual do app apenas valida campos vazios e exibe um aviso. As telas usam dados mockados e não têm proteção.

## Goals / Non-Goals

**Goals:**
- Módulo `api.py` reutilizável pelas próximas integrações, com URL vinda do ambiente, Bearer token, timeout e erros tratados.
- Login real, sessão persistida entre recarregamentos, perfil no Topbar, telas protegidas e "Sair" completo.
- Nenhuma mudança visual nas telas.

**Non-Goals:**
- Integrar dados de pacientes, agendamentos, médicos, convênios ou dashboard; qualquer chamada a endpoints de escrita além do login; recuperação de senha; controle de acesso por `role`; renovação de token.

## Decisions

### Cliente da API (`api.py`)
- `XANO_API_URL` é lida com `os.getenv` a cada chamada, após `load_dotenv()`; variável de ambiente já definida tem prioridade sobre o `.env` (permite apontar para outro ambiente sem editar arquivos). Sem URL, a chamada falha com mensagem orientando a definir o `.env`.
- `request(method, path, token=None, json=None, params=None)` é a função genérica; `login` e `get_me` a usam (o login usa `_send` diretamente porque 400/401/403 significam credencial inválida, e não sessão expirada).
- Exceções: `ApiError(message, status)`, com subclasses `InvalidCredentials` e `SessionExpired`. Mapeamento: com token, 401 e corpo `null` → `SessionExpired`; 403 → "sem permissão" (ou `message`); 5xx → "servidor indisponível"; demais 4xx → `message` da API ou mensagem genérica; timeout e falha de conexão → mensagens próprias. Sem token, corpo `null` é devolvido como `None`.
- O login envia a senha na chave `senha` do corpo JSON, conforme o endpoint do Xano.
- `get_me` e o login removem os campos `password` e `senha` do perfil por segurança, mesmo que a API não os envie.
- Tolerância: o token é lido como string pura ou de `authToken`, `auth_token`, `token`, `jwt` ou `access_token`; o perfil pode vir junto no login (`user`) ou ser buscado em `/auth/me`; se `/auth/me` falhar logo após um login bem-sucedido, o login segue e o perfil é recarregado ao abrir o Início.

### Estado e sessão (`AuthState`)
- `token` fica em `rx.LocalStorage` (persiste ao recarregar, como pedido). Trade-off conhecido: `localStorage` é legível por scripts da página (risco em caso de XSS); aceito nesta fase por decisão do produto.
- O perfil (`user`) não é persistido: é recarregado por `GET /auth/me` em toda abertura de tela autenticada (`on_load=AuthState.verificar_sessao`), o que também valida o token a cada navegação.
- `session_ok` é `True` só depois da verificação. `require_auth(page)` embrulha cada tela com `rx.cond(AuthState.session_ok, page(), <fundo vazio>)`, evitando que dados apareçam brevemente a quem não está autenticado. O wrapper é aplicado no registro das rotas, sem editar cada tela.
- Falha de rede ou 5xx em `/auth/me` não derruba a sessão (a tela abre e o nome cai para "Usuário"); somente 401/`null` encerram a sessão.
- O formulário de login continua em `State` (usuário, senha, mostrar senha, lembrar-me), sem lógica de autenticação. O envio vai direto para `AuthState.entrar`. O `State` é limpo (`reset`) após login e no "Sair" para não manter a senha em memória; como `auth.py` não pode importar o app no topo (o app importa o `Sidebar`, que usa o `AuthState`), o import é feito dentro do método.
- Erros e o carregamento do login vivem no `AuthState` (`login_error`, `loading`); "Sessão expirada. Entre novamente." usa o mesmo campo, exibido no Login após o redirecionamento.
- Para as próximas integrações: chamar `api.request(..., token=AuthState.token)` e, em `SessionExpired`, disparar `AuthState.sessao_expirada`.

### Diagnóstico do login real
Com a conta de teste do `.env`, `POST /auth/login` respondeu `200` com corpo `null` em todas as variações testadas (JSON, formulário, query string, senha errada, e-mail inexistente, corpo vazio), e `GET /auth/me` respondeu `200 null` inclusive com token inválido. Rotas inexistentes respondem `404` com o JSON de erro do Xano, portanto as rotas existem. Um input obrigatório ausente resultaria em `400` e um token inválido em `401`; a ausência desses erros indica endpoints sem inputs de autenticação nem resposta configurados no Xano (ou grupo de API diferente do que está no `.env`). A correção é do lado do Xano.
Depois de configurado no Xano, o login passou a responder `403` ao corpo com `password`; a causa era o nome da chave: o endpoint espera `{"email", "senha"}`. Com `senha`, a conta de teste recebe `200` com `authToken`, `token` e `user`, e `GET /auth/me` devolve o perfil. Os formatos dos endpoints de leitura estão em `docs/xano-formatos.md`.
No app, `login` passou a aceitar o token como string pura ou em `authToken`, `auth_token`, `token`, `jwt` ou `access_token`, e a diferenciar corpo `null` ("O servidor não retornou o token de acesso. Contate o administrador do sistema.") de resposta malformada ("Resposta inesperada do servidor.").

### Campo "Usuário"
O layout não muda: o campo continua com o placeholder "Usuário", e o valor digitado é enviado como `email`. A API só autentica por email; ajustar o rótulo para "Email" fica como decisão de produto.

### "Lembrar-me"
O checkbox permanece, porém sem efeito nesta change: o token é sempre persistido. Alterar isso (persistir só quando marcado) é uma mudança de comportamento a decidir depois.

## Risks / Trade-offs

- [Risk] `localStorage` expõe o token a XSS. -> Mitigation: aceito conscientemente; o app não renderiza HTML de terceiros e os dados vêm de fontes controladas.
- [Risk] A mensagem de erro da API pode vir em inglês (padrão do Xano, ex.: "Invalid Credentials."). -> Mitigation: o `message` é exibido como a API enviar, conforme pedido; pode ser traduzido no Xano ou mapeado depois.
- [Risk] Uma resposta `null` legítima de um endpoint autenticado seria lida como sessão inválida. -> Mitigation: regra explícita para a autenticação; ao integrar endpoints que possam devolver `null` de fato, usar uma chamada que não aplique essa regra.
- [Risk] A saudação "Olá, Dr. Roberto" no Início segue fixa. -> Mitigation: fora do escopo desta change (só o Topbar); passa a usar o perfil quando o Início for integrado.
- [Risk] O estado do login guarda dados por sessão no servidor do Reflex (memória). -> Mitigation: a senha é apagada logo após o login e o token vive no navegador.
