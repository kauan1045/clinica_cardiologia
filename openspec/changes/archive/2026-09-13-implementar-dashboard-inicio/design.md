## Context

A aplicação Reflex atual concentra a tela de login em um único módulo Python e ainda não possui layout autenticado, rotas de negócio ou componentes de navegação. O design system CardioVida já define Inter para a interface, Poppins para a marca, Azul Cobalto `#05589F`, Azul Médio `#6A9ECC`, Verde Sálvia `#4A7A69`, Verde `#88E0C1`, Verde Limão `#DCED6D`, Azul Bebê `#A7D8F0` e Branco `#FFFFFF`.

## Goals / Non-Goals

**Goals:**

- Introduzir um shell de aplicação reutilizável com `Sidebar` e `Topbar`.
- Criar uma composição de Dashboard responsiva, escaneável e visualmente alinhada ao protótipo Figma.
- Manter os dados mockados desacoplados da apresentação e prontos para substituição por serviço real.
- Preservar o login atual e deixar explícito que o Dashboard é uma tela mockada independente nesta change.

**Non-Goals:**

- Implementar autenticação, autorização ou redirecionamento após login.
- Criar backend, banco de dados, API ou persistência de pacientes/agendamentos.
- Implementar as telas de Pacientes, Agendamentos, Médicos, Convênio, Exames ou Configurações.

## Decisions

### Componentes compartilhados

Criar `Sidebar` e `Topbar` como funções de componente independentes, recebendo estado/props de apresentação quando necessário. A página do Dashboard compõe esses componentes em um shell comum, evitando que a navegação fique presa a uma tela específica.

Alternativa considerada: manter toda a navegação dentro de `index()`. Foi rejeitada porque dificultaria a reutilização e faria cada tela futura duplicar o shell.

### Dados mockados tipados

Manter listas e registros mockados em estruturas Python separadas da função visual, com campos como `time`, `patient`, `doctor` e `status`. A apresentação usa esses campos por iteração e ordenação crescente pelo horário.

Alternativa considerada: inserir os dados diretamente nos componentes. Foi rejeitada porque tornaria a futura troca por API mais invasiva.

### Navegação futura

Os itens da Sidebar e o link `Ver Todos` devem ter destinos de rota ou pontos de extensão claramente nomeados, mesmo quando as telas de destino ainda não existirem. O Dashboard não deve simular que essas áreas já estão prontas.

### Responsividade

Em desktop, a Sidebar permanece fixa/visível e o conteúdo ocupa o restante da tela. Em viewport estreita, a navegação deve colapsar ou reorganizar-se sem sobrepor o conteúdo; o Dashboard deve continuar legível e permitir acesso aos itens principais.

### Estilo

Usar fundo claro, Sidebar em Azul Bebê translúcido, cards em Verde com transparência e cantos próximos de `20px`. Badges `confirmado` usam Verde translúcido e `aguardando` usa Verde Limão translúcido. Ícones devem ter tooltips ou rótulos acessíveis quando sua função não for óbvia.

## Risks / Trade-offs

- [Risk] Rotas de telas futuras ainda não existem. -> Mitigation: manter os destinos como extensões explícitas e não apresentar navegação inexistente como concluída.
- [Risk] Dados mockados podem parecer reais. -> Mitigation: isolar a fonte mockada e manter o escopo sem persistência ou chamadas externas.
- [Risk] Muitos elementos no Dashboard podem prejudicar a leitura em telas menores. -> Mitigation: usar layout responsivo, hierarquia de conteúdo e validação visual em desktop e mobile.

## Migration Plan

1. Adicionar o shell e a página Dashboard sem remover a tela de login.
2. Validar compilação e renderização com os dados mockados.
3. Quando autenticação e backend existirem, substituir a fonte mockada e conectar a rota pós-login em uma change separada.

## Open Questions

- O nome exibido na saudação deve permanecer mockado como um nome fixo até a integração de sessão real.
