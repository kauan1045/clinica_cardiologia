import asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

import reflex as rx

from ProjetoCl_nicaCardiologia import api
from ProjetoCl_nicaCardiologia.auth import AuthState, tem_permissao
from ProjetoCl_nicaCardiologia.dashboard import (
    MONTHS,
    WEEKDAYS,
    Sidebar,
    Topbar,
    _extrair_lista,
    _id_relacao_paciente,
    _nome_relacionado,
    _interpretar_data,
    normalizar_agendamento,
    periodo_datas,
    status_badge,
    timestamp_fim,
    timestamp_inicio,
)


VISUALIZACOES = ("Dia", "Semana", "Mês")
ITENS_POR_PAGINA = 50
STATUS_AGENDAMENTO = ("Pendente", "Confirmado", "Cancelado", "Realizado")
STATUS_PAGAMENTO = ("Pendente", "Pago", "Estornado")
FORMAS_PAGAMENTO = ("Dinheiro", "Cartão", "Convênio")
PRAZO_PADRAO_CONSULTA_MINUTOS = 30


def _opcao_registro(item: dict[str, Any], rotulo: str, *chaves_nome: str) -> dict[str, str]:
    identificador = item.get("id") or item.get(f"{rotulo}_id")
    nome = next((item.get(chave) for chave in chaves_nome if item.get(chave)), "")
    if identificador is None or not str(nome).strip():
        return {}
    return {"id": str(identificador), "nome": str(nome).strip()}


def _inteiro_positivo(value: Any, *, limite: int = 1440) -> int | None:
    try:
        numero = int(value)
    except (TypeError, ValueError):
        return None
    return numero if 1 <= numero <= limite else None


def _duracao_registro(item: dict[str, Any]) -> int | None:
    for chave in ("duracao_minutos", "duracao", "tempo_minutos"):
        valor = _inteiro_positivo(item.get(chave))
        if valor is not None:
            return valor
    for chave in ("exame", "Exame", "exam"):
        relacionado = item.get(chave)
        if isinstance(relacionado, dict):
            valor = _duracao_registro(relacionado)
            if valor is not None:
                return valor
    return None


def _divisao_valor_exame(exame: dict[str, str] | None, convenio: dict[str, str] | None) -> tuple[int, int] | None:
    if not exame:
        return None
    try:
        total = Decimal(exame.get("valor_reais", "0"))
        percentual_convenio = Decimal(convenio.get("desconto", "0")) if convenio else Decimal("0")
        if total < 0 or not Decimal("0") <= percentual_convenio <= Decimal("100"):
            return None
        valor_convenio = (total * percentual_convenio / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        valor_paciente = total - valor_convenio
        return int(valor_paciente * 100), int(valor_convenio * 100)
    except (InvalidOperation, TypeError):
        return None


def _id_relacionado(item: dict[str, Any], chaves_id: tuple[str, ...], chaves_objeto: tuple[str, ...]) -> str:
    for chave in chaves_id:
        valor = item.get(chave)
        if valor is not None and not isinstance(valor, dict):
            return str(valor)
    for chave in chaves_objeto:
        valor = item.get(chave)
        if isinstance(valor, dict):
            relacionado_id = valor.get("id") or valor.get("id_medico") or valor.get("medico_id") or valor.get("exame_id")
            if relacionado_id is not None:
                return str(relacionado_id)
        elif valor is not None:
            return str(valor)
    return ""


async def _conflito_de_agenda(
    token: str,
    data: date,
    medico_id: int,
    inicio_novo: datetime,
    duracao_nova: int,
    exames: list[dict[str, str]],
) -> str:
    duracoes_por_exame = {
        item["id"]: duracao
        for item in exames
        if (duracao := _inteiro_positivo(item.get("duracao_minutos"))) is not None
    }
    inicio_novo = inicio_novo.replace(second=0, microsecond=0)
    fim_novo = inicio_novo + timedelta(minutes=duracao_nova)
    pagina = 1
    while True:
        resultado = await api.request(
            "GET",
            "/agendamento",
            token=token,
            params={
                "medico_id": medico_id,
                "data_inicio": timestamp_inicio(data),
                "data_fim": timestamp_fim(data),
                "page": pagina,
                "per_page": ITENS_POR_PAGINA,
            },
        )
        itens = _extrair_lista(resultado)
        for item in itens:
            if not isinstance(item, dict):
                continue
            medico_agendado = _id_relacionado(
                item,
                ("medico_id", "id_medico"),
                ("medico", "Medico", "doctor"),
            )
            if medico_agendado and medico_agendado != str(medico_id):
                continue
            status = str(item.get("status") or item.get("situacao") or "").casefold()
            if "cancel" in status:
                continue
            inicio_existente = _interpretar_data(
                item.get("data_hora") or item.get("datahora") or item.get("data") or item.get("inicio") or item.get("start")
            )
            if inicio_existente is None:
                continue
            inicio_existente = inicio_existente.replace(second=0, microsecond=0)
            exame_id = _id_relacionado(
                item,
                ("exame_id", "id_exame"),
                ("exame", "Exame", "exam"),
            )
            duracao_existente = _duracao_registro(item) or duracoes_por_exame.get(exame_id) or PRAZO_PADRAO_CONSULTA_MINUTOS
            fim_existente = inicio_existente + timedelta(minutes=duracao_existente)
            if inicio_novo < fim_existente and inicio_existente < fim_novo:
                return (
                    "Este horário se sobrepõe a outro atendimento do médico "
                    f"({inicio_existente.strftime('%H:%M')}–{fim_existente.strftime('%H:%M')}). Escolha outro horário."
                )

        total_paginas, tem_proxima = _metadados_paginacao(resultado, pagina, len(itens))
        if not tem_proxima or pagina >= total_paginas:
            return ""
        pagina += 1
        if pagina > 100:
            raise api.ApiError("A agenda do dia excedeu o limite de páginas para validar conflitos.")


def _texto_periodo(inicio: date, fim: date, visualizacao: str) -> str:
    if visualizacao == "Mês":
        return f"{MONTHS[inicio.month - 1].capitalize()} de {inicio.year}"
    if visualizacao == "Semana":
        if inicio.month == fim.month and inicio.year == fim.year:
            datas = f"{inicio.day} a {fim.day} de {MONTHS[fim.month - 1]} de {fim.year}"
        else:
            datas = f"{inicio.day} de {MONTHS[inicio.month - 1]} a {fim.day} de {MONTHS[fim.month - 1]} de {fim.year}"
        return f"Semana de {datas}"
    return f"{WEEKDAYS[inicio.weekday()]}, {inicio.day} de {MONTHS[inicio.month - 1]} de {inicio.year}"


def _metadados_paginacao(data: Any, pagina: int, itens_recebidos: int) -> tuple[int, bool]:
    """Lê metadados do Xano ou infere se há outra página pelo tamanho do lote."""
    candidatos: list[dict[str, Any]] = []
    if isinstance(data, dict):
        candidatos.append(data)
        for chave in ("pagination", "meta", "metadata", "page_info", "data", "result"):
            valor = data.get(chave)
            if isinstance(valor, dict):
                candidatos.append(valor)

    total_paginas: int | None = None
    total_itens: int | None = None
    tem_proxima: bool | None = None
    for item in candidatos:
        for chave in ("totalPages", "total_pages", "pages"):
            try:
                if item.get(chave) is not None:
                    total_paginas = int(item[chave])
                    break
            except (TypeError, ValueError):
                continue
        for chave in ("totalItems", "total_items", "total_count", "total"):
            try:
                if item.get(chave) is not None:
                    total_itens = int(item[chave])
                    break
            except (TypeError, ValueError):
                continue
        for chave in ("hasMore", "has_more", "hasNext", "has_next"):
            if isinstance(item.get(chave), bool):
                tem_proxima = item[chave]
                break
        if tem_proxima is None:
            for chave in ("nextPage", "next_page"):
                if chave in item:
                    tem_proxima = item[chave] is not None and item[chave] is not False
                    break
        if total_paginas is not None or total_itens is not None or tem_proxima is not None:
            break

    if total_paginas is None and total_itens is not None:
        total_paginas = max(1, -(-total_itens // ITENS_POR_PAGINA))
    if total_paginas is not None:
        total_paginas = max(1, total_paginas)
        return total_paginas, pagina < total_paginas
    if tem_proxima is not None:
        return (pagina + 1 if tem_proxima else pagina), tem_proxima
    tem_proxima = itens_recebidos >= ITENS_POR_PAGINA
    return (pagina + 1 if tem_proxima else pagina), tem_proxima


class AgendamentoState(rx.State):
    visualizacao: str = "Dia"
    pagina: int = 1
    total_paginas: int = 1
    tem_proxima_pagina: bool = False
    data_agenda: str = date.today().isoformat()
    busca: str = ""
    carregando: bool = True
    erro: str = ""
    id_remocao_pendente: str = ""
    removendo: bool = False
    agenda: list[dict[str, str]] = []
    pacientes_por_id: dict[str, str] = {}
    pacientes_resolvidos: bool = False
    modal_aberto: bool = False
    carregando_opcoes: bool = False
    salvando: bool = False
    erro_opcoes: str = ""
    erro_opcoes_opcionais: str = ""
    erro_form: str = ""
    pacientes: list[dict[str, str]] = []
    medicos: list[dict[str, str]] = []
    exames: list[dict[str, str]] = []
    convenios: list[dict[str, str]] = []
    form_paciente_id: str = ""
    form_medico_id: str = ""
    form_data: str = date.today().isoformat()
    form_hora: str = ""
    form_status: str = "Pendente"
    form_exame_id: str = ""
    form_convenio_id: str = ""
    form_forma_pagamento: str = ""
    form_status_pagamento: str = "Pendente"
    form_resultado: str = ""

    def _limpar_formulario(self):
        self.form_paciente_id = ""
        self.form_medico_id = ""
        self.form_data = date.today().isoformat()
        self.form_hora = ""
        self.form_status = "Pendente"
        self.form_exame_id = ""
        self.form_convenio_id = ""
        self.form_forma_pagamento = ""
        self.form_status_pagamento = "Pendente"
        self.form_resultado = ""

    @rx.event
    async def abrir_modal(self):
        auth = await self.get_state(AuthState)
        if not tem_permissao(auth.perfil, "agendamento:gerenciar"):
            self.erro = "Seu perfil não tem permissão para criar agendamentos."
            return
        token = auth.obter_token()
        if not token:
            yield AuthState.sessao_expirada
            return

        self._limpar_formulario()
        self.erro_form = ""
        self.erro_opcoes = ""
        self.erro_opcoes_opcionais = ""
        self.pacientes = []
        self.medicos = []
        self.exames = []
        self.convenios = []
        self.pacientes_por_id = {}
        self.pacientes_resolvidos = False
        self.modal_aberto = True
        self.carregando_opcoes = True
        yield

        respostas = await asyncio.gather(
            api.request("GET", "/paciente", token=token),
            api.request("GET", "/lista_medico", token=token),
            api.request("GET", "/exame", token=token),
            api.request("GET", "/convenio", token=token),
            return_exceptions=True,
        )
        pacientes_data, medicos_data, exames_data, convenios_data = respostas
        if any(isinstance(item, api.SessionExpired) for item in respostas):
            self.carregando_opcoes = False
            self.modal_aberto = False
            yield AuthState.sessao_expirada
            return

        erros_principais = [item for item in respostas[:2] if isinstance(item, api.ApiError)]
        if erros_principais:
            self.erro_opcoes = "Não foi possível carregar pacientes e médicos: " + erros_principais[0].message
        else:
            try:
                pacientes = _extrair_lista(pacientes_data)
                medicos = _extrair_lista(medicos_data)
                self.pacientes = []
                for item in pacientes:
                    if not isinstance(item, dict):
                        continue
                    opcao = _opcao_registro(item, "paciente", "nome", "name", "nome_completo")
                    if opcao:
                        # O identificador continua como valor interno do select, mas não aparece ao usuário.
                        opcao["rotulo"] = opcao["nome"]
                        opcao["email"] = str(item.get("email") or "").strip()
                        carteira = "".join(char for char in str(item.get("numero_carteirinha") or item.get("carteirinha_convenio") or item.get("carteirinha") or "") if char.isdigit())
                        opcao["codigo_convenio"] = carteira[-3:] if len(carteira) == 17 else ""
                        self.pacientes.append(opcao)
                        self.pacientes_por_id[opcao["id"]] = opcao["nome"]
                self.pacientes_resolvidos = True
                self.medicos = []
                for item in medicos:
                    if not isinstance(item, dict):
                        continue
                    opcao = _opcao_registro(item, "medico", "nome", "name")
                    if opcao:
                        especialidade = str(item.get("especialidade") or "").strip()
                        crm = str(item.get("crm") or item.get("CRM") or "").strip()
                        complemento = especialidade or crm
                        opcao["rotulo"] = f"{opcao['nome']} — {complemento}" if complemento else opcao["nome"]
                        self.medicos.append(opcao)
            except api.ApiError as error:
                self.erro_opcoes = "Não foi possível ler pacientes e médicos: " + error.message

        avisos_opcionais: list[str] = []
        for dados, rotulo in ((exames_data, "exames"), (convenios_data, "convênios")):
            if isinstance(dados, api.ApiError):
                avisos_opcionais.append(f"{rotulo}: {dados.message}")
        if avisos_opcionais:
            self.erro_opcoes_opcionais = "Não foi possível carregar " + "; ".join(avisos_opcionais) + ". O agendamento ainda pode ser criado sem esses vínculos."
            self.exames = []
            self.convenios = []
        else:
            try:
                self.exames = [
                    opcao
                    | {
                        "valor_reais": str(item.get("valor_do_exame_por_repasse") or item.get("valor") or item.get("valor_repasse") or "0"),
                        "duracao_minutos": str(_duracao_registro(item) or ""),
                        "prazo_resultado_dias": str(
                            _inteiro_positivo(item.get("prazo_resultado_dias"), limite=365) or ""
                        ),
                        "rotulo": (
                            f"{opcao['nome']} — {_duracao_registro(item)} min"
                            + (
                                f" · laudo em até {item['prazo_resultado_dias']} dias"
                                if _inteiro_positivo(item.get("prazo_resultado_dias"), limite=365)
                                else ""
                            )
                            if _duracao_registro(item)
                            else f"{opcao['nome']} (duração não cadastrada)"
                        ),
                    }
                    for item in _extrair_lista(exames_data)
                    if isinstance(item, dict)
                    and (opcao := _opcao_registro(item, "exame", "nome_do_exame", "nome", "name"))
                ]
                self.convenios = []
                for item in _extrair_lista(convenios_data):
                    if not isinstance(item, dict):
                        continue
                    opcao = _opcao_registro(item, "convenio", "nome", "name")
                    if opcao:
                        codigo = str(item.get("codigo") or "").strip()
                        opcao["codigo"] = codigo.zfill(3) if codigo.isdigit() else codigo
                        opcao["desconto"] = str(item.get("desconto") or "0")
                        opcao["rotulo"] = f"{opcao['nome']} — {codigo}" if codigo else opcao["nome"]
                        self.convenios.append(opcao)
            except api.ApiError as error:
                self.erro_opcoes_opcionais = "Não foi possível ler exames e convênios: " + error.message + ". O agendamento ainda pode ser criado sem esses vínculos."
                self.exames = []
                self.convenios = []
        self.carregando_opcoes = False

    @rx.event
    def fechar_modal(self):
        if not self.salvando:
            self.modal_aberto = False
            self.erro_form = ""

    @rx.event
    def alterar_modal(self, aberto: bool):
        if not aberto and not self.salvando:
            self.modal_aberto = False
            self.erro_form = ""

    @rx.event
    def selecionar_paciente(self, valor: str):
        self.form_paciente_id = valor
        paciente = next((item for item in self.pacientes if item["id"] == valor), None)
        codigo = paciente.get("codigo_convenio", "") if paciente else ""
        convenio = next((item for item in self.convenios if item.get("codigo") == codigo), None)
        self.form_convenio_id = convenio["id"] if convenio else ""
        self.form_forma_pagamento = "Convênio" if convenio else ""

    @rx.event
    def selecionar_medico(self, valor: str):
        self.form_medico_id = valor

    @rx.event
    def selecionar_exame(self, valor: str):
        self.form_exame_id = valor

    @rx.var
    def informacao_duracao_exame(self) -> str:
        if not self.form_exame_id:
            return ""
        exame = next((item for item in self.exames if item["id"] == self.form_exame_id), None)
        if exame is None or not exame.get("duracao_minutos"):
            return "Este exame não tem duração cadastrada no Xano. Atualize o cadastro antes de agendar."
        prazo = exame.get("prazo_resultado_dias")
        prazo_texto = (
            f"Prazo máximo do laudo: {prazo} dias após o exame."
            if prazo
            else "O prazo do laudo ainda não foi cadastrado para este exame."
        )
        return f"Duração deste exame: {exame['duracao_minutos']} minutos. {prazo_texto}"

    @rx.event
    def selecionar_convenio(self, valor: str):
        self.form_convenio_id = valor
        if valor:
            self.form_forma_pagamento = "Convênio"
        elif self.form_forma_pagamento == "Convênio":
            self.form_forma_pagamento = ""

    @rx.event
    def selecionar_status(self, valor: str):
        self.form_status = valor

    @rx.event
    def selecionar_status_pagamento(self, valor: str):
        self.form_status_pagamento = valor

    @rx.event
    def atualizar_data_form(self, valor: str):
        self.form_data = valor

    @rx.event
    def atualizar_hora_form(self, valor: str):
        self.form_hora = valor

    @rx.event
    def atualizar_forma_pagamento(self, valor: str):
        self.form_forma_pagamento = valor

    @rx.event
    def atualizar_resultado(self, valor: str):
        self.form_resultado = valor

    @rx.var
    def email_paciente_selecionado(self) -> str:
        for paciente in self.pacientes:
            if paciente["id"] == self.form_paciente_id:
                return paciente.get("email", "") or "Sem e-mail cadastrado"
        return ""

    @rx.var
    def convenio_paciente_selecionado(self) -> str:
        convenio = next((item for item in self.convenios if item["id"] == self.form_convenio_id), None)
        return convenio.get("nome", "Convênio não identificado") if convenio else "Sem convênio"

    @rx.var
    def informacao_valores_exame(self) -> str:
        if not self.form_exame_id:
            return "Selecione um exame para ver o valor e a divisão entre paciente e convênio."
        exame = next((item for item in self.exames if item["id"] == self.form_exame_id), None)
        if not exame:
            return "Não foi possível localizar o valor deste exame."
        try:
            total = Decimal(exame.get("valor_reais", "0"))
        except (InvalidOperation, TypeError):
            return "Não foi possível calcular a divisão do valor deste exame."
        convenio = next((item for item in self.convenios if item["id"] == self.form_convenio_id), None)
        divisao = _divisao_valor_exame(exame, convenio)
        if divisao is None:
            return "Não foi possível calcular a divisão do valor deste exame."
        paciente_centavos, convenio_centavos = divisao
        parte_paciente = Decimal(paciente_centavos) / 100
        parte_convenio = Decimal(convenio_centavos) / 100
        def moeda(valor: Decimal) -> str:
            return format(valor, ",.2f").replace(",", "X").replace(".", ",").replace("X", ".")
        return (
            f"Valor do exame: R$ {moeda(total)}. "
            f"Paciente: R$ {moeda(parte_paciente)}. "
            f"Convênio: R$ {moeda(parte_convenio)}."
        )

    @rx.event
    async def criar_agendamento(self, form_data: dict[str, Any]):
        if self.salvando:
            return
        auth = await self.get_state(AuthState)
        if not tem_permissao(auth.perfil, "agendamento:gerenciar"):
            self.erro_form = "Seu perfil não tem permissão para criar agendamentos."
            return
        token = auth.obter_token()
        if not token:
            self.modal_aberto = False
            yield AuthState.sessao_expirada
            return
        if not self.form_paciente_id or not self.form_medico_id:
            self.erro_form = "Selecione o paciente e o médico."
            return
        if not self.form_data or not self.form_hora:
            self.erro_form = "Informe a data e o horário do agendamento."
            return
        if self.form_forma_pagamento not in FORMAS_PAGAMENTO:
            self.erro_form = "Selecione a forma de pagamento: dinheiro, cartão ou convênio."
            return
        if self.form_forma_pagamento == "Convênio" and not self.form_convenio_id:
            self.erro_form = "Selecione o convênio utilizado neste agendamento."
            return
        paciente_selecionado = next((item for item in self.pacientes if item["id"] == self.form_paciente_id), None)
        if paciente_selecionado and paciente_selecionado.get("codigo_convenio") and not self.form_convenio_id:
            self.erro_form = "O código da carteirinha não corresponde a um convênio cadastrado. Confira o código no cadastro do convênio."
            return
        try:
            paciente_id = int(self.form_paciente_id)
            medico_id = int(self.form_medico_id)
            data_hora = datetime.strptime(f"{self.form_data}T{self.form_hora}", "%Y-%m-%dT%H:%M").astimezone()
        except (TypeError, ValueError, OverflowError, OSError):
            self.erro_form = "Confira o paciente, o médico, a data e o horário informados."
            return

        if not any(item["id"] == str(paciente_id) for item in self.pacientes):
            self.erro_form = "O paciente selecionado não está disponível. Atualize as opções e tente novamente."
            return
        if not any(item["id"] == str(medico_id) for item in self.medicos):
            self.erro_form = "O médico selecionado não está disponível. Atualize as opções e tente novamente."
            return
        duracao_nova = PRAZO_PADRAO_CONSULTA_MINUTOS
        if self.form_exame_id:
            exame_selecionado = next((item for item in self.exames if item["id"] == self.form_exame_id), None)
            duracao_nova = _inteiro_positivo(exame_selecionado.get("duracao_minutos")) if exame_selecionado else None
            if duracao_nova is None:
                self.erro_form = "Este exame não tem duração cadastrada. Informe a duração no cadastro de exames antes de agendar."
                return
        payload: dict[str, Any] = {
            "data_hora": int(data_hora.timestamp() * 1000),
            "status": self.form_status if self.form_status in STATUS_AGENDAMENTO else "Pendente",
            "status_pagamento": self.form_status_pagamento if self.form_status_pagamento in STATUS_PAGAMENTO else "Pendente",
            "paciente_id": paciente_id,
            "medico_id": medico_id,
        }
        if self.form_exame_id:
            if not any(item["id"] == self.form_exame_id for item in self.exames):
                self.erro_form = "O exame selecionado não está disponível. Atualize as opções e tente novamente."
                return
            payload["exame_id"] = int(self.form_exame_id)
        if self.form_convenio_id:
            if not any(item["id"] == self.form_convenio_id for item in self.convenios):
                self.erro_form = "O convênio selecionado não está disponível. Atualize as opções e tente novamente."
                return
            payload["convenio_id"] = int(self.form_convenio_id)
        if self.form_exame_id:
            exame_selecionado = next((item for item in self.exames if item["id"] == self.form_exame_id), None)
            convenio_selecionado = next((item for item in self.convenios if item["id"] == self.form_convenio_id), None)
            divisao = _divisao_valor_exame(exame_selecionado, convenio_selecionado)
            if divisao is None:
                self.erro_form = "Confira o valor cadastrado do exame e o percentual do convênio."
                return
            payload["valor_paciente"] = divisao[0]
            payload["valor_convenio"] = divisao[1]
        payload["forma_pagamento"] = self.form_forma_pagamento
        if self.form_resultado.strip():
            payload["resultado"] = self.form_resultado.strip()

        self.salvando = True
        self.erro_form = ""
        yield
        try:
            conflito = await _conflito_de_agenda(
                token,
                date.fromisoformat(self.form_data),
                medico_id,
                data_hora,
                duracao_nova,
                self.exames,
            )
        except api.SessionExpired:
            self.salvando = False
            self.modal_aberto = False
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.salvando = False
            self.erro_form = "Não foi possível verificar a disponibilidade do médico: " + error.message
            return
        if conflito:
            self.salvando = False
            self.erro_form = conflito
            return
        try:
            await api.request("POST", "/agendamento", token=token, json=payload)
        except api.SessionExpired:
            self.salvando = False
            self.modal_aberto = False
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.salvando = False
            if error.status == 403:
                self.erro_form = "Você não tem permissão para criar agendamentos."
            else:
                self.erro_form = "Não foi possível criar o agendamento. " + error.message
            return

        self.salvando = False
        self.modal_aberto = False
        self.data_agenda = self.form_data
        self.visualizacao = "Dia"
        self.pagina = 1
        self.carregando = True
        yield rx.toast.success("Agendamento criado com sucesso.", position="top-center")
        evento = await self._buscar()
        if evento:
            yield evento

    async def _buscar(self):
        auth = await self.get_state(AuthState)
        token = auth.obter_token()
        if not token:
            self.carregando = False
            return AuthState.sessao_expirada

        data_selecionada = date.fromisoformat(self.data_agenda)
        inicio, fim = periodo_datas(data_selecionada, self.visualizacao)
        params: dict[str, Any] = {
            "data_inicio": timestamp_inicio(inicio),
            "data_fim": timestamp_fim(fim),
            "page": self.pagina,
            "per_page": ITENS_POR_PAGINA,
        }
        if self.busca.strip():
            params["busca"] = self.busca.strip()

        try:
            resultado = await api.request("GET", "/agendamento", token=token, params=params)
            itens = _extrair_lista(resultado)
            if not itens and self.pagina > 1:
                self.pagina -= 1
                params["page"] = self.pagina
                resultado = await api.request("GET", "/agendamento", token=token, params=params)
                itens = _extrair_lista(resultado)

            # Algumas respostas antigas do Xano trazem apenas paciente_id. Carrega a lista
            # uma vez e resolve esses IDs para nomes, sem repetir a chamada a cada página.
            precisa_resolver_nomes = any(
                isinstance(item, dict)
                and not (
                    _nome_relacionado(item.get("paciente") or item.get("Paciente") or item.get("patient"))
                    or _nome_relacionado(item.get("paciente_nome"))
                    or _nome_relacionado(item.get("nome_paciente"))
                    or _nome_relacionado(item.get("nome"))
                )
                and _id_relacao_paciente(item)
                for item in itens
            )
            if precisa_resolver_nomes and not self.pacientes_resolvidos:
                try:
                    resposta_pacientes = await api.request("GET", "/paciente", token=token)
                    self.pacientes_por_id = {
                        str(item.get("id") or item.get("paciente_id")): nome
                        for item in _extrair_lista(resposta_pacientes)
                        if isinstance(item, dict)
                        and (nome := _nome_relacionado(item.get("nome") or item.get("name") or item.get("nome_completo")))
                        and (item.get("id") is not None or item.get("paciente_id") is not None)
                    }
                    self.pacientes_resolvidos = True
                except api.SessionExpired:
                    self.agenda = []
                    self.total_paginas = 1
                    self.tem_proxima_pagina = False
                    self.carregando = False
                    return AuthState.sessao_expirada
                except api.ApiError:
                    # A agenda continua visível; sem permissão para listar pacientes, o Xano
                    # precisa devolver a relação com o nome no próprio GET /agendamento.
                    self.pacientes_por_id = {}
                    self.pacientes_resolvidos = True
            self.total_paginas, self.tem_proxima_pagina = _metadados_paginacao(
                resultado,
                self.pagina,
                len(itens),
            )
            self.agenda = sorted(
                [normalizar_agendamento(item, self.pacientes_por_id) for item in itens if isinstance(item, dict)],
                key=lambda item: item["chave_ordem"],
            )
            self.erro = ""
        except api.SessionExpired:
            self.agenda = []
            self.total_paginas = 1
            self.tem_proxima_pagina = False
            self.carregando = False
            return AuthState.sessao_expirada
        except api.ApiError as error:
            self.agenda = []
            self.total_paginas = 1
            self.tem_proxima_pagina = False
            self.erro = error.message

        self.carregando = False
        return None

    @rx.event
    async def carregar_dados(self):
        self.carregando = True
        self.erro = ""
        yield
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.event
    async def selecionar_visualizacao(self, valor: str):
        if valor not in VISUALIZACOES or valor == self.visualizacao:
            return
        self.visualizacao = valor
        self.pagina = 1
        self.total_paginas = 1
        self.tem_proxima_pagina = False
        self.carregando = True
        yield
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.event
    async def mudar_periodo(self, direcao: int):
        atual = date.fromisoformat(self.data_agenda)
        if self.visualizacao == "Semana":
            atual += timedelta(days=7 * direcao)
        elif self.visualizacao == "Mês":
            primeiro = atual.replace(day=1)
            deslocado = (primeiro - timedelta(days=1)).replace(day=1) if direcao < 0 else (primeiro.replace(day=28) + timedelta(days=4)).replace(day=1)
            atual = deslocado
        else:
            atual += timedelta(days=direcao)
        self.data_agenda = atual.isoformat()
        self.pagina = 1
        self.total_paginas = 1
        self.tem_proxima_pagina = False
        self.carregando = True
        yield
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.event
    async def ir_para_hoje(self):
        self.data_agenda = date.today().isoformat()
        self.pagina = 1
        self.total_paginas = 1
        self.tem_proxima_pagina = False
        self.carregando = True
        yield
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.event
    def atualizar_busca(self, valor: str):
        self.busca = valor

    @rx.event
    async def buscar(self, form_data: dict[str, Any]):
        # O envio do formulário é a fonte confiável do valor final digitado; o
        # evento on_change pode chegar logo antes do submit no mesmo ciclo.
        if "busca" in form_data:
            self.busca = str(form_data.get("busca") or "").strip()
        self.pagina = 1
        self.total_paginas = 1
        self.tem_proxima_pagina = False
        self.carregando = True
        self.erro = ""
        yield
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.event
    def solicitar_remocao(self, identificador: str):
        if identificador:
            self.id_remocao_pendente = identificador

    @rx.event
    def cancelar_remocao(self):
        if not self.removendo:
            self.id_remocao_pendente = ""

    @rx.event
    async def remover_agendamento(self):
        if self.removendo or not self.id_remocao_pendente:
            return
        auth = await self.get_state(AuthState)
        if not tem_permissao(auth.perfil, "agendamento:gerenciar"):
            self.erro = "Seu perfil não tem permissão para remover agendamentos."
            self.id_remocao_pendente = ""
            return
        token = auth.obter_token()
        if not token:
            self.id_remocao_pendente = ""
            yield AuthState.sessao_expirada
            return
        identificador = self.id_remocao_pendente
        self.removendo = True
        self.erro = ""
        yield
        try:
            await api.request("DELETE", f"/agendamento/{identificador}", token=token)
        except api.SessionExpired:
            self.removendo = False
            self.id_remocao_pendente = ""
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.removendo = False
            self.erro = "Não foi possível remover o agendamento. " + error.message
            self.id_remocao_pendente = ""
            return
        self.removendo = False
        self.id_remocao_pendente = ""
        self.carregando = True
        yield rx.toast.success("Agendamento removido.", position="top-center")
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.event
    async def ir_para_pagina(self, pagina: int):
        pagina_nova = min(max(pagina, 1), self.total_paginas)
        if pagina_nova == self.pagina:
            return
        self.pagina = pagina_nova
        self.carregando = True
        yield
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.event
    async def pagina_anterior(self):
        if self.pagina <= 1:
            return
        self.pagina -= 1
        self.carregando = True
        yield
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.event
    async def proxima_pagina(self):
        if not self.tem_proxima_pagina:
            return
        self.pagina += 1
        self.carregando = True
        yield
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.var
    def periodo_exibido(self) -> str:
        selecionada = date.fromisoformat(self.data_agenda)
        inicio, fim = periodo_datas(selecionada, self.visualizacao)
        return _texto_periodo(inicio, fim, self.visualizacao)

    @rx.var
    def paginas(self) -> list[int]:
        total = max(self.total_paginas, self.pagina)
        if total <= 5:
            return list(range(1, total + 1))
        inicio = min(max(1, self.pagina - 2), total - 4)
        return list(range(inicio, inicio + 5))

    @rx.var
    def linhas_visiveis(self) -> list[dict[str, str]]:
        return self.agenda


def opcao_visualizacao(rotulo: str) -> rx.Component:
    selecionada = AgendamentoState.visualizacao == rotulo
    return rx.el.button(
        rotulo,
        type="button",
        on_click=AgendamentoState.selecionar_visualizacao(rotulo),
        aria_pressed=selecionada,
        style={
            "border": "none",
            "borderRadius": "9999px",
            "padding": "0.45rem 1rem",
            "cursor": "pointer",
            "fontFamily": "Inter",
            "fontSize": "0.9rem",
            "fontWeight": "600",
            "color": "#05589F",
            "background": "rgba(106,158,204,0.2)",
        },
        background=rx.cond(selecionada, "rgba(5,88,159,0.28)", "rgba(106,158,204,0.12)"),
    )


def seletor_visualizacao() -> rx.Component:
    return rx.hstack(*[opcao_visualizacao(rotulo) for rotulo in VISUALIZACOES], spacing="2", align="center")


def barra_data() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon(tag="chevron-left", size=18),
            type="button",
            aria_label="Período anterior",
            on_click=AgendamentoState.mudar_periodo(-1),
            variant="ghost",
            color="#05589F",
        ),
        rx.text(
            AgendamentoState.periodo_exibido,
            color="#05589F",
            font_family="Inter",
            font_size=rx.breakpoints(initial="0.9rem", md="1rem"),
            font_weight="600",
            text_align="center",
        ),
        rx.button(
            rx.icon(tag="chevron-right", size=18),
            type="button",
            aria_label="Próximo período",
            on_click=AgendamentoState.mudar_periodo(1),
            variant="ghost",
            color="#05589F",
        ),
        rx.button(
            "Hoje",
            type="button",
            on_click=AgendamentoState.ir_para_hoje,
            variant="soft",
            color="#05589F",
            border_radius="9999px",
        ),
        width="100%",
        justify="center",
        padding="0.35rem 0.5rem",
        border_radius="9999px",
        background="rgba(106,158,204,0.16)",
        wrap="wrap",
        spacing="2",
    )


def linha_agenda(linha: rx.Var[dict[str, str]]) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(linha["hora"], color="#05589F", font_family="Inter", font_weight="600"),
            rx.text(linha["data"], color="#6A9ECC", font_family="Inter", font_size="0.78rem"),
            spacing="0",
            align="start",
            width="150px",
            flex_shrink="0",
        ),
        rx.vstack(
            rx.text(linha["paciente"], color="#05589F", font_family="Inter", font_size="0.95rem", font_weight="600"),
            rx.text(linha["detalhe"], color="#6A9ECC", font_family="Inter", font_size="0.85rem"),
            spacing="1",
            align="start",
            min_width="0",
        ),
        rx.spacer(),
        status_badge(linha["status"]),
        rx.cond(
            AuthState.pode_gerenciar_agendamento & (linha["id"] != ""),
            rx.button(
                rx.icon(tag="trash-2", size=17),
                "Remover",
                type="button",
                aria_label="Remover agendamento",
                on_click=AgendamentoState.solicitar_remocao(linha["id"]),
                variant="soft",
                color_scheme="red",
                border_radius="9999px",
                size="2",
            ),
        ),
        width="100%",
        min_height="4rem",
        padding="0.75rem 0",
        border_bottom="1px solid #E6F2F7",
        align="center",
        spacing="3",
        flex_wrap=rx.breakpoints(initial="wrap", md="nowrap"),
    )


def botao_pagina(numero: rx.Var[int]) -> rx.Component:
    selecionada = AgendamentoState.pagina == numero
    return rx.el.button(
        rx.text(numero),
        type="button",
        aria_label="Ir para página",
        on_click=AgendamentoState.ir_para_pagina(numero),
        style={
            "minWidth": "2rem",
            "height": "2rem",
            "padding": "0 0.5rem",
            "border": "1px solid #A7D8F0",
            "borderRadius": "8px",
            "cursor": "pointer",
            "fontFamily": "Inter",
            "fontSize": "0.8rem",
            "fontWeight": "600",
            "color": "#05589F",
        },
        background=rx.cond(selecionada, "#A7D8F0", "#FFFFFF"),
    )


def paginacao() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon(tag="chevron-left", size=18),
            type="button",
            aria_label="Página anterior",
            on_click=AgendamentoState.pagina_anterior,
            disabled=AgendamentoState.pagina <= 1,
            variant="ghost",
            color="#05589F",
        ),
        rx.foreach(AgendamentoState.paginas, botao_pagina),
        rx.button(
            rx.icon(tag="chevron-right", size=18),
            type="button",
            aria_label="Próxima página",
            on_click=AgendamentoState.proxima_pagina,
            disabled=AgendamentoState.tem_proxima_pagina == False,
            variant="ghost",
            color="#05589F",
        ),
        spacing="2",
        align="center",
        justify="center",
        width="100%",
        padding_top="1rem",
    )


def campo_modal(rotulo: str, componente: rx.Component, obrigatorio: bool = False) -> rx.Component:
    return rx.vstack(
        rx.text(
            f"{rotulo}{' *' if obrigatorio else ''}",
            color="#05589F",
            font_family="Inter",
            font_size="0.9rem",
            font_weight="600",
        ),
        componente,
        spacing="1",
        width="100%",
        align="stretch",
    )


def seletor_registros(
    placeholder: str,
    registros: rx.Var[list[dict[str, str]]],
    valor: rx.Var[str],
    ao_alterar: Any,
    obrigatorio: bool = False,
) -> rx.Component:
    return rx.select.root(
        rx.select.trigger(placeholder=placeholder, width="100%"),
        rx.select.content(
            rx.select.group(
                rx.foreach(
                    registros,
                    lambda registro: rx.select.item(registro["rotulo"], value=registro["id"]),
                ),
            ),
        ),
        value=valor,
        on_change=ao_alterar,
        required=obrigatorio,
        width="100%",
    )


def novo_agendamento_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.dialog.title(
                        "Novo Agendamento",
                        color="#05589F",
                        font_family="Poppins",
                        font_size="1.5rem",
                        font_weight="600",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Informe paciente, médico, data e horário. O Xano processa a confirmação por e-mail do paciente.",
                        color="#6A9ECC",
                        font_family="Inter",
                        font_size="0.9rem",
                        line_height="1.5",
                    ),
                    rx.cond(
                        AgendamentoState.carregando_opcoes,
                        rx.hstack(
                            rx.spinner(size="3", color="#05589F"),
                            rx.text("Carregando cadastros do Xano...", color="#6A9ECC", font_family="Inter"),
                            spacing="3",
                            width="100%",
                        ),
                    ),
                    rx.cond(
                        AgendamentoState.erro_opcoes != "",
                        rx.callout(AgendamentoState.erro_opcoes, icon="triangle_alert", color_scheme="red", width="100%"),
                    ),
                    rx.cond(
                        AgendamentoState.erro_opcoes_opcionais != "",
                        rx.callout(AgendamentoState.erro_opcoes_opcionais, icon="info", color_scheme="blue", width="100%"),
                    ),
                    rx.grid(
                        campo_modal(
                            "Paciente",
                            seletor_registros(
                                "Selecione um paciente",
                                AgendamentoState.pacientes,
                                AgendamentoState.form_paciente_id,
                                AgendamentoState.selecionar_paciente,
                                obrigatorio=True,
                            ),
                            obrigatorio=True,
                        ),
                        campo_modal(
                            "Médico",
                            seletor_registros(
                                "Selecione um médico",
                                AgendamentoState.medicos,
                                AgendamentoState.form_medico_id,
                                AgendamentoState.selecionar_medico,
                                obrigatorio=True,
                            ),
                            obrigatorio=True,
                        ),
                        campo_modal(
                            "Data",
                            rx.input(
                                type="date",
                                value=AgendamentoState.form_data,
                                on_change=AgendamentoState.atualizar_data_form,
                                required=True,
                                width="100%",
                                color="#05589F",
                                border="1px solid #A7D8F0",
                                border_radius="12px",
                                background="#FFFFFF",
                            ),
                            obrigatorio=True,
                        ),
                        campo_modal(
                            "Horário",
                            rx.input(
                                type="time",
                                value=AgendamentoState.form_hora,
                                on_change=AgendamentoState.atualizar_hora_form,
                                required=True,
                                width="100%",
                                color="#05589F",
                                border="1px solid #A7D8F0",
                                border_radius="12px",
                                background="#FFFFFF",
                            ),
                            obrigatorio=True,
                        ),
                        campo_modal(
                            "Status",
                            rx.select(
                                list(STATUS_AGENDAMENTO),
                                value=AgendamentoState.form_status,
                                on_change=AgendamentoState.selecionar_status,
                                width="100%",
                            ),
                        ),
                        campo_modal(
                            "Status do pagamento",
                            rx.select(
                                list(STATUS_PAGAMENTO),
                                value=AgendamentoState.form_status_pagamento,
                                on_change=AgendamentoState.selecionar_status_pagamento,
                                width="100%",
                            ),
                        ),
                        campo_modal(
                            "Exame (opcional)",
                            seletor_registros(
                                "Selecione um exame",
                                AgendamentoState.exames,
                                AgendamentoState.form_exame_id,
                                AgendamentoState.selecionar_exame,
                            ),
                        ),
                        rx.cond(
                            AgendamentoState.form_exame_id != "",
                            rx.text(
                                AgendamentoState.informacao_duracao_exame,
                                color="#38566B",
                                font_family="Inter",
                                font_size="0.85rem",
                                line_height="1.4",
                            ),
                            rx.text(
                                "Sem exame selecionado: a agenda reserva 30 minutos para este atendimento.",
                                color="#38566B",
                                font_family="Inter",
                                font_size="0.85rem",
                                line_height="1.4",
                            ),
                        ),
                        rx.cond(
                            AgendamentoState.form_convenio_id != "",
                            campo_modal("Convênio identificado pela carteirinha", rx.text(AgendamentoState.convenio_paciente_selecionado, color="#05589F", font_family="Inter")),
                            campo_modal("Convênio", rx.text("Paciente sem convênio cadastrado", color="#6A9ECC", font_family="Inter")),
                        ),
                        campo_modal(
                            "Divisão do valor do exame",
                            rx.text(
                                AgendamentoState.informacao_valores_exame,
                                color="#38566B",
                                font_family="Inter",
                                font_size="0.9rem",
                                line_height="1.5",
                            ),
                        ),
                        campo_modal(
                            "Forma de pagamento",
                            rx.select(
                                list(FORMAS_PAGAMENTO),
                                value=AgendamentoState.form_forma_pagamento,
                                on_change=AgendamentoState.atualizar_forma_pagamento,
                                width="100%",
                            ),
                            obrigatorio=True,
                        ),
                        columns=rx.breakpoints(initial="1", md="2"),
                        spacing="4",
                        width="100%",
                    ),
                    rx.cond(
                        AgendamentoState.form_paciente_id != "",
                        rx.callout(
                            rx.cond(
                                AgendamentoState.email_paciente_selecionado == "Sem e-mail cadastrado",
                                "Paciente sem e-mail cadastrado. Atualize o cadastro para que receba a confirmação do agendamento.",
                                "A confirmação será processada pelo Xano para: " + AgendamentoState.email_paciente_selecionado,
                            ),
                            icon="mail",
                            color_scheme="blue",
                            width="100%",
                        ),
                    ),
                    campo_modal(
                        "Resultado ou observações (opcional)",
                        rx.text_area(
                            value=AgendamentoState.form_resultado,
                            on_change=AgendamentoState.atualizar_resultado,
                            placeholder="Observações relacionadas ao atendimento...",
                            width="100%",
                            min_height="90px",
                            resize="vertical",
                            color="#05589F",
                            border="1px solid #A7D8F0",
                            border_radius="12px",
                            background="#FFFFFF",
                        ),
                    ),
                    rx.cond(
                        AgendamentoState.pacientes.length() == 0,
                        rx.callout("Nenhum paciente disponível para agendar.", icon="info", color_scheme="blue", width="100%"),
                    ),
                    rx.cond(
                        AgendamentoState.medicos.length() == 0,
                        rx.callout("Nenhum médico disponível para agendar.", icon="info", color_scheme="blue", width="100%"),
                    ),
                    rx.cond(
                        AgendamentoState.erro_form != "",
                        rx.callout(AgendamentoState.erro_form, icon="triangle_alert", color_scheme="red", width="100%"),
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancelar",
                            type="button",
                            on_click=AgendamentoState.fechar_modal,
                            disabled=AgendamentoState.salvando,
                            variant="outline",
                            color="#05589F",
                            border_radius="9999px",
                            size="3",
                        ),
                        rx.button(
                            rx.cond(AgendamentoState.salvando, "Salvando...", "Criar agendamento"),
                            type="submit",
                            loading=AgendamentoState.salvando,
                            disabled=AgendamentoState.salvando
                            | AgendamentoState.carregando_opcoes
                            | (AgendamentoState.pacientes.length() == 0)
                            | (AgendamentoState.medicos.length() == 0),
                            background="#05589F",
                            color="#FFFFFF",
                            border_radius="9999px",
                            size="3",
                        ),
                        justify="end",
                        spacing="3",
                        width="100%",
                        padding_top="0.5rem",
                        flex_wrap="wrap",
                    ),
                    spacing="4",
                    width="100%",
                    align="stretch",
                ),
                on_submit=AgendamentoState.criar_agendamento,
                reset_on_submit=False,
            ),
            width="calc(100vw - 2rem)",
            max_width="720px",
            max_height="90vh",
            overflow_y="auto",
            border_radius="20px",
            padding=rx.breakpoints(initial="1.25rem", md="1.75rem"),
            box_sizing="border-box",
        ),
        open=AgendamentoState.modal_aberto,
        on_open_change=AgendamentoState.alterar_modal,
    )


def agendamento() -> rx.Component:
    return rx.hstack(
        Sidebar(active="Agendamentos"),
        rx.vstack(
            Topbar(),
            novo_agendamento_modal(),
            rx.dialog.root(
                rx.dialog.content(
                    rx.vstack(
                        rx.dialog.title("Remover agendamento?", color="#05589F", font_family="Poppins"),
                        rx.dialog.description("Esta ação excluirá o agendamento da agenda.", color="#6A9ECC", font_family="Inter"),
                        rx.hstack(
                            rx.button("Cancelar", type="button", on_click=AgendamentoState.cancelar_remocao, variant="outline", color="#05589F", border_radius="9999px"),
                            rx.button("Remover", type="button", on_click=AgendamentoState.remover_agendamento, loading=AgendamentoState.removendo, color_scheme="red", border_radius="9999px"),
                            justify="end",
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    max_width="420px",
                    border_radius="20px",
                    padding="1.5rem",
                ),
                open=AgendamentoState.id_remocao_pendente != "",
            ),
            rx.vstack(
                rx.hstack(
                    rx.heading("Agenda médica", color="#05589F", font_family="Poppins", font_size=rx.breakpoints(initial="1.7rem", md="2.1rem"), font_weight="600"),
                    rx.spacer(),
                    rx.cond(
                        AuthState.pode_gerenciar_agendamento,
                        rx.button(
                            "+ Novo Agendamento",
                            type="button",
                            on_click=AgendamentoState.abrir_modal,
                            background="#05589F",
                            color="#FFFFFF",
                            border_radius="9999px",
                            font_family="Inter",
                            font_weight="600",
                            white_space="nowrap",
                        ),
                    ),
                    seletor_visualizacao(),
                    width="100%",
                    align="center",
                    wrap="wrap",
                ),
                barra_data(),
                rx.form(
                    rx.hstack(
                        rx.input(
                            name="busca",
                            value=AgendamentoState.busca,
                            on_change=AgendamentoState.atualizar_busca,
                            placeholder="Buscar paciente, médico ou status...",
                            aria_label="Buscar na agenda",
                            width="auto",
                            flex="1",
                            min_width="0",
                            border="1px solid #A7D8F0",
                            border_radius="9999px",
                            background="#FFFFFF",
                            color="#05589F",
                            padding="0.7rem 1rem",
                        ),
                        rx.button(
                            rx.icon(tag="search", size=18),
                            "Buscar",
                            type="submit",
                            background="#05589F",
                            color="#FFFFFF",
                            border_radius="9999px",
                        ),
                        width="100%",
                        spacing="3",
                    ),
                    on_submit=AgendamentoState.buscar,
                    width="100%",
                ),
                spacing="4",
                align="start",
                width="100%",
            ),
            rx.box(
                rx.vstack(
                    rx.cond(
                        AgendamentoState.erro != "",
                        rx.callout(AgendamentoState.erro, icon="triangle_alert", color_scheme="red", width="100%"),
                    ),
                    rx.cond(
                        AgendamentoState.carregando,
                        rx.text("Carregando agenda do Xano...", color="#6A9ECC", padding_y="1rem"),
                        rx.cond(
                            AgendamentoState.linhas_visiveis.length() > 0,
                            rx.vstack(rx.foreach(AgendamentoState.linhas_visiveis, linha_agenda), paginacao(), spacing="1", width="100%"),
                            rx.text("Nenhum agendamento encontrado neste período.", color="#6A9ECC", padding_y="1rem"),
                        ),
                    ),
                    spacing="2",
                    width="100%",
                    align="stretch",
                ),
                width="100%",
                padding=rx.breakpoints(initial="1rem", md="1.5rem"),
                border_radius="20px",
                background="#FFFFFF",
                box_shadow="0 8px 24px rgba(5,88,159,0.08)",
                box_sizing="border-box",
            ),
            spacing="5",
            align="start",
            width="100%",
            max_width="1200px",
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
        on_mount=AgendamentoState.carregar_dados,
    )
