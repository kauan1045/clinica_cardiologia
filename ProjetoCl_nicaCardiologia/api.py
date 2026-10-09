import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()

TIMEOUT = httpx.Timeout(10.0)
LOGIN_FALLBACK_MESSAGE = "Email ou senha inválidos."
SESSION_EXPIRED_MESSAGE = "Sessão expirada. Entre novamente."
UNEXPECTED_RESPONSE_MESSAGE = "Resposta inesperada do servidor."
LOGIN_EMPTY_MESSAGE = "O servidor não retornou o token de acesso. Contate o administrador do sistema."
SENDGRID_AUTHORIZATION_INVALID_MESSAGE = "Não foi possível enviar o e-mail agora. Tente novamente mais tarde."
TOKEN_KEYS = ("authToken", "auth_token", "token", "jwt", "access_token")
SENSITIVE_USER_KEYS = ("password", "senha")


class ApiError(Exception):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.message = message
        self.status = status


class InvalidCredentials(ApiError):
    pass


class SessionExpired(ApiError):
    def __init__(self, message: str = SESSION_EXPIRED_MESSAGE, status: int | None = 401):
        super().__init__(message, status)


def _base_url(variable: str = "XANO_API_URL") -> str:
    url = os.getenv(variable, "").strip().rstrip("/")
    if not url:
        raise ApiError("O serviço está indisponível no momento. Tente novamente mais tarde.")
    return url


def _server_message(response: httpx.Response) -> str | None:
    try:
        data = response.json()
    except ValueError:
        return None
    message = data.get("message") if isinstance(data, dict) else None
    return message.strip() if isinstance(message, str) and message.strip() else None


async def _send(
    method: str,
    path: str,
    *,
    token: str | None = None,
    json: Any = None,
    params: dict[str, Any] | None = None,
    api_base_url: str | None = None,
) -> httpx.Response:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    base_url = httpx.URL(api_base_url or _base_url())
    query_params = dict(base_url.params)
    query_params.update(params or {})
    url = base_url.copy_with(
        path=f"{base_url.path.rstrip('/')}/{path.lstrip('/')}",
        params=query_params,
    )
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            return await client.request(method, url, headers=headers, json=json)
    except httpx.TimeoutException:
        raise ApiError("O servidor demorou para responder. Tente novamente.") from None
    except httpx.HTTPError:
        raise ApiError("Não foi possível conectar ao servidor. Verifique sua conexão.") from None


def _raise_for_status(
    response: httpx.Response,
    *,
    expose_server_error_message: bool = False,
) -> None:
    status = response.status_code
    if status < 400:
        return
    if status == 403:
        raise ApiError("Você não tem permissão para esta ação.", status)
    if status >= 500:
        server_message = _server_message(response) if expose_server_error_message else None
        normalized_message = (server_message or "").casefold()
        if (
            "sendgrid api error:" in normalized_message
            and "the provided authorization grant is invalid, expired, or revoked" in normalized_message
        ):
            raise ApiError(SENDGRID_AUTHORIZATION_INVALID_MESSAGE, status)
        raise ApiError(
            "O servidor está indisponível no momento. Tente novamente em instantes.",
            status,
        )
    messages = {
        400: "Não foi possível processar os dados enviados. Confira os campos e tente novamente.",
        404: "O item solicitado não foi encontrado.",
        409: "Não foi possível concluir a solicitação por causa de um conflito nos dados.",
        422: "Os dados enviados não passaram pela validação. Confira os campos.",
    }
    raise ApiError(messages.get(status, "Não foi possível concluir a solicitação. Tente novamente."), status)


def _json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        raise ApiError(UNEXPECTED_RESPONSE_MESSAGE, response.status_code) from None


async def request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    json: Any = None,
    params: dict[str, Any] | None = None,
    expose_server_error_message: bool = False,
) -> Any:
    """Chamada genérica à API. Com token, 401 e resposta `null` (200) significam sessão inválida."""
    response = await _send(method, path, token=token, json=json, params=params)
    if token and response.status_code == 401:
        raise SessionExpired(status=401)
    _raise_for_status(response, expose_server_error_message=expose_server_error_message)
    data = _json(response)
    if token and data is None:
        raise SessionExpired(status=response.status_code)
    return data


async def login(email: str, password: str) -> tuple[str, dict[str, Any] | None]:
    """POST /auth/login com `{"email", "senha"}`. Devolve (token, usuário ou None quando a API não envia o perfil)."""
    response = await _send("POST", "/auth/login", json={"email": email, "senha": password})
    if response.status_code in (400, 401, 403):
        raise InvalidCredentials(LOGIN_FALLBACK_MESSAGE, response.status_code)
    _raise_for_status(response)
    data = _json(response)
    token = _extract_token(data)
    if token is None:
        message = LOGIN_EMPTY_MESSAGE if data is None else UNEXPECTED_RESPONSE_MESSAGE
        raise ApiError(message, response.status_code)
    user = data.get("user") if isinstance(data, dict) else None
    return token, _clean_user(user) if isinstance(user, dict) else None


async def get_me(token: str) -> dict[str, Any]:
    """GET /auth/me. Devolve o perfil do usuário sem campos sensíveis."""
    data = await request("GET", "/auth/me", token=token)
    if not isinstance(data, dict):
        raise ApiError(UNEXPECTED_RESPONSE_MESSAGE)
    return _clean_user(data)


async def request_password_reset(email: str) -> Any:
    """Solicita ao Xano o envio de um link de redefinição para o endereço informado."""
    response = await _send(
        "GET",
        "/reset/request-reset-link",
        params={"email": email},
        api_base_url=_base_url("XANO_PASSWORD_RESET_API_URL"),
    )
    _raise_for_status(response)
    return _json(response)


def _extract_token(data: Any) -> str | None:
    """Aceita o token como string pura ou em qualquer uma das chaves conhecidas do Xano."""
    if isinstance(data, str):
        return data.strip() or None
    if isinstance(data, dict):
        for key in TOKEN_KEYS:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _clean_user(user: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in user.items() if key not in SENSITIVE_USER_KEYS}
