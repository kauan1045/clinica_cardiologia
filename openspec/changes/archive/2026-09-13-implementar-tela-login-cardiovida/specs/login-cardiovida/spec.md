# Spec: Login CardioVida

## ADDED Requirements

### Requirement: Exibir uma entrada de login da CardioVida
A página inicial deve exibir uma tela de login identificada como CardioVida, com composição responsiva e hierarquia visual adequada para o acesso à clínica, em vez do conteúdo inicial padrão do Reflex.

#### Scenario: Usuário abre a aplicação
- **WHEN** a aplicação é carregada na rota inicial
- **THEN** o usuário vê a marca ou nome CardioVida, uma explicação breve do acesso e um formulário de login sem conteúdo de demonstração do Reflex
- **AND** o layout permanece utilizável em viewport desktop e mobile

### Requirement: Coletar credenciais com campos acessíveis
O formulário deve oferecer campos identificados para Usuário e senha, além de uma opção de lembrar o acesso e uma ação principal de entrada.

#### Scenario: Usuário visualiza o formulário
- **WHEN** o formulário é exibido
- **THEN** cada campo possui label visível, tipo de entrada apropriado e valor controlado pelo estado Reflex
- **AND** a senha não é exibida em texto aberto
- **AND** a ação principal informa claramente que inicia o acesso

### Requirement: Validar o preenchimento localmente
O formulário deve detectar quando Usuário ou senha estão vazios antes de qualquer futura integração de autenticação.

#### Scenario: Usuário envia formulário incompleto
- **WHEN** o usuário aciona a ação de entrada sem Usuário ou sem senha preenchidos
- **THEN** a página exibe feedback de validação compreensível próximo ao formulário
- **AND** não ocorre redirecionamento nem concessão de acesso

#### Scenario: Usuário envia formulário preenchido
- **WHEN** o usuário fornece um Usuário não vazio e uma senha não vazia
- **THEN** a página exibe um feedback explícito de que a integração de autenticação ainda será conectada
- **AND** os dados não são persistidos nem enviados a um serviço externo

### Requirement: Oferecer extensões auxiliares sem simular fluxos
A tela deve apresentar a opção de recuperação de senha de forma distinguível, sem afirmar que esse fluxo já está implementado.

#### Scenario: Usuário seleciona uma opção auxiliar
- **WHEN** o usuário seleciona "Esqueceu sua senha?"
- **THEN** a interface mantém um destino ou estado de extensão claramente definido
- **AND** não apresenta a operação de recuperação como concluída
