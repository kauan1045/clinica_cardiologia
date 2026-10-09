## MODIFIED Requirements

### Requirement: Validar o preenchimento localmente
O formulário SHALL detectar quando Usuário ou senha estão vazios antes de chamar a API de autenticação e, quando preenchido, SHALL autenticar na API do Xano.

#### Scenario: Usuário envia formulário incompleto
- **WHEN** o usuário aciona a ação de entrada sem Usuário ou sem senha preenchidos
- **THEN** a página exibe feedback de validação compreensível próximo ao formulário
- **AND** não ocorre chamada à API, redirecionamento nem concessão de acesso

#### Scenario: Usuário envia formulário preenchido
- **WHEN** o usuário fornece um Usuário não vazio e uma senha não vazia
- **THEN** o valor de Usuário e a senha são enviados à API de autenticação nos campos `email` e `senha`
- **AND** o botão de entrada indica carregamento até a resposta
- **AND** em caso de sucesso o usuário é levado ao Início; em caso de falha a página exibe a mensagem de erro próximo ao formulário
