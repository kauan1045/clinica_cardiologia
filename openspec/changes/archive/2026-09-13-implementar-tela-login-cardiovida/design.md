# Design: Implementar tela de login CardioVida

## Contexto atual

A aplicação é um scaffold mínimo em Reflex 0.9.11. A função `index()` em `ProjetoCl_nicaCardiologia/ProjetoCl_nicaCardiologia.py` renderizava um container com seletor de tema, título de boas-vindas, texto sobre o arquivo e link para a documentação. Não há rotas adicionais ou camada de autenticação. O logo `assets/bi_heart-pulse.svg` foi disponibilizado nesta implementação.

## Abordagem

1. Reestruturar `index()` como uma composição de página de login, preservando `app.add_page(index)` e o ponto de entrada atual.
2. Expandir `State` com valores controlados para Usuário, senha, opção de lembrar e mensagem de erro/sucesso local.
3. Criar eventos Reflex para submeter o formulário e limpar ou exibir feedback sem simular autenticação real.
4. Usar componentes nativos `rx.form`, `rx.input`, `rx.checkbox`, `rx.button`, `rx.text`, `rx.link` e containers/layouts Reflex, com responsividade por propriedades de estilo.
5. Usar `assets/bi_heart-pulse.svg` como logo/ícone da tela, junto de uma direção visual clínica e acolhedora baseada na paleta compartilhada documentada em `openspec/design-system.md`.
6. Manter o seletor de modo de cor apenas se ele não prejudicar a legibilidade e garantir contraste adequado nos dois modos.

## Fluxo de interação

- O usuário preenche Usuário e senha e aciona `Entrar`.
- Enquanto a autenticação não existir, o submit valida apenas os campos obrigatórios e exibe uma mensagem orientando que o acesso será conectado em uma etapa posterior; não deve conceder acesso nem redirecionar.
- Usuário vazio ou senha vazia produzem feedback próximo ao formulário e preservam os valores digitados quando apropriado.
- `Lembrar de mim` altera apenas o estado local nesta mudança.
- O link `Esqueceu sua senha?` permanece uma ação de apresentação ou destino não implementado claramente indicado, sem fingir que existe um fluxo funcional.

## Paleta visual compartilhada

Toda a aplicação deve usar a paleta documentada em `openspec/design-system.md`, e não apenas esta tela:

- Azul Cobalto `#05589F`: fonte.
- Azul Médio `#6A9ECC`: fonte.
- Verde Limão `#DCED6D`: somente ícones que sinalizam informações importantes.
- Azul Bebê `#A7D8F0`.
- Verde `#88E0C1`.
- Verde Sálvia `#4A7A69`: logo, cor secundária e fonte.
- Vermelho de Status `#ED6D6D`: status e alertas.
- Branco `#FFFFFF`.

## Estados e acessibilidade

- Campos com labels visíveis, placeholders auxiliares e tipo de entrada adequado.
- Botão principal com estado desabilitado somente quando a validação local exigir, sem bloquear a correção dos campos.
- Mensagens de erro e confirmação com texto claro e região visual associada ao formulário.
- Layout responsivo para telas estreitas, sem depender de largura fixa.
- Foco, contraste e alvos de interação devem permanecer utilizáveis em desktop e mobile.

## Limites técnicos

- Não adicionar dependências externas para autenticação ou componentes.
- Não criar banco, API ou modelos nesta mudança.
- Validar a compilação da página usando o fluxo de processo Reflex do projeto.
