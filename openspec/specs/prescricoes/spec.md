# Prescrições Specification

## Purpose
Permitir que médicos emitam e salvem documentos clínicos vinculados a pacientes de sua agenda, e que secretaria/administrador revisem os documentos, resultados e valores pendentes antes de encaminhá-los ao e-mail cadastrado.

## Requirements

### Requirement: Autorizar os perfis clínicos
A rota `/prescricoes` SHALL estar disponível para médico, secretaria e administrador, conforme as permissões do perfil. Médicos SHALL poder criar documentos. Secretaria e administrador SHALL poder consultar a lista e solicitar o envio por e-mail.

#### Scenario: Médico abre Prescrições
- **WHEN** um usuário médico autenticado abre `/prescricoes`
- **THEN** vê a página de prescrições

#### Scenario: Secretaria consulta documentos
- **WHEN** um usuário secretaria ou administrador abre `/prescricoes`
- **THEN** vê a lista de prescrições com paciente, médico, e-mail, resultado do exame e saldo do exame ainda não pago
- **AND** pode acionar o envio ao e-mail cadastrado do paciente

### Requirement: Limitar pacientes e agendamentos à agenda do médico
A página SHALL carregar a lista de pacientes pelo endpoint `/paciente` e SHALL disponibilizar para vínculo somente os agendamentos retornados pelo endpoint `/agendamento` para o médico autenticado. Para o paciente escolhido, SHALL carregar o e-mail cadastrado e disponibilizar apenas os agendamentos desse paciente.
O Xano SHALL autorizar o perfil Médico a ler `GET /paciente` e `GET /paciente/{paciente_id}`, preservando as restrições de escrita dos cadastros.

#### Scenario: Médico escolhe paciente de sua agenda
- **WHEN** o médico seleciona um paciente disponível em sua agenda
- **THEN** a página mostra o e-mail cadastrado e os agendamentos desse paciente

#### Scenario: Paciente sem agendamento disponível
- **WHEN** o médico seleciona um paciente que não possui agendamento vinculado a ele
- **THEN** a página mantém o paciente selecionado e explica que é preciso criar ou vincular um agendamento
- **AND** não permite enviar a prescrição até que um agendamento relacionado seja selecionado

#### Scenario: Prescrição sem exame prévio
- **WHEN** o médico possui um agendamento relacionado para o paciente
- **THEN** a página permite selecionar esse agendamento sem exigir um exame concluído

#### Scenario: Paciente sem e-mail
- **WHEN** o paciente não tem e-mail cadastrado
- **THEN** a página explica o problema e não permite enviar a prescrição

### Requirement: Salvar prescrição e enviar pela secretaria
A página SHALL enviar `paciente_id`, `medico_id`, `agendamento_id`, `tipo_doc` e `conteudo_doc` ao endpoint autenticado `POST /prescricoes`. Esse endpoint SHALL salvar a prescrição sem disparar e-mail. Um endpoint separado autenticado SHALL permitir à secretaria/administrador enviar a prescrição já gravada ao e-mail cadastrado, incluindo o resultado do exame e saldo pendente, se houver.

#### Scenario: Médico salva prescrição
- **WHEN** o médico salva uma prescrição válida para paciente da sua agenda e seleciona um agendamento
- **THEN** a página chama `POST /prescricoes` com os cinco campos aceitos pelo Xano
- **AND** informa que o documento foi salvo e está disponível para a secretaria

#### Scenario: Secretaria envia documento
- **WHEN** a secretaria envia uma prescrição salva para paciente com e-mail cadastrado
- **THEN** o Xano envia o conteúdo da prescrição, o resultado do exame e o saldo pendente do exame, se houver
- **AND** só marca o e-mail como enviado após confirmação do serviço de e-mail

#### Scenario: API rejeita o envio
- **WHEN** o Xano retorna um erro ou não confirma o envio
- **THEN** a página mostra a mensagem de erro sem informar sucesso

### Requirement: Filtrar e apresentar prescrições
`GET /prescricoes` SHALL aceitar `paciente_id` como inteiro opcional e, quando enviado, filtrar pela coluna `prescricao.paciente_id`. O endpoint SHALL devolver os nomes do paciente e do médico e os dados do agendamento/exame usados para a revisão da secretaria. A consulta da secretaria deve listar documentos da clínica; a consulta do médico deve ficar limitada ao próprio médico.

#### Scenario: Médico consulta histórico
- **WHEN** um paciente é selecionado
- **THEN** a página carrega e exibe o histórico retornado pelo endpoint para aquele `paciente_id`
- **AND** mostra a quantidade de documentos no histórico como documentos enviados para o paciente selecionado

#### Scenario: Secretaria atualiza status após envio
- **WHEN** o Xano confirma o envio de um documento
- **THEN** a página recarrega o histórico do paciente
- **AND** atualiza a situação de e-mail do documento
