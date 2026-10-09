## Purpose

A capability Agendamento permite à equipe da clínica visualizar a agenda do dia em uma grade por horário, com atendimentos e intervalos, reaproveitando a navegação e o layout das demais telas autenticadas.

## ADDED Requirements

### Requirement: Reaproveitar navegação e layout compartilhados
A tela Agendamentos SHALL reaproveitar os componentes `Sidebar` e `Topbar` do Dashboard, sem duplicar código, destacando o item "Agendamentos" como ativo no menu lateral, e SHALL usar o mesmo layout de página da tela Pacientes (fundo, largura máxima de conteúdo, card branco e estilo de título).

#### Scenario: Usuário acessa a tela Agendamentos
- **WHEN** a tela Agendamentos é exibida
- **THEN** o usuário vê a mesma barra superior e o mesmo menu lateral do Dashboard e de Pacientes
- **AND** o item "Agendamentos" aparece visualmente destacado como ativo
- **AND** a grade da agenda aparece em um card branco sobre o mesmo fundo usado em Pacientes

### Requirement: Exibir título e seletor de visualização
A tela Agendamentos SHALL exibir o título "Agendamentos", com o mesmo estilo do título da tela Pacientes, e um seletor com as opções "Dia", "Semana" e "Mês", com a opção "Dia" selecionada por padrão.

#### Scenario: Usuário abre a tela
- **WHEN** a tela Agendamentos é carregada
- **THEN** o usuário vê o título "Agendamentos"
- **AND** vê o seletor com as opções "Dia", "Semana" e "Mês"
- **AND** a opção "Dia" aparece destacada como selecionada, com fundo mais escuro que as demais

#### Scenario: Usuário troca a visualização
- **WHEN** o usuário clica em "Semana" ou "Mês"
- **THEN** o destaque de selecionada passa para a opção clicada
- **AND** a grade diária exibida permanece a mesma

### Requirement: Exibir a data da agenda
A tela Agendamentos SHALL exibir, em uma barra abaixo do título, a data da agenda por extenso no formato "{dia da semana abreviado}, {dia} de {mês} de {ano}", gerada a partir de uma data mantida no estado, com o dia da semana calculado corretamente.

#### Scenario: Usuário consulta a data da agenda
- **WHEN** a agenda do dia 26/09/2026 é exibida
- **THEN** a barra de data mostra o texto "Sáb, 26 de setembro de 2026" em azul médio `#6A9ECC`
- **AND** o texto não é fixo: muda conforme a data mantida no estado

### Requirement: Exibir grade de horários
A tela Agendamentos SHALL exibir uma coluna de horários de 30 em 30 minutos, de 08:00 a 14:30, em azul `#05589F`, com o mesmo estilo de texto do nome do paciente na tabela de Pacientes, alinhada aos blocos da agenda.

#### Scenario: Usuário consulta a grade de horários
- **WHEN** a agenda do dia é exibida
- **THEN** o usuário vê os horários 08:00, 08:30, 09:00, 09:30, 10:00, 10:30, 11:00, 11:30, 12:00, 12:30, 13:00, 13:30, 14:00 e 14:30 em ordem crescente, de cima para baixo
- **AND** horários sem atendimento permanecem sem bloco ao lado

### Requirement: Exibir atendimentos na agenda
Cada atendimento SHALL ser exibido como um bloco em forma de pílula ao lado do seu horário, contendo em duas linhas o nome do paciente e o nome do médico com a especialidade ou tipo do atendimento.

#### Scenario: Usuário consulta os atendimentos do dia
- **WHEN** existem atendimentos na agenda
- **THEN** às 08:00 o usuário vê "Daiane Santos" e "Dr.Marcelo Cavalcante Junior - Cardiologista"
- **AND** às 09:00 vê "Iuri Souza" e "Dra. Juliana Almeida - Cardiologista"
- **AND** às 11:00 vê "Kauan Mendes" e "Dr.Felipe Costa - Ecocardiograma"
- **AND** às 14:00 vê "Rhonalds Medrade" e "Dra. Juliana Almeida - Retorno"
- **AND** cada bloco tem fundo translúcido (azul médio `#6A9ECC` ou verde `#88E0C1`, a 30% de opacidade), cantos arredondados e texto em `#05589F`
- **AND** o texto do bloco não é cortado, mesmo em janelas menores

### Requirement: Exibir intervalos na agenda
Cada intervalo SHALL ser exibido como um bloco em forma de pílula com o texto "Intervalo" e fundo verde-limão `#DCED6D` translúcido.

#### Scenario: Usuário consulta os intervalos
- **WHEN** a agenda do dia possui intervalos
- **THEN** o usuário vê quatro blocos "Intervalo" nos horários 12:00, 12:30, 13:00 e 13:30
- **AND** cada bloco tem fundo `#DCED6D` a 30% de opacidade e cantos arredondados

### Requirement: Paginar a agenda
A tela Agendamentos SHALL exibir, abaixo da grade de horários e dentro do card, uma paginação com seta anterior, quatro números de página (1, 2, 3, 4) em caixas com borda azul `#05589F` e seta próxima.

#### Scenario: Usuário visualiza a paginação
- **WHEN** a tela Agendamentos é carregada
- **THEN** o usuário vê a seta anterior, as caixas numeradas de 1 a 4 e a seta próxima, abaixo da grade
- **AND** cada caixa numérica tem borda de 1px `#05589F` e fundo cinza translúcido

#### Scenario: Usuário navega pela paginação
- **WHEN** o usuário clica em um número ou nas setas
- **THEN** a página atual do estado muda, limitada de 1 a 4
- **AND** a grade diária exibida permanece a mesma

### Requirement: Seguir a escala e a largura das telas existentes
Os tamanhos de texto, espaçamentos e componentes da tela Agendamentos SHALL seguir a escala das telas Dashboard e Pacientes, e o conteúdo SHALL ocupar a largura disponível até o mesmo máximo usado em Pacientes, sem rolagem horizontal.

#### Scenario: Usuário abre a tela em larguras comuns de monitor
- **WHEN** a largura da janela é 1280px, 1366px ou 1920px
- **THEN** não há rolagem horizontal
- **AND** o conteúdo ocupa a mesma largura máxima da tela Pacientes
- **AND** o seletor Dia/Semana/Mês e a barra da data aparecem inteiros

#### Scenario: Usuário reduz a largura da janela
- **WHEN** a janela fica mais estreita que a largura máxima do conteúdo
- **THEN** o conteúdo encolhe junto com a janela
- **AND** nenhum texto ou componente do conteúdo é cortado

### Requirement: Usar dados mockados substituíveis
Os dados de agenda exibidos SHALL vir de dados mockados mantidos separados da composição visual, carregados por funções isoladas, com campos compatíveis com uma futura fonte de dados real.

#### Scenario: Fonte de agendamentos é substituída
- **WHEN** a equipe conectar uma API futuramente
- **THEN** a origem dos atendimentos e intervalos pode ser substituída sem alterar o contrato visual da grade
- **AND** os campos de horário, paciente, médico, tipo e cor do bloco continuam disponíveis para a tela
