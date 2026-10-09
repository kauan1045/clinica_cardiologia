# dashboard-inicio Specification

## Purpose
O Dashboard de Início oferece à equipe da clínica uma visão operacional rápida do dia e estabelece a navegação compartilhada para as demais áreas do CardioVida.

## Requirements

### Requirement: Disponibilizar navegação lateral reutilizável
O Dashboard SHALL exibir um menu lateral com os itens Início, Pacientes, Agendamentos, Prescrições, Médicos, Convênio e Exames permitidos ao perfil do usuário, conforme o mapa de permissões, sem o item "Configurações", e um botão "Sair" fixo no rodapé do menu, reutilizável por outras telas autenticadas, cada uma podendo indicar qual item está ativo.

#### Scenario: Usuário acessa o Dashboard
- **WHEN** a tela inicial autenticada é exibida para um usuário Administrador ou secretaria
- **THEN** o usuário vê todos os itens de navegação lateral com seus respectivos nomes e ícones
- **AND** o item Início aparece visualmente destacado como ativo
- **AND** os demais itens permanecem disponíveis como destinos de navegação conforme as permissões do perfil
- **AND** o menu não exibe o item "Configurações"

#### Scenario: Médico visualiza o menu
- **WHEN** um usuário com perfil medico vê o menu lateral
- **THEN** o menu exibe somente os itens "Agendamentos" e "Prescrições", além do botão "Sair"

#### Scenario: Outra tela autenticada reutiliza o menu lateral
- **WHEN** uma tela diferente do Dashboard reutiliza o componente de navegação lateral
- **THEN** o item correspondente àquela tela aparece visualmente destacado como ativo
- **AND** o item Início deixa de aparecer destacado

#### Scenario: Menu lateral permanece fixo ao rolar a página
- **WHEN** o conteúdo da tela é mais alto que a janela e o usuário rola a página
- **THEN** o menu lateral mantém a altura da janela e permanece fixo no topo, sem rolar junto com o conteúdo
- **AND** o botão "Sair" continua visível no rodapé do menu

#### Scenario: Usuário visualiza o botão Sair
- **WHEN** qualquer tela que reutiliza o menu lateral é exibida
- **THEN** o botão "Sair", com ícone de logout, aparece no rodapé do menu lateral, na mesma escala e estilo dos itens do menu
- **AND** ao passar o mouse sobre o botão, o cursor vira pointer e o fundo do botão reage com o mesmo destaque discreto usado nos itens do menu

### Requirement: Disponibilizar barra superior reutilizável
O Dashboard SHALL exibir uma barra superior com busca, notificações e acesso ao perfil, e o controle de perfil SHALL exibir o nome do usuário autenticado.

#### Scenario: Usuário visualiza a barra superior
- **WHEN** o Dashboard é carregado
- **THEN** a barra superior exibe o campo com placeholder "Buscar paciente, médico ou convênio..."
- **AND** exibe um controle de notificações e um controle de perfil
- **AND** os controles têm nomes acessíveis e não dependem apenas de ícones para comunicar sua função

#### Scenario: Controle de perfil mostra o usuário autenticado
- **WHEN** uma tela autenticada é exibida
- **THEN** o controle de perfil exibe o nome (`name`) do usuário autenticado, ou o email quando não houver nome
- **AND** exibe "Usuário" se o perfil ainda não estiver disponível

### Requirement: Exibir resumo do dia
O Dashboard SHALL exibir uma saudação ao usuário, um texto de resumo, a data atual por extenso e o indicador "Total de pacientes hoje".

#### Scenario: Usuário abre o resumo diário
- **WHEN** a tela é carregada
- **THEN** o usuário vê uma saudação no formato "Olá, {nome do usuário}"
- **AND** vê o texto "Aqui está um resumo do que acontece hoje na clínica"
- **AND** vê a data atual em português por extenso, incluindo dia da semana, dia, mês e ano
- **AND** vê o total mockado de pacientes do dia e a variação em relação ao dia anterior

### Requirement: Listar próximos atendimentos ordenados
O Dashboard SHALL exibir a seção "Próximos atendimentos" com atendimentos mockados ordenados pelo horário.

#### Scenario: Usuário consulta os próximos atendimentos
- **WHEN** existem atendimentos mockados para o dia
- **THEN** cada item exibe horário, nome do paciente e médico responsável
- **AND** cada item exibe o status "confirmado" ou "aguardando"
- **AND** os itens aparecem em ordem crescente de horário
- **AND** a seção exibe o link "Ver Todos" apontando para a área de Agendamentos

### Requirement: Separar dados de apresentação
Os dados mockados do Dashboard SHALL ser mantidos em uma estrutura separada da composição visual, com campos compatíveis com uma futura fonte de dados real.

#### Scenario: Fonte de atendimentos é substituída
- **WHEN** a equipe conectar uma API ou banco de dados futuramente
- **THEN** a origem dos pacientes e atendimentos pode ser substituída sem alterar o contrato visual das seções
- **AND** os campos de horário, paciente, médico e status continuam disponíveis para a tela

### Requirement: Encerrar a sessão pelo botão Sair
O botão "Sair" do menu lateral SHALL apagar o token de autenticação e o perfil do usuário, limpar o estado de login e redirecionar o usuário para a tela de Login, com a lógica isolada em um único evento de estado.

#### Scenario: Usuário clica em Sair
- **WHEN** o usuário clica no botão "Sair" em qualquer tela autenticada
- **THEN** o token, o perfil e o estado de login (usuário, senha, opção "lembrar-me" e mensagem de erro) são apagados
- **AND** o usuário é redirecionado para a tela de Login
- **AND** os campos da tela de Login aparecem vazios

### Requirement: Filtrar e contabilizar indicadores por período
O Dashboard SHALL iniciar com o primeiro dia do mês até a data atual, permitir escolher as datas inicial e final e enviar esse intervalo a `GET /dashboard`. Consultas, exames, laudos enviados, faturamento, novos pacientes, repasse e faturamento por convênio SHALL refletir o intervalo selecionado. A seção de próximos atendimentos continua mostrando apenas os atendimentos do dia atual.

#### Scenario: Abrir o Dashboard
- **WHEN** o administrador abre o Dashboard
- **THEN** os indicadores iniciam filtrados do primeiro dia do mês atual até hoje

#### Scenario: Aplicar um período
- **WHEN** o administrador escolhe uma data inicial e final válidas e aplica o filtro
- **THEN** o Dashboard envia as datas como limites do período para `GET /dashboard`
- **AND** todos os cartões e totais por convênio refletem o período selecionado
- **AND** a agenda operacional continua mostrando os atendimentos de hoje

#### Scenario: Informar um período inválido
- **WHEN** a data final é anterior à data inicial ou uma data está ausente
- **THEN** o Dashboard informa o erro sem substituir os últimos indicadores válidos

### Requirement: Exportar indicadores em CSV
O Dashboard SHALL oferecer a exportação dos indicadores exibidos e do período selecionado em CSV UTF-8 com BOM, usando ponto e vírgula como separador para compatibilidade com planilhas em português.

#### Scenario: Exportar o Dashboard
- **WHEN** o administrador clica em "Exportar CSV"
- **THEN** o arquivo contém o período, contagens, valores financeiros e totais por convênio atualmente exibidos

### Requirement: Exibir valores financeiros na unidade correta
O Dashboard SHALL tratar `faturamento_periodo` e os totais por convênio recebidos de `/dashboard` como centavos, conforme o campo `Agendamento.valor_pago`, e SHALL converter o valor para reais antes da exibição, com duas casas decimais e separadores pt-BR. O indicador "Exames no período" SHALL continuar exibindo a quantidade de agendamentos com exame, não o valor do catálogo.

Cada item de `faturamento_por_convenio` SHALL incluir o nome do convênio e o total em centavos. O Xano SHALL agrupar os registros de `Agendamento` pelo campo `convenio_id`, somar `valor_pago` e associar o nome da tabela `Convenio`. Se um item não trouxer o total, o Dashboard SHALL identificar que o valor não foi retornado pela API e SHALL orientar a revisão do agregado no Xano, sem apresentar o nome isolado como se fosse um total válido.

#### Scenario: Formatar faturamento
- **WHEN** o Xano devolve `24000` centavos de faturamento do período
- **THEN** o Dashboard exibe `R$ 240,00`

#### Scenario: Exibir total de exames
- **WHEN** o Xano devolve dois agendamentos com exame no intervalo selecionado
- **THEN** o cartão "Exames no período" exibe `2`

### Requirement: Mostrar pagamentos pendentes ao administrador
O Dashboard SHALL mostrar ao administrador os pacientes com pagamento pendente no período escolhido, incluindo data do atendimento, forma de pagamento e convênio, quando houver. A forma deve ser apresentada como Dinheiro, Cartão ou Convênio. Valores de `Agendamento.valor_pago` devem ser identificados como já pagos/registrados, pois não representam necessariamente o saldo em aberto.

#### Scenario: Administrador consulta pagamentos pendentes
- **WHEN** o administrador abre o Dashboard ou aplica um período
- **THEN** vê a contagem e a lista de pacientes com `status_pagamento` pendente
- **AND** cada item informa se o pagamento está previsto em dinheiro, cartão ou convênio
- **AND** os agendamentos cancelados não aparecem nessa lista
- **AND** a exportação CSV inclui a contagem e os dados apresentados

#### Scenario: Período sem pagamentos pendentes
- **WHEN** o intervalo escolhido não contém pagamentos pendentes
- **THEN** o Dashboard informa que não há pagamentos pendentes no período

### Requirement: Exibir contador de laudos enviados para administração
O Dashboard SHALL exibir ao perfil administrador uma métrica de laudos/documentos cujo e-mail foi confirmado pelo SendGrid, recebida como `total_laudos_enviados` em `GET /dashboard`. A API SHALL contar apenas os envios confirmados, sem contar documentos gravados cujo envio falhou.

#### Scenario: Xano retorna a contagem confirmada
- **WHEN** o Xano retorna `total_laudos_enviados` em `GET /dashboard`
- **THEN** o Dashboard do administrador exibe essa contagem
- **AND** uma falha no SendGrid não aumenta o contador
