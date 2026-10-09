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
    modal_cadastro,
    mensagem_erro,
    tela_cadastro,
    texto,
)
from ProjetoCl_nicaCardiologia.patients import patient_status_badge


class MedicosState(CadastroState, rx.State):
    ENDPOINT: ClassVar[str] = "/medico"
    LIST_ENDPOINT: ClassVar[str] = "/lista_medico"
    NOME_LISTA: ClassVar[str] = "os médicos"
    VAZIO: ClassVar[str] = "Nenhum médico cadastrado"
    VAZIO_BUSCA: ClassVar[str] = "Nenhum médico encontrado para a busca"

    form_nome: str = ""
    form_crm: str = ""
    form_especialidade: str = ""
    atualizando_status_id: str = ""

    @rx.event
    def set_form_nome(self, value: str):
        self.form_nome = value

    @rx.event
    def set_form_crm(self, value: str):
        self.form_crm = value

    @rx.event
    def set_form_especialidade(self, value: str):
        self.form_especialidade = value

    @rx.event
    async def alternar_status(self, medico_id: str, status_atual: str):
        if not medico_id or self.atualizando_status_id:
            return
        auth = await self.get_state(AuthState)
        if not tem_permissao(auth.perfil, "medico:gerenciar"):
            yield rx.toast.error("Somente o administrador pode alterar o status do médico.", position="top-center")
            return
        token = auth.obter_token()
        if not token:
            yield AuthState.sessao_expirada
            return

        status = status_atual.strip().casefold()
        if status in ("ativo", "active", "true", "1"):
            novo_status = "Inativo"
        elif status in ("inativo", "inactive", "false", "0", ""):
            novo_status = "Ativo"
        else:
            yield rx.toast.error("O médico não tem um status reconhecido no Xano.", position="top-center")
            return

        self.atualizando_status_id = medico_id
        yield
        try:
            await api.request(
                "PATCH",
                "/medico",
                token=token,
                json={"medico_id": medico_id, "Status": novo_status},
            )
        except api.SessionExpired:
            self.atualizando_status_id = ""
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.atualizando_status_id = ""
            yield rx.toast.error(mensagem_erro(error, "alterar o status do médico"), position="top-center")
            return

        self.atualizando_status_id = ""
        self.carregando = True
        yield rx.toast.success(f"Status do médico atualizado para {novo_status.lower()}.", position="top-center")
        evento = await self._buscar()
        if evento:
            yield evento

    def _normalizar(self, item: dict[str, Any]) -> dict[str, str]:
        # O Xano devolve `Status` (S maiúsculo) e também um `status` herdado de outra tabela.
        status_original = texto(campo(item, "Status", "status")).strip().casefold()
        if status_original in ("ativo", "active", "true", "1"):
            status = "ativo"
        elif status_original in ("inativo", "inactive", "false", "0"):
            status = "inativo"
        else:
            status = status_original
        return {
            "id": texto(campo(item, "id", "medico_id")),
            "name": texto(campo(item, "nome", "name")),
            "especialidade": texto(campo(item, "especialidade", "specialty")),
            "crm": texto(campo(item, "crm", "CRM")),
            "status": status,
        }

    def _validar(self) -> tuple[dict[str, Any] | None, str]:
        nome = self.form_nome.strip()
        crm = self.form_crm.strip()
        especialidade = self.form_especialidade.strip()
        if not nome or not crm:
            return None, "Preencha nome e CRM."
        payload: dict[str, Any] = {"nome": nome, "crm": crm}
        if especialidade:
            payload["especialidade"] = especialidade
        return payload, ""

    def _limpar_formulario(self) -> None:
        self.form_nome = ""
        self.form_crm = ""
        self.form_especialidade = ""


def medicos_table_header() -> rx.Component:
    return rx.hstack(
        cabecalho_coluna("Nome", "28%"),
        cabecalho_coluna("Especialidade", "24%"),
        cabecalho_coluna("CRM", "18%"),
        cabecalho_coluna("Status", "16%"),
        cabecalho_coluna("Ação", "14%"),
        width="100%",
        padding="0 0.5rem 0.75rem",
        display=rx.breakpoints(initial="none", md="flex"),
        border_bottom="1px solid #E6F2F7",
        box_sizing="border-box",
    )


def medico_row(medico: rx.Var[dict[str, str]]) -> rx.Component:
    return rx.hstack(
        celula_responsiva("Nome", rx.text(medico["name"], color="#05589F", font_family="Inter", font_weight="600"), "28%"),
        celula_responsiva("Especialidade", rx.text(medico["especialidade"], color="#6A9ECC", font_family="Inter", font_size="0.9rem"), "24%"),
        celula_responsiva("CRM", rx.text(medico["crm"], color="#6A9ECC", font_family="Inter", font_size="0.9rem"), "18%"),
        celula_responsiva(
            "Status",
            rx.box(
                rx.cond(
                    medico["status"] != "",
                    patient_status_badge(medico["status"]),
                    rx.text("—", color="#6A9ECC", font_family="Inter", font_size="0.9rem"),
                ),
            ),
            "16%",
        ),
        celula_responsiva(
            "Ação",
            rx.button(
                rx.cond(medico["status"] == "ativo", "Desativar", "Ativar"),
                type="button",
                on_click=MedicosState.alternar_status(medico["id"], medico["status"]),
                disabled=(medico["id"] == "") | (MedicosState.atualizando_status_id != ""),
                loading=MedicosState.atualizando_status_id == medico["id"],
                variant="soft",
                background=rx.cond(medico["status"] == "ativo", "#FDE8E8", "#DCFCE7"),
                color=rx.cond(medico["status"] == "ativo", "#B42318", "#166534"),
                border_radius="9999px",
                size="2",
            ),
            "14%",
        ),
        width="100%",
        padding="0.85rem 0.5rem",
        align="start",
        flex_wrap=rx.breakpoints(initial="wrap", md="nowrap"),
        spacing=rx.breakpoints(initial="2", md="0"),
        border_bottom="1px solid #EEF4F7",
        box_sizing="border-box",
    )


def novo_medico_modal() -> rx.Component:
    return modal_cadastro(
        MedicosState,
        "Novo Médico",
        campo_input("Nome", MedicosState.form_nome, MedicosState.set_form_nome, obrigatorio=True, placeholder="Nome completo"),
        campo_input("CRM", MedicosState.form_crm, MedicosState.set_form_crm, obrigatorio=True, placeholder="Ex.: 12345SP"),
        campo_input("Especialidade", MedicosState.form_especialidade, MedicosState.set_form_especialidade, placeholder="Ex.: Cardiologista"),
    )


def medicos() -> rx.Component:
    return tela_cadastro(
        MedicosState,
        ativo="Médicos",
        titulo="Médicos",
        busca="Buscar Médico",
        botao="+ Novo Médico",
        cabecalho=medicos_table_header(),
        linha=medico_row,
        modal=novo_medico_modal(),
    )
