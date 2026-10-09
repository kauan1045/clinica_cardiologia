## 1. Permissões

- [x] 1.1 Criar em `auth.py` o mapa `PERMISSOES` (rotas, tela inicial e ações por perfil: administrador, secretaria, medico) e as funções `normalizar_perfil`, `rotas_do_perfil`, `rota_inicial` e `tem_permissao`.
- [x] 1.2 Registrar `agendamento:consultar` para todos os perfis e `agendamento:gerenciar` só para administrador e secretaria; expor `AuthState.pode_gerenciar_agendamento` para a futura change de Agendamentos.

## 2. Estado de autenticação

- [x] 2.1 Adicionar `perfil` e `medico_id` ao `AuthState` (em `rx.LocalStorage`) e a computed var `rotas_permitidas`; apagar os dois em "Sair", na expiração e na negação de acesso.
- [x] 2.2 `entrar`: obter o perfil (do login ou de `/auth/me`), recusar perfil desconhecido ou ausente com mensagem no Login, guardar `medico_id` e redirecionar para a tela inicial do perfil.
- [x] 2.3 `verificar_sessao`: atualizar o perfil pelo `/auth/me` (usando o salvo em falha de rede), negar perfil desconhecido e redirecionar rotas não permitidas para a tela inicial.
- [x] 2.4 `verificar_login` no `on_load` do Login: médico com sessão ativa vai para `/agendamento` (em falha de rede, servidor ou limite de requisições, vale o perfil salvo).

## 3. Interface

- [x] 3.1 `require_auth(page, rota)` renderiza só com sessão verificada e rota permitida; registrar as rotas com o par (tela, rota).
- [x] 3.2 Menu lateral exibe apenas os itens permitidos ao perfil, com "Sair" sempre visível e sem mudança visual para Administrador e secretaria.

## 4. Specs

- [x] 4.1 Escrever os deltas de `autenticacao` e `dashboard-inicio`.
- [x] 4.2 Rodar `openspec validate controlar-acesso-por-perfil --strict`.

## 5. Validação

- [x] 5.1 `reflex compile --dry` sem erros.
- [x] 5.2 Testar com servidor Xano simulado (somente `POST /auth/login` e GETs): destino do login por perfil (com maiúsculas e acento), `medico_id` (número, objeto, nulo), perfil desconhecido ou ausente bloqueado, login sem `user` usando `/auth/me`, médico redirecionado de todas as outras rotas, administrador e secretaria em todas as rotas, perfil alterado durante a sessão, falha de rede com perfil salvo, 401, Login com médico logado, permissões de agendamento e "Sair".
- [x] 5.3 Login real com as contas de teste do `.env` (`XANO_TEST_*` e `XANO_TEST_MEDICO_*`), com o fluxo do `AuthState` contra a API (só `POST /auth/login` e `GET /auth/me`): administrador (`role` "Administrador", `medico` nulo) → `/dashboard`, abre as seis telas, gerencia agenda, fica no Login ao abrir `/`; médico (`role` "Médico", `medico` como objeto com `id`, `nome`, `crm`, `especialidade`) → `/agendamento`, `medico_id` guardado e mantido após `/auth/me`, as demais telas e `/` redirecionam para `/agendamento`, sem gerenciar agenda; "Sair" limpa token, perfil e `medico_id` nos dois.
- [ ] 5.4 Testar no navegador com uma conta real de perfil medico e com uma de Administrador (menu, redirecionamentos, recarregar a página e "Sair").
