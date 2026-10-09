## Why

O CardioVida já possui a tela de login, mas ainda não oferece uma experiência inicial para a equipe após o acesso. O Dashboard será a primeira tela autenticada e estabelecerá a navegação lateral e a barra superior reutilizáveis para as próximas áreas do sistema.

## What Changes

- Criar a tela inicial autenticada (Dashboard) com saudação, data atual, indicador de pacientes do dia e próximos atendimentos.
- Criar um componente reutilizável `Sidebar` com as áreas Início, Pacientes, Agendamentos, Médicos, Convênio, Exames e Configurações.
- Criar um componente reutilizável `Topbar` com busca, notificações e perfil.
- Implementar dados mockados para indicadores e atendimentos, mantendo uma estrutura substituível por integração futura.
- Aplicar o design system CardioVida e a composição visual baseada no protótipo Figma informado.
- Manter o login existente e não adicionar redirecionamento automático nesta change.

## Capabilities

### New Capabilities

- `dashboard-inicio`: Dashboard autenticado com navegação compartilhada, indicadores do dia e próximos atendimentos.

### Modified Capabilities

Nenhuma.

## Impact

- Afeta a aplicação Reflex em `ProjetoCl_nicaCardiologia/ProjetoCl_nicaCardiologia.py` e os componentes auxiliares que serão extraídos para reuso.
- Adiciona uma rota ou entrada de página para o Dashboard, sem alterar o fluxo de autenticação existente.
- Não adiciona dependências externas, banco de dados ou APIs.
- Usa os padrões visuais documentados em `openspec/design-system.md`.
