"""state.py — Estado de sesión del empleado en onboarding.

Qué hace este módulo:
  - Guarda la ficha del empleado (desde empleados_demo.json), el día de
    onboarding (1-5) y el historial de mensajes entre turnos.
  - Helpers para el historial acotado (máx. MAX_TURNOS_HISTORIAL, config.py).

Para qué sirve:
  - Memoria de sesión para el chat y contexto de "en qué día está" para
    ajustar tono y tareas en chat + checklist (requisito transversal).

Qué NO debes hacer aquí:
  - No inventar ni adivinar datos del empleado a partir del texto: la ficha
    viene siempre de empleados_demo.json, no se extrae del mensaje.
"""

from config import MAX_TURNOS_HISTORIAL


def inicializar_estado(empleado: dict, dia: int = 1) -> dict:
    """Crea el dict de sesión para un empleado y día de onboarding dados.

    `empleado` es un registro tal cual de empleados_demo.json
    (id, nombre, departamento, rol, manager, modalidad, perfil, ...).
    """
    return {
        "empleado": empleado,
        "dia": dia,
        "messages": [],
        "turnos": 0,
    }


def append_user(state: dict, texto: str) -> None:
    state["messages"].append({"role": "user", "text": texto.strip()})


def append_assistant(state: dict, texto: str) -> None:
    state["messages"].append({"role": "assistant", "text": texto.strip()})
    state["turnos"] = state.get("turnos", 0) + 1


def historial_acotado(state: dict, max_turnos: int = MAX_TURNOS_HISTORIAL) -> list[dict]:
    """Devuelve los últimos mensajes limitados a max_turnos turnos completos
    (1 turno = 1 mensaje user + 1 mensaje assistant)."""
    msgs = state.get("messages", [])
    return msgs[-(max_turnos * 2):] if max_turnos > 0 else []


def avanzar_dia(state: dict, nuevo_dia: int) -> None:
    """Actualiza el día de onboarding simulado (1-5)."""
    state["dia"] = nuevo_dia


def perfil(state: dict) -> str | None:
    """Atajo para el perfil del empleado (dev_junior, comercial, remoto_eu)."""
    return state.get("empleado", {}).get("perfil")
