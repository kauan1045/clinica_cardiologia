## 1. Menu lateral

- [x] 1.1 Remover "Configurações" de `MENU_ITEMS` em `dashboard.py`.
- [x] 1.2 Criar `auth.py` com `AuthState.sair`, que limpa o estado do login (`State`) e redireciona para `/`, mantendo a lógica isolada para futura remoção do token da API.
- [x] 1.3 Adicionar ao `Sidebar` o botão "Sair" no rodapé (ícone de logout, mesma escala e estilo dos itens do menu, hover e cursor pointer) ligado a `AuthState.sair`.
- [x] 1.4 Fixar a `Sidebar` na altura da janela (100vh, sticky no topo), de modo que só o conteúdo role e o botão "Sair" fique sempre visível no rodapé do menu.
- [x] 1.5 Remover `assets/settings.svg`, sem referências restantes no código.

## 2. Tela Pacientes

- [x] 2.1 Remover o campo `status` do mock e a coluna Status (cabeçalho e linha) de `patients.py`, sem remover `patient_status_badge`, que Médicos e Convênio reutilizam.
- [x] 2.2 Adicionar o campo `email` ao mock e a coluna Email depois de Telefone, com larguras relativas que evitem rolagem horizontal e cortes.
- [x] 2.3 Incluir o email no filtro da busca.

## 3. Specs

- [x] 3.1 Escrever os deltas de `dashboard-inicio`, `pacientes`, `medicos`, `convenio` e `exames` e validar com `openspec validate ajustar-navegacao-e-pacientes --strict`.
- [x] 3.2 Escrever o Purpose das specs `openspec/specs/convenio/spec.md` e `openspec/specs/exames/spec.md` e confirmar que `openspec validate --all --strict` passa.

## 4. Validação

- [x] 4.1 Executar `reflex compile --dry` sem erros.
- [x] 4.2 Executar `reflex run` e conferir Login, Início, Pacientes, Agendamentos, Médicos, Convênio e Exames: nenhum item "Configurações" no menu, "Sair" presente no rodapé e sem rolagem horizontal em 1280, 1366 e 1920px.
- [x] 4.3 Testar "Sair" (hover, cursor, clique → Login com campos limpos) e, em Pacientes, a busca por email e a ausência de Status; conferir que os badges de Médicos, Convênio e Exames permanecem iguais.
- [x] 4.4 Conferir em todas as telas (principalmente Agendamentos, a mais alta) que a Sidebar ocupa a altura da janela, permanece fixa ao rolar o conteúdo e mantém o "Sair" visível, sem rolagem horizontal.
