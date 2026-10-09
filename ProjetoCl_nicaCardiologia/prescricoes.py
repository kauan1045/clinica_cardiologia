"""Emissão de prescrições integradas aos endpoints privados do Xano."""

import asyncio
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

import reflex as rx

from ProjetoCl_nicaCardiologia import api
from ProjetoCl_nicaCardiologia.auth import AuthState, tem_permissao
from ProjetoCl_nicaCardiologia.dashboard import Sidebar, Topbar


TIPOS_DOCUMENTO = ("Prescrição médica", "Receita médica", "Atestado médico")


def _extrair_lista(data: Any, chaves: tuple[str, ...]) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for chave in chaves:
            valor = data.get(chave)
            if isinstance(valor, list):
                return [item for item in valor if isinstance(item, dict)]
        for chave in ("data", "result", "results"):
            valor = data.get(chave)
            if isinstance(valor, dict):
                return _extrair_lista(valor, chaves)
    raise api.ApiError(api.UNEXPECTED_RESPONSE_MESSAGE)


def _extrair_registro(data: Any) -> dict[str, Any]:
    """Aceita o registro direto ou envolvido pelas respostas usuais do Xano."""
    atual = data
    for _ in range(4):
        if not isinstance(atual, dict):
            return {}
        relacionado = next(
            (
                atual[chave]
                for chave in ("paciente", "Paciente", "patient", "data", "result")
                if isinstance(atual.get(chave), dict)
            ),
            None,
        )
        if relacionado is None:
            return atual
        atual = relacionado
    return atual if isinstance(atual, dict) else {}


def _texto(valor: Any, padrao: str = "") -> str:
    if isinstance(valor, dict):
        for chave in ("nome", "name", "email", "titulo", "id"):
            if valor.get(chave):
                return str(valor[chave]).strip()
        return ""
    return str(valor).strip() if valor is not None else padrao


def _data_formatada(valor: Any) -> str:
    try:
        if isinstance(valor, (int, float)) and not isinstance(valor, bool):
            segundos = valor / 1000 if abs(valor) > 10_000_000_000 else valor
            instante = datetime.fromtimestamp(segundos).astimezone()
        elif isinstance(valor, str) and valor.strip():
            bruto = valor.strip()
            if bruto.isdigit():
                return _data_formatada(int(bruto))
            instante = datetime.fromisoformat(bruto.replace("Z", "+00:00"))
            instante = instante.astimezone() if instante.tzinfo else instante.astimezone()
        else:
            return "Data não informada"
        return instante.strftime("%d/%m/%Y às %H:%M")
    except (ValueError, OverflowError, OSError):
        return _texto(valor, "Data não informada")


def _normalizar_prescricao(item: dict[str, Any]) -> dict[str, str]:
    tipo = _texto(item.get("tipo_doc") or item.get("tipo_documento") or item.get("tipo"), "Prescrição médica")
    conteudo = _texto(
        item.get("conteudo_doc") or item.get("conteudo") or item.get("descricao") or item.get("texto"),
        "Conteúdo não informado.",
    )
    criado = item.get("created_at") or item.get("data_hora") or item.get("data")
    email_enviado = item.get("email_enviado")
    enviado_em = item.get("email_enviado_em") or item.get("enviado_em")
    status_email = _texto(item.get("status_email") or item.get("email_status")).casefold()
    if (
        email_enviado is True
        or str(email_enviado).casefold() in ("true", "1", "enviado", "sent")
        or bool(enviado_em)
    ):
        status_email = "enviado"
    elif status_email not in ("enviado", "sent"):
        status_email = "pendente"
    paciente = next(
        (item[chave] for chave in ("paciente", "Paciente", "patient") if isinstance(item.get(chave), dict)),
        {},
    )
    medico = next(
        (item[chave] for chave in ("medico", "Medico", "Médico", "doctor") if isinstance(item.get(chave), dict)),
        {},
    )
    agendamento = next(
        (item[chave] for chave in ("agendamento", "Agendamento", "appointment") if isinstance(item.get(chave), dict)),
        {},
    )
    exame = next(
        (agendamento[chave] for chave in ("exame", "Exame", "exam") if isinstance(agendamento.get(chave), dict)),
        {},
    )
    paciente_id = _texto(item.get("paciente_id") or paciente.get("id") or paciente.get("paciente_id"))
    paciente_nome = _texto(
        item.get("paciente_nome") or item.get("nome_paciente") or paciente.get("nome") or paciente.get("name"),
        f"Paciente #{paciente_id}" if paciente_id else "Paciente não informado",
    )
    paciente_email = _texto(item.get("paciente_email") or paciente.get("email"))
    medico_nome = _texto(
        item.get("medico_nome") or item.get("nome_medico") or medico.get("nome") or medico.get("name"),
        "Médico não informado",
    )
    resultado_exame = _texto(
        item.get("resultado_exame") or item.get("resultado") or agendamento.get("resultado") or agendamento.get("resultado_exame"),
        "Resultado ainda não informado.",
    )
    status_pagamento = _texto(
        agendamento.get("status_pagamento") or item.get("status_pagamento"), "Pendente"
    ).casefold()
    valor_pendente = "Sem valor pendente"
    valor_exame = (
        exame.get("valor_do_exame_por_repasse")
        or agendamento.get("valor_exame")
        or item.get("valor_exame")
        or item.get("valor_do_exame_por_repasse")
    )
    valor_pago = agendamento.get("valor_pago", item.get("valor_pago", 0))
    pago = status_pagamento in ("pago", "paga", "quitado", "quitada", "paid")
    try:
        if not pago and valor_exame is not None:
            total = Decimal(str(valor_exame).replace(",", "."))
            pago_decimal = Decimal(str(valor_pago or 0).replace(",", ".")) / Decimal("100")
            pendente = max(Decimal("0"), total - pago_decimal)
            if pendente > 0:
                arredondado = pendente.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                valor_pendente = "R$ " + f"{arredondado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (InvalidOperation, ValueError, TypeError):
        valor_pendente = "Valor do exame não informado"
    return {
        "id": _texto(item.get("id") or item.get("prescricao_id")),
        "paciente_id": paciente_id,
        "paciente_nome": paciente_nome,
        "paciente_email": paciente_email,
        "medico_nome": medico_nome,
        "resultado_exame": resultado_exame,
        "valor_pendente": valor_pendente,
        "tipo": tipo,
        "conteudo": conteudo,
        "data": _data_formatada(criado),
        "status_email": status_email,
    }


def _normalizar_agendamento(item: dict[str, Any]) -> dict[str, str]:
    agendamento_id = _texto(item.get("id") or item.get("agendamento_id"))
    paciente = next(
        (item[chave] for chave in ("Paciente", "paciente", "patient") if isinstance(item.get(chave), dict)),
        {},
    )
    paciente_ref = item.get("paciente_id") or item.get("id_paciente")
    if not paciente_ref:
        paciente_ref = item.get("paciente")
    paciente_id = _texto(paciente_ref if not isinstance(paciente_ref, dict) else paciente_ref.get("id"))
    if not paciente_id:
        paciente_id = _texto(paciente.get("id") or paciente.get("paciente_id"))
    paciente_nome = _texto(
        item.get("paciente_nome") or item.get("nome_paciente") or paciente.get("nome") or paciente.get("name"),
        f"Paciente #{paciente_id}" if paciente_id else "Paciente",
    ) or (f"Paciente #{paciente_id}" if paciente_id else "Paciente")
    paciente_email = _texto(item.get("paciente_email") or paciente.get("email"))
    medico = next(
        (item[chave] for chave in ("medico", "Medico", "doctor") if isinstance(item.get(chave), dict)),
        {},
    )
    medico_ref = item.get("medico_id") or item.get("id_medico")
    if not medico_ref:
        medico_ref = item.get("medico")
    medico_id = _texto(medico_ref if not isinstance(medico_ref, dict) else medico_ref.get("id"))
    if not medico_id:
        medico_id = _texto(medico.get("id") or medico.get("medico_id"))
    data = item.get("data_hora") or item.get("datahora") or item.get("data") or item.get("inicio")
    status = _texto(item.get("status") or item.get("situacao"), "Agendamento") or "Agendamento"
    return {
        "id": agendamento_id,
        "paciente_id": paciente_id,
        "paciente_nome": paciente_nome,
        "paciente_email": paciente_email,
        "medico_id": medico_id,
        "rotulo": f"{_data_formatada(data)} · {status.replace('_', ' ').title()}",
    }


async def _buscar_prescricoes(
    token: str, paciente_id: int | None = None, medico_id: int | None = None
) -> list[dict[str, str]]:
    # O Xano recebe filtros numéricos como inteiros; omitir paciente_id consulta
    # a lista da clínica usada pela secretaria. Carrega um lote amplo para a tela.
    filtros: dict[str, int] = {"page": 1, "per_page": 100}
    if paciente_id is not None:
        filtros["paciente_id"] = int(paciente_id)
    if medico_id is not None:
        filtros["medico_id"] = medico_id
    try:
        data = await api.request(
            "GET",
            "/prescricoes",
            token=token,
            params=filtros,
        )
    except api.ApiError as error:
        mensagem = error.message.casefold()
        if (
            'invalid value for param:"prescricao.paciente_id"' in mensagem
            or "unsupported parameter reference - paciente_id.id" in mensagem
        ):
            raise api.ApiError(
                "O Xano ainda rejeitou a relação do paciente em GET /prescricoes. Confira se a versão corrigida do endpoint foi publicada e atualize a página.",
                error.status,
            ) from None
        raise
    itens = _extrair_lista(data, ("prescricoes", "items", "itens", "data", "result", "results"))
    return [_normalizar_prescricao(item) for item in itens]


class PrescricaoState(rx.State):
    pacientes: list[dict[str, str]] = []
    agendamentos_medico: list[dict[str, str]] = []
    agendamentos: list[dict[str, str]] = []
    paciente_id: str = ""
    paciente_nome: str = ""
    paciente_email: str = ""
    agendamento_id: str = ""
    tipo_doc: str = TIPOS_DOCUMENTO[0]
    conteudo_doc: str = ""
    prescricoes: list[dict[str, str]] = []
    carregando_pacientes: bool = True
    carregando_prescricoes: bool = False
    salvando: bool = False
    erro: str = ""
    erro_paciente: str = ""
    erro_lista: str = ""
    erro_form: str = ""
    sucesso: str = ""
    enviando_email_id: str = ""

    @rx.event
    async def carregar_dados(self):
        auth = await self.get_state(AuthState)
        token = auth.obter_token()
        self.carregando_pacientes = True
        self.carregando_prescricoes = False
        self.pacientes = []
        self.agendamentos_medico = []
        self.agendamentos = []
        self.prescricoes = []
        self.paciente_id = ""
        self.paciente_nome = ""
        self.paciente_email = ""
        self.agendamento_id = ""
        self.erro_paciente = ""
        self.erro_lista = ""
        self.erro_form = ""
        self.sucesso = ""
        self.erro = ""
        if not token:
            self.carregando_pacientes = False
            yield AuthState.sessao_expirada
            return
        if auth.perfil in ("secretaria", "administrador"):
            yield
            try:
                self.prescricoes = await _buscar_prescricoes(token)
                self.pacientes = []
                self.erro_lista = ""
            except api.SessionExpired:
                self.carregando_pacientes = False
                yield AuthState.sessao_expirada
                return
            except api.ApiError as error:
                self.erro = "Não foi possível carregar as prescrições: " + error.message
            self.carregando_pacientes = False
            self.carregando_prescricoes = False
            return
        if auth.perfil != "medico" or not tem_permissao(auth.perfil, "prescricao:emitir"):
            self.carregando_pacientes = False
            self.erro = "Seu perfil não pode acessar esta área de prescrições."
            return
        if not auth.medico_id:
            self.carregando_pacientes = False
            self.erro = "Seu usuário médico não está vinculado a um cadastro de médico no Xano."
            return
        try:
            medico_id = int(auth.medico_id)
        except (TypeError, ValueError):
            self.carregando_pacientes = False
            self.erro = "O vínculo do seu usuário com o cadastro médico no Xano não possui um ID válido."
            return

        self.carregando_pacientes = True
        self.erro = ""
        yield
        respostas = await asyncio.gather(
            api.request("GET", "/paciente", token=token),
            api.request(
                "GET",
                "/agendamento",
                token=token,
                params={
                    "medico_id": medico_id,
                    # A consulta do Xano compara esses dois campos; enviá-los evita
                    # que filtros de data vazios eliminem os agendamentos do médico.
                    "data_inicio": 0,
                    "data_fim": 4102444800000,  # 01/01/2100 em milissegundos.
                    "page": 1,
                    "per_page": 100,
                },
            ),
            return_exceptions=True,
        )
        dados_pacientes, dados_agenda = respostas
        if any(isinstance(item, api.SessionExpired) for item in respostas):
            self.carregando_pacientes = False
            yield AuthState.sessao_expirada
            return

        erros_carregamento: list[str] = []
        self.agendamentos_medico = []
        if isinstance(dados_agenda, api.ApiError):
            erros_carregamento.append("Não foi possível carregar os agendamentos do médico: " + dados_agenda.message)
        else:
            try:
                itens_agenda = _extrair_lista(
                    dados_agenda,
                    ("agendamentos", "items", "itens", "data", "result", "results"),
                )
                self.agendamentos_medico = [
                    agendamento
                    for item in itens_agenda
                    if (agendamento := _normalizar_agendamento(item))["id"]
                    and agendamento["paciente_id"]
                    and (not agendamento["medico_id"] or agendamento["medico_id"] == str(medico_id))
                ]
            except api.ApiError as error:
                erros_carregamento.append("Não foi possível ler os agendamentos do médico: " + error.message)

        # O endpoint /agendamento aplica o vínculo do médico autenticado no Xano.
        # Intersectamos essa resposta com /paciente para nunca oferecer a lista geral.
        ids_na_agenda = {item["paciente_id"] for item in self.agendamentos_medico}
        pacientes_por_id: dict[str, dict[str, str]] = {}
        if isinstance(dados_pacientes, api.ApiError):
            if dados_pacientes.status == 403:
                erros_carregamento.append(
                    "O Xano negou GET /paciente (403). Confira a permissão de leitura para o perfil médico."
                )
            else:
                erros_carregamento.append("Não foi possível carregar a lista de pacientes: " + dados_pacientes.message)
        else:
            try:
                itens_pacientes = _extrair_lista(
                    dados_pacientes,
                    ("pacientes", "items", "itens", "data", "result", "results"),
                )
                for item in itens_pacientes:
                    paciente_id = _texto(item.get("id") or item.get("paciente_id"))
                    if not paciente_id or paciente_id not in ids_na_agenda:
                        continue
                    paciente_nome = _texto(item.get("nome") or item.get("name") or item.get("nome_completo"))
                    if not paciente_nome:
                        continue
                    paciente_email = _texto(item.get("email"))
                    pacientes_por_id[paciente_id] = {
                        "id": paciente_id,
                        "nome": paciente_nome,
                        "email": paciente_email,
                    }
            except api.ApiError as error:
                erros_carregamento.append("Não foi possível ler a lista de pacientes: " + error.message)

        # Usa também o join Paciente do agendamento quando GET /paciente não estiver disponível.
        for agendamento in self.agendamentos_medico:
            paciente_id = agendamento["paciente_id"]
            existente = pacientes_por_id.get(paciente_id, {})
            nome = existente.get("nome") or agendamento["paciente_nome"] or f"Paciente #{paciente_id}"
            email = existente.get("email") or agendamento["paciente_email"]
            pacientes_por_id[paciente_id] = {
                "id": paciente_id,
                "nome": nome,
                "email": email,
            }
        self.pacientes = [
            {
                **paciente,
                "rotulo": f"{paciente['nome']} — {paciente['email']}" if paciente["email"] else paciente["nome"],
            }
            for paciente in sorted(pacientes_por_id.values(), key=lambda paciente: paciente["nome"].casefold())
        ]
        self.erro = " ".join(erros_carregamento)
        self.carregando_pacientes = False

    @rx.event
    async def selecionar_paciente(self, paciente_id: str):
        escolhido = next((item for item in self.pacientes if item["id"] == paciente_id), None)
        if escolhido is None:
            self.paciente_id = ""
            self.paciente_nome = ""
            self.paciente_email = ""
            self.agendamentos = []
            self.agendamento_id = ""
            self.prescricoes = []
            self.erro_lista = ""
            self.erro_paciente = ""
            self.carregando_prescricoes = False
            return

        self.paciente_id = escolhido["id"]
        self.paciente_nome = escolhido["nome"]
        self.paciente_email = escolhido["email"]
        self.prescricoes = []
        self.agendamentos = [
            item for item in self.agendamentos_medico if item["paciente_id"] == self.paciente_id
        ]
        self.agendamento_id = ""
        self.erro_lista = ""
        self.erro_paciente = ""
        self.erro_form = ""
        self.sucesso = ""
        self.carregando_prescricoes = True
        yield

        auth = await self.get_state(AuthState)
        try:
            detalhe = await api.request(
                "GET",
                f"/paciente/{int(self.paciente_id)}",
                token=auth.obter_token(),
            )
            if isinstance(detalhe, dict):
                paciente = _extrair_registro(detalhe)
                self.paciente_nome = _texto(paciente.get("nome") or paciente.get("name"), self.paciente_nome)
                self.paciente_email = _texto(paciente.get("email"), self.paciente_email)
        except api.SessionExpired:
            self.carregando_prescricoes = False
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            if not self.paciente_email:
                self.erro_paciente = error.message

        try:
            medico_id: int | None = None
            if auth.perfil == "medico":
                if not auth.medico_id:
                    self.carregando_prescricoes = False
                    self.erro_lista = "Seu usuário médico não está vinculado a um cadastro de médico no Xano."
                    return
                try:
                    medico_id = int(auth.medico_id)
                except (TypeError, ValueError):
                    self.carregando_prescricoes = False
                    self.erro_lista = "O vínculo do usuário médico no Xano não possui um ID válido."
                    return
            self.prescricoes = await _buscar_prescricoes(
                auth.obter_token(), int(self.paciente_id), medico_id
            )
            self.erro_lista = ""
        except api.SessionExpired:
            self.carregando_prescricoes = False
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.prescricoes = []
            self.erro_lista = error.message
        self.carregando_prescricoes = False

    @rx.event
    def selecionar_agendamento(self, agendamento_id: str):
        if any(item["id"] == agendamento_id for item in self.agendamentos):
            self.agendamento_id = agendamento_id
        else:
            self.agendamento_id = ""
        self.erro_form = ""
        self.sucesso = ""

    @rx.var
    def total_prescricoes(self) -> str:
        """Quantidade de prescrições retornadas no histórico do paciente selecionado."""
        return str(len(self.prescricoes))

    @rx.event
    def atualizar_tipo(self, valor: str):
        if valor in TIPOS_DOCUMENTO:
            self.tipo_doc = valor
        self.erro_form = ""
        self.sucesso = ""

    @rx.event
    def atualizar_conteudo(self, valor: str):
        self.conteudo_doc = valor
        self.erro_form = ""
        self.sucesso = ""

    @rx.event
    async def emitir(self, form_data: dict[str, Any]):
        if self.salvando:
            return
        auth = await self.get_state(AuthState)
        token = auth.obter_token()
        if not token:
            yield AuthState.sessao_expirada
            return
        if auth.perfil != "medico" or not tem_permissao(auth.perfil, "prescricao:emitir"):
            self.erro_form = "Somente médicos podem criar prescrições."
            return
        if not auth.medico_id:
            self.erro_form = "Seu usuário médico não está vinculado ao Xano. Peça ao administrador para revisar o cadastro."
            return
        if not self.paciente_id:
            self.erro_form = "Selecione o paciente que receberá o documento."
            return
        if not self.agendamento_id:
            self.erro_form = "Selecione o agendamento relacionado à prescrição."
            return
        agendamento = next(
            (
                item
                for item in self.agendamentos
                if item["id"] == self.agendamento_id and item["paciente_id"] == self.paciente_id
            ),
            None,
        )
        if agendamento is None:
            self.erro_form = "O agendamento selecionado não pertence a este paciente. Atualize a página e tente novamente."
            return
        conteudo = self.conteudo_doc.strip()
        if not conteudo:
            self.erro_form = "Escreva o conteúdo da prescrição antes de enviar."
            return
        try:
            medico_id = int(auth.medico_id)
            paciente_id = int(self.paciente_id)
            agendamento_id = int(self.agendamento_id)
        except (TypeError, ValueError):
            self.erro_form = "O vínculo do paciente ou do médico no Xano não possui um ID válido."
            return
        if agendamento["medico_id"] and agendamento["medico_id"] != str(medico_id):
            self.erro_form = "Este agendamento não pertence ao médico autenticado. Atualize a agenda antes de enviar."
            return

        payload = {
            "paciente_id": paciente_id,
            "medico_id": medico_id,
            "agendamento_id": agendamento_id,
            "tipo_doc": self.tipo_doc,
            "conteudo_doc": conteudo,
        }
        self.salvando = True
        self.erro_form = ""
        self.sucesso = ""
        yield
        try:
            resultado = await api.request(
                "POST",
                "/prescricoes",
                token=token,
                json=payload,
            )
        except api.SessionExpired:
            self.salvando = False
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.salvando = False
            if error.status is not None and error.status >= 500:
                ids_anteriores = {item["id"] for item in self.prescricoes if item["id"]}
                self.carregando_prescricoes = True
                yield
                prescricao_salva = False
                try:
                    atualizadas = await _buscar_prescricoes(token, paciente_id, medico_id)
                    self.prescricoes = atualizadas
                    prescricao_salva = any(
                        item["id"]
                        and item["id"] not in ids_anteriores
                        and item["tipo"] == self.tipo_doc
                        and item["conteudo"] == conteudo
                        for item in atualizadas
                    )
                    self.erro_lista = ""
                except api.SessionExpired:
                    self.carregando_prescricoes = False
                    yield AuthState.sessao_expirada
                    return
                except api.ApiError as erro_historico:
                    self.erro_lista = erro_historico.message
                self.carregando_prescricoes = False
                if prescricao_salva:
                    self.sucesso = "Prescrição salva e disponível para a secretaria enviar por e-mail."
                    self.conteudo_doc = ""
                    yield rx.toast.success(self.sucesso, position="top-center")
                else:
                    self.erro_form = (
                        "O Xano não confirmou o salvamento da prescrição. Confira o histórico do paciente "
                        "antes de tentar novamente."
                    )
                return
            self.erro_form = error.message
            return

        self.salvando = False
        if isinstance(resultado, dict) and resultado.get("success") is False:
            self.erro_form = "Não foi possível confirmar o salvamento da prescrição. Confira o histórico antes de tentar novamente."
            return
        self.sucesso = "Prescrição salva e disponível para a secretaria enviar por e-mail."
        self.conteudo_doc = ""
        yield rx.toast.success(self.sucesso, position="top-center")

        self.carregando_prescricoes = True
        try:
            self.prescricoes = await _buscar_prescricoes(token, paciente_id, medico_id)
            self.erro_lista = ""
        except api.SessionExpired:
            self.carregando_prescricoes = False
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.erro_lista = error.message
        self.carregando_prescricoes = False

    @rx.event
    async def enviar_por_email(self, prescricao_id: str):
        if self.enviando_email_id:
            return
        auth = await self.get_state(AuthState)
        token = auth.obter_token()
        if not token:
            yield AuthState.sessao_expirada
            return
        if not tem_permissao(auth.perfil, "prescricao:email"):
            self.erro_lista = "Somente a secretaria ou o administrador pode enviar prescrições por e-mail."
            return
        prescricao = next((item for item in self.prescricoes if item["id"] == prescricao_id), None)
        if prescricao is None:
            self.erro_lista = "Atualize o histórico antes de enviar esta prescrição."
            return
        if prescricao["status_email"] == "enviado":
            self.sucesso = "Esta prescrição já consta como enviada."
            return
        if not prescricao["paciente_email"]:
            self.erro_lista = "Este paciente não tem e-mail cadastrado. Atualize o cadastro antes de enviar."
            return
        self.enviando_email_id = prescricao_id
        self.erro_lista = ""
        self.sucesso = ""
        yield
        try:
            resultado = await api.request(
                "POST",
                f"/prescricoes/{int(prescricao_id)}/enviar-email",
                token=token,
                json={},
            )
        except api.SessionExpired:
            self.enviando_email_id = ""
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.enviando_email_id = ""
            if error.status in (404, 405):
                self.erro_lista = (
                    "O Xano ainda não disponibiliza POST /prescricoes/{prescricao_id}/enviar-email. "
                    "Crie essa rota privada para secretaria e administrador."
                )
            elif error.status is not None and error.status >= 500:
                self.erro_lista = (
                    "O Xano não confirmou o envio. Confira o status no histórico e a autorização do SendGrid "
                    "antes de tentar novamente."
                )
            else:
                self.erro_lista = "Não foi possível enviar a prescrição. " + error.message
            return

        self.enviando_email_id = ""
        if isinstance(resultado, dict) and resultado.get("success") is False:
            self.erro_lista = "Não foi possível confirmar o envio da prescrição. Confira o histórico antes de tentar novamente."
            return
        self.sucesso = "Prescrição enviada ao e-mail cadastrado do paciente."
        yield rx.toast.success(self.sucesso, position="top-center")
        self.carregando_prescricoes = True
        yield
        try:
            paciente_id = int(prescricao["paciente_id"]) if prescricao["paciente_id"] else None
            self.prescricoes = await _buscar_prescricoes(
                token,
                paciente_id if auth.perfil == "medico" else None,
                int(auth.medico_id) if auth.perfil == "medico" and auth.medico_id else None,
            )
            self.erro_lista = ""
        except api.SessionExpired:
            self.carregando_prescricoes = False
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.erro_lista = error.message
        self.carregando_prescricoes = False


def _campo(rotulo: str, campo: rx.Component) -> rx.Component:
    return rx.vstack(
        rx.text(rotulo, color="#05589F", font_family="Inter", font_size="0.9rem", font_weight="600"),
        campo,
        spacing="1",
        width="100%",
    )


def _alerta_erro(mensagem: Any) -> rx.Component:
    return rx.hstack(
        rx.icon(tag="triangle_alert", size=20, color="#B42318", flex_shrink="0"),
        rx.text(
            mensagem,
            color="#7A1B16",
            font_family="Inter",
            font_size="0.9rem",
            font_weight="600",
            line_height="1.5",
            white_space="pre-wrap",
        ),
        align="start",
        spacing="3",
        width="100%",
        padding="0.85rem 1rem",
        border="1px solid #D92D20",
        border_radius="12px",
        background="#FEF3F2",
        box_sizing="border-box",
    )


def cartao_prescricao(item: rx.Var[dict[str, str]]) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Paciente", color="#4A7A69", font_family="Inter", font_size="0.78rem", font_weight="600"),
                rx.text(item["paciente_nome"], color="#05589F", font_family="Inter", font_weight="600"),
                spacing="1", align="start",
            ),
            rx.spacer(),
            rx.vstack(
                rx.text("Médico", color="#4A7A69", font_family="Inter", font_size="0.78rem", font_weight="600"),
                rx.text(item["medico_nome"], color="#38566B", font_family="Inter"),
                spacing="1", align="start",
            ),
            width="100%", align="start", flex_wrap="wrap",
        ),
        rx.hstack(
            rx.text(item["tipo"], color="#05589F", font_family="Inter", font_weight="600"),
            rx.spacer(),
            rx.text(item["data"], color="#38566B", font_family="Inter", font_size="0.85rem"),
            width="100%",
            align="center",
            flex_wrap="wrap",
        ),
        rx.text(
            item["conteudo"],
            color="#38566B",
            font_family="Inter",
            font_size="0.95rem",
            line_height="1.6",
            white_space="pre-wrap",
            word_break="break-word",
            width="100%",
        ),
        rx.vstack(
            rx.text("Resultado do exame", color="#05589F", font_family="Inter", font_weight="600"),
            rx.text(item["resultado_exame"], color="#38566B", font_family="Inter", white_space="pre-wrap", word_break="break-word"),
            rx.text("Valor pendente do exame: " + item["valor_pendente"], color="#38566B", font_family="Inter", font_weight="600"),
            spacing="2", align="start", width="100%", padding="0.85rem", border_radius="12px", background="#F0F7FA",
        ),
        rx.cond(
            item["paciente_email"] != "",
            rx.text("E-mail: " + item["paciente_email"], color="#38566B", font_family="Inter", font_size="0.85rem", word_break="break-word"),
            rx.callout("Paciente sem e-mail cadastrado.", icon="triangle_alert", color_scheme="orange", width="100%"),
        ),
        rx.cond(
            AuthState.perfil != "medico",
            rx.cond(
                item["status_email"] == "enviado",
                rx.badge("E-mail enviado", color_scheme="green", variant="soft"),
                rx.button(
                    rx.cond(
                        PrescricaoState.enviando_email_id == item["id"],
                        "Enviando...",
                        "Enviar ao paciente por e-mail",
                    ),
                    on_click=PrescricaoState.enviar_por_email(item["id"]),
                    loading=PrescricaoState.enviando_email_id == item["id"],
                    disabled=(PrescricaoState.enviando_email_id != "")
                    | (item["paciente_email"] == ""),
                    background="#05589F",
                    color="#FFFFFF",
                    border_radius="9999px",
                    width=rx.breakpoints(initial="100%", sm="fit-content"),
                ),
            ),
            rx.fragment(),
        ),
        spacing="3",
        width="100%",
        padding="1rem",
        border="1px solid #E6F2F7",
        border_radius="16px",
        background="#FFFFFF",
    )


def prescricoes() -> rx.Component:
    seletor_paciente = rx.select.root(
        rx.select.trigger(placeholder="Selecione um paciente", width="100%"),
        rx.select.content(
            rx.select.group(
                rx.foreach(
                    PrescricaoState.pacientes,
                    lambda paciente: rx.select.item(paciente["rotulo"], value=paciente["id"]),
                )
            ),
        ),
        value=PrescricaoState.paciente_id,
        on_change=PrescricaoState.selecionar_paciente,
        required=True,
        width="100%",
    )
    seletor_agendamento = rx.select.root(
        rx.select.trigger(placeholder="Selecione o agendamento", width="100%"),
        rx.select.content(
            rx.select.group(
                rx.foreach(
                    PrescricaoState.agendamentos,
                    lambda agendamento: rx.select.item(agendamento["rotulo"], value=agendamento["id"]),
                )
            ),
        ),
        value=PrescricaoState.agendamento_id,
        on_change=PrescricaoState.selecionar_agendamento,
        required=True,
        width="100%",
    )
    return rx.hstack(
        Sidebar(active="Prescrições"),
        rx.vstack(
            Topbar(),
            rx.vstack(
                rx.heading(
                    "Prescrições médicas",
                    color="#05589F",
                    font_family="Poppins",
                    font_size=rx.breakpoints(initial="1.65rem", md="2.1rem"),
                    font_weight="600",
                ),
                rx.text(
                    rx.cond(
                        AuthState.perfil == "medico",
                        "Crie prescrições para pacientes vinculados à sua agenda. A secretaria poderá enviar o documento por e-mail.",
                        "Consulte as prescrições dos pacientes e envie os documentos por e-mail.",
                    ),
                    color="#38566B",
                    font_family="Inter",
                    font_size="1rem",
                ),
                rx.cond(
                    PrescricaoState.erro != "",
                    _alerta_erro(PrescricaoState.erro),
                ),
                rx.cond(
                    PrescricaoState.carregando_pacientes,
                    rx.hstack(
                        rx.spinner(size="3", color="#05589F"),
                        rx.text(rx.cond(AuthState.perfil == "medico", "Carregando pacientes...", "Carregando prescrições..."), color="#38566B"),
                        spacing="3",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    (AuthState.perfil == "medico")
                    & (PrescricaoState.pacientes.length() == 0)
                    & (~PrescricaoState.carregando_pacientes)
                    & (PrescricaoState.erro == ""),
                    rx.callout(
                        rx.cond(
                            AuthState.perfil == "medico",
                            "Nenhum paciente com agendamento vinculado a este médico foi encontrado.",
                            "Nenhum paciente foi encontrado.",
                        ),
                        icon="info",
                        color_scheme="blue",
                        width="100%",
                    ),
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            rx.cond(AuthState.perfil == "medico", "Prescrições do paciente selecionado", "Prescrições da clínica"),
                            color="#4A7A69", font_family="Inter", font_size="0.9rem", font_weight="600",
                        ),
                        rx.heading(
                            rx.cond(
                                (AuthState.perfil == "medico") & (PrescricaoState.paciente_id == ""),
                                "—",
                                PrescricaoState.total_prescricoes,
                            ),
                            color="#05589F",
                            font_family="Poppins",
                            font_size="2rem",
                            line_height="1",
                        ),
                        spacing="2",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.icon(tag="send", size=24, color="#05589F"),
                    width="100%",
                    align="center",
                    padding="1rem 1.25rem",
                    border_radius="18px",
                    background="rgba(136,224,193,0.3)",
                    box_sizing="border-box",
                ),
                rx.vstack(
                    rx.cond(
                        AuthState.perfil == "medico",
                        rx.vstack(
                        rx.heading("Nova prescrição", color="#05589F", font_family="Poppins", font_size="1.2rem"),
                        rx.form(
                            rx.vstack(
                                _campo("Paciente", seletor_paciente),
                                rx.cond(
                                    PrescricaoState.paciente_id != "",
                                    rx.hstack(
                                        rx.icon(tag="mail", size=18, color="#05589F"),
                                        rx.text("Destinatário:", color="#38566B", font_family="Inter", font_weight="600"),
                                        rx.text(
                                            rx.cond(PrescricaoState.paciente_email != "", PrescricaoState.paciente_email, "Sem e-mail cadastrado"),
                                            color="#05589F",
                                            font_family="Inter",
                                            word_break="break-word",
                                        ),
                                        align="center",
                                        flex_wrap="wrap",
                                        spacing="2",
                                        width="100%",
                                        padding="0.75rem",
                                        border_radius="12px",
                                        background="#F0F7FA",
                                    ),
                                ),
                                rx.cond(
                                    PrescricaoState.erro_paciente != "",
                                    _alerta_erro("Não foi possível obter o e-mail cadastrado: " + PrescricaoState.erro_paciente),
                                ),
                                rx.cond(
                                    PrescricaoState.paciente_id != "",
                                    rx.cond(
                                        PrescricaoState.agendamentos.length() > 0,
                                        _campo("Agendamento relacionado", seletor_agendamento),
                                        rx.callout(
                                            "Este paciente não tem um agendamento com você. Peça à secretaria para criar ou vincular um agendamento antes de emitir a prescrição.",
                                            icon="info",
                                            color_scheme="blue",
                                            width="100%",
                                        ),
                                    ),
                                ),
                                _campo(
                                    "Tipo de documento",
                                    rx.select(
                                        list(TIPOS_DOCUMENTO),
                                        value=PrescricaoState.tipo_doc,
                                        on_change=PrescricaoState.atualizar_tipo,
                                        width="100%",
                                    ),
                                ),
                                _campo(
                                    "Conteúdo",
                                    rx.text_area(
                                        value=PrescricaoState.conteudo_doc,
                                        on_change=PrescricaoState.atualizar_conteudo,
                                        placeholder="Escreva a orientação ou os itens da prescrição...",
                                        aria_label="Conteúdo da prescrição",
                                        required=True,
                                        min_height="180px",
                                        width="100%",
                                        color="#38566B",
                                        font_family="Inter",
                                        border="1px solid #A7D8F0",
                                        border_radius="12px",
                                        padding="0.85rem 1rem",
                                        background="#FFFFFF",
                                        resize="vertical",
                                    ),
                                ),
                                rx.text(
                                    "Vincule a prescrição a um agendamento seu. Não é necessário ter exame prévio. Após salvar, a secretaria poderá conferir o histórico e enviar o documento ao paciente.",
                                    color="#38566B",
                                    font_family="Inter",
                                    font_size="0.85rem",
                                    line_height="1.5",
                                ),
                                rx.cond(
                                    PrescricaoState.erro_form != "",
                                    _alerta_erro(PrescricaoState.erro_form),
                                ),
                                rx.cond(
                                    PrescricaoState.sucesso != "",
                                    rx.callout(PrescricaoState.sucesso, icon="check", color_scheme="green", width="100%"),
                                ),
                                rx.button(
                                    rx.cond(PrescricaoState.salvando, "Salvando...", "Salvar prescrição"),
                                    type="submit",
                                    loading=PrescricaoState.salvando,
                                    disabled=PrescricaoState.salvando
                                    | PrescricaoState.carregando_pacientes
                                    | PrescricaoState.carregando_prescricoes
                                    | (PrescricaoState.paciente_id == "")
                                    | (PrescricaoState.agendamento_id == ""),
                                    width="100%",
                                    background="#05589F",
                                    color="#FFFFFF",
                                    font_family="Inter",
                                    font_weight="600",
                                    border_radius="9999px",
                                    size="3",
                                ),
                                spacing="4",
                                width="100%",
                            ),
                            on_submit=PrescricaoState.emitir,
                            reset_on_submit=False,
                            width="100%",
                        ),
                        align="start",
                        spacing="4",
                        width="100%",
                        padding="1.25rem",
                        border_radius="20px",
                        background="#FFFFFF",
                        box_shadow="0 8px 24px rgba(5,88,159,0.08)",
                        box_sizing="border-box",
                    ),
                        rx.fragment(),
                    ),
                    rx.vstack(
                        rx.cond(
                            AuthState.perfil == "medico",
                            rx.fragment(),
                            _campo("Paciente", seletor_paciente),
                        ),
                        rx.heading(
                            rx.cond(AuthState.perfil == "medico", "Histórico do paciente", "Prescrições para envio"),
                            color="#05589F", font_family="Poppins", font_size="1.2rem",
                        ),
                        rx.cond(
                            (AuthState.perfil == "medico") & (PrescricaoState.paciente_id != ""),
                            rx.text(
                                "Paciente: "
                                + PrescricaoState.paciente_nome
                                + " · "
                                + rx.cond(
                                    PrescricaoState.paciente_email != "",
                                    PrescricaoState.paciente_email,
                                    "sem e-mail cadastrado",
                                ),
                                color="#38566B",
                                font_family="Inter",
                                font_size="0.9rem",
                                word_break="break-word",
                            ),
                        ),
                        rx.cond(
                            (AuthState.perfil == "medico")
                            & (PrescricaoState.paciente_id != "")
                            & (PrescricaoState.paciente_email == ""),
                            rx.callout(
                                "Este paciente não tem e-mail cadastrado. Atualize o cadastro antes de tentar enviar.",
                                icon="triangle_alert",
                                color_scheme="orange",
                                width="100%",
                            ),
                        ),
                        rx.cond(
                            (AuthState.perfil == "medico") & (PrescricaoState.paciente_id == ""),
                            rx.text("Selecione um paciente para consultar as prescrições emitidas.", color="#38566B", font_family="Inter"),
                            rx.cond(
                                PrescricaoState.carregando_prescricoes,
                                rx.hstack(rx.spinner(size="3", color="#05589F"), rx.text("Carregando histórico...", color="#38566B"), spacing="3"),
                                rx.cond(
                                    PrescricaoState.erro_lista != "",
                                    _alerta_erro(PrescricaoState.erro_lista),
                                    rx.cond(
                                        PrescricaoState.prescricoes.length() == 0,
                                        rx.text(
                                            rx.cond(AuthState.perfil == "medico", "Nenhuma prescrição encontrada para este paciente.", "Nenhuma prescrição encontrada."),
                                            color="#38566B", font_family="Inter",
                                        ),
                                        rx.vstack(rx.foreach(PrescricaoState.prescricoes, cartao_prescricao), spacing="3", width="100%"),
                                    ),
                                ),
                            ),
                        ),
                        align="start",
                        spacing="4",
                        width="100%",
                        padding="1.25rem",
                        border_radius="20px",
                        background="#FFFFFF",
                        box_shadow="0 8px 24px rgba(5,88,159,0.08)",
                        box_sizing="border-box",
                    ),
                    spacing="4",
                    align_items="start",
                    width="100%",
                ),
                spacing="4",
                align="start",
                width="100%",
            ),
            spacing="5",
            align="start",
            width="100%",
            max_width="1280px",
            min_width="0",
            padding=rx.breakpoints(initial="1rem", md="2rem 2.5rem", lg="2.25rem 3rem"),
            box_sizing="border-box",
        ),
        width="100%",
        min_height="100vh",
        background=rx.color_mode_cond("#F8FCFD", "#0B1220"),
        spacing="0",
        align="stretch",
        flex_direction=rx.breakpoints(initial="column", md="row"),
        on_mount=PrescricaoState.carregar_dados,
    )
