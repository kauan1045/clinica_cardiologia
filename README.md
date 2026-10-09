# CardioVida — Gestão de Clínica Cardiológica

Sistema web para apoiar a rotina de uma clínica cardiológica. A aplicação usa [Reflex](https://reflex.dev/) para a interface e comunicação com os serviços de backend da clínica via API Xano.

## Funcionalidades

- Login e controle de acesso por perfil: administrador, secretaria e médico.
- Painel, cadastro de pacientes e médicos.
- Agendamentos, exames e convênios.
- Prescrições médicas e envio por e-mail.
- Integração com APIs externas configuradas pelo ambiente.

## Acesso de demonstração

Use a conta de demonstração abaixo, destinada a testes sem dados reais:

- **E-mail:** `admin3@admin.com`
- **Senha:** `admin12345`

Essa conta precisa existir e estar habilitada no backend configurado para que o login funcione.

## Executar localmente

Requisitos: Python 3.10 ou superior e Node.js compatível com a versão instalada pelo Reflex.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
reflex init
reflex run
```

Configure no `.env` os endereços de API usados pelo sistema. Não publique esse arquivo nem coloque tokens ou senhas reais no Git.

### Variáveis de ambiente

| Variável | Uso |
| --- | --- |
| `XANO_API_URL` | URL base da API principal do Xano. |
| `XANO_PASSWORD_RESET_API_URL` | URL da API de redefinição de senha. |

As variáveis `XANO_TEST_*` do `.env.example` são destinadas somente a testes locais.

## Publicação

O projeto usa Reflex: os manipuladores Python e o estado da aplicação são executados no servidor, e a interface se comunica com o backend por WebSocket. Configure os dois endereços de API como variáveis de ambiente de produção antes de publicar e use HTTPS.

Para publicar na Vercel, importe o repositório `kauan1045/clinica_cardiologia` na equipe autorizada, configure as variáveis acima e faça o deploy. Confirme no build da Vercel que o runtime mantém disponível o backend Reflex e sua conexão WebSocket; publicar apenas os arquivos estáticos não disponibiliza o sistema completo. Se o runtime escolhido não suportar o backend Reflex, hospede o backend em um serviço compatível com WebSocket e configure o frontend para apontar para ele conforme a documentação de hospedagem do Reflex.

## Erros de API

As respostas exibidas na interface usam mensagens amigáveis e genéricas. Detalhes técnicos e mensagens internas retornadas pelo provedor não devem ser exibidos ao usuário final.
