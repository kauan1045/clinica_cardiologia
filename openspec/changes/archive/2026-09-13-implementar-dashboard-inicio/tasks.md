## 1. Estrutura e dados

- [x] 1.1 Criar o módulo/estrutura de dados mockados do Dashboard com paciente, horário, médico e status, verificando que os registros tenham campos compatíveis com futura API.
- [x] 1.2 Separar a composição da página dos dados mockados e ordenar os atendimentos por horário, verificando a ordem crescente na renderização.

## 2. Shell reutilizável

- [x] 2.1 Implementar o componente `Sidebar` com os sete itens de navegação, estado ativo de Início e rótulos acessíveis, verificando que todos os itens aparecem no Dashboard.
- [x] 2.2 Implementar o componente `Topbar` com busca, notificações e perfil, verificando o placeholder exato "Buscar paciente, médico ou convênio..." e nomes acessíveis.
- [x] 2.3 Compor Sidebar e Topbar em um shell responsivo reutilizável, verificando que o conteúdo não fica encoberto em desktop e mobile.

## 3. Dashboard

- [x] 3.1 Implementar a saudação, resumo textual e data atual em português por extenso, verificando os textos e a formatação exibidos.
- [x] 3.2 Implementar o card "Total de pacientes hoje" com valor mockado e variação em relação a ontem, verificando o conteúdo e as cores do design system.
- [x] 3.3 Implementar a lista "Próximos atendimentos" com horário, paciente, médico, status e link "Ver Todos" para Agendamentos, verificando ordenação e badges.
- [x] 3.4 Aplicar a paleta, tipografia, transparências, raios de borda e espaçamentos do design system e do protótipo, verificando contraste e hierarquia visual.

## 4. Validação

- [x] 4.1 Executar `reflex compile --dry` e corrigir erros de componentes, estado ou rotas.
- [ ] 4.2 Verificar visualmente o Dashboard em viewport desktop e mobile, confirmando Sidebar, Topbar, card, lista e ausência de sobreposição ou overflow.
- [ ] 4.3 Confirmar que o login existente permanece inalterado e que não foi adicionado redirecionamento automático nesta change.
