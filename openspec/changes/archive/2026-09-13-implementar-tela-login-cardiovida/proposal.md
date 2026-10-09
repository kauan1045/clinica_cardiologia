# Proposal: Implementar tela de login CardioVida

## What
Criar a primeira tela de login da aplicação CardioVida, substituindo a página inicial padrão do Reflex por uma experiência visual de acesso para pacientes e equipe da clínica.

A tela deverá apresentar a identidade CardioVida, o logo/ícone `assets/bi_heart-pulse.svg`, campos de Usuário e senha, ação principal de entrada, opção de lembrar o acesso e o link `Esqueceu sua senha?`. O fluxo de autenticação real não faz parte desta mudança; a interface deve estar preparada para conectá-lo posteriormente.

## Why
A aplicação atualmente exibe o conteúdo inicial de demonstração do Reflex e não oferece um ponto de entrada reconhecível para usuários da clínica. Uma tela de login consistente estabelece a base da experiência do produto e permite validar a hierarquia visual e os estados básicos do formulário antes da integração com autenticação.

## Scope
- Substituir a página inicial padrão por uma tela de login responsiva.
- Adicionar identidade visual, logo, campos, ações e estados de validação locais do formulário.
- Aplicar a paleta compartilhada documentada em `openspec/design-system.md`.
- Manter a implementação compatível com o app Reflex existente.
- Usar textos e interface em português.

## Non-goals
- Autenticação contra banco de dados, API ou provedor externo.
- Persistência de sessão ou autorização por perfil.
- Implementação do fluxo de recuperação de senha.
- Alterações no modelo de dados da clínica.
