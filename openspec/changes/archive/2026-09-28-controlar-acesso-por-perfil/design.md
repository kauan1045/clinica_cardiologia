## Context

O `AuthState` guarda o token em `rx.LocalStorage`, e `verificar_sessao` (no `on_load` de cada tela autenticada) recarrega o perfil com `GET /auth/me`. `require_auth(page)` só renderiza a tela com `session_ok`. O login do Xano devolve `user` com `id`, `name`, `email`, `role` e `medico`; o `/auth/me` devolve `id`, `name`, `email` e `role`, sem `medico`. A conta de teste tem perfil Administrador e nenhum médico vinculado.

A tela de Agendamentos ainda usa dados locais e não tem botões de criar, editar, alterar status ou excluir. A regra de "somente leitura" para médicos precisa valer desde já para as próximas integrações.

## Goals / Non-Goals

**Goals:**
- Um único lugar para definir o que cada perfil acessa (rotas e ações), usado pelo menu, pela proteção das páginas e, no futuro, pela tela de Agendamentos.
- Médico restrito à agenda, apenas para consulta; Administrador e secretaria como hoje; perfil desconhecido bloqueado.
- Guardar o médico vinculado para filtrar a agenda depois.

**Non-Goals:**
- Integrar Agendamentos à API ou filtrar a agenda por médico.
- Controle de acesso no servidor: a autorização real continua sendo responsabilidade do Xano; aqui se trata da experiência no app.
- Telas de gestão de usuários ou perfis.

## Decisions

### Mapa de permissões (`auth.PERMISSOES`)
```python
PERMISSOES = {
    "administrador": {"rotas": ROTAS_ADMINISTRATIVAS, "inicial": "/dashboard", "acoes": ("agendamento:consultar", "agendamento:gerenciar")},
    "secretaria":    {"rotas": ROTAS_ADMINISTRATIVAS, "inicial": "/dashboard", "acoes": ("agendamento:consultar", "agendamento:gerenciar")},
    "medico":        {"rotas": ("/agendamento",),     "inicial": "/agendamento", "acoes": ("agendamento:consultar",)},
}
```
- `ROTAS_ADMINISTRATIVAS` reúne `/dashboard`, `/pacientes`, `/agendamento`, `/medicos`, `/convenio` e `/exames`.
- Funções auxiliares: `normalizar_perfil`, `rotas_do_perfil`, `rota_inicial` e `tem_permissao(perfil, acao)`.
- No estado, as computed vars `AuthState.rotas_permitidas` e `AuthState.pode_gerenciar_agendamento` servem à interface.
- A futura change de Agendamentos deve envolver os botões de criar, editar, alterar status e excluir em `rx.cond(AuthState.pode_gerenciar_agendamento, ...)`, e os eventos correspondentes devem checar `tem_permissao(perfil, "agendamento:gerenciar")` no backend antes de chamar a API.
- `normalizar_perfil` aplica `casefold` e remove acentos, para que "Administrador", "ADMINISTRADOR", "Médico" e "medico" funcionem. Perfil fora do mapa é tratado como sem permissão.
- Alternativa descartada: espalhar `if perfil == "medico"` pelas telas, o que dificultaria mudar as regras depois.

### Onde o perfil vive
- `perfil` (já normalizado) e `medico_id` ficam em `rx.LocalStorage`, junto com o token, e são apagados com ele.
  - `medico_id` precisa persistir porque `/auth/me` não devolve `medico`, e o `user` em memória se perde ao recarregar.
  - `perfil` persiste para que uma falha de rede em `/auth/me` não derrube a sessão, mantendo o comportamento atual.
- A fonte da verdade é o servidor: sempre que `/auth/me` responde, o perfil é atualizado a partir do `role`. O valor salvo só é usado quando `/auth/me` falha por rede ou servidor. Se o `/auth/me` um dia trouxer `medico`, o `medico_id` também é atualizado.
- `medico_id` é texto. Aceita o id numérico ou um objeto com `id`; `null` ou ausente vira "". Um médico sem vínculo entra normalmente; a futura agenda decide o que mostrar.

### Login
- Após `POST /auth/login`, o perfil sai de `user.role`. Sem `user`, sai de `GET /auth/me`, e se essa chamada falhar o login é interrompido com a mensagem de erro (antes o login seguia sem perfil).
- Perfil fora do mapa: exibe `NO_PERMISSION_MESSAGE` no Login, não guarda token e não redireciona.
- Perfil válido: guarda token, perfil e `medico_id` e redireciona para `rota_inicial(perfil)`.
- O Login (`/`) ganha `on_load=AuthState.verificar_login`: se há token e o perfil salvo é `medico`, confirma com `/auth/me` e redireciona para `/agendamento`. Para outros perfis, o Login continua como hoje, sem chamada à API. Se o `/auth/me` falhar por rede, servidor ou limite de requisições (429), vale o perfil salvo, como em `verificar_sessao`; a tela de destino valida a sessão de novo.

### Proteção das páginas
- `verificar_sessao` valida o token (401 ou `null` expiram a sessão, como hoje) e atualiza o perfil.
  - Perfil fora do mapa: apaga a sessão e volta ao Login com a mensagem de sem permissão.
  - Rota atual (`self.router.url.path`, sem barra final) fora das rotas do perfil: `session_ok = False` e redireciona para a tela inicial do perfil.
- `require_auth(page, rota)` passa a renderizar só com `session_ok` e com a `rota` em `AuthState.rotas_permitidas`. Assim a tela proibida não aparece nem por um instante, mesmo com o estado de uma navegação anterior ainda em memória.
- As rotas são registradas num laço com o par (tela, rota), usado tanto no `require_auth` quanto no `add_page`.

### Menu
Cada item de `MENU_ITEMS` é envolvido em `rx.cond(AuthState.rotas_permitidas.contains(href), ...)`. O botão "Sair" continua sempre visível. Para Administrador e secretaria o menu fica idêntico ao atual.

## Risks / Trade-offs

- [Risk] O perfil salvo no `localStorage` pode ser editado pelo usuário. → Mitigation: só é usado quando `/auth/me` falha e é sobrescrito na próxima resposta; a autorização dos dados é do Xano. Recomenda-se que o Xano também restrinja os endpoints por `role`.
- [Risk] Sessões abertas antes desta change não têm perfil salvo. → Mitigation: o `/auth/me` preenche o perfil na primeira tela aberta; só uma falha de rede nesse momento leva ao Login com a mensagem de sem permissão.
- [Risk] Novos perfis criados no Xano ficam bloqueados até entrarem no mapa. → Mitigation: comportamento pedido (perfil desconhecido não entra); basta acrescentar uma entrada em `PERMISSOES`.
- [Risk] O plano do Xano limita a 10 requisições a cada 20 segundos (`429 ERROR_CODE_TOO_MANY_REQUESTS`), e cada tela aberta chama `/auth/me` e a sua lista. → Mitigation: em 429 o acesso usa o perfil salvo e a sessão não cai; a mensagem de 429 no login ainda vem do Xano (em inglês) e pode ser tratada numa change futura do `api.py`.
