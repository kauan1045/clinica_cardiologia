## Why

Hoje qualquer usuário autenticado vê todas as telas do CardioVida. O Xano já informa o perfil (`role`: Administrador, medico ou secretaria) e o médico vinculado (`medico`). Médicos devem trabalhar só com a própria agenda, sem acesso a cadastros e sem poder alterar agendamentos. Perfis desconhecidos não devem entrar.

## What Changes

- Um mapa de permissões em `auth.py` define, para cada perfil, as rotas permitidas, a tela inicial e as ações (`agendamento:consultar`, `agendamento:gerenciar`). O menu e a proteção das páginas usam o mesmo mapa.
- **medico**: após o login vai direto para `/agendamento`. O menu mostra só "Agendamentos" e "Sair". Qualquer outra tela autenticada, inclusive o Login com sessão ativa, redireciona para `/agendamento`. Na agenda, o médico só consulta (sem `agendamento:gerenciar`).
- **Administrador** e **secretaria**: acesso a todas as telas, como hoje, e permissão de gerenciar agendamentos.
- **Perfil desconhecido ou ausente**: o login é recusado com "Seu perfil não tem permissão para acessar o CardioVida. Contate o administrador.", e nenhum token é guardado. A mesma regra vale se o perfil mudar no Xano durante a sessão.
- O perfil é comparado sem diferenciar maiúsculas, minúsculas e acentos.
- O id do médico vinculado (`medico` do login) fica guardado no `AuthState` (`medico_id`) para a futura integração de Agendamentos.
- Se o login vier sem o objeto `user` e `GET /auth/me` falhar, o login não é concluído, porque sem perfil não há como decidir o acesso.
- Sem mudança visual para Administrador e secretaria. A tela de Agendamentos continua com os dados atuais.

## Capabilities

### New Capabilities
<!-- nenhuma -->

### Modified Capabilities
- `autenticacao`: login leva à tela inicial do perfil e recusa perfis sem permissão; proteção das telas por perfil; mapa de permissões com ações; médico vinculado guardado; "Sair" apaga também perfil e médico.
- `dashboard-inicio`: o menu lateral exibe só os itens permitidos ao perfil.

## Impact

- Código: `auth.py` (mapa de permissões, `AuthState.perfil`, `medico_id`, `rotas_permitidas`, `pode_gerenciar_agendamento`, `verificar_login`, `require_auth(page, rota)`), `dashboard.py` (itens do menu condicionados ao perfil) e `ProjetoCl_nicaCardiologia.py` (registro das rotas e `on_load` do Login).
- API: somente `POST /auth/login` e `GET /auth/me`, já usados.
- Sem novas dependências.
