from typing import Any, ClassVar

import reflex as rx

from ProjetoCl_nicaCardiologia import api
from ProjetoCl_nicaCardiologia.auth import AuthState, tem_permissao
from ProjetoCl_nicaCardiologia.cadastros import (
    CadastroState,
    celula_responsiva,
    cabecalho_coluna,
    campo,
    campo_input,
    data_nascimento_valida,
    formatar_cpf,
    formatar_data,
    formatar_telefone,
    mascara_cpf,
    mascara_telefone,
    modal_cadastro,
    so_digitos,
    tela_cadastro,
    texto,
)


class PatientsState(CadastroState, rx.State):
    ENDPOINT: ClassVar[str] = "/paciente"
    NOME_LISTA: ClassVar[str] = "os pacientes"
    VAZIO: ClassVar[str] = "Nenhum paciente cadastrado"
    VAZIO_BUSCA: ClassVar[str] = "Nenhum paciente encontrado para a busca"

    form_nome: str = ""
    form_email: str = ""
    form_cpf: str = ""
    form_nascimento: str = ""
    form_telefone: str = ""
    form_carteirinha: str = ""
    paciente_remocao_id: str = ""
    removendo_paciente: bool = False
    erro_remocao: str = ""

    @rx.event
    def set_form_nome(self, value: str):
        self.form_nome = value

    @rx.event
    def set_form_email(self, value: str):
        self.form_email = value

    @rx.event
    def set_form_cpf(self, value: str):
        self.form_cpf = mascara_cpf(value)

    @rx.event
    def set_form_nascimento(self, value: str):
        self.form_nascimento = value

    @rx.event
    def set_form_telefone(self, value: str):
        self.form_telefone = mascara_telefone(value)

    @rx.event
    def set_form_carteirinha(self, value: str):
        digitos = so_digitos(value)[:17]
        self.form_carteirinha = f"{digitos[:14]}-{digitos[14:]}" if len(digitos) > 14 else digitos

    @rx.event
    def solicitar_remocao_paciente(self, identificador: str):
        if identificador:
            self.paciente_remocao_id = identificador
            self.erro_remocao = ""

    @rx.event
    def cancelar_remocao_paciente(self):
        if not self.removendo_paciente:
            self.paciente_remocao_id = ""
            self.erro_remocao = ""

    @rx.event
    async def remover_paciente(self):
        if self.removendo_paciente or not self.paciente_remocao_id:
            return
        auth = await self.get_state(AuthState)
        if not tem_permissao(auth.perfil, "paciente:gerenciar"):
            self.erro_remocao = "Seu perfil não tem permissão para remover pacientes."
            self.paciente_remocao_id = ""
            return
        token = auth.obter_token()
        if not token:
            self.paciente_remocao_id = ""
            yield AuthState.sessao_expirada
            return
        identificador = self.paciente_remocao_id
        self.removendo_paciente = True
        self.erro_remocao = ""
        yield
        try:
            await api.request("DELETE", f"/paciente/{identificador}", token=token)
        except api.SessionExpired:
            self.removendo_paciente = False
            self.paciente_remocao_id = ""
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.removendo_paciente = False
            if error.status in (404, 405):
                self.erro_remocao = (
                    "O Xano ainda não disponibiliza DELETE /paciente/{paciente_id} "
                    f"(HTTP {error.status}). Crie essa rota no Xano com autenticação e permissão "
                    "para administrador/secretaria para habilitar a exclusão."
                )
            elif error.status == 409:
                self.erro_remocao = "O Xano recusou a exclusão porque o paciente possui registros vinculados."
            else:
                self.erro_remocao = "Não foi possível remover o paciente. " + error.message
            self.paciente_remocao_id = ""
            return
        self.removendo_paciente = False
        self.paciente_remocao_id = ""
        self.carregando = True
        yield rx.toast.success("Paciente removido.", position="top-center")
        evento = await self._buscar()
        if evento:
            yield evento

    def _normalizar(self, item: dict[str, Any]) -> dict[str, str]:
        carteirinha = so_digitos(campo(item, "numero_carteirinha", "carteirinha_convenio", "carteirinha"))
        return {
            "id": str(campo(item, "id", "paciente_id") or ""),
            "name": texto(campo(item, "nome", "name", "nome_completo")),
            "email": texto(campo(item, "email", "e-mail")),
            "cpf": formatar_cpf(campo(item, "cpf")),
            "phone": formatar_telefone(campo(item, "telefone", "phone", "celular")),
            "carteirinha": f"{carteirinha[:14]}-{carteirinha[14:]}" if len(carteirinha) == 17 else "",
            "birth": formatar_data(campo(item, "data_nascimento", "nascimento", "birth_date")),
        }

    def _validar(self) -> tuple[dict[str, Any] | None, str]:
        nome = self.form_nome.strip()
        email = self.form_email.strip().lower()
        cpf = so_digitos(self.form_cpf)
        telefone = so_digitos(self.form_telefone)
        carteirinha = so_digitos(self.form_carteirinha)
        if not nome or not email or not cpf or not self.form_nascimento.strip():
            return None, "Preencha nome, e-mail, CPF e data de nascimento."
        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            return None, "Informe um endereço de e-mail válido."
        if len(cpf) != 11:
            return None, "Informe um CPF com 11 dígitos."
        nascimento = data_nascimento_valida(self.form_nascimento)
        if nascimento is None:
            return None, "Informe uma data de nascimento válida (até hoje)."
        if telefone and len(telefone) not in (10, 11):
            return None, "Informe o telefone com DDD (10 ou 11 dígitos)."
        if carteirinha and len(carteirinha) != 17:
            return None, "A carteirinha do convênio deve conter 17 dígitos (14 + código de 3 dígitos)."
        payload: dict[str, Any] = {"nome": nome, "email": email, "cpf": cpf, "data_nascimento": nascimento}
        if telefone:
            payload["telefone"] = telefone
        if carteirinha:
            payload["numero_carteirinha"] = carteirinha
        return payload, ""

    def _limpar_formulario(self) -> None:
        self.form_nome = ""
        self.form_email = ""
        self.form_cpf = ""
        self.form_nascimento = ""
        self.form_telefone = ""
        self.form_carteirinha = ""


def patient_status_badge(status: rx.Var[str]) -> rx.Component:
    return rx.text(
        status,
        color=rx.cond(status == "ativo", "#05589F", "#5C6B7A"),
        background=rx.cond(status == "ativo", "rgba(136,224,193,0.3)", "rgba(154,164,178,0.25)"),
        padding="0.3rem 0.9rem",
        border_radius="9999px",
        font_family="Inter",
        font_size="0.8rem",
        font_weight="600",
        width="fit-content",
    )


def patients_table_header() -> rx.Component:
    return rx.hstack(
        cabecalho_coluna("Nome", "18%"),
        cabecalho_coluna("E-mail", "19%"),
        cabecalho_coluna("CPF", "12%"),
        cabecalho_coluna("Telefone", "12%"),
        cabecalho_coluna("Carteirinha", "15%"),
        cabecalho_coluna("Data de nascimento", "14%"),
        cabecalho_coluna("Ações", "10%"),
        width="100%",
        padding="0 0.75rem 0.75rem",
        display=rx.breakpoints(initial="none", md="flex"),
        border_bottom="1px solid #E6F2F7",
        box_sizing="border-box",
    )


def patient_row(patient: rx.Var[dict[str, str]]) -> rx.Component:
    return rx.hstack(
        celula_responsiva("Nome", rx.text(patient["name"], color="#05589F", font_family="Inter", font_weight="600"), "18%"),
        celula_responsiva("E-mail", rx.text(patient["email"], color="#38566B", font_family="Inter", font_size="0.9rem", word_break="break-word"), "19%"),
        celula_responsiva("CPF", rx.text(patient["cpf"], color="#6A9ECC", font_family="Inter", font_size="0.9rem"), "12%"),
        celula_responsiva("Telefone", rx.text(patient["phone"], color="#6A9ECC", font_family="Inter", font_size="0.9rem"), "12%"),
        celula_responsiva("Carteirinha", rx.text(rx.cond(patient["carteirinha"] != "", patient["carteirinha"], "—"), color="#6A9ECC", font_family="Inter", font_size="0.85rem"), "15%"),
        celula_responsiva("Data de nascimento", rx.text(patient["birth"], color="#6A9ECC", font_family="Inter", font_size="0.9rem"), "14%"),
        rx.cond(
            AuthState.rotas_permitidas.contains("/pacientes") & (patient["id"] != ""),
            rx.button(
                rx.icon(tag="trash-2", size=17),
                "Remover",
                type="button",
                aria_label="Remover paciente",
                on_click=PatientsState.solicitar_remocao_paciente(patient["id"]),
                variant="soft",
                color_scheme="red",
                border_radius="9999px",
                size="2",
                width="10%",
            ),
        ),
        width="100%",
        padding=rx.breakpoints(initial="1rem 0.75rem", md="1rem 0.75rem"),
        align=rx.breakpoints(initial="start", md="center"),
        flex_wrap=rx.breakpoints(initial="wrap", md="nowrap"),
        spacing=rx.breakpoints(initial="2", md="0"),
        border_bottom="1px solid #EEF4F7",
        box_sizing="border-box",
    )


def novo_paciente_modal() -> rx.Component:
    return modal_cadastro(
        PatientsState,
        "Novo Paciente",
        campo_input("Nome", PatientsState.form_nome, PatientsState.set_form_nome, obrigatorio=True, placeholder="Nome completo"),
        campo_input("E-mail", PatientsState.form_email, PatientsState.set_form_email, obrigatorio=True, placeholder="paciente@exemplo.com", type="email"),
        campo_input("CPF", PatientsState.form_cpf, PatientsState.set_form_cpf, obrigatorio=True, placeholder="000.000.000-00", input_mode="numeric"),
        campo_input(
            "Data de nascimento",
            PatientsState.form_nascimento,
            PatientsState.set_form_nascimento,
            obrigatorio=True,
            type="date",
        ),
        campo_input("Telefone", PatientsState.form_telefone, PatientsState.set_form_telefone, placeholder="(00) 00000-0000", input_mode="tel"),
        campo_input(
            "Carteirinha do convênio (opcional)",
            PatientsState.form_carteirinha,
            PatientsState.set_form_carteirinha,
            placeholder="12345678912345-007",
            input_mode="numeric",
            max_length=18,
        ),
    )


def patients() -> rx.Component:
    return rx.fragment(
        tela_cadastro(
            PatientsState,
            ativo="Pacientes",
            titulo="Pacientes",
            busca="Buscar paciente",
            botao="+ Novo Paciente",
            cabecalho=patients_table_header(),
            linha=patient_row,
            modal=novo_paciente_modal(),
            largura_maxima="1180px",
        ),
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.dialog.title("Remover paciente?", color="#05589F", font_family="Poppins"),
                    rx.dialog.description("A exclusão pode ser bloqueada se houver agendamentos ou prescrições vinculados.", color="#6A9ECC", font_family="Inter"),
                    rx.cond(
                        PatientsState.erro_remocao != "",
                        rx.callout(PatientsState.erro_remocao, icon="triangle_alert", color_scheme="red", width="100%"),
                    ),
                    rx.hstack(
                        rx.button("Cancelar", type="button", on_click=PatientsState.cancelar_remocao_paciente, variant="outline", color="#05589F", border_radius="9999px"),
                        rx.button("Remover", type="button", on_click=PatientsState.remover_paciente, loading=PatientsState.removendo_paciente, color_scheme="red", border_radius="9999px"),
                        justify="end",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                max_width="460px",
                border_radius="20px",
                padding="1.5rem",
            ),
            open=(PatientsState.paciente_remocao_id != "") | (PatientsState.erro_remocao != ""),
        ),
    )
