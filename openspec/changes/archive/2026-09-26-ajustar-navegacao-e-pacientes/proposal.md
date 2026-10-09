## Why

O produto não terá a área "Configurações" nesta versão, e a equipe precisa de uma forma de encerrar a sessão a partir de qualquer tela. Além disso, a tela Pacientes não precisa do status ativo/inativo, mas sim do email de contato de cada paciente.

## What Changes

- Remover o item "Configurações" de `MENU_ITEMS` em `dashboard.py`; o menu lateral (compartilhado por todas as telas) passa a ter Início, Pacientes, Agendamentos, Médicos, Convênio e Exames.
- Adicionar ao `Sidebar` um botão "Sair" fixo no rodapé (acima da nota "Versão demonstrativa"), com ícone de logout, na mesma escala e estilo dos itens do menu, com hover e cursor pointer. Posição conforme o frame Configurações do Figma (node `31:585`, texto "Sair" no canto inferior esquerdo).
- Ao clicar em "Sair", o evento `AuthState.sair` (novo módulo `auth.py`) limpa o estado do login (`State`: usuário, senha, "lembrar-me" e feedback) e redireciona para a tela de Login (`/`). A lógica fica isolada nesse método para, futuramente, apagar também o token da API. Ainda não existe token no projeto.
- Tela Pacientes: remover a coluna Status, o badge e o campo `status` do mock; adicionar a coluna Email depois de Telefone, com emails mockados; a busca passa a filtrar também por email.
- `patient_status_badge` permanece em `patients.py` porque Médicos e Convênio o reutilizam; apenas Pacientes deixa de usá-lo. Os badges de Médicos, Convênio e Exames não mudam.
- Sidebar com a altura da janela (100vh) e fixa (sticky): só a área de conteúdo rola e o botão "Sair" fica sempre visível no rodapé do menu, inclusive em telas altas como Agendamentos.
- Escrever o Purpose das specs `convenio` e `exames` (estavam como placeholder "TBD" após o arquivamento), para que `openspec validate --all` passe.
- Specs: atualizar `dashboard-inicio` (menu sem "Configurações", com "Sair"), `pacientes` (sem status, com email) e ajustar a redação de `medicos`, `convenio` e `exames`, que descreviam o badge como "usado na tela Pacientes".

## Capabilities

### New Capabilities
Nenhuma.

### Modified Capabilities
- `dashboard-inicio`: menu lateral sem "Configurações" e com o botão "Sair", que encerra a sessão e leva ao Login.
- `pacientes`: tabela sem a coluna Status/badge e com a coluna Email; busca também por email; dados mockados com email em vez de status.
- `medicos`: o badge de status passa a ser descrito como o badge de status compartilhado, sem depender da tela Pacientes.
- `convenio`: idem.
- `exames`: o badge próprio da tela mantém o formato de pílula do badge de status compartilhado, sem depender da tela Pacientes.

## Impact

- `ProjetoCl_nicaCardiologia/dashboard.py`: `MENU_ITEMS` e `Sidebar` (botão "Sair", altura 100vh e posição sticky).
- `ProjetoCl_nicaCardiologia/auth.py` (novo): `AuthState.sair`.
- `ProjetoCl_nicaCardiologia/patients.py`: mock, busca, cabeçalho e linha da tabela.
- `openspec/specs/convenio/spec.md` e `openspec/specs/exames/spec.md`: apenas o texto do Purpose.
- `assets/settings.svg`: removido.
- Não altera `medicos.py`, `convenio.py`, `exames.py` nem `agendamento.py`, e não adiciona dependências, backend ou rotas.
- Remover o asset `assets/settings.svg`, que deixa de ser usado.
