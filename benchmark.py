"""benchmark.py — Motor del benchmark (Parte 4).

Qué hace este módulo:
  - Carga `data/plantilla_preguntas_benchmark.json` (12 casos).
  - Para cada caso, construye el prompt real de la app reutilizando
    `context.construir_contexto()` y `prompts.build_chat_prompt()` /
    `prompts.build_checklist_prompt()`.
  - Llama a cada modelo de `config.BENCHMARK_MODELS` con la MISMA
    temperatura (`config.TEMPERATURE`), reutilizando `gemini_client.safe_generate()`
    y `gemini_client.MetricasLlamada` (NO se duplican llamadas a la API
    fuera de safe_generate).
  - Los errores de API (p. ej. 429 por cuota) se capturan por fila sin
    detener la ejecución.

Para qué sirve:
  - Es la base para `report.py` (CSV + informe) y para rellenar
    `entregables/matriz_decision.md` y `entregables/recomendacion.md`.

Requisito de dependencias:
  - Necesita que `gemini_client.py` tenga el parámetro opcional `model`
    añadido para poder variar el modelo por llamada sin duplicar el cliente.
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

import context
import prompts
from config import BENCHMARK_DATA_PATH, BENCHMARK_MODELS, TEMPERATURE
from gemini_client import MetricasLlamada, safe_generate

DATA_DIR = BENCHMARK_DATA_PATH.parent

# Nivel gratuito de Gemini: 5 peticiones/minuto por modelo. 13s de margen
# entre llamadas evita 429 RESOURCE_EXHAUSTED sin tener que reintentar.
PAUSA_ENTRE_LLAMADAS_S = 13


@dataclass
class FilaBenchmark:
    timestamp: str
    caso_id: str
    tipo: str
    empleado_id: str
    dia: int
    modelo: str
    elapsed_ms: int
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    respuesta: str
    json_valido: bool | None
    docs_usados: str
    error: str | None = None


def cargar_casos(ruta=BENCHMARK_DATA_PATH) -> list[dict]:
    with ruta.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("plantilla_preguntas_benchmark.json debe ser una lista de casos")
    return data


def cargar_empleados() -> dict:
    ruta = DATA_DIR / "empleados_demo.json"
    with ruta.open(encoding="utf-8") as f:
        empleados = json.load(f)
    return {e["id"]: e for e in empleados}


def _construir_prompt(caso: dict, empleado: dict, docs: list[dict], faqs: list[dict]) -> tuple[str, bool, dict]:
    """Construye el prompt real de la app para un caso del benchmark.

    Devuelve (prompt, es_json, contexto_usado).
    """
    dia = caso.get("dia", 1)
    departamento = empleado.get("departamento")
    es_checklist = caso.get("tipo", "chat") == "checklist"

    if es_checklist:
        pregunta_sintetica = f"día {dia} onboarding checklist tareas"
        contexto = context.construir_contexto(pregunta_sintetica, departamento, docs=docs, faqs=faqs)
        prompt = prompts.build_checklist_prompt(empleado, dia, contexto)
    else:
        pregunta = caso["pregunta"]
        contexto = context.construir_contexto(pregunta, departamento, docs=docs, faqs=faqs)
        prompt = prompts.build_chat_prompt(empleado, dia, pregunta, contexto, historial=None)

    return prompt, es_checklist, contexto


def ejecutar_benchmark() -> list[FilaBenchmark]:
    casos = cargar_casos()
    empleados = cargar_empleados()
    docs = context.cargar_documentos()
    faqs = context.cargar_faq()

    filas: list[FilaBenchmark] = []
    total_llamadas = len(casos) * len(BENCHMARK_MODELS)
    llamada_actual = 0

    for caso in casos:
        caso_id = caso["id"]
        empleado_id = caso.get("empleado_id", "emp_01")
        empleado = empleados.get(empleado_id)
        if empleado is None:
            print(f"AVISO: empleado {empleado_id!r} no encontrado, se omite caso {caso_id!r}")
            continue

        prompt, json_mode, contexto = _construir_prompt(caso, empleado, docs, faqs)
        docs_usados = ",".join(d["id"] for d in contexto["docs"])
        dia = caso.get("dia", 1)
        tipo = caso.get("tipo", "chat")

        for modelo in BENCHMARK_MODELS:
            llamada_actual += 1
            ts = datetime.now(timezone.utc).isoformat()
            try:
                texto, m = safe_generate(
                    prompt,
                    model=modelo,
                    temperature=TEMPERATURE,
                    json_mode=json_mode,
                )

                json_valido = None
                if json_mode:
                    try:
                        json.loads(texto)
                        json_valido = True
                    except json.JSONDecodeError:
                        json_valido = False

                filas.append(
                    FilaBenchmark(
                        timestamp=ts,
                        caso_id=caso_id,
                        tipo=tipo,
                        empleado_id=empleado_id,
                        dia=dia,
                        modelo=modelo,
                        elapsed_ms=m.elapsed_ms,
                        prompt_tokens=m.prompt_tokens,
                        output_tokens=m.output_tokens,
                        total_tokens=m.total_tokens,
                        respuesta=texto,
                        json_valido=json_valido,
                        docs_usados=docs_usados,
                    )
                )
                print(f"OK  {caso_id} × {modelo} ({m.elapsed_ms} ms)")
            except Exception as exc:  # noqa: BLE001 — benchmark didáctico
                filas.append(
                    FilaBenchmark(
                        timestamp=ts,
                        caso_id=caso_id,
                        tipo=tipo,
                        empleado_id=empleado_id,
                        dia=dia,
                        modelo=modelo,
                        elapsed_ms=0,
                        prompt_tokens=None,
                        output_tokens=None,
                        total_tokens=None,
                        respuesta="",
                        json_valido=None,
                        docs_usados=docs_usados,
                        error=str(exc),
                    )
                )
                print(f"ERR {caso_id} × {modelo}: {exc}")

            # Respeta el límite de 5 peticiones/minuto del nivel gratuito.
            if llamada_actual < total_llamadas:
                time.sleep(PAUSA_ENTRE_LLAMADAS_S)

    return filas


def filas_a_dicts(filas: list[FilaBenchmark]) -> list[dict]:
    return [asdict(f) for f in filas]
