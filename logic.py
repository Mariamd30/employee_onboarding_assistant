"""logic.py — Orquestación del Employee Onboarding Assistant.

Qué hace este módulo:
  - `procesar_chat()` — funcionalidad 1: conversación de texto libre.
  - `procesar_checklist()` — funcionalidad 2: checklist JSON del día.
  - Ambas devuelven un dict uniforme {"status", "mensaje", "data"}.

Para qué sirve:
  - Es el único módulo que conoce el orden de las capas:
    validators -> context -> prompts -> gemini_client -> state.
  - Ningún otro módulo debería importar más de uno de los anteriores a la vez;
    logic.py es quien los conecta.

Qué NO hace este módulo:
  - No decide qué documentos son relevantes (context.py).
  - No construye el texto del prompt (prompts.py).
  - No llama directamente a la API de Gemini (gemini_client.py).
  - No valida la entrada (validators.py) — HOY es un stub que siempre pasa
    (ver nota Fase 3 más abajo); logic.py ya deja el hueco preparado para
    no tener que reordenar el flujo cuando se implemente de verdad.

Fase 3 (pendiente):
  - validators.validar_entrada() hoy siempre devuelve (True, None).
  - Cuando se implemente de verdad (longitud, inyección, dominio, datos
    sensibles), procesar_chat() ya rechaza ANTES de tocar context/prompts/
    gemini_client si es_valida=False (fail-closed), sin cambiar nada aquí.
"""

import json

import context
import prompts
import state
import validators
from gemini_client import safe_generate


# ---------------------------------------------------------------------------
# Contrato de respuesta uniforme
# ---------------------------------------------------------------------------

def respuesta_ok(mensaje: str, data: dict | None = None) -> dict:
    return {"status": "ok", "mensaje": mensaje, "data": data or {}}


def respuesta_error(mensaje: str, errores: list[str]) -> dict:
    return {"status": "error", "mensaje": mensaje, "data": {"errores": errores}}


# ---------------------------------------------------------------------------
# Funcionalidad 1 — Chat
# ---------------------------------------------------------------------------

def procesar_chat(
    sesion: dict,
    pregunta: str,
    docs: list[dict] | None = None,
    faqs: list[dict] | None = None,
) -> dict:
    """Responde una pregunta libre del empleado y actualiza el historial.

    `sesion` es el dict devuelto por state.inicializar_estado(). Se modifica
    in-place (se añaden los mensajes user/assistant al historial).

    `docs`/`faqs`: si el llamador (p. ej. main.py o benchmark.py) ya cargó
    onboarding_docs.json / faq_onboarding.json en memoria, se pasan aquí para
    no releer disco en cada llamada. Si se omiten, context.py los carga él
    mismo (cómodo para una demo suelta, pero evitar en bucles/benchmark).
    """
    es_valida, motivo = validators.validar_entrada(pregunta)
    if not es_valida:
        return respuesta_error("No se pudo procesar la pregunta.", [motivo])

    empleado = sesion["empleado"]
    dia = sesion["dia"]
    departamento = empleado.get("departamento")

    contexto = context.construir_contexto(pregunta, departamento, docs=docs, faqs=faqs)
    historial = state.historial_acotado(sesion)

    prompt = prompts.build_chat_prompt(
        empleado=empleado,
        dia=dia,
        pregunta=pregunta,
        contexto=contexto,
        historial=historial,
    )

    try:
        texto, metricas = safe_generate(prompt, json_mode=False)
    except ValueError as e:
        # Prompt demasiado grande (safe_generate ya valida MAX_TOKENS_INPUT)
        return respuesta_error("No se pudo generar la respuesta.", [str(e)])

    state.append_user(sesion, pregunta)
    state.append_assistant(sesion, texto)

    return respuesta_ok(
        "Respuesta generada.",
        data={
            "respuesta": texto,
            "docs_usados": [d["id"] for d in contexto["docs"]],
            "faqs_usadas": [f["id"] for f in contexto["faqs"]],
            "metricas": metricas.__dict__,
        },
    )


# ---------------------------------------------------------------------------
# Funcionalidad 2 — Checklist JSON
# ---------------------------------------------------------------------------

def _pregunta_sintetica_checklist(dia: int) -> str:
    """Construye un texto de apoyo para que context.py puntúe documentos
    relevantes al día de onboarding, ya que aquí no hay pregunta libre del
    empleado. Se apoya en tags típicos de onboarding_docs.json (bienvenida,
    primer_dia, checklist, engineering, sales...).
    """
    if dia == 1:
        return "primer día bienvenida accesos slack"
    return f"día {dia} onboarding checklist tareas integración"


def procesar_checklist(
    sesion: dict,
    docs: list[dict] | None = None,
    faqs: list[dict] | None = None,
) -> dict:
    """Genera el plan de tareas del día de onboarding en formato JSON.

    `docs`/`faqs`: ver nota en procesar_chat() sobre evitar releer disco.
    """
    empleado = sesion["empleado"]
    dia = sesion["dia"]
    departamento = empleado.get("departamento")

    es_valida, motivo = validators.validar_dia(dia)
    if not es_valida:
        return respuesta_error("Día de onboarding inválido.", [motivo])

    pregunta_sintetica = _pregunta_sintetica_checklist(dia)
    contexto = context.construir_contexto(pregunta_sintetica, departamento, docs=docs, faqs=faqs)

    prompt = prompts.build_checklist_prompt(empleado, dia, contexto)

    try:
        texto, metricas = safe_generate(prompt, json_mode=True)
    except ValueError as e:
        return respuesta_error("No se pudo generar la checklist.", [str(e)])

    try:
        checklist = json.loads(texto)
    except json.JSONDecodeError:
        return respuesta_error(
            "El modelo no devolvió un JSON válido para la checklist.",
            [f"Salida cruda: {texto[:200]}"],
        )

    return respuesta_ok(
        "Checklist generada.",
        data={
            "checklist": checklist,
            "docs_usados": [d["id"] for d in contexto["docs"]],
            "metricas": metricas.__dict__,
        },
    )